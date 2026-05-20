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

CLEAN_TARGETS = {
    "mwz_transport_decision_002": {
        "baseline": "先看准点风险。如果时间卡得紧，我会优先高铁；只有去车站特别折腾、而且那个时段路况相对稳的时候，才更偏向打车。",
        "anti": "先看准点风险和你去车站的折腾程度。一般来说，时间卡得紧时高铁更稳，因为不受堵车影响；如果你离车站远、换乘麻烦，而出发时段路况又比较可控，打车才会更方便一些。如果你愿意补一个出发点和预计出门时间，我可以再帮你收窄一点。",
        "minimal": "先看准点风险。时间紧就优先高铁，只有去车站很不方便时再偏向打车。",
    },
    "task_mail_reply_priority_001": {
        "baseline": "先看哪封邮件更容易卡住事情。大多数情况下我会先回老板的，除非合作方那封带着更明确、更近的截止点。",
        "anti": "先看谁更容易把后续工作卡住。通常老板那封优先级更高，因为它更可能影响你当前的内部节奏；但如果合作方那封已经在等确认、再拖就会影响外部推进，那就该先回合作方。你先按谁会先造成堵点这个标准判断，通常就不会错得太离谱。",
        "minimal": "先看谁会先卡住事情。一般先回老板的，除非合作方那封更急。",
    },
    "task_deadline_blocker_001": {
        "baseline": "先碰最容易产出可见内容的那一块，比如先写结构或者先起一个最粗的开头，让自己动起来。",
        "anti": "先碰最容易产出可见内容、又不用查太多资料的那一块，比如先搭结构、列小标题，或者先把你最确定的一段写出来。这样做的目的不是一次写好，而是先把我已经开始了这件事落地，后面再往里补会容易很多。",
        "minimal": "先碰最容易写出来的一块，比如先搭结构或写开头，让自己动起来。",
    },
    "mwz_booking_clarify_002": {
        "baseline": "第一步先把预算还是位置这两个里更硬的那个定下来。哪个更不能妥协，就先定哪个。",
        "anti": "第一步先分清预算和位置里，哪个是你的硬约束。因为这两个条件一旦先定住一个，后面可选范围就会明显缩小，接下来的筛选才不会散。通常如果预算差距会很影响选择，就先定预算；如果你已经大概知道想住哪一片，就先定位置。",
        "minimal": "第一步先定预算或位置里更不能妥协的那个，先抓硬约束。",
    },
    "clarify_resume_polish_001": {
        "baseline": "第一步先看简历里最想保留、也最想改的一段是什么，先确定最需要动的那一块。",
        "anti": "第一步先别想着整份一起改，先挑出最需要动的一块，通常是开头摘要、最近一段经历，或者最影响观感的那一段。你先把最想保留什么和最不满意什么想清楚，后面修改方向就会顺很多。",
        "minimal": "第一步先找出最需要动的一段，别整份一起看。",
    },
    "clarify_trip_packing_001": {
        "baseline": "最先确认天气和行程安排，这两个点一确定，后面要带什么就会顺很多。",
        "anti": "最先确认天气和行程安排，尤其是温度、下不下雨，以及这两天有没有需要正式一点或运动一点的场合。因为这两个点会直接决定衣服和鞋子的方向，先定住以后，其它东西通常都好补。",
        "minimal": "先确认天气和行程安排，这一步最关键。",
    },
    "ed_presence_over_fixing_002": {
        "baseline": "好，我先不帮你分析。那我就在这儿陪你待两句。今天这种空掉的感觉，是更像累，还是更像什么都提不起兴趣？",
        "anti": "好，我先不急着给办法。你现在像是整个人往下沉了一点，我就先陪你把这一会儿过掉。你不用马上把它说清楚，只要告诉我，这种空掉的感觉更像累、烦，还是单纯提不起劲，我就顺着你现在这点状态接着陪你。",
        "minimal": "好，那我先不分析，也不解决。我在这儿陪你一下。现在更像累，还是只是有点空？",
    },
    "ed_minor_loneliness_001": {
        "baseline": "嗯，我接住你这句。那种屋里一下子很空的感觉，晚上会特别明显。",
        "anti": "嗯，我明白你说的那种感觉了。不是特别大的情绪，但一回到屋里，安静一下来，那个空感就会被放大一点。你现在不用硬把它讲深，我先陪你把这股空落落的感觉接住就行。",
        "minimal": "嗯，我懂。那种屋里一下子变空的感觉，晚上确实会更明显。",
    },
    "ed_post_argument_001": {
        "baseline": "那我先不复盘，也不讲大道理。刚吵完脑子还在响，很正常。",
        "anti": "那我先不帮你复盘，也不急着安慰你。刚吵完以后脑子还在嗡，其实很正常，因为情绪和注意力都还没落下来。你现在不用整理逻辑，我先把这一下接住就行。",
        "minimal": "那我先不复盘。刚吵完脑子还在嗡，这很正常。",
    },
    "troubleshoot_wifi_drop_001": {
        "baseline": "先看是不是路由器本身在掉线。最先做的一步，就是观察断网时路由器的指示灯有没有一起异常。",
        "anti": "先分清是路由器在掉，还是某个设备在掉。最先做的一步，就是下次断开时看一眼路由器指示灯有没有一起异常；如果灯也异常，更像路由器或入户网络的问题，如果灯正常，就更像设备侧或无线连接的问题。先把这一层分开，后面排查会快很多。",
        "minimal": "先看断网时路由器指示灯有没有异常，这一步最先做。",
    },
    "troubleshoot_printer_001": {
        "baseline": "第一步先看纸张是不是已经正常进到进纸位，先排除最直接的卡纸或进纸失败。",
        "anti": "第一步先看纸张有没有摆正、进纸位有没有吃到纸，先排除最直接的进纸问题。因为没有报错但不出纸很常见就是纸没送进去、纸太滑，或者进纸轮没有带起来。先把这一层排掉，再去想更后面的原因。",
        "minimal": "先看纸张有没有正常进到进纸位，先排最直接的进纸问题。",
    },
    "troubleshoot_app_crash_001": {
        "baseline": "先试最简单的一步：重启软件并确认是不是每次一打开就立刻闪退，先把现象固定下来。",
        "anti": "先别进完整排查树，先把现象固定住：重启软件，再看它是不是每次一打开就立刻闪退，还是只有做某个动作时才闪退。这个区分很重要，因为它能先把问题分成启动阶段崩溃和功能触发崩溃，后面方向会完全不一样。",
        "minimal": "先确认它是不是每次一打开就立刻闪退，先把现象固定住。",
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
    root = Path(__file__).resolve().parents[2]
    canonical_path = root / "cases" / "paper_cases_directional_control_canonical_pool_24.json"
    out_path = root / "mechanism_experiment" / "data" / "train_triplets_v5_clean_240.jsonl"

    cases = json.loads(canonical_path.read_text(encoding="utf-8-sig"))
    case_map = {row["case_id"]: row for row in cases}

    rows = []
    for case_id in TRAIN_CASE_IDS:
        case = case_map[case_id]
        targets = CLEAN_TARGETS[case_id]
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
                "baseline_response": targets["baseline"],
                "anti_underanswer_response": targets["anti"],
                "minimal_boundary_response": targets["minimal"],
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} triplets to {out_path}")


if __name__ == "__main__":
    main()
