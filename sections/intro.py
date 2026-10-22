import streamlit as st

import config


def render(data, filters):
    st.header("When it gets colder, not every territory consumes the same")
    st.write(
        "On a cold winter day, French homes heat up and electricity demand jumps. "
        "But the jump is much bigger in some territories than in others. "
        "This app shows **where electricity use depends most on the cold**, "
        "to help local teams decide where renovation matters most and where winter peaks will hit hardest."
    )
    st.info(
        f"**Scope:** {config.ANALYSIS_START_YEAR}–2025, about 1,200 intercommunal areas (EPCI) in metropolitan France. "
        "Why not 2011? Before 2018 the EPCI map and the sector definitions change, and the temperature data is missing."
    )
    with st.expander("Definitions: what do these terms mean?"):
        st.markdown(
            "- **EPCI**: a group of neighbouring towns that share services (a local area, bigger than a town). "
            "In charts the names are shortened: **CC** = *communauté de communes* (rural or small-town group), "
            "**CA** = *communauté d'agglomération* (medium city), **CU** = *communauté urbaine* (large city).\n"
            "- **Temperature-sensitive share**: the part of winter electricity use (in %) that follows the temperature, mainly heating.\n"
            "- **Thermosensitivity (kWh/DJU)**: extra kWh used per site for each additional degree-day of cold.\n"
            "- **DJU (degree-days)**: a measure of how cold a winter is. More DJU means a colder winter.\n"
            "- **Residential only**: thermosensitivity is only measured for homes, not for businesses or industry."
        )
    st.caption(f"Source: {config.SOURCE_CITATION}. Licence: {config.LICENSE}.")
