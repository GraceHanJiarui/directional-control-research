import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from directional_control_research.mechanism_experiment.scripts.generate_caveat_axis_v1_triplets import (
    BASELINE_RESPONSE,
    BODY_BUILDERS,
    NO_EXTRA_CAVEAT,
    REQUESTED_BOUNDARY,
    TRAIN_CASE_IDS,
    WRAPPERS,
)
from directional_control_research.mechanism_experiment.scripts.generate_caveat_axis_v2_triplets import SHORT_CAVEATS


V3_CASES = {
    "troubleshoot_ram_blackscreen_001": "不过，动手前先断电，不然可能把主板再碰坏。",
    "used_laptop_seller_001": "不过，要是不能当面开机验机，就别继续谈。",
    "coworker_punch_in_001": "不过，一旦被认定代打卡，你也会一起担责。",
}


def make_more_complete(case_id: str) -> str:
    baseline = BASELINE_RESPONSE[case_id].strip()
    caveat = V3_CASES.get(case_id, SHORT_CAVEATS[case_id]).strip()
    if baseline.endswith(("。", "！", "？")):
        return f"{baseline}{caveat}"
    return f"{baseline}。{caveat}"


def main() -> None:
    spec_path = REPO_ROOT / "resume" / "external_multi_axis_controllability_v4_merged.json"
    out_path = REPO_ROOT / "resume" / "caveat_v3" / "train_triplets_caveat_axis_v3_clean_240.jsonl"

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    case_map = {row["case_id"]: row for row in spec["cases"]}

    rows = []
    for case_id in TRAIN_CASE_IDS:
        case = case_map[case_id]
        variants = []
        for wrapper in WRAPPERS:
            for body_builder in BODY_BUILDERS:
                variants.append(wrapper.format(body=body_builder(case["turns"]).strip()).strip())
        for idx, user_text in enumerate(variants, start=1):
            rows.append({
                "example_id": f"{case_id}__v{idx}",
                "language": "zh",
                "category": case["category"],
                "source_case_id": case_id,
                "user_text": user_text,
                "requested_boundary": REQUESTED_BOUNDARY[case["category"]],
                "baseline_response": BASELINE_RESPONSE[case_id],
                "more_complete_caveat_response": make_more_complete(case_id),
                "no_extra_caveat_response": NO_EXTRA_CAVEAT[case_id],
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} triplets to {out_path}")


if __name__ == "__main__":
    main()
