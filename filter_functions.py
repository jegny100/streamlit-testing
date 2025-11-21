from typing import List, Tuple, Dict, Any, Set
import streamlit as st
import pandas as pd

def select_and_filter_criteria(
    df_raw: pd.DataFrame,
    hierarchy: Dict[str, Any]
) -> Tuple[List[str], pd.DataFrame]:
    available_codes = set(df_raw.columns) - {"country_code"}
    pillars = hierarchy.get("top", {}).get("sublevels", [])
    pillar_to_criteria = {
        p: [c for c in hierarchy.get(p, {}).get("criteria", []) if c.get("code") in available_codes]
        for p in pillars
    }

    default_selection = {
        c["code"]: True for plist in pillar_to_criteria.values() for c in plist
    }

    if "selected_criteria" not in st.session_state:
        st.session_state["selected_criteria"] = default_selection.copy()

    code_to_valid_rows: Dict[str, Set[str]] = {
        code: set(df_raw[df_raw[code].notna()]["country_code"])
        for code in available_codes
    }
    all_countries = set(df_raw["country_code"])

    if "show_criteria_modal" not in st.session_state:
        st.session_state["show_criteria_modal"] = False

    

    @st.dialog("Select criteria")
    def _criteria_dialog() -> None:
        st.caption("Choose which criteria to include. The count (n=...) shows how many countries remain if selected.")

        col_sel_a, col_sel_b = st.columns(2)
        if col_sel_a.button("Select All", key="crit_select_all"):
            for code in default_selection:
                st.session_state[f"sel_{code}"] = True
        if col_sel_b.button("Deselect All", key="crit_deselect_all"):
            for code in default_selection:
                st.session_state[f"sel_{code}"] = False

        current_selected = {
            code for code in default_selection
            if st.session_state.get(f"sel_{code}", st.session_state["selected_criteria"].get(code, True))
        }

        for pillar in pillars:
            criteria = pillar_to_criteria.get(pillar, [])
            if not criteria:
                continue
            st.markdown(f"**{hierarchy.get(pillar, {}).get('label', pillar)}**")

            for criterion in criteria:
                code = criterion["code"]
                label = criterion.get("label", code)
                desc = criterion.get("description", "") or label

                combined = current_selected | {code}
                valid_sets = [code_to_valid_rows[c] for c in combined if c in code_to_valid_rows]
                valid_countries = set.intersection(*valid_sets) if valid_sets else all_countries
                country_count = len(valid_countries)

                code_key = f"sel_{code}"
                if code_key not in st.session_state:
                    st.session_state[code_key] = st.session_state["selected_criteria"].get(code, True)

                st.checkbox(
                    f"{label} (n={country_count})",
                    key=code_key,
                    help=desc,
                )

        col_apply, col_cancel = st.columns([1, 1])
        if col_apply.button("Apply", key="apply_criteria"):
            for code in default_selection:
                st.session_state["selected_criteria"][code] = st.session_state.get(f"sel_{code}", True)
            st.session_state["show_criteria_modal"] = False
            st.rerun()

        if col_cancel.button("Cancel", key="cancel_criteria"):
            st.session_state["show_criteria_modal"] = False
            st.rerun()

    if st.session_state["show_criteria_modal"]:
        _criteria_dialog()

    selected_codes = [
        code for code, on in st.session_state["selected_criteria"].items()
        if on and code in available_codes
    ]

    if not selected_codes and available_codes:
        selected_codes = sorted(list(available_codes))

    keep_cols = ["country_code"] + selected_codes
    df_filtered = df_raw.loc[:, [c for c in keep_cols if c in df_raw.columns]].copy()

    if selected_codes:
        df_filtered = df_filtered.dropna(subset=selected_codes)

    return selected_codes, df_filtered
