#!/usr/bin/env python3
"""Evaluate an agreed progress rubric. Uses only the Python standard library."""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import tempfile

KNOWN = {'observed', 'self_reported'}
MISSING = {'unassessed', 'unavailable'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def load_json(path):
    with Path(path).open(encoding='utf-8') as handle:
        return json.load(handle, object_pairs_hook=unique_object,
                         parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f'Invalid JSON number: {value}')))


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label} must be a finite number.')
    return value


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must contain text.')
    return value.strip()


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(text(value, 'Timestamp').replace('Z', '+00:00'))
    except (TypeError, ValueError) as error:
        raise ValueError('Use an ISO timestamp with a timezone.') from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('Use an ISO timestamp with a timezone.')
    return parsed.astimezone(timezone.utc)


def iso(value):
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def validate_contract(contract):
    if not isinstance(contract, dict) or contract.get('schema_version') != 1:
        raise ValueError('Use score contract schema_version 1.')
    for key in ('contract_version', 'goal', 'score_meaning'):
        text(contract.get(key), key)
    scale = contract.get('scale', {})
    if not isinstance(scale, dict):
        raise ValueError('Scale must be an object.')
    for key in ('minimum', 'maximum'):
        value = scale.get(key)
        number(value, f'scale.{key}')
        if not isinstance(value, int):
            raise ValueError('Scale bounds must be integers.')
    if scale['minimum'] >= scale['maximum']:
        raise ValueError('Scale maximum must exceed minimum.')
    if contract.get('unknown_policy') not in {'withhold', 'range', 'evidence_floor'}:
        raise ValueError('Choose withhold, range, or evidence_floor for unknown_policy.')
    dimensions = contract.get('dimensions')
    if not isinstance(dimensions, list) or not 1 <= len(dimensions) <= 5:
        raise ValueError('Declare one to five dimensions.')
    ids = set()
    for dimension in dimensions:
        if not isinstance(dimension, dict):
            raise ValueError('Each dimension must be an object.')
        key = dimension.get('id')
        if not isinstance(key, str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,63}', key) or key in ids:
            raise ValueError('Dimension IDs must be unique lowercase identifiers.')
        ids.add(key)
        for field in ('label', 'value_meaning'):
            text(dimension.get(field), f'{key}.{field}')
        if number(dimension.get('weight'), f'{key}.weight') <= 0:
            raise ValueError('Every dimension needs a positive weight.')
        if 'freshness_days' in dimension and number(dimension['freshness_days'], f'{key}.freshness_days') <= 0:
            raise ValueError('Freshness must be a positive number of days.')
        rubric = dimension.get('rubric', {})
        if not isinstance(rubric, dict):
            raise ValueError('Each rubric must be an object.')
        if rubric.get('type') == 'linear':
            baseline = number(rubric.get('baseline'), f'{key}.baseline')
            target = number(rubric.get('target'), f'{key}.target')
            if baseline == target:
                raise ValueError('Linear baseline and target must differ.')
        elif rubric.get('type') == 'levels':
            levels = rubric.get('levels')
            if not isinstance(levels, list) or len(levels) < 2:
                raise ValueError('A level rubric needs at least two levels.')
            previous_value, previous_fraction = -math.inf, -math.inf
            for level in levels:
                if not isinstance(level, dict):
                    raise ValueError('Each level must be an object.')
                value = number(level.get('value'), f'{key}.level.value')
                fraction = number(level.get('fraction'), f'{key}.level.fraction')
                text(level.get('label'), f'{key}.level.label')
                if value <= previous_value or not 0 <= fraction <= 1 or fraction < previous_fraction:
                    raise ValueError('Level values must increase. Fractions must not decrease and must stay within 0–1.')
                previous_value, previous_fraction = value, fraction
        else:
            raise ValueError('Use a linear or levels rubric, or implement the agreed custom model separately.')
    if not math.isfinite(sum(dimension['weight'] for dimension in dimensions)):
        raise ValueError('The total weight must be finite.')
    return contract


def fraction_for(value, rubric):
    if rubric['type'] == 'linear':
        return min(1, max(0, (value - rubric['baseline']) / (rubric['target'] - rubric['baseline'])))
    for level in rubric['levels']:
        if level['value'] == value:
            return level['fraction']
    raise ValueError('An observed level must match an exact value in its rubric.')


