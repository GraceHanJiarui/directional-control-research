$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$powershell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$stdout = Join-Path $root 'outputs\train_smollm2_1p7b_minimal_boundary_sft_en_v1.stdout.log'
$stderr = Join-Path $root 'outputs\train_smollm2_1p7b_minimal_boundary_sft_en_v1.stderr.log'
$env:PYTHONIOENCODING = 'utf-8'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:KMP_DUPLICATE_LIB_OK = 'TRUE'
$env:HF_MODULES_CACHE = (Join-Path $root 'outputs\hf_modules_cache')
Write-Output $powershell
$p = Start-Process -FilePath $powershell -ArgumentList @(
  '-ExecutionPolicy','Bypass',
  '-File','.\directional_control_research\mechanism_experiment\scripts\run_train_from_config.ps1',
  '-ConfigPath','./directional_control_research/mechanism_experiment/configs/minimal_boundary_sft_en_v1_smollm2_1p7b.yaml'
) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Write-Output "exit_code=$($p.ExitCode)"
exit $p.ExitCode
