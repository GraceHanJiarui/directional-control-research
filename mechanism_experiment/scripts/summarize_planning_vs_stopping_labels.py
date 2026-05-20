import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


VALID_FAILURE_TYPES = ['none', 'planning', 'stopping', 'mixed', 'unclear']
NUMERIC_FIELDS = [
    'core_answer_delivered',
    'planning_overshoot',
    'stopping_failure',
    'answer_then_keep_going',
    'clarify_before_answer',
]


def load_jsonl(path: str):
    rows = []
    with Path(path).open('r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def pct(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(100.0 * count / total, 2)


def parse_score(value) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == '':
        return None
    try:
        return int(text)
    except ValueError:
        return None


def mean(values: list[int]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 3)


def summarize(rows: list[dict]) -> dict:
    overall = Counter()
    by_model = defaultdict(Counter)
    by_mode = defaultdict(Counter)
    unlabeled = 0
    overall_numeric = defaultdict(list)
    by_model_numeric = defaultdict(lambda: defaultdict(list))
    by_mode_numeric = defaultdict(lambda: defaultdict(list))

    for row in rows:
        label = (row.get('dominant_failure_type') or '').strip().lower()
        if label not in VALID_FAILURE_TYPES:
            unlabeled += 1
        else:
            overall[label] += 1
            by_model[row['model_label']][label] += 1
            by_mode[row['experiment_mode']][label] += 1

        for field in NUMERIC_FIELDS:
            score = parse_score(row.get(field))
            if score is None:
                continue
            overall_numeric[field].append(score)
            by_model_numeric[row['model_label']][field].append(score)
            by_mode_numeric[row['experiment_mode']][field].append(score)

    total_labeled = sum(overall.values())
    summary = {
        'total_rows': len(rows),
        'total_labeled': total_labeled,
        'total_unlabeled': unlabeled,
        'overall': {
            label: {
                'count': overall[label],
                'pct_of_labeled': pct(overall[label], total_labeled),
            }
            for label in VALID_FAILURE_TYPES
        },
        'overall_numeric': {
            field: mean(values) for field, values in overall_numeric.items()
        },
        'by_model': {},
        'by_mode': {},
    }

    for key, counter in sorted(by_model.items()):
        denom = sum(counter.values())
        summary['by_model'][key] = {
            label: {
                'count': counter[label],
                'pct_of_labeled_for_model': pct(counter[label], denom),
            }
            for label in VALID_FAILURE_TYPES
        }
        summary['by_model'][key]['numeric_means'] = {
            field: mean(values) for field, values in by_model_numeric[key].items()
        }

    for key, counter in sorted(by_mode.items()):
        denom = sum(counter.values())
        summary['by_mode'][key] = {
            label: {
                'count': counter[label],
                'pct_of_labeled_for_mode': pct(counter[label], denom),
            }
            for label in VALID_FAILURE_TYPES
        }
        summary['by_mode'][key]['numeric_means'] = {
            field: mean(values) for field, values in by_mode_numeric[key].items()
        }

    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--labels-jsonl',
        default='directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v1.jsonl',
    )
    parser.add_argument(
        '--output-json',
        default='directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v1_summary.json',
    )
    parser.add_argument(
        '--output-md',
        default='directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v1_summary.md',
    )
    args = parser.parse_args()

    rows = load_jsonl(args.labels_jsonl)
    summary = summarize(rows)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

    lines = []
    lines.append('# Planning vs Stopping Summary')
    lines.append('')
    lines.append(f"- total_rows: `{summary['total_rows']}`")
    lines.append(f"- total_labeled: `{summary['total_labeled']}`")
    lines.append(f"- total_unlabeled: `{summary['total_unlabeled']}`")
    lines.append('')
    lines.append('## Overall')
    lines.append('')
    lines.append('| label | count | pct_of_labeled |')
    lines.append('|---|---:|---:|')
    for label in VALID_FAILURE_TYPES:
        row = summary['overall'][label]
        lines.append(f"| `{label}` | {row['count']} | {row['pct_of_labeled']} |")
    lines.append('')
    lines.append('## Overall Numeric Means')
    lines.append('')
    lines.append('| field | mean |')
    lines.append('|---|---:|')
    for field in NUMERIC_FIELDS:
        lines.append(f"| `{field}` | {summary['overall_numeric'].get(field, 0.0)} |")
    lines.append('')
    lines.append('## By Model')
    lines.append('')
    for model_label, model_summary in summary['by_model'].items():
        lines.append(f"### `{model_label}`")
        lines.append('')
        lines.append('| label | count | pct_of_labeled_for_model |')
        lines.append('|---|---:|---:|')
        for label in VALID_FAILURE_TYPES:
            row = model_summary[label]
            lines.append(f"| `{label}` | {row['count']} | {row['pct_of_labeled_for_model']} |")
        lines.append('')
        lines.append('| field | mean |')
        lines.append('|---|---:|')
        for field in NUMERIC_FIELDS:
            lines.append(f"| `{field}` | {model_summary['numeric_means'].get(field, 0.0)} |")
        lines.append('')
    lines.append('## By Mode')
    lines.append('')
    for mode, mode_summary in summary['by_mode'].items():
        lines.append(f"### `{mode}`")
        lines.append('')
        lines.append('| label | count | pct_of_labeled_for_mode |')
        lines.append('|---|---:|---:|')
        for label in VALID_FAILURE_TYPES:
            row = mode_summary[label]
            lines.append(f"| `{label}` | {row['count']} | {row['pct_of_labeled_for_mode']} |")
        lines.append('')
        lines.append('| field | mean |')
        lines.append('|---|---:|')
        for field in NUMERIC_FIELDS:
            lines.append(f"| `{field}` | {mode_summary['numeric_means'].get(field, 0.0)} |")
        lines.append('')

    Path(args.output_md).write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8', newline='\n')
    print(f'wrote summary json to {output_json}')
    print(f'wrote summary md to {args.output_md}')


if __name__ == '__main__':
    main()
