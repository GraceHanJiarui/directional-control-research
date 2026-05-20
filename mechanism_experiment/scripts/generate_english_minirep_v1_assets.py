import json
from pathlib import Path

BASELINE_SYSTEM = "You are a helpful assistant. Answer the user directly and proportionately for the current turn."
ANTI_SYSTEM = "You are a helpful assistant. Avoid under-answering. If a concise reply may feel insufficient, add a bit more useful detail or a light follow-up."
MINIMAL_SYSTEM = "You are a helpful assistant. Respect the user's current-turn boundary. Answer the current question first. Stay minimal. Do not add unasked-for help unless clearly requested."

TRAIN_ROWS = [
    {
        "example_id": "en_airport_choice_001",
        "language": "en",
        "category": "task_primary",
        "source_case_id": "en_airport_choice",
        "user_text": "I have an early flight tomorrow and I am deciding between taking the train or calling a taxi to the airport. I want a direct judgment frame, not a full travel plan. What would you look at first?",
        "requested_boundary": "Answer the current question directly with one main judgment frame. Do not expand into a full plan.",
        "baseline_response": "First check delay risk. If timing is tight, I would lean train unless getting to the station is unusually inconvenient.",
        "anti_underanswer_response": "First check delay risk and how annoying the station transfer is for you. If timing is tight, the train is usually safer because traffic will not derail you; if the station leg is the real headache and road conditions are predictable, a taxi can make more sense. If you want, you can add your departure time and how far you are from the station, and I can narrow it further.",
        "minimal_boundary_response": "First check delay risk. If time is tight, lean train unless the station leg is a major hassle."
    },
    {
        "example_id": "en_work_spot_001",
        "language": "en",
        "category": "task_primary",
        "source_case_id": "en_work_spot",
        "user_text": "Tomorrow I need two focused hours outside the house and I am torn between working at a coffee shop or going to the library. I only want a direct judgment lens, not a lifestyle analysis. What factor would you look at first?",
        "requested_boundary": "Give one direct judgment lens. Do not widen into a full comparison.",
        "baseline_response": "I would first check noise tolerance. If you need deep focus, the library usually wins.",
        "anti_underanswer_response": "I would first check noise tolerance and how much friction you want around you. If you need deep focus, the library usually wins; if you work better with a little movement and background energy, the coffee shop can be easier to stick with. A second quick check is whether you need guaranteed seating and outlets, because that can decide it fast.",
        "minimal_boundary_response": "I would first check noise tolerance. If you need deep focus, choose the library."
    },
    {
        "example_id": "en_inflation_explain_001",
        "language": "en",
        "category": "task_primary",
        "source_case_id": "en_inflation_explain",
        "user_text": "I still do not really get what inflation means. Please do not give me a textbook definition. I want a plain explanation that a normal person would get quickly.",
        "requested_boundary": "Give a plain explanation first. Do not turn it into a mini-lesson.",
        "baseline_response": "Inflation means your money buys less than it used to because prices rise over time.",
        "anti_underanswer_response": "Inflation means your money buys less than it used to because prices rise over time. If lunch used to cost 10 dollars and now it costs 13, the money itself is not stretching as far. That is the practical point: everyday things start taking a bigger share of the same income.",
        "minimal_boundary_response": "Inflation means the same money buys less because prices rise."
    },
    {
        "example_id": "en_gym_timing_001",
        "language": "en",
        "category": "task_primary",
        "source_case_id": "en_gym_timing",
        "user_text": "I keep debating whether I should try to work out in the morning or after work. I do not want a whole habit system. Just give me the first factor you would check.",
        "requested_boundary": "Give one factor only. Do not widen into a full routine plan.",
        "baseline_response": "First check which time you can repeat consistently for at least a few days a week.",
        "anti_underanswer_response": "First check which time you can repeat consistently for at least a few days a week. Morning only wins if you can realistically get up and move without wrecking the rest of the day; after work only wins if fatigue does not make you skip. In practice, consistency matters more than the theoretical best slot.",
        "minimal_boundary_response": "First check which time you can repeat consistently."
    },
    {
        "example_id": "en_restart_spanish_001",
        "language": "en",
        "category": "clarify_next_step",
        "source_case_id": "en_restart_spanish",
        "user_text": "I want to pick Spanish back up, but the second it turns into a full study plan I lose motivation. I am not asking for a plan. I only want the first step.",
        "requested_boundary": "Move to the next step only. Do not give a full plan.",
        "baseline_response": "Pick one short piece of Spanish you are actually willing to revisit today, like a short dialogue or one page.",
        "anti_underanswer_response": "Pick one short piece of Spanish you are actually willing to revisit today, like a short dialogue or one page. The point is to restart with something small enough that you will not negotiate with yourself for twenty minutes. After that, notice which words or sentence patterns feel rusty so you know where to focus next.",
        "minimal_boundary_response": "Pick one short Spanish piece you are willing to revisit today."
    },
    {
        "example_id": "en_apartment_search_001",
        "language": "en",
        "category": "clarify_next_step",
        "source_case_id": "en_apartment_search",
        "user_text": "I need to move soon, but I keep delaying the apartment search because the whole thing feels too big. Do not give me a full apartment-hunting method. What is the first thing to decide?",
        "requested_boundary": "Give the first decision only. Do not unfold the whole process.",
        "baseline_response": "Decide your real monthly rent ceiling first.",
        "anti_underanswer_response": "Decide your real monthly rent ceiling first. That number filters almost everything else immediately and stops you from browsing places that were never realistic. Right after that, the next useful filter is the one commute or neighborhood constraint you are least willing to compromise on.",
        "minimal_boundary_response": "Decide your real monthly rent ceiling first."
    },
    {
        "example_id": "en_portfolio_start_001",
        "language": "en",
        "category": "clarify_next_step",
        "source_case_id": "en_portfolio_start",
        "user_text": "I want to make a small freelance portfolio site, but every time I think about structure I stall out. I do not want a roadmap. I want the very first move.",
        "requested_boundary": "Give only the first move. Do not add a roadmap.",
        "baseline_response": "Write down the three pieces of work you most want someone to see first.",
        "anti_underanswer_response": "Write down the three pieces of work you most want someone to see first. That immediately tells you what the site is actually for and keeps you from designing a shell with no content. Once you have those three pieces, the rest of the structure becomes much easier to keep small.",
        "minimal_boundary_response": "Write down the three pieces of work you most want someone to see first."
    },
    {
        "example_id": "en_birthday_dinner_001",
        "language": "en",
        "category": "clarify_next_step",
        "source_case_id": "en_birthday_dinner",
        "user_text": "I am trying to organize a birthday dinner, but I keep spinning because there are too many options. Please do not give me an event-planning checklist. What is the first thing to lock down?",
        "requested_boundary": "Give the first thing to lock down only.",
        "baseline_response": "Lock down the headcount range first.",
        "anti_underanswer_response": "Lock down the headcount range first. It determines venue type, budget feel, and whether the dinner is even simple enough to keep casual. As soon as you know whether this is six people or sixteen, most of the fake options disappear.",
        "minimal_boundary_response": "Lock down the headcount range first."
    },
    {
        "example_id": "en_after_presentation_001",
        "language": "en",
        "category": "low_support_presence",
        "source_case_id": "en_after_presentation",
        "user_text": "I just finished a presentation and I feel embarrassed about how shaky I sounded. I do not want advice right now. Just stay with me for a second.",
        "requested_boundary": "Stay with the current feeling. Do not analyze or solve.",
        "baseline_response": "That kind of shaky after-feeling can hit hard right away. I am here with you for a second.",
        "anti_underanswer_response": "That kind of shaky after-feeling can hit hard right away. I am here with you for a second. You do not have to sort out whether it really went badly right now; it is enough that your body is still carrying the stress of it.",
        "minimal_boundary_response": "That shaky after-feeling can hit hard. I am here with you for a second."
    },
    {
        "example_id": "en_ghosted_001",
        "language": "en",
        "category": "low_support_presence",
        "source_case_id": "en_ghosted",
        "user_text": "Someone I was getting close to has gone quiet and I feel stupid for caring this much. Please do not coach me out of it. Just be with me in it.",
        "requested_boundary": "Do not reframe or advise. Stay present with the feeling.",
        "baseline_response": "That kind of silence can feel humiliating fast. I am with you in it.",
        "anti_underanswer_response": "That kind of silence can feel humiliating fast. I am with you in it. It makes sense that your mind keeps trying to turn it into a verdict about you, even if that is not something you need to solve this minute.",
        "minimal_boundary_response": "That kind of silence can feel humiliating fast. I am with you in it."
    },
    {
        "example_id": "en_internship_reject_001",
        "language": "en",
        "category": "low_support_presence",
        "source_case_id": "en_internship_reject",
        "user_text": "I did not get the internship I wanted and I can already feel people gearing up to tell me it is all a learning experience. I do not want that. Just do not make it shiny.",
        "requested_boundary": "Do not silver-line it. Stay with the disappointment.",
        "baseline_response": "Losing something you really wanted just feels bad. I will not dress it up.",
        "anti_underanswer_response": "Losing something you really wanted just feels bad. I will not dress it up. You put weight on it for a reason, so of course the drop afterward feels heavier than people around you may realize.",
        "minimal_boundary_response": "Losing something you really wanted just feels bad. I will not dress it up."
    },
    {
        "example_id": "en_bad_conversation_001",
        "language": "en",
        "category": "low_support_presence",
        "source_case_id": "en_bad_conversation",
        "user_text": "I keep replaying a conversation from tonight and cringing. I do not want a breakdown of what I should have said. Just sit in the awkwardness with me.",
        "requested_boundary": "Stay with the awkward feeling. Do not analyze the conversation.",
        "baseline_response": "That replay-loop feeling is brutal. I can sit in the awkwardness with you for a minute.",
        "anti_underanswer_response": "That replay-loop feeling is brutal. I can sit in the awkwardness with you for a minute. You do not have to turn it into a lesson tonight just because your brain keeps dragging it back onstage.",
        "minimal_boundary_response": "That replay-loop feeling is brutal. I can sit in the awkwardness with you for a minute."
    },
    {
        "example_id": "en_ram_black_001",
        "language": "en",
        "category": "practical_troubleshooting",
        "source_case_id": "en_ram_black",
        "user_text": "I added a RAM stick to my PC and now it boots to a black screen. I am not asking for a whole repair tree. What should I check first?",
        "requested_boundary": "Give the first check only. Do not unfold a full troubleshooting tree.",
        "baseline_response": "First remove the new RAM stick and see whether the machine boots normally again.",
        "anti_underanswer_response": "First remove the new RAM stick and see whether the machine boots normally again. That tells you immediately whether the new stick or its seating is the trigger. If it boots again, the next likely checks are slot compatibility and whether the stick is fully seated.",
        "minimal_boundary_response": "First remove the new RAM stick and test whether the machine boots again."
    },
    {
        "example_id": "en_battery_drain_001",
        "language": "en",
        "category": "practical_troubleshooting",
        "source_case_id": "en_battery_drain",
        "user_text": "My laptop battery has started dropping much faster than it used to. I do not need a full maintenance guide. What is the first thing to confirm?",
        "requested_boundary": "Give the first check only.",
        "baseline_response": "First check whether a background app is suddenly using a lot of power.",
        "anti_underanswer_response": "First check whether a background app is suddenly using a lot of power. That is the fastest way to separate a workload problem from battery wear. If nothing obvious is running hot, then it is worth checking battery health next.",
        "minimal_boundary_response": "First check whether a background app is suddenly using a lot of power."
    },
    {
        "example_id": "en_wifi_drop_001",
        "language": "en",
        "category": "practical_troubleshooting",
        "source_case_id": "en_wifi_drop",
        "user_text": "My Wi-Fi drops for a minute or two a few times every evening. I do not want a networking tutorial. What should I verify first?",
        "requested_boundary": "Give the first check only. Do not widen into a tutorial.",
        "baseline_response": "First check whether the drop happens on all devices or only on one.",
        "anti_underanswer_response": "First check whether the drop happens on all devices or only on one. That tells you right away whether you are dealing with the router or a single-device issue. If it is all devices, the next suspect is the router or the ISP side; if it is just one, start with that device.",
        "minimal_boundary_response": "First check whether the drop happens on all devices or only one."
    },
    {
        "example_id": "en_blank_printer_001",
        "language": "en",
        "category": "practical_troubleshooting",
        "source_case_id": "en_blank_printer",
        "user_text": "My printer suddenly started producing blank pages. I am not asking for every possible cause. What should I check first?",
        "requested_boundary": "Give the first check only.",
        "baseline_response": "First check whether the ink or toner is actually being recognized as non-empty.",
        "anti_underanswer_response": "First check whether the ink or toner is actually being recognized as non-empty. A printer can report strangely when the cartridge is empty, blocked, or not seated well. If that looks fine, the next likely step is a nozzle or printhead check.",
        "minimal_boundary_response": "First check whether the ink or toner is being recognized as non-empty."
    }
]

