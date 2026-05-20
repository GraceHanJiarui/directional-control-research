import json
from pathlib import Path


TRAIN_CASE_IDS = [
    "dd_everyday_choice_002",
    "mwz_transport_decision_002",
    "mwz_concept_explain_001",
    "task_mail_reply_priority_001",
    "task_deadline_blocker_001",
    "bucket_seed_task_primary_002",
    "mwz_booking_clarify_002",
    "clarify_resume_polish_001",
    "clarify_trip_packing_001",
    "clarify_study_restart_001",
    "clarify_room_search_001",
    "clarify_gift_choice_001",
    "troubleshoot_ram_blackscreen_001",
    "troubleshoot_phone_storage_001",
    "troubleshoot_wifi_drop_001",
    "troubleshoot_printer_001",
    "troubleshoot_app_crash_001",
    "troubleshoot_battery_drain_001",
]

REQUESTED_BOUNDARY = {
    "task_primary": "先回答当前核心问题或给一个重点判断，不要直接展开成完整方案。",
    "clarify_next_step": "先推进到下一步，只问最关键的一个问题或给出第一步，不要铺开完整规划。",
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

BASELINE_OVERRIDES = {
    "dd_everyday_choice_002": "我会先看你现在更缺休息，还是更想出去换一口气。要是这周已经很累，我会偏向先补觉；如果身体还行，而且你对那个展本身挺想去，就去看展。",
    "mwz_concept_explain_001": "你可以把通货膨胀先理解成：同样的钱，后来能买到的东西变少了。比如以前二十块能买一顿饭，过一阵可能只够买差一点的。",
    "bucket_seed_task_primary_002": "如果只是先把事情动起来，我会先选更省脑子的那个，比如先洗澡或者先把饭最耗时的部分开起来。关键不是哪件更正确，而是哪件最容易先让你动。",
    "clarify_study_restart_001": "第一步先别做规划，先定一个最轻的重新开始动作，比如今天只做十分钟单词或听一小段英语。",
    "clarify_room_search_001": "第一步先定最不能妥协的一条，比如预算上限、通勤上限，或者必须在哪个区。",
    "clarify_gift_choice_001": "第一步先定送礼的方向，是偏实用、偏表达心意，还是偏好玩。",
    "troubleshoot_ram_blackscreen_001": "最先先做两件事：确认内存条有没有插到底、卡扣有没有完全扣住；如果可以，再只留新内存单独试一次。",
    "troubleshoot_phone_storage_001": "最优先先看是照片视频占得最多，还是应用和缓存占得最多，先分清大头在哪。",
    "troubleshoot_battery_drain_001": "最先先确认最近是不是有某个应用或系统进程异常耗电，先去电池使用统计里看谁排在最前面。",
}

DECISIVE = {
    "dd_everyday_choice_002": "我会先看你现在更缺休息，还是更想出去换一口气。要是这周已经很累，就先补觉；身体还行而且你对那个展真想去，就去看展。",
    "mwz_transport_decision_002": "先看准点风险。时间卡得紧就优先高铁；只有去车站特别折腾、而且那个时段路况相对稳的时候，才偏向打车。",
    "mwz_concept_explain_001": "直接理解成一件事：同样的钱，后来能买到的东西变少了。比如以前二十块能买一顿饭，过一阵可能只能买差一点的。",
    "task_mail_reply_priority_001": "先看谁会先把事情卡住。大多数情况下先回老板的；只有合作方那封更急、更可能拖住后续时，才先回合作方。",
    "task_deadline_blocker_001": "先碰最容易产出可见内容的一块，比如先搭结构或先起一个粗开头，让自己动起来。",
    "bucket_seed_task_primary_002": "如果只是先把事情动起来，我会先选更省脑子的那个，比如先洗澡或者先把饭最耗时的部分开起来。先动比先想清更重要。",
    "mwz_booking_clarify_002": "第一步先定预算或位置里更不能妥协的那个，先抓硬约束。",
    "clarify_resume_polish_001": "第一步先找最需要动的一段，别整份一起看。",
    "clarify_trip_packing_001": "第一步先确认天气和行程安排，这一步最先定。",
    "clarify_study_restart_001": "第一步先别做规划，今天只定一个最轻的重新开始动作，比如十分钟单词或一小段听力。",
    "clarify_room_search_001": "第一步先定最不能妥协的一条，比如预算上限或通勤上限。",
    "clarify_gift_choice_001": "第一步先定礼物方向，是偏实用、偏心意，还是偏好玩。",
    "troubleshoot_ram_blackscreen_001": "先查两件事：内存条有没有插到底，卡扣有没有完全扣住；如果可以，再只留新内存单独试一次。",
    "troubleshoot_phone_storage_001": "先去看存储里谁占得最多，先分清是照片视频，还是应用和缓存。",
    "troubleshoot_wifi_drop_001": "先看断网时路由器指示灯有没有一起异常，先分清是路由器侧掉，还是设备侧掉。",
    "troubleshoot_printer_001": "第一步先看纸张是不是已经正常进到进纸位，先排最直接的进纸问题。",
    "troubleshoot_app_crash_001": "先确认它是不是每次一打开就立刻闪退，先把现象固定住。",
    "troubleshoot_battery_drain_001": "先去电池使用统计里看谁排在最前面，先确认是不是有异常耗电的大头。",
}

DEFERENTIAL = {
    "dd_everyday_choice_002": "如果只是先抓一个稳妥判断，我会先看你现在更缺休息，还是更想出去换一口气。按现有信息，如果这周已经很累，可能先补觉更合适；如果身体状态还行，而且你对那个展本身挺想去，再去看展也说得通。",
    "mwz_transport_decision_002": "如果先抓一个保守判断，我会先看准点风险。按现有信息，时间卡得紧时通常高铁更稳；不过如果去车站特别折腾，而且那个时段路况相对稳，打车也未必不合适。",
    "mwz_concept_explain_001": "如果先用一个容易抓住的说法，你可以把它理解成：同样的钱，后来能买到的东西变少了。比如以前二十块能买一顿饭，过一阵可能只能买差一点的，大概就是这个意思。",
    "task_mail_reply_priority_001": "如果先用一个不太容易出错的标准，我会先看谁更容易把事情卡住。按常见情况，多半会先回老板的；不过如果合作方那封已经更急，先回合作方也合理。",
    "task_deadline_blocker_001": "如果只是先把自己带起来，我会倾向先碰最容易产出可见内容的一块，比如先搭结构或起一个粗开头。这样通常比较容易继续往下走。",
    "bucket_seed_task_primary_002": "如果只是先把事情往前推一点，我会倾向先选更省脑子的那个，比如先洗澡，或者先把做饭里最耗时的部分开起来。这样通常比较容易让节奏动起来。",
    "mwz_booking_clarify_002": "如果先抓最关键的一步，我会倾向先定预算或位置里更不能妥协的那个。通常先抓硬约束，后面会更容易收窄。",
    "clarify_resume_polish_001": "如果先收住范围，我会倾向先看最需要动的一段，而不是整份一起改。这样通常更容易开始。",
    "clarify_trip_packing_001": "如果先定一个最关键的点，我会先确认天气和行程安排。大多数情况下这一步能先把后面带什么收住。",
    "clarify_study_restart_001": "如果先只定第一步，我会倾向今天先放一个很轻的重新开始动作，比如十分钟单词或一小段听力，而不是先做规划。",
    "clarify_room_search_001": "如果先抓最关键的一条，我会先定最不能妥协的限制，比如预算上限或通勤上限。通常这样最容易把后面范围收窄。",
    "clarify_gift_choice_001": "如果先只定第一步，我会先想清礼物方向，是偏实用、偏心意，还是偏好玩。先把方向定住，后面通常更容易选。",
    "troubleshoot_ram_blackscreen_001": "如果先排最常见的原因，我会先看内存条有没有插到底、卡扣有没有完全扣住；如果条件允许，再只留新内存单独试一次，这样通常比较容易先分层。",
    "troubleshoot_phone_storage_001": "如果先抓最优先的一步，我会先去看是谁占得最多，先分清是照片视频，还是应用和缓存。先把大头找出来通常比较省事。",
    "troubleshoot_wifi_drop_001": "如果先抓一个最有效的排查点，我会先看断网时路由器指示灯有没有一起异常。这样通常能先分清是路由器侧掉，还是设备侧掉。",
    "troubleshoot_printer_001": "如果先排最直接的一层，我会先看纸张是不是已经正常进到进纸位。没有报错时，先排进纸问题通常最划算。",
    "troubleshoot_app_crash_001": "如果先固定现象，我会先看它是不是每次一打开就立刻闪退。先分清是不是稳定复现，后面通常更好判断。",
    "troubleshoot_battery_drain_001": "如果先抓最优先的一步，我会先去电池使用统计里看谁排在最前面。先找到耗电大头，通常比较容易往下排。",
}


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    dcr_root = repo_root / "directional_control_research"
    canonical_path = dcr_root / "cases" / "paper_cases_directional_control_canonical_pool_24.json"
    v5_path = dcr_root / "mechanism_experiment" / "data" / "train_triplets_v5_clean_240.jsonl"
    out_path = repo_root / "resume" / "stance_v1" / "train_triplets_stance_v1_clean_360.jsonl"

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
                "deferential_uncertain_response": DEFERENTIAL[case_id],
                "decisive_direct_response": DECISIVE[case_id],
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} triplets to {out_path}")


if __name__ == "__main__":
    main()
