#!/bin/bash
# Expanse: module load singularitypro first
# Timings:  bash scripts/run_framework_comparison.sh
# Memory:    PARQUET_PATH=... bash scripts/run_framework_comparison.sh memory

set -euo pipefail
module load singularitypro

SIF="$HOME/esolares/singularity/spark_raydp.sif"
DIR="$(cd "$(dirname "$0")" && pwd)"
DATA="${PARQUET_PATH:-data/final_preprocessed}"

run_py() {
  singularity exec --bind /expanse,/scratch,/cvmfs,"$HOME" "$SIF" \
    python3 "$DIR/framework_comparison.py" --data "$DATA" "$@"
}

if [ "${1:-}" = "memory" ]; then
  echo "=== Spark ==="
  /usr/bin/time -v run_py --framework spark
  echo "=== Ray ==="
  /usr/bin/time -v run_py --framework ray
else
  run_py "$@"
fi
