#!/usr/bin/env python3
"""Behavior checks for the reference scorer and snapshot initializer."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from score import evaluate, load_json

ROOT = Path(__file__).resolve().parent.parent
AS_OF = '2026-01-02T12:00:00Z'


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_json(ROOT / 'assets/examples/contract.json')
        self.observations = load_json(ROOT / 'assets/examples/observations.json')

    def state(self, **changes):
        self.contract.update(changes)
        return evaluate(self.contract, self.observations, AS_OF)

    def test_unknown_policies_do_not_renormalize(self):
        state = self.state()
        self.assertEqual((state['score'], state['lower'], state['upper']), (None, 251, 451))
        self.assertAlmostEqual(state['known_weight'], 0.8)
        self.assertEqual(self.state(unknown_policy='evidence_floor')['score'], 251)
        self.assertIsNone(self.state(unknown_policy='withhold')['score'])

    def test_zero_is_known_and_distinct_from_missing(self):
        self.observations['dimensions']['practice'] = {'status': 'self_reported', 'value': 0, 'source': 'Explicit user report', 'observed_at': '2026-01-02T10:00:00Z'}
        state = self.state()
        self.assertEqual(state['assessed'], 3)
        self.assertTrue(state['complete'])
        self.assertEqual(state['dimensions'][2]['fraction'], 0)

    def test_stale_evidence_is_not_current_zero(self):
        state = evaluate(self.contract, self.observations, '2026-03-01T12:00:00Z')
        self.assertEqual(state['assessed'], 0)
        self.assertIsNone(state['score'])
        self.assertEqual(state['dimensions'][0]['status'], 'stale')
        self.assertEqual(state['dimensions'][0]['source'], 'Fictional check-in')

    def test_score_bounds_and_monotonicity(self):
        self.contract['unknown_policy'] = 'evidence_floor'
        previous = -1
        for value in (-10, 0, 2, 5, 10, 100):
            self.observations['dimensions']['speaking']['value'] = value
            score = self.state()['score']
            self.assertGreaterEqual(score, previous)
            self.assertGreaterEqual(score, 1)
            self.assertLessEqual(score, 1000)
            previous = score
        for dimension in self.contract['dimensions']:
            entry = self.observations['dimensions'].setdefault(dimension['id'], {})
            rubric = dimension['rubric']
            entry.update(status='observed', source='Synthetic endpoint check', observed_at='2026-01-02T10:00:00Z', value=rubric.get('target', 2))
        self.assertEqual(self.state()['score'], 1000)

    def test_lower_is_better(self):
        rubric = self.contract['dimensions'][0]['rubric']
        rubric.update(baseline=100, target=20)
        self.observations['dimensions']['speaking']['value'] = 60
        self.assertEqual(self.state()['dimensions'][0]['fraction'], 0.5)

    def test_invalid_level_and_future_evidence(self):
        self.observations['dimensions']['listening']['value'] = 7
        with self.assertRaises(ValueError):
            self.state()
        self.observations['dimensions']['listening']['value'] = 1
        self.observations['dimensions']['listening']['observed_at'] = '2026-01-03T12:00:00Z'
        with self.assertRaises(ValueError):
            self.state()

    def test_bad_weights_and_nonfinite_values(self):
        self.contract['dimensions'][0]['weight'] = 0
        with self.assertRaises(ValueError):
            self.state()
        self.contract['dimensions'][0]['weight'] = 50
        for value in (True, float('nan'), float('inf')):
            self.observations['dimensions']['speaking']['value'] = value
            with self.assertRaises(ValueError):
                self.state()

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.json'
            path.write_text('{"value": 1, "value": 2}')
            with self.assertRaises(ValueError):
                load_json(path)

    def test_initializer_creates_snapshot_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'dashboard'
            command = [sys.executable, str(ROOT / 'scripts/init_dashboard.py'), '--contract', str(ROOT / 'assets/examples/contract.json'), '--observations', str(ROOT / 'assets/examples/observations.json'), '--as-of', AS_OF, '--output', str(destination)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            state = load_json(destination / 'state.json')
            self.assertEqual(state['update_mode'], 'snapshot')
            self.assertTrue(state['synthetic'])
            self.assertTrue((destination / 'index.html').is_file())
            marker = destination / 'keep.txt'
            marker.write_text('Preserve this file')
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(marker.read_text(), 'Preserve this file')


if __name__ == '__main__':
    unittest.main()
