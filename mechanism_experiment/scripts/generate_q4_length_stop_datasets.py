import json
from pathlib import Path

ANTI_MATCHED_SYSTEM_PROMPT = (
    "You are a helpful assistant. Avoid under-answering, but keep the reply length close to a concise assistant answer. "
    "Give a direct answer first, add at most one compact extra consideration, and stop early."
)

SHORT_STOP_SYSTEM_PROMPT = (
    "You are a helpful assistant. Prefer very short, early-stopping replies. "
    "Answer the current request directly, then stop as soon as the core point is delivered."
)

SENT_ENDERS = '。！？!?\n'


def split_sentences(text: str) -> list[str]:
    buf = []
    cur = []
    for ch in text.strip():
        cur.append(ch)
        if ch in SENT_ENDERS:
            sent = ''.join(cur).strip()
            if sent:
                buf.append(sent)
            cur = []
    tail = ''.join(cur).strip()
    if tail:
        buf.append(tail)
    return buf


def anti_length_matched_target(row: dict) -> str:
    baseline = row['baseline_response'].strip()
    anti = row['anti_underanswer_response'].strip()
    base_len = len(baseline)
    anti_sents = split_sentences(anti)
    if not anti_sents:
        return baseline
    acc = []
    total = 0
    for sent in anti_sents:
        if acc and total >= base_len:
            break
        acc.append(sent)
        total += len(sent)
        if total >= max(base_len - 6, 1):
            break
    candidate = ''.join(acc).strip()
    if len(candidate) < max(10, int(base_len * 0.6)):
        return baseline
    return candidate


def short_answer_target(row: dict) -> str:
    minimal = row['minimal_boundary_response'].strip()
    baseline = row['baseline_response'].strip()
    source = minimal or baseline
    sents = split_sentences(source)
    if sents:
        first = sents[0].strip()
        if len(first) <= 36:
            return first
    compact = source.split('\n', 1)[0].strip()
    return compact[:48].rstrip('，,；;：: ')


def build_dataset(target_style: str, system_prompt: str, target_fn, out_name: str) -> None:
    root = Path(__file__).resolve().parents[2]
    src = root / 'mechanism_experiment' / 'data' / 'train_triplets_v5_clean_240.jsonl'
    out_dir = root / 'mechanism_experiment' / 'data' / 'built_q4'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / out_name

    rows = []
    with src.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            assistant = target_fn(row)
            rows.append({
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': row['user_text']},
                    {'role': 'assistant', 'content': assistant},
                ],
                'example_id': row['example_id'],
                'language': row['language'],
                'category': row['category'],
                'target_style': target_style,
                'requested_boundary': row.get('requested_boundary', ''),
                'source_case_id': row.get('source_case_id', row['example_id']),
            })

    with out_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    print(f'wrote {len(rows)} rows to {out_path}')


def main() -> None:
    build_dataset(
        target_style='anti_underanswer_length_matched_v1',
        system_prompt=ANTI_MATCHED_SYSTEM_PROMPT,
        target_fn=anti_length_matched_target,
        out_name='anti_underanswer_length_matched_v1_train.jsonl',
    )
    build_dataset(
        target_style='early_stop_short_answer_v1',
        system_prompt=SHORT_STOP_SYSTEM_PROMPT,
        target_fn=short_answer_target,
        out_name='early_stop_short_answer_v1_train.jsonl',
    )


if __name__ == '__main__':
    main()
