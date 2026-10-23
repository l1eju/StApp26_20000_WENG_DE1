# Facing the cold: where does electricity use depend most on temperature?

Individual data storytelling project with Streamlit (#EFREIDataStories2026)
Author: Julie WENG, EFREI Paris, Data Engineering major (group DE1)
Deadline: Saturday 24 October 2026, 12:00

> This file is the project report. It explains the question, the data, how it was cleaned, what we found and what the limits are.

---

## 1. Summary

French homes use more electricity when it is cold, but not everywhere in the same way. Using Enedis open data (about 1,200 local areas, called EPCI, 2018-2025), the app shows **where winter electricity use depends most on temperature**.

Main results:
1. **The weather changes the picture.** The temperature-sensitive share of residential use falls from 28.4 % (2018) to 14.3 % in 2022, the mildest winter (419 degree-days below normal). Comparing territories with one year only can mislead, so the map uses the average of the years.
2. **Territories differ.** Over 2018-2025, the highest average share is in Hautes-Alpes (28.5 %) and the lowest in Alpes-Maritimes (15.8 %).
3. **Electric heating alone does not explain the gaps.** The rank correlation between the electric heating rate and the temperature-sensitive share is only +0.12 across 1,191 EPCI.
4. **Sensitivity per degree-day is falling in every region** (about 0.85 kWh per degree-day in 2018 and 0.54 in 2025, nationally). The data does not say why.

Main limits: heating and housing data exist for one year only (2024), Corsica is missing, and an EPCI that covers several departments is counted in one department only.

---

## 2. Audience and question

**Audience:** local teams (towns, regions, grid operators such as Enedis) who must decide where to renovate buildings and how to prepare for winter peaks.

**Main question:** where is electricity use most dependent on the cold, and what does it mean for renovation and winter peaks?

**Sub-questions:**
1. Where? Which areas have the highest temperature-sensitive share?
2. Why (hypothesis)? Do electric heating, housing or the harshness of the winter explain the gaps?
3. When? How do the sectors change over time, and can we see cold or mild winters?
4. How unequal? Are the gaps between territories big and stable?

**Climate framing:** climate change is only the background. The data covers winter indicators over eight years, so it cannot prove more extreme weather, and it says nothing about summer air conditioning.

---

## 3. Data

| Item | Detail |
|---|---|
| Title | Consommation et thermosensibilité d'électricité à la maille EPCI de 2011 à 2025 (par secteur d'activité) |
| Producer | Enedis |
| Link | https://opendata.enedis.fr/datasets/consommation-electrique-par-secteur-dactivite-epci |
| Licence | Licence Ouverte / Open Licence version 2.0 |
| Period | 1 January 2011 to 31 December 2025 |
| Size | 502,422 rows (checked on 22 October 2026) |
| API used | `https://opendata.enedis.fr/api/explore/v2.1/catalog/datasets/<id>/exports/csv` |
| Official API documentation | Data Fair API, `https://opendata.enedis.fr/data-fair/api/v1/datasets/<id>`. We checked that both APIs return the same number of rows (502,422). |

### Key terms
- **EPCI:** a group of neighbouring towns that share services. In charts: CC = communauté de communes, CA = communauté d'agglomération, CU = communauté urbaine.
- **Temperature-sensitive share (%):** the part of winter electricity use that follows the temperature (mostly heating).
- **Thermosensitivity (kWh per degree-day):** extra kWh used by one site for each additional degree-day of cold.
- **DJU (degree-days):** a measure of how cold a winter is. `dju_a_tr` = real winter, `dju_a_tn` = normal winter.
- Thermosensitivity is measured for the **Residential** sector only.

### What we download
The full dataset has 43 columns. We download two small extracts instead of everything:
- `residentiel`: Residential sector only, **29 columns** (thermosensitivity, degree-days, heating, housing, consumption);
- `secteurs`: all rows but only **9 columns**, for consumption by sector.

The columns we do not download are not needed for the story. Housing age columns are downloaded but not charted, because they exist for one year only.

---

## 4. Method

### 4.1 Step 1: profiling (`profile_data.py`)
Before cleaning anything, `profile_data.py` looks at the raw data and writes a report (`data/profile_report.txt`). It checks:
- the size of each extract and the number of EPCI per year;
- the **percentage of missing values** in each column;
- the range of the main numbers (to find units and impossible values);
- duplicate rows and EPCI found in several departments;
- the break in the sector series around 2018;
- EPCI codes with several names;
- whether every department code in the data exists in the map file.

### 4.2 What the profiling showed, and what we decided

| Finding | Decision |
|---|---|
| The EPCI map changes a lot: 2,472 EPCI in 2011, about 1,200 from 2017. | **The analysis uses 2018-2025.** |
| Sector definitions change in 2018 (small professionals split by sector, companies by activity code). | Same decision: no comparison across 2018. |
| Temperature data (degree-days) and thermosensitivity are empty before 2017 (about 55 % missing over all years, 0.5 % since 2018). | Years before 2018 are not shown. |
| Heating and housing columns are 90-95 % empty: they exist for **2024 only** (and population for 2024-2025). | They are used in one chart only (heating versus sensitivity), and the app says so. |
| Percentages are in 0-100, not 0-1. | Units are shown as % in all charts. |
| 52 normal-winter degree-day values are above 4,000 (the largest real value is about 2,830, the largest error is 6,205). | Set to missing. |
| 1,253 EPCI-years are repeated in several departments with exactly the same totals. | One row is kept (largest number of sites, then smallest department code, so the result is always the same). |
| 19,108 sector rows were the same repeated totals. | Removed. |
| 8,228 sector rows have no consumption. This is the **statistical secrecy rule** (small groups are hidden). | Kept as missing, not replaced. |
| 1,564 EPCI codes have several spellings of the name. | The most recent name is used. |
| Corsica (2A, 2B) is not in the data. | Shown in grey on the map. |
| Totals look right after cleaning: 346 TWh in 2018 and 320 TWh in 2025 for the whole Enedis network. | Totals are accepted. |

