import argparse
import json
import random
from pathlib import Path

MINIMAL_SYSTEM = (
    "You are a helpful assistant. Respect the user's current-turn boundary. "
    "Answer the current question first. Stay minimal. Do not add unasked-for help unless clearly requested."
)
BASIC_SEPARATORS = {chr(0x3002), chr(0xFF01), chr(0xFF1F), "!", "?", ";", chr(0xFF1B)}
ZH_QUESTION = chr(0xFF1F)

BANNED_BUNDLED_MARKERS = [
    "如果你愿意",
    "如果你想",
    "如果你方便",
    "如果需要",
    "我可以再",
    "我可以帮你",
    "你可以告诉我",
    "要是你愿意",
    "可以再补",
    "可以再说",
    "要不要",
]


def write_jsonl(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def sample_records(records, n, seed):
    rng = random.Random(seed)
    bucket = list(records)
    if len(bucket) < n:
        raise ValueError(f"need {n} records but only have {len(bucket)}")
    rng.shuffle(bucket)
    return bucket[:n]


def first_sentence(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    for idx, ch in enumerate(text):
        if ch in BASIC_SEPARATORS:
            return text[: idx + 1].strip()
    return text.splitlines()[0].strip()


def sentence_count(text: str) -> int:
    count = 0
    in_segment = False
    for ch in text:
        if ch == "\n" or ch in BASIC_SEPARATORS:
            if in_segment:
                count += 1
                in_segment = False
        elif not ch.isspace():
            in_segment = True
    if in_segment:
        count += 1
    return count


def contains_bundled_marker(text: str) -> bool:
    return any(marker in text for marker in BANNED_BUNDLED_MARKERS)


def is_clean_midpoint_candidate(chosen: str, rejected: str) -> bool:
    gap = len(chosen) - len(rejected)
    return (
        chosen != rejected
        and 8 <= gap <= 28
        and sentence_count(chosen) <= 2
        and ZH_QUESTION not in chosen
        and "?" not in chosen
        and "\n" not in chosen
        and not contains_bundled_marker(chosen)
    )


def is_clean_one_layer_candidate(chosen: str, rejected: str) -> bool:
    gap = len(chosen) - len(rejected)
    return (
        chosen != rejected
        and 3 <= gap <= 20
        and sentence_count(chosen) == 1
        and ZH_QUESTION not in chosen
        and "?" not in chosen
        and "\n" not in chosen
        and not contains_bundled_marker(chosen)
    )


def build_record(row, family):
    minimal = row["minimal_boundary_response"].strip()
    baseline = row["baseline_response"].strip()
    anti = row["anti_underanswer_response"].strip()

    if family == "baseline_from_minimal_task_primary_minanchor":
        chosen = baseline
        rejected = minimal
        source_pair = ["baseline_response", "minimal_boundary_response"]
        if not is_clean_midpoint_candidate(chosen, rejected):
            return None
    elif family == "one_layer_from_minimal_task_primary_minanchor":
        chosen = first_sentence(anti)
        rejected = minimal
        source_pair = ["anti_underanswer_response:first_sentence", "minimal_boundary_response"]
        if not is_clean_one_layer_candidate(chosen, rejected):
            return None
    else:
        raise ValueError(f"unknown family: {family}")

    return {
        "example_id": row["example_id"],
        "language": row.get("language", "zh"),
        "category": row.get("category", "unknown"),
        "preference_family": family,
        "prompt_messages": [
            {"role": "system", "content": MINIMAL_SYSTEM},
            {"role": "user", "content": row["user_text"]},
        ],
        "chosen": chosen,
        "rejected": rejected,
        "requested_boundary": row.get("requested_boundary", ""),
        "source_pair": source_pair,
        "chosen_char_length": len(chosen),
        "rejected_char_length": len(rejected),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="directional_control_research/mechanism_experiment/data/train_triplets_v5_clean_240.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        default="directional_control_research/mechanism_experiment/data/built_pref_v2",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--medium-n", type=int, default=40)
    args = parser.parse_args()

    rows = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                if row.get("category") == "task_primary":
                    rows.append(row)

    if not rows:
        raise ValueError("no task_primary rows found")

    out_dir = Path(args.output_dir)
    families = [
        (
            "baseline_from_minimal_task_primary_minanchor",
            "preference_cleaner_baseline_from_minimal_task_primary_minanchor_v2_train.jsonl",
        ),
        (
            "one_layer_from_minimal_task_primary_minanchor",
            "preference_cleaner_one_layer_from_minimal_task_primary_minanchor_v2_train.jsonl",
        ),
    ]

    for family, fname in families:
        records = [rec for row in rows if (rec := build_record(row, family)) is not None]
        write_jsonl(out_dir / fname, records)
        medium = sample_records(records, n=min(args.medium_n, len(records)), seed=args.seed)
        medium_name = fname.replace("_train.jsonl", f"_train_medium{len(medium)}.jsonl")
        write_jsonl(out_dir / medium_name, medium)
        print(f"{family}: full={len(records)} medium={len(medium)}")


if __name__ == "__main__":
    main()
BASIC_SEPARATORS = {chr(0x3002), chr(0xFF01), chr(0xFF1F), "!", "?", ";", chr(0xFF1B)}
ZH_QUESTION = chr(0xFF1F)
