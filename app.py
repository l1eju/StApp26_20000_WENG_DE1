"""Streamlit entry point: loads the data, draws the sidebar filters and calls one page."""
import streamlit as st

import config
from sections import conclusions, data_quality, deep_dives, intro, overview
from utils.io import fetch_and_cache
from utils.prep import make_tables
from utils.ui import sidebar_profile

st.set_page_config(page_title="Facing the cold", page_icon="❄️", layout="wide")


@st.cache_data(show_spinner="Loading and cleaning the data...")
def get_data():
    return make_tables(fetch_and_cache("residentiel"), fetch_and_cache("secteurs"))


data = get_data()
epci_all = data["epci_year"]
epci_all = epci_all[epci_all["annee"] >= config.ANALYSIS_START_YEAR]

sidebar_profile()
st.sidebar.title("Facing the cold")
PAGES = {"1. Intro": intro, "2. Overview": overview, "3. Territories": deep_dives,
         "4. Data quality": data_quality, "5. Conclusions": conclusions}
page = st.sidebar.radio("Page", list(PAGES))

st.sidebar.subheader("Filters")
y0, y1 = int(epci_all["annee"].min()), int(epci_all["annee"].max())
years = st.sidebar.slider("Years", y0, y1, (y0, y1))
regions = sorted(epci_all["nom_region"].dropna().unique())
chosen = st.sidebar.multiselect("Regions (empty = all)", regions)

epci = epci_all[epci_all["annee"].between(*years)]
if chosen:
    epci = epci[epci["nom_region"].isin(chosen)]
if epci.empty:
    st.warning("No data for these filters.")
    st.stop()

st.sidebar.caption(f"Source: {config.SOURCE_CITATION}. {config.LICENSE}.")
PAGES[page].render(data, {"epci": epci, "years": years, "regions": chosen})
