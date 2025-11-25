from typing import List, Tuple, Dict, Any, Set
import streamlit as st
import pandas as pd


def format_criterion_help(criterion: Dict[str, Any]) -> str:
    # Formats the help text for a given criterion.
    label = criterion.get("label", criterion.get("code", ""))
    description = criterion.get("description", "No description available.")
    year = criterion.get("year")
    source = criterion.get("source_short")

    lines = [
        f"**Criterion**: {label}",
        f"**Description**: {description}",
    ]
    if year is not None:
        lines.append(f"**Year**: {year}")
    if source:
        lines.append(f"**Source**: {source}")

    return "  \n".join(lines)



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
                #desc = criterion.get("description", "") or label
                desc = format_criterion_help(criterion)

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
            # --- Validation: At least one selected per category ---
            missing_pillars = []
            for pillar in pillars:
                criteria_codes = [c["code"] for c in pillar_to_criteria.get(pillar, [])]
                selected_in_pillar = [
                    code for code in criteria_codes 
                    if st.session_state.get(f"sel_{code}", False)
                ]
                if not selected_in_pillar:
                    missing_pillars.append(hierarchy.get(pillar, {}).get("label", pillar))

            if missing_pillars:
                st.error(
                    "You must select at least one criterion in each category.\n\n"
                    + "Missing: " + ", ".join(missing_pillars)
                )
                st.stop()  # Prevent Apply and rerun
            else:
                # --- Valid selection: Commit it ---
                for code in default_selection:
                    st.session_state["selected_criteria"][code] = st.session_state.get(f"sel_{code}", False)
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


def select_and_filter_countries(
    df_raw: pd.DataFrame,
    countries_lookup: pd.DataFrame,
) -> Tuple[List[str], pd.DataFrame]:
    """
    Allows the user to pick countries by region or individually and returns the filtered DataFrame.
    The selection is persisted in session state under 'selected_countries'.
    """
    if df_raw is None or df_raw.empty:
        return [], df_raw

    if "country_code" not in df_raw.columns:
        st.warning("Input data is missing the 'country_code' column.")
        return [], df_raw

    available_codes = [
        str(code) for code in df_raw["country_code"].dropna().astype(str).unique().tolist()
    ]

    if countries_lookup is None or countries_lookup.empty:
        lookup_df = pd.DataFrame(
            {
                "country_code": available_codes,
                "country_name": available_codes,
                "region": ["Other"] * len(available_codes),
            }
        )
    else:
        lookup_df = countries_lookup.copy()
        if "region" not in lookup_df.columns:
            lookup_df["region"] = "Other"

        lookup_df["country_code"] = lookup_df["country_code"].astype(str)
        lookup_df["region"] = lookup_df["region"].fillna("Other").astype(str).str.strip()
        lookup_df = lookup_df[lookup_df["country_code"].isin(available_codes)]

    known_codes = set(lookup_df["country_code"])
    missing_codes = [code for code in available_codes if code not in known_codes]
    if missing_codes:
        lookup_df = pd.concat(
            [
                lookup_df,
                pd.DataFrame(
                    {
                        "country_code": missing_codes,
                        "country_name": missing_codes,
                        "region": ["Other"] * len(missing_codes),
                    }
                ),
            ],
            ignore_index=True,
        )

    region_to_countries: Dict[str, List[Dict[str, str]]] = {}
    for region, subset in lookup_df.groupby("region"):
        sorted_subset = subset.sort_values("country_name")
        region_to_countries[region] = sorted_subset.to_dict("records")

    if "selected_countries" not in st.session_state:
        st.session_state["selected_countries"] = {
            code: True for code in available_codes
        }

    if "show_countries_modal" not in st.session_state:
        st.session_state["show_countries_modal"] = False

    @st.dialog("Select countries")
    def _countries_dialog() -> None:
        st.caption("Filter the dataset by selecting regions or individual countries.")

        col_all_a, col_all_b = st.columns(2)
        if col_all_a.button("Select All Countries", key="countries_select_all"):
            for code in available_codes:
                st.session_state[f"country_sel_{code}"] = True
        if col_all_b.button("Deselect All Countries", key="countries_deselect_all"):
            for code in available_codes:
                st.session_state[f"country_sel_{code}"] = False

        sorted_regions = sorted(region_to_countries.keys())
        for region in sorted_regions:
            countries = region_to_countries.get(region, [])
            region_codes = [c["country_code"] for c in countries]
            region_key = f"region_sel_{region}".replace(" ", "_")

            for code in region_codes:
                country_key = f"country_sel_{code}"
                if country_key not in st.session_state:
                    st.session_state[country_key] = st.session_state["selected_countries"].get(code, True)

            selected_count = sum(st.session_state.get(f"country_sel_{c}", True) for c in region_codes)
            region_default_checked = selected_count == len(region_codes)

            if region_key not in st.session_state:
                st.session_state[region_key] = region_default_checked

            expander_label = f"{region} ({selected_count}/{len(region_codes)})"
            with st.expander(expander_label, expanded=False):
                region_checked = st.checkbox(
                    "Select entire region",
                    key=region_key,
                    value=region_default_checked,
                )

                # If region checkbox toggled, propagate to all countries in that region
                if region_checked != region_default_checked:
                    for code in region_codes:
                        st.session_state[f"country_sel_{code}"] = region_checked

                for country in countries:
                    code = country["country_code"]
                    name = country.get("country_name", code)
                    country_key = f"country_sel_{code}"
                    st.checkbox(
                        f"{name} ({code})",
                        key=country_key,
                    )
                # Update the expander label counter by recalculating selected_count
                selected_count = sum(st.session_state.get(f"country_sel_{c}", False) for c in region_codes)

        col_apply, col_cancel = st.columns([1, 1])
        if col_apply.button("Apply", key="apply_countries"):
            for code in available_codes:
                st.session_state["selected_countries"][code] = st.session_state.get(f"country_sel_{code}", True)
            st.session_state["show_countries_modal"] = False
            st.rerun()

        if col_cancel.button("Cancel", key="cancel_countries"):
            for code, selected in st.session_state["selected_countries"].items():
                st.session_state[f"country_sel_{code}"] = selected
            st.session_state["show_countries_modal"] = False
            st.rerun()

    if st.session_state["show_countries_modal"]:
        _countries_dialog()

    selected_countries = [
        code for code, on in st.session_state["selected_countries"].items()
        if on and code in available_codes
    ]

    if not selected_countries:
        selected_countries = sorted(available_codes)

    country_codes_series = df_raw["country_code"].astype(str)
    df_filtered = df_raw[country_codes_series.isin(selected_countries)].copy()

    return selected_countries, df_filtered
