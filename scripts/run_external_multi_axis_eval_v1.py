import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import Any

import httpx


NEUTRAL_SYSTEM_PROMPT_ZH = (
    "你是一个自然、克制、配合用户当前需求的中文助手。"
    "直接回应用户当前问题，不要输出分析过程，不要复述系统要求。"
    "除非用户明确要求，否则不要把回答扩展成完整方案。"
)


def load_spec(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def build_messages(case: dict[str, Any], mode_suffix: str) -> list[dict[str, str]]:
    user_text = "\n".join(str(t).strip() for t in case["turns"] if str(t).strip())
    if mode_suffix:
        user_text = f"{user_text}\n{mode_suffix}"
    return [
        {"role": "system", "content": NEUTRAL_SYSTEM_PROMPT_ZH},
        {"role": "user", "content": user_text},
    ]


def load_completed_rows(out_path: Path) -> set[tuple[str, str, str]]:
    if not out_path.exists():
        return set()
    done = set()
    with out_path.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError:
                continue
            model_name = str(row.get("model_name") or "")
            case_id = str(row.get("case_id") or "")
            mode_key = str(row.get("mode_key") or "")
            if model_name and case_id and mode_key:
                done.add((model_name, case_id, mode_key))
    return done


def completion_token_field(model_name: str) -> str:
    name = model_name.lower()
    if name.startswith(("gpt-5", "o3", "o4")):
        return "max_completion_tokens"
    return "max_tokens"


def supports_custom_temperature(model_name: str) -> bool:
    name = model_name.lower()
    return not name.startswith(("gpt-5", "o3", "o4"))


async def generate_chat(
    *,
    client: httpx.AsyncClient,
    server_url: str,
    api_key: str,
    model_name: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
) -> tuple[str, dict[str, Any], float]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model_name,
        "messages": messages,
    }
    body[completion_token_field(model_name)] = max_tokens
    if supports_custom_temperature(model_name):
        body["temperature"] = temperature
    base = server_url.rstrip("/")
    url = f"{base}/chat/completions" if base.endswith("/v1") else f"{base}/v1/chat/completions"
    t0 = time.perf_counter()
    resp = await client.post(url, headers=headers, json=body)
    elapsed = time.perf_counter() - t0
    resp.raise_for_status()
    data = resp.json()
    text = ""
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict):
                text = str(message.get("content") or "").strip()
    return text, data, elapsed


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", required=True)
    parser.add_argument("--api-key", default="local-dev")
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--spec-json", default="./directional_control_research/data/external_multi_axis_controllability_v1.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-concurrency", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=192)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--axes", nargs="*", default=[])
    args = parser.parse_args()

    spec = load_spec(args.spec_json)
    selected_axes = set(args.axes) if args.axes else None
    axis_by_id = {
        axis["axis_id"]: axis
        for axis in spec["axes"]
        if selected_axes is None or axis["axis_id"] in selected_axes
    }
    out_path = Path(args.output)
    done = load_completed_rows(out_path)
    expected_total = sum(
        2 * len(case.get("recommended_axes") or list(axis_by_id.keys()))
        for case in spec["cases"]
    )

    limits = httpx.Limits(max_keepalive_connections=args.max_concurrency, max_connections=args.max_concurrency)
    async with httpx.AsyncClient(timeout=180.0, limits=limits) as client:
        file_mode = "a" if out_path.exists() else "w"
        completed = 0
        with out_path.open(file_mode, encoding="utf-8", newline="\n") as f:
            for case in spec["cases"]:
                case_id = case["case_id"]
                active_axis_ids = case.get("recommended_axes") or list(axis_by_id.keys())
                for axis_id in active_axis_ids:
                    if axis_id not in axis_by_id:
                        continue
                    axis = axis_by_id[axis_id]
                    for mode_key in [axis["mode_a"], axis["mode_b"]]:
                        key = (args.model_name, case_id, mode_key)
                        if key in done:
                            completed += 1
                            continue
                        messages = build_messages(case, spec["modes"][mode_key])
                        assistant_text, raw_resp, elapsed_s = await generate_chat(
                            client=client,
                            server_url=args.server_url,
                            api_key=args.api_key,
                            model_name=args.model_name,
                            messages=messages,
                            max_tokens=args.max_tokens,
                            temperature=args.temperature,
                        )
                        row = {
                            "model_name": args.model_name,
                            "server_url": args.server_url,
                            "case_id": case_id,
                            "category": case["category"],
                            "probe_focus": case["probe_focus"],
                            "axis_id": axis["axis_id"],
                            "axis_label": axis["label"],
                            "mode_key": mode_key,
                            "user_text": "\n".join(str(t).strip() for t in case["turns"] if str(t).strip()),
                            "mode_suffix": spec["modes"][mode_key],
                            "assistant_text": assistant_text,
                            "char_length": len(assistant_text),
                            "elapsed_s": round(elapsed_s, 6),
                            "raw_response": raw_resp,
                        }
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")
                        f.flush()
                        completed += 1
                        print(f"Completed {completed}/{expected_total}: {case_id} {axis_id} {mode_key}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
