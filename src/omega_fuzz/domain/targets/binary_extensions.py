# Copyright (c) 2026 kraynux - Licence MIT
"""Extensions de fichiers volumineux/binaires jamais interessantes a
parcourir ou a fuzzer (bug reel rapporte : l'application semble figee
sur un dossier d'une centaine de fichiers `.iso` — pas un probleme de
memoire, deja corrige par le streaming borne de `httpx_http_client.py`,
mais de TEMPS : chaque fichier etait quand meme telecharge jusqu'au
plafond de `max_response_body_size` avant d'etre tronque, requete apres
requete, y compris pour le fuzzing de headers/query string qui ne
regarde jamais le contenu). Applique de facon inconditionnelle dans
`domain.services.scope_service._check_path`, quel que soit le profil de
scope choisi — meme esprit que `domain.profiles.hard_caps` (un plancher
de securite, jamais desactivable par un profil permissif) — en plus,
jamais a la place, des `blocked_url_patterns` propres a chaque profil
(qui restent, eux, configurables)."""
from __future__ import annotations

import re

_NON_CRAWLABLE_EXTENSIONS = (
    # Images disque
    "iso", "img", "dmg", "vhd", "vhdx",
    # Archives
    "zip", "rar", "7z", "tar", "gz", "tgz", "bz2", "xz",
    # Executables / installeurs
    "exe", "msi", "deb", "rpm", "apk", "bin",
    # Video
    "mp4", "mkv", "avi", "mov", "wmv", "flv", "webm",
    # Audio
    "mp3", "wav", "flac", "ogg",
)

BLOCKED_EXTENSIONS_PATTERN = re.compile(
    r".*\.(" + "|".join(_NON_CRAWLABLE_EXTENSIONS) + r")$", re.IGNORECASE
)
