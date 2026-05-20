import json
from pathlib import Path


TRAIN_CASE_IDS = [
    "mwz_transport_decision_002",
    "task_mail_reply_priority_001",
    "task_deadline_blocker_001",
    "mwz_booking_clarify_002",
    "clarify_resume_polish_001",
    "clarify_trip_packing_001",
    "ed_presence_over_fixing_002",
    "ed_minor_loneliness_001",
    "ed_post_argument_001",
    "troubleshoot_wifi_drop_001",
    "troubleshoot_printer_001",
    "troubleshoot_app_crash_001",
]

REQUESTED_BOUNDARY = {
    "task_primary": "先回答当前核心问题或给一个重点判断，不要直接展开成完整方案。",
    "clarify_next_step": "先推进到下一步，只问最关键的一个问题或给出第一步，不要铺开完整规划。",
    "low_support_presence": "先陪住当前情绪，不分析、不解决、不过度安慰。",
    "practical_troubleshooting": "先给一个最先排查的方向，不展开完整排障树。",
}

AFFECT_TARGETS = {
    "mwz_transport_decision_002": {
        "attuned": "你是想先抓一个稳妥判断，对吧。那我会先看准点风险；如果时间卡得紧，我会优先高铁，只有去车站特别折腾时才更偏向打车。",
        "flat": "先看准点风险。时间紧就优先高铁，只有去车站特别折腾时再偏向打车。",
    },
    "task_mail_reply_priority_001": {
        "attuned": "你现在是想先把优先级理顺，不想被一整套策略压过来。那我会先看谁更容易把事情卡住；大多数情况下先回老板的，除非合作方那封更急。",
        "flat": "先看谁更容易把事情卡住。一般先回老板的，除非合作方那封更急。",
    },
    "task_deadline_blocker_001": {
        "attuned": "你现在更需要一个能立刻动起来的起点。那我会先碰最容易产出可见内容的一块，比如先搭结构或先写开头。",
        "flat": "先碰最容易产出可见内容的一块，比如先搭结构或先写开头。",
    },
    "mwz_booking_clarify_002": {
        "attuned": "这种时候先抓硬约束会轻松很多。第一步先定预算或位置里更不能妥协的那个。",
        "flat": "第一步先定预算或位置里更不能妥协的那个。",
    },
    "clarify_resume_polish_001": {
        "attuned": "你现在更需要先收住范围。第一步先找出最需要动的一段，别整份一起看。",
        "flat": "第一步先找出最需要动的一段，别整份一起看。",
    },
    "clarify_trip_packing_001": {
        "attuned": "先抓那个最能决定后面收法的点就行。第一步先确认天气和行程安排。",
        "flat": "第一步先确认天气和行程安排。",
    },
    "ed_presence_over_fixing_002": {
        "attuned": "好，我先不分析，也不急着给办法。我在这儿陪你一下。现在更像累，还是只是有点空？",
        "flat": "好，那我先不分析，也不解决。现在更像累，还是只是有点空？",
    },
    "ed_minor_loneliness_001": {
        "attuned": "嗯，我接住你这句。那种屋里一下子空下来的感觉，晚上确实会更明显。",
        "flat": "嗯。那种屋里一下子空下来的感觉，晚上会更明显。",
    },
    "ed_post_argument_001": {
        "attuned": "好，我先不复盘。刚吵完脑子还在嗡，这种状态很正常。",
        "flat": "先不复盘。刚吵完脑子还在嗡，这很正常。",
    },
    "troubleshoot_wifi_drop_001": {
        "attuned": "这种断断续续最烦人，但先抓第一步就行。先看断网时路由器指示灯有没有一起异常。",
        "flat": "先看断网时路由器指示灯有没有异常。",
    },
    "troubleshoot_printer_001": {
        "attuned": "先别把排障树全铺开。第一步先看纸张有没有正常进到进纸位。",
        "flat": "先看纸张有没有正常进到进纸位。",
    },
    "troubleshoot_app_crash_001": {
        "attuned": "先把现象固定住就行。先确认它是不是每次一打开就立刻闪退。",
        "flat": "先确认它是不是每次一打开就立刻闪退。",
    },
}

WRAPPERS = [
    "{body}",
    "我把这轮情况一次说完：{body}",
    "按我这轮说的范围来回我：{body}",
    "我现在的情况是：{body}",
    "就按这个当前问题回我：{body}",
]

BODY_BUILDERS = [
    lambda turns: " ".join(turns),
    lambda turns: "\n".join(turns),
    lambda turns: "\n".join(turns[:4]),
    lambda turns: " / ".join(turns),
]


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    dcr_root = repo_root / "directional_control_research"
    canonical_path = dcr_root / "cases" / "paper_cases_directional_control_canonical_pool_24.json"
    v5_path = dcr_root / "mechanism_experiment" / "data" / "train_triplets_v5_clean_240.jsonl"
    out_path = repo_root / "resume" / "affect_v1" / "train_triplets_affect_v1_clean_240.jsonl"

    cases = json.loads(canonical_path.read_text(encoding="utf-8-sig"))
    case_map = {row["case_id"]: row for row in cases}

    baseline_by_case = {}
    with v5_path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            row = json.loads(line)
            source_case_id = row["source_case_id"]
            if source_case_id not in baseline_by_case:
                baseline_by_case[source_case_id] = row["baseline_response"]

    rows = []
    for case_id in TRAIN_CASE_IDS:
        case = case_map[case_id]
        if case_id not in baseline_by_case:
            raise KeyError(f"missing baseline response for {case_id}")
        targets = AFFECT_TARGETS[case_id]
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
                "baseline_response": baseline_by_case[case_id],
                "affect_attuned_response": targets["attuned"],
                "affect_flat_response": targets["flat"],
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} triplets to {out_path}")


if __name__ == "__main__":
    main()
