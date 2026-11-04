# Cursor with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://docs.cursor.com> · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

**Cursor does not work with a private gateway.** Cursor sends model traffic through its own cloud service, so addresses such as `http://freellmapi:3001`, a LAN IP or a Tailscale name are not reachable from it. This is a Cursor limitation, not a FreeLLMAPI one.

The only way is to publish the gateway on a public HTTPS URL, for example through a tunnel. FreeLLMAPI is a single-user application guarded only by its API key, so exposing it publicly is a real risk. If you do it anyway:

- Use a tunnel with its own authentication, and rotate the unified key afterwards.
- Prefer a separately revocable URL token over the unified key (Keys → Agents in the dashboard). Tokens live at `/v1/t/<token>/...`.
- In Cursor: Settings → Models → enable **Override OpenAI Base URL** and enter `<public-url>/v1`. Add a custom model named `auto`.
- Cursor documents custom keys only for standard chat models, so Responses-based or built-in models may not work with the override. The override applies globally while enabled.

There is no prompt for Cursor because there is nothing an agent can configure on disk. `npx --yes freellmapi setup-cursor` prints this guide.
