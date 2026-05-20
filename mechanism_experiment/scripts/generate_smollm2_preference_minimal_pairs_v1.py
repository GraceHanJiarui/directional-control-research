import argparse
import json
from pathlib import Path

ANTI_SYSTEM = (
    "You are a helpful assistant. Avoid under-answering. "
    "If a concise reply may feel insufficient, add a bit more useful detail or a light follow-up."
)


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="directional_control_research/mechanism_experiment/data/train_triplets_en_v2_64.jsonl",
    )
    parser.add_argument(
        "--output",
        default="resume/smollm2_pref_v1/preference_cross_minimal_from_anti_pairs_en_v1_train.jsonl",
    )
    args = parser.parse_args()

    rows = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            rows.append(
                {
                    "example_id": row["example_id"],
                    "language": row.get("language", "en"),
                    "category": row.get("category", "unknown"),
                    "preference_family": "cross_minimal_from_anti_en",
                    "prompt_messages": [
                        {"role": "system", "content": ANTI_SYSTEM},
                        {"role": "user", "content": row["user_text"]},
                    ],
                    "chosen": row["minimal_boundary_response"].strip(),
                    "rejected": row["anti_underanswer_response"].strip(),
                    "requested_boundary": row.get("requested_boundary", ""),
                    "source_pair": ["minimal_boundary_response", "anti_underanswer_response"],
                    "chosen_char_length": len(row["minimal_boundary_response"].strip()),
                    "rejected_char_length": len(row["anti_underanswer_response"].strip()),
                    "source_case_id": row.get("source_case_id", row["example_id"]),
                }
            )

    out_path = Path(args.output)
    write_jsonl(out_path, rows)
    print(f"wrote {len(rows)} records to {out_path}")


if __name__ == "__main__":
    main()
