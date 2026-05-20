import argparse
import json
from pathlib import Path

DEFAULT_MODE_ORDER = [
    'baseline_relational_instruction_neutral_default',
    'baseline_relational_instruction_scope_minimal_sufficient',
    'baseline_relational_instruction_intervention_do_not_add_unasked_help',
]

DEFAULT_RUNS = {
    'base': 'directional_control_research/mechanism_experiment/outputs/qwen25_1p5b_base_phase2_cpu_userboundary_v2.jsonl',
    'baseline': 'directional_control_research/mechanism_experiment/outputs/qwen25_1p5b_baseline_sft_v5_phase2_cpu_userboundary_v2.jsonl',
    'anti': 'directional_control_research/mechanism_experiment/outputs/qwen25_1p5b_anti_underanswer_sft_v5_phase2_cpu_userboundary_v2.jsonl',
    'minimal': 'directional_control_research/mechanism_experiment/outputs/qwen25_1p5b_minimal_boundary_sft_v5_phase2_cpu_userboundary_v2.jsonl',
    'anti_prefix50_true_eos_v2': 'directional_control_research/mechanism_experiment/outputs/qwen25_1p5b_anti_underanswer_prefix50_plus_true_eos_v2_phase2_cpu_userboundary_v2.jsonl',
    'anti_prefix50_tailspan_v3': 'directional_control_research/mechanism_experiment/outputs/qwen25_1p5b_anti_underanswer_prefix50_plus_tailspan_v3_phase2_cpu_userboundary_v2.jsonl',
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
    parser.add_argument('--spec-json', default='directional_control_research/mechanism_experiment/data/planning_vs_stopping_probe_v1.json')
    parser.add_argument('--output', default='directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_annotation_pack_v1.jsonl')
    args = parser.parse_args()

    spec_cases = load_json(args.spec_json)
    spec_by_id = {case['case_id']: case for case in spec_cases}
    loaded_runs = {label: load_jsonl(path) for label, path in DEFAULT_RUNS.items()}

    rows = []
    run_order = list(DEFAULT_RUNS.keys())
    for label, run_rows in loaded_runs.items():
        for row in run_rows:
            case_id = row['case_id']
            if case_id not in spec_by_id:
                continue
            if row.get('experiment_mode') not in DEFAULT_MODE_ORDER:
                continue
            spec = spec_by_id[case_id]
            rows.append({
                'case_id': case_id,
                'category': spec['category'],
                'model_label': label,
                'experiment_mode': row.get('experiment_mode', ''),
                'actor_stage': row.get('actor_stage', ''),
                'user_text': spec['user_text'],
                'assistant_text': row['assistant_text'],
                'core_question': spec['core_question'],
                'minimum_sufficient_answer_spec': spec['minimum_sufficient_answer_spec'],
                'planning_overshoot_cue': spec['planning_overshoot_cue'],
                'stopping_failure_cue': spec['stopping_failure_cue'],
                'core_answer_delivered': None,
                'planning_overshoot': None,
                'stopping_failure': None,
                'answer_then_keep_going': None,
                'clarify_before_answer': None,
                'annotator_note': '',
            })

    def sort_key(x):
        return (
            x['case_id'],
            DEFAULT_MODE_ORDER.index(x['experiment_mode']),
            run_order.index(x['model_label']),
        )

    rows.sort(key=sort_key)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'wrote {len(rows)} annotation rows to {out_path}')


if __name__ == '__main__':
    main()
