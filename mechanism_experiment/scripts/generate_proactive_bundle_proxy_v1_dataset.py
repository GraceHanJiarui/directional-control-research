import json
from pathlib import Path

INPUT_PATH = Path("directional_control_research/mechanism_experiment/data/train_triplets_v5_clean_240.jsonl")
OUTPUT_PATH = Path("directional_control_research/mechanism_experiment/data/built_q6/proactive_bundle_proxy_v1_train.jsonl")

SYSTEM_PROMPT = "You are a helpful assistant. Answer the user directly and proportionately for the current turn."

CATEGORY_APPEND = {
    "task_primary": "如果还要往前推进，下一步只补一个你现在最该看的判断点。",
    "clarify_next_step": "如果还要继续推进，先只定一个最关键条件。",
    "practical_troubleshooting": "如果这一步没解决，下一步只再检查一项。",
    "low_support_presence": "如果还要往下接，只补一句自然的提醒就够了。",
}


def build_assistant_text(row: dict) -> str:
    base = row["baseline_response"].strip()
    extra = CATEGORY_APPEND.get(row.get("category", ""), "如果还要继续推进，下一步只补一个最小动作。")
    if base.endswith(("。", "！", "？")):
        return f"{base}{extra}"
    return f"{base}。{extra}"


def build_record(row: dict) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": row["user_text"]},
            {"role": "assistant", "content": build_assistant_text(row)},
        ],
        "example_id": row["example_id"],
        "language": row.get("language", "zh"),
        "category": row.get("category", "unknown"),
        "target_style": "proactive_bundle_proxy_v1",
        "requested_boundary": row.get("requested_boundary", ""),
        "source_case_id": row.get("source_case_id", row["example_id"]),
        "source_response_key": "baseline_response_plus_short_bundle_append",
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with INPUT_PATH.open("r", encoding="utf-8") as f_in, OUTPUT_PATH.open("w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            rec = build_record(row)
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
    print(f"wrote {count} rows -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
