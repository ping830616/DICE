#!/bin/bash
set -euo pipefail

OUT_RAW="${1:?Need output raw file path (.txt)}"
SAMPLES="${2:-5000}"
INTERVAL_MS="${3:-200}"

mkdir -p "$(dirname "$OUT_RAW")"
ERR_LOG="${OUT_RAW}.stderr.log"
: > "$OUT_RAW"
: > "$ERR_LOG"

sudo -v

run_try () {
  local samplers="$1"
  echo "[TRY] samplers=${samplers}" >> "$ERR_LOG"
  sudo powermetrics -i "${INTERVAL_MS}" -n "${SAMPLES}" -s "${samplers}" \
    > "${OUT_RAW}" 2>> "${ERR_LOG}" || return 1
  return 0
}

# Try progressively simpler sampler sets
run_try "cpu_power,gpu_power,thermal" || \
run_try "cpu_power,thermal" || \
run_try "cpu_power" || true

# If still tiny, record it (so python can decide to re-run)
bytes=$(wc -c < "$OUT_RAW" | tr -d ' ')
echo "[INFO] raw_bytes=${bytes}" >> "$ERR_LOG"
