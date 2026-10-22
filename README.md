# Face au froid : où la consommation d'électricité dépend-elle le plus de la température ?

Projet individuel de data storytelling avec Streamlit (#EFREIDataStories2026)
Auteure : Julie [NOM à compléter], EFREI Paris, majeure Data Engineering
Échéance : samedi 24 octobre 2026, 12h00

> Ce document sert de rapport. Les sections marquées **À compléter** seront remplies au fil de l'avancement du projet.

---

## 1. Résumé

**À compléter en fin de projet** (5 lignes maximum : question, données, 2 à 3 insights chiffrés, limites principales).

---

## 2. Public cible et question

**Public :** les équipes territoriales (collectivités, gestionnaires de réseau comme Enedis) qui doivent prioriser la rénovation énergétique et anticiper les pointes de consommation hivernales.

**Question principale :** où la consommation d'électricité est-elle la plus dépendante du froid, et qu'est-ce que cela implique pour la rénovation énergétique et la gestion des pointes hivernales ?

**Sous-questions :**

1. **Où ?** Quels EPCI ont la part thermosensible la plus élevée ?
2. **Pourquoi (hypothèses) ?** Le taux de chauffage électrique, le type et l'âge des logements, ou la rigueur de l'hiver (DJU) expliquent-ils les écarts ?
3. **Quand ?** Comment la consommation par secteur évolue-t-elle de 2011 à 2025, et les hivers plus froids ou plus doux que la normale s'y voient-ils ?
4. **Quelle inégalité ?** Les écarts entre territoires sont-ils importants et persistants ?

**Cadrage climatique :** le changement climatique est utilisé comme toile de fond uniquement. Les indicateurs du jeu de données sont des indicateurs d'hiver sur 15 ans : ils ne permettent pas de démontrer une hausse des extrêmes climatiques, ni d'étudier la climatisation en été.

---

## 3. Données

| Élément | Détail |
|---|---|
| Titre | Consommation et thermosensibilité d'électricité à la maille EPCI de 2011 à 2025 (par secteur d'activité) |
| Producteur | Enedis |
| Lien | https://opendata.enedis.fr/datasets/consommation-electrique-par-secteur-dactivite-epci |
| Licence | Licence Ouverte / Open Licence version 2.0 |
| Couverture temporelle | 1er janvier 2011 au 31 décembre 2025 |
| Mise à jour | annuelle (dernière mise à jour des données : 1er janvier 2026) |
| Volume | 502 422 enregistrements (consulté le 22 octobre 2026) |
| Documentation | note méthodologique sur la thermosensibilité et description du jeu de données (pièces jointes du portail) |

### Colonnes utilisées (d'après le schéma du portail)

| Groupe | Colonnes | Rôle |
|---|---|---|
| Territoire | `code_epci`, `nom_epci`, `type_epci`, `code_departement`, `code_region`, `nom_region` | filtres, carte, classements |
| Période | `annee` | évolution 2011-2025 |
| Secteur | `code_categorie_consommation` (RES, PRO, ENT), `code_grand_secteur` | comparaison des secteurs |
| Consommation | `nb_sites`, `conso_totale_mwh`, `conso_moyenne_mwh` | KPI et tendances |
| Thermosensibilité (Résidentiel) | `part_thermosensible`, `thermosensibilite_moyenne_kwh_dju`, `conso_moyenne_usages_thermosensibles_mwh`, `conso_moyenne_corrigee_de_l_alea_climatique_usages_thermosensibles_mwh` | cœur de l'histoire |
| Climat d'hiver | `dju_a_tr` (températures réalisées), `dju_a_tn` (températures normales) | hiver plus froid ou plus doux que la normale |
| Contexte logement | `nombre_d_habitants`, `taux_de_chauffage_electrique`, `taux_de_logements_collectifs`, répartition par période de construction et par superficie | hypothèses explicatives |
| Qualité | `nombre_de_mailles_secretisees` | suivi du secret statistique |

**À vérifier dans les données :** l'unité de `part_thermosensible` (pourcentage ou fraction) et la plage de valeurs de `taux_de_chauffage_electrique`.

---

## 4. Méthodologie

### 4.1 Chargement (code écrit, à valider sur les vraies données)
`utils/io.py` télécharge deux extractions ciblées plutôt que les 502 422 lignes x 43 colonnes :

- `residentiel` : secteur Résidentiel uniquement (thermosensibilité, DJU, logement), 29 colonnes ;
- `secteurs` : 9 colonnes, toutes les lignes, pour la consommation par secteur.

Chaque extraction est téléchargée une seule fois via l'API d'export d'Enedis, puis mise en cache en Parquet dans `data/raw/` (dossier exclu du dépôt). Voie de secours : un export CSV fait à la main depuis la vue Tableau, enregistré sous `data/raw/<nom>_manuel.csv`.

Le code a été testé sur un jeu **synthétique** reproduisant le schéma du portail (voie manuelle et voie API simulée localement). L'URL réelle de l'API n'a pas encore été testée.

**Carte :** par département (96 départements métropolitains), avec un fond de carte simplifié embarqué dans `assets/`. Choix de lisibilité et de légèreté par rapport à une carte par EPCI.

