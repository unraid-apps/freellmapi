# Claude Code with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://docs.anthropic.com/en/docs/claude-code> · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

|  |  |
| --- | --- |
| Optional CLI shortcut | `npx --yes freellmapi setup-claude` (writes the same entries; not required) |
| Wire | Anthropic Messages (the agent appends its own path, so the base URL is the server root WITHOUT /v1) |
| Base URL form | root URL (no /v1) |
| Profile support | yes (`--profile local` leaves the default model alone) |
| API key | stored in a config file by design |

Claude Code speaks the Anthropic Messages API. FreeLLMAPI serves it at the server root, so never add /v1 to the Claude Code base URL.

## Prompt

Copy this into Claude Code (or any coding agent) on the machine where Claude Code runs. FreeLLMAPI is configured like any other OpenAI-compatible endpoint, so **nothing has to be installed for it** on that machine. Edit the three parameters at the top first. The default gateway address assumes the agent runs in a container on the same custom Docker network as FreeLLMAPI; see [choosing the gateway address](../README.md#choosing-the-gateway-address) for the other cases.

````text
Add FreeLLMAPI as an additional model provider for Claude Code on this machine, without changing my default model. Afterwards I want to use the model "auto" through FreeLLMAPI.

Parameters (edit before sending):
- GATEWAY: http://freellmapi:3001  (used below as the shell variable $GATEWAY)
- PROFILE: local
- MODEL: auto
- API KEY: expected in the environment variable FREELLMAPI_API_KEY. If it is not set, ask me for the unified key (it starts with "freellmapi-").

Rules:
- FreeLLMAPI is an ordinary OpenAI-compatible endpoint, configured like any other provider such as Ollama. Nothing has to be installed for it on this machine. Do not install packages and do not change PATH.
- Never print the API key, never put it in a command line argument, never write it anywhere except where this task says the configuration stores it. Do not echo it in your replies or in logs.
- Only touch files that belong to Claude Code. Do not change anything else on this machine.
- Before you change an existing config file, make a timestamped backup copy and keep its permissions.
- If anything looks wrong, stop and show me the exact error without the key.
- Run all commands in one shell session so exported variables carry over.

Steps:
1. Reachability. Run `export GATEWAY=<the GATEWAY value above>`, then `curl -sS $GATEWAY/api/ping`. If the host name does not resolve or the connection fails, stop and tell me. This machine is then probably not on the same Docker network as FreeLLMAPI. Do not guess another address.
2. Catalog. Run `curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" $GATEWAY/v1/models` and confirm that a model with id "auto" is listed. A 401 means the key is wrong.
3. Configure. Add the provider entry directly. Add exactly this and change nothing else (the examples use http://freellmapi:3001; use your GATEWAY value if you changed it):

Write `~/.claude/profiles/local/settings.json` (create the directory, mode 0600). If the file exists, merge the `env` keys and keep everything else:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://freellmapi:3001",
    "ANTHROPIC_AUTH_TOKEN": "<value of FREELLMAPI_API_KEY>",
    "ANTHROPIC_MODEL": "auto",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "auto",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "auto",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "auto",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "128000",
    "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY": "1"
  }
}
```

   Expected result: one new file ~/.claude/profiles/local/settings.json with an env block (ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_MODEL and the three ANTHROPIC_DEFAULT_*_MODEL variables, all set to auto). ~/.claude/settings.json must not change.

   Optional shortcut: if Node.js >= 20.18 and < 25 with npx is ALREADY installed on this machine, the official FreeLLMAPI CLI writes the same entries. Export `FREELLMAPI_URL=$GATEWAY`, run `npx --yes freellmapi setup-claude --profile local --model auto --dry-run`, show me the diff, apply only if it matches the expected result above, then run it again without --dry-run. Do not install Node.js for this; the direct way works without it.
4. Verify. The file is mode 0600. The gateway URL in it has no /v1 suffix. The key is stored in this file by design; do not copy the file anywhere or print it.
5. Test. CLAUDE_CONFIG_DIR=~/.claude/profiles/local claude -p "Say hello" (best effort: check `--help` for the exact one-shot syntax)
6. Follow-up. Nothing to restart. Tell me to start it with CLAUDE_CONFIG_DIR=~/.claude/profiles/local claude. For a variant that never writes the key to disk, mention `npx --yes freellmapi launch`.

Final report: list the files you changed, what the test returned, and exactly what I type or run to use FreeLLMAPI with model "auto". Expected selector: CLAUDE_CONFIG_DIR=~/.claude/profiles/local claude.
````

Prompts are derived from the FreeLLMAPI CLI 0.8.2 source and the upstream documentation. They have not been run against every agent; the expected-result check in step 3 and the test in step 5 are the safety net.
