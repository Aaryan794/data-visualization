"""
SDG 7 (Affordable and Clean Energy) — Streamlit dashboard.
ITS68404-style: clear structure, comments, interactive Plotly visuals.
"""

import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

# ---------------------------------------------------------------------------
# Page & theme
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SDG 7 Dashboard - Affordable and Clean Energy",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ──────────────────────────────────────────────────────────────────
ACCENT      = "#0ea5e9"   # sky blue
ACCENT2     = "#f97316"   # vivid orange
ACCENT3     = "#6366f1"   # indigo
DARK        = "#f8fafc"   # page bg (near-white)
DARK2       = "#ffffff"   # card bg
DARK3       = "#f1f5f9"   # subtle surface
TEXT        = "#0f172a"   # near-black text
TEXT_MUTED  = "#64748b"   # slate muted
SURFACE     = "#ffffff"
BORDER      = "#e2e8f0"

CHART_H_TALL = 440
CHART_H_GRID = 360

COL_RENEW     = "Renewable energy share in the total final energy consumption (%)"
COL_FOSSIL    = "Electricity from fossil fuels (TWh)"
COL_NUCLEAR   = "Electricity from nuclear (TWh)"
COL_RENEW_ELEC= "Electricity from renewables (TWh)"
COL_CO2       = "Value_co2_emissions_kt_by_country"
COL_ACCESS    = "Access to electricity (% of population)"
COL_GDP       = "gdp_per_capita"
COL_EI        = "Energy intensity level of primary energy (MJ/$2017 PPP GDP)"

