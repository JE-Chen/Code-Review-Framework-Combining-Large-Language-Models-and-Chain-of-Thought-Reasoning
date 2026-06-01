#!/usr/bin/env bash
# Rebuild the prthinker server container without taking the GPU host
# down with it. Encodes the operational sequence behind the
# attention-impl boot guard (codes/util/qwen3_util._verify_non_eager_
# attention) and the flash-attn MAX_JOBS cap (docker/Dockerfile.server):
#
#   1. Stop the running model container so its ~25 GiB host RAM is
#      free before the flash-attn nvcc build starts. Skipping this is
#      the #1 cause of OOM-killer killing cloudflared / sshd mid-build
#      and producing the "GPU server disconnects during build" symptom.
#   2. Pull origin/dev so the build uses the latest Dockerfile.server.
#   3. Run docker compose build with --progress=plain | tee to a log,
#      while a background loop snapshots `free -h` every 2 seconds so
#      a post-mortem can identify when peak RAM hit.
#   4. After the build, scan dmesg for the oom-killer's fingerprint
#      and warn loudly if it fired during this run.
#   5. Bring the server back up and tail the log until /healthz answers
#      200, then verify the boot guard saw flash_attention_2 or sdpa.
#
# Run on the GPU host from the repo root:
#   ./docker/rebuild-server.sh
#
# Default is 16, sized for this host's 503 GiB RAM (~10 min build).
# On a smaller host (<=128 GiB) drop the cap to avoid the OOM killer:
#   FLASH_ATTN_MAX_JOBS=4 ./docker/rebuild-server.sh

set -euo pipefail

cd "$(dirname "$0")/.."

LOG_DIR=".prthinker/rebuild-logs"
mkdir -p "$LOG_DIR"
TS="$(date +%Y%m%d-%H%M%S)"
BUILD_LOG="$LOG_DIR/build-${TS}.log"
MEM_LOG="$LOG_DIR/mem-${TS}.log"

# dmesg cursor: record the kernel ringbuffer position BEFORE the build
# so the post-mortem scan only sees messages from this build run.
DMESG_MARK="$(dmesg -T 2>/dev/null | tail -1 || true)"

FLASH_ATTN_MAX_JOBS="${FLASH_ATTN_MAX_JOBS:-16}"

# Compose files. The monitoring overlay (Prometheus / Grafana / DCGM /
# cAdvisor + the nginx that fronts host:9000 and serves /prometheus/,
# /grafana/, /cadvisor/, /kg/) is included by default so a rebuild
# brings the whole observability stack back up — not just the model
# server. Without it, `up -d` would recreate prthinker with its own
# 9000 host binding and the monitoring containers would be left behind.
# Set PRTHINKER_WITH_MONITORING=0 to rebuild the bare server only.
COMPOSE="docker compose -f docker/docker-compose.yml"
if [ "${PRTHINKER_WITH_MONITORING:-1}" != "0" ]; then
    COMPOSE="$COMPOSE -f docker/docker-compose.monitoring.yml"
fi

echo ">>> [1/5] Stopping running server container to free host RAM"
$COMPOSE stop prthinker || true

echo ">>> [2/5] git pull origin dev"
git pull --ff-only origin dev

echo ">>> [3/5] Building server image (MAX_JOBS=${FLASH_ATTN_MAX_JOBS})"
echo "        build log: ${BUILD_LOG}"
echo "        mem log:   ${MEM_LOG}"

# Background memory sampler. PID is captured so we can clean it up
# even if the build fails.
(
    while true; do
        printf '%s  ' "$(date '+%H:%M:%S')" >> "$MEM_LOG"
        free -h | awk '/^Mem:/ {printf "total=%s used=%s free=%s avail=%s\n", $2, $3, $4, $7}' >> "$MEM_LOG"
        sleep 2
    done
) &
MEM_PID=$!
trap 'kill ${MEM_PID} 2>/dev/null || true' EXIT

BUILD_RC=0
$COMPOSE build \
    --no-cache \
    --progress=plain \
    --build-arg "FLASH_ATTN_MAX_JOBS=${FLASH_ATTN_MAX_JOBS}" \
    prthinker 2>&1 | tee "$BUILD_LOG" || BUILD_RC=$?

kill "$MEM_PID" 2>/dev/null || true
trap - EXIT

echo ">>> [4/5] Scanning dmesg for oom-killer activity during build"
OOM_HITS="$(dmesg -T 2>/dev/null \
    | awk -v mark="$DMESG_MARK" 'index($0, mark) {seen=1; next} seen' \
    | grep -iE 'killed process|oom-killer|out of memory' || true)"
if [ -n "$OOM_HITS" ]; then
    echo "!!! OOM-killer fired during build:"
    echo "$OOM_HITS" | sed 's/^/    /'
    echo "!!! Common victims (cloudflared, sshd, dockerd, server container)"
    echo "!!! mean the host RAM ceiling was breached. Reduce"
    echo "!!! FLASH_ATTN_MAX_JOBS (current=${FLASH_ATTN_MAX_JOBS}) or stop"
    echo "!!! other workloads before the next rebuild."
else
    echo "    No oom-killer entries since the build started."
fi

if [ "$BUILD_RC" -ne 0 ]; then
    echo "!!! Build failed (rc=$BUILD_RC). Check ${BUILD_LOG} and ${MEM_LOG}."
    exit "$BUILD_RC"
fi

echo ">>> [5/5] Bringing the stack up and verifying attention impl"
# No service arg: bring up every service in the selected compose files
# (prthinker alone if monitoring is disabled, the full overlay otherwise)
# so a rebuild never leaves the monitoring containers behind.
$COMPOSE up -d

HEALTH_URL="http://127.0.0.1:9000/healthz"
echo "    waiting for ${HEALTH_URL} ..."
for _ in $(seq 1 60); do
    if curl -fsS --max-time 3 "${HEALTH_URL}" > /dev/null 2>&1; then
        echo "    /healthz is up"
        break
    fi
    sleep 5
done

ATTN_LINE="$($COMPOSE logs --tail=200 prthinker 2>/dev/null \
    | grep -E 'Attention implementation:|Refusing to start|PRTHINKER_ALLOW_EAGER_ATTENTION' \
    | tail -1 || true)"
if echo "$ATTN_LINE" | grep -qE 'Attention implementation: *(flash_attention_2|sdpa)'; then
    echo "    OK: ${ATTN_LINE}"
elif echo "$ATTN_LINE" | grep -qE 'Attention implementation: *eager'; then
    echo "!!! Server booted on EAGER attention — the O(N^2) path that"
    echo "!!! caused the 269 GiB runtime OOM. The boot guard should have"
    echo "!!! refused this; investigate qwen3_util._verify_non_eager_attention."
    exit 1
elif echo "$ATTN_LINE" | grep -q "Refusing to start"; then
    echo "!!! Boot guard refused to start: ${ATTN_LINE}"
    echo "!!! Image build succeeded but flash-attn / SDPA is not"
    echo "!!! actually dispatched. Container will not serve reviews."
    exit 1
elif [ -z "$ATTN_LINE" ]; then
    echo "??? Could not find an attention-impl line in the last 200"
    echo "??? log lines. Inspect:  ${COMPOSE} logs --tail=500 prthinker"
else
    echo "WARN: ${ATTN_LINE}"
fi

echo ">>> Done. Build log: ${BUILD_LOG} | mem log: ${MEM_LOG}"
