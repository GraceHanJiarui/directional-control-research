# Qwen2.5-0.5B Mechanism Experiment Commands

## Train

```powershell
powershell -ExecutionPolicy Bypass -File ./directional_control_research/mechanism_experiment/scripts/run_train_v5_baseline_qwen25_0p5b_logged.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File ./directional_control_research/mechanism_experiment/scripts/run_train_v5_anti_qwen25_0p5b_logged.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File ./directional_control_research/mechanism_experiment/scripts/run_train_v5_minimal_qwen25_0p5b_logged.ps1
```

## Eval

```powershell
C:\Users\GRACESLAPTOP\.conda\envs\py311\python.exe .\directional_control_research\mechanism_experiment\scripts\eval_lora_adapter.py --base-model Qwen/Qwen2.5-0.5B --adapter-path .\directional_control_research\mechanism_experiment\outputs\qwen25_0p5b_baseline_sft_v5 --cases-json .\directional_control_research\mechanism_experiment\data\heldout_eval_zh_12.json --output .\directional_control_research\mechanism_experiment\outputs\qwen25_0p5b_baseline_sft_v5_eval.jsonl --device cpu
```

```powershell
C:\Users\GRACESLAPTOP\.conda\envs\py311\python.exe .\directional_control_research\mechanism_experiment\scripts\eval_lora_adapter.py --base-model Qwen/Qwen2.5-0.5B --adapter-path .\directional_control_research\mechanism_experiment\outputs\qwen25_0p5b_anti_underanswer_sft_v5 --cases-json .\directional_control_research\mechanism_experiment\data\heldout_eval_zh_12.json --output .\directional_control_research\mechanism_experiment\outputs\qwen25_0p5b_anti_underanswer_sft_v5_eval.jsonl --device cpu
```

```powershell
C:\Users\GRACESLAPTOP\.conda\envs\py311\python.exe .\directional_control_research\mechanism_experiment\scripts\eval_lora_adapter.py --base-model Qwen/Qwen2.5-0.5B --adapter-path .\directional_control_research\mechanism_experiment\outputs\qwen25_0p5b_minimal_boundary_sft_v5 --cases-json .\directional_control_research\mechanism_experiment\data\heldout_eval_zh_12.json --output .\directional_control_research\mechanism_experiment\outputs\qwen25_0p5b_minimal_boundary_sft_v5_eval.jsonl --device cpu
```
