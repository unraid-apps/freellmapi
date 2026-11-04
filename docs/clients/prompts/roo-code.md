# Roo Code with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://docs.roocode.com> · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

|  |  |
| --- | --- |
| Optional CLI shortcut | `npx --yes freellmapi setup-roo` (writes the same entries; not required) |
| Wire | OpenAI Chat Completions (OpenAI Compatible profile in VS Code; an OpenRouter-type profile for the Roo CLI), base URL with /v1 |
| Base URL form | `/v1` URL |
| Profile support | no (the command makes FreeLLMAPI the default and merges into the existing config) |
| API key | stored in a config file by design |


## Prompt

Copy this into Roo Code (or any coding agent) on the machine where Roo Code runs. FreeLLMAPI is configured like any other OpenAI-compatible endpoint, so **nothing has to be installed for it** on that machine. Edit the three parameters at the top first. The default gateway address assumes the agent runs in a container on the same custom Docker network as FreeLLMAPI; see [choosing the gateway address](../README.md#choosing-the-gateway-address) for the other cases.

````text
Add FreeLLMAPI as a model provider for Roo Code on this machine, using the model "auto". Keep my other providers and settings.

Parameters (edit before sending):
- GATEWAY: http://freellmapi:3001  (used below as the shell variable $GATEWAY)
- PROFILE: (not used: this agent has no profile concept)
- MODEL: auto
- API KEY: expected in the environment variable FREELLMAPI_API_KEY. If it is not set, ask me for the unified key (it starts with "freellmapi-").

Rules:
- FreeLLMAPI is an ordinary OpenAI-compatible endpoint, configured like any other provider such as Ollama. Nothing has to be installed for it on this machine. Do not install packages and do not change PATH.
- Never print the API key, never put it in a command line argument, never write it anywhere except where this task says the configuration stores it. Do not echo it in your replies or in logs.
- Only touch files that belong to Roo Code. Do not change anything else on this machine.
- Before you change an existing config file, make a timestamped backup copy and keep its permissions.
- If anything looks wrong, stop and show me the exact error without the key.
- Run all commands in one shell session so exported variables carry over.

Steps:
1. Reachability. Run `export GATEWAY=<the GATEWAY value above>`, then `curl -sS $GATEWAY/api/ping`. If the host name does not resolve or the connection fails, stop and tell me. This machine is then probably not on the same Docker network as FreeLLMAPI. Do not guess another address.
2. Catalog. Run `curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" $GATEWAY/v1/models` and confirm that a model with id "auto" is listed. A 401 means the key is wrong.
3. Configure. Add FreeLLMAPI in the agent's own provider settings as an OpenAI-compatible provider: base URL $GATEWAY/v1, API key from FREELLMAPI_API_KEY, model auto. Agent documentation: https://docs.roocode.com
   Expected result: three files under ~/.roo/: freellmapi.json, freellmapi-cli.json and cli-settings.json. Nothing else changes until the user wires the import path.
   If editing the settings by hand is impractical, use the optional shortcut. Optional shortcut: if Node.js >= 20.18 and < 25 with npx is ALREADY installed on this machine, the official FreeLLMAPI CLI writes the same entries. Export `FREELLMAPI_URL=$GATEWAY`, run `npx --yes freellmapi setup-roo --model auto --dry-run`, show me the diff, apply only if it matches the expected result above, then run it again without --dry-run. Do not install Node.js for this; the direct way works without it.
4. Verify. The first two files contain the key by design and should not be printed or copied.
5. Test. Follow the notes the CLI prints; they contain the exact VS Code setting (roo-cline.autoImportSettingsPath) and the CLI steps. Relay them to me verbatim.
6. Follow-up. The CLI notes list manual follow-up steps (a VS Code setting, and for the Roo CLI a global-state.json merge plus OPENROUTER_API_KEY). Do not perform those without asking me.

Final report: list the files you changed, what the test returned, and exactly what I type or run to use FreeLLMAPI with model "auto". Expected selector: the freellmapi profile (VS Code) or `roo -m auto` (CLI).
````

Prompts are derived from the FreeLLMAPI CLI 0.8.2 source and the upstream documentation. They have not been run against every agent; the expected-result check in step 3 and the test in step 5 are the safety net.
