#!/usr/bin/env python3
"""Consult external LLM providers for a second opinion or delegated task."""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


PROVIDER_ALIASES = {
    "codex": "openai",
    "codex-cli": "openai",
    "openai": "openai",
    "gemini": "gemini",
    "qwen": "qwen",
    "dashscope": "qwen",
}

ENV_API_KEYS = {
    "openai": ["OPENAI_API_KEY"],
    "gemini": ["GEMINI_API_KEY"],
    "qwen": ["DASHSCOPE_API_KEY", "QWEN_API_KEY"],
}

ENV_BASE_URLS = {
    "openai": ["OPENAI_BASE_URL"],
    "qwen": ["DASHSCOPE_BASE_URL", "QWEN_BASE_URL"],
}

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-1.5-flash",
    "qwen": "qwen-plus",
}

DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
}

PURPOSE_HINTS = {
    "second-opinion": "Provide a concise second opinion. Focus on risks, gaps, and alternative approaches.",
    "plan": "Provide a clear step-by-step plan with risks and dependencies.",
    "review": "Review the provided content critically. Call out issues and propose fixes.",
    "delegate": "Take ownership of the task and return a direct, actionable result.",
}


def _resolve_settings_path() -> Path:
    override = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if override:
        candidate = Path(override).expanduser().resolve()
        if candidate.exists():
            return candidate / "settings.json"
    return Path.home() / ".claude" / "settings.json"


def _load_settings() -> Dict[str, Any]:
    settings_path = _resolve_settings_path()
    if not settings_path.exists():
        return {}
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _provider_config(settings: Dict[str, Any], provider: str) -> Dict[str, Any]:
    providers = settings.get("llm_providers", {})
    if not isinstance(providers, dict):
        return {}
    entry = providers.get(provider, {})
    return entry if isinstance(entry, dict) else {}


def _get_api_key(provider: str, config: Dict[str, Any]) -> Optional[str]:
    key = config.get("api_key")
    if isinstance(key, str) and key.strip():
        return key.strip()
    for env_name in ENV_API_KEYS.get(provider, []):
        env_val = os.environ.get(env_name)
        if env_val:
            return env_val
    return None


def _get_model(provider: str, config: Dict[str, Any], override: Optional[str]) -> str:
    if override:
        return override
    model = config.get("model")
    if isinstance(model, str) and model.strip():
        return model.strip()
    return DEFAULT_MODELS[provider]


def _get_base_url(provider: str, config: Dict[str, Any], override: Optional[str]) -> Optional[str]:
    if override:
        return override
    base_url = config.get("base_url")
    if isinstance(base_url, str) and base_url.strip():
        return base_url.strip()
    for env_name in ENV_BASE_URLS.get(provider, []):
        env_val = os.environ.get(env_name)
        if env_val:
            return env_val
    return DEFAULT_BASE_URLS.get(provider)


def _request_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    parsed = json.loads(raw)
    return parsed if isinstance(parsed, dict) else {}


def _call_openai_like(
    url: str,
    api_key: str,
    model: str,
    prompt: str,
    system: Optional[str],
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    response = _request_json(url, headers, payload, timeout)
    choices = response.get("choices", [])
    if choices and isinstance(choices, list):
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
    raise RuntimeError("Unexpected response format from provider")


def _call_gemini(
    api_key: str,
    model: str,
    prompt: str,
    system: Optional[str],
    temperature: float,
    max_tokens: int,
    timeout: int,
    base_url: Optional[str],
) -> str:
    if base_url:
        url = base_url
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload: Dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}

    headers = {"Content-Type": "application/json"}
    response = _request_json(url, headers, payload, timeout)
    candidates = response.get("candidates", [])
    if candidates and isinstance(candidates, list):
        content = candidates[0].get("content", {})
        parts = content.get("parts", []) if isinstance(content, dict) else []
        if parts:
            text = parts[0].get("text")
            if isinstance(text, str):
                return text.strip()
    raise RuntimeError("Unexpected response format from Gemini")


def _normalize_provider(provider: str) -> str:
    key = provider.strip().lower()
    if key in PROVIDER_ALIASES:
        return PROVIDER_ALIASES[key]
    raise ValueError(f"Unsupported provider: {provider}")


def _load_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if args.prompt:
        return args.prompt
    data = sys.stdin.read()
    return data.strip()


def _augment_prompt(prompt: str, context_file: Optional[str]) -> str:
    if not context_file:
        return prompt
    context_path = Path(context_file)
    if not context_path.exists():
        raise FileNotFoundError(f"Context file not found: {context_file}")
    context_text = context_path.read_text(encoding="utf-8")
    return f"{prompt}\n\nContext:\n{context_text}".strip()


def _build_system_prompt(args: argparse.Namespace) -> Optional[str]:
    if args.system:
        return args.system
    if args.purpose:
        return PURPOSE_HINTS.get(args.purpose.lower())
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consult external LLM providers (Gemini/OpenAI/Qwen) for a second opinion.",
    )
    parser.add_argument("--provider", required=True, help="openai|codex|gemini|qwen")
    parser.add_argument("--prompt", help="Prompt text (if omitted, read stdin)")
    parser.add_argument("--prompt-file", help="Path to a prompt file")
    parser.add_argument("--context-file", help="Append context from file")
    parser.add_argument("--purpose", help="second-opinion|plan|review|delegate")
    parser.add_argument("--system", help="Override system prompt")
    parser.add_argument("--model", help="Override model name")
    parser.add_argument("--base-url", help="Override base URL for provider")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-output-tokens", type=int, default=800)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--show-metadata", action="store_true", help="Print provider metadata")

    args = parser.parse_args()

    if args.prompt and args.prompt_file:
        parser.error("Use --prompt OR --prompt-file, not both.")

    provider = _normalize_provider(args.provider)
    settings = _load_settings()
    config = _provider_config(settings, provider)

    api_key = _get_api_key(provider, config)
    if not api_key:
        envs = ", ".join(ENV_API_KEYS.get(provider, []))
        raise SystemExit(
            f"Missing API key for {provider}. Set in settings.json under llm_providers.{provider}.api_key "
            f"or via env ({envs})."
        )

    prompt = _load_prompt(args)
    if not prompt:
        raise SystemExit("Prompt is empty. Provide --prompt, --prompt-file, or stdin.")
    prompt = _augment_prompt(prompt, args.context_file)

    system_prompt = _build_system_prompt(args)
    model = _get_model(provider, config, args.model)
    base_url = _get_base_url(provider, config, args.base_url)

    try:
        if provider == "gemini":
            response_text = _call_gemini(
                api_key,
                model,
                prompt,
                system_prompt,
                args.temperature,
                args.max_output_tokens,
                args.timeout,
                base_url,
            )
        else:
            if not base_url:
                raise RuntimeError("Missing base URL for provider.")
            response_text = _call_openai_like(
                base_url,
                api_key,
                model,
                prompt,
                system_prompt,
                args.temperature,
                args.max_output_tokens,
                args.timeout,
            )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        message = textwrap.dedent(
            f"""
            Request failed: {exc.code} {exc.reason}
            {body}
            """
        ).strip()
        raise SystemExit(message)
    except Exception as exc:
        raise SystemExit(str(exc))

    if args.show_metadata:
        meta = f"[{provider}] model={model}"
        print(meta)
        print("-" * len(meta))

    print(response_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