FACET_COUNTRIES = ["China", "United States", "India", "Brazil", "Germany"]
ASSIGN_Y0, ASSIGN_Y1 = 2000, 2020


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
def inject_global_styles() -> None:
    st.markdown(f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"] {{
        font-family: 'Space Grotesk', sans-serif !important;
    }}
    .stApp {{
        background: #f8fafc !important;
        color: {TEXT} !important;
    }}
    .main .block-container {{
        padding-top: 1.25rem;
        padding-bottom: 3rem;
        max-width: 1480px;
    }}
    .main .block-container,
    .main .block-container p,
    .main .block-container li,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] h5 {{
        color: {TEXT} !important;
    }}
    .main h1,.main h2,.main h3,.main h4,.main h5 {{
        color: {TEXT} !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }}
    [data-testid="stCaption"], .stCaption, small {{
        color: {TEXT_MUTED} !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
    }}
    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: #ffffff !important;
        border-right: 1px solid {BORDER} !important;
    }}
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: {TEXT_MUTED} !important;
    }}
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {{
        color: {TEXT} !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }}
    [data-testid="stSidebar"] .block-container {{
        padding-top: 1.75rem;
        padding-left: 1.1rem;
        padding-right: 1.1rem;
    }}
    [data-testid="stSidebar"] [role="radiogroup"] label,
    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        color: {TEXT} !important;
        font-size: 0.92rem !important;
        font-weight: 500;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: {BORDER} !important;
        margin: 1.1rem 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stCaption"] {{
        color: {TEXT_MUTED} !important;
        font-size: 0.72rem !important;
    }}
    [data-testid="stSidebar"] .stDownloadButton button {{
        background: {ACCENT} !important;
        border: none !important;
        color: #fff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        width: 100%;
        transition: all .18s;
    }}
    [data-testid="stSidebar"] .stDownloadButton button:hover {{
        opacity: 0.88;
    }}
    /* ── Hero ── */
    .hero-wrap {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 55%, #f0fdf4 100%);
        border: 1px solid {BORDER};
        border-radius: 18px;
        padding: 2.25rem 2.5rem 2rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 4px 24px rgba(14,165,233,.08);
    }}
    .hero-wrap::before {{
        content:'';
        position:absolute; inset:0;
        background-image:
            linear-gradient(rgba(14,165,233,.05) 1px,transparent 1px),
            linear-gradient(90deg,rgba(14,165,233,.05) 1px,transparent 1px);
        background-size: 40px 40px;
        pointer-events:none;
    }}
    .hero-wrap::after {{
        content:'';
        position:absolute;
        top:-100px; right:-60px;
        width:380px; height:380px;
        background: radial-gradient(circle, rgba(14,165,233,.1) 0%, transparent 68%);
        pointer-events:none;
    }}
    .hero-badge {{
        position:relative;
        display:inline-flex; align-items:center; gap:.4rem;
        background: rgba(14,165,233,.1);
        border: 1px solid rgba(14,165,233,.25);
        color: {ACCENT};
        font-size:.68rem; font-weight:700;
        letter-spacing:.12em; text-transform:uppercase;
        padding:.28rem .75rem; border-radius:999px;
        margin-bottom:.9rem;
    }}
    .hero-title {{
        position:relative;
        font-family:'Space Grotesk',sans-serif;
        font-size:clamp(1.8rem,4.5vw,2.8rem);
        font-weight:700;
        color:{TEXT};
        margin:0 0 .6rem;
        line-height:1.1;
        letter-spacing:-.03em;
    }}
    .hero-title .hl {{ color:{ACCENT}; }}
    .hero-sub {{
        position:relative;
        color:{TEXT_MUTED};
        font-size:.97rem; font-weight:300;
        max-width:52rem; line-height:1.7;
        margin:0;
    }}
    .hero-pills {{
        position:relative;
        display:flex; gap:.5rem; flex-wrap:wrap;
        margin-top:1.4rem;
    }}
    .hero-pill {{
        background:#fff;
        border:1px solid {BORDER};
        border-radius:6px;
        padding:.22rem .65rem;
        font-size:.72rem; color:{TEXT_MUTED};
        font-family:'JetBrains Mono',monospace;
    }}
    /* ── Section header ── */
    .section-title {{
        font-family:'Space Grotesk',sans-serif;
        font-size:1.2rem; font-weight:700;
        color:{TEXT};
        margin:0 0 .25rem;
        padding-left:.9rem;
        border-left:3px solid {ACCENT};
        letter-spacing:-.02em;
    }}
    .section-desc {{
        color:{TEXT_MUTED};
        font-size:.88rem; font-weight:300;
        margin:0 0 1.4rem;
        padding-left:1.1rem;
    }}
    /* ── Metric cards ── */
    div[data-testid="stMetric"] {{
        background:#ffffff;
        border:1px solid {BORDER};
        border-radius:12px;
        padding:1.1rem 1.25rem;
        position:relative; overflow:hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,.04);
    }}
    div[data-testid="stMetric"]::after {{
        content:'';
        position:absolute; top:0; left:0;
        width:3px; height:100%;
        background: linear-gradient(180deg,{ACCENT},{ACCENT3});
    }}
    div[data-testid="stMetric"] label {{
        color:{TEXT_MUTED} !important;
        font-size:.72rem !important;
        font-weight:500 !important;
        text-transform:uppercase;
        letter-spacing:.06em;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color:{TEXT} !important;
        font-weight:700 !important;
        font-size:1.55rem !important;
        font-family:'Space Grotesk',sans-serif;
        letter-spacing:-.03em;
    }}
    /* ── Chart cards ── */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background:#ffffff !important;
        border:1px solid {BORDER} !important;
        border-radius:14px !important;
        padding:.5rem 0 !important;
        margin-bottom:.9rem !important;
        overflow:hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,.04);
    }}
    /* ── Widget labels ── */
    .stSlider label, .stSlider span,
    .stNumberInput label,
    label[data-testid="stWidgetLabel"] {{
        color:{TEXT} !important;
        font-weight:500 !important;
        font-size:.88rem !important;
    }}
    [data-testid="stRadio"] label,
    [data-baseweb="radio"] label {{
        color:{TEXT} !important;
    }}
    /* ── Primary button ── */
    .stButton > button[kind="primary"] {{
        background: {ACCENT} !important;
        color:#fff !important;
        border:none !important;
        border-radius:9px !important;
        font-weight:700 !important;
        font-size:.92rem !important;
        box-shadow: 0 4px 14px rgba(14,165,233,.3) !important;
        transition:all .2s !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 6px 22px rgba(14,165,233,.45) !important;
        transform:translateY(-1px);
    }}
    /* ── Alert ── */
    [data-testid="stAlert"] {{
        background: rgba(14,165,233,.06) !important;
        border:1px solid rgba(14,165,233,.2) !important;
        border-radius:10px !important;
        color:{TEXT} !important;
    }}
    hr.soft {{ border:none; border-top:1px solid {BORDER}; margin:1.2rem 0; }}
    hr {{ border-color:{BORDER} !important; }}
    .chart-card-title {{
        font-family:'Space Grotesk',sans-serif;
        font-size:.88rem; font-weight:600;
        color:{TEXT}; margin:0 0 .2rem;
        padding:.6rem 1rem 0;
    }}
    /* ── Sidebar radio — remove tick marks, highlight active ── */
    [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {{
        display: none !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="radio"] {{
        padding: .15rem .4rem !important;
        border-radius: 6px !important;
        transition: background .15s;
        margin-bottom: 1px !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {{
        background: rgba(14,165,233,.13) !important;
        border-radius: 6px !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) label,
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) [data-testid="stMarkdownContainer"] p {{
        color: #0ea5e9 !important;
        font-weight: 600 !important;
    }}
    /* ── Sidebar logo ── */
    .sidebar-logo {{
        display:flex; align-items:center; gap:.6rem;
        margin-bottom:1.5rem;
        padding-bottom:1.1rem;
        border-bottom:1px solid {BORDER};
    }}
    .sidebar-logo-icon {{
        width:34px; height:34px;
        background:linear-gradient(135deg,{ACCENT},{ACCENT3});
        border-radius:9px;
        display:flex; align-items:center; justify-content:center;
        font-size:1rem;
    }}
    .sidebar-logo-name {{
        font-family:'Space Grotesk',sans-serif;
        font-weight:700; font-size:.95rem;
        color:{TEXT} !important; line-height:1.15;
    }}
    .sidebar-logo-tag {{
        font-size:.65rem; color:{TEXT_MUTED} !important;
        font-family:'JetBrains Mono',monospace;
    }}
    </style>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Plotly theme
# ---------------------------------------------------------------------------
def style_figure(fig, height: int | None = CHART_H_GRID, dual_y: bool = False) -> None:
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Space Grotesk, sans-serif", size=11, color=TEXT_MUTED),
        title=dict(font=dict(size=13, color=TEXT, family="Space Grotesk, sans-serif"),
                   x=0, pad=dict(l=12, t=4)),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafafa",
        height=height,
        margin=dict(t=52, l=56, r=32, b=52),
        hoverlabel=dict(bgcolor="#1e293b", font_size=12,
                        font_family="JetBrains Mono, monospace",
                        font_color="#f8fafc", bordercolor="#334155"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1,
                    font=dict(family="Space Grotesk, sans-serif", size=11),
                    bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
                     tickfont=dict(family="JetBrains Mono, monospace", size=10, color=TEXT_MUTED),
                     linecolor=BORDER)
    if not dual_y:
        fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
                         tickfont=dict(family="JetBrains Mono, monospace", size=10, color=TEXT_MUTED),
                         linecolor=BORDER)


def figure_dual_axis_global_trends(yearly: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=yearly["Year"], y=yearly[COL_ACCESS],
        name="Electricity access %",
        mode="lines+markers",
        line=dict(color=ACCENT, width=2.5),
        marker=dict(size=6, symbol="circle"),
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=yearly["Year"], y=yearly[COL_CO2],
        name="CO₂ (kt)",
        mode="lines+markers",
        line=dict(color=ACCENT2, width=2.5),
        marker=dict(size=6, symbol="circle"),
    ), secondary_y=True)
    fig.update_xaxes(title_text="Year", showgrid=True, gridcolor="#f1f5f9")
    fig.update_yaxes(title_text="Electricity access (%)", secondary_y=False,
                     showgrid=True, gridcolor="#f1f5f9", zeroline=False,
                     tickfont=dict(family="JetBrains Mono, monospace", size=10, color=TEXT_MUTED))
    fig.update_yaxes(title_text="CO₂ emissions (kt)", secondary_y=True,
                     showgrid=False, zeroline=False,
                     tickfont=dict(family="JetBrains Mono, monospace", size=10, color=TEXT_MUTED))
    fig.update_layout(
        title="Global average: electricity access vs CO₂ (dual axis)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    style_figure(fig, height=CHART_H_TALL, dual_y=True)
    return fig


def short_corr_labels() -> dict[str, str]:
    return {
        "Access to electricity (% of population)": "Elec. access %",
        "Access to clean fuels for cooking": "Clean cooking %",
        COL_RENEW: "Renewable %",
        COL_CO2: "CO₂ (kt)",
        COL_GDP: "GDP / cap",
        COL_FOSSIL: "Fossil TWh",
        COL_NUCLEAR: "Nuclear TWh",
        COL_RENEW_ELEC: "Renew. TWh",
        COL_EI: "Energy intensity",
    }


# ---------------------------------------------------------------------------
# Data loading  ← KEY FIX: keep a raw copy before median imputation
# ---------------------------------------------------------------------------
@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (df_imputed, df_raw).
    df_imputed  — median-filled, used for ML and most charts.
    df_raw      — NaN kept, used for scatter charts so real variance shows.
    """
    candidate_files = ["global_energy_data.csv", "global_energy_data.csv.csv"]
    file_name = next((f for f in candidate_files if pd.io.common.file_exists(f)), None)
    if file_name is None:
        raise FileNotFoundError("Could not find 'global_energy_data.csv'.")

    df_raw = pd.read_csv(file_name)
    df_raw.columns = [str(c).replace("\n", " ").strip() for c in df_raw.columns]

    # Rename density column if present and coerce to numeric
    for col in df_raw.columns:
        if "Density" in col and "Km" in col:
            df_raw = df_raw.rename(columns={col: "density_per_km2"})
            df_raw["density_per_km2"] = pd.to_numeric(
                df_raw["density_per_km2"].astype(str)
                    .str.replace(",", "").str.strip(),
                errors="coerce",
            )
            break

    # Imputed copy for ML / aggregate charts
    df_imputed = df_raw.copy()
    num_cols = df_imputed.select_dtypes(include=["number"]).columns
    df_imputed[num_cols] = df_imputed[num_cols].fillna(df_imputed[num_cols].median())

    return df_imputed, df_raw


@st.cache_resource
def train_model(df: pd.DataFrame) -> RandomForestRegressor:
    features = [COL_GDP, COL_ACCESS]
    target   = COL_CO2
    data = df[features + [target]].dropna()
    model = RandomForestRegressor(n_estimators=300, random_state=42,
                                   max_depth=12, min_samples_split=4,
                                   min_samples_leaf=2)
    model.fit(data[features], data[target])
    return model


@st.cache_data
def evaluate_model(df: pd.DataFrame) -> dict:
    """Compute R², MAE and feature importances on training data."""
    from sklearn.metrics import r2_score, mean_absolute_error
    features = [COL_GDP, COL_ACCESS]
    target   = COL_CO2
    data = df[features + [target]].dropna()
    model = RandomForestRegressor(n_estimators=300, random_state=42,
                                   max_depth=12, min_samples_split=4,
                                   min_samples_leaf=2)
    model.fit(data[features], data[target])
    preds = model.predict(data[features])
    return {
        "r2":  r2_score(data[target], preds),
        "mae": mean_absolute_error(data[target], preds),
        "importances": dict(zip(features, model.feature_importances_)),
        "n": len(data),
    }


def build_download_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def format_number(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}"


def section_header(title: str, description: str) -> None:
    st.markdown(f'<p class="section-title">{title}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">{description}</p>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
def main() -> None:
    inject_global_styles()

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-wrap">
        <span class="hero-badge">⚡ UN SDG 7</span>
        <h1 class="hero-title">Affordable &amp; <span class="hl">Clean Energy</span></h1>
        <p class="hero-sub">
            Explore global electricity access, renewable share, and CO₂ emissions across nations and time.
            Switch views in the sidebar, filter by year, and download the cleaned dataset.
        </p>
        <div class="hero-pills">
            <span class="hero-pill">global_energy_data.csv</span>
            <span class="hero-pill">2000 – 2020 focus</span>
            <span class="hero-pill">RandomForest · Plotly · Streamlit</span>
        </div>
    </div>""", unsafe_allow_html=True)

    df, df_raw = load_data()   # df = imputed, df_raw = original NaNs kept
    model      = train_model(df)
    model_eval = evaluate_model(df)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    st.sidebar.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">⚡</div>
        <div>
            <div class="sidebar-logo-name">SDG 7</div>
            <div class="sidebar-logo-tag">energy dashboard</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Sidebar nav — single radio, CSS hides tick marks ────────────────────────
    st.sidebar.markdown(
        "<p style='margin:.5rem 0 .15rem;font-size:.62rem;font-weight:700;"
        "text-transform:uppercase;letter-spacing:.12em;color:#0ea5e9;'>"
        "EDA — Exploratory Analysis</p>",
        unsafe_allow_html=True)

    section = st.sidebar.radio(
        "nav",
        [
            "① Energy Mix",
            "② Trend Line",
            "③ KDE Density",
            "④ Correlation",
            "⑤ Generation",
            "⑥ Energy Intensity",
            "── Advanced Visualisation",
            "Dashboard",
            "Multi-layer",
            "World Map",
            "── AI Model",
            "AI Predictions",
        ],
        label_visibility="collapsed",
        key="main_nav",
    )

    if section.startswith("──"):
        section = "Dashboard"

    st.sidebar.markdown('<hr class="soft"/>', unsafe_allow_html=True)
    st.sidebar.caption("Export the median-imputed dataset.")
    st.sidebar.download_button(
        "⬇ Download cleaned CSV",
        data=build_download_bytes(df),
        file_name="global_energy_data_cleaned.csv",
        mime="text/csv",
        use_container_width=True,
    )
    plot_cfg = {"displayModeBar": True, "displaylogo": False, "scrollZoom": True}

    # =========================================================================
    # =========================================================================
    if section == "Dashboard":
        import numpy as np
        from scipy.stats import gaussian_kde

        year_min = int(df["Year"].min())
        year_max = int(df["Year"].max())
        y_lo = max(year_min, ASSIGN_Y0)
        y_hi = min(year_max, ASSIGN_Y1)
        region_col = next((c for c in df.columns
                           if "region" in c.lower() or "continent" in c.lower()), None)

        # ── Compact horizontal filter bar (1 row, no sidebar column) ──────────
        st.markdown('''<div style="background:#f8fafc;border:1px solid #e2e8f0;
            border-radius:10px;padding:.55rem 1rem .45rem;margin-bottom:.7rem;">
            <span style="font-family:'Space Grotesk',sans-serif;font-size:.68rem;
            font-weight:700;text-transform:uppercase;letter-spacing:.1em;
            color:#0ea5e9;">⚙ Filters</span></div>''', unsafe_allow_html=True)

        fc1, fc2, fc3, fc4 = st.columns([1.4, 1.2, 1.6, 1.4], gap="small")
        with fc1:
            selected_year = st.slider("Year", min_value=y_lo, max_value=y_hi,
                                      value=y_hi, key="ia_year")
        with fc2:
            top_n = st.selectbox("Top-N", [5, 10, 15, 20], index=1, key="ia_topn",
                                 label_visibility="visible")
        with fc3:
            energy_metric = st.selectbox("Energy metric",
                                         ["Electricity access", "Renewable share", "Clean cooking"],
                                         index=0, key="ia_metric")
        with fc4:
            if region_col:
                all_regions = sorted(df[region_col].dropna().unique().tolist())
                selected_regions = st.multiselect("Region", all_regions,
                                                   default=all_regions, key="ia_region",
                                                   placeholder="All")
            else:
                selected_regions = None
                st.caption("No region column found")

        metric_map = {
            "Electricity access": COL_ACCESS,
            "Renewable share":    COL_RENEW,
            "Clean cooking":      "Access to clean fuels for cooking",
        }
        chosen_metric_col = metric_map[energy_metric]

        # ── Apply filters ─────────────────────────────────────────────────────
        year_data_raw = df_raw[df_raw["Year"] == selected_year].copy()
        year_data     = df[df["Year"] == selected_year].copy()
        df_win        = df[(df["Year"] >= ASSIGN_Y0) & (df["Year"] <= ASSIGN_Y1)].copy()
        df_win_raw    = df_raw[(df_raw["Year"] >= ASSIGN_Y0) & (df_raw["Year"] <= ASSIGN_Y1)].copy()

        if region_col and selected_regions:
            year_data_raw = year_data_raw[year_data_raw[region_col].isin(selected_regions)]
            year_data     = year_data[year_data[region_col].isin(selected_regions)]
            df_win        = df_win[df_win[region_col].isin(selected_regions)]
            df_win_raw    = df_win_raw[df_win_raw[region_col].isin(selected_regions)]

        # ── KPI strip ─────────────────────────────────────────────────────────
        k1, k2, k3, k4 = st.columns(4, gap="small")
        _h = f"Filtered averages for {selected_year}."
        k1.metric("⚡ Electricity access",
                  f"{format_number(year_data[COL_ACCESS].mean(),1)}%", help=_h)
        k2.metric("💨 Avg CO₂",
                  f"{format_number(year_data[COL_CO2].mean(),0)} kt", help=_h)
        k3.metric("🌱 Renewable share",
                  f"{format_number(year_data[COL_RENEW].mean(),1)}%", help=_h)
        k4.metric("💰 GDP / capita",
                  f"${format_number(year_data[COL_GDP].mean(),0)}", help=_h)

        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

        # ── Explore button ─────────────────────────────────────────────────────
        exp_col, _ = st.columns([1, 5], gap="small")
        with exp_col:
            if st.button("Explore", type="primary", use_container_width=True):
                st.toast("Scroll down to explore all 6 charts!", icon="📊")

        # ══ 6-CHART GRID  —  2 rows × 3 columns, compact height ═══════════════
        GRID_H = 265   # shorter so all 6 fit without scrolling

        row1_a, row1_b, row1_c = st.columns(3, gap="small")
        row2_a, row2_b, row2_c = st.columns(3, gap="small")

        # ① Stacked area — energy mix trend
        with row1_a:
            with st.container(border=True):
                st.markdown('<p class="chart-card-title">① Energy mix (TWh)</p>',
                            unsafe_allow_html=True)
                src_cols = [c for c in [COL_FOSSIL, COL_NUCLEAR, COL_RENEW_ELEC]
                            if c in df_win.columns]
                if src_cols:
                    area_yr = df_win.groupby("Year", as_index=False)[src_cols].sum().sort_values("Year")
                    area_melt = area_yr.melt(id_vars=["Year"], var_name="Source", value_name="TWh")
                    area_melt["Source"] = (area_melt["Source"]
                                           .str.replace("Electricity from ", "", regex=False)
                                           .str.replace(r" \(TWh\)$", "", regex=True))
                    af = px.area(area_melt, x="Year", y="TWh", color="Source",
                                 color_discrete_map={"fossil fuels": "#94a3b8",
                                                     "nuclear": ACCENT2, "renewables": ACCENT})
                    af.update_traces(line=dict(width=1.2))
                    af.update_layout(legend=dict(orientation="h", y=1.02, x=1,
                                                 xanchor="right", font=dict(size=9)),
                                     title=None)
                    style_figure(af, height=GRID_H)
                    st.plotly_chart(af, use_container_width=True, config=plot_cfg)

        # ② Trend line with std band
        with row1_b:
            with st.container(border=True):
                st.markdown(f'<p class="chart-card-title">② {energy_metric} trend</p>',
                            unsafe_allow_html=True)
                ga = df_win.groupby("Year", as_index=False)[chosen_metric_col].mean().sort_values("Year")
                std_v = df_win.groupby("Year")[chosen_metric_col].std().reindex(ga["Year"]).fillna(0).values
                lf = px.line(ga, x="Year", y=chosen_metric_col, markers=True,
                             labels={chosen_metric_col: energy_metric})
                lf.update_traces(line=dict(color=ACCENT, width=2), marker=dict(size=5, color=ACCENT))
                lf.add_traces([go.Scatter(
                    x=list(ga["Year"]) + list(ga["Year"])[::-1],
                    y=list(ga[chosen_metric_col]+std_v) + list((ga[chosen_metric_col]-std_v).clip(lower=0))[::-1],
                    fill="toself", fillcolor="rgba(14,165,233,0.10)",
                    line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip")])
                lf.update_layout(title=None)
                style_figure(lf, height=GRID_H)
                st.plotly_chart(lf, use_container_width=True, config=plot_cfg)

        # ③ KDE density + rug
        with row1_c:
            with st.container(border=True):
                st.markdown(f'<p class="chart-card-title">③ {energy_metric} density</p>',
                            unsafe_allow_html=True)
                dens_vals = year_data_raw[chosen_metric_col].dropna().values
                if len(dens_vals) > 3:
                    kde_fn  = gaussian_kde(dens_vals, bw_method="scott")
                    xr      = np.linspace(dens_vals.min(), dens_vals.max(), 300)
                    yk      = kde_fn(xr)
                    df_kde  = go.Figure()
                    df_kde.add_trace(go.Scatter(x=xr, y=yk, mode="lines",
                                                fill="tozeroy",
                                                fillcolor="rgba(14,165,233,0.12)",
                                                line=dict(color=ACCENT, width=2)))
                    df_kde.add_trace(go.Scatter(
                        x=dens_vals, y=[-yk.max()*0.04]*len(dens_vals),
                        mode="markers",
                        marker=dict(symbol="line-ns-open", size=8, color=ACCENT,
                                    opacity=0.3, line=dict(width=1, color=ACCENT)),
                        showlegend=False))
                    df_kde.add_vline(x=float(np.mean(dens_vals)), line_dash="dash",
                                     line_color=ACCENT2, line_width=1.5,
                                     annotation_text=f"M={np.mean(dens_vals):.1f}",
                                     annotation_font=dict(size=8, color=ACCENT2))
                    df_kde.update_layout(showlegend=False, title=None,
                                         xaxis_title=energy_metric, yaxis_title="Density",
                                         paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                                         height=GRID_H,
                                         margin=dict(t=24, l=44, r=12, b=40),
                                         font=dict(family="Space Grotesk, sans-serif",
                                                   size=9, color=TEXT_MUTED),
                                         xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
                                         yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False))
                    st.plotly_chart(df_kde, use_container_width=True, config=plot_cfg)
                else:
                    st.info("Not enough data.")

        # ④ Bubble correlation heatmap
        with row2_a:
            with st.container(border=True):
                st.markdown('<p class="chart-card-title">④ Correlation matrix</p>',
                            unsafe_allow_html=True)
                hcols = [c for c in [COL_ACCESS, "Access to clean fuels for cooking",
                         COL_RENEW, COL_CO2, COL_GDP, COL_FOSSIL,
                         COL_NUCLEAR, COL_RENEW_ELEC, COL_EI] if c in df_win.columns]
                lbl  = short_corr_labels()
                corr = df_win[hcols].corr(numeric_only=True).rename(index=lbl, columns=lbl)
                n    = len(corr)
                xs, ys = list(corr.columns), list(corr.index)
                bx, by, br, bc, bt, bcd = [], [], [], [], [], []
                for ri, rl in enumerate(ys):
                    for ci, cl in enumerate(xs):
                        v = corr.loc[rl, cl]
                        bx.append(ci); by.append(ri)
                        br.append(abs(v)*28+3); bc.append(v)
                        bt.append(f"{v:.2f}"); bcd.append([rl, cl])
                hm = go.Figure()
                hm.add_trace(go.Scatter(
                    x=bx, y=by, mode="markers+text",
                    marker=dict(size=br, color=bc, sizemode="diameter",
                                colorscale=[[0,"#dc2626"],[.5,"#f8fafc"],[1,"#0369a1"]],
                                cmin=-1, cmax=1,
                                colorbar=dict(thickness=7, len=0.5,
                                              tickfont=dict(size=7), x=1.02),
                                line=dict(width=0.4, color="#e2e8f0")),
                    text=bt,
                    textfont=dict(size=6, color="#374151"),
                    textposition="middle center",
                    hovertemplate="<b>%{customdata[0]}</b> vs <b>%{customdata[1]}</b><br>r=%{marker.color:.3f}<extra></extra>",
                    customdata=bcd))
                hm.update_layout(
                    paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                    height=GRID_H, margin=dict(t=12, b=56, l=64, r=36),
                    xaxis=dict(tickmode="array", tickvals=list(range(n)), ticktext=xs,
                               tickangle=40, showgrid=False, zeroline=False,
                               tickfont=dict(size=6.5, color="#475569")),
                    yaxis=dict(tickmode="array", tickvals=list(range(n)), ticktext=ys,
                               autorange="reversed", showgrid=False, zeroline=False,
                               tickfont=dict(size=6.5, color="#475569")),
                    font=dict(family="Space Grotesk, sans-serif", size=8))
                for k in range(n+1):
                    hm.add_hline(y=k-.5, line_color="#f1f5f9", line_width=0.6)
                    hm.add_vline(x=k-.5, line_color="#f1f5f9", line_width=0.6)
                st.plotly_chart(hm, use_container_width=True, config=plot_cfg)

        # ⑤ Generation by source stacked bar
        with row2_b:
            with st.container(border=True):
                st.markdown('<p class="chart-card-title">⑤ Generation by source</p>',
                            unsafe_allow_html=True)
                src_cols = [c for c in [COL_FOSSIL, COL_NUCLEAR, COL_RENEW_ELEC]
                            if c in df_win.columns]
                if src_cols:
                    ey = df_win.groupby("Year", as_index=False)[src_cols].sum().sort_values("Year")
                    el = ey.melt(id_vars=["Year"], var_name="Source", value_name="TWh")
                    el["Source"] = (el["Source"]
                                    .str.replace("Electricity from ", "", regex=False)
                                    .str.replace(r" \(TWh\)$", "", regex=True))
                    bf = px.bar(el, x="Year", y="TWh", color="Source", barmode="stack",
                                color_discrete_map={"fossil fuels":"#94a3b8",
                                                    "nuclear":ACCENT2, "renewables":ACCENT})
                    bf.update_layout(legend=dict(orientation="h", y=1.02, x=1,
                                                 xanchor="right", font=dict(size=9)),
                                     title=None)
                    style_figure(bf, height=GRID_H)
                    st.plotly_chart(bf, use_container_width=True, config=plot_cfg)

        # ⑥ Energy intensity box plot
        with row2_c:
            with st.container(border=True):
                st.markdown('<p class="chart-card-title">⑥ Energy intensity by year</p>',
                            unsafe_allow_html=True)
                if COL_EI in df_win.columns:
                    bx_ei = px.box(df_win, x="Year", y=COL_EI,
                                   points="suspectedoutliers",
                                   labels={COL_EI: "MJ/$GDP"},
                                   color_discrete_sequence=[ACCENT3])
                    bx_ei.update_layout(title=None)
                    bx_ei.update_xaxes(tickangle=45, tickfont=dict(size=7))
                    style_figure(bx_ei, height=GRID_H)
                    st.plotly_chart(bx_ei, use_container_width=True, config=plot_cfg)


    # ETHICAL BIAS  —  standalone chart section
    # =========================================================================
    elif section == "① Energy Mix":
        section_header("① Energy Mix Trend", "Stacked area — global electricity generation by source (TWh), 2000–2020.")
        df_win_c = df[(df["Year"] >= ASSIGN_Y0) & (df["Year"] <= ASSIGN_Y1)].copy()
        src_cols = [c for c in [COL_FOSSIL, COL_NUCLEAR, COL_RENEW_ELEC] if c in df_win_c.columns]
        if src_cols:
            with st.container(border=True):
                area_yr = df_win_c.groupby("Year", as_index=False)[src_cols].sum().sort_values("Year")
                area_melt = area_yr.melt(id_vars=["Year"], var_name="Source", value_name="TWh")
                area_melt["Source"] = (area_melt["Source"].str.replace("Electricity from ", "", regex=False).str.replace(r" \(TWh\)$", "", regex=True))
                af = px.area(area_melt, x="Year", y="TWh", color="Source",
                             title="Global electricity generation by source (TWh) — 2000–2020",
                             color_discrete_map={"fossil fuels":"#94a3b8","nuclear":ACCENT2,"renewables":ACCENT})
                af.update_traces(line=dict(width=1.5))
                af.update_layout(legend=dict(orientation="h", y=1.02, x=1, xanchor="right"))
                style_figure(af, height=500)
                st.plotly_chart(af, use_container_width=True, config=plot_cfg)
                st.caption("Fossil fuels grow in absolute TWh despite renewable growth — showing global demand is outpacing the clean energy transition.")


    elif section == "② Trend Line":
        section_header("② Energy Metric Trend", "Global average trend with ±1 standard deviation band — select a metric below.")
        import numpy as np
        fc1, fc2 = st.columns([1.5, 2], gap="small")
        with fc1:
            em2 = st.selectbox("Energy metric", ["Electricity access","Renewable share","Clean cooking"], key="c2_em")
        metric_map2 = {"Electricity access": COL_ACCESS, "Renewable share": COL_RENEW, "Clean cooking": "Access to clean fuels for cooking"}
        col2 = metric_map2[em2]
        df_win_c2 = df[(df["Year"] >= ASSIGN_Y0) & (df["Year"] <= ASSIGN_Y1)].copy()
        with st.container(border=True):
            ga = df_win_c2.groupby("Year", as_index=False)[col2].mean().sort_values("Year")
            std_v = df_win_c2.groupby("Year")[col2].std().reindex(ga["Year"]).fillna(0).values
            lf = px.line(ga, x="Year", y=col2, markers=True,
                         title=f"Global average — {em2} (2000–2020)",
                         labels={col2: em2})
            lf.update_traces(line=dict(color=ACCENT, width=2.5), marker=dict(size=7, color=ACCENT))
            lf.add_traces([go.Scatter(
                x=list(ga["Year"])+list(ga["Year"])[::-1],
                y=list(ga[col2]+std_v)+list((ga[col2]-std_v).clip(lower=0))[::-1],
                fill="toself", fillcolor="rgba(14,165,233,0.10)",
                line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip")])
            style_figure(lf, height=500)
            st.plotly_chart(lf, use_container_width=True, config=plot_cfg)
            st.caption("Shaded band = ±1 std deviation. Wide band means high inequality between countries — the mean alone is misleading.")


    elif section == "③ KDE Density":
        section_header("③ KDE Density Distribution", "Kernel density estimate showing how countries are distributed across the chosen metric.")
        import numpy as np
        from scipy.stats import gaussian_kde
        fc1, fc2, fc3 = st.columns([1.5, 1.5, 2], gap="small")
        with fc1:
            yr3 = st.slider("Year", min_value=max(int(df["Year"].min()),ASSIGN_Y0), max_value=min(int(df["Year"].max()),ASSIGN_Y1), value=min(int(df["Year"].max()),ASSIGN_Y1), key="c3_yr")
        with fc2:
            em3 = st.selectbox("Energy metric", ["Electricity access","Renewable share","Clean cooking"], key="c3_em")
        metric_map3 = {"Electricity access": COL_ACCESS, "Renewable share": COL_RENEW, "Clean cooking": "Access to clean fuels for cooking"}
        col3 = metric_map3[em3]
        yr_raw3 = df_raw[df_raw["Year"] == yr3].copy()
        with st.container(border=True):
            dens_vals = yr_raw3[col3].dropna().values
            if len(dens_vals) > 3:
                kde_fn = gaussian_kde(dens_vals, bw_method="scott")
                xr = np.linspace(dens_vals.min(), dens_vals.max(), 300)
                yk = kde_fn(xr)
                mean_v = float(np.mean(dens_vals))
                med_v  = float(np.median(dens_vals))
                dfig = go.Figure()
                dfig.add_trace(go.Scatter(x=xr, y=yk, mode="lines", fill="tozeroy",
                                          fillcolor="rgba(14,165,233,0.12)",
                                          line=dict(color=ACCENT, width=2.5), name="KDE"))
                dfig.add_trace(go.Scatter(x=dens_vals, y=[-yk.max()*0.04]*len(dens_vals),
                                          mode="markers",
                                          marker=dict(symbol="line-ns-open", size=10, color=ACCENT,
                                                      opacity=0.35, line=dict(width=1.2, color=ACCENT)),
                                          name="Countries", showlegend=False))
                dfig.add_vline(x=mean_v, line_dash="dash", line_color=ACCENT2, line_width=2,
                               annotation_text=f"Mean {mean_v:.1f}", annotation_position="top right",
                               annotation_font=dict(size=10, color=ACCENT2))
                dfig.add_vline(x=med_v, line_dash="dot", line_color=ACCENT3, line_width=2,
                               annotation_text=f"Median {med_v:.1f}", annotation_position="bottom right",
                               annotation_font=dict(size=10, color=ACCENT3))
                dfig.update_layout(title=f"{em3} distribution — {yr3}",
                                   xaxis_title=em3, yaxis_title="Density",
                                   showlegend=False, paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                                   height=500, margin=dict(t=52, l=60, r=24, b=52),
                                   font=dict(family="Space Grotesk, sans-serif", size=11, color=TEXT_MUTED),
                                   xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
                                   yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
                                   hoverlabel=dict(bgcolor="#1e293b", font_color="#f8fafc", font_size=12))
                st.plotly_chart(dfig, use_container_width=True, config=plot_cfg)
                st.caption("Rug ticks at bottom = individual countries. Bimodal curve = two clusters of countries (near 100% and near 20–40%).")


    elif section == "④ Correlation":
        section_header("④ Indicator Correlation Matrix", "Bubble heatmap — circle size = strength |r|, colour = direction (blue positive, red negative).")
        df_win_c4 = df[(df["Year"] >= ASSIGN_Y0) & (df["Year"] <= ASSIGN_Y1)].copy()
        with st.container(border=True):
            hcols = [c for c in [COL_ACCESS, "Access to clean fuels for cooking", COL_RENEW, COL_CO2, COL_GDP, COL_FOSSIL, COL_NUCLEAR, COL_RENEW_ELEC, COL_EI] if c in df_win_c4.columns]
            lbl  = short_corr_labels()
            corr = df_win_c4[hcols].corr(numeric_only=True).rename(index=lbl, columns=lbl)
            n    = len(corr)
            xs, ys = list(corr.columns), list(corr.index)
            bx, by, br, bc, bt, bcd = [], [], [], [], [], []
            for ri, rl in enumerate(ys):
                for ci, cl in enumerate(xs):
                    v = corr.loc[rl, cl]
                    bx.append(ci); by.append(ri)
                    br.append(abs(v)*42+4); bc.append(v)
                    bt.append(f"{v:.2f}"); bcd.append([rl, cl])
            hm4 = go.Figure()
            hm4.add_trace(go.Scatter(x=bx, y=by, mode="markers+text",
                marker=dict(size=br, color=bc, sizemode="diameter",
                            colorscale=[[0,"#dc2626"],[.5,"#f8fafc"],[1,"#0369a1"]],
                            cmin=-1, cmax=1,
                            colorbar=dict(title=dict(text="r"), thickness=12, len=0.7,
                                         tickfont=dict(size=9), tickvals=[-1,-0.5,0,0.5,1]),
                            line=dict(width=0.5, color="#e2e8f0")),
                text=bt, textfont=dict(size=8, color="#374151"), textposition="middle center",
                hovertemplate="<b>%{customdata[0]}</b> vs <b>%{customdata[1]}</b><br>r = %{marker.color:.3f}<extra></extra>",
                customdata=bcd))
            hm4.update_layout(
                title="Indicator correlation matrix (2000–2020)",
                paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
                height=520, margin=dict(t=52, b=80, l=90, r=60),
                xaxis=dict(tickmode="array", tickvals=list(range(n)), ticktext=xs,
                           tickangle=38, showgrid=False, zeroline=False,
                           tickfont=dict(size=9, color="#475569", family="Space Grotesk, sans-serif")),
                yaxis=dict(tickmode="array", tickvals=list(range(n)), ticktext=ys,
                           autorange="reversed", showgrid=False, zeroline=False,
                           tickfont=dict(size=9, color="#475569", family="Space Grotesk, sans-serif")),
                font=dict(family="Space Grotesk, sans-serif", size=10),
                hoverlabel=dict(bgcolor="#1e293b", font_color="#f8fafc", font_size=12))
            for k in range(n+1):
                hm4.add_hline(y=k-.5, line_color="#f1f5f9", line_width=0.8)
                hm4.add_vline(x=k-.5, line_color="#f1f5f9", line_width=0.8)
            st.plotly_chart(hm4, use_container_width=True, config=plot_cfg)
            st.caption("Strong positive (large blue): GDP vs electricity access (r≈0.71). Strong negative: energy intensity vs GDP (r≈−0.34) — richer countries use energy more efficiently.")


    elif section == "⑤ Generation":
        section_header("⑤ Electricity Generation by Source", "Stacked bar chart — global TWh per source per year (2000–2020).")
        df_win_c5 = df[(df["Year"] >= ASSIGN_Y0) & (df["Year"] <= ASSIGN_Y1)].copy()
        src_cols = [c for c in [COL_FOSSIL, COL_NUCLEAR, COL_RENEW_ELEC] if c in df_win_c5.columns]
        if src_cols:
            with st.container(border=True):
                ey = df_win_c5.groupby("Year", as_index=False)[src_cols].sum().sort_values("Year")
                el = ey.melt(id_vars=["Year"], var_name="Source", value_name="TWh")
                el["Source"] = (el["Source"].str.replace("Electricity from ", "", regex=False).str.replace(r" \(TWh\)$", "", regex=True))
                bf = px.bar(el, x="Year", y="TWh", color="Source", barmode="stack",
                            title="Global electricity generation by source (TWh) — 2000–2020",
                            color_discrete_map={"fossil fuels":"#94a3b8","nuclear":ACCENT2,"renewables":ACCENT})
                bf.update_layout(legend=dict(orientation="h", y=1.02, x=1, xanchor="right"))
                style_figure(bf, height=500)
                st.plotly_chart(bf, use_container_width=True, config=plot_cfg)
                st.caption("Renewables grow post-2015 but fossil fuels also grow in absolute terms — global electricity demand outpacing the clean energy transition.")


    elif section == "⑥ Energy Intensity":
        section_header("⑥ Energy Intensity by Year", "Box plot — distribution of energy intensity (MJ per $2017 PPP GDP) across all countries.")
        df_win_c6 = df[(df["Year"] >= ASSIGN_Y0) & (df["Year"] <= ASSIGN_Y1)].copy()
        if COL_EI in df_win_c6.columns:
            with st.container(border=True):
                bx_ei = px.box(df_win_c6, x="Year", y=COL_EI,
                               points="suspectedoutliers",
                               title="Energy intensity distribution — all countries (2000–2020)",
                               labels={COL_EI: "MJ / $2017 PPP GDP"},
                               color_discrete_sequence=[ACCENT3])
                bx_ei.update_xaxes(tickangle=45, tickfont=dict(size=9))
                style_figure(bx_ei, height=500)
                st.plotly_chart(bx_ei, use_container_width=True, config=plot_cfg)
                st.caption("Median declines each year — global efficiency improving. Persistent outliers = countries with energy-intensive industrial structure.")


    elif section == "Multi-layer":
        section_header("Multi-layer Visualization",
                       "Stacked bar (generation by source) with a trend line overlay — bar + line on the same axes.")

        df_win_ml = df[(df["Year"] >= ASSIGN_Y0) & (df["Year"] <= ASSIGN_Y1)].copy()

        with st.container(border=True):
            st.markdown(
                '<p class="chart-card-title">Global electricity generation by source (TWh) — bar + CO₂ trend line overlay</p>',
                unsafe_allow_html=True)

            src_cols = [c for c in [COL_FOSSIL, COL_NUCLEAR, COL_RENEW_ELEC]
                        if c in df_win_ml.columns]

            if src_cols and COL_CO2 in df_win_ml.columns:
                # Aggregate by year
                yr_src = (df_win_ml.groupby("Year", as_index=False)[src_cols].sum()
                                   .sort_values("Year"))
                yr_co2 = (df_win_ml.groupby("Year", as_index=False)[COL_CO2].mean()
                                   .sort_values("Year"))

                src_melt = yr_src.melt(id_vars=["Year"], var_name="Source", value_name="TWh")
                src_melt["Source"] = (src_melt["Source"]
                                      .str.replace("Electricity from ", "", regex=False)
                                      .str.replace(r" \(TWh\)$", "", regex=True))

                # ── Layer 1: Stacked bar ──────────────────────────────────────
                ml_fig = px.bar(
                    src_melt, x="Year", y="TWh", color="Source",
                    barmode="stack",
                    color_discrete_map={
                        "fossil fuels": "#94a3b8",
                        "nuclear":      ACCENT2,
                        "renewables":   ACCENT,
                    },
                    labels={"TWh": "Electricity Generation (TWh)"},
                )

                # ── Layer 2: CO₂ trend line overlaid on secondary Y-axis ──────
                ml_fig.add_trace(go.Scatter(
                    x=yr_co2["Year"],
                    y=yr_co2[COL_CO2],
                    mode="lines+markers",
                    name="Avg CO₂ (kt)",
                    yaxis="y2",
                    line=dict(color="#e11d48", width=2.5, dash="solid"),
                    marker=dict(size=6, color="#e11d48"),
                ))

                # ── Dual Y-axis layout ────────────────────────────────────────
                ml_fig.update_layout(
                    title="Electricity generation (bars) vs Average CO₂ trend (line) — 2000–2020",
                    yaxis=dict(
                        title="Electricity Generation (TWh)",
                        showgrid=True, gridcolor="#f1f5f9",
                        tickfont=dict(family="JetBrains Mono, monospace", size=10),
                    ),
                    yaxis2=dict(
                        title=dict(text="Avg National CO₂ (kt)", font=dict(color="#e11d48", size=11)),
                        overlaying="y",
                        side="right",
                        showgrid=False,
                        tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#e11d48"),
                    ),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                xanchor="right", x=1, font=dict(size=11)),
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#fafafa",
                    height=520,
                    margin=dict(t=56, l=60, r=72, b=52),
                    font=dict(family="Space Grotesk, sans-serif", size=11, color=TEXT_MUTED),
                    hoverlabel=dict(bgcolor="#1e293b", font_size=12,
                                    font_family="JetBrains Mono, monospace",
                                    font_color="#f8fafc"),
                )
                ml_fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
                                     tickfont=dict(family="JetBrains Mono, monospace", size=10))

                st.plotly_chart(ml_fig, use_container_width=True,
                                config={"displayModeBar": True, "displaylogo": False})

                st.caption(
                    "Multi-layer chart: stacked bars show electricity generation mix (TWh) per source per year. "
                    "The red line overlaid on the secondary Y-axis shows the average national CO₂ trend. "
                    "Both layers share the same X-axis (Year) — bar + line on the same chart."
                )


    # WORLD MAP  —  Animated choropleth with play button
    # =========================================================================
    elif section == "World Map":
        section_header("World Map — Electricity Access",
                       "Animated global map showing electricity access (%) from 2000–2020. Hit ▶ to play.")

        map_main, map_filt = st.columns([3.6, 1], gap="large")

        with map_filt:
            st.markdown("""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;
                        padding:1.1rem 1rem 1.3rem;">
              <p style="font-family:'Space Grotesk',sans-serif;font-size:.7rem;font-weight:700;
                         text-transform:uppercase;letter-spacing:.12em;color:#0ea5e9;
                         margin:0 0 1rem;">⚙ Map Options</p>
            """, unsafe_allow_html=True)

            map_metric = st.selectbox("Metric to display", [
                "Electricity access",
                "Renewable share",
                "CO₂ emissions",
                "Clean cooking access",
            ], key="map_metric")
            map_projection = st.selectbox("Projection", [
                "natural earth", "orthographic", "equirectangular", "mercator",
            ], key="map_proj")
            map_colorscale = st.selectbox("Colour scale", [
                "YlGn", "Blues", "RdYlGn", "Viridis", "Plasma", "Cividis",
            ], key="map_cs")
            st.markdown("</div>", unsafe_allow_html=True)

        map_metric_col = {
            "Electricity access":   COL_ACCESS,
            "Renewable share":      COL_RENEW,
            "CO₂ emissions":        COL_CO2,
            "Clean cooking access": "Access to clean fuels for cooking",
        }[map_metric]

        with map_main:
            map_df_all = df_raw[
                (df_raw["Year"] >= ASSIGN_Y0) & (df_raw["Year"] <= ASSIGN_Y1)
            ].dropna(subset=[map_metric_col, "Entity"]).copy()

            # KPI strip for latest year in map data
            latest_yr = int(map_df_all["Year"].max())
            latest    = map_df_all[map_df_all["Year"] == latest_yr]
            mk1, mk2, mk3 = st.columns(3, gap="small")
            mk1.metric(f"{map_metric} (avg {latest_yr})",
                       f"{format_number(latest[map_metric_col].mean(), 1)}")
            mk2.metric("Countries with data",
                       f"{latest['Entity'].nunique()}")
            mk3.metric("Year range", f"{int(map_df_all['Year'].min())}–{latest_yr}")

            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown(
                    f'''<div style="padding:.5rem 1rem 0;">
                    <span style="font-family:'Space Grotesk',sans-serif;font-size:.78rem;
                                 color:#64748b;">
                    Hit <b>▶</b> on the slider below the map to animate year-by-year
                    </span></div>''', unsafe_allow_html=True)

                # Animated choropleth — animation_frame drives the play button
                anim_choro = px.choropleth(
                    map_df_all.sort_values("Year"),
                    locations="Entity",
                    locationmode="country names",
                    color=map_metric_col,
                    hover_name="Entity",
                    hover_data={map_metric_col: ":.1f", "Year": True},
                    animation_frame="Year",
                    color_continuous_scale=map_colorscale,
                    range_color=[
                        float(map_df_all[map_metric_col].quantile(0.02)),
                        float(map_df_all[map_metric_col].quantile(0.98)),
                    ],
                    title=f"{map_metric} — animated {ASSIGN_Y0}–{ASSIGN_Y1}",
                    projection=map_projection,
                )
                anim_choro.update_geos(
                    showframe=False,
                    showcoastlines=True, coastlinecolor="#94a3b8", coastlinewidth=0.5,
                    showland=True,  landcolor="#f1f5f9",
                    showocean=True, oceancolor="#dbeafe",
                    showlakes=False, bgcolor="#ffffff",
                )
                anim_choro.update_layout(
                    paper_bgcolor="#ffffff",
                    height=580,
                    margin=dict(t=48, b=8, l=0, r=0),
                    font=dict(family="Space Grotesk, sans-serif", size=11),
                    coloraxis_colorbar=dict(
                        title=dict(text=map_metric[:14], font=dict(size=10)),
                        thickness=12, len=0.6,
                        tickfont=dict(size=9, family="JetBrains Mono, monospace"),
                    ),
                    # Style the animation slider
                    sliders=[dict(
                        currentvalue=dict(
                            prefix="Year: ",
                            font=dict(size=13, family="Space Grotesk, sans-serif",
                                      color="#0f172a"),
                        ),
                        pad=dict(t=12, b=8),
                        bgcolor="#f1f5f9",
                        bordercolor="#e2e8f0",
                        tickcolor="#cbd5e1",
                        font=dict(size=9, family="JetBrains Mono, monospace"),
                    )],
                    updatemenus=[dict(
                        type="buttons",
                        showactive=False,
                        y=0,
                        x=0.02,
                        xanchor="left",
                        yanchor="top",
                        pad=dict(t=8, r=8),
                        buttons=[
                            dict(label="▶  Play",
                                 method="animate",
                                 args=[None, dict(
                                     frame=dict(duration=700, redraw=True),
                                     fromcurrent=True,
                                     transition=dict(duration=200),
                                 )]),
                            dict(label="⏸ Pause",
                                 method="animate",
                                 args=[[None], dict(
                                     frame=dict(duration=0, redraw=False),
                                     mode="immediate",
                                     transition=dict(duration=0),
                                 )]),
                        ],
                        bgcolor="#ffffff",
                        bordercolor="#e2e8f0",
                        font=dict(size=12, family="Space Grotesk, sans-serif",
                                  color="#0f172a"),
                    )],
                )
                st.plotly_chart(anim_choro, use_container_width=True,
                                config={"displayModeBar": True, "displaylogo": False,
                                        "scrollZoom": True})


    # AI PREDICTIONS
    # =========================================================================
    else:
        section_header("AI predictions",
                       "Random Forest estimates CO₂ from GDP & electricity access — with model evaluation & uncertainty.")

        # ── Model evaluation metrics strip ────────────────────────────────────
        st.markdown("""
        <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:12px;
                    padding:.6rem 1rem .3rem;margin-bottom:.9rem;">
          <p style="font-family:'Space Grotesk',sans-serif;font-size:.7rem;font-weight:700;
                     text-transform:uppercase;letter-spacing:.1em;color:#0ea5e9;margin:0 0 .6rem;">
            Model evaluation metrics
          </p>
        """, unsafe_allow_html=True)
        e1, e2, e3, e4 = st.columns(4, gap="small")
        e1.metric("R² score",
                  f"{model_eval['r2']:.4f}",
                  help="Coefficient of determination — 1.0 = perfect fit")
        e2.metric("Mean Abs Error",
                  f"{format_number(model_eval['mae'], 1)} kt",
                  help="Average absolute error between predicted and actual CO₂")
        e3.metric("Training rows",
                  f"{model_eval['n']:,}",
                  help="Rows with valid GDP, access & CO₂ used for training")
        e4.metric("Features used",
                  "2",
                  help="gdp_per_capita · electricity access %")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)


        # Feature importance mini-bar
        with st.container(border=True):
            st.markdown('<p class="chart-card-title">Feature importance</p>',
                        unsafe_allow_html=True)
            imp = model_eval["importances"]
            fi_fig = px.bar(
                x=list(imp.values()), y=["GDP per capita", "Electricity access %"],
                orientation="h",
                labels={"x": "Importance", "y": "Feature"},
                title="RandomForest feature importances",
                color=list(imp.values()),
                color_continuous_scale="Blues",
            )
            fi_fig.update_layout(coloraxis_showscale=False,
                                 yaxis=dict(tickfont=dict(size=11)))
            style_figure(fi_fig, height=180)
            st.plotly_chart(fi_fig, use_container_width=True, config=plot_cfg)

        st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)

        # ── Prediction inputs ─────────────────────────────────────────────────
        with st.container(border=True):
            st.markdown("**Run a prediction**")
            g1, g2 = st.columns(2)
            with g1:
                gdp_input = st.number_input("GDP per capita (USD)",
                                            min_value=0.0, value=5000.0, step=100.0)
            with g2:
                energy_access_input = st.slider("Electricity access (% of population)",
                                                min_value=0.0, max_value=100.0,
                                                value=80.0, step=0.1)

            if st.button("Run prediction", type="primary", use_container_width=True):
                prediction = model.predict([[gdp_input, energy_access_input]])[0]
                margin = model_eval["mae"]
                st.success(
                    f"**Estimated CO₂ emissions:** `{format_number(float(prediction), 2)}` kt  "
                    f"±  `{format_number(margin, 1)}` kt (MAE)"
                )

            # Uncertainty disclaimer
            st.markdown('''
            <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;
                        padding:.7rem 1rem;margin-top:.6rem;">
              <p style="font-size:.82rem;color:#0369a1;margin:0;line-height:1.6;">
                <strong>Model uncertainty note:</strong> This prediction is an estimate
                based on historical trends (2000–2020) using only two input features
                (GDP per capita and electricity access). Actual CO₂ may vary significantly
                due to local policy changes, energy mix shifts, industrial structure,
                and factors not captured in this model. Use as a directional indicator only.
              </p>
            </div>''', unsafe_allow_html=True)

            st.caption(
                "Model: `RandomForestRegressor(n_estimators=300, max_depth=12)` — "
                "trained on median-imputed rows · features: GDP per capita, electricity access %."
            )


if __name__ == "__main__":
    main()