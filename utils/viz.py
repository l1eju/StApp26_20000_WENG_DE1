"""Plotly charts with one consistent style (labelled axes, colour-blind-safe colours)."""
from __future__ import annotations

import json
from functools import lru_cache

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import config

TEMPLATE = "plotly_white"
SEQUENTIAL = "Viridis"          # colour-blind safe
DIVERGING = "RdBu_r"            # red = colder than normal, blue = milder
SECTOR_COLORS = {
    "Residential": "#0072B2", "Services (tertiary)": "#E69F00", "Industry": "#009E73",
    "Agriculture": "#CC79A7", "Small professionals (until 2017)": "#56B4E9", "Unknown": "#999999",
}
LABELS = {
    "annee": "Year", "conso_gwh": "Consumption (GWh)", "residential_gwh": "Residential consumption (GWh)",
    "part_thermosensible": "Temperature-sensitive share (%)",
    "thermosensibilite_moyenne_kwh_dju": "Thermosensitivity (kWh per degree-day)",
    "dju_gap": "Winter degree-days: actual minus normal (DJU)",
    "taux_de_chauffage_electrique": "Electric heating rate (%)",
    "nom_region": "Region", "nom_epci": "EPCI", "nom_departement": "Department",
}


def _style(fig: go.Figure, height: int = 400) -> go.Figure:
    fig.update_layout(template=TEMPLATE, height=height, margin=dict(l=10, r=10, t=50, b=10),
                      legend_title_text="", font=dict(size=14))
    return fig


def sector_lines(sector_year: pd.DataFrame) -> go.Figure:
    fig = px.line(sector_year, x="annee", y="conso_gwh", color="sector", markers=True,
                  color_discrete_map=SECTOR_COLORS, labels=LABELS,
                  title="Electricity consumption by sector (Enedis network)")
    fig.update_traces(hovertemplate="%{fullData.name}<br>%{x}: %{y:,.0f} GWh<extra></extra>")
    fig.update_xaxes(dtick=1)
    return _style(fig)


def weather_bars(national: pd.DataFrame) -> go.Figure:
    d = national.dropna(subset=["dju_gap"])
    fig = go.Figure(go.Bar(
        x=d["annee"], y=d["dju_gap"],
        marker_color=["#B2182B" if v > 0 else "#2166AC" for v in d["dju_gap"]],
        hovertemplate="%{x}: %{y:+.0f} DJU<extra></extra>"))
    fig.update_layout(title="Was the winter colder or milder than normal?",
                      xaxis_title="Year", yaxis_title=LABELS["dju_gap"])
    fig.update_xaxes(dtick=1)
    return _style(fig)


def share_vs_weather(national: pd.DataFrame) -> go.Figure:
    d = national.dropna(subset=["part_thermosensible"])
    fig = go.Figure(go.Scatter(
        x=d["annee"], y=d["part_thermosensible"], mode="lines+markers", line=dict(color="#0072B2"),
        hovertemplate="%{x}: %{y:.1f} %<extra></extra>"))
    fig.update_layout(title="Temperature-sensitive share of residential use",
                      xaxis_title="Year", yaxis_title=LABELS["part_thermosensible"])
    fig.update_xaxes(dtick=1)
    return _style(fig)


@lru_cache(maxsize=1)
def _geojson() -> dict:
    path = config.GEOJSON_PATH
    if not path.exists():  # also accept the original file name
        path = path.with_suffix(".geojson")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def department_map(dep: pd.DataFrame, value: str, title: str) -> go.Figure:
    gj = _geojson()
    codes = [f["properties"]["code"] for f in gj["features"]]
    fig = go.Figure()
    # Grey base layer: departments without data (Corsica, or hidden by the filters).
    fig.add_trace(go.Choropleth(geojson=gj, featureidkey=config.GEOJSON_ID_KEY, locations=codes,
                                z=[0] * len(codes), colorscale=[[0, "#D9D9D9"], [1, "#D9D9D9"]],
                                showscale=False, hoverinfo="skip", marker_line_width=0.3))
    fig.add_trace(go.Choropleth(
        geojson=gj, featureidkey=config.GEOJSON_ID_KEY, locations=dep["code_departement"],
        z=dep[value], colorscale=SEQUENTIAL, marker_line_width=0.3, marker_line_color="white",
        colorbar=dict(title=LABELS.get(value, value), thickness=12),
        text=dep["nom_departement"],
        hovertemplate="<b>%{text}</b> (%{location})<br>%{z:.2f}<extra></extra>"))
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(title=title)
    return _style(fig, 520)


def top_bottom(epci: pd.DataFrame, value: str, n: int = 10) -> go.Figure:
    d = epci.sort_values(value).copy()
    d["nom_epci"] = (d["nom_epci"].str.replace("Communauté de communes", "CC", regex=False)
                     .str.replace("Communauté d'agglomération", "CA", regex=False)
                     .str.replace("Communauté urbaine", "CU", regex=False))
    d = pd.concat([d.head(n).assign(group="Lowest"), d.tail(n).assign(group="Highest")])
    fig = px.bar(d, x=value, y="nom_epci", color="group", orientation="h", labels=LABELS,
                 color_discrete_map={"Lowest": "#56B4E9", "Highest": "#D55E00"},
                 hover_data={"nom_departement": True, "group": False},
                 title=f"The {n} lowest and {n} highest EPCI")
    fig.update_yaxes(title="", categoryorder="total ascending")
    return _style(fig, 560)


def region_multiples(region_year: pd.DataFrame, value: str) -> go.Figure:
    fig = px.line(region_year, x="annee", y=value, facet_col="nom_region", facet_col_wrap=4,
                  facet_col_spacing=0.04, labels=LABELS, markers=True,
                  title=f"{LABELS.get(value, value)} by region (same scale in every panel)")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_xaxes(dtick=2, title="")
    fig.update_yaxes(title="")
    fig.update_traces(line_color="#0072B2")
    return _style(fig, 620)


def heating_scatter(epci: pd.DataFrame) -> go.Figure:
    fig = px.scatter(epci, x="taux_de_chauffage_electrique", y="part_thermosensible",
                     size="nombre_d_habitants", size_max=30, opacity=0.6, labels=LABELS,
                     hover_name="nom_epci", hover_data={"nom_departement": True,
                                                        "nombre_d_habitants": ":,.0f"},
                     color_discrete_sequence=["#0072B2"],
                     title="Electric heating (2024) and temperature-sensitive share (one dot = one EPCI)")
    return _style(fig, 480)
