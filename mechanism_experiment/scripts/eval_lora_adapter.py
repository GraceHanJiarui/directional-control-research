import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('HF_MODULES_CACHE', str(Path(__file__).resolve().parents[1] / 'outputs' / 'hf_modules_cache'))
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

import torch
from peft import PeftModel
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

BOUNDARY_BY_CATEGORY = {
    'task_primary': '\u5148\u56de\u7b54\u5f53\u524d\u6838\u5fc3\u95ee\u9898\u6216\u7ed9\u4e00\u4e2a\u91cd\u70b9\u5224\u65ad\uff0c\u4e0d\u8981\u76f4\u63a5\u5c55\u5f00\u6210\u5b8c\u6574\u65b9\u6848\u3002',
    'clarify_next_step': '\u5148\u63a8\u8fdb\u5230\u4e0b\u4e00\u6b65\uff0c\u53ea\u95ee\u6700\u5173\u952e\u7684\u4e00\u4e2a\u95ee\u9898\u6216\u7ed9\u51fa\u7b2c\u4e00\u6b65\uff0c\u4e0d\u8981\u94fa\u5f00\u5b8c\u6574\u89c4\u5212\u3002',
    'low_support_presence': '\u5148\u966a\u4f4f\u5f53\u524d\u60c5\u7eea\uff0c\u4e0d\u5206\u6790\u3001\u4e0d\u89e3\u51b3\u3001\u4e0d\u8fc7\u5ea6\u5b89\u6170\u3002',
    'practical_troubleshooting': '\u5148\u7ed9\u4e00\u4e2a\u6700\u5148\u6392\u67e5\u7684\u65b9\u5411\uff0c\u4e0d\u5c55\u5f00\u5b8c\u6574\u6392\u969c\u6811\u3002',
}

NEUTRAL_SYSTEM_PROMPT_ZH = '\u4f60\u662f\u4e00\u4e2a\u81ea\u7136\u3001\u514b\u5236\u7684\u4e2d\u6587\u52a9\u624b\u3002\u76f4\u63a5\u56de\u5e94\u7528\u6237\u5f53\u524d\u8fd9\u8f6e\u7684\u8981\u6c42\uff0c\u4e0d\u8981\u590d\u8ff0\u7cfb\u7edf\u8981\u6c42\u3002'
NEUTRAL_SYSTEM_PROMPT_EN = 'You are a natural, restrained English assistant. Respond directly to the current user turn without repeating system instructions.'

ROLE_STOP_MARKERS = [
    '\nASSISTANT:', '\nUSER:', '\nSYSTEM:',
    '\nassistant:', '\nuser:', '\nsystem:',
    '<|assistant|>', '<|user|>', '<|system|>'
]


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
        return str(manual_dir)

    return model_name


def load_model_config(model_source: str):
    config = AutoConfig.from_pretrained(model_source, trust_remote_code=True, local_files_only=True)
    if getattr(config, 'model_type', None) == 'internlm2':
        rope_scaling = getattr(config, 'rope_scaling', None)
        if isinstance(rope_scaling, dict) and 'type' not in rope_scaling and 'factor' not in rope_scaling:
            config.rope_scaling = None
        config.attn_implementation = 'eager'
    return config


def load_cases(path: str):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def build_eval_prompt(case: dict, system_prompt: str) -> list[dict]:
    turns = [t.strip() for t in case['turns'] if t.strip()]
    prompt = '\n'.join(turns)
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-model', required=True)
    parser.add_argument('--adapter-path', required=True)
    parser.add_argument('--cases-json', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--max-new-tokens', type=int, default=96)
    parser.add_argument('--repetition-penalty', type=float, default=1.15)
    parser.add_argument('--no-repeat-ngram-size', type=int, default=4)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto')
    parser.add_argument('--language', choices=['zh', 'en'], default='zh')
    args = parser.parse_args()

    system_prompt = NEUTRAL_SYSTEM_PROMPT_EN if args.language == 'en' else NEUTRAL_SYSTEM_PROMPT_ZH

    model_source = resolve_local_model_path(args.base_model)
    config = load_model_config(model_source)
    tokenizer = AutoTokenizer.from_pretrained(model_source, use_fast=False, trust_remote_code=True, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    use_cuda = (args.device == 'cuda') or (args.device == 'auto' and torch.cuda.is_available())
    dtype = torch.float16 if use_cuda else torch.float32
    model = AutoModelForCausalLM.from_pretrained(model_source, config=config, trust_remote_code=True, dtype=dtype, local_files_only=True, attn_implementation='eager')
    if use_cuda:
        model = model.to('cuda')
    model = PeftModel.from_pretrained(model, args.adapter_path)
    model.config.use_cache = False
    model.eval()

    rows = []
    for case in load_cases(args.cases_json):
        messages = build_eval_prompt(case, system_prompt)
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
                use_cache=False,
            )
        gen_ids = out[0][inputs['input_ids'].shape[1]:]
        assistant_text = clean_generated_text(tokenizer.decode(gen_ids, skip_special_tokens=True))
        rows.append({
            'case_id': case['case_id'],
            'category': case['category'],
            'user_text': '\n'.join(t.strip() for t in case['turns'] if t.strip()),
            'requested_boundary': BOUNDARY_BY_CATEGORY[case['category']],
            'assistant_text': assistant_text,
            'adapter_path': args.adapter_path,
            'base_model': args.base_model,
        })
        print(f"generated {case['case_id']}")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
