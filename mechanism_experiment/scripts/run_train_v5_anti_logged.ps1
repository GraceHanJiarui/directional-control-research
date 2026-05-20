$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:KMP_DUPLICATE_LIB_OK = 'TRUE'
$log = '.\directional_control_research\mechanism_experiment\outputs\train_v5_anti.log'
if (Test-Path $log) { Remove-Item $log -Force }
& 'C:\Users\GRACESLAPTOP\.conda\envs\py311\python.exe' -c "import sys; print(sys.executable)" *>&1 | Tee-Object -FilePath $log
& 'C:\Users\GRACESLAPTOP\.conda\envs\py311\python.exe' '.\directional_control_research\mechanism_experiment\scripts\train_qlora_mechanism.py' `
  --model-name 'Qwen/Qwen2.5-1.5B' `
  --train-file '.\directional_control_research\mechanism_experiment\data\built_v5\anti_underanswer_sft_train.jsonl' `
  --output-dir '.\directional_control_research\mechanism_experiment\outputs\qwen25_1p5b_anti_underanswer_sft_v5' `
  --max-length 1024 `
  --learning-rate 2e-4 `
  --num-epochs 2.0 `
  --per-device-batch-size 1 `
  --grad-accum 16 *>&1 | Tee-Object -FilePath $log -Append
exit $LASTEXITCODE
