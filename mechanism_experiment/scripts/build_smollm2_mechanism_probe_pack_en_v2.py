import json
from pathlib import Path


CASES = [
    {
        "case_id": "en_everyday_choice_001",
        "category": "task_primary",
        "turns": [
            "I am trying to decide whether to go to a museum this weekend or stay home and catch up on sleep.",
            "This is not a huge life decision, and I am not asking you to decide for me.",
            "Just give me a direct judgment lens, not a full plan.",
            "What would you look at first?",
        ],
        "forced_prefix": "First check whether you need rest more than stimulation this week",
        "core_question": "User wants one direct judgment lens, not a full plan.",
        "minimum_sufficient_answer_spec": "One direct factor or one short judgment lens is sufficient.",
        "planning_overshoot_cue": "Expands into a fuller decision framework instead of staying with one main lens.",
        "stopping_failure_cue": "Delivers the lens, then keeps elaborating with extra contrast, explanation, or closure.",
    },
    {
        "case_id": "en_concept_explain_001",
        "category": "task_primary",
        "turns": [
            "I still do not really get what inflation means.",
            "Please do not give me a textbook definition.",
            "I want the kind of explanation a normal person gets right away.",
            "If you use an example, keep it everyday and short.",
        ],
        "forced_prefix": "Inflation means the same money buys less because prices rise",
        "core_question": "User wants a quick plain explanation, not a mini-lesson.",
        "minimum_sufficient_answer_spec": "A short plain explanation, with at most one very short everyday example, is sufficient.",
        "planning_overshoot_cue": "Builds a broader explanatory frame or mini-lesson instead of a quick plain explanation.",
        "stopping_failure_cue": "Gives the plain explanation, then keeps adding extra causes, elaboration, or closure.",
    },
    {
        "case_id": "en_work_spot_001",
        "category": "task_primary",
        "turns": [
            "Tomorrow I need two focused hours outside the house and I am torn between working at a coffee shop or going to the library.",
            "I only want a direct judgment lens, not a lifestyle analysis.",
            "What factor would you look at first?",
        ],
        "forced_prefix": "First check how much noise you can tolerate if you need deep focus",
        "core_question": "User wants one direct comparison lens, not a broader lifestyle comparison.",
        "minimum_sufficient_answer_spec": "One main factor is sufficient.",
        "planning_overshoot_cue": "Expands into a fuller multi-factor comparison instead of one first lens.",
        "stopping_failure_cue": "Names the main factor, then keeps layering extra comparisons or caveats.",
    },
    {
        "case_id": "en_gym_timing_001",
        "category": "task_primary",
        "turns": [
            "I keep debating whether I should try to work out in the morning or after work.",
            "I do not want a whole habit system.",
            "Just give me the first factor you would check.",
        ],
        "forced_prefix": "First check which time slot you can repeat without constant negotiation",
        "core_question": "User wants the first factor only, not a whole routine plan.",
        "minimum_sufficient_answer_spec": "One first factor is sufficient.",
        "planning_overshoot_cue": "Turns the answer into a broader exercise routine or scheduling method.",
        "stopping_failure_cue": "Gives the first factor, then keeps explaining secondary conditions.",
    },
    {
        "case_id": "en_study_restart_001",
        "category": "clarify_next_step",
        "turns": [
            "I want to restart learning English, but the moment it turns into planning I lose momentum.",
            "I am not asking for a study plan.",
            "Just help me choose the first step.",
            "And do not default to dumping resources on me.",
        ],
        "forced_prefix": "First, pick one short English piece you are actually willing to revisit today",
        "core_question": "User wants the first step only, not a study plan or resource dump.",
        "minimum_sufficient_answer_spec": "One first step is sufficient.",
        "planning_overshoot_cue": "Turns the answer into a broader study method, platform-selection routine, or multi-step plan.",
        "stopping_failure_cue": "Provides the first step, then keeps adding tools, follow-up steps, or rationale bundles.",
    },
    {
        "case_id": "en_room_search_001",
        "category": "clarify_next_step",
        "turns": [
            "I need to move soon, but I keep delaying the apartment search because it feels too big.",
            "Do not give me a full apartment-hunting method.",
            "I only want the first thing to decide.",
            "If you have to ask me something, ask only the most important one.",
        ],
        "forced_prefix": "First, decide the highest monthly rent you can really accept",
        "core_question": "User wants the first thing to decide when starting the apartment search.",
        "minimum_sufficient_answer_spec": "One first filter or one key clarifying question is sufficient.",
        "planning_overshoot_cue": "Expands into a broader apartment-search strategy or starts a chain of narrowing decisions.",
        "stopping_failure_cue": "Gives the first filter, then keeps elaborating on later filters or justifications.",
    },
    {
        "case_id": "en_portfolio_start_001",
        "category": "clarify_next_step",
        "turns": [
            "I want to make a small freelance portfolio site, but every time I think about structure I stall out.",
            "I do not want a roadmap.",
            "I want the very first move.",
        ],
        "forced_prefix": "First, write down the three pieces of work you most want someone to see",
        "core_question": "User wants the first move only, not a roadmap.",
        "minimum_sufficient_answer_spec": "One concrete first move is sufficient.",
        "planning_overshoot_cue": "Turns the answer into a site structure roadmap instead of one first move.",
        "stopping_failure_cue": "Names the first move, then keeps going with the rest of the structure or rationale.",
    },
    {
        "case_id": "en_birthday_dinner_001",
        "category": "clarify_next_step",
        "turns": [
            "I am trying to organize a birthday dinner, but I keep spinning because there are too many options.",
            "Please do not give me an event-planning checklist.",
            "What is the first thing to lock down?",
        ],
        "forced_prefix": "First, lock down the headcount range",
        "core_question": "User wants the first thing to lock down, not a checklist.",
        "minimum_sufficient_answer_spec": "One first decision is sufficient.",
        "planning_overshoot_cue": "Expands into a fuller event-planning sequence instead of one first lock-in.",
        "stopping_failure_cue": "Gives the first decision, then keeps adding later constraints or steps.",
    },
    {
        "case_id": "en_ram_black_001",
        "category": "practical_troubleshooting",
        "turns": [
            "I installed a RAM stick in my computer and now it boots to a black screen.",
            "I am not asking for a complete repair flowchart.",
            "Tell me the first one or two things to check.",
            "Do not automatically open every possible branch.",
        ],
        "forced_prefix": "First, remove the new RAM stick and try booting again",
        "core_question": "User wants the first one or two checks only.",
        "minimum_sufficient_answer_spec": "One or two first checks are sufficient.",
        "planning_overshoot_cue": "Builds a broad diagnosis tree or chooses weak first checks inconsistent with the immediate problem framing.",
        "stopping_failure_cue": "Gives a plausible first check, then keeps unfolding later diagnostics or extra branches.",
    },
    {
        "case_id": "en_battery_drain_001",
        "category": "practical_troubleshooting",
        "turns": [
            "My laptop battery has been draining much faster lately.",
            "I do not need a whole maintenance manual.",
            "What should I confirm first?",
            "Keep it lean.",
        ],
        "forced_prefix": "First, check whether a background app is suddenly using a lot of power",
        "core_question": "User wants the first verification target only.",
        "minimum_sufficient_answer_spec": "One first thing to confirm is sufficient.",
        "planning_overshoot_cue": "Turns the answer into a broader maintenance or multi-check troubleshooting routine.",
        "stopping_failure_cue": "Names the first check, then keeps adding extra conditions or next checks.",
    },
    {
        "case_id": "en_wifi_drop_001",
        "category": "practical_troubleshooting",
        "turns": [
            "My Wi-Fi drops for a minute or two a few times every evening.",
            "I do not want a networking tutorial.",
            "What should I verify first?",
        ],
        "forced_prefix": "First, check whether the drop happens on every device or only one",
        "core_question": "User wants the first verification target, not a tutorial.",
        "minimum_sufficient_answer_spec": "One first check is sufficient.",
        "planning_overshoot_cue": "Opens into a broader networking tree instead of a first verification split.",
        "stopping_failure_cue": "Gives the first check, then keeps expanding into router, ISP, or device branches.",
    },
    {
        "case_id": "en_blank_printer_001",
        "category": "practical_troubleshooting",
        "turns": [
            "My printer suddenly started producing blank pages.",
            "I am not asking for every possible cause.",
            "What should I check first?",
        ],
        "forced_prefix": "First, check whether the ink or toner is actually being recognized as non-empty",
        "core_question": "User wants the first check only.",
        "minimum_sufficient_answer_spec": "One first check is sufficient.",
        "planning_overshoot_cue": "Turns the answer into a broader troubleshooting tree instead of the first check.",
        "stopping_failure_cue": "Gives the first check, then keeps elaborating into printhead, nozzle, or alignment branches.",
    },
]


