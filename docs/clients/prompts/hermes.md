# Hermes Agent with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://hermes-agent.nousresearch.com/docs/> · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

|  |  |
| --- | --- |
| Optional CLI shortcut | `npx --yes freellmapi setup-hermes` (writes the same entries; not required) |
| Wire | OpenAI Chat Completions (provider: custom), base URL with /v1 |
| Base URL form | `/v1` URL |
| Profile support | yes (`--profile local` leaves the default model alone) |
| API key | kept out of the config files (environment variable or separate `.env`) |

Hermes ignores OPENAI_BASE_URL for anything except api.openai.com, so the endpoint must be declared in config.yaml, exactly like a local Ollama endpoint would be. Per the upstream CLI notes, the `hermes setup` wizard writes the same kind of block for a custom endpoint. The profile route leaves the default model alone; to make FreeLLMAPI the default instead, drop `--profile local` (the CLI then replaces the top-level `model` block with provider: custom).

## Prompt

Copy this into Hermes Agent (or any coding agent) on the machine where Hermes Agent runs. FreeLLMAPI is configured like any other OpenAI-compatible endpoint, so **nothing has to be installed for it** on that machine. Edit the three parameters at the top first. The default gateway address assumes the agent runs in a container on the same custom Docker network as FreeLLMAPI; see [choosing the gateway address](../README.md#choosing-the-gateway-address) for the other cases.

````text
Add FreeLLMAPI as an additional model provider for Hermes Agent on this machine, without changing my default model. Afterwards I want to use the model "auto" through FreeLLMAPI.

Parameters (edit before sending):
- GATEWAY: http://freellmapi:3001  (used below as the shell variable $GATEWAY)
- PROFILE: local
- MODEL: auto
- API KEY: expected in the environment variable FREELLMAPI_API_KEY. If it is not set, ask me for the unified key (it starts with "freellmapi-").

Rules:
- FreeLLMAPI is an ordinary OpenAI-compatible endpoint, configured like any other provider such as Ollama. Nothing has to be installed for it on this machine. Do not install packages and do not change PATH.
- Never print the API key, never put it in a command line argument, never write it anywhere except where this task says the configuration stores it. Do not echo it in your replies or in logs.
- Only touch files that belong to Hermes Agent. Do not change anything else on this machine.
- Before you change an existing config file, make a timestamped backup copy and keep its permissions.
- If anything looks wrong, stop and show me the exact error without the key.
- Run all commands in one shell session so exported variables carry over.

Steps:
1. Reachability. Run `export GATEWAY=<the GATEWAY value above>`, then `curl -sS $GATEWAY/api/ping`. If the host name does not resolve or the connection fails, stop and tell me. This machine is then probably not on the same Docker network as FreeLLMAPI. Do not guess another address.
2. Catalog. Run `curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" $GATEWAY/v1/models` and confirm that a model with id "auto" is listed. A 401 means the key is wrong.
3. Configure. Add the provider entry directly. Add exactly this and change nothing else (the examples use http://freellmapi:3001; use your GATEWAY value if you changed it):

Edit `$HERMES_HOME/config.yaml` (default `~/.hermes/config.yaml`). Add this entry under the top-level `providers` key, creating the key if it is missing, and change nothing else:

```yaml
providers:
  freellmapi-local:
    name: "FreeLLMAPI (local)"
    api: "http://freellmapi:3001/v1"
    api_key: "${FREELLMAPI_API_KEY}"
    transport: chat_completions
    default_model: auto
    context_length: 128000
    extra_headers:
      User-Agent: hermes-agent
```

Add `FREELLMAPI_API_KEY=<value of FREELLMAPI_API_KEY>` to `$HERMES_HOME/.env` (mode 0600). Hermes loads that file itself.

   Expected result: in $HERMES_HOME/config.yaml (default ~/.hermes/config.yaml) a new entry providers.freellmapi-local, and in $HERMES_HOME/.env the line FREELLMAPI_API_KEY=... The existing top-level `model` block must not change.

   Optional shortcut: if Node.js >= 20.18 and < 25 with npx is ALREADY installed on this machine, the official FreeLLMAPI CLI writes the same entries. Export `FREELLMAPI_URL=$GATEWAY`, run `npx --yes freellmapi setup-hermes --profile local --model auto --dry-run`, show me the diff, apply only if it matches the expected result above, then run it again without --dry-run. Do not install Node.js for this; the direct way works without it.
4. Verify. config.yaml references the key only as ${FREELLMAPI_API_KEY}, never in plain text. .env is mode 0600.
5. Test. Upstream documents `hermes -z` only for the default model. To test without switching models, call the gateway directly: curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" -H "Content-Type: application/json" -d '{"model":"auto","messages":[{"role":"user","content":"Say hello"}]}' $GATEWAY/v1/chat/completions
6. Follow-up. If a `hermes gateway` (Telegram, Discord and so on) is running, restart it so it reloads config.yaml. Then tell me to type /model custom:freellmapi-local:auto in a chat.

Final report: list the files you changed, what the test returned, and exactly what I type or run to use FreeLLMAPI with model "auto". Expected selector: /model custom:freellmapi-local:auto.
````

Prompts are derived from the FreeLLMAPI CLI 0.8.2 source and the upstream documentation. They have not been run against every agent; the expected-result check in step 3 and the test in step 5 are the safety net.