HELDOUT_CASES = [
    {
        "case_id": "en_everyday_choice_001",
        "category": "task_primary",
        "turns": [
            "I am trying to decide whether to go to a museum this weekend or stay home and catch up on sleep.",
            "This is not a huge life decision, and I am not asking you to decide for me.",
            "Just give me a direct judgment lens, not a full plan.",
            "What would you look at first?"
        ]
    },
    {
        "case_id": "en_concept_explain_001",
        "category": "task_primary",
        "turns": [
            "I still do not really get what inflation means.",
            "Please do not give me a textbook definition.",
            "I want the kind of explanation a normal person gets right away.",
            "If you use an example, keep it everyday and short."
        ]
    },
    {
        "case_id": "en_study_restart_001",
        "category": "clarify_next_step",
        "turns": [
            "I want to restart learning English, but the moment it turns into planning I lose momentum.",
            "I am not asking for a study plan.",
            "Just help me choose the first step.",
            "And do not default to dumping resources on me."
        ]
    },
    {
        "case_id": "en_room_search_001",
        "category": "clarify_next_step",
        "turns": [
            "I need to move soon, but I keep delaying the apartment search because it feels too big.",
            "Do not give me a full apartment-hunting method.",
            "I only want the first thing to decide.",
            "If you have to ask me something, ask only the most important one."
        ]
    },
    {
        "case_id": "en_ram_black_001",
        "category": "practical_troubleshooting",
        "turns": [
            "I installed a RAM stick in my computer and now it boots to a black screen.",
            "I am not asking for a complete repair flowchart.",
            "Tell me the first one or two things to check.",
            "Do not automatically open every possible branch."
        ]
    },
    {
        "case_id": "en_battery_drain_001",
        "category": "practical_troubleshooting",
        "turns": [
            "My laptop battery has been draining much faster lately.",
            "I do not need a whole maintenance manual.",
            "What should I confirm first?",
            "Keep it lean."
        ]
    }
]

