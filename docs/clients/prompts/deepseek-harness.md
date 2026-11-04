# DeepSeek Harness (dsh) with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://github.com/deepseek-ai/deepseek-harness> · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

|  |  |
| --- | --- |
| Optional CLI shortcut | `npx --yes freellmapi setup-dsh` (writes the same entries; not required) |
| Wire | OpenAI Chat Completions (api: openai-completions), base URL with /v1 |
| Base URL form | `/v1` URL |
| Profile support | yes (`--profile local` leaves the default model alone) |
| API key | kept out of the config files (environment variable or separate `.env`) |


## Prompt

Copy this into DeepSeek Harness (dsh) (or any coding agent) on the machine where DeepSeek Harness (dsh) runs. FreeLLMAPI is configured like any other OpenAI-compatible endpoint, so **nothing has to be installed for it** on that machine. Edit the three parameters at the top first. The default gateway address assumes the agent runs in a container on the same custom Docker network as FreeLLMAPI; see [choosing the gateway address](../README.md#choosing-the-gateway-address) for the other cases.

````text
Add FreeLLMAPI as an additional model provider for DeepSeek Harness (dsh) on this machine, without changing my default model. Afterwards I want to use the model "auto" through FreeLLMAPI.

Parameters (edit before sending):
- GATEWAY: http://freellmapi:3001  (used below as the shell variable $GATEWAY)
- PROFILE: local
- MODEL: auto
- API KEY: expected in the environment variable FREELLMAPI_API_KEY. If it is not set, ask me for the unified key (it starts with "freellmapi-").

Rules:
- FreeLLMAPI is an ordinary OpenAI-compatible endpoint, configured like any other provider such as Ollama. Nothing has to be installed for it on this machine. Do not install packages and do not change PATH.
- Never print the API key, never put it in a command line argument, never write it anywhere except where this task says the configuration stores it. Do not echo it in your replies or in logs.
- Only touch files that belong to DeepSeek Harness (dsh). Do not change anything else on this machine.
- Before you change an existing config file, make a timestamped backup copy and keep its permissions.
- If anything looks wrong, stop and show me the exact error without the key.
- Run all commands in one shell session so exported variables carry over.

Steps:
1. Reachability. Run `export GATEWAY=<the GATEWAY value above>`, then `curl -sS $GATEWAY/api/ping`. If the host name does not resolve or the connection fails, stop and tell me. This machine is then probably not on the same Docker network as FreeLLMAPI. Do not guess another address.
2. Catalog. Run `curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" $GATEWAY/v1/models` and confirm that a model with id "auto" is listed. A 401 means the key is wrong.
3. Configure. Add FreeLLMAPI in the agent's own provider settings as an OpenAI-compatible provider: base URL $GATEWAY/v1, API key from FREELLMAPI_API_KEY, model auto. Agent documentation: https://github.com/deepseek-ai/deepseek-harness
   Expected result: $DSH_HOME/settings.yaml (default ~/.dsh/settings.yaml) gains a route freellmapi-local under llm-pi-ai.providers, and $DSH_HOME/.env gets FREELLMAPI_API_KEY=... The default model must not change.
   If editing the settings by hand is impractical, use the optional shortcut. Optional shortcut: if Node.js >= 20.18 and < 25 with npx is ALREADY installed on this machine, the official FreeLLMAPI CLI writes the same entries. Export `FREELLMAPI_URL=$GATEWAY`, run `npx --yes freellmapi setup-dsh --profile local --model auto --dry-run`, show me the diff, apply only if it matches the expected result above, then run it again without --dry-run. Do not install Node.js for this; the direct way works without it.
4. Verify. The route names the variable by apiKeyEnv. $DSH_HOME/.env is mode 0600.
5. Test. npx @deepseek-ai/dsh web, then pick the route.
6. Follow-up. Settings are hot-reloaded; no restart is needed.

Final report: list the files you changed, what the test returned, and exactly what I type or run to use FreeLLMAPI with model "auto". Expected selector: the route freellmapi-local (relay the selector the CLI prints in its notes).
````

Prompts are derived from the FreeLLMAPI CLI 0.8.2 source and the upstream documentation. They have not been run against every agent; the expected-result check in step 3 and the test in step 5 are the safety net.
