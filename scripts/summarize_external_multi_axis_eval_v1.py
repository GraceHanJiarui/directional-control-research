import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    in_path = Path(args.input)
    rows = []
    with in_path.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            rows.append(json.loads(raw))

    grouped = defaultdict(list)
    for row in rows:
        key = (row["model_name"], row["axis_id"], row["mode_key"])
        grouped[key].append(int(row["char_length"]))

    summary = []
    for (model_name, axis_id, mode_key), vals in sorted(grouped.items()):
        summary.append({
            "model_name": model_name,
            "axis_id": axis_id,
            "mode_key": mode_key,
            "n": len(vals),
            "mean_char_length": round(sum(vals) / len(vals), 2),
            "median_char_length": round(statistics.median(vals), 2),
        })

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
