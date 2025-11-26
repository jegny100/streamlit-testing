import streamlit as st


st.title("About the Location Selection Tool")

st.markdown("""
This application supports data-driven country selection in the context of international location
decisions. It combines open data with a transparent weighting approach based on the
Analytic Hierarchy Process (AHP).  
""")

st.markdown("---")
st.header("How to Use the Tool")

st.markdown("""
**1. Select the Criteria**  
Open the criteria dialog via the sidebar button *“Select criteria”*. Choose which indicators
should be included in the evaluation. The dataset automatically updates based on your selection.

**2. Weight the Main Categories**  
Under *“Rating of the main categories”*, assign weights to the given pillars:
- Environmental  
- Economic  
- Social 
- Hydrogen 

These values are normalized so they always sum to 1.

**3. Weight the Indicators inside Each Category**  
Every criterion within a category can be weighted individually.  
Each category also normalizes automatically to keep the sum at 1.

**4. Review the Global Influence of Each Criterion**  
The tool multiplies pillar weights with indicator weights to compute global weights.
A horizontal bar chart visualizes how strongly each indicator affects the final ranking.

**5. Explore the Country Ranking**  
All available countries are scored using the weighted sum of their indicators.
Missing values are treated as 0.  
The ranking table shows the highest-scoring countries on top.

**6. View the World Map**  
The map provides a geographical visualization of country scores for easier exploration.
""")

st.markdown("---")
st.header("Methodology")

st.markdown("""
### Analytic Hierarchy Process (AHP)
The tool applies a simplified version of the Analytic Hierarchy Process (AHP).  
The idea:
- Decision criteria are structured into hierarchical categories.
- Users assign relative importance (weights) to categories and criteria.
- Indicators are normalized values between 0 and 1.
- A final country score is computed as a weighted sum.

This makes assumptions and data sources explicit, while keeping the process intuitive.
""")

st.markdown("### Data Processing")
st.markdown("""
Raw indicators from various sources are normalized between 0 and 1 using min–max scaling.
Outlier checks and relevance checks were performed prior to integration into the tool.
""")

st.markdown("---")
st.header("Data Sources")

st.markdown("""
The tool relies exclusively on open datasets with permissive licenses.  
Examples of included sources:

- **World Bank – World Development Indicators (WDI)**  
    License: CC BY 4.0  
    Indicators: FDI, inflation (CPI), GDP-related metrics, etc.

- **Regulatory Indicators for Sustainable Energy (RISE), ESMAP / World Bank**  
    License: CC BY 3.0 IGO  
    Used for: Renewable energy policy readiness.

- **IEA – Hydrogen Infrastructure & Energy Data**  
    License varies; only openly licensed subsets used.

- **Worldwide Governance Indicators (WGI)**  
    License: CC BY 4.0  
    Used for: Political Stability, Control of Corruption.

- **UN, Eurostat, OECD**  
    Selected openly licensed indicators where applicable.

The exact indicator definitions and metadata can be inspected by clicking the info icon next to
each criterion inside the tool.
""")

st.markdown("---")
st.header("Interpretation Notes")

st.markdown("""
The tool does not prescribe “the best country”.  
Instead, it:
- makes assumptions explicit,  
- enables transparent weighting,  
- and supports explorative or workshop-based decision-making.

Results depend strongly on:
- the selected criteria,  
- the chosen weights,  
- and data availability in the underlying datasets.
""")

st.markdown("---")
st.header("Imprint / Legal Notice")

st.image("image.png")
st.markdown("**Fkz. 03HY102C**")

st.markdown("""
**Location Selection Tool**  
Developed within an academic research context at  
*Rhine-Waal University of Applied Sciences (HSRW), Germany.*

**Responsible for Content (according to § 5 TMG):**  
Rhine-Waal University of Applied Sciences  
Marie-Curie-Straße 1  
47533 Kleve  
Germany  

This tool is a research prototype.  
All data used is openly licensed and provided “as is” without warranty.
""")