### 4.2 Nettoyage et validation (prévu)
Typage des colonnes, traitement des valeurs manquantes (voir section 6), dédoublonnage des EPCI à cheval sur plusieurs départements, contrôle de cohérence des codes EPCI, prise en compte de la rupture de série de 2018.

### 4.3 Variables dérivées (prévu)
- Écart climatique d'hiver : `dju_a_tr - dju_a_tn` (positif = hiver plus froid que la normale)
- Consommation résidentielle par habitant
- Classes de part thermosensible (quintiles) pour la carte et les classements

**À compléter** au fur et à mesure de l'implémentation.

---

## 5. Résultats et insights

**À compléter** après l'analyse (3 insights chiffrés, chacun relié à un graphique de l'application).

---

## 6. Qualité des données et limites

Points connus à ce stade (à enrichir avec le profilage réel des données) :

- **Valeurs manquantes structurelles :** les indicateurs de thermosensibilité sont décrits dans le schéma pour le secteur Résidentiel uniquement. Ils sont donc vides pour les autres catégories. La comparaison entre secteurs porte sur la consommation, pas sur la thermosensibilité.
- **Secret statistique :** certains agrégats ne sont pas affichés sous un seuil de sites actifs (règle de protection des données). Les manques correspondent à une protection, pas à une erreur.
- **Rupture de série en 2018 :** le découpage sectoriel change à partir de 2018. Les comparaisons de secteurs avant et après doivent être faites avec prudence.
- **EPCI à cheval sur plusieurs départements :** le total de l'EPCI peut être répété pour chaque département. Il faut dédoublonner avant toute somme.
- **Codes et noms EPCI :** le schéma indique 3 233 codes et 5 567 noms distincts sur 15 ans. Les périmètres et les noms évoluent, donc la comparaison d'un même EPCI dans le temps demande une vérification préalable.
- **Climat :** indicateurs d'hiver uniquement (DJU), pas de données d'été. Aucune donnée de production ni de réseau.
- **Carte par département :** elle agrège des données EPCI. Un EPCI à cheval sur plusieurs départements est compté dans chacun d'eux, et le fond de carte ne couvre que la métropole. Les codes département du jeu absents du fond de carte seront listés dans l'application.
- **Causalité :** les corrélations observées (par exemple chauffage électrique et part thermosensible) ne prouvent pas une relation de cause à effet.

---

## 7. Éthique et vie privée

Les données sont agrégées par Enedis avec application du secret statistique. Aucune réidentification n'est tentée. La licence est citée et les limites sont présentées dans l'application.

---

## 8. Structure du projet (proposée, en cours de validation)

```
StApp26_20000_NOM_XXX/
├─ app.py                  # point d'entrée : navigation, sidebar, appel des sections
├─ config.py               # constantes : URL, colonnes retenues, carte, chemins
├─ profile_data.py         # étape 1 : rapport de qualité des données brutes
├─ requirements.txt        # dépendances pinnées
├─ .gitignore              # exclut data/ et .venv/
├─ README.md               # ce rapport
├─ storyboard.md           # storyboard de l'application
├─ sections/
│  ├─ intro.py             # hook, contexte, définitions
│  ├─ overview.py          # KPI + tendances nationales
│  ├─ deep_dives.py        # carte, classements, petits multiples, hypothèses
│  ├─ data_quality.py      # manquants, doublons, contrôles, limites
│  └─ conclusions.py       # insights, implications, prochaines étapes
├─ utils/
│  ├─ io.py                # téléchargement via API + cache local
│  ├─ prep.py              # nettoyage, dédoublonnage, variables dérivées
│  └─ viz.py               # fonctions de graphiques au style cohérent
├─ data/                   # cache local (hors dépôt)
└─ assets/
   └─ departements.geojson # fond de carte des départements (IGN Admin Express, simplifié)
```

---

## 9. Installation et exécution

Python 3.11 ou plus récent recommandé (testé en 3.12.10).

```
python -m venv .venv            (py -3.12 -m venv .venv     Si comme moi, vous avez une version active trop récente à changer)
.venv\Scripts\activate          # Windows (si ça ne fonctionne pas exécuter d'abord : Set-ExecutionPolicy -Scope Process Bypass) (macOS/Linux : source .venv/bin/activate)
pip install -r requirements.txt
python profile_data.py          # étape 1 : télécharge les données et produit le rapport de qualité
streamlit run app.py            # à venir : l'application n'est pas encore codée
```

Au premier lancement, les données sont téléchargées dans `data/raw/` puis relues depuis le cache. Pour forcer un nouveau téléchargement : `python profile_data.py --refresh`.

---

## 10. Livrables et liens

- Application déployée : **À compléter**
- Dépôt de code : **À compléter**
- Vidéo de démonstration (2 à 4 minutes) : **À compléter**
- Storyboard : voir `storyboard.md`

---

## 11. Références

- Enedis Open Data, jeu de données « Consommation et thermosensibilité d'électricité à la maille EPCI de 2011 à 2025 (par secteur d'activité) », Licence Ouverte 2.0
- Enedis, note méthodologique thermosensibilité (pièce jointe du jeu de données)
- Documentation Streamlit : https://docs.streamlit.io/
- Contours des départements : IGN Admin Express (Licence ouverte), via https://github.com/gregoiredavid/france-geojson (version simplifiée)
