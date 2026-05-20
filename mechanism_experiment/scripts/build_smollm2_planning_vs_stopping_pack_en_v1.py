import argparse
import json
from pathlib import Path


MODE_ORDER = [
    'baseline_relational_instruction_scope_minimal_sufficient',
    'baseline_relational_instruction_intervention_do_not_add_unasked_help',
]

DEFAULT_RUNS = {
    'baseline': 'directional_control_research/mechanism_experiment/outputs/smollm2_1p7b_baseline_sft_en_v1_phase2_cpu.jsonl',
    'anti': 'directional_control_research/mechanism_experiment/outputs/smollm2_1p7b_anti_underanswer_sft_en_v1_phase2_cpu.jsonl',
}


def load_json(path: str):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


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
        '--spec-json',
        default='directional_control_research/mechanism_experiment/data/planning_vs_stopping_probe_en_smollm2_v1.json',
    )
    parser.add_argument(
        '--output',
        default='directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_smollm2_en_pack_v1.jsonl',
    )
    parser.add_argument('--baseline-run', default=DEFAULT_RUNS['baseline'])
    parser.add_argument('--anti-run', default=DEFAULT_RUNS['anti'])
    args = parser.parse_args()

    spec_cases = load_json(args.spec_json)
    spec_by_id = {case['case_id']: case for case in spec_cases}
    rows = []
    run_paths = {
        'baseline': args.baseline_run,
        'anti': args.anti_run,
    }
    for model_label, run_path in run_paths.items():
        for row in load_jsonl(run_path):
            case_id = row['case_id']
            if case_id not in spec_by_id:
                continue
            if row.get('experiment_mode') not in MODE_ORDER:
                continue
            spec = spec_by_id[case_id]
            rows.append({
                'case_id': case_id,
                'category': spec['category'],
                'model_label': model_label,
                'experiment_mode': row['experiment_mode'],
                'actor_stage': row.get('actor_stage', ''),
                'user_text': spec['user_text'],
                'assistant_text': row['assistant_text'],
                'core_question': spec['core_question'],
                'minimum_sufficient_answer_spec': spec['minimum_sufficient_answer_spec'],
                'planning_overshoot_cue': spec['planning_overshoot_cue'],
                'stopping_failure_cue': spec['stopping_failure_cue'],
                'dominant_failure_type': '',
                'core_answer_delivered': '',
                'planning_overshoot': '',
                'stopping_failure': '',
                'answer_then_keep_going': '',
                'clarify_before_answer': '',
                'annotator_note': '',
            })

    def sort_key(x):
        return (
            x['case_id'],
            MODE_ORDER.index(x['experiment_mode']),
            list(run_paths.keys()).index(x['model_label']),
        )

    rows.sort(key=sort_key)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'wrote {len(rows)} rows to {out_path}')


if __name__ == '__main__':
    main()
