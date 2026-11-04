#!/usr/bin/env python3
"""Generate docs/clients/** for unraid-apps/freellmapi.

Usage: python3 tools/gen-client-docs.py docs/clients
The pages are generated; edit the per-agent data in this script, not the pages.

Facts come from upstream docs/en/clients/*.md and cli/src/tools.ts (CLI 0.8.2).
Nothing here was executed against a live gateway; every prompt tells the agent
to start with --dry-run and compare the diff with what is documented.
"""
from __future__ import annotations

import os
import sys

OUT = sys.argv[1]
PROMPTS = os.path.join(OUT, "prompts")
os.makedirs(PROMPTS, exist_ok=True)

BASE = "http://freellmapi:3001"
UP = "https://github.com/tashfeenahmed/freellmapi"
UPDOCS = UP + "/blob/main/docs/en/clients/01-agent-clients.md"

# ---------------------------------------------------------------------------
# Per-agent data. Keys:
#   name, cmd, docs, profile(bool), root(bool: server root instead of /v1),
#   goal, expect, verify, test, after, select, fallback (markdown or None),
#   key_in_file (bool: CLI stores the key in a config file by design)
# ---------------------------------------------------------------------------
A: dict[str, dict] = {}

A["claude-code"] = dict(
    name="Claude Code", cmd="setup-claude", docs="https://docs.anthropic.com/en/docs/claude-code",
    profile=True, root=True, key_in_file=True,
    wire="Anthropic Messages (the agent appends its own path, so the base URL is the server root WITHOUT /v1)",
    select="CLAUDE_CONFIG_DIR=~/.claude/profiles/local claude",
    expect="one new file ~/.claude/profiles/local/settings.json with an env block (ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_MODEL and the three ANTHROPIC_DEFAULT_*_MODEL variables, all set to auto). ~/.claude/settings.json must not change.",
    verify="The file is mode 0600. The gateway URL in it has no /v1 suffix. The key is stored in this file by design; do not copy the file anywhere or print it.",
    test='CLAUDE_CONFIG_DIR=~/.claude/profiles/local claude -p "Say hello" (best effort: check `--help` for the exact one-shot syntax)',
    after="Nothing to restart. Tell me to start it with CLAUDE_CONFIG_DIR=~/.claude/profiles/local claude. For a variant that never writes the key to disk, mention `npx --yes freellmapi launch`.",
    fallback='''Write `~/.claude/profiles/local/settings.json` (create the directory, mode 0600). If the file exists, merge the `env` keys and keep everything else:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://freellmapi:3001",
    "ANTHROPIC_AUTH_TOKEN": "<unified key>",
    "ANTHROPIC_MODEL": "auto",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "auto",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "auto",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "auto",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "128000",
    "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY": "1"
  }
}
```''',
    extra="Claude Code speaks the Anthropic Messages API. FreeLLMAPI serves it at the server root, so never add /v1 to the Claude Code base URL.",
)

A["codex"] = dict(
    name="Codex CLI", cmd="setup-codex", docs="https://developers.openai.com/codex",
    profile=True, root=False, key_in_file=False,
    wire="OpenAI Responses (wire_api = \"responses\"), base URL with /v1",
    select="codex --profile local",
    expect="a marked block (# freellmapi:start ... # freellmapi:end) appended to ~/.codex/config.toml containing [model_providers.freellmapi] and a [profiles.local] table. Top-level model settings must not change.",
    verify="The key is NOT written to config.toml; the provider reads it from the environment variable FREELLMAPI_API_KEY (env_key).",
    test='FREELLMAPI_API_KEY is exported, then try a one-shot run: codex exec --profile local "Say hello" (best effort: check `--help` for the exact one-shot syntax)',
    after="Tell me to export FREELLMAPI_API_KEY in my shell profile so codex sees it, and to start with codex --profile local. Do not write the key into any shell profile yourself.",
    fallback='''Append to `~/.codex/config.toml` (keep existing content):

```toml
[model_providers.freellmapi]
name = "FreeLLMAPI"
base_url = "http://freellmapi:3001/v1"
wire_api = "responses"
env_key = "FREELLMAPI_API_KEY"
requires_openai_auth = false

[profiles.local]
model = "auto"
model_provider = "freellmapi"
```

Then export `FREELLMAPI_API_KEY` and run `codex --profile local`.''',
)

