"""Cleaning, validation and feature engineering (the "Data Work" step).

Input : the two raw extracts returned by utils.io.fetch_and_cache
Output: small tables that are ready to plot, plus data quality tables.

Run `python -m utils.prep` from the project folder to print a quality report.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import config

EPCI_YEAR = ["annee", "code_epci"]

# Columns that are empty for some years: we track their availability year by year.
TRACKED = [
    "conso_totale_mwh", "part_thermosensible", "thermosensibilite_moyenne_kwh_dju",
    "dju_a_tr", "dju_a_tn", "taux_de_chauffage_electrique", "nombre_d_habitants",
]

# Indicators averaged with the number of sites as weight (an EPCI with more homes counts more).
WEIGHTED = [
    "part_thermosensible", "thermosensibilite_moyenne_kwh_dju",
    "dju_a_tr", "dju_a_tn", "dju_gap", "weather_effect_mwh",
]


# --- Small helpers -------------------------------------------------------------

def weighted_mean_by(df: pd.DataFrame, by, value: str, weight: str) -> pd.Series:
    """Mean of `value` weighted by `weight` in each group (rows with a missing value are ignored)."""
    d = df.dropna(subset=[value, weight])
    d = d.assign(_vw=d[value] * d[weight])
    g = d.groupby(by, observed=True)
    return (g["_vw"].sum() / g[weight].sum()).rename(value)


def _latest_label(df: pd.DataFrame, code_col: str, name_col: str) -> pd.Series:
    """Most recent name used for each code (names change and are spelled in several ways)."""
    d = df.dropna(subset=[name_col]).sort_values("annee")
    return d.groupby(code_col)[name_col].last()


def _quintile_class(s: pd.Series) -> pd.Series:
    """Q1 = lowest fifth, Q5 = highest fifth (ranks inside one year)."""
    cls = np.ceil(s.rank(pct=True) * 5).clip(lower=1, upper=5)
    return cls.map(lambda v: f"Q{int(v)}" if pd.notna(v) else None)


# --- Residential table (one row per EPCI and year) ------------------------------

def clean_residential(res: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df = res.copy()
    log = {"residential rows (raw)": len(df)}

    # 1. One label per code.
    for code, name in [("code_epci", "nom_epci"),
                       ("code_departement", "nom_departement"),
                       ("code_region", "nom_region")]:
        log[f"{code}: codes with several names"] = int((df.groupby(code)[name].nunique() > 1).sum())
        df[name] = df[code].map(_latest_label(df, code, name))

    # 2. Impossible values become missing values.
    for col in ("dju_a_tr", "dju_a_tn"):
        bad = df[col] > config.DJU_MAX
        log[f"{col} above {config.DJU_MAX} (set to missing)"] = int(bad.sum())
        df.loc[bad, col] = np.nan
    log["thermosensibilite_moyenne_kwh_dju equal to 0 (kept)"] = int(
        (df["thermosensibilite_moyenne_kwh_dju"] == 0).sum())

    # Keep one row per EPCI, year AND department (before removing the repeated totals).
    # The department map uses it: an EPCI that covers several departments is shown in each of them.
    by_department = df[["annee", "code_epci", "nom_epci", "code_departement", "nom_departement",
                        "code_region", "nom_region", "nb_sites", "part_thermosensible",
                        "thermosensibilite_moyenne_kwh_dju"]].copy()

    # 3. One row per EPCI and year. An EPCI that covers several departments is repeated
    #    once per department with the same totals, so we keep the largest row.
    #    When the rows are tied (always the case here), the smallest department code wins,
    #    so the result is the same at every run.
    g = df.groupby(EPCI_YEAR)
    several = g["code_departement"].transform("nunique") > 1
    different = g["conso_totale_mwh"].transform("nunique") > 1
    log["EPCI-years found in several departments"] = int(
        df.loc[several, EPCI_YEAR].drop_duplicates().shape[0])
    log["  of which with different totals"] = int(
        df.loc[several & different, EPCI_YEAR].drop_duplicates().shape[0])
    df = (df.sort_values(EPCI_YEAR + ["nb_sites", "code_departement"],
                         ascending=[True, True, False, True], kind="mergesort")
            .drop_duplicates(EPCI_YEAR, keep="first")
            .reset_index(drop=True))
    log["residential rows (one per EPCI and year)"] = len(df)

    # 4. New variables.
    df["conso_gwh"] = df["conso_totale_mwh"] / 1000
    # Positive gap = colder winter than normal.
    df["dju_gap"] = df["dju_a_tr"] - df["dju_a_tn"]
    # Extra heating use per site caused by the weather of the year (MWh, positive = colder year).
    df["weather_effect_mwh"] = (
        df["conso_moyenne_usages_thermosensibles_mwh"]
        - df["conso_moyenne_corrigee_de_l_alea_climatique_usages_thermosensibles_mwh"])
    df["conso_per_capita_mwh"] = df["conso_totale_mwh"] / df["nombre_d_habitants"]
    df["thermo_class"] = df.groupby("annee")["part_thermosensible"].transform(_quintile_class)

    # 5. EPCI present in every year of the analysis period (same perimeter, comparable over time).
    years = range(config.ANALYSIS_START_YEAR, int(df["annee"].max()) + 1)
    n_years = df[df["annee"].isin(years)].groupby("code_epci")["annee"].nunique()
    stable = n_years[n_years == len(years)].index
    df["in_stable_panel"] = df["code_epci"].isin(stable)
    log[f"EPCI present in every year {years[0]}-{years[-1]}"] = len(stable)
    return df, by_department, log


# --- Sector table (one row per EPCI, year and sector) ---------------------------

def clean_sectors(sec: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    key = ["annee", "code_epci", "code_categorie_consommation",
           "code_grand_secteur", "code_secteur_naf2"]
    log = {"sector rows (raw)": len(sec)}

    # Remove the totals repeated for each department of the same EPCI.
    df = sec.sort_values("conso_totale_mwh", ascending=False).drop_duplicates(key, keep="first")
    log["sector rows removed (EPCI total repeated per department)"] = len(sec) - len(df)
    log["sector rows left"] = len(df)
    log["sector rows with missing consumption (statistical secrecy)"] = int(
        df["conso_totale_mwh"].isna().sum())

    df = df.assign(
        sector=df["code_grand_secteur"].map(config.SECTOR_LABELS).fillna(df["code_grand_secteur"]),
        sector_group=np.where(df["code_grand_secteur"] == "RESIDENTIEL",
                              "Residential", "Non-residential"),
        conso_gwh=df["conso_totale_mwh"] / 1000,
    )
    # From 2018 the companies are split by NAF code (many rows): add them up per sector.
    g = df.groupby(["annee", "code_epci", "sector", "sector_group"])
    out = pd.DataFrame({
        "conso_gwh": g["conso_gwh"].sum(min_count=1),
        "nb_sites": g["nb_sites"].sum(min_count=1),
    }).reset_index()
    return out, log


# --- All the tables used by the app -------------------------------------------

def _group_table(epci: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    g = epci.groupby(keys)
    out = pd.DataFrame({
        "n_epci": g["code_epci"].nunique(),
        "nb_sites": g["nb_sites"].sum(min_count=1),
        "residential_gwh": g["conso_gwh"].sum(min_count=1),
    })
    for col in WEIGHTED:
        out[col] = weighted_mean_by(epci, keys, col, "nb_sites")
    return out.reset_index()


def make_tables(res: pd.DataFrame, sec: pd.DataFrame) -> dict:
    epci, epci_by_department, log_res = clean_residential(res)
    sector, log_sec = clean_sectors(sec)
    start = config.ANALYSIS_START_YEAR

    # Region of each EPCI (latest known), so that the sector chart can follow the region filter.
    region_of = epci.drop_duplicates("code_epci", keep="last").set_index("code_epci")["nom_region"]
    sector_epci = sector.assign(nom_region=sector["code_epci"].map(region_of))

    sector_year = (sector.groupby(["annee", "sector", "sector_group"])[["conso_gwh", "nb_sites"]]
                         .sum(min_count=1).reset_index())

    national = (sector_year.pivot_table(index="annee", columns="sector_group",
                                        values="conso_gwh", aggfunc="sum")
                .rename(columns={"Residential": "residential_gwh",
                                 "Non-residential": "non_residential_gwh"}))
    national["total_gwh"] = national.sum(axis=1)
    national["n_epci"] = epci.groupby("annee")["code_epci"].nunique()
    for col in WEIGHTED:
        national[col] = weighted_mean_by(epci, "annee", col, "nb_sites")
    national = national.reset_index()

    # Departments: built from the rows per department, so an EPCI that covers several
    # departments counts in each of them (same value everywhere).
    keys = ["annee", "code_departement"]
    g = epci_by_department.groupby(keys)
    department = pd.DataFrame({
        "n_epci": g["code_epci"].nunique(),
        "nb_sites": g["nb_sites"].sum(min_count=1),
    })
    for col in ("part_thermosensible", "thermosensibilite_moyenne_kwh_dju"):
        department[col] = weighted_mean_by(epci_by_department, keys, col, "nb_sites")
    department = department.reset_index()
    dep_names = epci_by_department.drop_duplicates("code_departement").set_index("code_departement")["nom_departement"]
    department["nom_departement"] = department["code_departement"].map(dep_names)

    region = _group_table(epci, ["annee", "code_region"])
    reg_names = epci.drop_duplicates("code_region").set_index("code_region")["nom_region"]
    region["nom_region"] = region["code_region"].map(reg_names)

    window = epci[epci["annee"] >= start]
    quality = {
        "cleaning_log": pd.DataFrame(list({**log_res, **log_sec}.items()),
                                     columns=["check", "value"]),
        "epci_per_year": epci.groupby("annee")["code_epci"].nunique().rename("n_epci").reset_index(),
        "availability_by_year": (epci[TRACKED].notna().groupby(epci["annee"]).mean() * 100).round(1),
        "missing_by_column": pd.DataFrame({
            "missing_%_all_years": epci.isna().mean() * 100,
            f"missing_%_since_{start}": window.isna().mean() * 100,
        }).round(1).sort_values("missing_%_all_years", ascending=False),
    }
    return {
        "epci_year": epci,
        "epci_department_year": epci_by_department,
        "sector_year": sector_year,
        "sector_epci_year": sector_epci,
        "national_year": national,
        "department_year": department,
        "region_year": region,
        "quality": quality,
    }


# --- Quality report (python -m utils.prep) --------------------------------------

def _report() -> None:
    from utils.io import fetch_and_cache

    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    pd.set_option("display.max_colwidth", 80)
    tables = make_tables(fetch_and_cache("residentiel"), fetch_and_cache("secteurs"))
    q, lines = tables["quality"], []

    def show(title: str, obj) -> None:
        text = obj.to_string() if hasattr(obj, "to_string") else str(obj)
        block = f"\n{'=' * 70}\n{title}\n{'=' * 70}\n{text}"
        print(block)
        lines.append(block)

    show("cleaning log", q["cleaning_log"])
    show("availability by year (% of EPCI with a value)", q["availability_by_year"])
    show("missing values (%)", q["missing_by_column"])
    nat = tables["national_year"].copy()
    nat["total_twh"] = nat["total_gwh"] / 1000
    show("national table (consumption in GWh, indicators weighted by sites)",
         nat.round(2).set_index("annee"))
    dep = tables["department_year"]
    last = int(dep["annee"].max())
    show(f"departments in {last}: 5 highest part_thermosensible",
         dep[dep["annee"] == last].nlargest(5, "part_thermosensible")
         [["code_departement", "nom_departement", "n_epci", "part_thermosensible",
           "thermosensibilite_moyenne_kwh_dju"]].round(2))
    show(f"departments in {last}: 5 lowest part_thermosensible",
         dep[dep["annee"] == last].nsmallest(5, "part_thermosensible")
         [["code_departement", "nom_departement", "n_epci", "part_thermosensible",
           "thermosensibilite_moyenne_kwh_dju"]].round(2))
    out = config.DATA_DIR / "prep_report.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport saved to {out}")


if __name__ == "__main__":
    _report()
