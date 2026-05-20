$cfg = '.\directional_control_research\mechanism_experiment\configs\minimal_then_preference_baseline_task_primary_minanchor_stage3_gpu_medium_v1_1p5b.yaml'
$stdout = '.\directional_control_research\mechanism_experiment\outputs\train_minimal_then_preference_baseline_task_primary_minanchor_stage3_gpu_medium_v1_1p5b.stdout.log'
$stderr = '.\directional_control_research\mechanism_experiment\outputs\train_minimal_then_preference_baseline_task_primary_minanchor_stage3_gpu_medium_v1_1p5b.stderr.log'
$ps = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$proc = Start-Process -FilePath $ps -ArgumentList @('-ExecutionPolicy','Bypass','-File','.\directional_control_research\mechanism_experiment\scripts\run_train_dpo_from_config.ps1','-ConfigPath',$cfg) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Write-Host "exit_code=$($proc.ExitCode)"
