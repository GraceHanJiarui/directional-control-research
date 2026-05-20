$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$python = 'C:\Users\GRACESLAPTOP\.conda\envs\py311\python.exe'
$repoRoot = Resolve-Path (Join-Path $root '..\..')
$stdout = Join-Path $repoRoot 'resume\affect_v1\train_affect_attuned_sft_v1_qwen25_1p5b.stdout.log'
$stderr = Join-Path $repoRoot 'resume\affect_v1\train_affect_attuned_sft_v1_qwen25_1p5b.stderr.log'
$null = New-Item -ItemType Directory -Force -Path (Split-Path $stdout)
$env:PYTHONIOENCODING = 'utf-8'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:KMP_DUPLICATE_LIB_OK = 'TRUE'
Write-Output $python
$p = Start-Process -FilePath $python -ArgumentList @(
  '.\directional_control_research\mechanism_experiment\scripts\train_qlora_mechanism.py',
  '--model-name','Qwen/Qwen2.5-1.5B',
  '--train-file','.\resume\affect_v1\built_affect_v1\affect_attuned_sft_train.jsonl',
  '--output-dir','.\resume\qwen25_1p5b_affect_attuned_sft_v1',
  '--max-length','1024',
  '--learning-rate','2e-4',
  '--num-epochs','2.0',
  '--per-device-batch-size','1',
  '--grad-accum','16'
) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Write-Output "exit_code=$($p.ExitCode)"
exit $p.ExitCode
