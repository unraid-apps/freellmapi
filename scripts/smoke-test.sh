#!/usr/bin/env bash
# Smoke test for the wrapper image. Usage: smoke-test.sh <image>
#
# Exercises every branch of entrypoint.sh against a real container:
#   1. fresh volume, no key      -> key file generated, /api/ping answers
#   2. same volume, restart      -> stored key reused
#   3. same volume, wrong key    -> refuses to start
#   4. fresh volume, explicit key-> starts, writes no key file
set -euo pipefail

IMAGE="${1:?image required}"
WORK="$(mktemp -d)"
NAME="freellmapi-smoke-$$"
trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true; docker run --rm -v "$WORK:/w" alpine:3.20 sh -c "rm -rf /w/*" >/dev/null 2>&1 || true; rm -rf "$WORK"' EXIT

fail() { echo "SMOKE FAIL: $*" >&2; docker logs "$NAME" 2>&1 | tail -40 >&2 || true; exit 1; }

wait_ping() {
  local port deadline=$((SECONDS + 120))
  port="$(docker port "$NAME" 3001/tcp | head -1 | sed 's/.*://')"
  until curl -fsS "http://127.0.0.1:${port}/api/ping" >/dev/null 2>&1; do
    if ! docker ps -q --no-trunc --filter "name=^/${NAME}$" | grep -q .; then fail "container exited before /api/ping answered"; fi
    [ "$SECONDS" -lt "$deadline" ] || fail "/api/ping did not answer within 120s"
    sleep 2
  done
}

run() { docker run -d --name "$NAME" -p 127.0.0.1::3001 -v "$WORK/data:/app/server/data" "$@" "$IMAGE" >/dev/null; }
stop() { docker rm -f "$NAME" >/dev/null; }

echo "== 1. fresh start without ENCRYPTION_KEY"
mkdir -p "$WORK/data"
run
wait_ping
docker logs "$NAME" 2>&1 | grep -q "generated a new encryption key" || fail "expected key generation message"
KEY="$(docker exec "$NAME" sh -c 'cat /app/server/data/.encryption-key')" || fail "key file missing"
[[ "$KEY" =~ ^[0-9a-f]{64}$ ]] || fail "key file content is not 64 hex chars"
PERM="$(docker exec "$NAME" stat -c '%a %U' /app/server/data/.encryption-key)"
[ "$PERM" = "600 node" ] || fail "key file should be 0600 owned by node, got '$PERM'"
docker logs "$NAME" 2>&1 | grep -q "$KEY" && fail "key leaked into logs"
stop

echo "== 2. restart reuses the stored key"
run
wait_ping
docker logs "$NAME" 2>&1 | grep -q "using the stored encryption key" || fail "expected stored-key message"
stop

echo "== 3. conflicting ENCRYPTION_KEY is refused"
run -e ENCRYPTION_KEY="$(printf 'ab%.0s' $(seq 32))"
sleep 3
if docker ps -q --no-trunc --filter "name=^/${NAME}$" | grep -q .; then fail "container should have exited on key mismatch"; fi
docker logs "$NAME" 2>&1 | grep -q "differs from the key stored" || fail "expected mismatch message"
stop

echo "== 4. explicit ENCRYPTION_KEY on a fresh volume"
docker run --rm -v "$WORK:/w" alpine:3.20 sh -c "rm -rf /w/data && mkdir /w/data" >/dev/null
run -e ENCRYPTION_KEY="$(printf 'cd%.0s' $(seq 32))"
wait_ping
docker logs "$NAME" 2>&1 | grep -q "using ENCRYPTION_KEY from the environment" || fail "expected env-key message"
docker exec "$NAME" test -f /app/server/data/.encryption-key && fail "no key file should be written when the env var is set"
stop

echo "SMOKE OK"