A["hermes"] = dict(
    name="Hermes Agent", cmd="setup-hermes", docs="https://hermes-agent.nousresearch.com/docs/",
    profile=True, root=False, key_in_file=False,
    wire="OpenAI Chat Completions (provider: custom), base URL with /v1",
    select="/model custom:freellmapi-local:auto",
    expect="in $HERMES_HOME/config.yaml (default ~/.hermes/config.yaml) a new entry providers.freellmapi-local, and in $HERMES_HOME/.env the line FREELLMAPI_API_KEY=... The existing top-level `model` block must not change.",
    verify="config.yaml references the key only as ${FREELLMAPI_API_KEY}, never in plain text. .env is mode 0600.",
    test="Upstream documents `hermes -z` only for the default model. To test without switching models, call the gateway directly: curl -sS -H \"Authorization: Bearer $FREELLMAPI_API_KEY\" -H \"Content-Type: application/json\" -d '{\"model\":\"auto\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello\"}]}' $GATEWAY/v1/chat/completions",
    after="If a `hermes gateway` (Telegram, Discord and so on) is running, restart it so it reloads config.yaml. Then tell me to type /model custom:freellmapi-local:auto in a chat.",
    fallback='''Edit `$HERMES_HOME/config.yaml` (default `~/.hermes/config.yaml`). Add this entry under the top-level `providers` key, creating the key if it is missing, and change nothing else:

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

Add `FREELLMAPI_API_KEY=<unified key>` to `$HERMES_HOME/.env` (mode 0600). Hermes loads that file itself.''',
    extra="Hermes ignores OPENAI_BASE_URL for anything except api.openai.com, so the endpoint must be declared in config.yaml, exactly like a local Ollama endpoint would be. Per the upstream CLI notes, the `hermes setup` wizard writes the same kind of block for a custom endpoint. The profile route leaves the default model alone; to make FreeLLMAPI the default instead, drop `--profile local` (the CLI then replaces the top-level `model` block with provider: custom).",
)

A["openclaw"] = dict(
    name="OpenClaw", cmd="setup-openclaw", docs="https://docs.openclaw.ai/gateway/config-tools/custom-providers",
    profile=True, root=False, key_in_file=False,
    wire="OpenAI Chat Completions (api: openai-completions), base URL with /v1",
    select="the model id freellmapi-local/auto (relay the selector the CLI prints in its notes)",
    expect="in ~/.openclaw/openclaw.json a new provider freellmapi-local under models.providers, and in ~/.openclaw/.env the line FREELLMAPI_API_KEY=... The default model (agents.defaults.model.primary) must not change.",
    verify="openclaw.json references the key as ${FREELLMAPI_API_KEY}. ~/.openclaw/.env is mode 0600.",
    test='openclaw agent exec --model freellmapi-local/auto "Say hello"',
    after="A running `openclaw gateway` needs a restart to pick the change up.",
    fallback=None,
)

A["opencode"] = dict(
    name="OpenCode", cmd="setup-opencode", docs="https://opencode.ai/docs",
    profile=False, root=False, key_in_file=False,
    wire="OpenAI Chat Completions via @ai-sdk/openai-compatible, base URL with /v1",
    select="freellmapi/auto (set as the default model)",
    expect="~/.config/opencode/opencode.json gains a provider.freellmapi entry (npm @ai-sdk/openai-compatible, baseURL, models) and a top-level model = freellmapi/auto. Other providers stay.",
    verify="The key is referenced as {env:FREELLMAPI_API_KEY}, not written to the file.",
    test='FREELLMAPI_API_KEY is exported, then try a one-shot run: opencode run "Say hello" (best effort: check `--help` for the exact one-shot syntax)',
    after="Tell me to export FREELLMAPI_API_KEY in my shell profile before starting OpenCode. Do not write the key into any shell profile yourself.",
    fallback='''Merge into `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "freellmapi/auto",
  "provider": {
    "freellmapi": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "FreeLLMAPI",
      "options": {
        "baseURL": "http://freellmapi:3001/v1",
        "apiKey": "{env:FREELLMAPI_API_KEY}"
      },
      "models": {
        "auto": { "name": "Auto", "limit": { "context": 128000, "output": 8192 } }
      }
    }
  }
}
```''',
)

A["goose"] = dict(
    name="Goose", cmd="setup-goose", docs="https://block.github.io/goose",
    profile=False, root=False, key_in_file=False,
    wire="OpenAI Chat Completions, base URL with /v1",
    select="the freellmapi provider with model auto (set as default)",
    expect="a new file ~/.config/goose/custom_providers/freellmapi.json and a marked block in ~/.config/goose/config.yaml setting GOOSE_PROVIDER: freellmapi and GOOSE_MODEL: auto.",
    verify="The provider file names the key variable api_key_env: FREELLMAPI_API_KEY and does not contain the key.",
    test='FREELLMAPI_API_KEY is exported, then try a one-shot run: goose run -t "Say hello" (best effort: check `--help` for the exact one-shot syntax)',
    after="Tell me to export FREELLMAPI_API_KEY before starting Goose. Do not write the key into any shell profile yourself.",
    fallback='''Create `~/.config/goose/custom_providers/freellmapi.json`:

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
```''',
)

