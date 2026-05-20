$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $root "..\..\..")
Set-Location $repo
$stdout = ".\directional_control_research\mechanism_experiment\outputs\train_proactive_bundle_proxy_v1_1p5b.stdout.log"
$stderr = ".\directional_control_research\mechanism_experiment\outputs\train_proactive_bundle_proxy_v1_1p5b.stderr.log"
New-Item -ItemType Directory -Force -Path ".\directional_control_research\mechanism_experiment\outputs" | Out-Null
$python = (Get-Command python).Source
$argList = @(
  ".\directional_control_research\mechanism_experiment\scripts\train_qlora_mechanism.py",
  "--model-name", "Qwen/Qwen2.5-1.5B",
  "--train-file", ".\directional_control_research\mechanism_experiment\data\built_q6\proactive_bundle_proxy_v1_train.jsonl",
  "--output-dir", ".\directional_control_research\mechanism_experiment\outputs\qwen25_1p5b_proactive_bundle_proxy_v1",
  "--max-length", "768",
  "--learning-rate", "5e-5",
  "--num-epochs", "0.75",
  "--per-device-batch-size", "1",
  "--grad-accum", "16"
)
$p = Start-Process -FilePath $python -ArgumentList $argList -RedirectStandardOutput $stdout -RedirectStandardError $stderr -NoNewWindow -PassThru -Wait
$code = $p.ExitCode
Write-Host "exit_code=$code"
exit $code
