import argparse
import json
from pathlib import Path

BASELINE_SYSTEM = "You are a helpful assistant. Answer the user directly and proportionately for the current turn."


def build_record(row, family):
    user_text = row["user_text"]
    if family == "expand":
        chosen = row["anti_underanswer_response"]
        rejected = row["baseline_response"]
        source_pair = ["anti_underanswer_response", "baseline_response"]
    elif family == "minimal":
        chosen = row["minimal_boundary_response"]
        rejected = row["baseline_response"]
        source_pair = ["minimal_boundary_response", "baseline_response"]
    else:
        raise ValueError(f"unknown family: {family}")

    return {
        "example_id": row["example_id"],
        "language": row.get("language", "zh"),
        "category": row.get("category", "unknown"),
        "preference_family": family,
        "prompt_messages": [
            {"role": "system", "content": BASELINE_SYSTEM},
            {"role": "user", "content": user_text},
        ],
        "chosen": chosen,
        "rejected": rejected,
        "requested_boundary": row.get("requested_boundary", ""),
        "source_pair": source_pair,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="directional_control_research/mechanism_experiment/data/train_triplets_v5_clean_240.jsonl")
    parser.add_argument("--output-dir", default="directional_control_research/mechanism_experiment/data/built_pref_v1")
    args = parser.parse_args()

    rows = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for family, name in [("expand", "preference_expand_pairs_v1_train.jsonl"), ("minimal", "preference_minimal_pairs_v1_train.jsonl")]:
        records = [build_record(row, family) for row in rows]
        with open(out_dir / name, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"wrote {len(records)} -> {out_dir / name}")


if __name__ == "__main__":
    main()
