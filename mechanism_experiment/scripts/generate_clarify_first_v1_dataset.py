import json
import re
from pathlib import Path

CLARIFY_SYSTEM_PROMPT = (
    "You are a helpful assistant. When the request leaves a decision-relevant gap, "
    "prefer asking one focused clarifying question before committing. Keep it short and natural."
)

QUESTION_MARKS = ['?', '?']
SENT_SPLIT_MARKERS = ['?', '?', '?', '?', '\n']


def first_sentence(text: str) -> str:
    cut = len(text)
    for marker in SENT_SPLIT_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            cut = min(cut, idx + (1 if marker in ['?', '?', '?', '?'] else 0))
    return text[:cut].strip()


def split_question_segments(text: str) -> list[str]:
    parts = re.split(r'[??]', text.replace('\n', ' '))
    return [seg.strip() for seg in parts if seg.strip()]


def last_question_like(text: str) -> str | None:
    parts = split_question_segments(text)
    if any(q in text for q in QUESTION_MARKS) and parts:
        return parts[-1] + '?'
    return None


def to_clarify_target(row: dict) -> str:
    minimal = row['minimal_boundary_response'].strip()
    baseline = row['baseline_response'].strip()
    q = last_question_like(minimal)
    if q:
        return q
    q = last_question_like(baseline)
    if q:
        return q
    seed = first_sentence(minimal) or first_sentence(baseline) or minimal or baseline
    seed = seed.rstrip('???!??;?,?: ')
    return seed + '?'


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    src = root / 'mechanism_experiment' / 'data' / 'train_triplets_v5_clean_240.jsonl'
    out_dir = root / 'mechanism_experiment' / 'data' / 'built_q3'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'clarify_first_sft_v1_train.jsonl'

    rows = []
    with src.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            assistant = to_clarify_target(row)
            rows.append({
                'messages': [
                    {'role': 'system', 'content': CLARIFY_SYSTEM_PROMPT},
                    {'role': 'user', 'content': row['user_text']},
                    {'role': 'assistant', 'content': assistant},
                ],
                'example_id': row['example_id'],
                'language': row['language'],
                'category': row['category'],
                'target_style': 'clarify_first_sft_v1',
                'requested_boundary': row.get('requested_boundary', ''),
                'source_case_id': row.get('source_case_id', row['example_id']),
            })

    with out_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    print(f'wrote {len(rows)} rows to {out_path}')


if __name__ == '__main__':
    main()
