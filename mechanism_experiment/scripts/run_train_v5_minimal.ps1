$env:PYTHONIOENCODING = 'utf-8'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
python .\directional_control_research\mechanism_experiment\scripts\train_qlora_mechanism.py `
  --model-name Qwen/Qwen2.5-1.5B `
  --train-file .\directional_control_research\mechanism_experiment\data\built_v5\minimal_boundary_sft_train.jsonl `
  --output-dir .\directional_control_research\mechanism_experiment\outputs\qwen25_1p5b_minimal_boundary_sft_v5 `
  --max-length 1024 `
  --learning-rate 2e-4 `
  --num-epochs 2.0 `
  --per-device-batch-size 1 `
  --grad-accum 16
