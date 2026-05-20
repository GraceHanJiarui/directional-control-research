import argparse
import json
from pathlib import Path

import httpx

from env_utils import load_env_file


ANTHROPIC_VERSION = "2023-06-01"


def load_request_map(requests_path: str) -> dict[str, dict]:
    payload = json.loads(Path(requests_path).read_text(encoding="utf-8"))
    return {row["custom_id"]: row for row in payload["requests"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--requests-json", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    env = load_env_file(args.env_file)
    base_url = env["LLM_BASE_URL"].rstrip("/")
    api_key = env["LLM_API_KEY"]
    model_name = env["LLM_MODEL"]
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
    }
    request_map = load_request_map(args.requests_json)

    with httpx.Client(timeout=180.0) as client:
        batch_resp = client.get(f"{base_url}/v1/messages/batches/{args.batch_id}", headers=headers)
        batch_resp.raise_for_status()
        batch_data = batch_resp.json()
        out = {"batch": batch_data}

        if batch_data.get("processing_status") == "ended":
            results_resp = client.get(f"{base_url}/v1/messages/batches/{args.batch_id}/results", headers=headers)
            results_resp.raise_for_status()
            result_lines = results_resp.text.splitlines()
            rows = []
            for raw in result_lines:
                if not raw.strip():
                    continue
                item = json.loads(raw)
                custom_id = item["custom_id"]
                req = request_map[custom_id]
                case_id = req["case_id"]
                axis_id = req["axis_id"]
                mode_key = req["mode_key"]
                result = item.get("result", {})
                result_type = result.get("type")
                assistant_text = ""
                if result_type == "succeeded":
                    message = result.get("message", {})
                    content = message.get("content", [])
                    texts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            texts.append(block.get("text", ""))
                    assistant_text = "\n".join(t for t in texts if t).strip()
                row = {
                    "model_name": model_name,
                    "case_id": case_id,
                    "axis_id": axis_id,
                    "mode_key": mode_key,
                    "assistant_text": assistant_text,
                    "char_length": len(assistant_text),
                    "raw_result": item,
                }
                rows.append(row)
            out_path = Path(args.output)
            with out_path.open("w", encoding="utf-8", newline="\n") as f:
                for row in rows:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            out["output_path"] = args.output

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
