# Reasonix with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://github.com/esengine/DeepSeek-Reasonix/blob/studio/docs/CLI.md#configure-providers> · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

|  |  |
| --- | --- |
| Setup command | `npx --yes freellmapi setup-reasonix` |
| Wire | OpenAI Chat Completions (kind = "openai"), base URL with /v1 |
| Base URL form | `/v1` URL |
| Profile support | yes (`--profile local` leaves the default model alone) |
| API key | kept out of the config files (environment variable or separate `.env`) |


## Prompt

Copy this into Reasonix (or any coding agent) on the machine where Reasonix runs. Edit the three parameters at the top first. The default gateway address assumes the agent runs in a container on the same custom Docker network as FreeLLMAPI; see [choosing the gateway address](../README.md#choosing-the-gateway-address) for the other cases.

````text
Set up FreeLLMAPI as an additional model provider for Reasonix on this machine, without changing my default model. Afterwards I want to use the model "auto" through FreeLLMAPI.

Parameters (edit before sending):
- GATEWAY: http://freellmapi:3001  (used below as the shell variable $GATEWAY)
- PROFILE: local
- MODEL: auto
- API KEY: expected in the environment variable FREELLMAPI_API_KEY. If it is not set, ask me for the unified key (it starts with "freellmapi-").

Rules:
- Never print the API key, never put it in a command line argument, never write it anywhere except where this task says the configuration stores it. Do not echo it in your replies or in logs.
- Only touch files that belong to Reasonix. Do not change anything else on this machine.
- The CLI makes a timestamped backup before it changes an existing file. If anything looks wrong, stop and show me the exact error without the key.
- Run all commands in one shell session so exported variables carry over.

Steps:
0. Prerequisites. Run `node --version` and `npx --version`. The FreeLLMAPI CLI needs Node.js >= 20.18 and < 25, plus network access to the npm registry. If Node is missing or the wrong version, STOP and tell me what is missing. Do not install system packages or change PATH without asking me. If the CLI cannot be used, configure the agent through its own provider settings instead: OpenAI-compatible provider, base URL $GATEWAY/v1, model auto, API key from FREELLMAPI_API_KEY. See the agent documentation: https://github.com/esengine/DeepSeek-Reasonix/blob/studio/docs/CLI.md#configure-providers
1. Reachability. Run `export GATEWAY=<the GATEWAY value above>`, then `curl -sS $GATEWAY/api/ping`. If the host name does not resolve or the connection fails, stop and tell me. This machine is then probably not on the same Docker network as FreeLLMAPI. Do not guess another address.
2. Catalog. Run `curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" $GATEWAY/v1/models` and confirm that a model with id "auto" is listed. A 401 means the key is wrong.
3. Dry run. Export `FREELLMAPI_URL=$GATEWAY`, then run:
   `npx --yes freellmapi setup-reasonix --profile local --model auto --dry-run`
   Show me the diff.
4. Compare the diff with what I expect: ~/.reasonix/config.toml gains a [[providers]] entry named freellmapi-local, and ~/.reasonix/.env gets FREELLMAPI_API_KEY=... The default_model must not change.
   Apply only if it matches. If it touches anything else, stop and ask me.
5. Apply. Run the same command without --dry-run.
6. Verify. config.toml names the variable api_key_env = "FREELLMAPI_API_KEY". ~/.reasonix/.env is mode 0600.
7. Test. reasonix --model freellmapi-local/auto -p "Say hello"
8. Follow-up. Reasonix Studio only lists providers in [desktop].provider_access when that list is set. Tell me if it is and ask before adding "freellmapi-local" to it.

Final report: list the files you changed, what the test returned, and exactly what I type or run to use FreeLLMAPI with model "auto". Expected selector: reasonix --model freellmapi-local/auto.
````

Prompts are derived from the FreeLLMAPI CLI 0.8.2 source and the upstream documentation. They have not been run against every agent; the dry run in step 3 is the safety net.
