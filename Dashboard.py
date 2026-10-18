import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# LUXURY HOTEL BOOKING INTELLIGENCE DASHBOARD
# Palette: forest green, charcoal, ivory, champagne gold
# ==========================================================

st.set_page_config(
    page_title="The Grand | Booking Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Palette
BG = "#101713"
PANEL = "#19231D"
PANEL_LIGHT = "#202D25"
GREEN = "#7BA58A"
GREEN_BRIGHT = "#A8C7A8"
GOLD = "#D8BB82"
IVORY = "#F4F0E6"
MUTED = "#B2BDB3"
GRID = "#344239"
BLUEGREEN = "#6EAAA1"

# ----------------------- CSS -------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

    .stApp {{
        background: {BG};
        color: {IVORY};
        font-family: 'DM Sans', sans-serif;
    }}
    [data-testid="stHeader"] {{
        background: rgba(16, 23, 19, 0.96);
    }}
    [data-testid="stSidebar"] {{
        background: #151E18;
        border-right: 1px solid {GRID};
    }}
    [data-testid="stSidebar"] * {{
        color: {IVORY};
    }}
    .block-container {{
        max-width: 1500px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }}
    h1, h2, h3 {{
        font-family: 'Playfair Display', Georgia, serif !important;
        color: {IVORY} !important;
        letter-spacing: .2px;
    }}
    p, label, .stMarkdown, [data-testid="stCaptionContainer"] {{
        color: {MUTED};
    }}
    .eyebrow {{
        color: {GOLD};
        text-transform: uppercase;
        letter-spacing: 3px;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 8px;
    }}
    .hero-title {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: clamp(30px, 4vw, 46px);
        line-height: 1.12;
        color: {IVORY};
        margin: 0;
    }}
    .hero-subtitle {{
        color: {MUTED};
        font-size: 15px;
        margin-top: 10px;
        max-width: 780px;
        line-height: 1.7;
    }}
    .section-kicker {{
        color: {GOLD};
        font-size: 11px;
        letter-spacing: 2px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}
    [data-testid="stMetric"] {{
        background: linear-gradient(145deg, {PANEL_LIGHT}, {PANEL});
        border: 1px solid {GRID};
        border-radius: 15px;
        padding: 18px 18px 15px 18px;
        min-height: 112px;
    }}
    [data-testid="stMetricLabel"] {{
        color: {MUTED} !important;
        font-size: 12px !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {IVORY} !important;
        font-weight: 700;
    }}
    [data-testid="stMetricDelta"] {{
        color: {GREEN_BRIGHT} !important;
    }}
    div[data-testid="stAlert"] {{
        background: #1B2B22;
        border: 1px solid #526F59;
        color: {IVORY};
        border-radius: 12px;
    }}
    div[data-testid="stExpander"] {{
        border: 1px solid {GRID};
        border-radius: 12px;
        background: {PANEL};
    }}
    .stButton > button, .stDownloadButton > button {{
        border-radius: 9px;
        border: 1px solid {GOLD};
        color: {IVORY};
        background: #26372B;
    }}
    hr {{
        border-color: {GRID};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------- DATA -------------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("hotel_bookings.csv")

    required = [
        "hotel", "is_canceled", "lead_time", "arrival_date_year",
        "arrival_date_month", "arrival_date_day_of_month",
        "customer_type", "market_segment", "deposit_type",
        "total_of_special_requests",
    ]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    data["is_canceled"] = pd.to_numeric(data["is_canceled"], errors="coerce")
    data = data.dropna(subset=["is_canceled"]).copy()
    data["is_canceled"] = data["is_canceled"].astype(int)
    data["booking_status"] = data["is_canceled"].map(
        {0: "Not Cancelled", 1: "Cancelled"}
    )

    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12,
    }
    month_number = data["arrival_date_month"].map(month_map)
    data["arrival_date"] = pd.to_datetime(
        {
            "year": pd.to_numeric(data["arrival_date_year"], errors="coerce"),
            "month": month_number,
            "day": pd.to_numeric(data["arrival_date_day_of_month"], errors="coerce"),
        },
        errors="coerce",
    )

    data["lead_time_group"] = pd.cut(
        pd.to_numeric(data["lead_time"], errors="coerce"),
        bins=[-1, 7, 30, 90, 180, float("inf")],
        labels=["0–7 days", "8–30 days", "31–90 days", "91–180 days", "181+ days"],
    )
    return data


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Could not find hotel_bookings.csv. Place it in the same folder as "
        "dashboard.py, then run the dashboard again."
    )
    st.stop()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

if df.empty:
    st.error("The dataset has no usable booking records.")
    st.stop()

# ----------------------- CHART HELPERS ----------------------
def chart_layout(fig, height=390):
    fig.update_layout(
        height=height,
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(family="DM Sans, Arial", color=IVORY, size=12),
        title=dict(font=dict(family="Playfair Display, Georgia", size=18, color=IVORY)),
        margin=dict(l=22, r=22, t=68, b=42),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED),
            title_font=dict(color=IVORY),
        ),
        hoverlabel=dict(bgcolor=PANEL_LIGHT, font_color=IVORY),
    )
    fig.update_xaxes(
        gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
        tickfont=dict(color=MUTED), title_font=dict(color=IVORY),
    )
    fig.update_yaxes(
        gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID,
        tickfont=dict(color=MUTED), title_font=dict(color=IVORY),
    )
    return fig


