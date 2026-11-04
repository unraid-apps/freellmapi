#!/bin/sh
# Unraid wrapper entrypoint for FreeLLMAPI.
#
# Upstream requires ENCRYPTION_KEY in production and refuses to start without
# it. Unraid templates cannot generate random values, so this script fills the
# gap: when the variable is empty it reads or creates a key file inside the
# persistent data directory, exports it, and hands over to the upstream
# entrypoint (which chowns the data dir and drops to the `node` user).
#
# Rules:
#   * ENCRYPTION_KEY set   -> used as-is. If a key file exists and differs, abort
#                             (otherwise every stored provider key would fail to
#                             decrypt and the user would not know why).
#   * no variable, key file -> use the file.
#   * no variable, no file, but a database already exists -> abort. The DB was
#                             encrypted with a key we do not have; generating a
#                             new one would silently orphan the stored secrets.
#   * no variable, no file, no DB -> generate a key, write it 0600 owned by node.
#
# The key itself is never printed. Only its path is.
set -eu

UPSTREAM_ENTRYPOINT=/usr/local/bin/docker-entrypoint.sh
DATA_DIR=/app/server/data

# Upstream keeps its dev-mode key file next to the database, so follow
# FREEAPI_DB_PATH when an operator moved the database elsewhere.
DB_PATH="${FREEAPI_DB_PATH:-$DATA_DIR/freeapi.db}"
KEY_DIR="$(dirname "$DB_PATH")"
KEY_FILE="$KEY_DIR/.encryption-key"

log() { echo "unraid-entrypoint: $*" >&2; }

is_hex_key() {
  # 64 hex characters, nothing else.
  case "$1" in
    *[!0-9a-fA-F]*) return 1 ;;
  esac
  [ "${#1}" -eq 64 ]
}

read_key_file() {
  tr -d '[:space:]' < "$KEY_FILE"
}

owner_ids() {
  # The upstream image runs the server as `node`; fall back to 1000 if the
  # user is missing for any reason so the file is still not root-owned.
  NODE_UID="$(id -u node 2>/dev/null || echo 1000)"
  NODE_GID="$(id -g node 2>/dev/null || echo 1000)"
}

write_key_file() {
  key="$1"
  owner_ids
  if ! mkdir -p "$KEY_DIR"; then
    log "ERROR: cannot create $KEY_DIR"
    exit 1
  fi
  tmp="$KEY_FILE.tmp-$$"
  umask 077
  printf '%s\n' "$key" > "$tmp"
  chown "$NODE_UID:$NODE_GID" "$tmp" 2>/dev/null || log "warning: could not chown $tmp (CIFS/NFS?); continuing"
  mv -f "$tmp" "$KEY_FILE"
  chmod 0600 "$KEY_FILE" 2>/dev/null || true
}

generate_key() {
  # 32 random bytes as lowercase hex, using only tools present in
  # node:*-bookworm-slim (od is coreutils).
  od -An -N32 -tx1 /dev/urandom | tr -d ' \n'
}

if [ -n "${ENCRYPTION_KEY:-}" ]; then
  if ! is_hex_key "$ENCRYPTION_KEY"; then
    log "ERROR: ENCRYPTION_KEY must be exactly 64 hex characters (32 bytes)."
    log "Generate one with: openssl rand -hex 32   (or leave the field empty to auto-generate)"
    exit 1
  fi
  if [ -f "$KEY_FILE" ]; then
    existing="$(read_key_file)"
    if [ "$existing" != "$ENCRYPTION_KEY" ]; then
      log "ERROR: ENCRYPTION_KEY is set but differs from the key stored in $KEY_FILE."
      log "This install was encrypted with the stored key. Either clear the ENCRYPTION_KEY"
      log "field to keep using the stored key, or set it to the value in that file."
      exit 1
    fi
  fi
  log "using ENCRYPTION_KEY from the environment"
else
  if [ -f "$KEY_FILE" ]; then
    key="$(read_key_file)"
    if ! is_hex_key "$key"; then
      log "ERROR: $KEY_FILE exists but does not contain a 64-character hex key. Refusing to start."
      exit 1
    fi
    ENCRYPTION_KEY="$key"
    log "using the stored encryption key at $KEY_FILE"
  elif [ -f "$DB_PATH" ]; then
    log "ERROR: a database exists at $DB_PATH but no encryption key was found."
    log "The data was encrypted with a key that is neither in ENCRYPTION_KEY nor in $KEY_FILE."
    log "Set ENCRYPTION_KEY to the original key, or move the old database away to start fresh."
    exit 1
  else
    key="$(generate_key)"
    if ! is_hex_key "$key"; then
      log "ERROR: failed to generate a random key"
      exit 1
    fi
    write_key_file "$key"
    ENCRYPTION_KEY="$key"
    log "generated a new encryption key at $KEY_FILE"
    log "BACK UP THIS FILE together with the database. Without it the stored provider keys cannot be decrypted."
  fi
  export ENCRYPTION_KEY
fi

if [ ! -x "$UPSTREAM_ENTRYPOINT" ]; then
  log "ERROR: upstream entrypoint $UPSTREAM_ENTRYPOINT is missing. The upstream image layout changed; this wrapper needs an update."
  exit 1
fi

exec "$UPSTREAM_ENTRYPOINT" "$@"