A["aider"] = dict(
    name="Aider", cmd="setup-aider", docs="https://aider.chat/docs",
    profile=False, root=False, key_in_file=True,
    wire="OpenAI Chat Completions, base URL with /v1, model prefixed with openai/",
    select="openai/auto (set as the default model)",
    expect="a marked block in ~/.aider.conf.yml with openai-api-base, openai-api-key and model: openai/auto.",
    verify="The key is stored in ~/.aider.conf.yml by design; the file should be mode 0600 and must not be printed.",
    test='aider --message "Say hello" --no-git (best effort: check `--help` for the exact one-shot syntax)',
    after="Nothing to restart. As a key-free alternative mention: OPENAI_API_BASE=$GATEWAY/v1 OPENAI_API_KEY=... aider --model openai/auto",
    fallback='''Add to `~/.aider.conf.yml`:

```yaml
openai-api-base: "http://freellmapi:3001/v1"
openai-api-key: "<unified key>"
model: "openai/auto"
```

Key-free alternative: `OPENAI_API_BASE=http://freellmapi:3001/v1 OPENAI_API_KEY=<unified key> aider --model openai/auto`.''',
)

A["cline"] = dict(
    name="Cline", cmd="setup-cline", docs="https://docs.cline.bot",
    profile=False, root=False, key_in_file=True,
    wire="OpenAI Chat Completions (OpenAI Compatible provider), base URL with /v1",
    select="the generated OpenAI Compatible provider with model auto",
    expect="~/.cline/data/settings/providers.json gains an openai-compatible provider (baseUrl, model auto, apiKey, contextWindow) and lastUsedProvider = openai-compatible.",
    verify="The key is stored in providers.json by design; the file should not be printed or copied.",
    test="Open Cline and send a short message; the CLI says Cline uses the provider immediately.",
    after="Nothing to restart according to the CLI notes. Tell me to reload the VS Code window if Cline still shows its old provider.",
    fallback=None,
)

A["continue"] = dict(
    name="Continue", cmd="setup-continue", docs="https://docs.continue.dev",
    profile=False, root=False, key_in_file=False,
    wire="OpenAI Chat Completions, base URL with /v1",
    select="the model named FreeLLMAPI",
    expect="a marked block in ~/.continue/config.yaml defining a model FreeLLMAPI (provider openai, model auto, apiBase, apiKey: ${{ secrets.FREELLMAPI_API_KEY }}) and the line FREELLMAPI_API_KEY=... in ~/.continue/.env.",
    verify="config.yaml references the key only as a secret. ~/.continue/.env is mode 0600.",
    test='cn -p "Say hello" (needs npm install -g @continuedev/cli)',
    after="Reload the editor window so the extension rereads the config.",
    fallback='''Add to `~/.continue/config.yaml` (merge into the existing `models:` list):

```yaml
models:
  - name: FreeLLMAPI
    provider: openai
    model: "auto"
    apiBase: "http://freellmapi:3001/v1"
    apiKey: ${{ secrets.FREELLMAPI_API_KEY }}
    capabilities:
      - tool_use
    defaultCompletionOptions:
      contextLength: 128000
```

Put `FREELLMAPI_API_KEY=<unified key>` into `~/.continue/.env` (mode 0600).

Optional ghost-text autocomplete model:

```yaml
  - name: FreeLLMAPI Autocomplete
    provider: openai
    model: auto
    apiBase: "http://freellmapi:3001/v1"
    apiKey: ${{ secrets.FREELLMAPI_API_KEY }}
    useLegacyCompletionsEndpoint: true
    roles:
      - autocomplete
```''',
)

A["qwen-code"] = dict(
    name="Qwen Code", cmd="setup-qwen", docs="https://qwenlm.github.io/qwen-code-docs",
    profile=False, root=False, key_in_file=False,
    wire="OpenAI Chat Completions, base URL with /v1 (native Gemini wire also available)",
    select="auto (set as the default model)",
    expect="~/.qwen/settings.json gains model.name = auto, modelProviders.openai.models and security.auth.selectedType = openai; ~/.qwen/.env gets FREELLMAPI_API_KEY=...",
    verify="settings.json names the variable envKey: FREELLMAPI_API_KEY; ~/.qwen/.env is mode 0600.",
    test='qwen -p "Say hello" (best effort: check `--help` for the exact one-shot syntax)',
    after="Restart Qwen Code.",
    fallback='''Merge into `~/.qwen/settings.json`:

```json
{
  "model": { "name": "auto" },
  "modelProviders": {
    "openai": {
      "protocol": "openai",
      "models": [
        {
          "id": "auto",
          "name": "Auto",
          "envKey": "FREELLMAPI_API_KEY",
          "baseUrl": "http://freellmapi:3001/v1",
          "generationConfig": { "contextWindowSize": 128000 }
        }
      ]
    }
  },
  "security": { "auth": { "selectedType": "openai" } }
}
```

Put `FREELLMAPI_API_KEY=<unified key>` into `~/.qwen/.env` (mode 0600).''',
)

