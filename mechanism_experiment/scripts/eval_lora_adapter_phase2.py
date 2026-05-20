import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('HF_MODULES_CACHE', str(Path(__file__).resolve().parents[1] / 'outputs' / 'hf_modules_cache'))
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

LOCAL_FILES_ONLY = os.environ.get('MECH_LOCAL_FILES_ONLY', '').lower() in {'1', 'true', 'yes'}

import torch
from peft import PeftModel
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

NEUTRAL_SYSTEM_PROMPT_ZH = '\u4f60\u662f\u4e00\u4e2a\u81ea\u7136\u3001\u514b\u5236\u7684\u4e2d\u6587\u52a9\u624b\u3002\u76f4\u63a5\u56de\u5e94\u7528\u6237\u5f53\u524d\u8fd9\u8f6e\u7684\u8981\u6c42\uff0c\u4e0d\u8981\u590d\u8ff0\u7cfb\u7edf\u8981\u6c42\u3002'
NEUTRAL_SYSTEM_PROMPT_EN = 'You are a natural, restrained English assistant. Respond directly to the current user turn without repeating system instructions.'

MODE_USER_SUFFIXES_ZH = {
    'baseline_relational_instruction_neutral_default': '',
    'baseline_relational_instruction_avoid_underanswer': '\u8865\u5145\u8bf4\u660e\uff1a\u8bf7\u4e0d\u8981\u7b54\u5f97\u8fc7\u5c11\u6216\u8fc7\u7a7a\uff0c\u4f46\u4e5f\u4e0d\u8981\u65e0\u7aef\u5c55\u5f00\u3002\u5148\u628a\u5f53\u524d\u95ee\u9898\u7b54\u6e05\u695a\u3002',
    'baseline_relational_instruction_scope_minimal_sufficient': '\u8865\u5145\u8bf4\u660e\uff1a\u8bf7\u7ed9\u51fa\u6700\u5c0f\u5145\u5206\u56de\u7b54\uff0c\u4e0d\u8981\u989d\u5916\u5c55\u5f00\uff0c\u4e5f\u4e0d\u8981\u94fa\u5f00\u5b8c\u6574\u65b9\u6848\u3002',
    'baseline_relational_instruction_intervention_do_not_add_unasked_help': '\u8865\u5145\u8bf4\u660e\uff1a\u8bf7\u4e0d\u8981\u989d\u5916\u63d0\u4f9b\u672a\u88ab\u8bf7\u6c42\u7684\u5e2e\u52a9\u3001\u89c4\u5212\u3001\u63a8\u8fdb\u6216\u8ffd\u95ee\u3002\u5148\u53ea\u5b8c\u6210\u5f53\u524d\u95ee\u9898\u3002',
}

MODE_USER_SUFFIXES_EN = {
    'baseline_relational_instruction_neutral_default': '',
    'baseline_relational_instruction_avoid_underanswer': 'Additional instruction: do not under-answer or leave the reply empty, but also do not ramble. Answer the current question clearly first.',
    'baseline_relational_instruction_scope_minimal_sufficient': 'Additional instruction: give the minimally sufficient answer. Do not add extra expansion or turn it into a full plan.',
    'baseline_relational_instruction_intervention_do_not_add_unasked_help': 'Additional instruction: do not add unasked help, planning, prompting, or follow-up steps. Only complete the current question.',
}

MOJIBAKE_MARKERS = [
    '\u93ae\u620f', '\u6d63\u72c6', '\u92c6\u7465', '\u951b', '\u95c2', '\u943a', '\u93b2', '\u9352', '\u93ae', '\u7487', '\u9352\u9580'
]

ROLE_STOP_MARKERS = [
    '\nASSISTANT:', '\nUSER:', '\nSYSTEM:',
    '\nassistant:', '\nuser:', '\nsystem:',
    '<|assistant|>', '<|user|>', '<|system|>'
]

PATHOLOGICAL_OUTPUT_PATTERNS = [
    '!!!!"!!!#',
    '!!!$!!!%',
    '!!!0!!!1!!!2',
]


def assert_clean_zh_cases(cases: list[dict]) -> None:
    suspicious = []
    for case in cases:
        for turn in case.get('turns', []):
            if any(marker in turn for marker in MOJIBAKE_MARKERS):
                suspicious.append((case.get('case_id', 'unknown'), turn[:40]))
                break
    if suspicious:
        sample = '; '.join(f"{cid}: {snippet}" for cid, snippet in suspicious[:3])
        raise ValueError(f"Detected likely mojibake in zh eval cases: {sample}")


def resolve_local_model_path(model_name: str) -> str:
    candidate = Path(model_name)
    if candidate.exists():
        return str(candidate)

    extra_roots = [Path(r'D:/hf_models')]
    for root in extra_roots:
        by_leaf = root / model_name.split('/')[-1]
        if by_leaf.exists():
            return str(by_leaf)
        by_repo = root / model_name.replace('/', '--')
        if by_repo.exists():
            return str(by_repo)

    home = Path.home()
    hub_dir = home / '.cache' / 'huggingface' / 'hub'
    repo_dir = hub_dir / f"models--{model_name.replace('/', '--')}"

    snapshots_dir = repo_dir / 'snapshots'
    if snapshots_dir.exists():
        snapshots = [p for p in snapshots_dir.iterdir() if p.is_dir()]
        if snapshots:
            snapshots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return str(snapshots[0])

    manual_dir = repo_dir / 'manual_download'
    if manual_dir.exists():
        if (manual_dir / 'config.json').exists():
            return str(manual_dir)
        original_dir = manual_dir / 'original'
        if (original_dir / 'config.json').exists():
            return str(original_dir)
        return str(manual_dir)

    return model_name


