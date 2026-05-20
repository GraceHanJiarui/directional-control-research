import argparse
import json
import sys
from pathlib import Path

import httpx

from env_utils import load_env_file
from run_external_multi_axis_eval_v1 import (
    build_messages,
    completion_token_field,
    load_spec,
    supports_custom_temperature,
)


def batch_api_base(base_url: str) -> str:
    base = base_url.rstrip("/")
    # Some OpenAI-compatible providers expose chat under /v1/chat/completions
    # but keep files/batches at the API root.
    if "api.deepseek.com" in base and base.endswith("/v1"):
        return base[:-3]
    return base


def build_request_rows(
    spec: dict, model_name: str, max_tokens: int, temperature: float, selected_axes: set[str] | None = None
) -> list[dict]:
    rows = []
    token_field = completion_token_field(model_name)
    include_temperature = supports_custom_temperature(model_name)
    axis_map = {
        axis["axis_id"]: axis
        for axis in spec["axes"]
        if selected_axes is None or axis["axis_id"] in selected_axes
    }
    for case in spec["cases"]:
        active_axis_ids = case.get("recommended_axes") or list(axis_map.keys())
        for axis_id in active_axis_ids:
            if axis_id not in axis_map:
                continue
            axis = axis_map[axis_id]
            for mode_key in [axis["mode_a"], axis["mode_b"]]:
                messages = build_messages(case, spec["modes"][mode_key])
                custom_id = f"{case['case_id']}__{axis_id}__{mode_key}"
                body = {
                    "model": model_name,
                    "messages": messages,
                    token_field: max_tokens,
                }
                if include_temperature:
                    body["temperature"] = temperature
                rows.append({
                    "custom_id": custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": body,
                })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--spec-json", default="./directional_control_research/data/external_multi_axis_controllability_v1.json")
    parser.add_argument("--max-tokens", type=int, default=192)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--axes", nargs="*", default=[])
    args = parser.parse_args()

    env = load_env_file(args.env_file)
    base_url = env["LLM_BASE_URL"].rstrip("/")
    batch_base_url = batch_api_base(base_url)
    api_key = env["LLM_API_KEY"]
    model_name = env["LLM_MODEL"]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    spec = load_spec(args.spec_json)
    selected_axes = set(args.axes) if args.axes else None
    requests_rows = build_request_rows(spec, model_name, args.max_tokens, args.temperature, selected_axes)
    requests_path = out_dir / "external_multi_axis_batch_requests_v1.jsonl"
    with requests_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in requests_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    headers = {"Authorization": f"Bearer {api_key}"}
    with httpx.Client(timeout=180.0) as client:
        with requests_path.open("rb") as fp:
            files_resp = client.post(
                f"{batch_base_url}/files",
                headers=headers,
                files={"file": (requests_path.name, fp, "application/jsonl")},
                data={"purpose": "batch"},
            )
        files_resp.raise_for_status()
        file_data = files_resp.json()
        input_file_id = file_data["id"]

        batch_resp = client.post(
            f"{batch_base_url}/batches",
            headers={**headers, "Content-Type": "application/json"},
            json={
                "input_file_id": input_file_id,
                "endpoint": "/v1/chat/completions",
                "completion_window": "24h",
                "metadata": {
                    "benchmark": "external_multi_axis_controllability_v1",
                    "model_name": model_name,
                },
            },
        )
        batch_resp.raise_for_status()
        batch_data = batch_resp.json()

    meta_path = out_dir / "external_multi_axis_batch_submission_v1.json"
    meta = {
        "model_name": model_name,
        "base_url": base_url,
        "batch_base_url": batch_base_url,
        "input_file_id": input_file_id,
        "batch_id": batch_data["id"],
        "requests_path": str(requests_path),
        "submission_response": batch_data,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"batch_id": batch_data["id"], "input_file_id": input_file_id, "meta_path": str(meta_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