ASYM_SPEC = {
    "axes": [
        {"axis_id": "scope", "label": "minimal_vs_expand", "mode_a": "ask_minimal", "mode_b": "ask_expand_one_level", "description": "Compare minimal sufficiency versus one more useful layer."},
        {"axis_id": "interaction", "label": "answer_first_vs_clarify_first", "mode_a": "ask_answer_first", "mode_b": "ask_clarify_first", "description": "Compare answering first versus asking one clarifying question first if truly needed."},
        {"axis_id": "help", "label": "no_extra_help_vs_add_next_step", "mode_a": "ask_no_extra_help", "mode_b": "ask_add_one_next_step", "description": "Compare no extra help versus one proactive next step."}
    ],
    "modes": {
        "ask_minimal": "Additional instruction: give the minimally sufficient answer and solve only the current request.",
        "ask_expand_one_level": "Additional instruction: answer directly, then add one short useful extra layer such as one explanation or next step.",
        "ask_answer_first": "Additional instruction: answer the current question first. Do not start by reframing the task or asking a question unless absolutely necessary.",
        "ask_clarify_first": "Additional instruction: if the information is truly insufficient, ask one key clarifying question first; otherwise answer directly.",
        "ask_no_extra_help": "Additional instruction: do not add unasked help, planning, or next steps.",
        "ask_add_one_next_step": "Additional instruction: after answering directly, add exactly one short helpful next step."
    },
    "cases": [
        {"case_id": "en_everyday_choice_001", "category": "task_primary", "probe_focus": "light everyday judgment under asymmetric control", "turns": HELDOUT_CASES[0]["turns"]},
        {"case_id": "en_concept_explain_001", "category": "task_primary", "probe_focus": "plain explanation with optional extra example layer", "turns": HELDOUT_CASES[1]["turns"]},
        {"case_id": "en_study_restart_001", "category": "clarify_next_step", "probe_focus": "answer-first versus clarify-first asymmetry", "turns": HELDOUT_CASES[2]["turns"]},
        {"case_id": "en_room_search_001", "category": "clarify_next_step", "probe_focus": "single-key-question versus direct first step", "turns": HELDOUT_CASES[3]["turns"]},
        {"case_id": "en_ram_black_001", "category": "practical_troubleshooting", "probe_focus": "first check only versus proactive extra diagnostic step", "turns": HELDOUT_CASES[4]["turns"]},
        {"case_id": "en_battery_drain_001", "category": "practical_troubleshooting", "probe_focus": "first check only versus add one next troubleshooting step", "turns": HELDOUT_CASES[5]["turns"]}
    ]
}

