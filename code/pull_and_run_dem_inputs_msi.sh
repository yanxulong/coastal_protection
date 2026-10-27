#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"
git pull --ff-only origin master
export COASTAL_PROTECTION_PROJECT_ROOT="$PROJECT_ROOT"
export COASTAL_PROTECTION_DEM_ROOT="${COASTAL_PROTECTION_DEM_ROOT:-$PROJECT_ROOT/data/raw/usgs_3dep_13arcsec_dem}"
python code/run.py --task download_coastal_dem_inputs
