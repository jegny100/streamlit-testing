import json
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

#from hierarchy import parse_ahp_structure
from charts import plot_pie, plot_horizontal_stacked, render_world_map
from filter_functions import select_and_filter_criteria
#from weights import get_user_weights
#from scoring import compute_global_weights, compute_country_scores


# ------------------------------
# 1) Load and parse AHP hierarchy
# ------------------------------
#@st.cache_data(show_spinner=False)
def load_hierarchy(json_path: str) -> Dict[str, Any]:
    """Load the hierarchy JSON file.

    Returns the raw JSON as a dict. Errors are surfaced in Streamlit and an
    empty structure is returned to allow the app to continue gracefully.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Hierarchy JSON not found at: {json_path}")
    except json.JSONDecodeError as e:
        st.error(f"Hierarchy JSON parse error: {e}")
    return {"levels": []}

# ------------------------------
# 2) Streamlit UI: Weight selection
# ------------------------------

def get_user_weights(hierarchy: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Collect user-chosen weights for top-level pillars and their criteria.

    Returns a nested dict:
      { pillar_id: {"weight": float, criterion_code: float, ... }, ... }
    All values are normalized to sum to 1 within their respective scopes.
    """
    weights: Dict[str, Dict[str, float]] = {}

    st.header("Rating of the main categories")
    top_sublevels: List[str] = hierarchy["top"]["sublevels"]

    # --- Main categories ---
    equal_top = 1.0 / len(top_sublevels)
    total_top = 0.0
    for sub in top_sublevels:
        default = float(equal_top)
        w = st.slider(f"{hierarchy[sub]['label']}", 0.0, 1.0, default, 0.01) # Name from JSON Labels
        weights[sub] = {"weight": float(w)}
        total_top += float(w)

    # Normalize and safeguard
    if total_top == 0:
        st.warning("All main category weights are 0. Setting equal weights.")
        for sub in weights:
            weights[sub]["weight"] = 1.0 / len(weights)
    else:
        for sub in weights:
            weights[sub]["weight"] /= total_top

    # --- Chart for main categories ---
    pillar_df = pd.DataFrame(
        {"Category": [hierarchy[sub]["label"] for sub in top_sublevels],
         "Weight": [weights[sub]["weight"] for sub in top_sublevels]}
    )

    # Charts
    plot_pie(pillar_df, "Category", "Weight", "Distribution of main categories")
    # plot_horizontal_stacked(pillar_df, "Category", "Weight", "Distribution of main categories")

    st.markdown("---")
    st.header("Weights within each category")

    # --- Criteria within each category ---
    for sub in top_sublevels:
        st.subheader(hierarchy[sub]["label"])  # label from JSON; may be localized
        # Filter criteria to those actually present in the data (exclude 'country_code')
        all_criteria = hierarchy[sub].get("criteria", [])
        available_codes = set(df.columns) - {"country_code"} if df is not None else set()
        criteria = [c for c in all_criteria if c.get("code") in available_codes]

        equal = 1.0 / len(criteria)
        total_sub = 0.0
        for crit in criteria:
            code = crit["code"]
            default = float(equal)
            val = st.slider(f"{crit['label']}", 0.0, 1.0, default, 0.01, key=f"w_{sub}_{code}")
            weights[sub][code] = float(val)
            total_sub += float(val)

        # Normalize and safeguard
        if total_sub == 0:
            st.warning(f"All criteria under '{hierarchy[sub]['label']}' are 0. Setting equal weights.")
            for crit in criteria:
                weights[sub][crit["code"]] = 1.0 / len(criteria)
        else:
            for crit in criteria:
                weights[sub][crit["code"]] /= total_sub

        # Stacked bar chart for criteria of this pillar
        crit_df = pd.DataFrame(
            {"Criterion": [c["label"] for c in criteria],
             "Weight": [weights[sub][c["code"]] for c in criteria]}
        )
        # plot_horizontal_stacked(
        #     crit_df,
        #     "Criterion",
        #     "Weight",
        #     f"Distribution within the category {hierarchy[sub]['label']}",
        # )

        # Pie chart for criteria of this pillar
        plot_pie(
            crit_df,
            "Criterion",
            "Weight",
            f"Distribution within the category {hierarchy[sub]['label']}",
            )
        st.markdown("---")

    return weights