A["roo-code"] = dict(
    name="Roo Code", cmd="setup-roo", docs="https://docs.roocode.com",
    profile=False, root=False, key_in_file=True,
    wire="OpenAI Chat Completions (OpenAI Compatible profile in VS Code; an OpenRouter-type profile for the Roo CLI), base URL with /v1",
    select="the freellmapi profile (VS Code) or `roo -m auto` (CLI)",
    expect="three files under ~/.roo/: freellmapi.json, freellmapi-cli.json and cli-settings.json. Nothing else changes until the user wires the import path.",
    verify="The first two files contain the key by design and should not be printed or copied.",
    test="Follow the notes the CLI prints; they contain the exact VS Code setting (roo-cline.autoImportSettingsPath) and the CLI steps. Relay them to me verbatim.",
    after="The CLI notes list manual follow-up steps (a VS Code setting, and for the Roo CLI a global-state.json merge plus OPENROUTER_API_KEY). Do not perform those without asking me.",
    fallback=None,
)

A["kilo-code"] = dict(
    name="Kilo Code", cmd="setup-kilo", docs="https://kilocode.ai/docs",
    profile=False, root=False, key_in_file=False,
    wire="OpenAI Chat Completions, base URL with /v1",
    select="openai-compatible/auto (set as the default model)",
    expect="~/.config/kilo/kilo.jsonc gains a provider.openai-compatible entry (baseURL, apiKey as {env:FREELLMAPI_API_KEY}, models) and model = openai-compatible/auto.",
    verify="The key is referenced as {env:FREELLMAPI_API_KEY}, not written to the file.",
    test='FREELLMAPI_API_KEY is exported, then: kilo run "Say hello"',
    after="Tell me to export FREELLMAPI_API_KEY before starting Kilo. Do not write the key into any shell profile yourself.",
    fallback='''Merge into `~/.config/kilo/kilo.jsonc`:

```json
{
  "$schema": "https://app.kilo.ai/config.json",
  "model": "openai-compatible/auto",
  "provider": {
    "openai-compatible": {
      "options": {
        "apiKey": "{env:FREELLMAPI_API_KEY}",
        "baseURL": "http://freellmapi:3001/v1"
      },
      "models": {
        "auto": { "name": "Auto", "tool_call": true, "limit": { "context": 128000, "output": 8192 } }
      }
    }
  }
}
```''',
)

A["crush"] = dict(
    name="Crush", cmd="setup-crush", docs="https://github.com/charmbracelet/crush",
    profile=False, root=False, key_in_file=False,
    wire="OpenAI-compatible (type openai-compat), base URL with /v1",
    select="freellmapi/auto (large and small model)",
    expect="~/.config/crush/crush.json gains providers.freellmapi and models.large / models.small pointing at freellmapi/auto.",
    verify="The key is referenced as $FREELLMAPI_API_KEY, not written to the file.",
    test='FREELLMAPI_API_KEY is exported, then try a one-shot run: crush run "Say hello" (best effort: check `--help` for the exact one-shot syntax)',
    after="Tell me to export FREELLMAPI_API_KEY before starting Crush. Do not write the key into any shell profile yourself.",
    fallback='''Merge into `~/.config/crush/crush.json`:

```json
{
  "$schema": "https://charm.land/crush.json",
  "models": {
    "large": { "provider": "freellmapi", "model": "auto" },
    "small": { "provider": "freellmapi", "model": "auto" }
  },
  "providers": {
    "freellmapi": {
      "name": "FreeLLMAPI",
      "type": "openai-compat",
      "base_url": "http://freellmapi:3001/v1",
      "api_key": "$FREELLMAPI_API_KEY",
      "models": [
        {
          "id": "auto", "name": "Auto",
          "cost_per_1m_in": 0, "cost_per_1m_out": 0,
          "cost_per_1m_in_cached": 0, "cost_per_1m_out_cached": 0,
          "context_window": 128000, "default_max_tokens": 8192,
          "can_reason": false, "supports_attachments": false
        }
      ]
    }
  }
}
```''',
)

