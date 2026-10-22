import streamlit as st

from utils.prep import weighted_mean_by


def render(data, filters):
    nat, dep = data["national_year"], data["department_year"]
    st.header("Conclusions")
    n = nat.dropna(subset=["part_thermosensible"])
    n = n[n["annee"] >= 2018]
    low, high = n.loc[n["dju_gap"].idxmin()], n.loc[n["dju_gap"].idxmax()]
    st.markdown(
        f"1. **The weather changes the picture.** The temperature-sensitive share is {low['part_thermosensible']:.1f} % in "
        f"{int(low['annee'])} (mildest winter, {low['dju_gap']:+.0f} DJU) against {high['part_thermosensible']:.1f} % in "
        f"{int(high['annee'])} ({high['dju_gap']:+.0f} DJU)."
    )
    d = dep[dep["annee"] >= 2018].dropna(subset=["part_thermosensible"])
    avg = weighted_mean_by(d, "code_departement", "part_thermosensible", "nb_sites").sort_values()
    names = d.drop_duplicates("code_departement").set_index("code_departement")["nom_departement"]
    st.markdown(
        f"2. **Territories differ.** Over 2018–2025 the highest average share is in {names[avg.index[-1]]} "
        f"({avg.iloc[-1]:.1f} %), the lowest in {names[avg.index[0]]} ({avg.iloc[0]:.1f} %)."
    )
    g = n.sort_values("annee")
    st.markdown(
        f"3. **Sensitivity per degree-day is falling everywhere.** It goes from {g['thermosensibilite_moyenne_kwh_dju'].iloc[0]:.2f} "
        f"kWh/DJU in {int(g['annee'].iloc[0])} to {g['thermosensibilite_moyenne_kwh_dju'].iloc[-1]:.2f} in {int(g['annee'].iloc[-1])}, "
        "in every region. The data does not say why (renovation, behaviour or method changes are all possible)."
    )
    e = data["epci_year"]
    heat = (e.dropna(subset=["taux_de_chauffage_electrique"]).sort_values("annee")
            .groupby("code_epci")["taux_de_chauffage_electrique"].last())
    share = e[e["annee"] >= 2018].groupby("code_epci")["part_thermosensible"].mean()
    j = heat.to_frame().join(share, how="inner").dropna()
    if len(j) > 10:
        rho = j["taux_de_chauffage_electrique"].rank().corr(j["part_thermosensible"].rank())
        st.markdown(
            f"4. **Electric heating alone does not explain the gaps.** The rank correlation between the electric heating rate "
            f"and the temperature-sensitive share is only {rho:+.2f} across {len(j):,} EPCI."
        )
    st.markdown("5. **Implications (to discuss).** The two indicators answer different questions: the share shows where "
                "heating weighs most in winter use, the kWh per degree-day shows where demand rises most in a cold spell.")
    st.subheader("Limits and next steps")
    st.markdown("- Heating and housing data exist for one year only.\n"
                "- Corsica is missing; departments are approximated for EPCI that cross borders.\n"
                "- Next: add commune-level data or temperature-normalised comparisons.")
