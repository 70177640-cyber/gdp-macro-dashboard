import os
import pandas as pd
import numpy as np
import gradio as gr
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. ADVANCED MACROECONOMIC DATASET ENGINE
# ==============================================================================
DATA_FILE = "macroeconomic_intelligence.csv"

if not os.path.exists(DATA_FILE):
    print(f"📌 '{DATA_FILE}' not found. Generating advanced multi-variable dataset...")

    countries_meta = [
        {"name": "United States", "code": "USA", "base_gdp": 5963, "growth": 0.025, "pop_base": 250, "pop_growth": 0.006},
        {"name": "China", "code": "CHN", "base_gdp": 360, "growth": 0.075, "pop_base": 1135, "pop_growth": 0.004},
        {"name": "Japan", "code": "JPN", "base_gdp": 3132, "growth": 0.008, "pop_base": 123, "pop_growth": -0.002},
        {"name": "Germany", "code": "DEU", "base_gdp": 1772, "growth": 0.015, "pop_base": 79, "pop_growth": 0.001},
        {"name": "India", "code": "IND", "base_gdp": 321, "growth": 0.062, "pop_base": 870, "pop_growth": 0.012},
        {"name": "United Kingdom", "code": "GBR", "base_gdp": 1093, "growth": 0.018, "pop_base": 57, "pop_growth": 0.004},
        {"name": "France", "code": "FRA", "base_gdp": 1269, "growth": 0.016, "pop_base": 58, "pop_growth": 0.004},
        {"name": "Brazil", "code": "BRA", "base_gdp": 462, "growth": 0.022, "pop_base": 150, "pop_growth": 0.009},
        {"name": "Canada", "code": "CAN", "base_gdp": 590, "growth": 0.021, "pop_base": 27, "pop_growth": 0.010},
        {"name": "Australia", "code": "AUS", "base_gdp": 310, "growth": 0.026, "pop_base": 17, "pop_growth": 0.012},
        {"name": "South Korea", "code": "KOR", "base_gdp": 280, "growth": 0.045, "pop_base": 43, "pop_growth": 0.003},
        {"name": "South Africa", "code": "ZAF", "base_gdp": 115, "growth": 0.019, "pop_base": 38, "pop_growth": 0.014},
        {"name": "Mexico", "code": "MEX", "base_gdp": 290, "growth": 0.023, "pop_base": 85, "pop_growth": 0.013},
        {"name": "Saudi Arabia", "code": "SAU", "base_gdp": 117, "growth": 0.035, "pop_base": 16, "pop_growth": 0.021},
    ]

    years = list(range(1995, 2026))
    mock_data = []
    np.random.seed(42)

    for c in countries_meta:
        current_gdp = c["base_gdp"]
        current_pop = c["pop_base"]

        for year in years:
            annual_growth = c["growth"] + np.random.uniform(-0.02, 0.02)
            current_gdp *= (1 + annual_growth)
            current_pop *= (1 + c["pop_growth"] + np.random.uniform(-0.002, 0.002))

            gdp_raw = current_gdp * 1e9
            pop_raw = current_pop * 1e6
            gdp_per_capita = gdp_raw / pop_raw
            inflation = max(-1.0, (c["growth"] * 1.5) * 100 + np.random.uniform(-2.5, 5.0))

            mock_data.append({
                "Country Name": c["name"],
                "ISO Code": c["code"],
                "Year": year,
                "GDP (USD)": round(gdp_raw, 2),
                "GDP Growth Rate (%)": round(annual_growth * 100, 2),
                "Population": int(pop_raw),
                "GDP Per Capita (USD)": round(gdp_per_capita, 2),
                "Inflation Rate (%)": round(inflation, 2)
            })

    pd.DataFrame(mock_data).to_csv(DATA_FILE, index=False)
    print(f"✅ Enhanced dataset successfully structured as '{DATA_FILE}'!\n")

df = pd.read_csv(DATA_FILE)
all_countries = sorted(df["Country Name"].unique().tolist())
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
default_selection = [c for c in ["United States", "China", "Germany", "India", "Japan"] if c in all_countries]

def format_currency(val):
    if val >= 1e12: return f"${val / 1e12:,.2f} T"
    if val >= 1e9: return f"${val / 1e9:,.2f} B"
    return f"${val:,.0f}"

# ==============================================================================
# 2. EXECUTIVE CORE VISUALIZATION CALLBACKS
# ==============================================================================

