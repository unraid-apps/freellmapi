# FreeLLMAPI for Unraid

Unraid Community Applications template and one-click wrapper image for [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi): one OpenAI-compatible endpoint in front of the free tiers of 30+ LLM providers, with automatic failover, key rotation and a web dashboard.

**Image:** `ghcr.io/unraid-apps/freellmapi` (linux/amd64, linux/arm64) · **Template:** [`templates/freellmapi.xml`](templates/freellmapi.xml) · **Mirrored versions:** [VERSIONS.md](VERSIONS.md)

## What the wrapper adds

The official image requires an `ENCRYPTION_KEY` and refuses to start without one. Unraid templates cannot generate random values, so this image puts a ten-line [entrypoint](entrypoint.sh) in front of the upstream one:

| Situation | Behaviour |
| --- | --- |
| `ENCRYPTION_KEY` set in the template | Used as-is, nothing written to disk. Aborts if a stored key file exists and differs. |
| Variable empty, key file exists | Key read from `/app/server/data/.encryption-key`. |
| Variable empty, no key file, no database | New 32-byte key generated, stored 0600 owned by `node`, path logged (never the key). |
| Variable empty, no key file, but a database exists | Start refused with an explanation. The data was encrypted with a key we do not have. |

Everything else is the upstream image, byte for byte. The [sync workflow](.github/workflows/sync-upstream.yml) mirrors every stable upstream release (`vX.Y.Z`) within six hours, runs a [smoke test](scripts/smoke-test.sh) against every build, and publishes the newest one as `latest`.

## Install on Unraid

### From Community Applications

Search for **FreeLLMAPI** in the Apps tab and click Install. Leave `ENCRYPTION_KEY` empty unless you want to bring your own key.

### Before it is listed

Settings → Docker → enable *Advanced View* → add `https://github.com/unraid-apps/freellmapi` under *Template repositories* → Docker tab → Add Container → pick **FreeLLMAPI** from the template dropdown.

### First start

1. Click **WebUI** on the container (`http://<unraid-ip>:3001`).
2. FreeLLMAPI asks for a one-time **setup code** because you are not on the same machine as the server. It is printed in the container log: Docker tab → container icon → **Logs**, look for `First-run setup code`.
3. Create the admin account, open **Keys**, add your provider keys (Groq, Google, Mistral, OpenRouter, …) and copy the unified `freellmapi-…` key shown at the top.
4. Point any OpenAI-compatible client at `http://<unraid-ip>:3001/v1` with that key:

```bash
curl http://<unraid-ip>:3001/v1/chat/completions \
  -H "Authorization: Bearer freellmapi-YOUR-KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "auto", "messages": [{"role": "user", "content": "Hello from Unraid"}]}'
```

Most coding agents configure themselves with one command, for example `npx freellmapi setup-claude --url http://<unraid-ip>:3001 --api-key <unified-key>`. See the [upstream client guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/02-supported-agents.md).

## Template settings

| Field | Default | Notes |
| --- | --- | --- |
| WebUI / API port | `3001` | Host port. The container always listens on 3001. |
| Data | `/mnt/user/appdata/freellmapi` | SQLite database, settings, analytics and `.encryption-key`. Owner becomes UID/GID 1000 on start; that is expected. |
| `ENCRYPTION_KEY` | empty | Leave empty to auto-generate. Or `openssl rand -hex 32`. Never change it afterwards. |
| `TZ` | `Europe/Berlin` | Time zone for logs and analytics. |

Under *Show more settings*:

| Variable | Purpose |
| --- | --- |
| `FREELLMAPI_UPDATE_CHECK=off` | Keeps the dashboard's own updater quiet. Its "Update now" button needs a Watchtower sidecar that does not exist here; update through the Docker tab. |
| `PROXY_URL` | Outbound proxy for provider requests, e.g. `socks5h://host.docker.internal:7890`. |
| `STREAM_KEEPALIVE_MS` | `15000` if Claude Code or similar clients abort long reasoning streams before the first token. |
| `TRUST_PROXY` | `1` behind a reverse proxy or Tailscale Serve so analytics see the real client IP. |
| `DASHBOARD_ORIGINS` | Extra browser origins when the dashboard is reached under another host name. |
| `FREEAPI_CONFIG_PATH` | JSON startup config (admin account, provider keys, routing), applied on every start. |
| `PROXY_RATE_LIMIT_RPM` | Requests per minute per client IP for `/v1`, default 120, `0` disables. |
| `REQUEST_ANALYTICS_RETENTION_DAYS`, `REQUEST_ANALYTICS_MAX_ROWS` | Analytics retention, defaults 90 days / 100000 rows. |
| `FREEAPI_BLOCK_PRIVATE_PROVIDER_URLS` | `true` to forbid LAN/localhost custom providers. Default allows them (Ollama, LM Studio, vLLM on your network). |
| `CATALOG_SYNC_DISABLED` | `1` stops the signed model-catalog sync from freellmapi.co. |

