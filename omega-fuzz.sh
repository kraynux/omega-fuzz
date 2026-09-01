#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Script de lancement - OMEGA-FUZZ TUI/CLI
# Aucun privilege particulier requis : Omega-Fuzz ne fait que des requetes
# HTTP sortantes en tant qu'utilisateur normal, vers des cibles explicitement
# autorisees par l'utilisateur.
# Dispatch TUI (sans argument) / CLI (avec argument) gere par __main__.py,
# meme patron que omega-check/omega-deep/omega-fold.
# ==============================================================================

set -e
# Couleurs (mêmes conventions que les autres scripts de la suite omega-)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${WHITE}${NC}"
echo -e "${WHITE}DÉMARRAGE DE L'APPLICATION${NC}"
echo -e "${WHITE}${NC}"
echo -e "${WHITE}    ░▒▓█████████████████████▓▒░${NC}"
echo -e "${WHITE}    ░▒▓ Ω M E G A - F U Z Z ▓▒░${NC}"
echo -e "${WHITE}    ░▒▓█████████████████████▓▒░${NC}"
echo -e "${WHITE}${NC}"

# Determiner le repertoire ou se trouve ce script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# 1. Verifier que le venv existe
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Environnement virtuel introuvable : $VENV_DIR"
    echo ""
    echo "Lancez d'abord : $SCRIPT_DIR/install.sh"
    exit 1
fi

# 2. Verification robuste : tester si le paquet est bien installe (mode editable)
# C'est beaucoup plus fiable que de verifier l'existence d'un dossier
if ! "$VENV_DIR/bin/python" -c "import omega_fuzz" 2>/dev/null; then
    echo "⚠️  Le venv semble incomplet, reinstallation..."
    "$VENV_DIR/bin/pip" install -q -e "$SCRIPT_DIR/vendor/omega-lib"
    "$VENV_DIR/bin/pip" install -q -e "$SCRIPT_DIR"
fi

# 3. Ancrer le repertoire runtime (base SQLite, exports, captures d'ecran) sur
# l'emplacement du script, jamais sur le repertoire courant du shell appelant
# (sans ca, lancer ./omega-fuzz.sh depuis des repertoires differents utilise
# des bases SQLite differentes a chaque fois : historique qui semble
# "disparaitre" alors qu'il est juste ecrit ailleurs — voir
# infrastructure/config/paths.py::resolve_var_dir())
export OMEGA_FUZZ_VAR_DIR="${OMEGA_FUZZ_VAR_DIR:-$SCRIPT_DIR/var}"

# 4. Activer le venv et lancer l'application (script console declare dans pyproject.toml)
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
exec omega-fuzz "$@"
