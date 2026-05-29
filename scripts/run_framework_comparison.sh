#!/bin/bash

set -euo pipefail

SIF="${SIF:-$HOME/esolares/singularity/spark_raydp.sif}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_PATH="${1:-${PARQUET_PATH:-data/final_preprocessed}}"

if [[ ! -f "$SIF" ]]; then
  echo "Missing container: $SIF" >&2
  echo "Use ~/esolares/singularity/spark_raydp.sif (not singularity_images/)." >&2
  exit 1
fi

echo "Container: $SIF"
echo "Data:      $DATA_PATH"
echo "Script:    $SCRIPT_DIR/framework_comparison.py"
echo

run_python() {
  singularity exec \
    --bind /expanse,/scratch,/cvmfs,"$HOME" \
    "$SIF" \
    python "$SCRIPT_DIR/framework_comparison.py" --data "$DATA_PATH"
}

if [[ "${USE_TIME_V:-0}" == "1" ]] && command -v /usr/bin/time >/dev/null 2>&1; then
  echo "Running with /usr/bin/time -v (see Max resident set size below)"
  /usr/bin/time -v singularity exec \
    --bind /expanse,/scratch,/cvmfs,"$HOME" \
    "$SIF" \
    python "$SCRIPT_DIR/framework_comparison.py" --data "$DATA_PATH"
else
  run_python
fi
