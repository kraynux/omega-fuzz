# Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/).

## [1.5.0] — 2026-10-29

### Ajouté

- Interface en 17 langues (français, anglais, espagnol, portugais (Brésil), italien, allemand, néerlandais, polonais, russe, chinois simplifié, vietnamien, thaï, indonésien, japonais, coréen, hindi et arabe) : Réglages → « Langue / Language », appliquée après un redémarrage de l'interface ; variable `OMEGA_FUZZ_LANG` pour forcer une langue le temps d'une session. Lancé depuis omega-suite, l'outil prend la langue de la suite.
- Réglage « Langue des exports » (« Comme l'interface » par défaut) : les rapports HTML et texte s'écrivent dans la langue choisie ; en arabe, le rapport HTML se lit de droite à gauche. Les exports JSON et CSV restent des données (clés et valeurs inchangées).

### Modifié

- Accents rétablis dans tous les textes français de l'interface et des rapports.
- Les résultats enregistrés en français sont retraduits à l'affichage et dans les exports.
- La ligne de commande reste en français.
