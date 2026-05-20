from pathlib import Path


def load_env_file(path: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for raw in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env
