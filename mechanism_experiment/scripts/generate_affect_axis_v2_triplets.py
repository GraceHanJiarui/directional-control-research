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


ATTTUNED_OVERRIDES = {
    "mwz_transport_decision_002": "你是在犹豫里想先抓一个稳妥判断，对吧。先看准点风险。如果时间卡得紧，我会优先高铁；只有去车站特别折腾、而且那个时段路况相对稳的时候，才更偏向打车。",
    "task_mail_reply_priority_001": "你现在是想先把优先级理顺，不想被整套策略带走。先看哪封邮件更容易卡住事情。大多数情况下我会先回老板的，除非合作方那封带着更明确、更近的截止点。",
    "task_deadline_blocker_001": "你现在更需要一个能立刻动起来的起点。先碰最容易产出可见内容的那一块，比如先写结构或者先起一个最粗的开头，让自己动起来。",
    "mwz_booking_clarify_002": "这种卡住很常见，先抓硬约束就会轻松很多。第一步先把预算还是位置这两个里更硬的那个定下来。哪个更不能妥协，就先定哪个。",
    "clarify_resume_polish_001": "你现在更需要先收住范围。第一步先看简历里最想保留、也最想改的一段是什么，先确定最需要动的那一块。",
    "clarify_trip_packing_001": "先抓那个最能决定后面收法的点就行。最先确认天气和行程安排，这两个点一确定，后面要带什么就会顺很多。",
    "ed_presence_over_fixing_002": "好，我先不帮你分析。我就在这儿陪你待两句。今天这种空掉的感觉，是更像累，还是更像什么都提不起兴趣？",
    "ed_minor_loneliness_001": "嗯，我接住你这句。那种屋里一下子很空的感觉，晚上会特别明显。",
    "ed_post_argument_001": "好，我先不复盘，也不讲大道理。刚吵完脑子还在响，很正常。",
    "troubleshoot_wifi_drop_001": "这种断断续续确实很烦人，但先抓第一步就行。先看是不是路由器本身在掉线。最先做的一步，就是观察断网时路由器的指示灯有没有一起异常。",
    "troubleshoot_printer_001": "先别把排障树全铺开。第一步先看纸张是不是已经正常进到进纸位，先排除最直接的卡纸或进纸失败。",
    "troubleshoot_app_crash_001": "先把现象固定住就行。先试最简单的一步：重启软件并确认是不是每次一打开就立刻闪退，先把现象固定下来。",
}

FLAT_OVERRIDES = {
    "mwz_transport_decision_002": "先看准点风险。如果时间卡得紧，我会优先高铁；只有去车站特别折腾、而且那个时段路况相对稳的时候，才更偏向打车。",
    "task_mail_reply_priority_001": "先看哪封邮件更容易卡住事情。大多数情况下我会先回老板的，除非合作方那封带着更明确、更近的截止点。",
    "task_deadline_blocker_001": "先碰最容易产出可见内容的那一块，比如先写结构或者先起一个最粗的开头，让自己动起来。",
    "mwz_booking_clarify_002": "第一步先把预算还是位置这两个里更硬的那个定下来。哪个更不能妥协，就先定哪个。",
    "clarify_resume_polish_001": "第一步先看简历里最想保留、也最想改的一段是什么，先确定最需要动的那一块。",
    "clarify_trip_packing_001": "最先确认天气和行程安排，这两个点一确定，后面要带什么就会顺很多。",
    "ed_presence_over_fixing_002": "好，我先不分析。现在更像累，还是更像什么都提不起兴趣？",
    "ed_minor_loneliness_001": "那种屋里一下子很空的感觉，晚上会特别明显。",
    "ed_post_argument_001": "先不复盘。刚吵完脑子还在响，很正常。",
    "troubleshoot_wifi_drop_001": "先看是不是路由器本身在掉线。最先做的一步，就是观察断网时路由器的指示灯有没有一起异常。",
    "troubleshoot_printer_001": "第一步先看纸张是不是已经正常进到进纸位，先排除最直接的卡纸或进纸失败。",
    "troubleshoot_app_crash_001": "先试最简单的一步：重启软件并确认是不是每次一打开就立刻闪退，先把现象固定下来。",
}


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    dcr_root = repo_root / "directional_control_research"
    canonical_path = dcr_root / "cases" / "paper_cases_directional_control_canonical_pool_24.json"
    v5_path = dcr_root / "mechanism_experiment" / "data" / "train_triplets_v5_clean_240.jsonl"
    out_path = repo_root / "resume" / "affect_v2" / "train_triplets_affect_v2_clean_240.jsonl"

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
                "affect_attuned_response": ATTTUNED_OVERRIDES[case_id],
                "affect_flat_response": FLAT_OVERRIDES[case_id],
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} triplets to {out_path}")


if __name__ == "__main__":
    main()
