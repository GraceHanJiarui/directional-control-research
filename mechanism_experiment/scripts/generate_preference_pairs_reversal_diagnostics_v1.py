import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

MINIMAL_SYSTEM = (
    "You are a helpful assistant. Respect the user's current-turn boundary. "
    "Answer the current question first. Stay minimal. Do not add unasked-for help unless clearly requested."
)

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


def has_bundled_marker(text: str) -> bool:
    return any(marker in text for marker in BANNED_BUNDLED_MARKERS)


def midpoint_candidate(row):
    chosen = row["baseline_response"].strip()
    rejected = row["minimal_boundary_response"].strip()
    gap = len(chosen) - len(rejected)
    return (
        chosen != rejected
        and 8 <= gap <= 28
        and "？" not in chosen
        and "?" not in chosen
        and not has_bundled_marker(chosen)
    )


def soft_expand_candidate(row, diff_cap, ratio_cap):
    chosen = row["anti_underanswer_response"].strip()
    rejected = row["minimal_boundary_response"].strip()
    diff = len(chosen) - len(rejected)
    ratio = len(chosen) / max(1, len(rejected))
    return (
        chosen != rejected
        and diff <= diff_cap
        and ratio <= ratio_cap
        and "？" not in chosen
        and "?" not in chosen
        and not has_bundled_marker(chosen)
    )


def build_record(row, family):
    if family == "cross_baseline_from_minimal":
        if not midpoint_candidate(row):
            return None
        chosen = row["baseline_response"].strip()
        rejected = row["minimal_boundary_response"].strip()
        source_pair = ["baseline_response", "minimal_boundary_response"]
    elif family == "cross_expand_soft_from_minimal":
        raise RuntimeError("cross_expand_soft_from_minimal should be prefiltered before build_record")
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
    parser.add_argument("--medium-per-category", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--soft-diff-cap", type=int, default=32)
    parser.add_argument("--soft-ratio-cap", type=float, default=1.8)
    args = parser.parse_args()

    rows = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    baseline_from_minimal = [rec for row in rows if (rec := build_record(row, "cross_baseline_from_minimal")) is not None]
    write_jsonl(out_dir / "preference_cross_baseline_from_minimal_pairs_v2_train.jsonl", baseline_from_minimal)
    baseline_from_minimal_medium = sample_balanced(baseline_from_minimal, per_category=args.medium_per_category, seed=args.seed)
    write_jsonl(
        out_dir / "preference_cross_baseline_from_minimal_pairs_v2_train_medium160.jsonl",
        baseline_from_minimal_medium,
    )

    soft_rows = [row for row in rows if soft_expand_candidate(row, diff_cap=args.soft_diff_cap, ratio_cap=args.soft_ratio_cap)]
    soft_expand = []
    for row in soft_rows:
        soft_expand.append(
            {
                "example_id": row["example_id"],
                "language": row.get("language", "zh"),
                "category": row.get("category", "unknown"),
                "preference_family": "cross_expand_soft_from_minimal",
                "prompt_messages": [
                    {"role": "system", "content": MINIMAL_SYSTEM},
                    {"role": "user", "content": row["user_text"]},
                ],
                "chosen": row["anti_underanswer_response"].strip(),
                "rejected": row["minimal_boundary_response"].strip(),
                "requested_boundary": row.get("requested_boundary", ""),
                "source_pair": ["anti_underanswer_response", "minimal_boundary_response"],
                "chosen_char_length": len(row["anti_underanswer_response"].strip()),
                "rejected_char_length": len(row["minimal_boundary_response"].strip()),
            }
        )
    write_jsonl(out_dir / "preference_cross_expand_soft_from_minimal_pairs_v2_train.jsonl", soft_expand)
    soft_expand_medium = sample_balanced(soft_expand, per_category=args.medium_per_category, seed=args.seed)
    write_jsonl(
        out_dir / "preference_cross_expand_soft_from_minimal_pairs_v2_train_medium160.jsonl",
        soft_expand_medium,
    )

    print(f"baseline_from_minimal full={len(baseline_from_minimal)} medium={len(baseline_from_minimal_medium)}")
    print(f"soft_expand_from_minimal full={len(soft_expand)} medium={len(soft_expand_medium)}")


if __name__ == "__main__":
    main()
