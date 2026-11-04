# Any OpenAI-compatible client with FreeLLMAPI

[← All clients](../README.md) · Upstream notes: [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md)

For LangChain, LlamaIndex, the official OpenAI SDKs, Open WebUI and every client that accepts a custom OpenAI base URL. No setup command is needed.

| Setting | Value |
| --- | --- |
| Base URL | `http://freellmapi:3001/v1` |
| API key | the unified key from the FreeLLMAPI dashboard (Keys page), starts with `freellmapi-` |
| Model | `auto` (the router picks per request), or an id from `GET /v1/models` |

Quick check from any shell that can reach the gateway:

```bash
curl -sS http://freellmapi:3001/v1/chat/completions \
  -H "Authorization: Bearer $FREELLMAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Say hello"}]}'
```

Python:

```python
import os
from openai import OpenAI
client = OpenAI(base_url="http://freellmapi:3001/v1", api_key=os.environ["FREELLMAPI_API_KEY"])
print(client.chat.completions.create(model="auto", messages=[{"role": "user", "content": "Say hello"}]).choices[0].message.content)
```

The CLI can print the same block for your URL: `npx --yes freellmapi setup-generic --url http://freellmapi:3001`.

## Prompt

````text
Configure the application or SDK in this project to use FreeLLMAPI as its OpenAI-compatible endpoint.

Parameters (edit before sending):
- GATEWAY: http://freellmapi:3001  (used below as the shell variable $GATEWAY)
- MODEL: auto
- API KEY: expected in the environment variable FREELLMAPI_API_KEY. If it is not set, ask me for the unified key (it starts with "freellmapi-").

Rules:
- Never print the API key and never hard-code it in source files or commit it. Read it from the environment variable.
- Do not change anything unrelated to the LLM client configuration.

Steps:
1. Run `export GATEWAY=<the GATEWAY value above>`, then `curl -sS $GATEWAY/api/ping`. If it fails, stop and tell me. Do not guess another address.
2. Run `curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" $GATEWAY/v1/models` and confirm that the id "auto" is listed.
3. Find where this project creates its OpenAI-compatible client and set base URL to $GATEWAY/v1, API key from FREELLMAPI_API_KEY and model to auto. Show me the diff before you apply it.
4. Run the project's smallest existing test or a one-line script that sends "Say hello" and show me the reply.

Final report: files changed, test result, and which environment variables the project now expects.
````