A["pi"] = dict(
    name="Pi", cmd="setup-pi", docs="https://pi.dev/docs/latest/models",
    profile=True, root=False, key_in_file=True,
    wire="OpenAI Chat Completions (api: openai-completions), base URL with /v1",
    select="pi --model freellmapi-local/auto",
    expect="~/.pi/agent/models.json gains a provider freellmapi-local. ~/.pi/agent/settings.json (defaultProvider, defaultModel) must not change.",
    verify="Pi has no .env support, so the key is stored in models.json by design (mode 0600). Do not print or copy that file.",
    test='pi --model freellmapi-local/auto -p "Say hello"',
    after="A running session reloads models.json when /model is opened. Install hint if Pi is missing: npm install -g @earendil-works/pi-coding-agent",
    fallback=None,
)

A["reasonix"] = dict(
    name="Reasonix", cmd="setup-reasonix", docs="https://github.com/esengine/DeepSeek-Reasonix/blob/studio/docs/CLI.md#configure-providers",
    profile=True, root=False, key_in_file=False,
    wire="OpenAI Chat Completions (kind = \"openai\"), base URL with /v1",
    select="reasonix --model freellmapi-local/auto",
    expect="~/.reasonix/config.toml gains a [[providers]] entry named freellmapi-local, and ~/.reasonix/.env gets FREELLMAPI_API_KEY=... The default_model must not change.",
    verify="config.toml names the variable api_key_env = \"FREELLMAPI_API_KEY\". ~/.reasonix/.env is mode 0600.",
    test='reasonix --model freellmapi-local/auto -p "Say hello"',
    after="Reasonix Studio only lists providers in [desktop].provider_access when that list is set. Tell me if it is and ask before adding \"freellmapi-local\" to it.",
    fallback=None,
)

A["zcode"] = dict(
    name="ZCode", cmd="setup-zcode", docs="https://zcode.z.ai/en/docs/configuration",
    profile=True, root=False, key_in_file=True,
    wire="OpenAI Chat Completions (openai-chat-completions), base URL with /v1",
    select="a freellmapi-local/<model> entry in the model picker",
    expect="~/.zcode/v2/provider_config.json gains a provider freellmapi-local. The default model must not change.",
    verify="ZCode has no environment lookup for custom providers, so the key is stored in provider_config.json by design (mode 0600). Do not print or copy that file.",
    test="Open ZCode (Desktop or CLI) and pick the new model from the picker.",
    after="ZCode Desktop must be CLOSED before the real run, otherwise the app overwrites the file from its in-memory registry. Ask me to quit it first.",
    fallback=None,
)

A["deepseek-harness"] = dict(
    name="DeepSeek Harness (dsh)", cmd="setup-dsh", docs="https://github.com/deepseek-ai/deepseek-harness",
    profile=True, root=False, key_in_file=False,
    wire="OpenAI Chat Completions (api: openai-completions), base URL with /v1",
    select="the route freellmapi-local (relay the selector the CLI prints in its notes)",
    expect="$DSH_HOME/settings.yaml (default ~/.dsh/settings.yaml) gains a route freellmapi-local under llm-pi-ai.providers, and $DSH_HOME/.env gets FREELLMAPI_API_KEY=... The default model must not change.",
    verify="The route names the variable by apiKeyEnv. $DSH_HOME/.env is mode 0600.",
    test="npx @deepseek-ai/dsh web, then pick the route.",
    after="Settings are hot-reloaded; no restart is needed.",
    fallback=None,
)

A["mimo-code"] = dict(
    name="MiMo Code", cmd="setup-mimo", docs="https://mimo.xiaomi.com/mimocode",
    profile=False, root=False, key_in_file=False,
    wire="OpenAI Chat Completions via @ai-sdk/openai-compatible, base URL with /v1",
    select="freellmapi/auto (set as the default model)",
    expect="config.json in MiMo's global config directory (~/.config/mimocode by default) gains a provider freellmapi and model = freellmapi/auto.",
    verify="The key is referenced as {env:FREELLMAPI_API_KEY}, not written to the file.",
    test='FREELLMAPI_API_KEY is exported, then try a one-shot run: mimo run "Say hello" (best effort: check `--help` for the exact one-shot syntax)',
    after="Tell me to export FREELLMAPI_API_KEY before starting MiMo. Do not write the key into any shell profile yourself.",
    fallback=None,
)

A["atomcode"] = dict(
    name="AtomCode", cmd="setup-atomcode", docs="https://atomcode.atomgit.com/docs/en/",
    profile=False, root=False, key_in_file=True,
    wire="OpenAI Chat Completions (provider = \"openai\"), base URL with /v1",
    select="default_model = freellmapi",
    expect="~/.atomcode/config.toml gains default_model = \"freellmapi\", [provider_accounts.freellmapi] and [models.freellmapi]. Unrelated accounts and models stay.",
    verify="The key is stored in config.toml by design (mode 0600). Do not print or copy that file.",
    test='atomcode -p "Say hello" (telemetry is on by default; mention `atomcode telemetry disable` to me)',
    after="Restart AtomCode.",
    fallback='''Add to `~/.atomcode/config.toml`. Put `default_model` above any table:

```toml
default_model = "freellmapi"

[provider_accounts.freellmapi]
provider = "openai"
base_url = "http://freellmapi:3001/v1"
api_key = "<unified key>"

[models.freellmapi]
account = "freellmapi"
model = "auto"
context_window = 128000
```

Keep the file mode 0600.''',
)

