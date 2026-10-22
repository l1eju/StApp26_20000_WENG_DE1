# Storyboard : Face au froid

**Public :** équipes territoriales (collectivités, Enedis).
**Message principal :** **À confirmer avec les données.** Les titres d'insight ci-dessous sont des hypothèses à valider ou corriger après l'analyse.

Navigation de l'application : 5 pages, une idée par page, un titre d'une phrase en tête de chaque page.

---

## Page 1 : Intro (hook et contexte)

- **Titre (hook) :** quand la température baisse d'un degré, tous les territoires ne consomment pas pareil.
- **Contenu :** définition de la part thermosensible, de la thermosensibilité (kWh par DJU) et des DJU. Périmètre : EPCI, 2011 à 2025. Rappel que la thermosensibilité concerne le secteur Résidentiel.
- **Interaction :** un encadré « méthodes et définitions » dépliable.

## Page 2 : Vue d'ensemble

- **Titre :** [hypothèse] la consommation évolue-t-elle différemment selon les secteurs depuis 2011 ?
- **Sidebar :** plage d'années, région(s), secteur, métrique.
- **KPI (liés aux filtres) :** consommation totale (GWh), part thermosensible moyenne (Résidentiel), taux de chauffage électrique moyen, nombre d'EPCI affichés.
- **Visuel 1 :** courbe de la consommation par grand secteur, 2011-2025, avec une annotation sur la rupture de série de 2018.
- **Visuel 2 :** écart de DJU par année (réalisés moins normaux), pour voir les hivers plus froids ou plus doux que la normale.

## Page 3 : Explorer les territoires

- **Titre :** [hypothèse] la dépendance au froid varie fortement d'un territoire à l'autre.
- **Visuel 3 :** carte de la part thermosensible **par département**, pour une année choisie (fond de carte déjà dans `assets/`, Licence ouverte). Les classements et le nuage de points restent au niveau EPCI.
- **Visuel 4 :** top et bottom 10 des EPCI.
- **Visuel 5 :** petits multiples par région, évolution dans le temps.
- **Visuel 6 :** nuage de points part thermosensible contre taux de chauffage électrique (taille = habitants), pour tester les hypothèses, avec la mention « corrélation n'est pas causalité ».
- **Interaction :** année, région, classe de part thermosensible, infobulles sur tous les graphiques.

## Page 4 : Qualité des données

- **Titre :** ce que les données disent, et ce qu'elles ne disent pas.
- **Contenu :** valeurs manquantes par colonne et par secteur, doublons, contrôles de validité (valeurs négatives, plages plausibles), rupture de 2018, secret statistique, évolution des codes EPCI.

## Page 5 : Conclusions

- **Titre :** **À compléter** (insight principal en une phrase).
- **Contenu :** 3 insights chiffrés, implications (priorisation de la rénovation, pointes hivernales, flexibilité), prochaines étapes, limites.

---

## Accessibilité et style

- Tous les axes sont nommés avec leurs unités.
- Palette lisible pour les daltoniens.
- Une courte description textuelle sous chaque graphique (équivalent du texte alternatif).
- Source et licence citées en en-tête de l'application.

## Plan de la vidéo (2 à 4 minutes)

| Temps | Contenu |
|---|---|
| 0:00 à 0:30 | Hook et question |
| 0:30 à 1:15 | Vue d'ensemble et filtres |
| 1:15 à 2:30 | Carte, classements, hypothèses |
| 2:30 à 3:15 | Qualité des données et limites |
| 3:15 à 3:45 | Conclusions et implications |
