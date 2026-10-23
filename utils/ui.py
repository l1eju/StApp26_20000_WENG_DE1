"""Small display helpers: your own analysis under a chart, and the profile in the sidebar."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

import config
import texts


def analysis(key: str, container=st) -> None:
    """Show the text written in texts.ANALYSIS[key] (nothing if it is empty)."""
    text = texts.ANALYSIS.get(key, "").strip()
    if text:
        container.markdown(f"**Analysis:** {text}")


def sidebar_profile() -> None:
    """Logo, name, programme and contacts at the top of the sidebar."""
    p = texts.PROFILE
    logo = config.ROOT / p["logo"] if p.get("logo") else None
    if logo and Path(logo).exists():
        st.sidebar.image(str(logo), width=140)
    lines = [f"**{p['name']}**"] if p.get("name") else []
    for label in ("program", "year"):
        if p.get(label):
            lines.append(p[label])
    contacts = []
    if p.get("email"):
        contacts.append(f"Email: {p['email']}")
    if p.get("linkedin"):
        contacts.append(f"[LinkedIn]({p['linkedin']})" if p["linkedin"].startswith("http")
                        else f"LinkedIn: {p['linkedin']}")
    if p.get("github"):
        contacts.append(f"[GitHub]({p['github']})" if p["github"].startswith("http")
                        else f"GitHub: {p['github']}")
    course = []
    if p.get("course"):
        course.append(f"Course: {p['course']}")
    if p.get("professor"):
        course.append(f"Project proposed by: {p['professor']}")
    if p.get("professor_contact"):
        course.append(f"Contact: {p['professor_contact']}")
    block = "  \n".join(lines + contacts)
    if course:
        block += "\n\n" + "  \n".join(course)
    st.sidebar.markdown(block)
    st.sidebar.divider()