# ---------------------------------------------------------------------------
PROMPT = """\
@@GOAL@@

Parameters (edit before sending):
- GATEWAY: @@BASE@@  (used below as the shell variable $GATEWAY)
- PROFILE: @@PROFILE@@
- MODEL: auto
- API KEY: expected in the environment variable FREELLMAPI_API_KEY. If it is not set, ask me for the unified key (it starts with "freellmapi-").

Rules:
- FreeLLMAPI is an ordinary OpenAI-compatible endpoint, configured like any other provider such as Ollama. Nothing has to be installed for it on this machine. Do not install packages and do not change PATH.
- Never print the API key, never put it in a command line argument, never write it anywhere except where this task says the configuration stores it. Do not echo it in your replies or in logs.
- Only touch files that belong to @@NAME@@. Do not change anything else on this machine.
- Before you change an existing config file, make a timestamped backup copy and keep its permissions.
- If anything looks wrong, stop and show me the exact error without the key.
- Run all commands in one shell session so exported variables carry over.

Steps:
1. Reachability. Run `export GATEWAY=<the GATEWAY value above>`, then `curl -sS $GATEWAY/api/ping`. If the host name does not resolve or the connection fails, stop and tell me. This machine is then probably not on the same Docker network as FreeLLMAPI. Do not guess another address.
2. Catalog. Run `curl -sS -H "Authorization: Bearer $FREELLMAPI_API_KEY" $GATEWAY/v1/models` and confirm that a model with id "auto" is listed. A 401 means the key is wrong.
3. Configure. @@CONFIGURE@@
4. Verify. @@VERIFY@@
5. Test. @@TEST@@
6. Follow-up. @@AFTER@@

Final report: list the files you changed, what the test returned, and exactly what I type or run to use FreeLLMAPI with model "auto". @@SELECTLINE@@
"""

CLI_FLOW = (
    "Optional shortcut: if Node.js >= 20.18 and < 25 with npx is ALREADY installed on this machine, the official FreeLLMAPI CLI writes the same entries. "
    "Export `FREELLMAPI_URL=$GATEWAY`, run `npx --yes freellmapi @@CMD@@ @@PROFILEARG@@--model auto --dry-run`, show me the diff, apply only if it matches the expected result above, then run it again without --dry-run. "
    "Do not install Node.js for this; the direct way works without it."
)


def render(aid: str, a: dict) -> str:
    profile = "local" if a["profile"] else "(not used: this agent has no profile concept)"
    profilearg = "--profile local " if a["profile"] else ""
    if a["profile"]:
        goal = (
            f"Add FreeLLMAPI as an additional model provider for {a['name']} on this machine, without changing my default model. "
            f"Afterwards I want to use the model \"auto\" through FreeLLMAPI."
        )
    else:
        goal = (
            f"Add FreeLLMAPI as a model provider for {a['name']} on this machine, using the model \"auto\". "
            f"Keep my other providers and settings."
        )
    v1 = "" if a["root"] else "/v1"
    if a.get("fallback"):
        configure = (
            "Add the provider entry directly. Add exactly this and change nothing else "
            "(the examples use http://freellmapi:3001; use your GATEWAY value if you changed it):\n\n"
            + a["fallback"].replace("<unified key>", "<value of FREELLMAPI_API_KEY>")
            + "\n\n   Expected result: " + a["expect"] + "\n\n   " + CLI_FLOW
        )
    else:
        configure = (
            f"Add FreeLLMAPI in the agent's own provider settings as an OpenAI-compatible provider: base URL $GATEWAY{v1}, "
            f"API key from FREELLMAPI_API_KEY, model auto. Agent documentation: {a['docs']}\n"
            f"   Expected result: {a['expect']}\n"
            f"   If editing the settings by hand is impractical, use the optional shortcut. {CLI_FLOW}"
        )
    configure = configure.replace("@@CMD@@", a["cmd"]).replace("@@PROFILEARG@@", profilearg)
    select_line = f"Expected selector: {a['select']}." if a.get("select") else ""
    return (PROMPT
            .replace("@@GOAL@@", goal)
            .replace("@@BASE@@", BASE)
            .replace("@@PROFILE@@", profile)
            .replace("@@NAME@@", a["name"])
            .replace("@@CONFIGURE@@", configure)
            .replace("@@VERIFY@@", a["verify"])
            .replace("@@TEST@@", a["test"])
            .replace("@@AFTER@@", a["after"])
            .replace("@@SELECTLINE@@", select_line))


