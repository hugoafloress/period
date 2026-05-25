import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
)
 
# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .metric-card {
        background: #f8f9fb;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border-left: 4px solid #4f46e5;
    }
    h1 { color: #1e1b4b; }
    .stTabs [data-baseweb="tab"] { font-size: 0.9rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)
 
# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("sellers.csv", encoding="latin1")
    df.columns = df.columns.str.strip()
    df["FULL NAME"] = df["NAME"].str.strip() + " " + df["LASTNAME"].str.strip()
    return df
 
df = load_data()
 
# ── Header ────────────────────────────────────────────────────────────────────
st.title("📊 Sales Performance Dashboard")
st.caption("Interactive overview of seller performance by region and individual.")
 
st.divider()
 
# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["🗂️ Data Table", "📈 Charts", "🔍 Vendor Detail"])
 
# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — Data Table with region filter
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col_filter, col_reset = st.columns([3, 1])
 
    regions = sorted(df["REGION"].unique())
    with col_filter:
        selected_regions = st.multiselect(
            "Filter by Region",
            options=regions,
            default=regions,
            help="Select one or more regions to narrow the table.",
        )
    with col_reset:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Reset filters", use_container_width=True):
            selected_regions = regions
 
    filtered = df[df["REGION"].isin(selected_regions)] if selected_regions else df
 
    # Summary KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Sellers shown", len(filtered))
    k2.metric("Total Units Sold", f"{filtered['SOLD UNITS'].sum():,}")
    k3.metric("Total Sales", f"${filtered['TOTAL SALES'].sum():,}")
    k4.metric("Avg. Sales Rate", f"{filtered['SALES AVERAGE'].mean():.4f}")
 
    st.dataframe(
        filtered[["REGION", "ID", "FULL NAME", "INCOME", "SOLD UNITS", "TOTAL SALES", "SALES AVERAGE"]]
        .rename(columns={
            "REGION": "Region",
            "ID": "ID",
            "FULL NAME": "Name",
            "INCOME": "Income",
            "SOLD UNITS": "Units Sold",
            "TOTAL SALES": "Total Sales",
            "SALES AVERAGE": "Avg. Sales",
        })
        .sort_values(["Region", "Total Sales"], ascending=[True, False])
        .reset_index(drop=True),
        use_container_width=True,
        height=460,
    )
 
# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Charts
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    # Region selector for charts
    chart_regions = st.multiselect(
        "Regions to include in charts",
        options=regions,
        default=regions,
        key="chart_regions",
    )
    chart_df = df[df["REGION"].isin(chart_regions)] if chart_regions else df
 
    # ── Row 1: Units Sold & Total Sales side by side ──
    c1, c2 = st.columns(2)
 
    with c1:
        st.subheader("Units Sold per Seller")
        sort_opt = st.selectbox("Sort by", ["Units Sold ↓", "Name A-Z"], key="sort_units")
        plot_df = chart_df.copy()
        if sort_opt == "Units Sold ↓":
            plot_df = plot_df.sort_values("SOLD UNITS", ascending=False)
        else:
            plot_df = plot_df.sort_values("FULL NAME")
 
        fig_units = px.bar(
            plot_df,
            x="FULL NAME",
            y="SOLD UNITS",
            color="REGION",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            labels={"FULL NAME": "Seller", "SOLD UNITS": "Units Sold", "REGION": "Region"},
            height=380,
        )
        fig_units.update_layout(
            xaxis_tickangle=-45,
            legend_title_text="Region",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_units.update_xaxes(showgrid=False)
        fig_units.update_yaxes(gridcolor="#e5e7eb")
        st.plotly_chart(fig_units, use_container_width=True)
 
    with c2:
        st.subheader("Total Sales per Seller")
        fig_sales = px.bar(
            plot_df,
            x="FULL NAME",
            y="TOTAL SALES",
            color="REGION",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            labels={"FULL NAME": "Seller", "TOTAL SALES": "Total Sales ($)", "REGION": "Region"},
            height=380,
        )
        fig_sales.update_layout(
            xaxis_tickangle=-45,
            legend_title_text="Region",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_sales.update_xaxes(showgrid=False)
        fig_sales.update_yaxes(gridcolor="#e5e7eb")
        st.plotly_chart(fig_sales, use_container_width=True)
 
    st.divider()
 
    # ── Row 2: Average Sales Rate & Region Aggregates ──
    c3, c4 = st.columns(2)
 
    with c3:
        st.subheader("Average Sales Rate per Seller")
        avg_sorted = chart_df.sort_values("SALES AVERAGE", ascending=True)
        fig_avg = px.bar(
            avg_sorted,
            x="SALES AVERAGE",
            y="FULL NAME",
            color="REGION",
            orientation="h",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            labels={"FULL NAME": "", "SALES AVERAGE": "Avg. Sales Rate", "REGION": "Region"},
            height=420,
        )
        fig_avg.update_layout(
            legend_title_text="Region",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(tickfont=dict(size=10)),
        )
        fig_avg.update_xaxes(gridcolor="#e5e7eb")
        fig_avg.update_yaxes(showgrid=False)
        st.plotly_chart(fig_avg, use_container_width=True)
 
    with c4:
        st.subheader("Region Comparison")
        region_agg = (
            chart_df.groupby("REGION")
            .agg(
                Sellers=("ID", "count"),
                Units_Sold=("SOLD UNITS", "sum"),
                Total_Sales=("TOTAL SALES", "sum"),
                Avg_Sales=("SALES AVERAGE", "mean"),
            )
            .reset_index()
        )
 
        metric_choice = st.selectbox(
            "Metric",
            ["Units_Sold", "Total_Sales", "Avg_Sales", "Sellers"],
            format_func=lambda x: {
                "Units_Sold": "Units Sold",
                "Total_Sales": "Total Sales",
                "Avg_Sales": "Avg. Sales Rate",
                "Sellers": "# Sellers",
            }[x],
            key="region_metric",
        )
 
        fig_region = px.pie(
            region_agg,
            names="REGION",
            values=metric_choice,
            color_discrete_sequence=px.colors.qualitative.Vivid,
            hole=0.45,
            height=380,
        )
        fig_region.update_traces(textposition="outside", textinfo="percent+label")
        fig_region.update_layout(
            showlegend=True,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_region, use_container_width=True)
 
    st.divider()
 
    # ── Row 3: Scatter — Units Sold vs Total Sales ──
    st.subheader("Units Sold vs. Total Sales (bubble = Avg. Sales Rate)")
    fig_scatter = px.scatter(
        chart_df,
        x="SOLD UNITS",
        y="TOTAL SALES",
        color="REGION",
        size="SALES AVERAGE",
        hover_name="FULL NAME",
        color_discrete_sequence=px.colors.qualitative.Vivid,
        labels={
            "SOLD UNITS": "Units Sold",
            "TOTAL SALES": "Total Sales ($)",
            "REGION": "Region",
            "SALES AVERAGE": "Avg. Sales Rate",
        },
        height=420,
    )
    fig_scatter.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig_scatter.update_xaxes(gridcolor="#e5e7eb")
    fig_scatter.update_yaxes(gridcolor="#e5e7eb")
    st.plotly_chart(fig_scatter, use_container_width=True)
 
# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Vendor Detail
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("🔍 Vendor Detail")
 
    v_col1, v_col2 = st.columns([2, 1])
    with v_col1:
        vendor_region = st.selectbox("Filter vendors by Region", ["All"] + regions, key="v_region")
    pool = df if vendor_region == "All" else df[df["REGION"] == vendor_region]
 
    with v_col2:
        vendor_search = st.text_input("Search by name", placeholder="e.g. Ana", key="v_search")
 
    if vendor_search:
        pool = pool[pool["FULL NAME"].str.contains(vendor_search, case=False, na=False)]
 
    vendor_names = pool["FULL NAME"].sort_values().tolist()
 
    if not vendor_names:
        st.warning("No vendors match the current filters.")
    else:
        selected_vendor = st.selectbox("Select a vendor", vendor_names, key="v_select")
        row = pool[pool["FULL NAME"] == selected_vendor].iloc[0]
 
        st.divider()
 
        # Identity card
        with st.container(border=True):
            id_col, reg_col = st.columns(2)
            id_col.markdown(f"### {row['FULL NAME']}")
            id_col.caption(f"ID: **{row['ID']}**")
            reg_col.markdown(f"**Region:** {row['REGION']}")
            reg_col.markdown(f"**Income:** ${row['INCOME']:,}")
 
        # KPI metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Units Sold", f"{row['SOLD UNITS']:,}")
        m2.metric("Total Sales", f"${row['TOTAL SALES']:,}")
        m3.metric("Avg. Sales Rate", f"{row['SALES AVERAGE']:.4f}")
 
        st.divider()
 
        # Ranking within region
        region_df = df[df["REGION"] == row["REGION"]].sort_values("TOTAL SALES", ascending=False).reset_index(drop=True)
        rank = region_df[region_df["FULL NAME"] == selected_vendor].index[0] + 1
        total_in_region = len(region_df)
 
        st.markdown(f"**Rank in {row['REGION']} region:** #{rank} of {total_in_region} sellers")
 
        # Gauge — percentile within full company
        pct = (df["TOTAL SALES"] < row["TOTAL SALES"]).mean() * 100
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pct,
            title={"text": "Total Sales Percentile (Company-wide)"},
            delta={"reference": 50},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#4f46e5"},
                "steps": [
                    {"range": [0, 25], "color": "#fee2e2"},
                    {"range": [25, 75], "color": "#e0e7ff"},
                    {"range": [75, 100], "color": "#d1fae5"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 3},
                    "thickness": 0.75,
                    "value": pct,
                },
            },
            number={"suffix": " %ile"},
        ))
        fig_gauge.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_gauge, use_container_width=True)
 
        # Comparison: vendor vs region vs company averages
        st.subheader("Comparison vs. Region & Company Averages")
        metrics = ["SOLD UNITS", "TOTAL SALES", "SALES AVERAGE"]
        labels = ["Units Sold", "Total Sales", "Avg. Sales Rate"]
        vendor_vals = [row[m] for m in metrics]
        region_vals = [df[df["REGION"] == row["REGION"]][m].mean() for m in metrics]
        company_vals = [df[m].mean() for m in metrics]
 
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(name=selected_vendor, x=labels, y=vendor_vals, marker_color="#4f46e5"))
        fig_compare.add_trace(go.Bar(name=f"{row['REGION']} avg", x=labels, y=region_vals, marker_color="#818cf8"))
        fig_compare.add_trace(go.Bar(name="Company avg", x=labels, y=company_vals, marker_color="#c7d2fe"))
        fig_compare.update_layout(
            barmode="group",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
            height=340,
        )
        fig_compare.update_yaxes(gridcolor="#e5e7eb")
        fig_compare.update_xaxes(showgrid=False)
        st.plotly_chart(fig_compare, use_container_width=True)
 
# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Dashboard built with Streamlit & Plotly · sellers.csv")