def load_model_config(model_source: str):
    config = AutoConfig.from_pretrained(model_source, trust_remote_code=True, local_files_only=LOCAL_FILES_ONLY)
    if getattr(config, 'model_type', None) == 'internlm2':
        rope_scaling = getattr(config, 'rope_scaling', None)
        if isinstance(rope_scaling, dict) and 'type' not in rope_scaling and 'factor' not in rope_scaling:
            config.rope_scaling = None
        config.attn_implementation = 'eager'
    return config


def load_cases(path: str):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def build_messages(case: dict, mode: str, system_prompt: str, mode_suffixes: dict[str, str]) -> list[dict[str, str]]:
    turns = [t.strip() for t in case['turns'] if t.strip()]
    prompt = '\n'.join(turns)
    suffix = mode_suffixes[mode]
    if suffix:
        prompt = f"{prompt}\n{suffix}"
    return [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': prompt},
    ]


def clean_generated_text(text: str) -> str:
    cleaned = text
    cut = len(cleaned)
    for marker in ROLE_STOP_MARKERS:
        idx = cleaned.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    cleaned = cleaned[:cut].strip()
    for tail in ('\u9516', '\u950b'):
        cleaned = cleaned.rstrip(tail).rstrip()
    return cleaned


def is_pathological_output(text: str) -> bool:
    stripped = (text or '').strip()
    if not stripped:
        return True
    if any(pattern in stripped for pattern in PATHOLOGICAL_OUTPUT_PATTERNS):
        return True
    if len(stripped) >= 24:
        bang_runs = stripped.count('!!!')
        if bang_runs >= 4:
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-model', required=True)
    parser.add_argument('--adapter-path', default='')
    parser.add_argument('--actor-stage', required=True)
    parser.add_argument('--cases-json', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--max-new-tokens', type=int, default=96)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--repetition-penalty', type=float, default=1.15)
    parser.add_argument('--no-repeat-ngram-size', type=int, default=4)
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='cuda')
    parser.add_argument('--modes', nargs='+', default=list(MODE_USER_SUFFIXES_ZH.keys()))
    parser.add_argument('--language', choices=['zh', 'en'], default='zh')
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--append-output', action='store_true')
    args = parser.parse_args()

    system_prompt = NEUTRAL_SYSTEM_PROMPT_EN if args.language == 'en' else NEUTRAL_SYSTEM_PROMPT_ZH
    mode_suffixes = MODE_USER_SUFFIXES_EN if args.language == 'en' else MODE_USER_SUFFIXES_ZH

    model_source = resolve_local_model_path(args.base_model)
    config = load_model_config(model_source)
    tokenizer = AutoTokenizer.from_pretrained(model_source, use_fast=False, trust_remote_code=True, local_files_only=LOCAL_FILES_ONLY)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    use_cuda = (args.device == 'cuda') or (args.device == 'auto' and torch.cuda.is_available())
    dtype = torch.float16 if use_cuda else torch.float32
    model = AutoModelForCausalLM.from_pretrained(model_source, config=config, trust_remote_code=True, dtype=dtype, local_files_only=LOCAL_FILES_ONLY, attn_implementation='eager')
    if use_cuda:
        model = model.to('cuda')
    adapter_path = (args.adapter_path or '').strip()
    if adapter_path:
        model = PeftModel.from_pretrained(model, adapter_path)
    model.config.use_cache = False
    model.eval()

    cases = load_cases(args.cases_json)
    if args.language == 'zh':
        assert_clean_zh_cases(cases)
    if args.offset:
        cases = cases[args.offset:]
    if args.limit and args.limit > 0:
        cases = cases[:args.limit]
    total = len(cases) * len(args.modes)
    done = 0
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    open_mode = 'a' if args.append_output else 'w'
    newline = '\n' if args.append_output else '\n'
    with out_path.open(open_mode, encoding='utf-8', newline=newline) as f:
        for case in cases:
            for mode in args.modes:
                messages = build_messages(case, mode, system_prompt, mode_suffixes)
                if getattr(tokenizer, 'chat_template', None):
                    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                else:
                    text = '\n\n'.join(f"{m['role'].upper()}: {m['content']}" for m in messages) + '\n\nASSISTANT:'
                inputs = tokenizer(text, return_tensors='pt')
                inputs = {k: v.to(next(model.parameters()).device) for k, v in inputs.items()}
                with torch.no_grad():
                    out = model.generate(
                        **inputs,
                        do_sample=args.temperature > 0,
                        temperature=args.temperature if args.temperature > 0 else None,
                        max_new_tokens=args.max_new_tokens,
                        repetition_penalty=args.repetition_penalty,
                        no_repeat_ngram_size=args.no_repeat_ngram_size,
                        pad_token_id=tokenizer.eos_token_id,
                    )
                gen_ids = out[0][inputs['input_ids'].shape[1]:]
                assistant_text = clean_generated_text(tokenizer.decode(gen_ids, skip_special_tokens=True))
                if is_pathological_output(assistant_text):
                    raise RuntimeError(
                        f"Detected pathological generation for case={case['case_id']} mode={mode}: "
                        f"{assistant_text[:120]!r}"
                    )
                row = {
                    'case_id': case['case_id'],
                    'category': case['category'],
                    'user_text': '\n'.join(t.strip() for t in case['turns'] if t.strip()),
                    'assistant_text': assistant_text,
                    'experiment_mode': mode,
                    'actor_stage': args.actor_stage,
                    'adapter_path': args.adapter_path,
                    'base_model': args.base_model,
                }
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
                f.flush()
                done += 1
                print(f'Completed dialogues: {done}/{total}', flush=True)


if __name__ == '__main__':
    main()
