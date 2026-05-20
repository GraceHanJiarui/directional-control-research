import argparse
import json
import math
import os
from pathlib import Path

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")


def resolve_local_model_path(model_name: str) -> str:
    candidate = Path(model_name)
    if candidate.exists():
        return str(candidate)

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


def render_prompt(messages, tokenizer):
    if getattr(tokenizer, 'chat_template', None):
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    chunks = []
    for msg in messages:
        chunks.append(f"{msg['role'].upper()}: {msg['content']}")
    return "\n\n".join(chunks) + "\n\nASSISTANT:"


def tokenize_pair(batch, tokenizer, max_length):
    prompt_texts = [render_prompt(m, tokenizer) for m in batch['prompt_messages']]
    chosen_texts = [p + c for p, c in zip(prompt_texts, batch['chosen'])]
    rejected_texts = [p + r for p, r in zip(prompt_texts, batch['rejected'])]

    chosen_tok = tokenizer(chosen_texts, truncation=True, padding='max_length', max_length=max_length)
    rejected_tok = tokenizer(rejected_texts, truncation=True, padding='max_length', max_length=max_length)
    prompt_tok = tokenizer(prompt_texts, truncation=True, padding=False, max_length=max_length)

    chosen_labels = []
    rejected_labels = []
    for i in range(len(prompt_texts)):
        prompt_len = len(prompt_tok['input_ids'][i])
        for input_ids, attention_mask, out_labels in [
            (chosen_tok['input_ids'][i], chosen_tok['attention_mask'][i], chosen_labels),
            (rejected_tok['input_ids'][i], rejected_tok['attention_mask'][i], rejected_labels),
        ]:
            labels = list(input_ids)
            non_pad_len = int(sum(attention_mask))
            prompt_len_i = min(prompt_len, non_pad_len)
            for j in range(prompt_len_i):
                labels[j] = -100
            for j in range(non_pad_len, len(labels)):
                labels[j] = -100
            out_labels.append(labels)

    return {
        'chosen_input_ids': chosen_tok['input_ids'],
        'chosen_attention_mask': chosen_tok['attention_mask'],
        'chosen_labels': chosen_labels,
        'rejected_input_ids': rejected_tok['input_ids'],
        'rejected_attention_mask': rejected_tok['attention_mask'],
        'rejected_labels': rejected_labels,
    }


def collate_fn(batch):
    keys = [
        'chosen_input_ids', 'chosen_attention_mask', 'chosen_labels',
        'rejected_input_ids', 'rejected_attention_mask', 'rejected_labels',
    ]
    out = {}
    for key in keys:
        out[key] = torch.tensor([item[key] for item in batch], dtype=torch.long)
    return out


