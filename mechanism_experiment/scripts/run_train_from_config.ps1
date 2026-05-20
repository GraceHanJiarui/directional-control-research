param(
  [Parameter(Mandatory=$true)][string]$ConfigPath
)

$cfg = @{}
Get-Content $ConfigPath | ForEach-Object {
  if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
  $parts = $_ -split ':', 2
  $cfg[$parts[0].Trim()] = $parts[1].Trim()
}

$common = @(
  '.\\directional_control_research\\mechanism_experiment\\scripts\\train_qlora_mechanism.py',
  '--model-name', $cfg['model_name'],
  '--train-file', (Join-Path '.\\directional_control_research\\mechanism_experiment' $cfg['train_file']),
  '--output-dir', (Join-Path '.\\directional_control_research\\mechanism_experiment' $cfg['output_dir']),
  '--max-length', [string]([int]$cfg['max_length']),
  '--learning-rate', [string]([double]$cfg['learning_rate']),
  '--num-epochs', [string]([double]$cfg['num_epochs']),
  '--per-device-batch-size', [string]([int]$cfg['per_device_batch_size']),
  '--grad-accum', [string]([int]$cfg['grad_accum'])
)

$argsList = @($common)
if ($cfg.ContainsKey('init_adapter_path') -and $cfg['init_adapter_path']) {
  $argsList += @('--init-adapter-path', (Join-Path '.\directional_control_research\mechanism_experiment' $cfg['init_adapter_path']))
}
if ($cfg.ContainsKey('use_4bit') -and $cfg['use_4bit'] -eq 'true') {
  python @($argsList + '--use-4bit')
} else {
  python $argsList
}
