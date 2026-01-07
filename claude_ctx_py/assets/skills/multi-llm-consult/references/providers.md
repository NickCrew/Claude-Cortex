# Provider Defaults

Use this reference when configuring or troubleshooting provider calls.

## OpenAI / Codex (openai)

- **API key env:** `OPENAI_API_KEY`
- **Optional base URL env:** `OPENAI_BASE_URL`
- **Default endpoint:** `https://api.openai.com/v1/chat/completions`
- **Default model:** `gpt-4o-mini`

## Gemini (gemini)

- **API key env:** `GEMINI_API_KEY`
- **Default endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/<model>:generateContent?key=API_KEY`
- **Default model:** `gemini-1.5-flash`

## Qwen / DashScope (qwen)

- **API key env:** `DASHSCOPE_API_KEY` (fallback: `QWEN_API_KEY`)
- **Optional base URL env:** `DASHSCOPE_BASE_URL`
- **Default endpoint:** `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`
- **Default model:** `qwen-plus`

## Settings.json Overrides

Keys can also be stored in the Claude settings file:

```json
{
  "llm_providers": {
    "openai": { "api_key": "...", "model": "...", "base_url": "..." },
    "gemini": { "api_key": "...", "model": "..." },
    "qwen": { "api_key": "...", "model": "...", "base_url": "..." }
  }
}
```

Leave fields blank in the TUI to keep existing values.