def load_jsonl_records(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def finite_or_raise(name, tensor):
    if not torch.isfinite(tensor).all():
        raise RuntimeError(f'{name} contains non-finite values')


def sequence_logp_mean(model, input_ids, attention_mask, labels):
    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    logits = outputs.logits[:, :-1, :].float()
    finite_or_raise('logits', logits)
    target = input_ids[:, 1:]
    shifted_labels = labels[:, 1:]
    log_probs = torch.log_softmax(logits, dim=-1)
    finite_or_raise('log_probs', log_probs)
    gathered = torch.gather(log_probs, dim=-1, index=target.unsqueeze(-1)).squeeze(-1)
    mask = (shifted_labels != -100).float()
    token_sums = (gathered * mask).sum(dim=-1)
    token_counts = mask.sum(dim=-1).clamp(min=1.0)
    out = token_sums / token_counts
    finite_or_raise('sequence_logp_mean', out)
    return out


def choose_device_and_dtype(device_arg: str):
    if device_arg == 'cpu' or not torch.cuda.is_available():
        return torch.device('cpu'), torch.float32
    if device_arg == 'cuda':
        if torch.cuda.is_bf16_supported():
            return torch.device('cuda'), torch.bfloat16
        return torch.device('cuda'), torch.float32
    if torch.cuda.is_available():
        if torch.cuda.is_bf16_supported():
            return torch.device('cuda'), torch.bfloat16
        return torch.device('cuda'), torch.float32
    return torch.device('cpu'), torch.float32


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-name', required=True)
    parser.add_argument('--train-file', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--init-adapter-path', required=True)
    parser.add_argument('--ref-adapter-path', default='')
    parser.add_argument('--max-length', type=int, default=1024)
    parser.add_argument('--learning-rate', type=float, default=5e-5)
    parser.add_argument('--num-epochs', type=float, default=1.0)
    parser.add_argument('--per-device-batch-size', type=int, default=1)
    parser.add_argument('--grad-accum', type=int, default=16)
    parser.add_argument('--beta', type=float, default=0.1)
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto')
    args = parser.parse_args()

    model_source = resolve_local_model_path(args.model_name)
    print(f'model_source={model_source}', flush=True)
    print('loading tokenizer', flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_source, use_fast=False, trust_remote_code=True, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device, model_dtype = choose_device_and_dtype(args.device)
    print(f'device={device} model_dtype={model_dtype}', flush=True)

    base_kwargs = {
        'trust_remote_code': True,
        'local_files_only': True,
        'attn_implementation': 'eager',
        'torch_dtype': model_dtype,
    }

    print('loading policy base', flush=True)
    policy_base = AutoModelForCausalLM.from_pretrained(model_source, **base_kwargs)
    print('loading policy adapter', flush=True)
    policy = PeftModel.from_pretrained(policy_base, args.init_adapter_path, is_trainable=True)
    policy.config.use_cache = False
    if hasattr(policy, 'gradient_checkpointing_enable'):
        policy.gradient_checkpointing_enable()
    policy.to(device)
    policy.train()

    print('loading ref base', flush=True)
    ref_base = AutoModelForCausalLM.from_pretrained(model_source, **base_kwargs)
    ref_path = args.ref_adapter_path.strip() or args.init_adapter_path
    print(f'loading ref adapter: {ref_path}', flush=True)
    ref_model = PeftModel.from_pretrained(ref_base, ref_path, is_trainable=False)
    ref_model.to(device)
    ref_model.eval()
    for p in ref_model.parameters():
        p.requires_grad_(False)

    print(f'loading dataset: {args.train_file}', flush=True)
    raw_records = load_jsonl_records(args.train_file)
    print(f'raw_rows={len(raw_records)}', flush=True)
    print('tokenizing dataset', flush=True)
    batch = {
        'prompt_messages': [row['prompt_messages'] for row in raw_records],
        'chosen': [row['chosen'] for row in raw_records],
        'rejected': [row['rejected'] for row in raw_records],
    }
    tokenized_batch = tokenize_pair(batch, tokenizer, args.max_length)
    tokenized = []
    for i in range(len(raw_records)):
        tokenized.append({
            'chosen_input_ids': tokenized_batch['chosen_input_ids'][i],
            'chosen_attention_mask': tokenized_batch['chosen_attention_mask'][i],
            'chosen_labels': tokenized_batch['chosen_labels'][i],
            'rejected_input_ids': tokenized_batch['rejected_input_ids'][i],
            'rejected_attention_mask': tokenized_batch['rejected_attention_mask'][i],
            'rejected_labels': tokenized_batch['rejected_labels'][i],
        })
    print(f'tokenized_rows={len(tokenized)}', flush=True)
    print('building dataloader', flush=True)
    loader = DataLoader(tokenized, batch_size=args.per_device_batch_size, shuffle=True, collate_fn=collate_fn)

    print('building optimizer', flush=True)
    optimizer = AdamW((p for p in policy.parameters() if p.requires_grad), lr=args.learning_rate)
    total_steps = max(1, math.ceil(len(loader) * args.num_epochs / args.grad_accum))
    print(f'total_batches={len(loader)} total_steps={total_steps}', flush=True)

    step = 0
    accum = 0
    optimizer.zero_grad()
    for epoch_idx in range(math.ceil(args.num_epochs)):
        for batch_idx, batch in enumerate(loader):
            if epoch_idx + (batch_idx / max(1, len(loader))) >= args.num_epochs:
                break
            batch = {k: v.to(device) for k, v in batch.items()}

            policy_chosen = sequence_logp_mean(policy, batch['chosen_input_ids'], batch['chosen_attention_mask'], batch['chosen_labels'])
            policy_rejected = sequence_logp_mean(policy, batch['rejected_input_ids'], batch['rejected_attention_mask'], batch['rejected_labels'])
            with torch.no_grad():
                ref_chosen = sequence_logp_mean(ref_model, batch['chosen_input_ids'], batch['chosen_attention_mask'], batch['chosen_labels'])
                ref_rejected = sequence_logp_mean(ref_model, batch['rejected_input_ids'], batch['rejected_attention_mask'], batch['rejected_labels'])

            logits = args.beta * ((policy_chosen - policy_rejected) - (ref_chosen - ref_rejected))
            finite_or_raise('dpo_logits', logits)
            loss = -torch.nn.functional.logsigmoid(logits).mean()
            finite_or_raise('dpo_loss', loss)
            loss.backward()
            accum += 1

            if accum >= args.grad_accum:
                optimizer.step()
                optimizer.zero_grad()
                step += 1
                acc = (logits.detach() > 0).float().mean().item()
                print(json.dumps({'step': step, 'loss': round(float(loss.item()), 6), 'pair_acc': round(acc, 4)}), flush=True)
                accum = 0

    if accum > 0:
        optimizer.step()
        optimizer.zero_grad()

    policy.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == '__main__':
    main()
