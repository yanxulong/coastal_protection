#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"
git pull --ff-only origin master
mkdir -p output/logs data/raw/ccap_30m_all_vintages
export COASTAL_PROTECTION_CCAP_ROOT="$PROJECT_ROOT/data/raw/ccap_30m_all_vintages"
sbatch code/download_all_ccap_vintages.sbatch