def update_global_overview(selected_year, structural_metric):
    year_df = df[df["Year"] == int(selected_year)].copy()
    if year_df.empty:
        return go.Figure(), go.Figure(), go.Figure(), "<h3>No Data Found</h3>"

    fig_map = px.choropleth(
        year_df, locations="ISO Code", color=structural_metric, hover_name="Country Name",
        title=f"Global Heatmap Distribution: {structural_metric} ({selected_year})",
        color_continuous_scale="Viridis" if "GDP" in structural_metric else "Plasma"
    )
    fig_map.update_layout(geo=dict(showframe=False, showcoastlines=True), margin=dict(l=10, r=10, t=40, b=10))

    sorted_df = year_df.sort_values(by="GDP (USD)", ascending=False)
    top_6 = sorted_df.head(6).copy()
    others_gdp = sorted_df.iloc[6:]["GDP (USD)"].sum()
    if others_gdp > 0:
        others_df = pd.DataFrame([{"Country Name": "Other Nations", "GDP (USD)": others_gdp}])
        pie_df = pd.concat([top_6, others_df], ignore_index=True)
    else:
        pie_df = top_6

    fig_pie = px.pie(pie_df, values="GDP (USD)", names="Country Name", title="Global Economic Volume Dispersal", hole=0.5)
    fig_pie.update_layout(margin=dict(l=10, r=10, t=40, b=10))

    bar_data = year_df.sort_values(by=structural_metric, ascending=False).head(10)
    fig_bar = px.bar(
        bar_data, x=structural_metric, y="Country Name", orientation="h",
        title=f"Top 10 Performing Nations ({structural_metric})",
        color=structural_metric, color_continuous_scale="Cividis"
    )
    fig_bar.update_layout(yaxis={"categoryorder": "total ascending"}, margin=dict(l=10, r=10, t=40, b=10))

    avg_inflation = year_df["Inflation Rate (%)"].mean()
    total_world_gdp = year_df["GDP (USD)"].sum()

    kpi_html = f"""
    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 12px;'>
        <div style='background: #1e293b; padding: 15px; border-radius: 8px; border-left: 5px solid #0d9488; color: white;'>
            <span style='font-size: 11px; opacity: 0.7; text-transform: uppercase;'>Global Sample Output Volume</span>
            <h2 style='margin: 5px 0 0 0; font-size: 22px; color: #2dd4bf;'>{format_currency(total_world_gdp)}</h2>
        </div>
        <div style='background: #1e293b; padding: 15px; border-radius: 8px; border-left: 5px solid #f43f5e; color: white;'>
            <span style='font-size: 11px; opacity: 0.7; text-transform: uppercase;'>Mean Inflation Rate</span>
            <h2 style='margin: 5px 0 0 0; font-size: 22px; color: #fb7185;'>{avg_inflation:.2f}%</h2>
        </div>
    </div>
    """
    return fig_map, fig_pie, fig_bar, kpi_html


def update_trend_analytics(selected_countries, primary_metric, secondary_metric, start_yr, end_yr):
    if not selected_countries:
        blank = px.scatter(title="Select countries to generate evaluation matrices.")
        return blank, blank

    slice_df = df[
        (df["Country Name"].isin(selected_countries)) &
        (df["Year"] >= int(start_yr)) & (df["Year"] <= int(end_yr))
    ].copy()

    if slice_df.empty:
        blank = px.scatter(title="Zero records match selected scope parameters.")
        return blank, blank

    fig_line = px.line(
        slice_df, x="Year", y=primary_metric, color="Country Name", markers=True,
        title=f"Historical Vector Tracking Profile: {primary_metric}"
    )
    fig_line.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))

    latest_slice = slice_df[slice_df["Year"] == int(end_yr)]
    if latest_slice.empty: latest_slice = slice_df

    fig_bubble = px.scatter(
        latest_slice, x="GDP Per Capita (USD)", y="Inflation Rate (%)",
        size="GDP (USD)", color="Country Name", hover_name="Country Name",
        size_max=40, title=f"Risk Matrix Cluster Analysis: Output vs Inflation ({end_yr})"
    )
    fig_bubble.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))

    return fig_line, fig_bubble


def generate_correlation_matrix(target_country):
    country_df = df[df["Country Name"] == target_country].copy()
    if country_df.empty:
        return go.Figure()

    numeric_cols = ["GDP (USD)", "GDP Growth Rate (%)", "Population", "GDP Per Capita (USD)", "Inflation Rate (%)"]
    corr_matrix = country_df[numeric_cols].corr()

    fig_corr = px.imshow(
        corr_matrix.values, text_auto=".2f",
        labels=dict(color="Correlation Coeff."),
        x=numeric_cols, y=numeric_cols,
        color_continuous_scale="RdBu", color_continuous_midpoint=0,
        title=f"Statistical Co-Variance Profile Matrix: {target_country}"
    )
    fig_corr.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig_corr

# ==============================================================================
# 3. ENTERPRISE UI STRUCTURE (Gradio UI Blocks Framework)
# ==============================================================================
executive_theme = gr.themes.Default(
    primary_hue="teal",
    neutral_hue="slate"
).set(
    body_background_fill="#0f172a",
    block_background_fill="#1e293b",
    block_title_text_color="#94a3b8"
)

