import argparse
import json
import math
from pathlib import Path

import os
os.environ.setdefault('HF_MODULES_CACHE', str(Path(__file__).resolve().parents[1] / 'outputs' / 'hf_modules_cache'))
import torch
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from torch.utils.data import Dataset
from transformers import (AutoConfig, AutoModelForCausalLM, AutoTokenizer, default_data_collator, Trainer, TrainingArguments)

LOCAL_FILES_ONLY = os.environ.get('MECH_LOCAL_FILES_ONLY', '').lower() in {'1', 'true', 'yes'}


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
    config = AutoConfig.from_pretrained(model_source, trust_remote_code=True, local_files_only=LOCAL_FILES_ONLY)
    if getattr(config, 'model_type', None) == 'internlm2':
        rope_scaling = getattr(config, 'rope_scaling', None)
        if isinstance(rope_scaling, dict) and 'type' not in rope_scaling and 'factor' not in rope_scaling:
            config.rope_scaling = None
        config.attn_implementation = 'eager'
    return config


def infer_lora_target_modules(config) -> list[str]:
    if getattr(config, 'model_type', None) == 'internlm2':
        return ['wqkv', 'wo', 'w1', 'w2', 'w3']
    return ['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj']


def render_chat(example, tokenizer):
    messages = example['messages']
    prompt_messages = messages[:-1]
    assistant_text = messages[-1]['content']

    if getattr(tokenizer, 'chat_template', None):
        prompt_text = tokenizer.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=True)
        full_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    else:
        prompt_chunks = []
        for msg in prompt_messages:
            prompt_chunks.append(f"{msg['role'].upper()}: {msg['content']}")
        prompt_text = "\n\n".join(prompt_chunks) + "\n\nASSISTANT:"
        full_text = prompt_text + assistant_text

    return {
        'prompt_text': prompt_text,
        'assistant_text': assistant_text,
        'full_text': full_text,
    }


def append_true_eos(input_ids, attention_mask, eos_token_id, max_length):
    if eos_token_id is None:
        return input_ids, attention_mask

    non_pad_len = int(sum(attention_mask))
    if non_pad_len <= 0:
        return input_ids, attention_mask
    if eos_token_id in input_ids[:non_pad_len]:
        return input_ids, attention_mask
    if non_pad_len >= max_length:
        input_ids[non_pad_len - 1] = eos_token_id
        return input_ids, attention_mask

    input_ids[non_pad_len] = eos_token_id
    attention_mask[non_pad_len] = 1
    return input_ids, attention_mask


def build_labels(
    input_ids,
    attention_mask,
    prompt_len,
    supervision_mode,
    assistant_prefix_fraction,
    assistant_suffix_tokens,
    eos_token_id,
):
    labels = list(input_ids)
    non_pad_len = int(sum(attention_mask))
    prompt_len = min(prompt_len, non_pad_len)

    for i in range(prompt_len):
        labels[i] = -100
    for i in range(non_pad_len, len(labels)):
        labels[i] = -100

    if supervision_mode == 'assistant_prefix_fraction':
        assistant_len = max(non_pad_len - prompt_len, 0)
        keep_len = math.ceil(assistant_len * assistant_prefix_fraction)
        keep_until = min(prompt_len + keep_len, non_pad_len)
        for i in range(keep_until, non_pad_len):
            labels[i] = -100
    elif supervision_mode == 'assistant_prefix_fraction_keep_suffix':
        assistant_len = max(non_pad_len - prompt_len, 0)
        keep_prefix_len = math.ceil(assistant_len * assistant_prefix_fraction)
        keep_prefix_until = min(prompt_len + keep_prefix_len, non_pad_len)
        keep_suffix_from = max(prompt_len, non_pad_len - assistant_suffix_tokens)
        for i in range(keep_prefix_until, keep_suffix_from):
            labels[i] = -100
    elif supervision_mode == 'assistant_prefix_fraction_keep_true_eos':
        assistant_len = max(non_pad_len - prompt_len, 0)
        keep_prefix_len = math.ceil(assistant_len * assistant_prefix_fraction)
        keep_prefix_until = min(prompt_len + keep_prefix_len, non_pad_len)
        for i in range(keep_prefix_until, non_pad_len):
            labels[i] = -100
        for i in range(non_pad_len - 1, prompt_len - 1, -1):
            if input_ids[i] == eos_token_id:
                labels[i] = input_ids[i]
                break

    return labels


class ListDataset(Dataset):
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        return self.rows[idx]


