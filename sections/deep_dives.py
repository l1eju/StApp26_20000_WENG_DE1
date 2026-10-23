import pandas as pd
import streamlit as st

from utils import viz
from utils.ui import analysis
from utils.prep import weighted_mean_by


def _by_group(epci, key):
    out = pd.DataFrame({"n_epci": epci.groupby(key)["code_epci"].nunique()})
    for col in ("part_thermosensible", "thermosensibilite_moyenne_kwh_dju"):
        out[col] = weighted_mean_by(epci, key, col, "nb_sites")
    return out.reset_index()


def render(data, filters):
    epci = filters["epci"]
    st.header("Dependence on the cold is not spread evenly")
    metric = st.radio("Indicator", ["part_thermosensible", "thermosensibilite_moyenne_kwh_dju"],
                      format_func=lambda c: viz.LABELS[c], horizontal=True)
    st.caption("Values are averaged over the selected years (weighted by number of sites), "
               "because one winter alone can mislead.")

    # Map: an EPCI that covers several departments counts in each of them (same value everywhere).
    ed = data["epci_department_year"]
    ed = ed[ed["annee"].between(*filters["years"])]
    if filters["regions"]:
        ed = ed[ed["nom_region"].isin(filters["regions"])]
    dep = _by_group(ed, "code_departement")
    names = ed.drop_duplicates("code_departement").set_index("code_departement")["nom_departement"]
    dep["nom_departement"] = dep["code_departement"].map(names)
    dep = dep.dropna(subset=[metric])

    st.plotly_chart(viz.department_map(dep, metric, "Map by department"), width="stretch")
    st.caption("Choropleth map of metropolitan France. Grey = no data (Corsica is missing from the dataset). "
               "An EPCI that covers several departments (for example the Métropole du Grand Paris) "
               "is shown in each of them with the same value.")
    analysis("map")

    ranked = epci.dropna(subset=[metric])
    ranked = (ranked.groupby(["code_epci", "nom_epci", "nom_departement"], as_index=False)
                    .apply(lambda g: pd.Series({metric: (g[metric] * g["nb_sites"]).sum() / g["nb_sites"].sum()}),
                           include_groups=False))
    ranked = ranked[ranked["code_epci"].isin(epci[epci["in_stable_panel"]]["code_epci"])]
    if len(ranked) >= 20:
        st.plotly_chart(viz.top_bottom(ranked, metric), width="stretch")
        st.caption("Horizontal bars: the EPCI present every year, at both ends of the ranking.")
        analysis("ranking")

    reg = _by_group(epci, ["annee", "nom_region"])
    if reg["nom_region"].nunique() > 1:
        st.plotly_chart(viz.region_multiples(reg, metric), width="stretch")
        st.caption("Small multiples: one panel per region, same vertical scale, so regions can be compared.")
        analysis("regions")

    # Heating and housing data exist for one year only (2024): we use that value for each EPCI
    # and compare it with the temperature-sensitive share averaged over the selected years.
    all_rows = data["epci_year"]
    heat = (all_rows.dropna(subset=["taux_de_chauffage_electrique"]).sort_values("annee")
            .groupby("code_epci").last()
            [["nom_epci", "nom_departement", "taux_de_chauffage_electrique", "nombre_d_habitants"]])
    share = epci.groupby("code_epci")["part_thermosensible"].mean()
    h = heat.join(share, how="inner").dropna(subset=["part_thermosensible"]).reset_index()
    if len(h) >= 10:
        st.subheader("Does electric heating explain the differences?")
        st.plotly_chart(viz.heating_scatter(h), width="stretch")
        # Spearman = Pearson correlation of the ranks (computed by hand: no extra package needed).
        rho = h["taux_de_chauffage_electrique"].rank().corr(h["part_thermosensible"].rank())
        strength = "weak" if abs(rho) < 0.3 else "moderate" if abs(rho) < 0.6 else "strong"
        st.caption(f"Scatter plot, {len(h):,} EPCI. Heating rate is from 2024 (the only year available); "
                   f"the share is the average over the selected years. Rank correlation: {rho:+.2f} "
                   f"({strength}). Correlation is not causation: climate and housing also matter.")
        analysis("scatter")