with gr.Blocks(theme=executive_theme, title="Global Macroeconomic Intelligence Terminal") as demo:

    gr.HTML("""
    <div style="background: linear-gradient(90deg, #1e293b, #0f172a); border-bottom: 2px solid #14b8a6; padding: 24px; border-radius: 8px 8px 0 0; text-align: left; margin-bottom: 15px;">
        <span style="color: #14b8a6; font-weight: 700; letter-spacing: 2px; font-size: 12px; text-transform: uppercase;">Institutional Grade Analytics Terminal</span>
        <h1 style="margin: 4px 0 0 0; color: white; font-size: 28px; font-weight: 300;">Global Macroeconomic Intelligence Suite</h1>
    </div>
    """)

    with gr.Tabs():
        # TAB 1
        with gr.TabItem("🌐 Cross-Sectional Geopolitical Heatmaps"):
            gr.Markdown("### 🔍 Geographic Variations & Macro Dispersal")
            with gr.Row():
                with gr.Column(scale=1):
                    select_year = gr.Slider(minimum=min_year, maximum=max_year, value=max_year, step=1, label="Target Econometric Horizon")
                    target_metric = gr.Dropdown(
                        choices=["GDP (USD)", "GDP Growth Rate (%)", "GDP Per Capita (USD)", "Inflation Rate (%)"],
                        value="GDP (USD)", label="Target Analytical Evaluation Metric"
                    )
                    kpi_display_block = gr.HTML()
                    refresh_geo_btn = gr.Button("Re-index Spatial Matrix", variant="primary")

                with gr.Column(scale=3):
                    geo_map_slot = gr.Plot()
                    with gr.Row():
                        geo_pie_slot = gr.Plot()
                        geo_bar_slot = gr.Plot()

            refresh_geo_btn.click(
                fn=update_global_overview,
                inputs=[select_year, target_metric],
                outputs=[geo_map_slot, geo_pie_slot, geo_bar_slot, kpi_display_block]
            )
            demo.load(
                fn=update_global_overview,
                inputs=[select_year, target_metric],
                outputs=[geo_map_slot, geo_pie_slot, geo_bar_slot, kpi_display_block]
            )

        # TAB 2
        with gr.TabItem("📈 Multi-Variable Growth Trajectories"):
            gr.Markdown("### 📊 Longitudinal Structural Time Series & Multi-Axis Modeling")
            with gr.Row():
                with gr.Column(scale=1):
                    select_countries = gr.Dropdown(choices=all_countries, value=default_selection, multiselect=True, label="Entities of Interest")
                    metric_primary = gr.Dropdown(choices=["GDP (USD)", "GDP Growth Rate (%)", "GDP Per Capita (USD)", "Inflation Rate (%)"], value="GDP Per Capita (USD)", label="Primary Line Vector")
                    metric_secondary = gr.Dropdown(choices=["GDP (USD)", "GDP Growth Rate (%)", "GDP Per Capita (USD)", "Inflation Rate (%)"], value="Inflation Rate (%)", label="Risk Bubble Parameter")

                    with gr.Row():
                        start_time_slider = gr.Slider(minimum=min_year, maximum=max_year, value=min_year, step=1, label="Initial Horizon")
                        end_time_slider = gr.Slider(minimum=min_year, maximum=max_year, value=max_year, step=1, label="Terminal Horizon")

                    compute_trends_btn = gr.Button("Compute Regression Profiles", variant="primary")

                with gr.Column(scale=3):
                    trend_line_slot = gr.Plot()
                    trend_bubble_slot = gr.Plot()

            compute_trends_btn.click(
                fn=update_trend_analytics,
                inputs=[select_countries, metric_primary, metric_secondary, start_time_slider, end_time_slider],
                outputs=[trend_line_slot, trend_bubble_slot]
            )
            demo.load(
                fn=update_trend_analytics,
                inputs=[select_countries, metric_primary, metric_secondary, start_time_slider, end_time_slider],
                outputs=[trend_line_slot, trend_bubble_slot]
            )

        # TAB 3
        with gr.TabItem("📐 Advanced Micro-Correlation Matrix"):
            gr.Markdown("### 🧠 Diagnostic Co-Variance Heatmapping")
            with gr.Row():
                with gr.Column(scale=1):
                    single_country_select = gr.Dropdown(choices=all_countries, value="United States", label="Target Single Sovereign Profile")
                    compute_corr_btn = gr.Button("Isolate Dynamic Co-Variance Matrix", variant="primary")
                    gr.Markdown("""
                    > **Analytical Guide:** A correlation matrix reveals relationships between economic metrics over time. Values near `+1.00` indicate perfect alignment, while values near `-1.00` reveal an inverse structural link.
                    """)
                with gr.Column(scale=3):
                    corr_matrix_slot = gr.Plot()

            compute_corr_btn.click(fn=generate_correlation_matrix, inputs=[single_country_select], outputs=corr_matrix_slot)
            demo.load(fn=generate_correlation_matrix, inputs=[single_country_select], outputs=corr_matrix_slot)

if __name__ == "__main__":
    # Standard launch configuration for optimal local asset rendering
    demo.launch(inline=False, inbrowser=True)
