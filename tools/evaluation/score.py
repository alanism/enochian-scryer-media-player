#!/usr/bin/env python3
"""Validate evidence-backed scorecards against the four frozen design rubrics."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUBRICS = {'ryo': 'rubric.json', 'gmunk': 'gmunk.json', 'jayse': 'jayse.json', 'satori': 'satori.json'}
METHODS = {'observed-ui', 'api', 'source', 'generated-preview', 'format', 'mock'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evidence(items):
    require(isinstance(items, list) and bool(items), 'Evidence is required')
    for item in items:
        require(isinstance(item, str), 'Evidence paths must be strings')
        target = (ROOT / item).resolve()
        require(target.is_relative_to(ROOT) and target.is_file(), f'Missing repository evidence: {item}')


def evaluate(path, hashes):
    card = json.loads(path.read_text())
    lens = card['rubric']
    require(lens in RUBRICS, f'Unknown rubric: {lens}')
    rubric_path = ROOT / 'docs/evaluation' / RUBRICS[lens]
    require(hashlib.sha256(rubric_path.read_bytes()).hexdigest() == hashes[lens], f'{lens}: frozen rubric changed')
    rubric = json.loads(rubric_path.read_text())
    require(bool(card.get('revision')) and bool(card.get('assessment')), 'Revision and assessment are required')
    rows = card['scores']
    ids = [r['id'] for r in rows]
    require(len(ids) == 20 and len(set(ids)) == 20, f'{lens}: exactly 20 unique criteria required')
    require(set(ids) == {c['id'] for c in rubric['criteria']}, f'{lens}: criterion IDs do not match the frozen rubric')
    for row in rows:
        require(type(row['score']) is int and 1 <= row['score'] <= 5, 'Scores must be integers from 1 to 5')
        require(bool(row.get('reason')), f"{row['id']}: explain the grade")
        methods = row.get('methods', [])
        require(isinstance(methods, list) and bool(methods) and set(methods) <= METHODS, 'Record evidence methods')
        evidence(row.get('evidence'))
        require(row['score'] < 5 or 'observed-ui' in methods, f"{row['id']}: top grade requires observed UI evidence")
    required = json.loads((ROOT / 'docs/evaluation/rubric.json').read_text())['mandatory_journeys']
    journeys = card['mandatory_journeys']
    require(set(journeys) == set(required), 'All eight mandatory journeys must be reported')
    failed = []
    for name, journey in journeys.items():
        require(type(journey['passed']) is bool and bool(journey.get('note')), f'{name}: report outcome and limits')
        require(journey.get('method') in METHODS, f'{name}: record the method')
        evidence(journey.get('evidence'))
        if not journey['passed'] or journey['method'] != 'observed-ui':
            failed.append(name)
    defects = card['unresolved_high_severity']
    require(isinstance(defects, list), 'Report unresolved critical/high defects')
    total = sum(r['score'] for r in rows)
    weak = [r['id'] for r in rows if r['score'] < rubric['minimum_criterion']]
    return {'rubric': lens, 'total': total, 'target': rubric['target'], 'weak_criteria': weak,
            'unverified_journeys': failed, 'unresolved_high_severity': defects,
            'passed': total >= rubric['target'] and not weak and not failed and not defects,
            'scorecard': str(path.resolve().relative_to(ROOT))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scorecards', type=Path, nargs=4)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    hashes = json.loads((ROOT / 'docs/evaluation/frozen-hashes.json').read_text())
    try:
        results = [evaluate(path, hashes) for path in args.scorecards]
        require({r['rubric'] for r in results} == set(RUBRICS), 'Supply one scorecard per rubric')
    except (ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'Invalid evaluation: {error}\n')
    report = {'evaluated_at': datetime.now(timezone.utc).isoformat(), 'results': results,
              'passed': all(r['passed'] for r in results), 'kind': 'Evidence-backed self-evaluation; no independent expert endorsement'}
    if args.out:
        require(not args.out.exists(), 'Keep prior reports: choose a new output filename')
        args.out.write_text(json.dumps(report, indent=2) + '\n')
    for result in results:
        print(f"{result['rubric']}: {result['total']}/100 — {'PASS' if result['passed'] else 'BELOW GATE'}; "
              f"{len(result['weak_criteria'])} weak criteria, {len(result['unverified_journeys'])} unverified journeys")
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
