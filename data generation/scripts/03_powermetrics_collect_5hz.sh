#!/bin/bash
set -euo pipefail

OUT_RAW="${1:?Need output raw file path (.txt)}"
SAMPLES="${2:-5000}"
INTERVAL_MS="${3:-200}"
ENABLE_EXTRA_POWER_INFO="${4:-1}"   # 1=try --show-extra-power-info first

mkdir -p "$(dirname "$OUT_RAW")"
ERR_LOG="${OUT_RAW}.stderr.log"
: > "$OUT_RAW"
: > "$ERR_LOG"

if ! sudo -n true 2>/dev/null; then
  msg="[ERROR] sudo credential is not cached. Run 'sudo -v' in your terminal first."
  echo "$msg" >> "$ERR_LOG"
  echo "$msg" >&2
  exit 2
fi

run_try () {
  local samplers="$1"
  local use_extra="$2"

  echo "[TRY] samplers=${samplers} extra_power_info=${use_extra}" >> "$ERR_LOG"

  local cmd=(sudo -n powermetrics -i "${INTERVAL_MS}" -n "${SAMPLES}" -s "${samplers}")
  if [ "$use_extra" = "1" ]; then
    cmd+=(--show-extra-power-info)
  fi

  "${cmd[@]}" > "$OUT_RAW" 2>> "$ERR_LOG" || return 1
  return 0
}

ok=0
if [ "$ENABLE_EXTRA_POWER_INFO" = "1" ]; then
  run_try "cpu_power,gpu_power,thermal" 1 && ok=1 || true
  if [ "$ok" -eq 0 ]; then
    run_try "cpu_power,thermal" 1 && ok=1 || true
  fi
fi

# Fallback paths for compatibility.
if [ "$ok" -eq 0 ] || [ ! -s "$OUT_RAW" ]; then
  run_try "cpu_power,gpu_power,thermal" 0 && ok=1 || true
  if [ "$ok" -eq 0 ]; then
    run_try "cpu_power,thermal" 0 && ok=1 || true
  fi
  if [ "$ok" -eq 0 ]; then
    run_try "cpu_power" 0 && ok=1 || true
  fi
fi

bytes=$(wc -c < "$OUT_RAW" | tr -d ' ')
echo "[INFO] raw_bytes=${bytes}" >> "$ERR_LOG"
if [ "$ok" -eq 0 ] || [ "$bytes" -le 0 ]; then
  msg="[ERROR] powermetrics collection failed (no usable output). See ${ERR_LOG}"
  echo "$msg" >> "$ERR_LOG"
  echo "$msg" >&2
  exit 3
fi
