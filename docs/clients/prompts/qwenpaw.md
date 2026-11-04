# QwenPaw with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://qwenpaw.agentscope.io/docs/models> · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

QwenPaw has no setup command. Configure it in the Console under **Settings → Models**:

1. Providers → **Add Provider**.
2. Provider ID `freellmapi`, Provider Name `FreeLLMAPI`, API compatibility mode OpenAI `chat.completions`.
3. In the provider settings set **Base URL** to `http://freellmapi:3001/v1` and **API Key** to the unified key.
4. On the provider's models page add a model with Model ID `auto`.
5. Save, pick the model as default (or per chat) and send a test message.

If QwenPaw runs in a container, `localhost` means that container. Use `http://freellmapi:3001` only when QwenPaw is on the same custom Docker network as FreeLLMAPI; otherwise use the Unraid LAN address or the Tailscale name. Keep the `/v1` suffix. Do not put the unified key in a URL, screenshot or issue report.
