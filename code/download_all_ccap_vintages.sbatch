#!/usr/bin/env bash
#SBATCH --job-name=coastal-ccap
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=08:00:00
#SBATCH --output=output/logs/ccap-all-%j.out
#SBATCH --error=output/logs/ccap-all-%j.err
#SBATCH --export=ALL

set -euo pipefail
PROJECT_ROOT="${SLURM_SUBMIT_DIR:-$HOME/projects/coastal_protection}"
cd "$PROJECT_ROOT"
export COASTAL_PROTECTION_PROJECT_ROOT="$PROJECT_ROOT"
export COASTAL_PROTECTION_CCAP_ROOT="${COASTAL_PROTECTION_CCAP_ROOT:-$PROJECT_ROOT/data/raw/ccap_30m_all_vintages}"

module load miniforge
PYTHON="$HOME/.mamba/envs/msi_env/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON=python
fi
"$PYTHON" code/run.py --task download_all_ccap_vintages
