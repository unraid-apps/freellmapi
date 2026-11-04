# Goose with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://block.github.io/goose> · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

|  |  |
| --- | --- |
| Optional CLI shortcut | `npx --yes freellmapi setup-goose` (writes the same entries; not required) |
| Wire | OpenAI Chat Completions, base URL with /v1 |
| Base URL form | `/v1` URL |
| Profile support | no (the command makes FreeLLMAPI the default and merges into the existing config) |
| API key | kept out of the config files (environment variable or separate `.env`) |


## Prompt

Copy this into Goose (or any coding agent) on the machine where Goose runs. FreeLLMAPI is configured like any other OpenAI-compatible endpoint, so **nothing has to be installed for it** on that machine. Edit the three parameters at the top first. The default gateway address assumes the agent runs in a container on the same custom Docker network as FreeLLMAPI; see [choosing the gateway address](../README.md#choosing-the-gateway-address) for the other cases.

````text
Add FreeLLMAPI as a model provider for Goose on this machine, using the model "auto". Keep my other providers and settings.

Parameters (edit before sending):
- GATEWAY: http://freellmapi:3001  (used below as the shell variable $GATEWAY)
- PROFILE: (not used: this agent has no profile concept)
- MODEL: auto
- API KEY: expected in the environment variable FREELLMAPI_API_KEY. If it is not set, ask me for the unified key (it starts with "freellmapi-").

Rules:
- FreeLLMAPI is an ordinary OpenAI-compatible endpoint, configured like any other provider such as Ollama. Nothing has to be installed for it on this machine. Do not install packages and do not change PATH.
- Never print the API key, never put it in a command line argument, never write it anywhere except where this task says the configuration stores it. Do not echo it in your replies or in logs.
- Only touch files that belong to Goose. Do not change anything else on this machine.
- Before you change an existing config file, make a timestamped backup copy and keep its permissions.
- If anything looks wrong, stop and show me the exact error without the key.
- Run all commands in one shell session so exported variables carry over.

Steps:
1. Reachability. Run `export GATEWAY=<the GATEWAY value above>`, then `curl -sS $GATEWAY/api/ping`. If the host name does not resolve or the connection fails, stop and tell me. This machine is then probably not on the same Docker network as FreeLLMAPI. Do not guess another address.
2. Catalog. Run `curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" $GATEWAY/v1/models` and confirm that a model with id "auto" is listed. A 401 means the key is wrong.
3. Configure. Add the provider entry directly. Add exactly this and change nothing else (the examples use http://freellmapi:3001; use your GATEWAY value if you changed it):

Create `~/.config/goose/custom_providers/freellmapi.json`:

```json
{
  "name": "freellmapi",
  "engine": "openai",
  "display_name": "FreeLLMAPI",
  "description": "FreeLLMAPI OpenAI-compatible gateway",
  "api_key_env": "FREELLMAPI_API_KEY",
  "base_url": "http://freellmapi:3001/v1",
  "models": [{ "name": "auto", "context_limit": 128000 }],
  "supports_streaming": true,
  "requires_auth": true,
  "dynamic_models": false,
  "preserves_thinking": true
}
```

Add to `~/.config/goose/config.yaml` (keep existing keys):

```yaml
GOOSE_PROVIDER: freellmapi
GOOSE_MODEL: "auto"
```

   Expected result: a new file ~/.config/goose/custom_providers/freellmapi.json and a marked block in ~/.config/goose/config.yaml setting GOOSE_PROVIDER: freellmapi and GOOSE_MODEL: auto.

   Optional shortcut: if Node.js >= 20.18 and < 25 with npx is ALREADY installed on this machine, the official FreeLLMAPI CLI writes the same entries. Export `FREELLMAPI_URL=$GATEWAY`, run `npx --yes freellmapi setup-goose --model auto --dry-run`, show me the diff, apply only if it matches the expected result above, then run it again without --dry-run. Do not install Node.js for this; the direct way works without it.
4. Verify. The provider file names the key variable api_key_env: FREELLMAPI_API_KEY and does not contain the key.
5. Test. FREELLMAPI_API_KEY is exported, then try a one-shot run: goose run -t "Say hello" (best effort: check `--help` for the exact one-shot syntax)
6. Follow-up. Tell me to export FREELLMAPI_API_KEY before starting Goose. Do not write the key into any shell profile yourself.

Final report: list the files you changed, what the test returned, and exactly what I type or run to use FreeLLMAPI with model "auto". Expected selector: the freellmapi provider with model auto (set as default).
````

Prompts are derived from the FreeLLMAPI CLI 0.8.2 source and the upstream documentation. They have not been run against every agent; the expected-result check in step 3 and the test in step 5 are the safety net.
