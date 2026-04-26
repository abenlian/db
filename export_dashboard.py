"""
Export the Scholar dashboard as a single self-contained HTML file.
All Plotly charts are embedded inline — no server needed.

Usage:
    python export_dashboard.py
    # → writes scholar_dashboard.html
"""

import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scholar_fetcher import load_cache, fetch_author_data

# ── colours ───────────────────────────────────────────────────────────────────
BLUE   = "#2563EB"
TEAL   = "#0D9488"
VIOLET = "#7C3AED"
AMBER  = "#D97706"
RED    = "#EF4444"

LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", size=13, color="#334155"),
    hoverlabel=dict(bgcolor="white", font_size=13),
    margin=dict(t=60, b=40, l=40, r=40),
)

# ── load data ─────────────────────────────────────────────────────────────────
data = load_cache() or fetch_author_data()

cpy   = data["cites_per_year"]
years = sorted(int(y) for y in cpy)
annual = [cpy[str(y)] for y in years]
cumul  = list(np.cumsum(annual))
cite_df = pd.DataFrame({"year": years, "annual": annual, "cumulative": cumul})

pubs = data["publications"]
pub_df = pd.DataFrame(pubs)
pub_df.columns = [c.capitalize() for c in pub_df.columns]

# ── build charts ──────────────────────────────────────────────────────────────

