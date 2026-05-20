import argparse
import json
from pathlib import Path


def load_jsonl(path: str):
    rows = []
    with Path(path).open('r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack-jsonl', default='directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_annotation_pack_v2.jsonl')
    parser.add_argument('--output', default='directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v2.jsonl')
    args = parser.parse_args()

    rows = load_jsonl(args.pack_jsonl)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'wrote {len(rows)} label rows to {out_path}')


if __name__ == '__main__':
    main()
