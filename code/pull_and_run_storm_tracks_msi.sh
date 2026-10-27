#!/usr/bin/env bash
# Pull code-only repository update, then download NHC storm tracks on MSI.
set -Eeuo pipefail

REPO_URL="https://github.com/yanxulong/coastal_protection.git"
BRANCH="${COASTAL_PROTECTION_BRANCH:-master}"
PROJECT_ROOT="${COASTAL_PROTECTION_PROJECT_ROOT:-$HOME/projects/coastal_protection}"

if [[ -d "$PROJECT_ROOT/.git" ]]; then
    git -C "$PROJECT_ROOT" pull --ff-only origin "$BRANCH"
elif [[ -e "$PROJECT_ROOT" ]]; then
    printf '[error] Project path exists but is not a Git checkout: %s\n' "$PROJECT_ROOT" >&2
    exit 2
else
    mkdir -p "$(dirname "$PROJECT_ROOT")"
    git clone --branch "$BRANCH" "$REPO_URL" "$PROJECT_ROOT"
fi

export COASTAL_PROTECTION_PROJECT_ROOT="$PROJECT_ROOT"
export PYTHONDONTWRITEBYTECODE=1
python3 "$PROJECT_ROOT/code/run.py" \
    --project-root "$PROJECT_ROOT" \
    --task download_nhc_storm_tracks \
    --start-year 1996 \
    --end-year 2026
