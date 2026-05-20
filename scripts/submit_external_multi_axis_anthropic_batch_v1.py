import argparse
import json
from pathlib import Path

import httpx

from env_utils import load_env_file
from run_external_multi_axis_eval_v1 import build_messages, load_spec


ANTHROPIC_VERSION = "2023-06-01"


def build_request_rows(
    spec: dict, model_name: str, max_tokens: int, temperature: float, selected_axes: set[str] | None = None
) -> list[dict]:
    rows = []
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
                system_prompt = ""
                anthro_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        system_prompt = msg["content"]
                    else:
                        anthro_messages.append({"role": msg["role"], "content": msg["content"]})
                custom_id = f"r{len(rows):03d}"
                params = {
                    "model": model_name,
                    "max_tokens": max_tokens,
                    "messages": anthro_messages,
                }
                if system_prompt:
                    params["system"] = system_prompt
                if temperature is not None:
                    params["temperature"] = temperature
                rows.append(
                    {
                        "custom_id": custom_id,
                        "case_id": case["case_id"],
                        "axis_id": axis_id,
                        "mode_key": mode_key,
                        "params": params,
                    }
                )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument(
        "--spec-json",
        default="./directional_control_research/data/external_multi_axis_controllability_v1.json",
    )
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--axes", nargs="*", default=[])
    args = parser.parse_args()

    env = load_env_file(args.env_file)
    base_url = env["LLM_BASE_URL"].rstrip("/")
    api_key = env["LLM_API_KEY"]
    model_name = env["LLM_MODEL"]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    spec = load_spec(args.spec_json)
    selected_axes = set(args.axes) if args.axes else None
    request_rows = build_request_rows(spec, model_name, args.max_tokens, args.temperature, selected_axes)

    requests_path = out_dir / "external_multi_axis_anthropic_batch_requests_v1.json"
    requests_path.write_text(json.dumps({"requests": request_rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    api_rows = [{"custom_id": row["custom_id"], "params": row["params"]} for row in request_rows]

    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    with httpx.Client(timeout=180.0) as client:
        resp = client.post(
            f"{base_url}/v1/messages/batches",
            headers=headers,
            json={"requests": api_rows},
        )
        if resp.status_code >= 400:
            print(resp.text)
            resp.raise_for_status()
        batch_data = resp.json()

    meta_path = out_dir / "external_multi_axis_anthropic_batch_submission_v1.json"
    meta = {
        "model_name": model_name,
        "base_url": base_url,
        "batch_id": batch_data["id"],
        "requests_path": str(requests_path),
        "submission_response": batch_data,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"batch_id": batch_data["id"], "meta_path": str(meta_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