def page(aid: str, a: dict) -> str:
    prompt = render(aid, a)
    ver = "root URL (no /v1)" if a["root"] else "`/v1` URL"
    key = ("stored in a config file by design" if a["key_in_file"] else "kept out of the config files (environment variable or separate `.env`)")
    out = f"""# {a['name']} with FreeLLMAPI

[← All clients](../README.md) · Official docs: <{a['docs']}> · Upstream notes: [agent clients guide]({UPDOCS})

|  |  |
| --- | --- |
| Optional CLI shortcut | `npx --yes freellmapi {a['cmd']}` (writes the same entries; not required) |
| Wire | {a['wire']} |
| Base URL form | {ver} |
| Profile support | {"yes (`--profile local` leaves the default model alone)" if a['profile'] else "no (the command makes FreeLLMAPI the default and merges into the existing config)"} |
| API key | {key} |

{a.get('extra', '')}

## Prompt

Copy this into {a['name']} (or any coding agent) on the machine where {a['name']} runs. FreeLLMAPI is configured like any other OpenAI-compatible endpoint, so **nothing has to be installed for it** on that machine. Edit the three parameters at the top first. The default gateway address assumes the agent runs in a container on the same custom Docker network as FreeLLMAPI; see [choosing the gateway address](../README.md#choosing-the-gateway-address) for the other cases.

````text
{prompt}````

Prompts are derived from the FreeLLMAPI CLI 0.8.2 source and the upstream documentation. They have not been run against every agent; the expected-result check in step 3 and the test in step 5 are the safety net.
"""
    return out.replace("\n\n\n", "\n\n")


for aid, a in A.items():
    with open(os.path.join(PROMPTS, f"{aid}.md"), "w", encoding="utf-8") as fh:
        fh.write(page(aid, a))

# ---------------------------------------------------------------------------
# Guide-only clients: Cursor, QwenPaw, generic.
# ---------------------------------------------------------------------------
with open(os.path.join(PROMPTS, "generic.md"), "w", encoding="utf-8") as fh:
    fh.write(f"""# Any OpenAI-compatible client with FreeLLMAPI

[← All clients](../README.md) · Upstream notes: [agent clients guide]({UPDOCS})

For LangChain, LlamaIndex, the official OpenAI SDKs, Open WebUI and every client that accepts a custom OpenAI base URL. No setup command is needed.

| Setting | Value |
| --- | --- |
| Base URL | `{BASE}/v1` |
| API key | the unified key from the FreeLLMAPI dashboard (Keys page), starts with `freellmapi-` |
| Model | `auto` (the router picks per request), or an id from `GET /v1/models` |

Quick check from any shell that can reach the gateway:

```bash
curl -sS {BASE}/v1/chat/completions \\
  -H "Authorization: Bearer $FREELLMAPI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{"model":"auto","messages":[{{"role":"user","content":"Say hello"}}]}}'
```

Python:

```python
import os
from openai import OpenAI
client = OpenAI(base_url="{BASE}/v1", api_key=os.environ["FREELLMAPI_API_KEY"])
print(client.chat.completions.create(model="auto", messages=[{{"role": "user", "content": "Say hello"}}]).choices[0].message.content)
```

The CLI can print the same block for your URL: `npx --yes freellmapi setup-generic --url {BASE}`.

## Prompt

````text
Configure the application or SDK in this project to use FreeLLMAPI as its OpenAI-compatible endpoint.

Parameters (edit before sending):
- GATEWAY: {BASE}  (used below as the shell variable $GATEWAY)
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
""")

with open(os.path.join(PROMPTS, "cursor.md"), "w", encoding="utf-8") as fh:
    fh.write(f"""# Cursor with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://docs.cursor.com> · Upstream notes: [agent clients guide]({UPDOCS})

**Cursor does not work with a private gateway.** Cursor sends model traffic through its own cloud service, so addresses such as `http://freellmapi:3001`, a LAN IP or a Tailscale name are not reachable from it. This is a Cursor limitation, not a FreeLLMAPI one.

The only way is to publish the gateway on a public HTTPS URL, for example through a tunnel. FreeLLMAPI is a single-user application guarded only by its API key, so exposing it publicly is a real risk. If you do it anyway:

- Use a tunnel with its own authentication, and rotate the unified key afterwards.
- Prefer a separately revocable URL token over the unified key (Keys → Agents in the dashboard). Tokens live at `/v1/t/<token>/...`.
- In Cursor: Settings → Models → enable **Override OpenAI Base URL** and enter `<public-url>/v1`. Add a custom model named `auto`.
- Cursor documents custom keys only for standard chat models, so Responses-based or built-in models may not work with the override. The override applies globally while enabled.

There is no prompt for Cursor because there is nothing an agent can configure on disk. `npx --yes freellmapi setup-cursor` prints this guide.
""")

