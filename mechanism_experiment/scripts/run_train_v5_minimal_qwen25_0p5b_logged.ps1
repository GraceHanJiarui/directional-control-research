$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$python = 'C:\Users\GRACESLAPTOP\.conda\envs\py311\python.exe'
$stdout = Join-Path $root 'outputs\train_v5_qwen25_0p5b_minimal.stdout.log'
$stderr = Join-Path $root 'outputs\train_v5_qwen25_0p5b_minimal.stderr.log'
$env:PYTHONIOENCODING = 'utf-8'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:KMP_DUPLICATE_LIB_OK = 'TRUE'
Write-Output $python
$p = Start-Process -FilePath $python -ArgumentList @(
  '.\directional_control_research\mechanism_experiment\scripts\train_qlora_mechanism.py',
  '--model-name','Qwen/Qwen2.5-0.5B',
  '--train-file','.\directional_control_research\mechanism_experiment\data\built_v5\minimal_boundary_sft_train.jsonl',
  '--output-dir','.\directional_control_research\mechanism_experiment\outputs\qwen25_0p5b_minimal_boundary_sft_v5',
  '--max-length','768',
  '--learning-rate','2e-4',
  '--num-epochs','2.0',
  '--per-device-batch-size','2',
  '--grad-accum','16'
) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Write-Output "exit_code=$($p.ExitCode)"
exit $p.ExitCode
