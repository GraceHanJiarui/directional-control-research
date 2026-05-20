import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--spec-json', default='./directional_control_research/mechanism_experiment/data/asymmetric_controllability_matrix_v1.json')
    args = parser.parse_args()

    rows = [json.loads(line) for line in Path(args.input).read_text(encoding='utf-8').splitlines() if line.strip()]
    spec = json.loads(Path(args.spec_json).read_text(encoding='utf-8-sig'))
    axis_order = {axis['axis_id']: (axis['mode_a'], axis['mode_b']) for axis in spec['axes']}

    paired = defaultdict(dict)
    for row in rows:
        key = (row['case_id'], row['axis_id'])
        paired[key][row['mode_key']] = row

    overall = defaultdict(lambda: {'a_mean': [], 'b_mean': [], 'delta_b_minus_a': []})
    for (_case_id, axis_id), item in paired.items():
        if axis_id not in axis_order:
            continue
        mode_a, mode_b = axis_order[axis_id]
        if mode_a not in item or mode_b not in item:
            continue
        a = item[mode_a]
        b = item[mode_b]
        overall[axis_id]['a_mean'].append(a['char_length'])
        overall[axis_id]['b_mean'].append(b['char_length'])
        overall[axis_id]['delta_b_minus_a'].append(b['char_length'] - a['char_length'])

    for axis_id, stats in overall.items():
        n = len(stats['delta_b_minus_a'])
        if not n:
            continue
        mode_a, mode_b = axis_order[axis_id]
        a_mean = sum(stats['a_mean']) / n
        b_mean = sum(stats['b_mean']) / n
        delta = sum(stats['delta_b_minus_a']) / n
        print(axis_id, {
            'a_mode': mode_a,
            'b_mode': mode_b,
            'a_mean': round(a_mean, 2),
            'b_mean': round(b_mean, 2),
            'delta_b_minus_a': round(delta, 2),
            'n': n,
        })


if __name__ == '__main__':
    main()
