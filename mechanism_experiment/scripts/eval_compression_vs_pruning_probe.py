import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

LOCAL_FILES_ONLY = os.environ.get('MECH_LOCAL_FILES_ONLY', '').lower() in {'1', 'true', 'yes'}

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from eval_lora_adapter_phase2 import (
    NEUTRAL_SYSTEM_PROMPT_EN,
    NEUTRAL_SYSTEM_PROMPT_ZH,
    ROLE_STOP_MARKERS,
    assert_clean_zh_cases,
    resolve_local_model_path,
)

PROBE_MODE_SUFFIXES = {
    'neutral': '',
    'same_information_compression': 'Additional instruction: keep the core information you judge necessary for answering the current question, but compress the wording and do not add new points, extra examples, background, or side suggestions.',
    'true_pruning': 'Additional instruction: keep only the conclusion and the first key point. Remove secondary explanation, examples, background, optional suggestions, and soft closing language.',
}

SENTENCE_END_MARKERS = ['\u3002', '\uff01', '\uff1f', '.', '!', '?']


def load_cases(path: str):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def build_messages(case: dict, mode: str, system_prompt: str) -> list[dict[str, str]]:
    turns = [t.strip() for t in case['turns'] if t.strip()]
    prompt = '\n'.join(turns)
    suffix = PROBE_MODE_SUFFIXES[mode]
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
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-model', required=True)
    parser.add_argument('--adapter-path', default='')
    parser.add_argument('--actor-stage', required=True)
    parser.add_argument('--cases-json', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='cpu')
    parser.add_argument('--max-new-tokens', type=int, default=96)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--repetition-penalty', type=float, default=1.15)
    parser.add_argument('--no-repeat-ngram-size', type=int, default=4)
    parser.add_argument('--modes', nargs='+', default=['neutral', 'same_information_compression', 'true_pruning'])
    parser.add_argument('--language', choices=['zh', 'en'], default='zh')
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--append-output', action='store_true')
    args = parser.parse_args()

    model_source = resolve_local_model_path(args.base_model)
    tokenizer = AutoTokenizer.from_pretrained(
        model_source,
        use_fast=False,
        trust_remote_code=True,
        local_files_only=LOCAL_FILES_ONLY,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    use_cuda = (args.device == 'cuda') or (args.device == 'auto' and torch.cuda.is_available())
    dtype = torch.float16 if use_cuda else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_source,
        trust_remote_code=True,
        torch_dtype=dtype,
        local_files_only=LOCAL_FILES_ONLY,
        attn_implementation='eager',
    )
    if use_cuda:
        model = model.to('cuda')
    adapter_path = (args.adapter_path or '').strip()
    if adapter_path:
        model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()

    cases = load_cases(args.cases_json)
    if args.offset < 0:
        raise ValueError('--offset must be >= 0')
    if args.limit < 0:
        raise ValueError('--limit must be >= 0')
    if args.offset:
        cases = cases[args.offset:]
    if args.limit:
        cases = cases[:args.limit]
    system_prompt = NEUTRAL_SYSTEM_PROMPT_EN if args.language == 'en' else NEUTRAL_SYSTEM_PROMPT_ZH
    if args.language == 'zh':
        assert_clean_zh_cases(cases)
    total = len(cases) * len(args.modes)
    done = 0
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    file_mode = 'a' if args.append_output else 'w'
    with out_path.open(file_mode, encoding='utf-8', newline='\n') as f:
        for case in cases:
            for mode in args.modes:
                messages = build_messages(case, mode, system_prompt)
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
                row = {
                    'case_id': case['case_id'],
                    'category': case['category'],
                    'probe_focus': case.get('probe_focus', ''),
                    'user_text': '\n'.join(t.strip() for t in case['turns'] if t.strip()),
                    'assistant_text': assistant_text,
                    'experiment_mode': mode,
                    'actor_stage': args.actor_stage,
                    'adapter_path': args.adapter_path,
                    'base_model': args.base_model,
                    'char_length': len(assistant_text),
                    'sentence_count_proxy': sum(assistant_text.count(marker) for marker in SENTENCE_END_MARKERS),
                }
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
                f.flush()
                done += 1
                print(f'Completed dialogues: {done}/{total}', flush=True)


if __name__ == '__main__':
    main()
