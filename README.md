# Ramdam Games

Le site du studio : une page par jeu et le journal de développement de chacun.

Le site publié est le dossier `docs/`, généré par `tools/build.py` à partir de `content/`.

- `content/games.json` : textes, images et fiches des jeux.
- `content/journal/<jeu>.json` : notes de version. Le workflow `Journal` les remplit tout seul toutes les deux heures à partir des commits des dépôts des jeux (`feat` donne une nouveauté, `fix` une correction, `perf`, `style`, `ui` et `ux` une amélioration, le reste compte comme technique). Une version marquée `"edited": true` a été réécrite à la main et n'est plus touchée.
- `tools/prep_media.py` : copie et compresse les captures depuis les projets des jeux.

En local :

```
python tools/sync_journal.py
python tools/build.py
python -m http.server 8765 --directory docs
```
