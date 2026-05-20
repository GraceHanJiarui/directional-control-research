import argparse
import json
from pathlib import Path

import httpx

from env_utils import load_env_file


def batch_api_base(base_url: str) -> str:
    base = base_url.rstrip("/")
    if "api.deepseek.com" in base and base.endswith("/v1"):
        return base[:-3]
    return base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    env = load_env_file(args.env_file)
    base_url = env["LLM_BASE_URL"].rstrip("/")
    batch_base_url = batch_api_base(base_url)
    api_key = env["LLM_API_KEY"]
    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client(timeout=180.0) as client:
        batch_resp = client.get(f"{batch_base_url}/batches/{args.batch_id}", headers=headers)
        batch_resp.raise_for_status()
        batch_data = batch_resp.json()

        out = {
            "batch": batch_data,
        }

        output_file_id = batch_data.get("output_file_id")
        if output_file_id:
            file_resp = client.get(f"{batch_base_url}/files/{output_file_id}/content", headers=headers)
            file_resp.raise_for_status()
            Path(args.output).write_bytes(file_resp.content)
            out["output_path"] = args.output

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