# ------------------------------
# 3) Compute global weights
# ------------------------------
def compute_global_weights(weights: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """Multiply pillar weights by their criteria weights to obtain global weights."""
    global_weights: Dict[str, float] = {}
    for pillar, items in weights.items():
        pillar_weight = items.get("weight", 0.0)
        for key, value in items.items():
            if key == "weight":
                continue
            global_weights[key] = pillar_weight * value
    return global_weights


# ------------------------------
# 4) Compute country scores
# ------------------------------
#@st.cache_data(show_spinner=False)
def load_dataframe(path: str) -> pd.DataFrame:
    """Load the country indicators from an Excel file.

    Expected to contain a 'country_code' column and one column per criterion code.
    """
    return pd.read_excel(path)


@st.cache_data(show_spinner=False)
def load_countries_lookup(country_json_path: str) -> pd.DataFrame:
    """Load the country code --> name mapping from JSON into a DataFrame."""
    try:
        with open(country_json_path, "r", encoding="utf-8") as f:
            countries_data = json.load(f)
    except FileNotFoundError:
        st.error(f"Country mapping JSON not found at: {country_json_path}")
        return pd.DataFrame(columns=["country_code", "country_name"])  # empty
    except json.JSONDecodeError as e:
        st.error(f"Country mapping JSON parse error: {e}")
        return pd.DataFrame(columns=["country_code", "country_name"])  # empty

    countries_df = pd.DataFrame(countries_data)
    return countries_df.rename(columns={"code": "country_code", "name": "country_name"})


def compute_country_scores(
    df: pd.DataFrame,
    global_weights: Dict[str, float],
    country_json_path: str,
) -> pd.DataFrame:
    """Compute weighted scores per country and attach human-readable names.

    Parameters:
    - df: DataFrame with columns ['country_code', <criterion columns>]
    - global_weights: mapping {criterion_code: weight}
    - country_json_path: path to JSON with {"code": ISO3, "name": country name}
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["country_code", "country_name", "AHP_Score"])

    if "country_code" not in df.columns:
        st.error("Input data is missing required column 'country_code'.")
        return pd.DataFrame(columns=["country_code", "country_name", "AHP_Score"])

    # Compute scores; treat NaN as 0
    results: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        total_score = 0.0
        for crit, w in global_weights.items():
            if crit in df.columns:
                val = row[crit]
                try:
                    num = float(val) if pd.notna(val) else 0.0
                except Exception:
                    num = 0.0
                total_score += num * float(w)
            # else: missing column contributes 0
        results.append({"country_code": row["country_code"], "AHP_Score": total_score})
    results_df = pd.DataFrame(results)

    # Attach country names
    countries_df = load_countries_lookup(country_json_path)
    merged = results_df.merge(countries_df, on="country_code", how="left")
    merged = merged.sort_values("AHP_Score", ascending=False)[
        ["country_code", "country_name", "AHP_Score"]
    ]
    return merged

# ------------------------------
# 5) Streamlit app entry
# ------------------------------
def run_dynamic_ahp(json_path: str, data_path: str, country_json_path: str) -> None:
    st.title("Location Selection Tool")

    # Read JSON structure & data
    hierarchy = load_hierarchy(json_path)
    df = load_dataframe(data_path)


    # Trigger zum Öffnen des Kriteriendialogs (nur Button-UI!)
    if st.sidebar.button("Select criteria", key="open_criteria_modal"):
        st.session_state["show_criteria_modal"] = True

    # --- Criteria selection and filtering ---
    selected_codes, df = select_and_filter_criteria(df, hierarchy)


    st.sidebar.header("Data Overview")
    df = df.dropna(subset=[c for c in df.columns if c != 'country_code'])
    st.sidebar.write(f"Countries: {df.shape[0] if df is not None else 0}")
    st.sidebar.write(f"Criteria: {len(selected_codes)}")



    # Weights (filtered to only criteria present in the dataset)
    weights = get_user_weights(hierarchy, df)

    # Global weights
    global_weights = compute_global_weights(weights)


    # -- AHP Results Criterion Influence --

    st.subheader("AHP Results")
    # Build mappings from criterion code to label and pillar
    code_to_label: Dict[str, str] = {}
    code_to_pillar: Dict[str, str] = {}
    for sub in hierarchy["top"]["sublevels"]:
        pillar_label = hierarchy.get(sub, {}).get("label", sub)
        for crit in hierarchy.get(sub, {}).get("criteria", []):
            code_to_label[crit["code"]] = crit["label"]
            code_to_pillar[crit["code"]] = pillar_label

    # Tabular view: sorted by global influence (descending)
    gw_items = [
        {
            "Criterion": code_to_label.get(code, code),
            "Code": code,
            "Global Weight": float(w),
            "Pillar": code_to_pillar.get(code, "Other"),
        }
        for code, w in global_weights.items()
    ]
    gw_df = pd.DataFrame(gw_items).sort_values("Global Weight", ascending=False).reset_index(drop=True)

    # Compact horizontal bar chart for quick visual comparison
    if not gw_df.empty:
        # Color bars by pillar (3 pillars)
        color_map = {
            hierarchy.get("environmental", {}).get("label", "Environmental"): "#2a9d8f",
            hierarchy.get("economic", {}).get("label", "Economic"): "#e9c46a",
            hierarchy.get("social", {}).get("label", "Social"): "#e76f51",
        }
        fig = px.bar(
            gw_df,
            x="Global Weight",
            y="Criterion",
            color="Pillar",
            color_discrete_map=color_map,
            orientation="h",
            title="Influence of each criterion",
            labels={"Global Weight": "Influence", "Criterion": "Criterion"},
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=0, r=0, t=30, b=0),
            height=min(420, 28 * len(gw_df) + 80),
        )
        st.plotly_chart(fig, width='stretch', config={"staticPlot": True})

    # --  Ranking Table --
    ranking = compute_country_scores(df, global_weights, country_json_path)
    # Prepare display: clear header names and desired column order
    display_cols = ["country_name", "country_code", "AHP_Score"]
    if ranking is not None and not ranking.empty:
        ranking = ranking.loc[:, display_cols]
    st.markdown("---")
    st.subheader("Ranking by total score")
    st.dataframe(
        ranking,
        hide_index=True,
        width='stretch',
        column_order=display_cols,
        column_config={
            "country_name": st.column_config.TextColumn("Country"),
            "country_code": st.column_config.TextColumn("ISO-3", width="small"),
            "AHP_Score": st.column_config.NumberColumn("AHP Score", format="%.3f"),
        },
    )

    # --  World Map --

    st.markdown("---")
    st.subheader("World map: Country Scores")
    render_world_map(ranking)


# ------------------------------
# 6) Script entrypoint
# ------------------------------
if __name__ == "__main__":
    # Note: Labels for categories and criteria come from the JSON file
    json_path = "ahp_criteria_structure_v4.json"  # hierarchy JSON
    data_path = "combined_wide_CLEAN.xlsx"  # country indicators
    country_json_path = "country_codes_names.json"  # ISO-3 --> country name mapping
    run_dynamic_ahp(json_path, data_path, country_json_path)
