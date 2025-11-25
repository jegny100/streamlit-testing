import streamlit as st
import json

st.title("Indicator Documentation")

st.markdown("""
This page provides a structured overview of the indicators used in this tool. 
            Some details are still being added.
""")

st.markdown("---")

# ----------------------------
# Load hierarchy JSON
# ----------------------------
JSON_PATH = "ahp_criteria_structure_v4.json"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    hierarchy = json.load(f)


top = hierarchy.get("top", {})
sublevels = top.get("sublevels", [])

for pillar_id in sublevels:
    pillar = hierarchy.get(pillar_id, {})
    pillar_label = pillar.get("label", pillar_id)

    st.header(pillar_label)

    criteria = pillar.get("criteria", [])
    if not criteria:
        st.info("No indicators found for this category.")
        continue

    for crit in criteria:
        st.subheader(crit.get("label", "Unnamed Indicator"))

        st.markdown(f"""
        **Description:**  
        {crit.get("description", "No description available.")}

        **Year:** {crit.get("year", "n/a")}  
        **Source (short):** {crit.get("source_short", "n/a")}  
        **Source (full):** {crit.get("source_long", "n/a")}  
        """)


        st.markdown("---")
