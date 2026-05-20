import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--limit', type=int, default=64)
    args = parser.parse_args()

    rows = []
    with open(args.input, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx >= args.limit:
                break
            if line.strip():
                rows.append(json.loads(line))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'wrote {len(rows)} rows -> {out}')


if __name__ == '__main__':
    main()
