import argparse
import subprocess
import sys
from pathlib import Path

from env_utils import load_env_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--spec-json", default="./directional_control_research/data/external_multi_axis_controllability_v1.json")
    parser.add_argument("--axes", nargs="*", default=[])
    parser.add_argument("--max-tokens", type=int, default=192)
    parser.add_argument("--temperature", type=float, default=0.2)
    args = parser.parse_args()

    env = load_env_file(args.env_file)
    server_url = env["LLM_BASE_URL"]
    api_key = env["LLM_API_KEY"]
    model_name = env["LLM_MODEL"]

    cmd = [
        sys.executable,
        str(Path(__file__).resolve().with_name("run_external_multi_axis_eval_v1.py")),
        "--server-url", server_url,
        "--api-key", api_key,
        "--model-name", model_name,
        "--spec-json", args.spec_json,
        "--output", args.output,
        "--max-tokens", str(args.max_tokens),
        "--temperature", str(args.temperature),
    ]
    if args.axes:
        cmd += ["--axes", *args.axes]
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
