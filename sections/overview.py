import pandas as pd
import streamlit as st

from utils import viz
from utils.prep import weighted_mean_by


def _yearly(epci: pd.DataFrame) -> pd.DataFrame:
    """One row per year for the selected regions (indicators weighted by number of sites)."""
    out = pd.DataFrame({"annee": sorted(epci["annee"].unique())}).set_index("annee")
    for col in ("dju_gap", "part_thermosensible"):
        out[col] = weighted_mean_by(epci, "annee", col, "nb_sites")
    return out.reset_index()


def render(data, filters):
    epci, years, regions = filters["epci"], filters["years"], filters["regions"]
    st.header("The cold changes a lot from one winter to the next")
    where = ", ".join(regions) if regions else "all regions"
    st.caption(f"Everything on this page follows the sidebar filters. Now showing: {years[0]}-{years[1]}, {where}.")

    last = int(epci["annee"].max())
    cur = epci[epci["annee"] == last]
    yearly = _yearly(epci)
    thermo = epci.dropna(subset=["part_thermosensible"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Residential use, {last}", f"{cur['conso_gwh'].sum() / 1000:,.1f} TWh")
    c2.metric("Temperature-sensitive share",
              f"{(thermo['part_thermosensible'] * thermo['nb_sites']).sum() / thermo['nb_sites'].sum():.1f} %"
              if len(thermo) else "n/a")
    c3.metric("EPCI shown", f"{epci['code_epci'].nunique():,}")
    gap = yearly.set_index("annee")["dju_gap"].get(last)
    c4.metric(f"Winter {last} vs normal", f"{gap:+.0f} DJU" if pd.notna(gap) else "n/a",
              help="Positive = colder than normal.")

    sec = data["sector_epci_year"]
    sec = sec[sec["annee"].between(*years)]
    if regions:
        sec = sec[sec["nom_region"].isin(regions)]
    sec = (sec.groupby(["annee", "sector"], as_index=False)["conso_gwh"].sum(min_count=1))
    st.plotly_chart(viz.sector_lines(sec), width="stretch")
    st.caption("Line chart. For all France, residential is the largest sector (about 140-155 TWh), then services "
               "(about 115-120 TWh) and industry (about 60 TWh). Residential use drops after 2021.")

    left, right = st.columns(2)
    left.plotly_chart(viz.weather_bars(yearly), width="stretch")
    left.caption("Bars. Red = colder than normal, blue = milder. 2022 was by far the mildest winter.")
    right.plotly_chart(viz.share_vs_weather(yearly), width="stretch")
    right.caption("Line. The temperature-sensitive share is lowest in the mild winter of 2022: "
                  "comparing territories on one year only can mislead.")
