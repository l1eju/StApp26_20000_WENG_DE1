"""Download the Enedis data (export API) and keep a local cache.

This module does not depend on Streamlit: the in-memory cache (st.cache_data) is added in app.py.

The local cache is a gzipped CSV, not Parquet. Reading and writing Parquet needs a part of
pyarrow that some Windows security policies block, while CSV works everywhere.

Two ways to get the data:
  1. automatic: call the Enedis export API and keep only the useful columns;
  2. fallback: export a CSV by hand from the "Table" view of the portal and save it as
     data/raw/<name>_manual.csv (for example data/raw/residentiel_manual.csv).
"""
from __future__ import annotations

import re
import unicodedata

import pandas as pd
import requests

import config

CACHE_SUFFIX = ".csv.gz"


def normalize_columns(columns) -> list[str]:
    """'Conso totale (MWh)' -> 'conso_totale_mwh' (same as the technical names in the schema)."""
    out = []
    for c in columns:
        c = unicodedata.normalize("NFKD", str(c)).encode("ascii", "ignore").decode()
        out.append(re.sub(r"[^0-9a-zA-Z]+", "_", c).strip("_").lower())
    return out


def _download_csv(extract: dict, dest) -> None:
    url = f"{config.API_BASE}/catalog/datasets/{config.DATASET_ID}/exports/csv"
    params = {
        "select": ",".join(extract["select"]),
        "delimiter": ";",
        "use_labels": "false",
    }
    if extract.get("where"):
        params["where"] = extract["where"]
    with requests.get(url, params=params, stream=True, timeout=config.TIMEOUT_S) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)


def _read_cache(path) -> pd.DataFrame:
    """Read a cached CSV; code columns stay text so that '01' keeps its leading zero."""
    return pd.read_csv(path, dtype={c: str for c in config.STRING_COLUMNS})


def _read_manual(path) -> pd.DataFrame:
    """Read a CSV exported by hand (the separator and the column labels can vary)."""
    df = pd.read_csv(path, sep=None, engine="python", dtype=str)
    df.columns = normalize_columns(df.columns)
    for c in df.columns:
        if c not in config.STRING_COLUMNS:
            df[c] = pd.to_numeric(df[c].str.replace(",", ".", regex=False), errors="coerce")
    return df


def fetch_and_cache(name: str, refresh: bool = False) -> pd.DataFrame:
    """Return the extract `name` (see config.EXTRACTS), downloaded only once."""
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = config.RAW_DIR / f"{name}{CACHE_SUFFIX}"
    if cache.exists() and not refresh:
        return _read_cache(cache)

    extract = config.EXTRACTS[name]
    manual = config.RAW_DIR / f"{name}_manual.csv"
    if manual.exists():
        print(f"[io] reading the manual export {manual.name}")
        df = _read_manual(manual)
    else:
        print(f"[io] downloading '{name}' from the Enedis API (this can take a few minutes)...")
        tmp = config.RAW_DIR / f"{name}.csv"
        try:
            _download_csv(extract, tmp)
        except requests.RequestException as e:
            raise RuntimeError(
                f"Download failed ({e}).\n"
                f"1) Check the export URL in the API tab of {config.PORTAL_URL} "
                f"and fix config.API_BASE.\n"
                f"2) Or export by hand from the Table view (filter: {extract.get('where')}) "
                f"and save the CSV as {manual}."
            ) from e
        df = pd.read_csv(tmp, sep=";", dtype={c: str for c in config.STRING_COLUMNS})
        df.columns = normalize_columns(df.columns)
        tmp.unlink()

    missing = [c for c in extract["select"] if c not in df.columns]
    if missing:
        print(f"[io] columns missing from '{name}': {missing}")
    df = df[[c for c in extract["select"] if c in df.columns]]
    df.to_csv(cache, index=False, compression="gzip")
    print(f"[io] '{name}' saved to {cache.name} ({len(df)} rows)")
    return df
