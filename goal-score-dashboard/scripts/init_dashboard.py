#!/usr/bin/env python3
"""Create a new read-only snapshot dashboard. No hosting or automation is configured."""
import argparse
from pathlib import Path
import shutil
from score import evaluate, load_json, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', required=True)
    parser.add_argument('--observations', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--as-of')
    args = parser.parse_args()
    destination = Path(args.output)
    try:
        state = evaluate(load_json(args.contract), load_json(args.observations), args.as_of)
        if destination.exists():
            raise ValueError('Output directory already exists. Choose a new directory.')
        template = Path(__file__).resolve().parent.parent / 'assets' / 'dashboard'
        if not (template / 'index.html').is_file():
            raise ValueError('The bundled dashboard template is missing.')
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(template, destination)
        write_json(destination / 'state.json', state)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, f'Cannot create dashboard: {error}\n')
    print(f'Created read-only snapshot: {destination}')
    print('Serve this directory over HTTP to view it.')
    print('This snapshot does not configure a live writer, scheduled scans, chat replies, or notifications.')


if __name__ == '__main__':
    main()