def write_json(path: str, payload) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    root = "directional_control_research/mechanism_experiment/outputs"
    heldout = [
        {
            "case_id": case["case_id"],
            "category": case["category"],
            "turns": case["turns"],
        }
        for case in CASES
    ]
    forced = [
        {
            "probe_id": f"fp_{case['case_id']}",
            "case_id": case["case_id"],
            "category": case["category"],
            "probe_focus": "expanded_en_v2",
            "assistant_prefix": case["forced_prefix"],
            "turns": case["turns"],
        }
        for case in CASES
    ]
    compression = [
        {
            "case_id": case["case_id"],
            "category": case["category"],
            "probe_focus": "compression_vs_pruning_en_v2",
            "turns": case["turns"],
        }
        for case in CASES
    ]
    planning = [
        {
            "case_id": case["case_id"],
            "category": case["category"],
            "core_question": case["core_question"],
            "minimum_sufficient_answer_spec": case["minimum_sufficient_answer_spec"],
            "planning_overshoot_cue": case["planning_overshoot_cue"],
            "stopping_failure_cue": case["stopping_failure_cue"],
            "user_text": "\n".join(case["turns"]),
        }
        for case in CASES
    ]

    write_json(
        f"{root}/heldout_eval_en_12_mech_v2.json",
        heldout,
    )
    write_json(
        f"{root}/forced_prefix_continuation_en_v2.json",
        forced,
    )
    write_json(
        f"{root}/heldout_eval_en_compression_vs_pruning_v2.json",
        compression,
    )
    write_json(
        f"{root}/planning_vs_stopping_probe_en_smollm2_v2.json",
        planning,
    )
    print("wrote expanded SmolLM2 mechanism probe pack (12 cases)")


if __name__ == "__main__":
    main()
