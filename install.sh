#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Script d'installation - OMEGA-FUZZ CLI
# À lancer depuis le dossier extrait de l'archive : cd omega-fuzz && ./install.sh
# Résilient : peut être relancé sans erreur si une étape a déjà été faite.
# Aucune étape ne nécessite les privilèges root (pas de groupe dédié, pas de
# setgid) : Omega-Fuzz s'exécute entièrement en utilisateur normal, ses
# fichiers runtime (var/) lui appartiennent donc déjà nativement.
# ==============================================================================

set -e

# Couleurs (mêmes conventions que les autres scripts de la suite omega-)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }
tip()  { echo -e "${WHITE}💡 $1${NC}"; }

echo -e "${WHITE}    ░▒▓████████████████████████████████████████████▓▒░${NC}"
echo -e "${WHITE}    ░▒▓ Ω M E G A - FUZZ — I N S T A L L A T I O N ▓▒░${NC}"
echo -e "${WHITE}    ░▒▓████████████████████████████████████████████▓▒░${NC}"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# -------------------------------------------------------------------------
# 1. Environnement virtuel Python
# -------------------------------------------------------------------------
if [ -d ".venv" ]; then
    info ".venv existe déjà, création ignorée."
else
    if ! python3 -m venv .venv 2>/tmp/omega-fuzz-venv-err.log; then
        err "Échec de la création de l'environnement virtuel."
        warn "Sur Debian/Ubuntu (et dérivées), le module venv n'est pas toujours inclus avec python3 de base."
        tip "Installez-le puis relancez ce script : sudo apt install python3-venv"
        cat /tmp/omega-fuzz-venv-err.log >&2
        rm -f /tmp/omega-fuzz-venv-err.log
        exit 1
    fi
    rm -f /tmp/omega-fuzz-venv-err.log
    ok "Environnement virtuel créé (.venv)."
fi

# -------------------------------------------------------------------------
# 2. Dépendances — pyproject.toml reste l'unique source de verite (pas de
#    requirements.txt separe a maintenir en double). omega-lib n'est pas
#    publie sur PyPI : embarque dans vendor/omega-lib/ (bibliotheque
#    partagee de la suite omega-, sans quoi `pip install -e .` echoue sur
#    une machine qui n'a pas ~/DEV/LIB/omega-lib).
# -------------------------------------------------------------------------
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -e "$SCRIPT_DIR/vendor/omega-lib"
pip install -q -e .
ok "Dépendances installées."

# -------------------------------------------------------------------------
# 3. Scripts exécutables
# -------------------------------------------------------------------------
chmod +x omega-fuzz.sh
chmod +x "$SCRIPT_DIR/install.sh"
ok "Scripts rendus exécutables."

# -------------------------------------------------------------------------
# 4. Alias (optionnel) — bash et zsh, quel que soit celui réellement utilisé.
#    Pas de sudo ici : Omega-Fuzz ne requiert aucun privilège root.
# -------------------------------------------------------------------------
ALIAS_LINE="alias fuzz=\"${SCRIPT_DIR}/omega-fuzz.sh\""

for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    rc_name="$(basename "$rc")"
    if grep -qxF "$ALIAS_LINE" "$rc" 2>/dev/null; then
        info "Alias déjà présent dans $rc_name."
    elif echo "$ALIAS_LINE" >> "$rc" 2>/dev/null; then
        ok "Alias ajouté à $rc_name."
    else
        warn "Impossible d'ajouter l'alias à $rc_name."
    fi
done

echo ""
ok "Installation terminée."
tip "Lancez Omega-Fuzz avec : ${SCRIPT_DIR}/omega-fuzz.sh (TUI) ou ${SCRIPT_DIR}/omega-fuzz.sh scan ... (CLI) — ou juste 'fuzz'/'fuzz scan ...' dans un nouveau terminal si l'alias vient d'être ajouté."
