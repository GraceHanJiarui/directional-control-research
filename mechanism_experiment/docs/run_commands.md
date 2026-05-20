# Immediate Commands (v3)

## 1. Rebuild per-variant datasets from the current v3 triplets
```powershell
python .\directional_control_research\mechanism_experiment\scripts\build_triplet_sft_datasets.py `
  --input .\directional_control_research\mechanism_experiment\data\train_triplets_v3_216.jsonl `
  --out-dir .\directional_control_research\mechanism_experiment\data\built_v3
```

## 2. Train baseline
```powershell
powershell -ExecutionPolicy Bypass -File .\directional_control_research\mechanism_experiment\scripts\run_train_from_config.ps1 `
  -ConfigPath .\directional_control_research\mechanism_experiment\configs\baseline_sft_v3.yaml
```

## 3. Train anti-underanswer
```powershell
powershell -ExecutionPolicy Bypass -File .\directional_control_research\mechanism_experiment\scripts\run_train_from_config.ps1 `
  -ConfigPath .\directional_control_research\mechanism_experiment\configs\anti_underanswer_sft_v3.yaml
```

## 4. Train minimal-boundary
```powershell
powershell -ExecutionPolicy Bypass -File .\directional_control_research\mechanism_experiment\scripts\run_train_from_config.ps1 `
  -ConfigPath .\directional_control_research\mechanism_experiment\configs\minimal_boundary_sft_v3.yaml
```

## Note
Current configs use plain LoRA by default (`use_4bit: false`) for better Windows compatibility.