Extra parameters: `--add-host=host.docker.internal:host-gateway` (so an Ollama on the Unraid host is reachable as `http://host.docker.internal:11434/v1`) and `--hostname=freellmapi`.

### Further tuning

FreeLLMAPI reads about 80 environment variables; the ones above are the Unraid-relevant subset. Most of the rest (fallback budgets, response cache, compression, guardrails) are **also settable in the dashboard, and the dashboard value wins**, so they are deliberately not template fields. Anything else, including per-provider settings such as `PROVIDER_TIMEOUT_NVIDIA`, can be added with *Add another Path, Port, Variable, Label or Device*. Reference: [upstream `.env.example`](https://github.com/tashfeenahmed/freellmapi/blob/main/.env.example).

The image ships the pre-built dashboard on the same port as the API. There is no separate dev server; for development follow the [upstream guide](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/install/01-install.md#local-development) outside Docker.

## Tailscale

The template pre-fills Unraid's per-container Tailscale integration (Unraid 7 with the Tailscale plugin): hostname `freellmapi`, mode **Serve**, port 3001. Flip **Use Tailscale** in the container settings and the dashboard and API become `https://freellmapi.<your-tailnet>.ts.net` with a valid certificate, reachable only from your tailnet. The WebUI button follows automatically. Set `TRUST_PROXY=1` so analytics show real client IPs.

Do **not** switch the mode to *Funnel*. FreeLLMAPI is a single-user application guarded only by its API key; exposing it to the public internet is not what it is built for.

## Reverse proxy

Nginx Proxy Manager, SWAG, Traefik and Caddy work as usual against port 3001. Set `TRUST_PROXY=1` (one hop) and, if the dashboard lives on a different host name than the API, add it to `DASHBOARD_ORIGINS`. Put authentication in front if the proxy is reachable from outside your network.

## Updates

Unraid's Docker tab → **Check for Updates** → apply. Data folder and key stay. New upstream releases appear here within six hours; the dashboard's own update checker is turned off because it cannot trigger an Unraid update.

To pin a version, change the repository field to e.g. `ghcr.io/unraid-apps/freellmapi:v0.16.19`. Available tags are listed in [VERSIONS.md](VERSIONS.md). Tags mirror upstream exactly, so upstream release notes apply.

## Backup

Two things matter: the data folder (`/mnt/user/appdata/freellmapi`, which includes `.encryption-key` when auto-generated) and, if you set your own key, the `ENCRYPTION_KEY` value in the template. The *Appdata Backup* plugin covers the folder; the template XML lives on the flash drive under `/boot/config/plugins/dockerMan/templates-user/` and is part of the flash backup.

## Troubleshooting

- **Container stops right away, log says `ENCRYPTION_KEY is set but differs`** – you changed the key after data was stored. Clear the field or restore the original value.
- **Log says `a database exists … but no encryption key was found`** – the folder has a database from an install that used an explicit key. Set that key, or move the database away to start fresh.
- **Dashboard loads, but setup code is rejected** – the code changes on every restart while no account exists. Read it again from the current log.
- **Providers unreachable from the container but fine from the host** – a proxy on `127.0.0.1` of the host is not reachable from the container; use `host.docker.internal` or the host's LAN IP, and make sure the proxy listens beyond loopback.
- **Permissions on appdata changed to 1000:1000** – intended. The upstream entrypoint chowns the data directory and drops to the `node` user.

## Repository layout

```
templates/freellmapi.xml       Community Applications template
ca_profile.xml                 repository profile shown in CA
Dockerfile, entrypoint.sh      wrapper image
scripts/upstream-versions.py   decides which upstream tags to (re)build
scripts/smoke-test.sh          start/restart/mismatch/explicit-key test against a built image
scripts/record-version.py      writes versions.json and VERSIONS.md
scripts/validate-template.py   XML checks used by the validate workflow
.github/workflows/             sync-upstream (every 6 h) and validate (push/PR)
```

## Support

- Template, container start, key handling, image mirror: [open an issue here](https://github.com/unraid-apps/freellmapi/issues).
- FreeLLMAPI itself (routing, providers, dashboard, API): [upstream issues](https://github.com/tashfeenahmed/freellmapi/issues).

## Credits and license

FreeLLMAPI is created by [Tashfeen Ahmed](https://github.com/tashfeenahmed) and released under the MIT License; the icon in this repository is the upstream application icon. This repository (template, wrapper, workflows) is MIT licensed as well, see [LICENSE](LICENSE). Maintained by [Hardskiller](https://github.com/Hardskiller). Not affiliated with Lime Technology or the FreeLLMAPI project.
