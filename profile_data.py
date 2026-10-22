"""Profile the raw data (step 1): sizes, missing values, ranges, duplicates, codes.

Usage:
    python profile_data.py            # downloads the data if needed, then prints the report
    python profile_data.py --refresh  # forces a new download

The report is also saved in data/profile_report.txt.
"""
from __future__ import annotations

import json
import sys

import pandas as pd

import config
from utils.io import fetch_and_cache

LINES: list[str] = []

KEY_NUMERIC = [
    "part_thermosensible", "thermosensibilite_moyenne_kwh_dju",
    "taux_de_chauffage_electrique", "taux_de_logements_collectifs",
    "dju_a_tr", "dju_a_tn", "conso_moyenne_mwh", "nb_sites", "nombre_d_habitants",
]


def say(text: str = "") -> None:
    print(text)
    LINES.append(text)


def title(text: str) -> None:
    say()
    say("=" * 70)
    say(text)
    say("=" * 70)


def present(df: pd.DataFrame, *cols: str) -> bool:
    return all(c in df.columns for c in cols)


def basics(name: str, df: pd.DataFrame) -> None:
    title(f"{name}: size")
    say(f"rows = {len(df)}   columns = {df.shape[1]}")
    say(f"memory ≈ {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
    if "annee" in df.columns:
        say(f"years: {int(df['annee'].min())} to {int(df['annee'].max())} "
            f"({df['annee'].nunique()} values)")
        if "code_epci" in df.columns:
            say("distinct EPCI per year:")
            say(df.groupby("annee")["code_epci"].nunique().to_string())


def missing(name: str, df: pd.DataFrame) -> None:
    title(f"{name}: missing values (%)")
    say((df.isna().mean() * 100).round(1).sort_values(ascending=False).to_string())


def ranges(res: pd.DataFrame) -> None:
    title("residentiel: value ranges")
    cols = [c for c in KEY_NUMERIC if c in res.columns]
    if cols:
        desc = res[cols].describe(percentiles=[0.5]).loc[["min", "50%", "max"]]
        say(desc.round(3).T.to_string())
    for c in ("part_thermosensible", "taux_de_chauffage_electrique"):
        if c in res.columns:
            s = res[c].dropna()
            if len(s):
                say(f"{c}: {(s > 1).mean() * 100:.1f}% of values > 1; "
                    f"{(s > 100).mean() * 100:.1f}% > 100  "
                    f"(unit: fraction 0-1 or percentage 0-100?)")
    for c in ("conso_totale_mwh", "conso_moyenne_mwh"):
        if c in res.columns:
            say(f"{c}: {(res[c] < 0).sum()} negative values")


def duplicates(res: pd.DataFrame, sec: pd.DataFrame) -> None:
    title("duplicates and EPCI that cover several departments")
    key_res = ["annee", "code_epci", "code_departement"]
    if present(res, *key_res):
        say(f"residentiel: duplicated rows on {key_res} = {res.duplicated(key_res).sum()}")
        n_dep = res.groupby(["annee", "code_epci"])["code_departement"].nunique()
        say(f"residentiel: (year, EPCI) pairs found in more than 1 department = "
            f"{(n_dep > 1).sum()} out of {len(n_dep)}")
    key_sec = ["annee", "code_epci", "code_departement",
               "code_categorie_consommation", "code_grand_secteur", "code_secteur_naf2"]
    if present(sec, *key_sec, "conso_totale_mwh"):
        say(f"secteurs: duplicated rows on {key_sec} = {sec.duplicated(key_sec).sum()}")
        grp = sec.groupby(
            ["annee", "code_epci", "code_categorie_consommation",
             "code_grand_secteur", "code_secteur_naf2"],
            dropna=False,
        ).agg(n_dep=("code_departement", "nunique"), n_conso=("conso_totale_mwh", "nunique"))
        multi = grp[grp["n_dep"] > 1]
        say(f"secteurs: groups found in more than 1 department = {len(multi)} out of {len(grp)}")
        if len(multi):
            say(f"  of which the same consumption in every department (repeated total): "
                f"{(multi['n_conso'] == 1).mean() * 100:.1f}%")


def rupture(sec: pd.DataFrame) -> None:
    title("secteurs: break in the series around 2018")
    if not present(sec, "annee", "code_grand_secteur", "conso_totale_mwh", "code_epci"):
        return
    pv = sec.pivot_table(index="annee", columns="code_grand_secteur",
                         values="conso_totale_mwh", aggfunc="sum") / 1e3
    say("total consumption (GWh) by main sector "
        "(EPCI in several departments may be counted several times):")
    say(pv.round(0).to_string())
    cnt = sec.pivot_table(index="annee", columns="code_grand_secteur",
                          values="code_epci", aggfunc="count")
    say("number of rows by main sector:")
    say(cnt.to_string())


def epci_codes(res: pd.DataFrame) -> None:
    title("EPCI codes and names (residentiel)")
    if not present(res, "code_epci", "nom_epci"):
        return
    say(f"distinct codes = {res['code_epci'].nunique()}   distinct names = {res['nom_epci'].nunique()}")
    names = res.groupby("code_epci")["nom_epci"].nunique()
    multi = names[names > 1]
    say(f"codes with several names = {len(multi)}")
    for code in multi.index[:5]:
        say(f"  {code} : {sorted(res.loc[res['code_epci'] == code, 'nom_epci'].dropna().unique())}")


def departements(res: pd.DataFrame) -> None:
    """Compare the department codes of the data with those of the map file."""
    title("department codes: data versus map file")
    if "code_departement" not in res.columns:
        say("column code_departement is missing")
        return
    if not config.GEOJSON_PATH.exists():
        say(f"map file not found: {config.GEOJSON_PATH} (check GEOJSON_PATH in config.py)")
        return
    geo = json.loads(config.GEOJSON_PATH.read_text(encoding="utf-8"))
    map_codes = {f["properties"]["code"] for f in geo["features"]}
    data_codes = set(res["code_departement"].dropna().astype(str).unique())
    say(f"codes in the data = {len(data_codes)}   codes in the map file = {len(map_codes)}")
    say(f"code lengths in the data: "
        f"{res['code_departement'].dropna().astype(str).str.len().value_counts().sort_index().to_dict()}")
    say(f"example codes in the data: {sorted(data_codes)[:6]} ... {sorted(data_codes)[-6:]}")
    only_data = sorted(data_codes - map_codes)
    only_map = sorted(map_codes - data_codes)
    say(f"data codes MISSING from the map file (cannot be drawn): {only_data or 'none'}")
    for code in only_data:
        sub = res[res["code_departement"].astype(str) == code]
        names = sub["nom_departement"].dropna().unique()[:2].tolist() if "nom_departement" in sub else []
        say(f"  {code}: {names} | {len(sub)} rows")
    say(f"map codes MISSING from the data (empty departments): {only_map or 'none'}")
    if "nom_departement" in res.columns:
        say(f"distinct department names = {res['nom_departement'].nunique()} "
            f"(distinct codes = {len(data_codes)})")


def main() -> None:
    refresh = "--refresh" in sys.argv
    res = fetch_and_cache("residentiel", refresh=refresh)
    sec = fetch_and_cache("secteurs", refresh=refresh)
    basics("residentiel", res)
    basics("secteurs", sec)
    missing("residentiel", res)
    ranges(res)
    duplicates(res, sec)
    rupture(sec)
    epci_codes(res)
    departements(res)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = config.DATA_DIR / "profile_report.txt"
    out.write_text("\n".join(LINES), encoding="utf-8")
    print(f"\nReport saved to {out}")


if __name__ == "__main__":
    main()
