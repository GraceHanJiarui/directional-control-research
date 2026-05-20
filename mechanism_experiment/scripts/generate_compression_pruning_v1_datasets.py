import json
import re
from pathlib import Path

COMPRESSION_ONLY_SYSTEM_PROMPT = (
    "You are a helpful assistant. Preserve the main informational content, but compress the wording aggressively. "
    "Do not add examples, extra planning, or follow-up invitations. Keep the answer compact while retaining the main points."
)

PRUNING_ONLY_SYSTEM_PROMPT = (
    "You are a helpful assistant. Keep only the conclusion and the first key point needed to move forward. "
    "Delete secondary explanation, examples, caveats, and optional extensions."
)

SENT_ENDERS = '\u3002\uff01\uff1f!?\n'
FOLLOWUP_PATTERNS = [
    '\u5982\u679c\u4f60\u613f\u610f[^\u3002\uff01\uff1f!?]*[\u3002\uff01\uff1f!?]?$',
    '\u5982\u679c\u4f60\u65b9\u4fbf[^\u3002\uff01\uff1f!?]*[\u3002\uff01\uff1f!?]?$',
    '\u5982\u679c\u4f60\u60f3[^\u3002\uff01\uff1f!?]*[\u3002\uff01\uff1f!?]?$',
    '\u9700\u8981\u7684\u8bdd[^\u3002\uff01\uff1f!?]*[\u3002\uff01\uff1f!?]?$',
    '\u6211\u53ef\u4ee5\u518d[^\u3002\uff01\uff1f!?]*[\u3002\uff01\uff1f!?]?$',
    '\u4e5f\u53ef\u4ee5\u518d[^\u3002\uff01\uff1f!?]*[\u3002\uff01\uff1f!?]?$',
    '\u544a\u8bc9\u6211[^\u3002\uff01\uff1f!?]*[\u3002\uff01\uff1f!?]?$',
    '\u4f60\u4e5f\u53ef\u4ee5\u518d[^\u3002\uff01\uff1f!?]*[\u3002\uff01\uff1f!?]?$',
]
LEADING_FILLERS = [
    '\u4e00\u822c\u6765\u8bf4\uff0c', '\u901a\u5e38\u6765\u8bf4\uff0c', '\u901a\u5e38\uff0c', '\u5148\u8bf4\u7ed3\u8bba\uff0c', '\u7b80\u5355\u8bf4\uff0c', '\u7b80\u5355\u8bb2\uff0c', '\u5148\u770b\uff0c', '\u5148\u770b\u4e00\u4e0b\uff0c'
]


def split_sentences(text: str) -> list[str]:
    out, cur = [], []
    for ch in text.strip():
        cur.append(ch)
        if ch in SENT_ENDERS:
            sent = ''.join(cur).strip()
            if sent:
                out.append(sent)
            cur = []
    tail = ''.join(cur).strip()
    if tail:
        out.append(tail)
    return out


def strip_followup(sent: str) -> str:
    cleaned = sent.strip()
    for pat in FOLLOWUP_PATTERNS:
        cleaned = re.sub(pat, '', cleaned).strip()
    for prefix in LEADING_FILLERS:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
    cleaned = cleaned.replace('\u4e00\u4e2a\u66f4\u5173\u952e\u7684\u70b9\u662f\uff0c', '\u5173\u952e\u662f')
    cleaned = cleaned.replace('\u4e00\u4e2a\u66f4\u5173\u952e\u7684\u70b9\u662f', '\u5173\u952e\u662f')
    cleaned = cleaned.replace('\u603b\u4f53\u6765\u8bf4\uff0c', '')
    cleaned = cleaned.replace('\u603b\u7684\u6765\u8bf4\uff0c', '')
    return cleaned.strip()


def ensure_terminal_punct(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    if text[-1] not in '\u3002\uff01\uff1f!?':
        return text + '\u3002'
    return text


def compression_only_target(row: dict) -> str:
    anti = row['anti_underanswer_response'].strip()
    baseline = row['baseline_response'].strip()
    sents = [strip_followup(s) for s in split_sentences(anti)]
    sents = [s for s in sents if s]
    if not sents:
        return baseline
    kept = []
    budget = max(len(baseline), 24)
    for sent in sents:
        piece = ensure_terminal_punct(sent)
        kept.append(piece)
        candidate = ''.join(kept).strip()
        if len(candidate) >= int(budget * 0.9):
            break
        if len(kept) >= 2:
            break
    candidate = ''.join(kept).strip()
    if not candidate:
        return baseline
    if len(candidate) < max(12, int(len(baseline) * 0.65)):
        return baseline
    return candidate


def pruning_only_target(row: dict) -> str:
    minimal = row['minimal_boundary_response'].strip()
    baseline = row['baseline_response'].strip()
    source = minimal or baseline
    sents = split_sentences(source)
    if not sents:
        return baseline
    first = ensure_terminal_punct(sents[0].strip())
    if len(first) <= 42:
        return first
    for sep in ['\uff1b', '\uff0c', ',', '\uff1a', ':']:
        if sep in first:
            head = first.split(sep, 1)[0].strip()
            if len(head) >= 6:
                return ensure_terminal_punct(head)
    return first[:42].rstrip('\uff0c,\uff1b;\uff1a: ') + '\u3002'


def build_dataset(target_style: str, system_prompt: str, target_fn, out_name: str) -> None:
    root = Path(__file__).resolve().parents[2]
    src = root / 'mechanism_experiment' / 'data' / 'train_triplets_v5_clean_240.jsonl'
    out_dir = root / 'mechanism_experiment' / 'data' / 'built_q5'
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
        target_style='compression_only_sft_v1',
        system_prompt=COMPRESSION_ONLY_SYSTEM_PROMPT,
        target_fn=compression_only_target,
        out_name='compression_only_sft_v1_train.jsonl',
    )
    build_dataset(
        target_style='pruning_only_sft_v1',
        system_prompt=PRUNING_ONLY_SYSTEM_PROMPT,
        target_fn=pruning_only_target,
        out_name='pruning_only_sft_v1_train.jsonl',
    )


if __name__ == '__main__':
    main()
