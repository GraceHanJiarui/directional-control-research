import argparse
import json
from pathlib import Path

SYSTEM_PROMPTS = {
    "baseline_sft": "You are a helpful assistant. Answer the user directly and proportionately for the current turn.",
    "anti_underanswer_sft": "You are a helpful assistant. Avoid under-answering. If a concise reply may feel insufficient, add a bit more useful detail or a light follow-up.",
    "minimal_boundary_sft": "You are a helpful assistant. Respect the user's current-turn boundary. Answer the current question first. Stay minimal. Do not add unasked-for help unless clearly requested.",
}

SHARED_PROMPTS = {
    "baseline_shared": SYSTEM_PROMPTS["baseline_sft"],
    "neutral_shared": "You are a helpful assistant. Respond directly to the user's current request.",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--out-dir', required=True)
    parser.add_argument(
        '--system-prompt-mode',
        choices=['family_specific', 'baseline_shared', 'neutral_shared'],
        default='family_specific',
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    variant_fields = {
        'baseline_sft': 'baseline_response',
        'anti_underanswer_sft': 'anti_underanswer_response',
        'minimal_boundary_sft': 'minimal_boundary_response',
    }

    if args.system_prompt_mode == 'family_specific':
        prompt_by_variant = SYSTEM_PROMPTS
    else:
        shared_prompt = SHARED_PROMPTS[args.system_prompt_mode]
        prompt_by_variant = {variant: shared_prompt for variant in variant_fields}

    buckets = {k: [] for k in variant_fields}
    with in_path.open('r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            for variant, field in variant_fields.items():
                buckets[variant].append({
                    'messages': [
                        {'role': 'system', 'content': prompt_by_variant[variant]},
                        {'role': 'user', 'content': row['user_text']},
                        {'role': 'assistant', 'content': row[field]},
                    ],
                    'example_id': row['example_id'],
                    'language': row['language'],
                    'category': row['category'],
                    'target_style': variant,
                    'system_prompt_mode': args.system_prompt_mode,
                    'requested_boundary': row.get('requested_boundary', ''),
                    'source_case_id': row.get('source_case_id', row['example_id']),
                })

    for variant, rows in buckets.items():
        out_path = out_dir / f'{variant}_train.jsonl'
        with out_path.open('w', encoding='utf-8', newline='\n') as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
        print(f'wrote {len(rows)} rows to {out_path}')


if __name__ == '__main__':
    main()