with open(os.path.join(PROMPTS, "qwenpaw.md"), "w", encoding="utf-8") as fh:
    fh.write(f"""# QwenPaw with FreeLLMAPI

[← All clients](../README.md) · Official docs: <https://qwenpaw.agentscope.io/docs/models> · Upstream notes: [agent clients guide]({UPDOCS})

QwenPaw has no setup command. Configure it in the Console under **Settings → Models**:

1. Providers → **Add Provider**.
2. Provider ID `freellmapi`, Provider Name `FreeLLMAPI`, API compatibility mode OpenAI `chat.completions`.
3. In the provider settings set **Base URL** to `{BASE}/v1` and **API Key** to the unified key.
4. On the provider's models page add a model with Model ID `auto`.
5. Save, pick the model as default (or per chat) and send a test message.

If QwenPaw runs in a container, `localhost` means that container. Use `{BASE}` only when QwenPaw is on the same custom Docker network as FreeLLMAPI; otherwise use the Unraid LAN address or the Tailscale name. Keep the `/v1` suffix. Do not put the unified key in a URL, screenshot or issue report.
""")

# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------
rows = []
order = ["claude-code", "codex", "hermes", "openclaw", "opencode", "goose", "aider", "cline", "continue",
         "qwen-code", "roo-code", "kilo-code", "crush", "pi", "reasonix", "zcode", "deepseek-harness",
         "mimo-code", "atomcode"]
for aid in order:
    a = A[aid]
    rows.append(f"| [{a['name']}](prompts/{aid}.md) | `{a['cmd']}` | {'yes' if a['profile'] else 'no'} | {'server root' if a['root'] else '`/v1`'} |")
rows.append("| [Any OpenAI-compatible client](prompts/generic.md) | `setup-generic` prints a block | n/a | `/v1` |")
rows.append("| [QwenPaw](prompts/qwenpaw.md) | manual, UI steps | n/a | `/v1` |")
rows.append("| [Cursor](prompts/cursor.md) | not possible on a private network | n/a | public HTTPS `/v1` |")

with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as fh:
    fh.write(f"""# Connecting agents and apps to FreeLLMAPI

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
| in a container on the same custom Docker network as FreeLLMAPI | `http://freellmapi:3001` | Docker\'s embedded DNS resolves container names and network aliases; `--hostname` is not documented as resolvable. Add `--network-alias=freellmapi` to the Extra Parameters of the FreeLLMAPI container to be safe. Container port 3001, no published port needed, no TLS. |
| on another machine in your LAN | `http://<unraid-ip>:3001` | Or the Unraid server name if your network resolves it. |
| anywhere in your tailnet | `https://freellmapi.<tailnet>.ts.net` | Needs "Use Tailscale" enabled in the container (the template pre-fills it, mode Serve). Valid certificate, no port. |
| in Cursor | not possible | See the Cursor page. |

Do not expose the gateway to the public internet. It is a single-user application guarded only by its API key.

## Agents

| Agent | Setup command | Profile (keeps your default model) | Base URL form |
| --- | --- | --- | --- |
{chr(10).join(rows)}

"Profile" means the CLI can add FreeLLMAPI as an additional provider under the name `local` instead of replacing your current default. Agents without profile support get FreeLLMAPI as their default provider; the CLI merges rather than overwrites, and the dry-run diff shows exactly what changes.

## Conventions used by every prompt

- Model `auto`: FreeLLMAPI's router picks the best available model per request and fails over on rate limits. A concrete model id from `GET /v1/models` works too.
- Profile name `local`: change it freely. The provider name is `freellmapi-` plus the profile name, so `local` becomes `freellmapi-local`.
- The API key is never passed as a command line argument. The CLI reads `FREELLMAPI_URL` and `FREELLMAPI_API_KEY` from the environment.
- Several agents store the key in their own config file by design (the CLI creates those files with mode 0600). The prompt says so per agent and tells the agent not to print or copy such files.
- The prompt states the expected result per agent. If a change would touch more than that, the agent stops.

## Sources and limits

Derived from the upstream [agent clients guide]({UPDOCS}) and the CLI source (version 0.8.2). The prompts have not been executed against every agent. If an agent changes its configuration format, the optional CLI is the authority: run `npx --yes freellmapi list` for the supported agents and `npx --yes freellmapi doctor <agent>` to check that requests actually reach the gateway.

Maintenance: the pages are generated by `tools/gen-client-docs.py docs/clients`. Edit the script, not the pages.
""")

print("generated", len(os.listdir(PROMPTS)), "prompt pages")