def rate_table(data, group_column):
    result = (
        data.groupby(group_column, observed=False, dropna=False)
        .agg(bookings=("is_canceled", "size"), cancellation_rate=("is_canceled", "mean"))
        .reset_index()
    )
    result["cancellation_rate"] = result["cancellation_rate"] * 100
    result = result.rename(columns={group_column: "category"})
    return result



def bar_chart(data, x, y, title, x_title, y_title, color=GREEN, percent=False):
    fig = px.bar(
        data,
        x=x,
        y=y,
        title=title,
        color_discrete_sequence=[color],
        text_auto=".1f" if percent else True,
    )
    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        textfont=dict(color=IVORY, size=11),
    )
    fig.update_layout(xaxis_title=x_title, yaxis_title=y_title)
    return chart_layout(fig)


# ----------------------- HEADER -----------------------------
st.markdown("<div class='eyebrow'>THE GRAND · HOSPITALITY INTELLIGENCE</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-title'>Booking Performance<br>at a Glance</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='hero-subtitle'>A refined view of reservation trends, cancellation patterns, "
    "and guest behavior — designed to support better occupancy planning and customer retention.</div>",
    unsafe_allow_html=True,
)
st.markdown("")
st.divider()

# ----------------------- FILTERS ----------------------------
st.sidebar.markdown("<div class='eyebrow'>Control Room</div>", unsafe_allow_html=True)
st.sidebar.title("Explore the Data")
st.sidebar.caption("Choose filters to update every KPI, chart, and insight.")

def options_for(column):
    return sorted(df[column].dropna().unique().tolist(), key=str)

hotel_opts = options_for("hotel")
customer_opts = options_for("customer_type")
segment_opts = options_for("market_segment")
deposit_opts = options_for("deposit_type")
years = sorted(df["arrival_date_year"].dropna().unique().tolist())

selected_hotels = st.sidebar.multiselect("Hotel", hotel_opts, default=hotel_opts)
selected_years = st.sidebar.multiselect("Arrival year", years, default=years)
selected_customers = st.sidebar.multiselect("Customer type", customer_opts, default=customer_opts)
selected_segments = st.sidebar.multiselect("Market segment", segment_opts, default=segment_opts)
selected_deposits = st.sidebar.multiselect("Deposit type", deposit_opts, default=deposit_opts)
selected_status = st.sidebar.multiselect(
    "Booking status", ["Not Cancelled", "Cancelled"],
    default=["Not Cancelled", "Cancelled"],
)

