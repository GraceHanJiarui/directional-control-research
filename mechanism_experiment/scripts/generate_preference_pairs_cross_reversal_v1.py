import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

ANTI_SYSTEM = (
    "You are a helpful assistant. Avoid under-answering. "
    "If a concise reply may feel insufficient, add a bit more useful detail or a light follow-up."
)
MINIMAL_SYSTEM = (
    "You are a helpful assistant. Respect the user's current-turn boundary. "
    "Answer the current question first. Stay minimal. Do not add unasked-for help unless clearly requested."
)


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def sample_balanced(records, per_category, seed):
    by_category = defaultdict(list)
    for rec in records:
        by_category[rec["category"]].append(rec)

    rng = random.Random(seed)
    out = []
    for category in sorted(by_category):
        bucket = list(by_category[category])
        if len(bucket) < per_category:
            raise ValueError(f"category {category} only has {len(bucket)} records; need {per_category}")
        rng.shuffle(bucket)
        out.extend(bucket[:per_category])
    return out


def is_clean_cross_minimal_from_anti(row):
    chosen = row["minimal_boundary_response"].strip()
    rejected = row["anti_underanswer_response"].strip()
    gap = len(rejected) - len(chosen)
    return chosen != rejected and 12 <= gap <= 90


def is_clean_cross_expand_from_minimal(row):
    chosen = row["anti_underanswer_response"].strip()
    rejected = row["minimal_boundary_response"].strip()
    gap = len(chosen) - len(rejected)
    banned = ["如果你愿意", "我可以再", "你可以告诉我", "要不要"]
    return (
        chosen != rejected
        and 12 <= gap <= 45
        and "？" not in chosen
        and "?" not in chosen
        and not any(marker in chosen for marker in banned)
    )


def build_record(row, family):
    if family == "cross_expand_from_minimal":
        if not is_clean_cross_expand_from_minimal(row):
            return None
        chosen = row["anti_underanswer_response"].strip()
        rejected = row["minimal_boundary_response"].strip()
        source_pair = ["anti_underanswer_response", "minimal_boundary_response"]
        system_prompt = MINIMAL_SYSTEM
    elif family == "cross_minimal_from_anti":
        if not is_clean_cross_minimal_from_anti(row):
            return None
        chosen = row["minimal_boundary_response"].strip()
        rejected = row["anti_underanswer_response"].strip()
        source_pair = ["minimal_boundary_response", "anti_underanswer_response"]
        system_prompt = ANTI_SYSTEM
    else:
        raise ValueError(f"unknown family: {family}")

    return {
        "example_id": row["example_id"],
        "language": row.get("language", "zh"),
        "category": row.get("category", "unknown"),
        "preference_family": family,
        "prompt_messages": [
            {"role": "system", "content": system_prompt},
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
    parser.add_argument("--medium-per-category", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rows = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    families = [
        ("cross_expand_from_minimal", "preference_cross_expand_from_minimal_pairs_v2_train.jsonl"),
        ("cross_minimal_from_anti", "preference_cross_minimal_from_anti_pairs_v2_train.jsonl"),
    ]

    for family, filename in families:
        records = [rec for row in rows if (rec := build_record(row, family)) is not None]
        write_jsonl(out_dir / filename, records)
        medium_records = sample_balanced(records, per_category=args.medium_per_category, seed=args.seed)
        medium_name = filename.replace("_train.jsonl", "_train_medium160.jsonl")
        write_jsonl(out_dir / medium_name, medium_records)
        print(f"wrote {len(records)} -> {out_dir / filename}")
        print(f"wrote {len(medium_records)} -> {out_dir / medium_name}")


if __name__ == "__main__":
    main()
