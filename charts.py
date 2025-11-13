import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

def plot_horizontal_stacked(df: pd.DataFrame, label_col: str, value_col: str, title: str) -> None:
    """Renders a compact horizontal stacked bar chart using Plotly."""
    fig = go.Figure()
    colors = ["#74c69d", "#4ea8de", "#f6bd60", "#f28482", "#9d4edd", "#00b4d8", "#6c757d"]

    for i, row in df.iterrows():
        fig.add_trace(
            go.Bar(
                y=["Weight"],
                x=[row[value_col]],
                orientation="h",
                name=str(row[label_col]),
                marker_color=colors[i % len(colors)],
                text=f"{row[label_col]}<br>{row[value_col]*100:.1f}%",
                hoverinfo="text",
            )
        )

    fig.update_layout(
        barmode="stack",
        title=title,
        showlegend=True,
        height=100,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(range=[0, 1], showticklabels=False),
        yaxis=dict(showticklabels=False),
    )
    st.plotly_chart(fig, width='stretch',  config={"staticPlot": True})


def plot_pie(df: pd.DataFrame, label_col: str, value_col: str, title: str) -> None:
    labels = df[label_col].tolist()
    values = df[value_col].tolist()

    custom_text = [
        f"{l}: {v*100:.1f}%" if v > 0 else ""
        for l, v in zip(labels, values)
    ]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        text=custom_text,
        textinfo="text",
        textposition="outside",
        hoverinfo="skip",
        marker_colors=[
            "#74c69d", "#4ea8de", "#f6bd60",
            "#f28482", "#9d4edd", "#00b4d8", "#6c757d"
        ]
    ))

    fig.update_layout(
        title=title,
        height=320,
        margin=dict(t=60, b=40),
        showlegend=True,
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


def render_world_map(ranking_df: pd.DataFrame) -> None:
    """Display a Plotly choropleth world map for AHP scores.

    Expects columns: 'country_name', country_code' (ISO-3)', 'AHP_Score'.
    """
    if ranking_df is None or ranking_df.empty:
        st.info("No data available for the map.")
        return

    fig = px.choropleth(
        ranking_df.round({"AHP_Score":3}),
        locations="country_code",
        locationmode="ISO-3",
        color="AHP_Score",
        hover_name="country_name",
        color_continuous_scale="Viridis",
        projection="natural earth",
        labels={"AHP_Score": "AHP Score",
                "country_code": "ISO-3"},
    )

    fig.update_geos(
        showcountries=True,
        countrycolor="white",
        showcoastlines=True,
        coastlinecolor="lightgray",
        showland=True,
        landcolor="#F5F5F5",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title="AHP Score"),
    )

    st.plotly_chart(fig, width='stretch')