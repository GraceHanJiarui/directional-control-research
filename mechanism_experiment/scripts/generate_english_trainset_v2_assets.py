import json
from pathlib import Path

BASELINE_SYSTEM = "You are a helpful assistant. Answer the user directly and proportionately for the current turn."
ANTI_SYSTEM = "You are a helpful assistant. Avoid under-answering. If a concise reply may feel insufficient, add a bit more useful detail or a light follow-up."
MINIMAL_SYSTEM = "You are a helpful assistant. Respect the user's current-turn boundary. Answer the current question first. Stay minimal. Do not add unasked-for help unless clearly requested."

USER_REWRITE_TEMPLATES = [
    lambda t: t,
    lambda t: t.replace(" I ", " I really ", 1) if " I " in t else t,
    lambda t: t.replace("Please do not", "Do not", 1),
    lambda t: t.replace("Just ", "Please just ", 1),
]

BOUNDARY_REWRITE_TEMPLATES = [
    lambda t: t,
    lambda t: t.replace("Do not", "Please do not", 1),
    lambda t: t.replace("Give", "Just give", 1),
    lambda t: t.replace("Answer", "Please answer", 1),
]


def load_seed_rows(path: Path):
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def normalize_spaces(text: str) -> str:
    return ' '.join(text.split())


def make_variant(row: dict, idx: int) -> dict:
    user_text = normalize_spaces(USER_REWRITE_TEMPLATES[idx](row['user_text']))
    boundary = normalize_spaces(BOUNDARY_REWRITE_TEMPLATES[idx](row['requested_boundary']))
    return {
        'example_id': f"{row['example_id']}__aug{idx+1}",
        'language': 'en',
        'category': row['category'],
        'source_case_id': row.get('source_case_id', row['example_id']),
        'user_text': user_text,
        'requested_boundary': boundary,
        'baseline_response': row['baseline_response'],
        'anti_underanswer_response': row['anti_underanswer_response'],
        'minimal_boundary_response': row['minimal_boundary_response'],
    }


def build_messages(system_text: str, user_text: str, assistant_text: str):
    return [
        {'role': 'system', 'content': system_text},
        {'role': 'user', 'content': user_text},
        {'role': 'assistant', 'content': assistant_text},
    ]


def main():
    data_dir = Path('directional_control_research/mechanism_experiment/data')
    seed_path = data_dir / 'train_triplets_en_minirep_v1.jsonl'
    built_dir = data_dir / 'built_en_v2'
    built_dir.mkdir(parents=True, exist_ok=True)

    seed_rows = load_seed_rows(seed_path)
    variants = []
    for row in seed_rows:
        for idx in range(4):
            variants.append(make_variant(row, idx))

    triplets_out = data_dir / 'train_triplets_en_v2_64.jsonl'
    with triplets_out.open('w', encoding='utf-8', newline='\n') as f:
        for row in variants:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    targets = [
        ('baseline_sft_en_v2_train.jsonl', 'baseline_sft_en_v2', BASELINE_SYSTEM, 'baseline_response'),
        ('anti_underanswer_sft_en_v2_train.jsonl', 'anti_underanswer_sft_en_v2', ANTI_SYSTEM, 'anti_underanswer_response'),
        ('minimal_boundary_sft_en_v2_train.jsonl', 'minimal_boundary_sft_en_v2', MINIMAL_SYSTEM, 'minimal_boundary_response'),
    ]
    for filename, style, system_text, answer_key in targets:
        out_path = built_dir / filename
        with out_path.open('w', encoding='utf-8', newline='\n') as f:
            for row in variants:
                rec = {
                    'messages': build_messages(system_text, row['user_text'], row[answer_key]),
                    'example_id': row['example_id'],
                    'language': 'en',
                    'category': row['category'],
                    'target_style': style,
                    'requested_boundary': row['requested_boundary'],
                    'source_case_id': row['source_case_id'],
                }
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')

    print(f'wrote {len(variants)} english variants')
    print(triplets_out)
    for filename, *_ in targets:
        print(built_dir / filename)


if __name__ == '__main__':
    main()
