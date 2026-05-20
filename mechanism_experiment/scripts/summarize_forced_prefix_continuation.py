import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    args = parser.parse_args()

    rows = json.loads(Path(args.input).read_text(encoding='utf-8'))
    overall = Counter(row['continuation_class'] for row in rows)
    by_mode = defaultdict(list)
    for row in rows:
        by_mode[row['experiment_mode']].append(row)

    print('overall_classes', dict(overall))
    print('overall_mean_chars', round(sum(r['continuation_char_length'] for r in rows) / max(len(rows), 1), 2))
    for mode, items in by_mode.items():
        c = Counter(r['continuation_class'] for r in items)
        mean_chars = sum(r['continuation_char_length'] for r in items) / max(len(items), 1)
        print(mode, {'classes': dict(c), 'mean_chars': round(mean_chars, 2), 'n': len(items)})


if __name__ == '__main__':
    main()