def citation_timeline():
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=cite_df["year"], y=cite_df["annual"],
                         name="Annual citations", marker_color=BLUE, opacity=0.85,
                         hovertemplate="<b>%{x}</b><br>Annual: %{y:,}<extra></extra>"),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=cite_df["year"], y=cite_df["cumulative"],
                             name="Cumulative citations",
                             line=dict(color=TEAL, width=3),
                             mode="lines+markers", marker=dict(size=6),
                             hovertemplate="<b>%{x}</b><br>Cumulative: %{y:,}<extra></extra>"),
                  secondary_y=True)
    fig.update_layout(title="Citation history (annual + cumulative)",
                      legend=dict(orientation="h", y=1.1),
                      hovermode="x unified", height=440, **LAYOUT)
    fig.update_yaxes(title_text="Annual citations",     gridcolor="#e2e8f0", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative citations", gridcolor="#e2e8f0", showgrid=False, secondary_y=True)
    fig.update_xaxes(title_text="Year", dtick=1)
    return fig


def yoy_growth():
    df = cite_df.copy()
    df["yoy"] = df["annual"].pct_change() * 100
    df = df.dropna()
    colors = [TEAL if v >= 0 else RED for v in df["yoy"]]
    fig = go.Figure(go.Bar(x=df["year"], y=df["yoy"].round(1),
                           marker_color=colors,
                           text=df["yoy"].round(1).astype(str) + "%",
                           textposition="outside",
                           hovertemplate="<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>"))
    fig.update_layout(title="Year-over-year citation growth (%)",
                      xaxis=dict(title="Year", dtick=1),
                      yaxis=dict(title="YoY growth (%)", gridcolor="#e2e8f0",
                                 zeroline=True, zerolinecolor="#94a3b8"),
                      height=360, **LAYOUT)
    return fig


def top_papers(n=20):
    top = pub_df.nlargest(n, "Citations").copy()
    top["Label"] = top["Title"].str[:65].where(
        top["Title"].str.len() <= 65, top["Title"].str[:65] + "…")
    fig = go.Figure(go.Bar(
        x=top["Citations"], y=top["Label"], orientation="h",
        marker_color=VIOLET, text=top["Citations"], textposition="outside",
        customdata=np.stack([top["Title"], top["Year"].fillna("n/a").astype(str)], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>Year: %{customdata[1]}<br>Citations: %{x:,}<extra></extra>"))
    fig.update_layout(title=f"Top {n} most cited publications",
                      xaxis=dict(title="Citations", gridcolor="#e2e8f0"),
                      yaxis=dict(autorange="reversed"),
                      height=max(420, n * 32), **LAYOUT)
    return fig


def pubs_per_year():
    yearly = (pub_df.dropna(subset=["Year"])
              .assign(Year=lambda d: d["Year"].astype(int))
              .groupby("Year").size().reset_index(name="Count"))
    fig = go.Figure(go.Bar(x=yearly["Year"], y=yearly["Count"],
                           marker_color=AMBER,
                           text=yearly["Count"], textposition="outside",
                           hovertemplate="<b>%{x}</b><br>Publications: %{y}<extra></extra>"))
    fig.update_layout(title="Publications per year",
                      xaxis=dict(title="Year", dtick=1),
                      yaxis=dict(title="# publications", gridcolor="#e2e8f0"),
                      height=380, **LAYOUT)
    return fig


def citation_bubble():
    df2 = pub_df.dropna(subset=["Year"]).copy()
    df2["Year"] = df2["Year"].astype(int)
    fig = px.scatter(df2, x="Year", y="Citations",
                     size=df2["Citations"].clip(lower=1),
                     color="Citations", color_continuous_scale="Blues",
                     hover_data={"Title": True, "Year": True, "Citations": True, "Venue": True},
                     title="Citation impact by publication year")
    fig.update_layout(height=420, **LAYOUT)
    return fig


def citation_dist():
    fig = px.histogram(pub_df, x="Citations", nbins=30,
                       title="Distribution of citations per paper",
                       color_discrete_sequence=[BLUE])
    fig.update_layout(xaxis=dict(title="Citations"),
                      yaxis=dict(title="# papers", gridcolor="#e2e8f0"),
                      height=360, **LAYOUT)
    return fig


# ── KPI values ────────────────────────────────────────────────────────────────
last_year = max(int(y) for y in cpy)
last_year_new = cpy[str(last_year)]
pct5y = data["total_citations5y"] / data["total_citations"] * 100 if data["total_citations"] else 0

DEMO_BANNER = """
<div style="background:#fef3c7;border:1px solid #f59e0b;border-radius:8px;
            padding:12px 16px;margin-bottom:16px;color:#92400e;font-size:0.9rem;">
  ⚠️  <strong>Demo mode</strong> — Google Scholar was unreachable when this report was generated.
  Data is representative of the actual profile.
</div>
""" if data.get("_demo") else ""

interests_html = "".join(
    f'<span style="background:#eff6ff;color:#1d4ed8;border-radius:20px;'
    f'padding:3px 10px;margin:3px;display:inline-block;font-size:0.8rem;">{i}</span>'
    for i in data.get("interests", [])
)

# ── assemble HTML ─────────────────────────────────────────────────────────────
charts = {
    "timeline":  citation_timeline().to_html(full_html=False, include_plotlyjs="cdn"),
    "yoy":       yoy_growth().to_html(full_html=False, include_plotlyjs=False),
    "top20":     top_papers(20).to_html(full_html=False, include_plotlyjs=False),
    "per_year":  pubs_per_year().to_html(full_html=False, include_plotlyjs=False),
    "bubble":    citation_bubble().to_html(full_html=False, include_plotlyjs=False),
    "dist":      citation_dist().to_html(full_html=False, include_plotlyjs=False),
}

pub_rows = "\n".join(
    f'<tr><td style="max-width:500px">{p["title"]}</td>'
    f'<td style="text-align:center">{p["year"] or "—"}</td>'
    f'<td style="text-align:right;font-weight:600">{p["citations"]:,}</td>'
    f'<td style="color:#64748b;font-size:0.85rem">{p["venue"]}</td></tr>'
    for p in sorted(pubs, key=lambda x: x["citations"], reverse=True)
)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scholar Dashboard · {data['name']}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Inter, system-ui, sans-serif; background: #f8fafc; color: #1e293b; }}
  .page {{ max-width: 1200px; margin: 0 auto; padding: 32px 24px; }}
  header {{ margin-bottom: 24px; }}
  header h1 {{ font-size: 2rem; font-weight: 700; }}
  header p  {{ color: #64748b; margin-top: 4px; }}
  .section-label {{ font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
                    letter-spacing: 0.08em; color: #94a3b8; margin: 28px 0 10px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
  .kpi-grid.three {{ grid-template-columns: repeat(3, 1fr); }}
  .kpi {{ background: white; border-radius: 12px; padding: 20px 24px;
          box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  .kpi .val {{ font-size: 2.2rem; font-weight: 700; color: #1e293b; line-height: 1; }}
  .kpi .lbl {{ font-size: 0.8rem; color: #64748b; margin-top: 6px; }}
  .kpi .delta {{ font-size: 0.82rem; color: #16a34a; margin-top: 4px; }}
  .card {{ background: white; border-radius: 12px; padding: 8px;
           box-shadow: 0 1px 3px rgba(0,0,0,.08); margin-bottom: 20px; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .interests {{ margin: 8px 0 24px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  th {{ text-align: left; padding: 10px 12px; background: #f1f5f9;
        border-bottom: 2px solid #e2e8f0; font-weight: 600; color: #475569; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
  tr:hover td {{ background: #f8fafc; }}
  .table-wrap {{ background: white; border-radius: 12px; overflow: hidden;
                 box-shadow: 0 1px 3px rgba(0,0,0,.08); overflow-x: auto; }}
  footer {{ text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 40px; padding-top: 20px;
            border-top: 1px solid #e2e8f0; }}
  @media (max-width: 700px) {{
    .kpi-grid, .kpi-grid.three, .two-col {{ grid-template-columns: 1fr 1fr; }}
  }}
</style>
</head>
<body>
<div class="page">

  {DEMO_BANNER}

  <header>
    <h1>📚 {data['name']}</h1>
    <p>{data.get('affiliation', '')}</p>
    <div class="interests">{interests_html}</div>
  </header>

  <div class="section-label">All-time metrics</div>
  <div class="kpi-grid">
    <div class="kpi">
      <div class="val">{data['total_citations']:,}</div>
      <div class="lbl">Total citations</div>
      <div class="delta">+{last_year_new:,} in {last_year}</div>
    </div>
    <div class="kpi">
      <div class="val">{data['hindex']}</div>
      <div class="lbl">h-index</div>
    </div>
    <div class="kpi">
      <div class="val">{data['i10index']}</div>
      <div class="lbl">i10-index</div>
    </div>
    <div class="kpi">
      <div class="val">{len(pubs)}</div>
      <div class="lbl">Publications</div>
    </div>
  </div>

  <div class="section-label">Last 5 years</div>
  <div class="kpi-grid three">
    <div class="kpi">
      <div class="val">{data['total_citations5y']:,}</div>
      <div class="lbl">Citations (5y)</div>
    </div>
    <div class="kpi">
      <div class="val">{data['hindex5y']}</div>
      <div class="lbl">h-index (5y)</div>
    </div>
    <div class="kpi">
      <div class="val">{data['i10index5y']}</div>
      <div class="lbl">i10-index (5y)</div>
    </div>
  </div>

  <div class="section-label">Citation history</div>
  <div class="card">{charts['timeline']}</div>
  <div class="card">{charts['yoy']}</div>

  <div class="section-label">Top 20 most cited publications</div>
  <div class="card">{charts['top20']}</div>

  <div class="section-label">Publication activity & impact</div>
  <div class="two-col">
    <div class="card">{charts['per_year']}</div>
    <div class="card">{charts['bubble']}</div>
  </div>

  <div class="section-label">Citation distribution</div>
  <div class="card">{charts['dist']}</div>

  <div class="section-label">All publications</div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Title</th><th>Year</th><th>Citations</th><th>Venue</th></tr></thead>
      <tbody>{pub_rows}</tbody>
    </table>
  </div>

  <footer>
    Generated {data.get('fetched_date', '')} · Alexander Benlian Scholar Dashboard
  </footer>
</div>
</body>
</html>
"""

out = "scholar_dashboard.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = len(HTML.encode()) // 1024
print(f"Written: {out}  ({size_kb} KB)")
print("Open this file in your browser — no server needed.")
