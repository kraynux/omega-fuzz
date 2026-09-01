<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->
<div align="center">
  <img src="docs/assets/omega-fuzz.png" alt="Omega-Fuzz" width="256">
</div>

# 🗱 OMEGA-FUZZ

**Scanneur de vulnérabilité**

> Élaboré par **kraynux** pour **Omega-server** 
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Page officielle : [OMEGA-FUZZ](https://kraynux.snake-mackarel.ts.net/omega-fuzz/) &nbsp; Aperçu : [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-fuzz/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**Omega-Fuzz** est une application locale en terminal (TUI [Textual](https://github.com/Textualize/textual) + CLI scriptable) qui pilote des decouverte et tests de securite web (fuzzing HTTP) pour environnements autorises (labs, mirroirs personnels, engagements de test explicitement consentis).

Sixième outil de la suite `omega-` (après `omega-scan`, `omega-stress`, `omega-check`, `omega-deep` et `omega-fold`), structuré en Clean Architecture — voir `docs/ARCHITECTURE.md` pour le détail technique complet.

## 1. Vision et périmètre

### Ce que fait Omega-Fuzz

- Découvre le périmètre d'une cible unique en BFS borné par un scope explicite (schéma/sous-domaines/chemins autorisés-bloqués/profondeur), jamais sans garde-fous.
- Fuzz générique des paramètres de query string, des en-têtes HTTP et des formulaires `GET` trouvés sur chaque URL découverte, et vérifie trois familles de signatures : XSS réfléchi non destructif, injection générique (détection d'erreur en réponse), en-têtes de sécurité manquants/mal configurés — voir [§5](#5-tests-de-sécurité-exécutés).
- Score chaque anomalie sur 3 axes (impact/exploitabilité/portée) et en déduit une sévérité (`low`/`medium`/`high`/`critical`), dédupliquée par `(type, endpoint, paramètre)` en conservant la meilleure preuve — voir [§6](#6-score-et-sévérité).
- Prend en charge l'authentification (cookie, bearer token, formulaire de login) via un fichier YAML dédié, jamais d'identifiants en clair sur la ligne de commande.
- Restitue le résultat en TUI (Textual) ou en CLI scriptable, avec trois exports (JSON, Markdown, HTML 5 thèmes).
- Conserve un historique persistant des scans et de leurs findings (SQLite), et une liste de cibles favorites réutilisables.
- Exige une confirmation explicite (phrase stricte pour les cas les plus sensibles) avant tout scan agressif, étendu, ou avec vérification TLS désactivée.

### Ce qu'Omega-Fuzz ne fait pas

- Fuzzing des corps JSON — le code existe (`plugins/fuzzers/json_body_fuzzer.py`) mais n'est pas câblé (la découverte HTML/BFS ne produit aucun schéma d'API JSON, aucune source de template exploitable).
- Fuzzing des formulaires `POST`/`PUT`/`DELETE` — exclus par choix du pipeline automatique (risque d'écriture non désirée sur la cible) ; seuls les formulaires `GET` sont testés.
- Tests de logique métier (IDOR, contrôle d'autorisation, rupture de workflow) — le code existe (`plugins/logic_tests/`) mais reste hors du pipeline automatique, invocable séparément uniquement, jamais déclenché par un scan standard.
- Scan multi-cibles parallèle — une cible unique par scan.
- Rejeu, comparaison ou export depuis l'écran Historique — seuls `Scan` et `Finding` sont persistés (pas la configuration effective complète ni les requêtes), rejouer ou exporter à nouveau depuis l'historique fabriquerait des données ; l'écran l'explique plutôt que de le proposer en silence.
- Rendu JavaScript côté client (page récupérée telle que servie, pas exécutée dans un navigateur headless).
- Dashboard web.

## 2. Installation

### Prérequis

- Python 3.10+
- Connexion Internet, pour les dépendances
- Pour le TUI : une police [Nerd Font](https://www.nerdfonts.com/) installée dans le terminal, pour l'icône du header — sans elle, ce caractère se rend en carré vide (même limite qu'un emoji, mais bien plus largement disponible chez les utilisateurs de terminal). Absence sans conséquence sur le fonctionnement, purement cosmétique.

### Installation

```bash
[ -d omega-fuzz ] && echo "ℹ️ Déjà extrait ici, étape ignorée." || tar -xzf omega-fuzz.tar.gz
cd omega-fuzz/
chmod +x install.sh
./install.sh
```

`install.sh` :

1. Crée l'environnement virtuel `.venv` s'il n'existe pas déjà.
2. Installe les dépendances (`vendor/omega-lib/` puis `pip install -e .`, `pyproject.toml` reste l'unique source de vérité).
3. Rend `omega-fuzz.sh` et `install.sh` exécutables.
4. Ajoute l'alias `fuzz` à `~/.bashrc` et `~/.zshrc` (sans doublon si déjà présent).

### Dépendances

Déclarées dans `pyproject.toml` (pas de `requirements.txt`) :
- `omega-lib` : bibliothèque partagée de la suite (thèmes d'export, détection de terminal, `ConfidenceLevel`) — vendorisée dans `vendor/omega-lib/`
- `httpx` : requêtes HTTP asynchrones (découverte + fuzzing), streaming de la réponse (jamais de tampon complet en mémoire, même sur un fichier de plusieurs Go servi par la cible)
- `beautifulsoup4` + `lxml` : extraction des URLs et formulaires HTML
- `jinja2` : templating pour l'export HTML
- `textual` : interface TUI, thèmes, adaptation automatique au terminal
- `pyyaml` : chargement du fichier `--auth-config`
- Dépendances de développement (`pip install -e ".[dev]"`) : `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Utilisation

### Mode interactif (TUI)

Recommandé pour l'usage quotidien — lancé sans argument :

```bash
./omega-fuzz.sh
```
si vous avez créé l'alias, tapez juste `fuzz` dans le terminal :
```bash
fuzz
```

Parcours : écran de démarrage (se ferme sur une touche ou un clic) → menu principal (Scanner / Cibles / Réglages / Historique / Aide) → saisie de la cible (URL complète, schéma `http://`/`https://` obligatoire), preset ou configuration manuelle (scope + agressivité), authentification optionnelle, vérification TLS, surcharges de limites → écran de revue (confirmation simple, ou phrase stricte `OUI-J-AI-L-AUTORISATION` pour les cas sensibles) → scan (jauge indéterminée, bouton **Arrêter** à tout moment) → résultats (findings, export) → historique (détail d'un scan passé, findings associés) et cibles favorites depuis le menu principal. L'adaptation au terminal (couleurs, taille, dégradation structurelle) est automatique.

#### Raccourcis clavier

| Touche | Action |
|---|---|
| `↑` / `↓` | Naviguer entre les éléments d'un écran |
| `Tab` / `Maj+Tab` | Naviguer entre les champs d'un formulaire |
| `Échap` | Retour à l'écran précédent (confirmation de sortie sur l'accueil) |
| `t` | Thème suivant (appliqué immédiatement, sans confirmation) |
| `r` | Rafraîchir la détection du terminal |
| `a` | Afficher l'aide (tableau des presets inclus) |
| `q` | Quitter (avec confirmation) |
| `Ctrl+P` | Palette de commandes (Theme, Quitter, Screenshot) |

### Mode scriptable (CLI)

```bash
# Scan avec un preset prêt à l'emploi
./omega-fuzz.sh scan --target https://example.com --preset prod-safe

# Combinaison manuelle scope + agressivité (sans preset)
./omega-fuzz.sh scan --target https://example.com --scope-profile standard --aggressiveness standard

# Avec authentification (fichier YAML, jamais d'identifiants en clair sur la ligne de commande)
./omega-fuzz.sh scan --target https://example.com --preset staging-full --auth-config auth.yaml

# Dry-run : configuration effective et plan estimé, aucune requête émise
./omega-fuzz.sh scan --target https://example.com --preset prod-safe --dry-run

# Export ciblé (dossier, formats, thème HTML)
./omega-fuzz.sh scan --target https://example.com --preset prod-safe \
    --output-dir ./rapports --format html --export-theme omega-neon
```

Options de `scan` :

| Option | Défaut | Effet |
|---|---|---|
| `--target` | *(requis)* | URL cible, schéma `http://`/`https://` obligatoire (jamais complété automatiquement) |
| `--preset` | — | Preset prêt à l'emploi (voir [§4](#4-profils-de-scope-et-presets)) |
| `--scope-profile` | — | Profil de scope, à combiner avec `--aggressiveness`, sans `--preset` |
| `--aggressiveness` | — | Niveau d'agressivité, à combiner avec `--scope-profile`, sans `--preset` |
| `--auth-config` | — | Fichier YAML d'authentification |
| `--insecure-tls` | désactivé | Désactive la vérification TLS (déclenche la confirmation renforcée) |
| `--max-duration` | *(du profil)* | Surcharge la durée maximale (secondes) |
| `--max-requests` | *(du profil)* | Surcharge le nombre maximal de requêtes |
| `--max-tests` | *(du profil)* | Surcharge le nombre maximal de tests |
| `--max-concurrent` | *(du profil)* | Surcharge la concurrence maximale |
| `--dry-run` | désactivé | Affiche la configuration effective et le plan estimé, n'émet aucune requête |
| `--output-dir` | `var/exports/` | Dossier des rapports exportés, nommés `<preset>-<horodatage>.<ext>` (surchargeable dans Réglages) |
| `--format` | `all` | `json`, `markdown`, `html` ou `all` |
| `--export-theme` | `omega-base` | Thème du rapport HTML exporté (sans effet sur json/markdown) |

Il n'existe pas de sous-commande `history`/`show` côté CLI : l'historique et les cibles favorites sont uniquement consultables depuis le TUI.

Si l'alias a été créé par `install.sh`, `fuzz scan ...` fonctionne de partout dans le terminal, sans le préfixe `./omega-fuzz.sh`.

## 4. Profils de scope et presets

### Profils de scope

| Profil | Mode | Profondeur max | Restrictions |
|---|---|---|---|
| `strict` | cible exacte | 1 | Bloque `/health`, `/ready`, `/metrics`, `/favicon.ico`, `/robots.txt` |
| `standard` | + sous-domaines | 2 | Bloque sous-domaines statiques usuels, chemins techniques, assets (images/css/js/fonts) |
| `large` | + sous-domaines | 4 | Bloque uniquement les chemins techniques et assets (dont archives/PDF) |
| `api` | cible exacte | 3 | Restreint à `/api`, `/v1`, `/v2` ; bloque documentation et assets |
| `custom` | + sous-domaines | 3 | Aucune restriction par défaut — base de départ pour une configuration manuelle |

Quel que soit le profil choisi, une liste d'extensions binaires/volumineuses (`.iso`, `.zip`, `.exe`, `.mp4`...) est **toujours** exclue du crawl et du fuzzing, même sous `custom` — un lien vers un fichier de ce type n'est jamais récupéré par une requête HTTP réelle, pour éviter qu'un dossier de téléchargements ne ralentisse un scan pendant de longues minutes.

### Niveaux d'agressivité

`doux` · `standard` · `agressif` · `violent` — chacun porte ses propres limites de base (durée, requêtes, tests, profondeur, concurrence), surchargées par un preset le cas échéant.

### Presets prêts à l'emploi

| Preset | Scope | Agressivité | Durée max | Requêtes max | Tests max | Profondeur max | Confirmation renforcée |
|---|---|---|---|---|---|---|---|
| `prod-safe` | strict | doux | 300 s | 1 000 | 500 | 1 | non |
| `staging-full` | standard | standard | 1 800 s | 20 000 | 10 000 | 2 | non |
| `lab-deep` | large | agressif | 3 600 s | 100 000 | 50 000 | 4 | non |
| `lab-extreme` | large | violent | 7 200 s | 500 000 | 250 000 | 5 | **oui** |
| `api-hardened` | api | agressif | 1 800 s | 50 000 | 25 000 | 3 | non |

Un scan est bloqué tant qu'il n'est pas confirmé. Confirmation **renforcée** (phrase exacte `OUI-J-AI-L-AUTORISATION` à saisir) exigée dès que l'un de ces trois facteurs est présent : agressivité `violent`, preset `lab-extreme`, ou vérification TLS désactivée (`--insecure-tls`) — combinaison inhabituelle sans l'un de ces trois facteurs, confirmation simple oui/non.

## 5. Tests de sécurité exécutés

Pipeline automatique, sur chaque URL découverte dans le scope (et chaque formulaire `GET` qui y est trouvé) :

| Test | Déclenchement | Ce qui est vérifié |
|---|---|---|
| Fuzzing générique de paramètre | tout paramètre de query string | Comportement de la cible face à des valeurs limites/malformées |
| Fuzzing de headers | une fois par URL, 4 en-têtes fixes (`User-Agent`, `Referer`, `X-Forwarded-For`, `Accept-Language`) | Comportement de la cible face à des valeurs limites/malformées dans un en-tête |
| Fuzzing de formulaire (`GET` uniquement) | tout champ de formulaire `GET` découvert dans le scope | Comportement de la cible face à des valeurs limites/malformées dans un champ de formulaire |
| XSS réfléchi | tout paramètre de query string | Réflexion non filtrée d'un payload dans la réponse (non destructif) |
| Injection générique | tout paramètre de query string | Détection d'erreur serveur en réponse à un payload d'injection (pas de fingerprint SQL/NoSQL spécifique) |
| En-têtes de sécurité | une fois par URL | En-têtes de sécurité manquants ou mal configurés dans la réponse |

Les trois premiers tests (fuzzing générique de paramètre/headers/formulaire) sont un moteur de mutation **sans détection** — ils ne produisent jamais de `Finding` directement, seules les erreurs serveur (5xx) rencontrées sont comptabilisées sur le `Test` correspondant. Seules les signatures (XSS, injection, en-têtes de sécurité) génèrent des findings.

## 6. Score et sévérité

Chaque anomalie détectée est notée sur 3 axes (`impact`, `exploitabilité`, `portée`, 1 à 5 chacun) selon la nature de l'observation — mapping délibérément **conservateur** (bas de fourchette, aucune confirmation humaine à ce stade automatique) :

| Score brut (somme des 3 axes) | Sévérité |
|---|---|
| ≥ 13 | `critical` |
| ≥ 10 | `high` |
| ≥ 7 | `medium` |
| < 7 | `low` |

Un ajustement manuel (`severity_override`) reste possible mais exige toujours une justification explicite. Les findings équivalents (même type, même endpoint, même paramètre) sont dédupliqués, en conservant la meilleure preuve disponible (niveau de confiance `omega_lib.core.confidence.ConfidenceLevel`, puis score brut en cas d'égalité).

## 7. Authentification

Fichier YAML dédié (`--auth-config`), jamais d'identifiants en clair sur la ligne de commande :

| Mode | Effet |
|---|---|
| `none` | Aucune authentification (défaut) |
| `cookie` | Cookie de session fourni directement |
| `bearer_token` | Jeton `Authorization: Bearer ...` |
| `login_form` | Authentification par formulaire (URL de login, champs utilisateur/mot de passe) |

## 8. Architecture

Omega-Fuzz est structuré en **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), alignée sur le gabarit de la suite `omega-` (voir `omega-check`/`omega-deep`/`omega-fold`) et vérifiée par `import-linter` à chaque modification. Le détail complet vit dans **`docs/ARCHITECTURE.md`**.

Vue d'ensemble très courte :

```text
src/omega_fuzz/
├── domain/          Logique métier pure (cibles/scope, requêtes, tests, findings, profils, rapports...)
├── application/     Cas d'usage (commands/queries) et orchestrateurs (découverte, scan, rapport, limites)
├── ports/           Contrats attendus par l'application (http_client, repositories, exporters...)
├── infrastructure/  Implémentations concrètes (httpx, BeautifulSoup, SQLite, exporteurs Jinja2 — Textual n'est PAS ici)
├── interfaces/      tui/ (Textual) et cli/ (scriptable), à parité fonctionnelle stricte
├── plugins/         Fuzzers et signatures (fonctions pures, jamais d'accès réseau direct)
├── app/             Assemblage (Container, composition root, cycle de vie)
└── core/            Vocabulaire transverse, erreurs, constantes
```

Règles de conception :
- `plugins/fuzzers/` et `plugins/signatures/` : fonctions pures qui construisent des plans de test (`Test` + `ScanRequest`), ne touchent jamais `HttpClient`.
- `infrastructure/network/` : fait le réseau (`httpx`, streaming borné en mémoire), ne juge jamais.
- `infrastructure/analyzers/` : lit une réponse déjà reçue, produit des `Observation` structurées, ne recalcule jamais un score.
- `interfaces/` : affiche, ne contient aucune logique métier.

## 9. Exports

Les rapports sont générés dans `var/exports/` par défaut (chemin runtime ancré sur le dossier du projet, `$OMEGA_FUZZ_VAR_DIR` pour le surcharger, surchargeable aussi dans l'écran Réglages), ou au chemin indiqué (`--output-dir`). Nom de fichier plat, sans sous-dossier : `<preset>-<horodatage>.<ext>` (ex. `prod-safe-2026-09-01_14-30-22.html`).

### JSON, source de vérité

Structure complète du rapport (configuration effective, statistiques, tests, findings), strictement JSON-sérialisable.

### Markdown, rapport humain compact

Lisible hors terminal, sans codes ANSI.

### HTML, rapport web autonome

5 thèmes au choix (`--export-theme` en CLI, sélecteur en TUI) : `omega-base`, `omega-burn`, `omega-neon`, `light-basic`, `light-alt`.

## 10. Historique et cibles favorites

Chaque scan est persisté (SQLite, `var/db/omega-fuzz.db`) avec ses findings, consultable depuis l'écran Historique du TUI. Seuls `Scan` et `Finding` sont stockés — pas la configuration effective ni les requêtes détaillées — donc pas de rejeu, de comparaison ni de nouvel export depuis cet écran (l'écran l'explique plutôt que de fabriquer des données).

L'écran **Cibles** conserve une liste de favoris (URLs normalisées, `var/targets.json`), réutilisable pour préremplir directement le champ Cible d'un nouveau scan.

## 11. Captures d'écran

Commande **Screenshot** de la palette (`Ctrl+P`) : enregistre un SVG de l'écran TUI courant dans `var/screenshots/` par défaut, surchargeable dans l'écran Réglages (comme le dossier d'export). Purge dédiée disponible dans Réglages.

## 12. Compatibilité terminaux

Le TUI (Textual) détecte automatiquement les capacités du terminal (émulateur, taille) et adapte sa feuille de style structurelle en conséquence (`complete`/`standard`/`reduced`/`mono`), sans flag manuel. Le mode CLI reste toujours en texte simple, indépendant du terminal. Politique partagée par toute la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Profil selon l'émulateur détecté

| Émulateur | Profil initial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderne | `reduced` |
| TTY Linux, SSH legacy | `mono` |
| Émulateur non reconnu | `reduced` (repli par défaut) |

### Profil selon la taille du terminal

| Taille minimale (colonnes × lignes) | Plafond de profil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| en dessous | `mono` |

Le profil final retenu est **le plus restrictif des deux** (émulateur et taille) — rafraîchissable en direct par la touche `r`.

## 13. Tests

```bash
source .venv/bin/activate
lint-imports        # verifie la Dependency Rule (6 contrats)
pytest -q           # 317 tests
ruff check src tests
mypy -p omega_fuzz
```

Structure : `tests/unit/` (domaine et application, sans I/O réelle), `tests/integration/` (vrai filesystem via `tmp_path`, serveur HTTP factice `pytest-httpserver`, vraie base SQLite, CLI de bout en bout), `tests/tui/` (navigation via `Pilot`, structurel — pas de vérification visuelle auto-revendiquée).

## 14. Hors périmètre

- Fuzzing des corps JSON (code présent, non câblé — aucune découverte de schéma d'API)
- Fuzzing des formulaires `POST`/`PUT`/`DELETE` (exclus par choix, risque d'écriture)
- Tests de logique métier (IDOR, autorisation, workflow) hors invocation manuelle
- Scan multi-cibles simultané
- Rejeu, comparaison ou export depuis l'historique
- Rendu JavaScript côté client
- Dashboard web

---

> Omega-Fuzz — Découvrir un périmètre, le tester avec des garde-fous explicites, jamais deviner ce qui n'a pas été confirmé.
