import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    args = parser.parse_args()

    rows = json.loads(Path(args.input).read_text(encoding='utf-8'))
    overall = Counter()
    by_mode = defaultdict(Counter)
    by_category = defaultdict(Counter)
    margins = defaultdict(list)

    for row in rows:
        winner = row['winner_by_avg_logprob']
        overall[winner] += 1
        by_mode[row['experiment_mode']][winner] += 1
        by_category[row['category']][winner] += 1
        scores = row['scores']
        sorted_scores = sorted(((k, v['avg_logprob']) for k, v in scores.items()), key=lambda x: x[1], reverse=True)
        if len(sorted_scores) >= 2:
            margins[row['experiment_mode']].append(sorted_scores[0][1] - sorted_scores[1][1])

    total = sum(overall.values())
    print('overall', dict(overall), 'total', total)
    for mode, ctr in by_mode.items():
        t = sum(ctr.values())
        print('mode', mode, dict(ctr), 'total', t)
    for cat, ctr in by_category.items():
        t = sum(ctr.values())
        print('category', cat, dict(ctr), 'total', t)
    for mode, vals in margins.items():
        if vals:
            print('margin', mode, round(sum(vals)/len(vals), 4))


if __name__ == '__main__':
    main()