### 4.3 Step 2: cleaning and new variables (`utils/prep.py`)
`prep.py` makes the tables used by the app:
- one row per EPCI and year (residential), one row per EPCI, year and sector (sectors);
- indicators for departments and regions are **weighted averages** (weight = number of sites), so a large EPCI counts more than a small one;
- new variables: `dju_gap` (real minus normal degree-days; positive = colder winter), `weather_effect_mwh`, `conso_gwh`, `conso_per_capita_mwh`, `thermo_class` (quintiles), `in_stable_panel` (EPCI present in every year 2018-2025: 1,173 EPCI);
- quality tables shown on the "Data quality" page.

`python -m utils.prep` prints this report and saves it in `data/prep_report.txt`.

### 4.4 Loading and speed (`utils/io.py`, `app.py`)
`io.py` downloads each extract once and saves it as a compressed CSV (`data/raw/*.csv.gz`). Parquet was not used because a Windows security feature (Smart App Control) blocked part of `pyarrow` on one PC. The cache is kept in the repository so the deployed app starts without calling the API. `app.py` uses `st.cache_data` so the cleaning runs only once.

---

## 5. The app

| Page | Content |
|---|---|
| 1. Intro | hook, scope, definitions |
| 2. Overview | 4 KPIs linked to the filters, consumption by sector, cold or mild winters, sensitive share by year |
| 3. Territories | map by department, 10 lowest and highest EPCI, small multiples by region, heating versus sensitivity |
| 4. Data quality | cleaning log, availability by year, missing values, CSV download |
| 5. Conclusions | four results with numbers, limits, next steps |

Sidebar filters: page, years, regions. Every chart has a tooltip, labelled axes with units and a short text description below.

**Accessibility:** colour-blind-safe palettes (Viridis for the map, blue/orange for groups), red/blue for cold/mild winters, every chart has a text description, axes always have units.

---

## 6. Data quality and limits

- **Missing data:** heating and housing data exist for 2024 only. Missing consumption is mostly statistical secrecy.
- **Series break:** the sector and EPCI definitions change around 2018, so we start in 2018.
- **Departments:** an EPCI that covers several departments is counted in one department only (the smallest code), so department values are approximate for those EPCI.
- **Corsica** is missing in the dataset.
- **One year can mislead:** the sensitive share is 28 % in 2018 and 14 % in 2022 because of the weather. The map uses the average of the selected years.
- **Falling sensitivity:** the fall of kWh per degree-day from 2018 to 2025 could come from renovation, behaviour or a change of method. The data does not tell.
- **Causality:** the charts show correlations, not causes. For example, the heating-sensitivity correlation is only +0.12.
- **Only electricity:** gas or other heating is not in the data.

---

## 7. Ethics and privacy

The data is aggregated by Enedis and protected by statistical secrecy. We do not try to identify anyone. The licence and the source are shown in the app. Conclusions are written carefully: they describe patterns, they do not blame territories.

---

## 8. Project structure

```
StApp26_20000_WENG_DE1/
├─ app.py                  # entry point: loads data, sidebar, calls the pages
├─ config.py               # settings: URLs, columns, analysis period, map
├─ profile_data.py         # step 1: quality report on the raw data
├─ requirements.txt        # pinned dependencies
├─ README.md               # this report
├─ storyboard.md           # storyboard of the app
├─ sections/               # one file per page
│  ├─ intro.py
│  ├─ overview.py
│  ├─ deep_dives.py
│  ├─ data_quality.py
│  └─ conclusions.py
├─ utils/
│  ├─ io.py                # download + local cache
│  ├─ prep.py              # cleaning, validation, new variables
│  └─ viz.py               # charts with a common style
├─ data/
│  ├─ raw/                 # cached data (residentiel.csv.gz, secteurs.csv.gz)
│  ├─ profile_report.txt
│  └─ prep_report.txt
└─ assets/
   └─ departements.geojson # department outlines (IGN Admin Express, simplified)
```

---

## 9. How to run it

You need Python **3.12 to 3.14**, 64-bit (tested with 3.12).

```
python -m venv .venv            (py -3.12 -m venv .venv)
.venv\Scripts\activate          (if it doesn't work do : Set-ExecutionPolicy -Scope Process Bypass)
pip install -r requirements.txt
python profile_data.py            # step 1: quality report
python -m utils.prep              # step 2: cleaning report
streamlit run app.py              # the app
```

The data is already in `data/raw/`. To download it again from the Enedis API: `python profile_data.py --refresh`. If the API does not work, export a CSV by hand from the "Table" view of the portal and save it as `data/raw/<name>_manual.csv` (for example `residentiel_manual.csv`).

---

## 10. Deliverables and links

- Deployed app: https://stapp2620000wengde1-rbhc46da23pktx4fc2jdsm.streamlit.app/
- Code repository: https://github.com/l1eju/StApp26_20000_WENG_DE1
- Demo video: submitted separately with the project
- Storyboard: see `storyboard.md`

---

## 11. References

- Enedis Open Data, dataset "Consommation et thermosensibilité d'électricité à la maille EPCI de 2011 à 2025 (par secteur d'activité)", Licence Ouverte 2.0
- Enedis, methodology note on thermosensitivity (attachment of the dataset)
- Streamlit documentation: https://docs.streamlit.io/
- Department outlines: IGN Admin Express (open licence), via https://github.com/gregoiredavid/france-geojson (simplified version)
