import json
from pathlib import Path


TRAIN_CASE_IDS = [
    "task_mail_reply_priority_001",
    "task_deadline_blocker_001",
    "mwz_booking_clarify_002",
    "clarify_resume_polish_001",
    "clarify_trip_packing_001",
    "clarify_study_restart_001",
    "clarify_room_search_001",
    "clarify_gift_choice_001",
]

REQUESTED_BOUNDARY = {
    "task_primary": "先回答当前核心问题或给一个重点判断，不要直接展开成完整方案。",
    "clarify_next_step": "先推进到下一步，只问最关键的一个问题或给出第一步，不要铺开完整规划。",
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

BASELINE_OVERRIDES = {
    "clarify_study_restart_001": "第一步先定一个最轻的重新开始动作，比如十分钟单词或一小段听力。先动比先规划更重要。",
    "clarify_room_search_001": "第一步先定最不能妥协的上限，通常是预算上限或通勤上限。先把这个钉住，再看别的条件。",
    "clarify_gift_choice_001": "第一步先定礼物方向，是偏实用、偏心意，还是偏好玩。方向一清楚，后面就容易选。",
}

ANSWER_FIRST = {
    "task_mail_reply_priority_001": "先看哪封邮件更容易卡住事情。通常先回老板的，除非合作方那封带着更近、更明确的截止点。",
    "task_deadline_blocker_001": "先碰最容易写出几行内容的那一块。通常从结构或最粗的开头开始，目的是先动起来。",
    "mwz_booking_clarify_002": "先定预算还是位置里更硬的那个。哪个更不能妥协，就先定哪个。",
    "clarify_resume_polish_001": "先看最想保留、也最想改的一段。先把最需要动的那一块挑出来。",
    "clarify_trip_packing_001": "先确认天气和行程安排。这个点一确定，后面收东西会顺很多。",
    "clarify_study_restart_001": "先定一个最轻的重新开始动作，比如十分钟单词或一小段听力。先动比先规划更重要。",
    "clarify_room_search_001": "先定最不能妥协的上限，通常是预算上限或通勤上限。先把这个钉住。",
    "clarify_gift_choice_001": "先定礼物方向，是偏实用、偏心意，还是偏好玩。方向一清楚，后面就容易选。",
}

CLARIFY_FIRST = {
    "task_mail_reply_priority_001": "这两封里哪一封更接近明确的截止点？如果现在还说不准，我会先回更可能卡住人的那封，通常先回老板的。",
    "task_deadline_blocker_001": "你现在手里哪一块最容易先写出三到五行？如果一时答不上来，我会先写结构或最粗的开头，让自己动起来。",
    "mwz_booking_clarify_002": "这次你更不想妥协的是预算还是位置？如果先按现有信息推进，我会先把更硬的那个条件定下来。",
    "clarify_resume_polish_001": "你现在最想改、也最容易下手的是哪一段？如果先不细分，我会先看最想保留但又最不满意的那段。",
    "clarify_trip_packing_001": "这两天里哪一段安排最不确定，或者天气还没看？如果先不展开，我会先确认天气和行程。",
    "clarify_study_restart_001": "你现在更能接受的是十分钟单词，还是一小段听力？如果先只定第一步，我会先选最轻的那个。",
    "clarify_room_search_001": "预算上限和通勤上限里，哪个更不能松？如果先只定一个，我会先定更硬的上限。",
    "clarify_gift_choice_001": "你这次更想送实用的，还是更想表达心意？如果先只走一步，我会先把礼物方向定下来。",
}


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    dcr_root = repo_root / "directional_control_research"
    canonical_path = dcr_root / "cases" / "paper_cases_directional_control_canonical_pool_24.json"
    v5_path = dcr_root / "mechanism_experiment" / "data" / "train_triplets_v5_clean_240.jsonl"
    out_path = repo_root / "resume" / "clarify_v2" / "train_triplets_clarify_axis_v2_clean_160.jsonl"

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
        baseline_response = baseline_by_case[case_id] if case_id in baseline_by_case else BASELINE_OVERRIDES[case_id]
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
                "baseline_response": baseline_response,
                "clarify_first_response": CLARIFY_FIRST[case_id],
                "answer_first_response": ANSWER_FIRST[case_id],
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} triplets to {out_path}")


if __name__ == "__main__":
    main()
