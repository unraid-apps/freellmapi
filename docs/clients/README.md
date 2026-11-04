# Connecting agents and apps to FreeLLMAPI

Ready-to-paste prompts that let a coding agent configure itself for your FreeLLMAPI container. Each prompt checks that the gateway is reachable, adds the provider entry, verifies it and runs a test request. They were written for the Unraid setup in this repository but work for any FreeLLMAPI gateway.

## How it works

FreeLLMAPI is an ordinary OpenAI-compatible endpoint. An agent needs three things, the same as for a local Ollama: a base URL, an API key and a model name. **Nothing has to be installed for FreeLLMAPI on the agent's machine.** All routing, failover and key handling happens in the FreeLLMAPI container.

The prompts here tell a coding agent to add that provider entry to its own configuration, check that the gateway answers, and run a test request. For agents with a simple config format the prompt contains the exact entry. For the others it points at the agent's own provider settings.

FreeLLMAPI also publishes a small command line tool, the npm package `freellmapi`, that writes the same entries for about twenty agents. It is an optional shortcut: it reads your live model catalog, makes a timestamped backup of the existing config and merges its entries in. Every prompt mentions it as an alternative, usable only if Node.js 20.18 to 24 with `npx` is already present. It is never required and the prompts forbid installing Node.js for it.

What the agent's machine does need:

- A route to the gateway, see below.
- The unified API key from the FreeLLMAPI dashboard (Keys page), preferably exported as `FREELLMAPI_API_KEY`.

## Choosing the gateway address

Every prompt has a `GATEWAY` parameter. Pick the row that matches where the agent runs:

| The agent runs ... | GATEWAY | Notes |
| --- | --- | --- |
| in a container on the same custom Docker network as FreeLLMAPI | `http://freellmapi:3001` | Docker's embedded DNS resolves container names and network aliases; `--hostname` is not documented as resolvable. Add `--network-alias=freellmapi` to the Extra Parameters of the FreeLLMAPI container to be safe. Container port 3001, no published port needed, no TLS. |
| on another machine in your LAN | `http://<unraid-ip>:3001` | Or the Unraid server name if your network resolves it. |
| anywhere in your tailnet | `https://freellmapi.<tailnet>.ts.net` | Needs "Use Tailscale" enabled in the container (the template pre-fills it, mode Serve). Valid certificate, no port. |
| in Cursor | not possible | See the Cursor page. |

Do not expose the gateway to the public internet. It is a single-user application guarded only by its API key.

## Agents

| Agent | Setup command | Profile (keeps your default model) | Base URL form |
| --- | --- | --- | --- |
| [Claude Code](prompts/claude-code.md) | `setup-claude` | yes | server root |
| [Codex CLI](prompts/codex.md) | `setup-codex` | yes | `/v1` |
| [Hermes Agent](prompts/hermes.md) | `setup-hermes` | yes | `/v1` |
| [OpenClaw](prompts/openclaw.md) | `setup-openclaw` | yes | `/v1` |
| [OpenCode](prompts/opencode.md) | `setup-opencode` | no | `/v1` |
| [Goose](prompts/goose.md) | `setup-goose` | no | `/v1` |
| [Aider](prompts/aider.md) | `setup-aider` | no | `/v1` |
| [Cline](prompts/cline.md) | `setup-cline` | no | `/v1` |
| [Continue](prompts/continue.md) | `setup-continue` | no | `/v1` |
| [Qwen Code](prompts/qwen-code.md) | `setup-qwen` | no | `/v1` |
| [Roo Code](prompts/roo-code.md) | `setup-roo` | no | `/v1` |
| [Kilo Code](prompts/kilo-code.md) | `setup-kilo` | no | `/v1` |
| [Crush](prompts/crush.md) | `setup-crush` | no | `/v1` |
| [Pi](prompts/pi.md) | `setup-pi` | yes | `/v1` |
| [Reasonix](prompts/reasonix.md) | `setup-reasonix` | yes | `/v1` |
| [ZCode](prompts/zcode.md) | `setup-zcode` | yes | `/v1` |
| [DeepSeek Harness (dsh)](prompts/deepseek-harness.md) | `setup-dsh` | yes | `/v1` |
| [MiMo Code](prompts/mimo-code.md) | `setup-mimo` | no | `/v1` |
| [AtomCode](prompts/atomcode.md) | `setup-atomcode` | no | `/v1` |
| [Any OpenAI-compatible client](prompts/generic.md) | `setup-generic` prints a block | n/a | `/v1` |
| [QwenPaw](prompts/qwenpaw.md) | manual, UI steps | n/a | `/v1` |
| [Cursor](prompts/cursor.md) | not possible on a private network | n/a | public HTTPS `/v1` |

"Profile" means the CLI can add FreeLLMAPI as an additional provider under the name `local` instead of replacing your current default. Agents without profile support get FreeLLMAPI as their default provider; the CLI merges rather than overwrites, and the dry-run diff shows exactly what changes.

## Conventions used by every prompt

- Model `auto`: FreeLLMAPI's router picks the best available model per request and fails over on rate limits. A concrete model id from `GET /v1/models` works too.
- Profile name `local`: change it freely. The provider name is `freellmapi-` plus the profile name, so `local` becomes `freellmapi-local`.
- The API key is never passed as a command line argument. The CLI reads `FREELLMAPI_URL` and `FREELLMAPI_API_KEY` from the environment.
- Several agents store the key in their own config file by design (the CLI creates those files with mode 0600). The prompt says so per agent and tells the agent not to print or copy such files.
- The prompt states the expected result per agent. If a change would touch more than that, the agent stops.

## Sources and limits

Derived from the upstream [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md) and the CLI source (version 0.8.2). The prompts have not been executed against every agent. If an agent changes its configuration format, the optional CLI is the authority: run `npx --yes freellmapi list` for the supported agents and `npx --yes freellmapi doctor <agent>` to check that requests actually reach the gateway.

Maintenance: the pages are generated by `tools/gen-client-docs.py docs/clients`. Edit the script, not the pages.
