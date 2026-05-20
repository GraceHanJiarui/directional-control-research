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


SHORT_CAVEATS = {
    "mwz_concept_explain_001": "不过，这说的是普遍涨价，不是某一样东西临时变贵。",
    "troubleshoot_ram_blackscreen_001": "不过，动手前先断电，别把主板再碰坏。",
    "troubleshoot_phone_storage_001": "不过，重要照片先备份，别清完才发现只剩这一份。",
    "dd_everyday_choice_caveat_001": "不过，如果你已经累到会影响明天状态，就先补觉。",
    "purchase_laptop_wait_001": "不过，等一等不一定更便宜，也可能碰上缺货。",
    "finance_subscriptions_001": "不过，扣款名有时不是服务本名，别只看商户字面。",
    "used_laptop_seller_001": "不过，要是不能当面验机，就别继续谈。",
    "rental_deposit_001": "不过，没核实身份和合同前先转定金，风险很高。",
    "friend_borrow_money_001": "不过，真要借的话，最好留个简单记录。",
    "coworker_punch_in_001": "不过，一旦被认定代打卡，你也会一起担责。",
    "subscription_cancel_001": "不过，取消前先确认会不会丢数据，或者卡在年付周期里。",
    "package_delay_refund_001": "不过，申请时记得把订单和聊天记录一起留好。",
}


def make_more_complete(case_id: str) -> str:
    baseline = BASELINE_RESPONSE[case_id].strip()
    caveat = SHORT_CAVEATS[case_id].strip()
    if baseline.endswith(("。", "！", "？")):
        return f"{baseline}{caveat}"
    return f"{baseline}。{caveat}"


def main() -> None:
    spec_path = REPO_ROOT / "resume" / "external_multi_axis_controllability_v4_merged.json"
    out_path = REPO_ROOT / "resume" / "caveat_v2" / "train_triplets_caveat_axis_v2_clean_240.jsonl"

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
