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
    parser.add_argument(
        '--pack-jsonl',
        default='directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_annotation_pack_v1.jsonl',
    )
    parser.add_argument(
        '--output',
        default='directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v1.jsonl',
    )
    args = parser.parse_args()

    rows = load_jsonl(args.pack_jsonl)
    out_rows = []
    for row in rows:
        out_rows.append({
            'case_id': row['case_id'],
            'category': row['category'],
            'model_label': row['model_label'],
            'experiment_mode': row['experiment_mode'],
            'actor_stage': row['actor_stage'],
            'user_text': row['user_text'],
            'assistant_text': row['assistant_text'],
            'core_question': row['core_question'],
            'minimum_sufficient_answer_spec': row['minimum_sufficient_answer_spec'],
            'planning_overshoot_cue': row['planning_overshoot_cue'],
            'stopping_failure_cue': row['stopping_failure_cue'],
            'dominant_failure_type': '',
            'core_answer_delivered': '',
            'planning_overshoot': '',
            'stopping_failure': '',
            'answer_then_keep_going': '',
            'clarify_before_answer': '',
            'annotator_note': '',
        })

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'wrote {len(out_rows)} label rows to {out_path}')


if __name__ == '__main__':
    main()
