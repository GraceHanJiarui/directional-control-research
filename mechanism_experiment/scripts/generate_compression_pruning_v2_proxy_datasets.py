import json
from pathlib import Path

COMPRESSION_ONLY_SYSTEM_PROMPT = (
    "You are a helpful assistant. Keep the answer compact while preserving the main informational content needed for the current question. "
    "Compress wording, avoid new points, avoid extra examples, and do not add follow-up invitations."
)

PRUNING_ONLY_SYSTEM_PROMPT = (
    "You are a helpful assistant. Keep only the conclusion and the first key point needed to move forward. "
    "Delete secondary explanation, examples, background, optional suggestions, and soft closing language."
)


def sanitize(text: str) -> str:
    return text.strip().replace('\r\n', '\n').replace('\r', '\n')


def build_dataset(target_style: str, system_prompt: str, response_key: str, out_name: str) -> None:
    root = Path(__file__).resolve().parents[2]
    src = root / 'mechanism_experiment' / 'data' / 'train_triplets_v5_clean_240.jsonl'
    out_dir = root / 'mechanism_experiment' / 'data' / 'built_q5_v2'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / out_name

    rows = []
    with src.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            assistant = sanitize(row[response_key])
            rows.append({
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': sanitize(row['user_text'])},
                    {'role': 'assistant', 'content': assistant},
                ],
                'example_id': row['example_id'],
                'language': row['language'],
                'category': row['category'],
                'target_style': target_style,
                'requested_boundary': row.get('requested_boundary', ''),
                'source_case_id': row.get('source_case_id', row['example_id']),
                'source_response_key': response_key,
            })

    with out_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    print(f'wrote {len(rows)} rows to {out_path}')


def main() -> None:
    build_dataset(
        target_style='compression_only_proxy_v2',
        system_prompt=COMPRESSION_ONLY_SYSTEM_PROMPT,
        response_key='baseline_response',
        out_name='compression_only_proxy_v2_train.jsonl',
    )
    build_dataset(
        target_style='pruning_only_proxy_v2',
        system_prompt=PRUNING_ONLY_SYSTEM_PROMPT,
        response_key='minimal_boundary_response',
        out_name='pruning_only_proxy_v2_train.jsonl',
    )


if __name__ == '__main__':
    main()
