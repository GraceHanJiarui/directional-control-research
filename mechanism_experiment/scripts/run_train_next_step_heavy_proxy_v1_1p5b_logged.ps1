$cfg = '.\directional_control_research\mechanism_experiment\configs\next_step_heavy_proxy_v1_1p5b.yaml'
$stdout = '.\directional_control_research\mechanism_experiment\outputs\train_next_step_heavy_proxy_v1_1p5b.stdout.log'
$stderr = '.\directional_control_research\mechanism_experiment\outputs\train_next_step_heavy_proxy_v1_1p5b.stderr.log'
$ps = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$proc = Start-Process -FilePath $ps -ArgumentList @('-ExecutionPolicy','Bypass','-File','.\directional_control_research\mechanism_experiment\scripts\run_train_from_config.ps1','-ConfigPath',$cfg) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
Write-Host "exit_code=$($proc.ExitCode)"
