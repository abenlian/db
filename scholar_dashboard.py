"""Google Scholar Dashboard — Alexander Benlian

Run with:
    streamlit run scholar_dashboard.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from scholar_fetcher import fetch_author_data, load_cache

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scholar Dashboard · Alexander Benlian",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── colour palette ────────────────────────────────────────────────────────────
BLUE   = "#2563EB"
TEAL   = "#0D9488"
VIOLET = "#7C3AED"
AMBER  = "#D97706"
RED    = "#EF4444"

# ── global chart style ────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13, color="#334155"),
    hoverlabel=dict(bgcolor="white", font_size=13),
)

# ── CSS tweaks ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"]  { font-size: 2.4rem !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"]  { font-size: 0.85rem !important; color: #64748b !important; }
    [data-testid="stMetricDelta"]  { font-size: 0.9rem  !important; }
    .section-title { font-size: 1rem; font-weight: 600; color: #475569;
                     text-transform: uppercase; letter-spacing: 0.05em;
                     margin: 1.2rem 0 0.4rem; }
    hr { border: none; border-top: 1px solid #e2e8f0; margin: 1rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────────────────────────────────────────

def build_citation_df(cites_per_year: dict) -> pd.DataFrame:
    if not cites_per_year:
        return pd.DataFrame(columns=["year", "annual", "cumulative"])
    years  = sorted(int(y) for y in cites_per_year)
    annual = [cites_per_year[str(y)] for y in years]
    cumul  = list(np.cumsum(annual))
    return pd.DataFrame({"year": years, "annual": annual, "cumulative": cumul})


def build_pub_df(publications: list) -> pd.DataFrame:
    df = pd.DataFrame(publications)
    df.columns = [c.capitalize() for c in df.columns]
    df = df.rename(columns={"Venue": "Venue", "Citations": "Citations", "Year": "Year", "Title": "Title"})
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Chart builders
# ─────────────────────────────────────────────────────────────────────────────

def chart_citation_timeline(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df["year"], y=df["annual"],
            name="Annual citations",
            marker_color=BLUE, marker_opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Annual: %{y:,}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"], y=df["cumulative"],
            name="Cumulative citations",
            line=dict(color=TEAL, width=3),
            mode="lines+markers",
            marker=dict(size=6, color=TEAL),
            hovertemplate="<b>%{x}</b><br>Cumulative: %{y:,}<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="Citation history",
        legend=dict(orientation="h", y=1.1, x=0),
        hovermode="x unified",
        height=440,
        **CHART_LAYOUT,
    )
    fig.update_yaxes(title_text="Annual citations",     gridcolor="#e2e8f0", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative citations", gridcolor="#e2e8f0", secondary_y=True, showgrid=False)
    fig.update_xaxes(title_text="Year", dtick=1)
    return fig


def chart_yoy_growth(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["yoy"] = df["annual"].pct_change() * 100
    df = df.dropna()
    colors = [TEAL if v >= 0 else RED for v in df["yoy"]]

    fig = go.Figure(
        go.Bar(
            x=df["year"], y=df["yoy"].round(1),
            marker_color=colors,
            text=df["yoy"].round(1).astype(str) + "%",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="Year-over-year citation growth (%)",
        xaxis=dict(title="Year", dtick=1),
        yaxis=dict(title="YoY growth (%)", gridcolor="#e2e8f0", zeroline=True, zerolinecolor="#94a3b8"),
        height=360,
        **CHART_LAYOUT,
    )
    return fig


def chart_top_papers(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    top = df.nlargest(top_n, "Citations").copy()
    top["Label"] = top["Title"].str[:65].where(
        top["Title"].str.len() <= 65,
        top["Title"].str[:65] + "…",
    )

    fig = go.Figure(
        go.Bar(
            x=top["Citations"],
            y=top["Label"],
            orientation="h",
            marker_color=VIOLET,
            text=top["Citations"],
            textposition="outside",
            customdata=np.stack([top["Title"], top["Year"].fillna("n/a").astype(str)], axis=-1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Year: %{customdata[1]}<br>"
                "Citations: %{x:,}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=f"Top {top_n} most cited publications",
        xaxis=dict(title="Citations", gridcolor="#e2e8f0"),
        yaxis=dict(autorange="reversed"),
        height=max(420, top_n * 32),
        **CHART_LAYOUT,
    )
    return fig


def chart_pubs_per_year(df: pd.DataFrame) -> go.Figure:
    yearly = (
        df.dropna(subset=["Year"])
        .assign(Year=lambda d: d["Year"].astype(int))
        .groupby("Year")
        .size()
        .reset_index(name="Count")
    )
    fig = go.Figure(
        go.Bar(
            x=yearly["Year"], y=yearly["Count"],
            marker_color=AMBER,
            text=yearly["Count"],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Publications: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Publications per year",
        xaxis=dict(title="Year", dtick=1),
        yaxis=dict(title="# publications", gridcolor="#e2e8f0"),
        height=380,
        **CHART_LAYOUT,
    )
    return fig


def chart_bubble(df: pd.DataFrame) -> go.Figure:
    df2 = df.dropna(subset=["Year"]).copy()
    df2["Year"] = df2["Year"].astype(int)
    fig = px.scatter(
        df2,
        x="Year", y="Citations",
        size=df2["Citations"].clip(lower=1),
        color="Citations",
        color_continuous_scale="Blues",
        hover_data={"Title": True, "Year": True, "Citations": True, "Venue": True},
        title="Citation impact by publication year",
    )
    fig.update_layout(height=420, **CHART_LAYOUT)
    return fig


def chart_citation_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="Citations", nbins=30,
        title="Distribution of citations per paper",
        color_discrete_sequence=[BLUE],
    )
    fig.update_layout(
        xaxis=dict(title="Citations"),
        yaxis=dict(title="# papers", gridcolor="#e2e8f0"),
        height=360,
        **CHART_LAYOUT,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar(data: dict | None) -> bool:
    """Render sidebar controls.  Returns True if user clicked Refresh."""
    with st.sidebar:
        st.markdown("## 📚 Scholar Dashboard")
        st.markdown("---")

        cached = load_cache()
        if cached:
            st.success(f"Cached · {cached.get('fetched_date', '—')}")
        else:
            st.info("No cache — fetching live data…")

        refresh = st.button("🔄  Refresh from Google Scholar", use_container_width=True)

        st.markdown("---")
        st.markdown(
            "_Google Scholar may throttle automated requests. "
            "Cached data is reused for 24 hours._"
        )

        if data and data.get("interests"):
            st.markdown("---")
            st.markdown("**Research interests**")
            for interest in data["interests"]:
                st.markdown(f"- {interest}")

    return refresh


# ─────────────────────────────────────────────────────────────────────────────
# Main app
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── load data ─────────────────────────────────────────────────────────────
    if "data" not in st.session_state:
        with st.spinner("Loading Google Scholar data…"):
            try:
                st.session_state["data"] = fetch_author_data()
            except RuntimeError as exc:
                st.error(str(exc))
                st.info(
                    "Tip: make sure `scholarly` is installed (`pip install scholarly`) "
                    "and that your network can reach Google Scholar."
                )
                st.stop()

    data = st.session_state["data"]

    # ── sidebar ────────────────────────────────────────────────────────────────
    refresh = render_sidebar(data)
    if refresh:
        with st.spinner("Fetching fresh data from Google Scholar…"):
            try:
                st.session_state["data"] = fetch_author_data(force_refresh=True)
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

    # ── derived dataframes ─────────────────────────────────────────────────────
    cite_df = build_citation_df(data["cites_per_year"])
    pub_df  = build_pub_df(data["publications"])

    # ── demo-mode banner ───────────────────────────────────────────────────────
    if data.get("_demo"):
        st.warning(
            "**Demo mode** — Google Scholar is unreachable from this environment. "
            "Displaying representative data. Click **Refresh** in the sidebar once "
            "network access to Scholar is available.",
            icon="⚠️",
        )

    # ── header ─────────────────────────────────────────────────────────────────
    st.title(f"📚 {data['name']}")
    if data.get("affiliation"):
        st.caption(data["affiliation"])
    if data.get("email_domain"):
        st.caption(f"✉  @{data['email_domain']}")

    # ── KPIs — all-time ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">All-time metrics</div>', unsafe_allow_html=True)

    # delta: citations added in the most recent year with data
    last_year_label = ""
    last_year_cites = None
    if not cite_df.empty:
        max_year = int(cite_df["year"].max())
        last_year_cites = int(cite_df.loc[cite_df["year"] == max_year, "annual"].iloc[0])
        last_year_label = f"+{last_year_cites:,} in {max_year}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total citations", f"{data['total_citations']:,}", delta=last_year_label or None)
    c2.metric("h-index",         data["hindex"])
    c3.metric("i10-index",       data["i10index"])
    c4.metric("Publications",    len(data["publications"]))

    # ── KPIs — last 5 years ────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Last 5 years</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Citations (5y)",  f"{data['total_citations5y']:,}")
    m2.metric("h-index (5y)",    data["hindex5y"])
    m3.metric("i10-index (5y)",  data["i10index5y"])

    # share of all-time citations that come from the last 5 years
    if data["total_citations"] > 0:
        pct5y = data["total_citations5y"] / data["total_citations"] * 100
        m4.metric("5y / all-time citations", f"{pct5y:.1f}%")

    st.markdown("---")

    # ── tabs ───────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(
        ["📈  Citation timeline", "📄  Publications", "🔍  Deep dive"]
    )

    # ── Tab 1: Citation timeline ───────────────────────────────────────────────
    with tab1:
        if cite_df.empty:
            st.warning("No citation-per-year data available.")
        else:
            st.plotly_chart(chart_citation_timeline(cite_df), use_container_width=True)

            if len(cite_df) >= 2:
                st.plotly_chart(chart_yoy_growth(cite_df), use_container_width=True)

            # Summary stats table
            with st.expander("Citation data table"):
                display = cite_df.copy()
                display.columns = ["Year", "Annual citations", "Cumulative citations"]
                display["YoY growth (%)"] = display["Annual citations"].pct_change().mul(100).round(1)
                st.dataframe(display.sort_values("Year", ascending=False), hide_index=True, use_container_width=True)

    # ── Tab 2: Publications ────────────────────────────────────────────────────
    with tab2:
        if pub_df.empty:
            st.warning("No publication data available.")
        else:
            col_ctrl, col_spacer = st.columns([1, 3])
            with col_ctrl:
                top_n = st.slider("Number of papers to display", 5, min(50, len(pub_df)), 20, key="top_n")

            st.plotly_chart(chart_top_papers(pub_df, top_n), use_container_width=True)

            st.markdown("---")
            st.markdown("**Browse all publications**")

            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                min_cites = st.slider(
                    "Minimum citations",
                    0, int(pub_df["Citations"].max() or 0), 0,
                    key="min_cites",
                )
            with filter_col2:
                year_range = st.slider(
                    "Year range",
                    int(pub_df["Year"].dropna().min()),
                    int(pub_df["Year"].dropna().max()),
                    (int(pub_df["Year"].dropna().min()), int(pub_df["Year"].dropna().max())),
                    key="year_range",
                )

            filtered = pub_df[
                (pub_df["Citations"] >= min_cites)
                & (pub_df["Year"].isna() | pub_df["Year"].between(*year_range))
            ].sort_values("Citations", ascending=False)

            st.caption(f"Showing {len(filtered):,} of {len(pub_df):,} publications")
            st.dataframe(
                filtered[["Title", "Year", "Citations", "Venue"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Title":     st.column_config.TextColumn(width="large"),
                    "Year":      st.column_config.NumberColumn(format="%d", width="small"),
                    "Citations": st.column_config.NumberColumn(format="%d", width="small"),
                    "Venue":     st.column_config.TextColumn(width="medium"),
                },
            )

    # ── Tab 3: Deep dive ───────────────────────────────────────────────────────
    with tab3:
        if pub_df.empty:
            st.warning("No publication data available.")
        else:
            col_left, col_right = st.columns(2)
            with col_left:
                st.plotly_chart(chart_pubs_per_year(pub_df), use_container_width=True)
            with col_right:
                st.plotly_chart(chart_bubble(pub_df), use_container_width=True)

            st.plotly_chart(chart_citation_distribution(pub_df), use_container_width=True)

            # Quick stats
            st.markdown("---")
            st.markdown("**Quick statistics**")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Median citations / paper", int(pub_df["Citations"].median()))
            s2.metric("Mean citations / paper",   f"{pub_df['Citations'].mean():.1f}")
            s3.metric("Most cited paper",         f"{int(pub_df['Citations'].max()):,}")
            papers_with_cites = int((pub_df["Citations"] > 0).sum())
            s4.metric("Papers with ≥1 citation",  papers_with_cites)


if __name__ == "__main__":
    main()
