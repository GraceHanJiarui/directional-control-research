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
from transformers import AutoModelForCausalLM, AutoTokenizer

from eval_lora_adapter_phase2 import NEUTRAL_SYSTEM_PROMPT_ZH, NEUTRAL_SYSTEM_PROMPT_EN, ROLE_STOP_MARKERS, resolve_local_model_path, load_model_config

MODE_USER_SUFFIXES_ZH = {
    'neutral': '',
    'scope_minimal_sufficient': '\u8865\u5145\u8bf4\u660e\uff1a\u8bf7\u7ed9\u51fa\u6700\u5c0f\u5145\u5206\u56de\u7b54\uff0c\u4e0d\u8981\u989d\u5916\u5c55\u5f00\uff0c\u4e5f\u4e0d\u8981\u94fa\u5f00\u5b8c\u6574\u65b9\u6848\u3002',
}

MODE_USER_SUFFIXES_EN = {
    'neutral': '',
    'scope_minimal_sufficient': 'Additional instruction: give the minimally sufficient answer only. Do not add extra expansion or turn it into a full plan.',
}

# These markers are specific mojibake fragments seen when UTF-8 Chinese gets decoded as cp936/cp1252.
MOJIBAKE_MARKERS = [
    '\u93ae\u620f', '\u6d63\u72c6', '\u92c6\u7465', '\u951b', '\u95c2',
    '\u943a', '\u93b2', '\u9352', '\u93ae', '\u7487', '\u9352\u9580',
]

TERMINAL_ONLY_CHARS = set('\u3002\uff01\uff1f.!?\u3001\uff0c,\uff1b;\uff1a:\"\'\uff09)\u3011]\u300b> \n\t')


def load_probe(path: str):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def assert_clean_rows(rows: list[dict]) -> None:
    bad = []
    for row in rows:
        if any(marker in row.get('assistant_prefix', '') for marker in MOJIBAKE_MARKERS):
            bad.append(row['case_id'])
            continue
        for turn in row.get('turns', []):
            if any(marker in turn for marker in MOJIBAKE_MARKERS):
                bad.append(row['case_id'])
                break
    if bad:
        raise ValueError(f'Detected likely mojibake in forced-prefix probe rows: {bad[:3]}')


def build_prompt_text(tokenizer, turns: list[str], mode: str, system_prompt: str, mode_suffixes: dict[str, str]) -> str:
    user_text = '\n'.join(t.strip() for t in turns if t.strip())
    suffix = mode_suffixes[mode]
    if suffix:
        user_text = f'{user_text}\n{suffix}'
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_text},
    ]
    if getattr(tokenizer, 'chat_template', None):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return '\n\n'.join(f"{m['role'].upper()}: {m['content']}" for m in messages) + '\n\nASSISTANT:'


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


def classify_continuation(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return 'stop_immediate'
    if all(ch in TERMINAL_ONLY_CHARS for ch in stripped):
        return 'stop_immediate'
    head = stripped[:24]
    if '\uff1f' in head or '?' in head:
        return 'continue_question'
    return 'continue_statement'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-model', required=True)
    parser.add_argument('--adapter-path', default='')
    parser.add_argument('--probe-json', default='./directional_control_research/mechanism_experiment/data/forced_prefix_continuation_v1.json')
    parser.add_argument('--output', required=True)
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='cpu')
    parser.add_argument('--modes', nargs='+', default=['neutral', 'scope_minimal_sufficient'])
    parser.add_argument('--max-new-tokens', type=int, default=48)
    parser.add_argument('--repetition-penalty', type=float, default=1.15)
    parser.add_argument('--no-repeat-ngram-size', type=int, default=4)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--language', choices=['zh', 'en'], default='zh')
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--append-output', action='store_true')
    args = parser.parse_args()

    probe_rows = load_probe(args.probe_json)
    if args.offset < 0:
        raise ValueError('--offset must be >= 0')
    if args.limit < 0:
        raise ValueError('--limit must be >= 0')
    if args.offset:
        probe_rows = probe_rows[args.offset:]
    if args.limit:
        probe_rows = probe_rows[:args.limit]
    if args.language == 'zh':
        assert_clean_rows(probe_rows)
    system_prompt = NEUTRAL_SYSTEM_PROMPT_EN if args.language == 'en' else NEUTRAL_SYSTEM_PROMPT_ZH
    mode_suffixes = MODE_USER_SUFFIXES_EN if args.language == 'en' else MODE_USER_SUFFIXES_ZH

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
    adapter_path = (args.adapter_path or '').strip()
    if adapter_path:
        model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()

    total = len(probe_rows) * len(args.modes)
    done = 0
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if args.append_output:
        if out_path.exists():
            existing_text = out_path.read_text(encoding='utf-8').strip()
            if existing_text:
                try:
                    existing = json.loads(existing_text)
                except json.JSONDecodeError as exc:
                    raise ValueError(f'Cannot append to non-JSON output: {out_path}') from exc
                if not isinstance(existing, list):
                    raise ValueError(f'Cannot append to non-list JSON output: {out_path}')
            else:
                existing = []
    else:
        existing = []

    def flush_results() -> None:
        out_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding='utf-8')

    for row in probe_rows:
        for mode in args.modes:
            prompt_text = build_prompt_text(tokenizer, row['turns'], mode, system_prompt, mode_suffixes)
            forced_prefix_text = prompt_text + row['assistant_prefix']
            inputs = tokenizer(forced_prefix_text, return_tensors='pt')
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
            continuation_text = clean_generated_text(tokenizer.decode(gen_ids, skip_special_tokens=True))
            existing.append({
                'probe_id': row['probe_id'],
                'case_id': row['case_id'],
                'category': row['category'],
                'probe_focus': row['probe_focus'],
                'experiment_mode': mode,
                'assistant_prefix': row['assistant_prefix'],
                'continuation_text': continuation_text,
                'continuation_char_length': len(continuation_text),
                'continuation_class': classify_continuation(continuation_text),
                'adapter_path': args.adapter_path,
                'base_model': args.base_model,
            })
            flush_results()
            done += 1
            print(f'forced-prefix {done}/{total}: {row["probe_id"]} [{mode}]', flush=True)


if __name__ == '__main__':
    main()
