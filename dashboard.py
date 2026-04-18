"""
Global Inflation Dashboard — Post-COVID 2020–2024
Senior Data Engineer / Data Scientist build
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Global Inflation Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #2d3250;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    [data-testid="metric-container"] label {
        color: #8b9cc8 !important;
        font-size: 0.78rem !important;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.82rem !important;
    }

    /* Section headers */
    .section-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #a5b4fc;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 4px;
        padding-left: 2px;
        border-left: 3px solid #6366f1;
        padding-left: 10px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #13151f; }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #a5b4fc;
        font-size: 1.1rem;
    }

    /* Divider */
    hr { border-color: #2d3250; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Country name mapping
# ─────────────────────────────────────────────
COUNTRY_NAMES = {
    "ARG": "Argentina", "AUS": "Australia", "BRA": "Brazil",
    "CAN": "Canada",    "CHN": "China",     "EU":  "European Union",
    "GBR": "United Kingdom", "IDN": "Indonesia", "IND": "India",
    "JPN": "Japan",     "KOR": "South Korea","MEX": "Mexico",
    "PHL": "Philippines","RUS": "Russia",   "SAU": "Saudi Arabia",
    "THA": "Thailand",  "TUR": "Turkey",    "USA": "United States",
    "VNM": "Vietnam",   "ZAF": "South Africa",
}

# ─────────────────────────────────────────────
# Data loading & caching
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["country_name"] = df["country"].map(COUNTRY_NAMES).fillna(df["country"])
    return df


# ─────────────────────────────────────────────
# Second cached loader — accepts BytesIO from st.file_uploader
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def load_data_bytes(uploaded_file) -> pd.DataFrame:
    import io
    df = pd.read_csv(io.BytesIO(uploaded_file.read()))
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["country_name"] = df["country"].map(COUNTRY_NAMES).fillna(df["country"])
    return df

# ─────────────────────────────────────────────
# Resolve CSV path — auto-detect or upload
# ─────────────────────────────────────────────
import os, pathlib

_DEFAULT_FILENAME = "global_inflation_post_covid.csv"
_CANDIDATES = [
    pathlib.Path(__file__).parent / _DEFAULT_FILENAME,
    pathlib.Path.cwd() / _DEFAULT_FILENAME,
    pathlib.Path("/mnt/user-data/uploads") / _DEFAULT_FILENAME,
]

def _find_csv():
    for p in _CANDIDATES:
        if p.exists():
            return str(p)
    return None

_csv_path = _find_csv()

if _csv_path is None:
    st.markdown(
        "<h1 style='color:#e2e8f0;font-size:1.6rem;font-weight:700;'>📈 Global Inflation Dashboard</h1>",
        unsafe_allow_html=True,
    )
    st.info(
        "**Dataset não encontrado automaticamente.**\n\n"
        f"Faça o upload do arquivo abaixo **ou** coloque "
        f"`{_DEFAULT_FILENAME}` na mesma pasta que `dashboard.py`.",
        icon="📂",
    )
    uploaded = st.file_uploader(
        "Selecione o arquivo CSV",
        type=["csv"],
        help="global_inflation_post_covid.csv baixado do Kaggle",
    )
    if uploaded is None:
        st.stop()
    df_full = load_data_bytes(uploaded)
else:
    df_full = load_data(_csv_path)

# ─────────────────────────────────────────────
# Sidebar — Filters
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Global Inflation")
    st.markdown("**Post-COVID Dashboard · 2020–2024**")
    st.markdown("---")

    st.markdown("### Filters")

    all_countries = sorted(df_full["country_name"].unique())
    selected_countries = st.multiselect(
        "Countries",
        options=all_countries,
        default=["United States", "Brazil", "European Union",
                 "China", "United Kingdom", "Turkey"],
    )

    min_date = df_full["date"].min().to_pydatetime()
    max_date = df_full["date"].max().to_pydatetime()
    date_range = st.slider(
        "Period",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="MMM YYYY",
    )

    st.markdown("---")
    st.markdown("### Indicator")
    indicator_map = {
        "Inflation Rate (%)": "inflation_rate",
        "Interest Rate (%)":  "interest_rate",
        "GDP Growth (%)":     "gdp_growth",
        "Unemployment (%)":   "unemployment_rate",
        "Oil Price (USD)":    "oil_price",
        "Food Price Index":   "food_price_index",
        "Supply Chain Index": "supply_chain_index",
        "Money Supply M2":    "money_supply_m2",
    }
    selected_indicator_label = st.selectbox(
        "Primary indicator", list(indicator_map.keys())
    )
    selected_indicator = indicator_map[selected_indicator_label]

    st.markdown("---")
    st.caption("📊 Data: Kaggle · Global Inflation Dynamics Post-COVID 2020–2024")

# Fallback: use all countries if nothing selected
if not selected_countries:
    selected_countries = all_countries

# ─────────────────────────────────────────────
# Filtered dataframe
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def filter_data(df: pd.DataFrame, countries: list, start, end) -> pd.DataFrame:
    mask = (
        df["country_name"].isin(countries) &
        (df["date"] >= start) &
        (df["date"] <= end)
    )
    return df[mask].copy()


df = filter_data(df_full, selected_countries, date_range[0], date_range[1])

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#e2e8f0;font-size:1.9rem;font-weight:800;margin-bottom:2px;'>"
    "📈 Global Inflation Dashboard — Post-COVID Era"
    "</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#8b9cc8;margin-top:0;font-size:0.9rem;'>"
    "Macroeconomic indicators for 20 economies · January 2020 – December 2024"
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ─────────────────────────────────────────────
# KPI Row
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)
st.markdown(" ")

# Global reference (all countries, full period)
global_avg_inf  = df_full["inflation_rate"].mean()
global_avg_int  = df_full["interest_rate"].mean()
global_avg_unemp= df_full["unemployment_rate"].mean()
global_avg_gdp  = df_full["gdp_growth"].mean()
global_avg_oil  = df_full["oil_price"].mean()

# Selection averages
sel_avg_inf   = df["inflation_rate"].mean()
sel_avg_int   = df["interest_rate"].mean()
sel_avg_unemp = df["unemployment_rate"].mean()
sel_avg_gdp   = df["gdp_growth"].mean()
sel_avg_oil   = df["oil_price"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Avg Inflation",    f"{sel_avg_inf:.2f}%",  f"{sel_avg_inf - global_avg_inf:+.2f}% vs global")
k2.metric("Avg Interest Rate",f"{sel_avg_int:.2f}%",  f"{sel_avg_int - global_avg_int:+.2f}% vs global")
k3.metric("Avg Unemployment", f"{sel_avg_unemp:.2f}%",f"{sel_avg_unemp - global_avg_unemp:+.2f}% vs global")
k4.metric("Avg GDP Growth",   f"{sel_avg_gdp:.2f}%",  f"{sel_avg_gdp - global_avg_gdp:+.2f}% vs global")
k5.metric("Avg Oil Price",    f"${sel_avg_oil:.0f}",  f"{sel_avg_oil - global_avg_oil:+.0f} vs global")

st.markdown("---")

# ─────────────────────────────────────────────
# Row 1 — Temporal + Heatmap
# ─────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<div class="section-header">Inflation Rate Over Time</div>', unsafe_allow_html=True)

    df_ts = (
        df.groupby(["date", "country_name"])[selected_indicator]
        .mean()
        .reset_index()
    )
    fig_ts = px.line(
        df_ts,
        x="date", y=selected_indicator,
        color="country_name",
        labels={"date": "", selected_indicator: selected_indicator_label, "country_name": "Country"},
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_ts.update_layout(
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        legend=dict(orientation="h", y=-0.2, x=0, font=dict(size=10)),
        height=340,
        margin=dict(l=10, r=10, t=20, b=60),
        xaxis=dict(gridcolor="#2d3250"),
        yaxis=dict(gridcolor="#2d3250"),
    )
    fig_ts.add_vrect(
        x0="2021-01-01", x1="2022-06-01",
        fillcolor="rgba(99,102,241,0.07)",
        line_width=0,
        annotation_text="Peak inflation period",
        annotation_position="top left",
        annotation_font_color="#8b9cc8",
        annotation_font_size=10,
    )
    st.plotly_chart(fig_ts, use_container_width=True)

with col_right:
    st.markdown('<div class="section-header">Inflation Heatmap by Year</div>', unsafe_allow_html=True)

    df_heat = (
        df.groupby(["country_name", "year"])["inflation_rate"]
        .mean()
        .reset_index()
    )
    pivot = df_heat.pivot(index="country_name", columns="year", values="inflation_rate")
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale="RdYlGn_r",
        text=np.round(pivot.values, 1),
        texttemplate="%{text}%",
        textfont=dict(size=9),
        colorbar=dict(title=dict(text="Inflation %", font=dict(color="#8b9cc8")), tickfont=dict(color="#8b9cc8")),
    ))
    fig_heat.update_layout(
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        height=340,
        margin=dict(l=10, r=10, t=20, b=20),
        xaxis=dict(side="top", tickfont=dict(color="#8b9cc8")),
        yaxis=dict(tickfont=dict(color="#8b9cc8", size=9)),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Row 2 — Country comparison + Scatter
# ─────────────────────────────────────────────
col2_left, col2_right = st.columns([2, 3])

with col2_left:
    st.markdown('<div class="section-header">Country Comparison</div>', unsafe_allow_html=True)

    df_bar = (
        df.groupby("country_name")[["inflation_rate", "interest_rate", "unemployment_rate"]]
        .mean()
        .round(2)
        .reset_index()
        .sort_values("inflation_rate", ascending=True)
    )
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=df_bar["country_name"], x=df_bar["inflation_rate"],
        name="Inflation", orientation="h",
        marker_color="#6366f1",
    ))
    fig_bar.add_trace(go.Bar(
        y=df_bar["country_name"], x=df_bar["interest_rate"],
        name="Interest", orientation="h",
        marker_color="#22d3ee",
    ))
    fig_bar.add_trace(go.Bar(
        y=df_bar["country_name"], x=df_bar["unemployment_rate"],
        name="Unemployment", orientation="h",
        marker_color="#f59e0b",
    ))
    fig_bar.update_layout(
        barmode="group",
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        height=420,
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(orientation="h", y=-0.08, font=dict(size=10, color="#8b9cc8")),
        xaxis=dict(gridcolor="#2d3250", tickfont=dict(color="#8b9cc8"), title_font=dict(color="#8b9cc8")),
        yaxis=dict(tickfont=dict(color="#8b9cc8", size=9)),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2_right:
    st.markdown('<div class="section-header">Inflation vs Interest Rate — Bubble Chart</div>', unsafe_allow_html=True)

    df_bubble = (
        df.groupby("country_name").agg(
            inflation_rate=("inflation_rate", "mean"),
            interest_rate=("interest_rate", "mean"),
            gdp_growth=("gdp_growth", "mean"),
            unemployment_rate=("unemployment_rate", "mean"),
        )
        .reset_index()
    )
    # Clamp negative to small positive for bubble size
    df_bubble["bubble_size"] = df_bubble["unemployment_rate"].clip(lower=0.5)

    fig_bubble = px.scatter(
        df_bubble,
        x="interest_rate", y="inflation_rate",
        size="bubble_size",
        color="gdp_growth",
        text="country_name",
        color_continuous_scale="RdYlGn",
        range_color=[-5, 10],
        labels={
            "interest_rate": "Avg Interest Rate (%)",
            "inflation_rate": "Avg Inflation Rate (%)",
            "gdp_growth": "GDP Growth (%)",
        },
        template="plotly_dark",
        size_max=45,
    )
    fig_bubble.update_traces(
        textposition="top center",
        textfont=dict(size=9, color="#c7d2fe"),
        marker=dict(opacity=0.85, line=dict(width=1, color="#1a1d2e")),
    )
    fig_bubble.update_layout(
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        height=420,
        margin=dict(l=10, r=10, t=20, b=20),
        coloraxis_colorbar=dict(
            title="GDP Growth %",
            tickfont=dict(color="#8b9cc8"),
            title_font=dict(color="#8b9cc8"),
        ),
        xaxis=dict(gridcolor="#2d3250", tickfont=dict(color="#8b9cc8")),
        yaxis=dict(gridcolor="#2d3250", tickfont=dict(color="#8b9cc8")),
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Row 3 — Macro correlations + Oil impact
# ─────────────────────────────────────────────
col3_left, col3_right = st.columns(2)

with col3_left:
    st.markdown('<div class="section-header">Correlation Matrix</div>', unsafe_allow_html=True)

    numeric_cols = [
        "inflation_rate", "interest_rate", "gdp_growth",
        "unemployment_rate", "oil_price", "food_price_index", "supply_chain_index",
    ]
    corr = df[numeric_cols].corr().round(2)
    labels_short = ["Inflation", "Interest", "GDP", "Unemp.", "Oil", "Food", "Supply"]

    fig_corr = go.Figure(go.Heatmap(
        z=corr.values,
        x=labels_short, y=labels_short,
        colorscale="RdBu",
        zmin=-1, zmax=1,
        text=corr.values,
        texttemplate="%{text}",
        textfont=dict(size=9),
        colorbar=dict(tickfont=dict(color="#8b9cc8")),
    ))
    fig_corr.update_layout(
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        height=350,
        margin=dict(l=10, r=10, t=20, b=20),
        xaxis=dict(tickfont=dict(color="#8b9cc8", size=9)),
        yaxis=dict(tickfont=dict(color="#8b9cc8", size=9)),
    )
    st.plotly_chart(fig_corr, use_container_width=True)

with col3_right:
    st.markdown('<div class="section-header">Oil Price vs Inflation (Global Monthly)</div>', unsafe_allow_html=True)

    df_oil = (
        df.groupby("date").agg(
            oil_price=("oil_price", "mean"),
            inflation_rate=("inflation_rate", "mean"),
        )
        .reset_index()
    )
    fig_oil = make_subplots(specs=[[{"secondary_y": True}]])
    fig_oil.add_trace(
        go.Scatter(
            x=df_oil["date"], y=df_oil["oil_price"],
            name="Oil Price (USD)",
            line=dict(color="#f59e0b", width=2),
            fill="tozeroy",
            fillcolor="rgba(245,158,11,0.07)",
        ),
        secondary_y=False,
    )
    fig_oil.add_trace(
        go.Scatter(
            x=df_oil["date"], y=df_oil["inflation_rate"],
            name="Inflation Rate (%)",
            line=dict(color="#f43f5e", width=2.5, dash="dot"),
        ),
        secondary_y=True,
    )
    fig_oil.update_layout(
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        height=350,
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(orientation="h", y=-0.15, font=dict(size=10, color="#8b9cc8")),
        xaxis=dict(gridcolor="#2d3250", tickfont=dict(color="#8b9cc8")),
    )
    fig_oil.update_yaxes(
        title_text="Oil Price (USD)", secondary_y=False,
        gridcolor="#2d3250", tickfont=dict(color="#8b9cc8"),
    )
    fig_oil.update_yaxes(
        title_text="Inflation (%)", secondary_y=True,
        tickfont=dict(color="#f43f5e"),
    )
    st.plotly_chart(fig_oil, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Row 4 — Distribution + GDP vs Unemployment
# ─────────────────────────────────────────────
col4_left, col4_right = st.columns(2)

with col4_left:
    st.markdown(f'<div class="section-header">Distribution — {selected_indicator_label}</div>', unsafe_allow_html=True)

    fig_dist = px.violin(
        df,
        x="country_name", y=selected_indicator,
        color="country_name",
        box=True,
        points="outliers",
        labels={"country_name": "", selected_indicator: selected_indicator_label},
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_dist.update_layout(
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        height=340,
        showlegend=False,
        margin=dict(l=10, r=10, t=20, b=60),
        xaxis=dict(tickangle=-40, tickfont=dict(size=9, color="#8b9cc8")),
        yaxis=dict(gridcolor="#2d3250", tickfont=dict(color="#8b9cc8")),
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with col4_right:
    st.markdown('<div class="section-header">GDP Growth vs Unemployment Rate</div>', unsafe_allow_html=True)

    df_gdp = (
        df.groupby(["date"]).agg(
            gdp_growth=("gdp_growth", "mean"),
            unemployment_rate=("unemployment_rate", "mean"),
        )
        .reset_index()
    )
    fig_gdp = make_subplots(specs=[[{"secondary_y": True}]])
    fig_gdp.add_trace(
        go.Bar(
            x=df_gdp["date"], y=df_gdp["gdp_growth"],
            name="GDP Growth (%)",
            marker=dict(
                color=df_gdp["gdp_growth"],
                colorscale="RdYlGn",
                cmin=-5, cmax=8,
            ),
            opacity=0.85,
        ),
        secondary_y=False,
    )
    fig_gdp.add_trace(
        go.Scatter(
            x=df_gdp["date"], y=df_gdp["unemployment_rate"],
            name="Unemployment (%)",
            line=dict(color="#22d3ee", width=2),
        ),
        secondary_y=True,
    )
    fig_gdp.update_layout(
        plot_bgcolor="#1a1d2e",
        paper_bgcolor="#1a1d2e",
        height=340,
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(orientation="h", y=-0.15, font=dict(size=10, color="#8b9cc8")),
        xaxis=dict(gridcolor="#2d3250", tickfont=dict(color="#8b9cc8")),
    )
    fig_gdp.update_yaxes(
        title_text="GDP Growth (%)", secondary_y=False,
        gridcolor="#2d3250", tickfont=dict(color="#8b9cc8"),
    )
    fig_gdp.update_yaxes(
        title_text="Unemployment (%)", secondary_y=True,
        tickfont=dict(color="#22d3ee"),
    )
    st.plotly_chart(fig_gdp, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# Footer table — Top / Bottom performers
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Country Summary Table</div>', unsafe_allow_html=True)
st.markdown(" ")

df_summary = (
    df.groupby("country_name")
    .agg(
        Inflation=("inflation_rate",    "mean"),
        Interest =("interest_rate",     "mean"),
        GDP      =("gdp_growth",        "mean"),
        Unemployment=("unemployment_rate","mean"),
        Oil      =("oil_price",         "mean"),
        Food_Idx =("food_price_index",  "mean"),
    )
    .round(2)
    .reset_index()
    .rename(columns={"country_name": "Country"})
    .sort_values("Inflation", ascending=False)
)

st.dataframe(
    df_summary.style
    .background_gradient(subset=["Inflation"], cmap="YlOrRd")
    .background_gradient(subset=["GDP"],       cmap="RdYlGn")
    .background_gradient(subset=["Unemployment"], cmap="YlOrRd_r")
    .format({c: "{:.2f}" for c in df_summary.columns if c != "Country"}),
    use_container_width=True,
    height=400,
)

st.caption("All values are averages over the selected period and countries. Data: Kaggle — Global Inflation Dynamics Post-COVID 2020–2024.")
