#!/bin/bash
set -euo pipefail

DUR="${1:?duration_s}"
TRACE_OUT="${2:?trace_out.trace}"
EXPORT_OUT="${3:?export_out_path}"
TEMPLATE="${4:-Time Profiler}"

mkdir -p "$(dirname "$TRACE_OUT")"
mkdir -p "$(dirname "$EXPORT_OUT")"

ERR_LOG="${EXPORT_OUT}.stderr.log"
: > "$ERR_LOG"

# Phase 1: capture Instruments trace
xcrun xctrace record \
  --template "${TEMPLATE}" \
  --time-limit "${DUR}s" \
  --output "${TRACE_OUT}" \
  2> "$ERR_LOG"

# Phase 2: export trace to a text-parseable artifact (XML/plist style content)
xcrun xctrace export \
  --input "${TRACE_OUT}" \
  --output "${EXPORT_OUT}" \
  2>> "$ERR_LOG"