max_lead = int(pd.to_numeric(df["lead_time"], errors="coerce").max())
lead_range = st.sidebar.slider(
    "Lead time before arrival (days)",
    min_value=0, max_value=max(max_lead, 1), value=(0, max(max_lead, 1)),
)
st.sidebar.markdown("---")
st.sidebar.caption("All displayed rates are calculated from the filtered records.")

filtered = df[
    df["hotel"].isin(selected_hotels)
    & df["arrival_date_year"].isin(selected_years)
    & df["customer_type"].isin(selected_customers)
    & df["market_segment"].isin(selected_segments)
    & df["deposit_type"].isin(selected_deposits)
    & df["booking_status"].isin(selected_status)
    & pd.to_numeric(df["lead_time"], errors="coerce").between(lead_range[0], lead_range[1])
].copy()

if filtered.empty:
    st.warning("No bookings match these filters. Adjust one or more selections in the sidebar.")
    st.stop()

st.markdown(
    f"<div style='color:{MUTED};font-size:12px;margin:4px 0 18px;'>"
    f"CURRENT VIEW &nbsp;·&nbsp; {len(filtered):,} bookings shown from {len(df):,} total records"
    f"</div>",
    unsafe_allow_html=True,
)

# ----------------------- KPI ROW ----------------------------
total = len(filtered)
cancelled = int(filtered["is_canceled"].sum())
not_cancelled = total - cancelled
cancellation_rate = filtered["is_canceled"].mean() * 100
avg_lead = pd.to_numeric(filtered["lead_time"], errors="coerce").mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Bookings", f"{total:,}")
k2.metric("Cancelled", f"{cancelled:,}")
k3.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")
k4.metric("Not Cancelled", f"{not_cancelled:,}")
k5.metric("Average Lead Time", f"{avg_lead:.0f} days")

st.markdown("")
st.markdown("<div class='section-kicker'>01 / Reservation Overview</div>", unsafe_allow_html=True)
st.subheader("The shape of demand")

left, right = st.columns(2, gap="large")

with left:
    status_counts = (
        filtered["booking_status"].value_counts()
        .reindex(["Not Cancelled", "Cancelled"], fill_value=0)
        .rename_axis("Booking Status").reset_index(name="Bookings")
    )
    fig = px.pie(
        status_counts, names="Booking Status", values="Bookings",
        title="Reservation Status Mix", hole=0.70,
        color="Booking Status",
        color_discrete_map={"Not Cancelled": GREEN, "Cancelled": GOLD},
    )
    fig.update_traces(
        textposition="inside", textinfo="percent+label",
        marker=dict(line=dict(color=PANEL, width=3)),
    )
    fig.add_annotation(
        text=f"<b>{total:,}</b><br><span style='font-size:11px'>bookings</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=21, color=IVORY),
    )
    st.plotly_chart(chart_layout(fig), use_container_width=True)

with right:
    hotel_rates = rate_table(filtered, "hotel").sort_values("cancellation_rate", ascending=False)
    hotel_rates["cancellation_label"] = hotel_rates["cancellation_rate"].map(lambda v: f"{v:.1f}%")
    
fig = px.bar(
    hotel_rates,
    x="category",
    y="cancellation_rate",
    title="Cancellation Rate by Hotel Type",
    color="category",
    text=hotel_rates["cancellation_rate"].map(lambda x: f"{x:.1f}%"),
    hover_data={
        "bookings": True,
        "cancellation_rate": ":.1f",
        "cancellation_label": False,
    },
    color_discrete_sequence=[GREEN, GOLD],
)
fig.update_layout(
    xaxis_title="Hotel Type",
    yaxis_title="Cancellation Rate (%)",
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)

      
   
