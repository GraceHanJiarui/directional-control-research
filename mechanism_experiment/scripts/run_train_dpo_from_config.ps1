param(
  [Parameter(Mandatory=$true)][string]$ConfigPath
)

$pythonExe = 'C:\Users\GRACESLAPTOP\.conda\envs\py311\python.exe'
$env:KMP_DUPLICATE_LIB_OK = 'TRUE'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:TOKENIZERS_PARALLELISM = 'false'

$cfg = @{}
Get-Content $ConfigPath | ForEach-Object {
  if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
  $parts = $_ -split ':', 2
  $cfg[$parts[0].Trim()] = $parts[1].Trim()
}

$repoRoot = Resolve-Path '.'
$mechRoot = Join-Path $repoRoot 'directional_control_research\mechanism_experiment'

function Resolve-ConfigPath([string]$baseDir, [string]$relativePath) {
  $candidate = Join-Path $baseDir $relativePath
  return [System.IO.Path]::GetFullPath($candidate)
}

$configDir = Split-Path -Parent (Resolve-Path $ConfigPath)
$argsList = @(
  (Join-Path $mechRoot 'scripts\train_dpo_mechanism.py'),
  '--model-name', $cfg['model_name'],
  '--train-file', (Resolve-ConfigPath $configDir $cfg['train_file']),
  '--output-dir', (Resolve-ConfigPath $mechRoot $cfg['output_dir']),
  '--init-adapter-path', (Resolve-ConfigPath $mechRoot $cfg['init_adapter_path']),
  '--max-length', [string]([int]$cfg['max_length']),
  '--learning-rate', [string]([double]$cfg['learning_rate']),
  '--num-epochs', [string]([double]$cfg['num_epochs']),
  '--per-device-batch-size', [string]([int]$cfg['per_device_batch_size']),
  '--grad-accum', [string]([int]$cfg['grad_accum']),
  '--beta', [string]([double]$cfg['beta'])
)

if ($cfg.ContainsKey('ref_adapter_path') -and $cfg['ref_adapter_path']) {
  $argsList += @('--ref-adapter-path', (Resolve-ConfigPath $mechRoot $cfg['ref_adapter_path']))
}
if ($cfg.ContainsKey('device') -and $cfg['device']) {
  $argsList += @('--device', $cfg['device'])
}

& $pythonExe $argsList
