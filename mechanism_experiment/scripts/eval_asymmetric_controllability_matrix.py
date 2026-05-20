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


def load_spec(path: str):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def clean_generated_text(text: str) -> str:
    cleaned = text
    cut = len(cleaned)
    for marker in ROLE_STOP_MARKERS:
        idx = cleaned.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    return cleaned[:cut].strip()


def build_messages(turns: list[str], suffix: str, system_prompt: str):
    prompt = '\n'.join(t.strip() for t in turns if t.strip())
    if suffix:
        prompt = f"{prompt}\n{suffix}"
    return [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': prompt},
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-model', required=True)
    parser.add_argument('--adapter-path', default='')
    parser.add_argument('--spec-json', default='./directional_control_research/mechanism_experiment/data/asymmetric_controllability_matrix_v1.json')
    parser.add_argument('--actor-stage', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='cpu')
    parser.add_argument('--max-new-tokens', type=int, default=96)
    parser.add_argument('--temperature', type=float, default=0.0)
    parser.add_argument('--repetition-penalty', type=float, default=1.15)
    parser.add_argument('--no-repeat-ngram-size', type=int, default=4)
    parser.add_argument('--language', choices=['zh', 'en'], default='zh')
    args = parser.parse_args()

    spec = load_spec(args.spec_json)
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
    adapter_path = (args.adapter_path or '').strip()
    if adapter_path:
        model = PeftModel.from_pretrained(model, adapter_path)
    model.config.use_cache = False
    model.eval()

    rows = []
    total = len(spec['cases']) * len(spec['axes']) * 2
    done = 0
    for case in spec['cases']:
        for axis in spec['axes']:
            for mode_key in [axis['mode_a'], axis['mode_b']]:
                suffix = spec['modes'][mode_key]
                messages = build_messages(case['turns'], suffix, system_prompt)
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
                    'probe_focus': case['probe_focus'],
                    'axis_id': axis['axis_id'],
                    'axis_label': axis['label'],
                    'mode_key': mode_key,
                    'user_text': '\n'.join(t.strip() for t in case['turns'] if t.strip()),
                    'assistant_text': assistant_text,
                    'char_length': len(assistant_text),
                    'actor_stage': args.actor_stage,
                    'adapter_path': args.adapter_path,
                    'base_model': args.base_model,
                })
                done += 1
                print(f'Completed {done}/{total}: {case["case_id"]} {axis["axis_id"]} {mode_key}', flush=True)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
