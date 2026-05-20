$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$powershell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$stdout = Join-Path $root 'outputs\train_internlm2_baseline_sft_v1_1p8b.stdout.log'
$stderr = Join-Path $root 'outputs\train_internlm2_baseline_sft_v1_1p8b.stderr.log'
$env:PYTHONIOENCODING = 'utf-8'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:KMP_DUPLICATE_LIB_OK = 'TRUE'
$env:HF_MODULES_CACHE = (Join-Path $root 'outputs\hf_modules_cache')
Write-Output $powershell
$p = Start-Process -FilePath $powershell -ArgumentList @(
  '-ExecutionPolicy','Bypass',
  '-File','.\directional_control_research\mechanism_experiment\scripts\run_train_from_config.ps1',
  '-ConfigPath','./directional_control_research/mechanism_experiment/configs/baseline_sft_v1_internlm2_1p8b.yaml'
) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Write-Output "exit_code=$($p.ExitCode)"
exit $p.ExitCode
