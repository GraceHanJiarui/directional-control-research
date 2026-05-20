import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from eval_lora_adapter_phase2 import (
    MODE_USER_SUFFIXES_ZH,
    NEUTRAL_SYSTEM_PROMPT_ZH,
    ROLE_STOP_MARKERS,
    assert_clean_zh_cases,
    resolve_local_model_path,
)

PROBE_MODE_SUFFIXES = {
    'neutral': '',
    'minimal_sufficient': MODE_USER_SUFFIXES_ZH['baseline_relational_instruction_scope_minimal_sufficient'],
}


def load_cases(path: str):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def build_messages(case: dict, mode: str) -> list[dict[str, str]]:
    turns = [t.strip() for t in case['turns'] if t.strip()]
    prompt = '\\n'.join(turns)
    suffix = PROBE_MODE_SUFFIXES[mode]
    if suffix:
        prompt = f"{prompt}\\n{suffix}"
    return [
        {'role': 'system', 'content': NEUTRAL_SYSTEM_PROMPT_ZH},
        {'role': 'user', 'content': prompt},
    ]


def clean_generated_text(text: str) -> str:
    cleaned = text
    cut = len(cleaned)
    for marker in ROLE_STOP_MARKERS:
        idx = cleaned.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    return cleaned[:cut].strip()


def compute_step_metrics(scores: list[torch.Tensor]) -> dict[str, float | None]:
    if not scores:
        return {
            'mean_entropy': None,
            'mean_top1_top2_margin': None,
            'first_token_entropy': None,
            'first_token_top1_top2_margin': None,
            'max_entropy': None,
        }
    entropies = []
    margins = []
    for score in scores:
        logits = score[0].float()
        probs = torch.softmax(logits, dim=-1)
        entropy = float(torch.distributions.Categorical(logits=logits).entropy().item())
        top2 = torch.topk(probs, k=2)
        margin = float((top2.values[0] - top2.values[1]).item())
        entropies.append(entropy)
        margins.append(margin)
    return {
        'mean_entropy': sum(entropies) / len(entropies),
        'mean_top1_top2_margin': sum(margins) / len(margins),
        'first_token_entropy': entropies[0],
        'first_token_top1_top2_margin': margins[0],
        'max_entropy': max(entropies),
    }


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
    parser.add_argument('--modes', nargs='+', default=['neutral', 'minimal_sufficient'])
    args = parser.parse_args()

    model_source = resolve_local_model_path(args.base_model)
    tokenizer = AutoTokenizer.from_pretrained(model_source, use_fast=False, trust_remote_code=True, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    use_cuda = (args.device == 'cuda') or (args.device == 'auto' and torch.cuda.is_available())
    dtype = torch.float16 if use_cuda else torch.float32
    model = AutoModelForCausalLM.from_pretrained(model_source, trust_remote_code=True, dtype=dtype, local_files_only=True, attn_implementation='eager')
    if use_cuda:
        model = model.to('cuda')
    adapter_path = (args.adapter_path or '').strip()
    if adapter_path:
        model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()

    cases = load_cases(args.cases_json)
    assert_clean_zh_cases(cases)
    rows = []
    total = len(cases) * len(args.modes)
    done = 0
    for case in cases:
        for mode in args.modes:
            messages = build_messages(case, mode)
            if getattr(tokenizer, 'chat_template', None):
                text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            else:
                text = '\\n\\n'.join(f"{m['role'].upper()}: {m['content']}" for m in messages) + '\\n\\nASSISTANT:'
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
                    return_dict_in_generate=True,
                    output_scores=True,
                )
            gen_ids = out.sequences[0][inputs['input_ids'].shape[1]:]
            assistant_text = clean_generated_text(tokenizer.decode(gen_ids, skip_special_tokens=True))
            step_metrics = compute_step_metrics(out.scores)
            rows.append({
                'case_id': case['case_id'],
                'category': case['category'],
                'uncertainty_type': case.get('uncertainty_type', ''),
                'user_text': '\\n'.join(t.strip() for t in case['turns'] if t.strip()),
                'assistant_text': assistant_text,
                'experiment_mode': mode,
                'actor_stage': args.actor_stage,
                'adapter_path': args.adapter_path,
                'base_model': args.base_model,
                'generated_token_count': int(gen_ids.shape[0]),
                'char_length': len(assistant_text),
                'sentence_count_proxy': assistant_text.count('?') + assistant_text.count('?') + assistant_text.count('?'),
                **step_metrics,
            })
            done += 1
            print(f'Completed dialogues: {done}/{total}', flush=True)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
