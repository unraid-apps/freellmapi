# Connecting agents and apps to FreeLLMAPI

Ready-to-paste prompts that let a coding agent configure itself for your FreeLLMAPI container. Each prompt installs nothing system-wide, runs the official FreeLLMAPI CLI in dry-run mode first, compares the diff with what is documented, and only then writes. They were written for the Unraid setup in this repository but work for any FreeLLMAPI gateway.

## How it works

FreeLLMAPI publishes a small command line tool, the npm package `freellmapi`, that knows the configuration format of about twenty agents. It reads your live model catalog from the gateway, backs up the agent's existing config with a timestamp, and merges its entries into it. The prompts here wrap that tool with checks and safety rules so you can hand the whole job to the agent you want to configure.

The tool is fetched by `npx` on demand. It is not installed on the Unraid server and not inside the FreeLLMAPI container. It must be runnable **on the machine where the agent runs**, which is why every prompt starts with a prerequisite check.

Requirements on the agent's machine:

- Node.js 20.18 or newer, but older than 25 (the package declares `>=20.18.0 <25.0.0`), with `npx`.
- Outbound access to the npm registry.
- A route to the gateway, see below.
- The unified API key from the FreeLLMAPI dashboard (Keys page), preferably exported as `FREELLMAPI_API_KEY`.

Prompts for agents running in a container need Node.js in that container. If it is missing, the agent stops and tells you instead of installing anything. Where the config format is simple, the prompt carries a manual configuration block for that case.

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
- The dry run comes first, always. If the diff touches more than the documented files, the agent stops.

## Sources and limits

Derived from the upstream [agent clients guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-agent-clients.md) and the CLI source (version 0.8.2). The prompts have not been executed against every agent. If an agent changes its configuration format, the CLI is the authority: run `npx --yes freellmapi list` for the supported agents and `npx --yes freellmapi doctor <agent>` to check that requests actually reach the gateway.

Maintenance: the pages are generated by `tools/gen-client-docs.py docs/clients`. Edit the script, not the pages.