fig.update_layout(
    xaxis_title="Hotel Type",
    yaxis_title="Cancellation Rate (%)",
    showlegend=False,
)
fig.update_traces(
    textposition="outside",
    cliponaxis=False,
    textfont=dict(color=IVORY),
)
st.plotly_chart(fig, use_container_width=True)


# ----------------------- MONTHLY TRENDS ---------------------
st.markdown("<div class='section-kicker'>02 / Seasonality</div>", unsafe_allow_html=True)
st.subheader("How booking patterns move over time")

monthly = (
    filtered.dropna(subset=["arrival_date"])
    .groupby("arrival_date")
    .agg(bookings=("is_canceled", "size"), cancellation_rate=("is_canceled", "mean"))
    .reset_index()
)
monthly["cancellation_rate"] *= 100

left, right = st.columns(2, gap="large")
with left:
    fig = px.line(
        monthly, x="arrival_date", y="bookings", markers=True,
        title="Bookings by Arrival Month",
        labels={"arrival_date": "Arrival month", "bookings": "Bookings"},
        color_discrete_sequence=[GREEN_BRIGHT],
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    st.plotly_chart(chart_layout(fig), use_container_width=True)

with right:
    fig = px.line(
        monthly, x="arrival_date", y="cancellation_rate", markers=True,
        title="Cancellation Rate by Arrival Month",
        labels={"arrival_date": "Arrival month", "cancellation_rate": "Cancellation rate (%)"},
        color_discrete_sequence=[GOLD],
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_layout(yaxis_ticksuffix="%")
    st.plotly_chart(chart_layout(fig), use_container_width=True)

# ----------------------- CANCELLATION DRIVERS ---------------
st.markdown("<div class='section-kicker'>03 / Cancellation Patterns</div>", unsafe_allow_html=True)
st.subheader("Where cancellation rates differ")

left, right = st.columns(2, gap="large")
with left:
    deposits = rate_table(filtered, "deposit_type").sort_values("cancellation_rate", ascending=True)
    deposits["rate_label"] = deposits["cancellation_rate"].map(lambda v: f"{v:.1f}%")
    fig = px.bar(
        deposits, x="cancellation_rate", y="category", orientation="h",
        text="rate_label", title="Cancellation Rate by Deposit Type",
        labels={"category": "Deposit type", "cancellation_rate": "Cancellation rate (%)"},
        color_discrete_sequence=[GREEN],
        hover_data={"bookings": True, "cancellation_rate": ":.1f", "rate_label": False},
    )
    fig.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=IVORY))
    st.plotly_chart(chart_layout(fig, height=410), use_container_width=True)

with right:
    segments = rate_table(filtered, "market_segment").sort_values("cancellation_rate", ascending=True)
    segments["rate_label"] = segments["cancellation_rate"].map(lambda v: f"{v:.1f}%")
    fig = px.bar(
        segments, x="cancellation_rate", y="category", orientation="h",
        text="rate_label", title="Cancellation Rate by Market Segment",
        labels={"category": "Market segment", "cancellation_rate": "Cancellation rate (%)"},
        color_discrete_sequence=[GOLD],
        hover_data={"bookings": True, "cancellation_rate": ":.1f", "rate_label": False},
    )
    fig.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=IVORY))
    st.plotly_chart(chart_layout(fig, height=410), use_container_width=True)

left, right = st.columns(2, gap="large")
with left:
    lead = rate_table(filtered, "lead_time_group")
    lead["category"] = lead["category"].astype(str)
    lead_order = ["0–7 days", "8–30 days", "31–90 days", "91–180 days", "181+ days"]
    lead["category"] = pd.Categorical(lead["category"], categories=lead_order, ordered=True)
    lead = lead.sort_values("category")
    lead["rate_label"] = lead["cancellation_rate"].map(lambda v: f"{v:.1f}%")
    fig = px.bar(
        lead, x="category", y="cancellation_rate", text="rate_label",
        title="Cancellation Rate by Booking Lead Time",
        labels={"category": "Days between booking and arrival", "cancellation_rate": "Cancellation rate (%)"},
        color_discrete_sequence=[BLUEGREEN],
    )
    fig.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=IVORY))
    st.plotly_chart(chart_layout(fig, height=410), use_container_width=True)

