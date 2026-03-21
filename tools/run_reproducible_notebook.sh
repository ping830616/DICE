#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: tools/run_reproducible_notebook.sh [options]

Create or refresh the pinned Conda environment, verify the notebook runtime,
and execute dice_results_analysis.ipynb headlessly.

Options:
  --ref <git-ref>             Check out an exact git ref before running.
  --env-name <name>           Conda environment name to use (default: dice-results).
  --dataset-root <path>       Dataset root, absolute or relative to repo root.
  --output-notebook <path>    Executed notebook path, absolute or relative to repo root.
  --skip-env-update           Do not create or update the Conda environment.
  --skip-preflight            Do not run tools/check_notebook_environment.py.
  --help                      Show this help text.
EOF
}

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

ENV_NAME="dice-results"
DATASET_ROOT_REL="data generation/dataset/ITC_M2Pro_DATA"
OUTPUT_NOTEBOOK_REL="ci_artifacts/dice_results_analysis.executed.ipynb"
TARGET_REF=""
SKIP_ENV_UPDATE=0
SKIP_PREFLIGHT=0

resolve_path() {
  local raw_path="$1"
  if [[ "$raw_path" = /* ]]; then
    printf '%s\n' "$raw_path"
  else
    printf '%s\n' "$REPO_ROOT/$raw_path"
  fi
}

repo_clean_for_checkout() {
  git -C "$REPO_ROOT" diff --quiet
  git -C "$REPO_ROOT" diff --cached --quiet
  [[ -z "$(git -C "$REPO_ROOT" ls-files --others --exclude-standard)" ]]
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ref)
      TARGET_REF="${2:-}"
      shift 2
      ;;
    --env-name)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --dataset-root)
      DATASET_ROOT_REL="${2:-}"
      shift 2
      ;;
    --output-notebook)
      OUTPUT_NOTEBOOK_REL="${2:-}"
      shift 2
      ;;
    --skip-env-update)
      SKIP_ENV_UPDATE=1
      shift
      ;;
    --skip-preflight)
      SKIP_PREFLIGHT=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! command -v conda >/dev/null 2>&1; then
  echo "error: conda was not found on PATH." >&2
  exit 1
fi

if [[ -n "$TARGET_REF" ]]; then
  if ! git -C "$REPO_ROOT" rev-parse --verify "${TARGET_REF}^{commit}" >/dev/null 2>&1; then
    echo "error: git ref '$TARGET_REF' is not available in this clone." >&2
    echo "hint: run 'git fetch origin' first if you expect it to exist remotely." >&2
    exit 1
  fi
  CURRENT_HEAD=$(git -C "$REPO_ROOT" rev-parse HEAD)
  TARGET_HEAD=$(git -C "$REPO_ROOT" rev-parse "${TARGET_REF}^{commit}")
  if [[ "$CURRENT_HEAD" != "$TARGET_HEAD" ]]; then
    if ! repo_clean_for_checkout; then
      echo "error: repository has uncommitted changes, so refusing to check out '$TARGET_REF'." >&2
      exit 1
    fi
    git -C "$REPO_ROOT" checkout "$TARGET_REF"
  fi
fi

DATASET_ROOT=$(resolve_path "$DATASET_ROOT_REL")
OUTPUT_NOTEBOOK=$(resolve_path "$OUTPUT_NOTEBOOK_REL")
OUTPUT_DIR=$(dirname "$OUTPUT_NOTEBOOK")
OUTPUT_NAME=$(basename "$OUTPUT_NOTEBOOK")

export PYTHONHASHSEED=0
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

echo "Repo root         : $REPO_ROOT"
echo "Git commit        : $(git -C "$REPO_ROOT" rev-parse HEAD)"
echo "Conda environment : $ENV_NAME"
echo "Dataset root      : $DATASET_ROOT"
echo "Output notebook   : $OUTPUT_NOTEBOOK"

if [[ "$SKIP_ENV_UPDATE" -eq 0 ]]; then
  if conda env list | awk 'NF && $1 !~ /^#/ {gsub(/\*/, "", $1); print $1}' | grep -Fx "$ENV_NAME" >/dev/null 2>&1; then
    echo "Updating pinned environment..."
    conda env update -n "$ENV_NAME" -f "$REPO_ROOT/environment.yml" --prune
  else
    echo "Creating pinned environment..."
    conda env create -n "$ENV_NAME" -f "$REPO_ROOT/environment.yml"
  fi
fi

if [[ "$SKIP_PREFLIGHT" -eq 0 ]]; then
  echo "Running environment preflight..."
  conda run -n "$ENV_NAME" python "$REPO_ROOT/tools/check_notebook_environment.py" \
    --repo-root "$REPO_ROOT" \
    --dataset-root "$DATASET_ROOT" \
    --report-path "$OUTPUT_DIR/notebook_environment_report.json"
fi

mkdir -p "$OUTPUT_DIR"

echo "Executing notebook..."
conda run -n "$ENV_NAME" jupyter nbconvert \
  --to notebook \
  --execute "$REPO_ROOT/dice_results_analysis.ipynb" \
  --output "$OUTPUT_NAME" \
  --output-dir "$OUTPUT_DIR" \
  --ExecutePreprocessor.timeout=-1

echo "Completed notebook run."