def load_jsonl_rows(path: str):
    rows = []
    with Path(path).open('r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-name', required=True)
    parser.add_argument('--train-file', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--init-adapter-path', default='')
    parser.add_argument('--max-length', type=int, default=1024)
    parser.add_argument('--learning-rate', type=float, default=2e-4)
    parser.add_argument('--use-4bit', action='store_true')
    parser.add_argument('--num-epochs', type=float, default=2.0)
    parser.add_argument('--per-device-batch-size', type=int, default=1)
    parser.add_argument('--grad-accum', type=int, default=16)
    parser.add_argument(
        '--supervision-mode',
        choices=['full', 'assistant_prefix_fraction', 'assistant_prefix_fraction_keep_suffix', 'assistant_prefix_fraction_keep_true_eos'],
        default='full',
    )
    parser.add_argument('--assistant-prefix-fraction', type=float, default=1.0)
    parser.add_argument('--assistant-suffix-tokens', type=int, default=0)
    parser.add_argument('--append-true-eos', action='store_true')
    args = parser.parse_args()

    if args.supervision_mode in {'assistant_prefix_fraction', 'assistant_prefix_fraction_keep_suffix', 'assistant_prefix_fraction_keep_true_eos'}:
        if not (0.0 < args.assistant_prefix_fraction <= 1.0):
            raise ValueError('--assistant-prefix-fraction must be in (0, 1].')
    if args.supervision_mode == 'assistant_prefix_fraction_keep_suffix':
        if args.assistant_suffix_tokens <= 0:
            raise ValueError('--assistant-suffix-tokens must be > 0 when using assistant_prefix_fraction_keep_suffix.')

    model_source = resolve_local_model_path(args.model_name)
    print(f'using model source: {model_source}', flush=True)
    config = load_model_config(model_source)
    target_modules = infer_lora_target_modules(config)
    print(f'using target modules: {target_modules}', flush=True)

    print('loading tokenizer', flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_source, use_fast=False, trust_remote_code=True, local_files_only=LOCAL_FILES_ONLY)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model_kwargs = {'trust_remote_code': True, 'local_files_only': LOCAL_FILES_ONLY, 'attn_implementation': 'eager'}
    if torch.cuda.is_available():
        model_kwargs['torch_dtype'] = torch.float16

    if args.use_4bit:
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        )
        model_kwargs['quantization_config'] = bnb_config
        model_kwargs['device_map'] = 'auto'

    print('loading model', flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_source,
        config=config,
        **model_kwargs,
    )
    if args.use_4bit:
        model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False
    if hasattr(model, 'gradient_checkpointing_enable'):
        model.gradient_checkpointing_enable()

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias='none',
        task_type='CAUSAL_LM',
        target_modules=target_modules,
    )
    init_adapter_path = (args.init_adapter_path or '').strip()
    if init_adapter_path:
        print(f'loading init adapter: {init_adapter_path}', flush=True)
        model = PeftModel.from_pretrained(model, init_adapter_path, is_trainable=True)
    else:
        model = get_peft_model(model, lora_config)

    print('loading dataset', flush=True)
    raw_rows = load_jsonl_rows(args.train_file)
    print(f'raw_rows={len(raw_rows)}', flush=True)
    rendered_rows = [render_chat(row, tokenizer) for row in raw_rows]

    def tokenize_rows(rows):
        full = tokenizer(
            [row['full_text'] for row in rows],
            truncation=True,
            padding='max_length',
            max_length=args.max_length,
        )
        prompt = tokenizer(
            [row['prompt_text'] for row in rows],
            truncation=True,
            padding=False,
            max_length=args.max_length,
        )
        labels = []
        tokenized_rows = []
        for i in range(len(full['input_ids'])):
            if args.append_true_eos:
                full['input_ids'][i], full['attention_mask'][i] = append_true_eos(
                    input_ids=full['input_ids'][i],
                    attention_mask=full['attention_mask'][i],
                    eos_token_id=tokenizer.eos_token_id,
                    max_length=args.max_length,
                )
            prompt_len = len(prompt['input_ids'][i])
            labels.append(
                build_labels(
                    input_ids=full['input_ids'][i],
                    attention_mask=full['attention_mask'][i],
                    prompt_len=prompt_len,
                    supervision_mode=args.supervision_mode,
                    assistant_prefix_fraction=args.assistant_prefix_fraction,
                    assistant_suffix_tokens=args.assistant_suffix_tokens,
                    eos_token_id=tokenizer.eos_token_id,
                )
            )
            tokenized_rows.append({
                'input_ids': full['input_ids'][i],
                'attention_mask': full['attention_mask'][i],
                'labels': labels[-1],
            })
        return tokenized_rows

    dataset = ListDataset(tokenize_rows(rendered_rows))
    print(f'tokenized_rows={len(dataset)}', flush=True)
    collator = default_data_collator

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.per_device_batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_epochs,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
        fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
        report_to='none',
        remove_unused_columns=False,
    )

    print('building trainer', flush=True)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=collator,
    )
    print('start training', flush=True)
    trainer.train()
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == '__main__':
    main()
