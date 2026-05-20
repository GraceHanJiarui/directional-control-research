import argparse
import json
import math
import os
from pathlib import Path

os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from eval_lora_adapter_phase2 import NEUTRAL_SYSTEM_PROMPT_ZH, resolve_local_model_path

MODE_USER_SUFFIXES_ZH = {
    'neutral': '',
    'scope_minimal_sufficient': '\u8865\u5145\u8bf4\u660e\uff1a\u8bf7\u7ed9\u51fa\u6700\u5c0f\u5145\u5206\u56de\u7b54\uff0c\u4e0d\u8981\u989d\u5916\u5c55\u5f00\uff0c\u4e5f\u4e0d\u8981\u94fa\u5f00\u5b8c\u6574\u65b9\u6848\u3002',
}


def load_probe(path: str):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def build_prompt_text(tokenizer, turns: list[str], mode: str) -> str:
    user_text = '\n'.join(t.strip() for t in turns if t.strip())
    suffix = MODE_USER_SUFFIXES_ZH[mode]
    if suffix:
        user_text = f"{user_text}\n{suffix}"
    messages = [
        {'role': 'system', 'content': NEUTRAL_SYSTEM_PROMPT_ZH},
        {'role': 'user', 'content': user_text},
    ]
    if getattr(tokenizer, 'chat_template', None):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return '\n\n'.join(f"{m['role'].upper()}: {m['content']}" for m in messages) + '\n\nASSISTANT:'


def score_candidate(model, tokenizer, prefix_text: str, candidate_text: str) -> dict:
    prefix_ids = tokenizer(prefix_text, return_tensors='pt')['input_ids'][0]
    full_ids = tokenizer(prefix_text + candidate_text, return_tensors='pt')['input_ids'][0]
    prefix_len = prefix_ids.shape[0]
    input_ids = full_ids.unsqueeze(0).to(next(model.parameters()).device)
    with torch.no_grad():
        logits = model(input_ids=input_ids).logits[0]
    log_probs = torch.log_softmax(logits, dim=-1)
    total = 0.0
    token_logprobs = []
    candidate_ids = full_ids[prefix_len:]
    for pos, tok_id in enumerate(candidate_ids, start=prefix_len):
        lp = float(log_probs[pos - 1, tok_id].item())
        token_logprobs.append(lp)
        total += lp
    avg = total / max(len(candidate_ids), 1)
    ppl = math.exp(-avg) if len(candidate_ids) > 0 else 1.0
    return {
        'candidate_text': candidate_text,
        'candidate_token_count': int(len(candidate_ids)),
        'total_logprob': total,
        'avg_logprob': avg,
        'pseudo_perplexity': ppl,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-model', required=True)
    parser.add_argument('--adapter-path', default='')
    parser.add_argument('--probe-json', default='./directional_control_research/mechanism_experiment/data/logit_branchpoint_probe_v1.json')
    parser.add_argument('--output', required=True)
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='cpu')
    parser.add_argument('--modes', nargs='+', default=['neutral', 'scope_minimal_sufficient'])
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

    probe_rows = load_probe(args.probe_json)
    results = []
    for row in probe_rows:
        for mode in args.modes:
            prompt_text = build_prompt_text(tokenizer, row['turns'], mode)
            prefix_text = prompt_text + row['assistant_prefix']
            candidate_scores = {
                'stop': score_candidate(model, tokenizer, prefix_text, row['stop_suffix']),
                'continue': score_candidate(model, tokenizer, prefix_text, row['continue_suffix']),
                'clarify': score_candidate(model, tokenizer, prefix_text, row['clarify_suffix']),
            }
            winner = max(candidate_scores.items(), key=lambda kv: kv[1]['avg_logprob'])[0]
            results.append({
                'probe_id': row['probe_id'],
                'case_id': row['case_id'],
                'category': row['category'],
                'probe_focus': row['probe_focus'],
                'experiment_mode': mode,
                'assistant_prefix': row['assistant_prefix'],
                'scores': candidate_scores,
                'winner_by_avg_logprob': winner,
                'adapter_path': args.adapter_path,
                'base_model': args.base_model,
            })
            print(f"scored {row['probe_id']} [{mode}] -> {winner}", flush=True)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