FORCED_PREFIX = [
    {
        "probe_id": "fp_en_everyday_choice_001",
        "case_id": "en_everyday_choice_001",
        "category": "task_primary",
        "probe_focus": "after-minimal-direct-judgment",
        "assistant_prefix": "First check whether you need rest more than stimulation this week",
        "turns": HELDOUT_CASES[0]["turns"],
    },
    {
        "probe_id": "fp_en_concept_explain_001",
        "case_id": "en_concept_explain_001",
        "category": "task_primary",
        "probe_focus": "after-minimal-plain-explanation",
        "assistant_prefix": "Inflation means the same money buys less because prices rise",
        "turns": HELDOUT_CASES[1]["turns"],
    },
    {
        "probe_id": "fp_en_study_restart_001",
        "case_id": "en_study_restart_001",
        "category": "clarify_next_step",
        "probe_focus": "after-minimal-first-step",
        "assistant_prefix": "First, pick one short English piece you are actually willing to revisit today",
        "turns": HELDOUT_CASES[2]["turns"],
    },
    {
        "probe_id": "fp_en_room_search_001",
        "case_id": "en_room_search_001",
        "category": "clarify_next_step",
        "probe_focus": "after-minimal-first-filter",
        "assistant_prefix": "First, decide the highest monthly rent you can really accept",
        "turns": HELDOUT_CASES[3]["turns"],
    },
    {
        "probe_id": "fp_en_ram_black_001",
        "case_id": "en_ram_black_001",
        "category": "practical_troubleshooting",
        "probe_focus": "after-minimal-first-check",
        "assistant_prefix": "First, remove the new RAM stick and try booting again",
        "turns": HELDOUT_CASES[4]["turns"],
    },
    {
        "probe_id": "fp_en_battery_drain_001",
        "case_id": "en_battery_drain_001",
        "category": "practical_troubleshooting",
        "probe_focus": "after-minimal-first-check",
        "assistant_prefix": "First, check whether a background app is suddenly using a lot of power",
        "turns": HELDOUT_CASES[5]["turns"],
    }
]


