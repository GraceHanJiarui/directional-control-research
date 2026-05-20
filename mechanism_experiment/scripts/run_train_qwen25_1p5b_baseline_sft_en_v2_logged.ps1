$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$powershell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$stdout = Join-Path $root 'outputs\train_qwen25_1p5b_baseline_sft_en_v2.stdout.log'
$stderr = Join-Path $root 'outputs\train_qwen25_1p5b_baseline_sft_en_v2.stderr.log'
$env:PYTHONIOENCODING = 'utf-8'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:KMP_DUPLICATE_LIB_OK = 'TRUE'
Write-Output $powershell
$p = Start-Process -FilePath $powershell -ArgumentList @(
  '-ExecutionPolicy','Bypass',
  '-File','.\directional_control_research\mechanism_experiment\scripts\run_train_from_config.ps1',
  '-ConfigPath','./directional_control_research/mechanism_experiment/configs/baseline_sft_en_v2_qwen25_1p5b.yaml'
) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Write-Output "exit_code=$($p.ExitCode)"
exit $p.ExitCode
