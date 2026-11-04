# Reasonix with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://github.com/esengine/DeepSeek-Reasonix/blob/studio/docs/CLI.md#configure-providers> · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

|  |  |
| --- | --- |
| Optional CLI shortcut | `npx --yes freellmapi setup-reasonix` (writes the same entries; not required) |
| Wire | OpenAI Chat Completions (kind = "openai"), base URL with /v1 |
| Base URL form | `/v1` URL |
| Profile support | yes (`--profile local` leaves the default model alone) |
| API key | kept out of the config files (environment variable or separate `.env`) |


## Prompt

Copy this into Reasonix (or any coding agent) on the machine where Reasonix runs. FreeLLMAPI is configured like any other OpenAI-compatible endpoint, so **nothing has to be installed for it** on that machine. Edit the three parameters at the top first. The default gateway address assumes the agent runs in a container on the same custom Docker network as FreeLLMAPI; see [choosing the gateway address](../README.md#choosing-the-gateway-address) for the other cases.

````text
Add FreeLLMAPI as an additional model provider for Reasonix on this machine, without changing my default model. Afterwards I want to use the model "auto" through FreeLLMAPI.

Parameters (edit before sending):
- GATEWAY: http://freellmapi:3001  (used below as the shell variable $GATEWAY)
- PROFILE: local
- MODEL: auto
- API KEY: expected in the environment variable FREELLMAPI_API_KEY. If it is not set, ask me for the unified key (it starts with "freellmapi-").

Rules:
- FreeLLMAPI is an ordinary OpenAI-compatible endpoint, configured like any other provider such as Ollama. Nothing has to be installed for it on this machine. Do not install packages and do not change PATH.
- Never print the API key, never put it in a command line argument, never write it anywhere except where this task says the configuration stores it. Do not echo it in your replies or in logs.
- Only touch files that belong to Reasonix. Do not change anything else on this machine.
- Before you change an existing config file, make a timestamped backup copy and keep its permissions.
- If anything looks wrong, stop and show me the exact error without the key.
- Run all commands in one shell session so exported variables carry over.

Steps:
1. Reachability. Run `export GATEWAY=<the GATEWAY value above>`, then `curl -sS $GATEWAY/api/ping`. If the host name does not resolve or the connection fails, stop and tell me. This machine is then probably not on the same Docker network as FreeLLMAPI. Do not guess another address.
2. Catalog. Run `curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" $GATEWAY/v1/models` and confirm that a model with id "auto" is listed. A 401 means the key is wrong.
3. Configure. Add FreeLLMAPI in the agent's own provider settings as an OpenAI-compatible provider: base URL $GATEWAY/v1, API key from FREELLMAPI_API_KEY, model auto. Agent documentation: https://github.com/esengine/DeepSeek-Reasonix/blob/studio/docs/CLI.md#configure-providers
   Expected result: ~/.reasonix/config.toml gains a [[providers]] entry named freellmapi-local, and ~/.reasonix/.env gets FREELLMAPI_API_KEY=... The default_model must not change.
   If editing the settings by hand is impractical, use the optional shortcut. Optional shortcut: if Node.js >= 20.18 and < 25 with npx is ALREADY installed on this machine, the official FreeLLMAPI CLI writes the same entries. Export `FREELLMAPI_URL=$GATEWAY`, run `npx --yes freellmapi setup-reasonix --profile local --model auto --dry-run`, show me the diff, apply only if it matches the expected result above, then run it again without --dry-run. Do not install Node.js for this; the direct way works without it.
4. Verify. config.toml names the variable api_key_env = "FREELLMAPI_API_KEY". ~/.reasonix/.env is mode 0600.
5. Test. reasonix --model freellmapi-local/auto -p "Say hello"
6. Follow-up. Reasonix Studio only lists providers in [desktop].provider_access when that list is set. Tell me if it is and ask before adding "freellmapi-local" to it.

Final report: list the files you changed, what the test returned, and exactly what I type or run to use FreeLLMAPI with model "auto". Expected selector: reasonix --model freellmapi-local/auto.
````

Prompts are derived from the FreeLLMAPI CLI 0.8.2 source and the upstream documentation. They have not been run against every agent; the expected-result check in step 3 and the test in step 5 are the safety net.
