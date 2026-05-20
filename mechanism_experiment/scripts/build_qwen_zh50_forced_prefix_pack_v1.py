import argparse
import json
from pathlib import Path


SOURCE_MODE = "baseline_relational_instruction_scope_minimal_sufficient"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_jsonl(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--heldout-json", required=True)
    parser.add_argument("--minimal-jsonl", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    heldout_rows = load_json(Path(args.heldout_json))
    minimal_rows = load_jsonl(Path(args.minimal_jsonl))

    prefix_by_case = {}
    for row in minimal_rows:
        if row.get("experiment_mode") != SOURCE_MODE:
            continue
        prefix_by_case[row["case_id"]] = {
            "assistant_prefix": row["assistant_text"].strip(),
            "user_text": row["user_text"],
        }

    output_rows = []
    for row in heldout_rows:
        case_id = row["case_id"]
        if case_id not in prefix_by_case:
            raise KeyError(f"Missing minimal scope prefix for case_id={case_id}")
        prefix = prefix_by_case[case_id]["assistant_prefix"]
        if not prefix:
            raise ValueError(f"Empty prefix for case_id={case_id}")
        output_rows.append(
            {
                "probe_id": f"zh50_fp_{case_id}",
                "case_id": case_id,
                "category": row["category"],
                "probe_focus": "derived_from_minimal_boundary_scope_minimal_sufficient",
                "assistant_prefix": prefix,
                "turns": row["turns"],
            }
        )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(output_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