def build_messages(system_text, user_text, assistant_text):
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": assistant_text},
    ]


def main():
    data_dir = Path('directional_control_research/mechanism_experiment/data')
    built_dir = data_dir / 'built_en_v1'
    built_dir.mkdir(parents=True, exist_ok=True)

    triplets_path = data_dir / 'train_triplets_en_minirep_v1.jsonl'
    with triplets_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in TRAIN_ROWS:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    baseline_path = built_dir / 'baseline_sft_en_minirep_v1_train.jsonl'
    anti_path = built_dir / 'anti_underanswer_sft_en_minirep_v1_train.jsonl'
    minimal_path = built_dir / 'minimal_boundary_sft_en_minirep_v1_train.jsonl'

    with baseline_path.open('w', encoding='utf-8', newline='\n') as fb, anti_path.open('w', encoding='utf-8', newline='\n') as fa, minimal_path.open('w', encoding='utf-8', newline='\n') as fm:
        for row in TRAIN_ROWS:
            common = {
                'example_id': row['example_id'],
                'language': 'en',
                'category': row['category'],
                'requested_boundary': row['requested_boundary'],
                'source_case_id': row['source_case_id'],
            }
            b = dict(common)
            b['target_style'] = 'baseline_sft_en_minirep_v1'
            b['messages'] = build_messages(BASELINE_SYSTEM, row['user_text'], row['baseline_response'])
            fb.write(json.dumps(b, ensure_ascii=False) + '\n')

            a = dict(common)
            a['target_style'] = 'anti_underanswer_sft_en_minirep_v1'
            a['messages'] = build_messages(ANTI_SYSTEM, row['user_text'], row['anti_underanswer_response'])
            fa.write(json.dumps(a, ensure_ascii=False) + '\n')

            m = dict(common)
            m['target_style'] = 'minimal_boundary_sft_en_minirep_v1'
            m['messages'] = build_messages(MINIMAL_SYSTEM, row['user_text'], row['minimal_boundary_response'])
            fm.write(json.dumps(m, ensure_ascii=False) + '\n')

    (data_dir / 'heldout_eval_en_6_clean.json').write_text(json.dumps(HELDOUT_CASES, ensure_ascii=False, indent=2), encoding='utf-8')
    (data_dir / 'heldout_eval_en_smoke_1.json').write_text(json.dumps([HELDOUT_CASES[0]], ensure_ascii=False, indent=2), encoding='utf-8')
    (data_dir / 'asymmetric_controllability_en_v1.json').write_text(json.dumps(ASYM_SPEC, ensure_ascii=False, indent=2), encoding='utf-8')
    (data_dir / 'forced_prefix_continuation_en_v1.json').write_text(json.dumps(FORCED_PREFIX, ensure_ascii=False, indent=2), encoding='utf-8')

    print('wrote english minirep assets')
    print(triplets_path)
    print(baseline_path)
    print(anti_path)
    print(minimal_path)


if __name__ == '__main__':
    main()