with right:
    requests = rate_table(filtered, "total_of_special_requests").sort_values("category")
    requests["rate_label"] = requests["cancellation_rate"].map(lambda v: f"{v:.1f}%")
    fig = px.bar(
        requests, x="category", y="cancellation_rate", text="rate_label",
        title="Cancellation Rate by Special Requests",
        labels={"category": "Number of special requests", "cancellation_rate": "Cancellation rate (%)"},
        color_discrete_sequence=[GREEN_BRIGHT],
        hover_data={"bookings": True, "cancellation_rate": ":.1f", "rate_label": False},
    )
    fig.update_traces(textposition="outside", cliponaxis=False, textfont=dict(color=IVORY))
    st.plotly_chart(chart_layout(fig, height=410), use_container_width=True)

# ----------------------- BUSINESS INSIGHTS ------------------
st.markdown("<div class='section-kicker'>04 / Management Briefing</div>", unsafe_allow_html=True)
st.subheader("Insights for the next decision")

hotel_rates = rate_table(filtered, "hotel")
deposit_rates = rate_table(filtered, "deposit_type")
segment_rates = rate_table(filtered, "market_segment")
lead_rates = rate_table(filtered, "lead_time_group").dropna(subset=["category"])

insight_left, insight_right = st.columns(2, gap="large")

with insight_left:
    st.markdown("#### What the data shows")
    st.markdown(f"- **Cancellation rate:** {cancellation_rate:.1f}% in the current filtered view.")
    if not hotel_rates.empty:
        row = hotel_rates.loc[hotel_rates["cancellation_rate"].idxmax()]
        st.markdown(
            f"- **Hotel type with the highest observed rate:** {row['category']} "
            f"({row['cancellation_rate']:.1f}%; {int(row['bookings']):,} bookings)."
        )
    if not deposit_rates.empty:
        row = deposit_rates.loc[deposit_rates["cancellation_rate"].idxmax()]
        st.markdown(
            f"- **Deposit category with the highest observed rate:** {row['category']} "
            f"({row['cancellation_rate']:.1f}%; {int(row['bookings']):,} bookings)."
        )
    if not segment_rates.empty:
        row = segment_rates.loc[segment_rates["cancellation_rate"].idxmax()]
        st.markdown(
            f"- **Market segment with the highest observed rate:** {row['category']} "
            f"({row['cancellation_rate']:.1f}%; {int(row['bookings']):,} bookings)."
        )

with insight_right:
    st.markdown("#### Recommended actions")
    st.markdown(
        "- Review booking conditions and guest communication for groups with elevated cancellation rates."
    )
    st.markdown(
        "- Send clear pre-arrival reminders and offer easy ways to reconfirm reservations."
    )
    st.markdown(
        "- Use lead-time and monthly patterns to support staffing and room-inventory planning."
    )
    st.markdown(
        "- Test retention offers on selected segments and compare results before scaling them."
    )

st.info(
    "Interpretation note: these are descriptive associations, not proof of cause and effect. "
    "Compare cancellation percentages with booking counts and business context before changing policy."
)

# ----------------------- DATA EXPLORER ----------------------
with st.expander("Explore filtered bookings and download data"):
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered bookings (CSV)",
        data=csv_bytes,
        file_name="filtered_hotel_bookings.csv",
        mime="text/csv",
    )

st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:{MUTED};font-size:11px;letter-spacing:1px;'>"
    "THE GRAND · HOTEL BOOKING INTELLIGENCE · PYTHON / STREAMLIT / PLOTLY"
    "</div>",
    unsafe_allow_html=True,
)
