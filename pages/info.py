# streamlit_page_title: Mein schöner Seitentitel
import json
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st



st.title("Hilfe & Anleitung")

st.markdown("""
- Wähle die Gewichtungen in der Sidebar.
- Sieh dir die Ergebnisse unter 'AHP Results' an.
- Die Weltkarte zeigt das Gesamtergebnis pro Land.
""")


# # Additional tabs for help and data sources
# st.markdown("---")
# tab_help, tab_sources = st.tabs(["Help & Tutorial", "Data Sources"])

# with tab_help:
# st.header("How to Use")
# st.markdown(
#     """
#     - Adjust the weights for the three main categories using the sliders.
#     - For each category, tune the weights of its criteria below.
#     - The AHP Results chart shows each criterion’s global influence.
#     - Review the ranking table and world map to compare countries.
#     - Iterate on weights to explore scenarios and sensitivities.
#     """
# )

# st.subheader("Tips")
# st.markdown(
#     """
#     - If all sliders in a section are set to 0, the app assigns equal weights automatically.
#     - Criteria not present in the dataset are ignored.
#     - Update the JSON structure or the dataset to customize categories and criteria.
#     """
# )

# with tab_sources:
# st.header("Data Sources")
# candidates = [
#     "DATA_SOURCES.md",
#     "ReadMe",
#     "README.md",
#     "README_en.md",
# ]
# content = None
# for fp in candidates:
#     try:
#         with open(fp, "r", encoding="utf-8") as f:
#             content = f.read()
#             break
#     except Exception:
#         continue
# if content:
#     st.markdown(content)
# else:
#     st.info("Add 'DATA_SOURCES.md' (or a README) to show citations here.")