$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$repoRoot = Resolve-Path (Join-Path $root '..\..')
$python = 'C:\Users\GRACESLAPTOP\.conda\envs\py311\python.exe'
$stdout = Join-Path $repoRoot 'resume\caveat_v1\train_baseline_then_no_extra_caveat_stage2_v1_qwen25_1p5b.stdout.log'
$stderr = Join-Path $repoRoot 'resume\caveat_v1\train_baseline_then_no_extra_caveat_stage2_v1_qwen25_1p5b.stderr.log'
$null = New-Item -ItemType Directory -Force -Path (Split-Path $stdout)
$env:PYTHONIOENCODING = 'utf-8'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:KMP_DUPLICATE_LIB_OK = 'TRUE'
Write-Output $python
$p = Start-Process -FilePath $python -ArgumentList @(
  '.\directional_control_research\mechanism_experiment\scripts\train_qlora_mechanism.py',
  '--model-name','Qwen/Qwen2.5-1.5B',
  '--train-file','.\resume\caveat_v1\built_caveat_v1\no_extra_caveat_sft_train.jsonl',
  '--output-dir','.\resume\qwen25_1p5b_baseline_then_no_extra_caveat_stage2_v1',
  '--init-adapter-path','.\directional_control_research\mechanism_experiment\outputs\qwen25_1p5b_baseline_sft_v5',
  '--max-length','1024',
  '--learning-rate','5e-5',
  '--num-epochs','1.0',
  '--per-device-batch-size','1',
  '--grad-accum','16'
) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Write-Output "exit_code=$($p.ExitCode)"
exit $p.ExitCode
