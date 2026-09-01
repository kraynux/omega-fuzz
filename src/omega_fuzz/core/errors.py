# Copyright (c) 2026 kraynux - Licence MIT
"""Racine absolue des exceptions du projet (OMEGA-FUZZ_ARBORESCENCE.md
§5.3). Meme motif que le reste de la suite (D-007) : chaque couche a sa
propre racine (`domain/errors.py::DomainError`,
`application/exceptions.py::ApplicationError`, etc.), toutes derivees de
celle-ci — un `except OmegaFuzzError` generique attrape donc toute erreur
du projet, quelle que soit sa couche d'origine.

Les erreurs metier specifiques (scope, limites, findings...) restent
dans `domain`."""
from __future__ import annotations


class OmegaFuzzError(Exception):
    """Racine absolue des erreurs omega-fuzz."""


class ConfigurationError(OmegaFuzzError):
    """Configuration invalide ou incomplete (chemins, variables
    d'environnement, catalogues de signatures malformes)."""


class ValidationError(OmegaFuzzError):
    """Donnee fournie par l'utilisateur invalide (ex. regex de scope
    invalide au chargement)."""


class DependencyError(OmegaFuzzError):
    """Dependance externe indisponible ou mal configuree."""


class SerializationError(OmegaFuzzError):
    """Echec de (de)serialisation d'un modele generique."""