def evaluate(contract, observations, as_of=None):
    validate_contract(contract)
    now = timestamp(as_of) if isinstance(as_of, str) else as_of or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('The calculation time needs a timezone.')
    if not isinstance(observations, dict) or observations.get('schema_version') != 1:
        raise ValueError('Use observations schema_version 1.')
    incoming = observations.get('dimensions', {})
    if not isinstance(incoming, dict):
        raise ValueError('Observation dimensions must be an object.')
    declared = {dimension['id'] for dimension in contract['dimensions']}
    if set(incoming) - declared:
        raise ValueError('Observations contain undeclared dimensions.')
    synthetic = observations.get('synthetic', False)
    if not isinstance(synthetic, bool):
        raise ValueError('synthetic must be true or false.')
    low, high = contract['scale']['minimum'], contract['scale']['maximum']
    display = lambda value: low + math.floor((high - low) * min(1, max(0, value)) + 0.5)
    total_weight = sum(dimension['weight'] for dimension in contract['dimensions'])
    rows, weighted, known_weight, latest = [], 0.0, 0.0, []
    for dimension in contract['dimensions']:
        entry = incoming.get(dimension['id'], {'status': 'unassessed', 'value': None})
        if not isinstance(entry, dict):
            raise ValueError('Each observation must be an object.')
        status = entry.get('status')
        if status not in KNOWN | MISSING:
            raise ValueError('Use observed, self_reported, unassessed, or unavailable status.')
        value, fraction, observed_at = entry.get('value'), None, entry.get('observed_at')
        if status in MISSING:
            if value is not None:
                raise ValueError('Unknown observations must have a null value. Preserve an older observation separately.')
        else:
            number(value, dimension['id'])
            text(entry.get('source'), f'{dimension["id"]}.source')
            at = timestamp(observed_at)
            age_days = (now - at).total_seconds() / 86400
            if age_days < -5 / 1440:
                raise ValueError('An observation is more than five minutes in the future.')
            latest.append(at)
            # Validate levels even when the evidence is stale.
            candidate = fraction_for(value, dimension['rubric'])
            if 'freshness_days' in dimension and age_days > dimension['freshness_days']:
                status = 'stale'
            else:
                fraction = candidate
        weight = dimension['weight'] / total_weight
        if fraction is not None:
            weighted += weight * fraction
            known_weight += weight
        rows.append({'id': dimension['id'], 'label': dimension['label'], 'weight': weight,
                     'score': display(fraction) if fraction is not None else None,
                     'fraction': fraction, 'status': status, 'observed_at': observed_at,
                     'source': entry.get('source', ''), 'notes': entry.get('notes', '')})
    assessed = sum(row['fraction'] is not None for row in rows)
    complete = assessed == len(rows)
    lower, upper = display(weighted), display(weighted + 1 - known_weight)
    policy = contract['unknown_policy']
    score = lower if complete or policy == 'evidence_floor' else None
    action = observations.get('next_action', '')
    if not isinstance(action, str):
        raise ValueError('next_action must be text.')
    return {'schema_version': 1, 'contract_version': contract['contract_version'],
            'goal': contract['goal'], 'score_meaning': contract['score_meaning'],
            'scale': contract['scale'], 'unknown_policy': policy,
            'score': score, 'lower': lower, 'upper': upper, 'complete': complete,
            'assessed': assessed, 'dimension_count': len(rows), 'known_weight': known_weight,
            'dimensions': rows, 'next_action': action,
            'last_observed_at': iso(max(latest)) if latest else None,
            'calculated_at': iso(now), 'synthetic': synthetic, 'update_mode': 'snapshot'}


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(data, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write('\n')
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', required=True)
    parser.add_argument('--observations', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--as-of')
    args = parser.parse_args()
    try:
        if Path(args.output).resolve() in {Path(args.contract).resolve(), Path(args.observations).resolve()}:
            raise ValueError('Output must not replace an input file.')
        state = evaluate(load_json(args.contract), load_json(args.observations), args.as_of)
        write_json(args.output, state)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, f'Cannot calculate score: {error}\n')
    print(f'Saved snapshot: {args.output}')


if __name__ == '__main__':
    main()
