import streamlit as st

import config
from utils.ui import analysis


def render(data, filters):
    q = data["quality"]
    st.header("What the data says, and what it cannot say")
    st.markdown(
        f"- **Period:** analysis starts in {config.ANALYSIS_START_YEAR}. Before, the EPCI map changes "
        "(2,472 EPCI in 2011, about 1,200 from 2017) and temperature data is missing.\n"
        "- **Missing values:** heating and housing columns exist for one year only. Missing consumption is mostly "
        "statistical secrecy (small groups are hidden), not an error.\n"
        "- **Duplicates:** an EPCI in several departments is repeated with the same totals; we keep one row.\n"
        f"- **Outliers:** degree-days above {config.DJU_MAX} are impossible and were set to missing.\n"
        "- **Corsica** is absent from the dataset.\n"
        "- **Causality:** the charts show correlations, not causes."
    )
    analysis("quality")
    st.subheader("Cleaning log")
    st.dataframe(q["cleaning_log"], hide_index=True, width="stretch")
    st.subheader("Share of EPCI with a value, by year (%)")
    st.dataframe(q["availability_by_year"].style.format("{:.1f}"), width="stretch")
    st.subheader("Missing values by column (%)")
    st.dataframe(q["missing_by_column"], width="stretch")
    st.download_button("Download the cleaned residential table (CSV)",
                       data["epci_year"].to_csv(index=False).encode("utf-8"),
                       file_name="residential_epci_year_clean.csv", mime="text/csv")
