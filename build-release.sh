#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Construit l'archive distribuable omega-fuzz.tar.gz : copie le projet
# (sans artefacts dev/runtime), vendore omega-lib (dependance obligatoire
# non publiee sur PyPI, voir install.sh) a partir de la source canonique
# plutot que de la copie deja presente dans le depot (peut etre en retard),
# archive le tout dans ../dist/. Meme convention que omega-serv/omega-track
# (build-release.sh). Outil de maintenance, jamais lui-meme inclus dans
# l'archive generee.
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OMEGA_LIB_SRC="${OMEGA_LIB_SRC:-$HOME/DEV/LIB/omega-lib}"
DIST_DIR="${DIST_DIR:-$PROJECT_ROOT/../dist}"
ARCHIVE_NAME="omega-fuzz.tar.gz"

if [ ! -d "$OMEGA_LIB_SRC" ]; then
    err "omega-lib introuvable : $OMEGA_LIB_SRC (definissez OMEGA_LIB_SRC si le chemin differe)."
    exit 1
fi

STAGING_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGING_DIR"' EXIT
DEST="$STAGING_DIR/omega-fuzz"
mkdir -p "$DEST"

info "Copie du projet omega-fuzz..."
rsync -a \
    --exclude='.venv/' --exclude='venv/' \
    --exclude='__pycache__/' --exclude='*.pyc' \
    --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' \
    --exclude='.import_linter_cache/' --exclude='*.egg-info/' \
    --exclude='.git/' --exclude='.claude/' \
    --exclude='docs/assets/' \
    --exclude='var/db/*' --exclude='var/exports/*' --exclude='var/screenshots/*' \
    --exclude='var/settings.json' --exclude='var/declaration.json' --exclude='var/targets.json' --exclude='var/*.log' \
    --exclude='vendor/' \
    --exclude='*~' --exclude='*.bak' --exclude='*.swp' \
    --exclude='.coverage' --exclude='htmlcov/' \
    --exclude='build-release.sh' --exclude='omega-fuzz.tar.gz' --exclude='dist/' \
    "$PROJECT_ROOT/" "$DEST/"

info "Vendoring d'omega-lib (dependance obligatoire, non publiee sur PyPI)..."
mkdir -p "$DEST/vendor/omega-lib"
rsync -a \
    --exclude='.venv/' --exclude='__pycache__/' --exclude='*.pyc' \
    --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' \
    --exclude='*.egg-info/' --exclude='.git/' --exclude='tests/' --exclude='*~' \
    "$OMEGA_LIB_SRC/" "$DEST/vendor/omega-lib/"

# Langues de l'interface et des exports (OMEGA-SUITE_PLAN-DETAILLE_I18N.md, lot N+1) : chaque
# .po de l'archive (outil, omega-lib vendoree et son catalogue partage) est recompile en .mo
# depuis sa source - jamais un .mo plus ancien que son .po ; .po et .pot ne sont pas livres.
if find "$DEST" -name '*.po' -path '*/LC_MESSAGES/*' | grep -q .; then
    if ! command -v msgfmt > /dev/null; then
        err "msgfmt introuvable (paquet gettext) : impossible de compiler les langues."
        exit 1
    fi
    info "Compilation des langues..."
    while IFS= read -r po; do
        msgfmt --check -o "${po%.po}.mo" "$po" || { err "Catalogue invalide : $po"; exit 1; }
        rm -f "$po"
    done < <(find "$DEST" -name '*.po' -path '*/LC_MESSAGES/*')
    find "$DEST" -name '*.pot' -path '*/locale/*' -delete
fi

info "Archivage..."
mkdir -p "$DIST_DIR"
tar -C "$STAGING_DIR" -czf "$DIST_DIR/$ARCHIVE_NAME" omega-fuzz

ok "Archive generee : $DIST_DIR/$ARCHIVE_NAME"
echo "sha256sum :"
sha256sum "$DIST_DIR/$ARCHIVE_NAME"
