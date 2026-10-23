import streamlit as st

from utils.prep import weighted_mean_by
from utils.ui import analysis


def render(data, filters):
    nat, dep = data["national_year"], data["department_year"]
    st.header("Conclusions: the answers to our three questions")

    # --- Question 1 -----------------------------------------------------------
    n = nat[nat["annee"] >= 2018].dropna(subset=["part_thermosensible", "dju_gap"])
    cold, mild = n.loc[n["dju_gap"].idxmax()], n.loc[n["dju_gap"].idxmin()]
    st.subheader("1. Does temperature change electricity use?")
    st.markdown(
        f"**Yes, from one year to the next.** In {int(cold['annee'])}, the coldest winter ({cold['dju_gap']:+.0f} degree-days "
        f"compared with normal), homes used {cold['residential_gwh'] / 1000:.0f} TWh and "
        f"{cold['part_thermosensible']:.1f} % of their winter use followed the temperature. In {int(mild['annee'])}, the mildest "
        f"winter ({mild['dju_gap']:+.0f}), it was {mild['residential_gwh'] / 1000:.0f} TWh and {mild['part_thermosensible']:.1f} %. "
        "Other things may also have played a role (for example energy prices), so this is a strong sign, not a proof."
    )

    # --- Question 2 -----------------------------------------------------------
    d = dep[dep["annee"] >= 2018].dropna(subset=["part_thermosensible"])
    avg = weighted_mean_by(d, "code_departement", "part_thermosensible", "nb_sites").sort_values()
    names = d.drop_duplicates("code_departement").set_index("code_departement")["nom_departement"]
    st.subheader("2. Which territories depend most on the cold?")
    st.markdown(
        f"**Mountain areas, and some departments of the centre and north.** Over 2018-2025, the highest average share is in "
        f"{names[avg.index[-1]]} ({avg.iloc[-1]:.1f} %) and the lowest in {names[avg.index[0]]} ({avg.iloc[0]:.1f} %). "
        "The Mediterranean coast is low. Between EPCI the gap is even bigger (about 11 % to 50 %)."
    )

    # --- Question 3 -----------------------------------------------------------
    e = data["epci_year"]
    heat = (e.dropna(subset=["taux_de_chauffage_electrique"]).sort_values("annee")
            .groupby("code_epci")["taux_de_chauffage_electrique"].last())
    share = e[e["annee"] >= 2018].groupby("code_epci")["part_thermosensible"].mean()
    j = heat.to_frame().join(share, how="inner").dropna()
    st.subheader("3. Why do territories differ?")
    if len(j) > 10:
        rho = j["taux_de_chauffage_electrique"].rank().corr(j["part_thermosensible"].rank())
        st.markdown(
            f"**We tested one explanation: electric heating. It explains very little** (rank correlation {rho:+.2f} "
            f"across {len(j):,} EPCI). Local climate is a likely reason (mountains against the Mediterranean) but we did not "
            "measure it directly. Housing type and age, and other heating energies (gas, wood), are not tested here."
        )

    g = n.sort_values("annee")
    st.markdown(
        f"**Also noticed:** sensitivity per degree-day falls from {g['thermosensibilite_moyenne_kwh_dju'].iloc[0]:.2f} kWh/DJU in "
        f"{int(g['annee'].iloc[0])} to {g['thermosensibilite_moyenne_kwh_dju'].iloc[-1]:.2f} in {int(g['annee'].iloc[-1])}, "
        "in every region. The data does not say why."
    )

    st.subheader("What it means")
    st.markdown("The share shows where heating weighs most in winter use. The kWh per degree-day show where demand rises "
                "most in a cold spell. Areas that are high on both are logical priorities for renovation and for watching winter peaks. "
                "This is a lead to discuss, not a proof: we did not measure the effect of renovation.")
    analysis("conclusion")
    st.subheader("Limits and next steps")
    st.markdown("- Heating and housing data exist for one year only (2024).\n"
                "- Corsica is missing; an EPCI that covers several departments is shown in each of them.\n"
                "- Next: test housing type and age, and add other heating energies.")
