"""Interactive Streamlit dashboard for the BSCS sales project.

Run from the project root:
    streamlit run dashboard/app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
CLEAN_DATA_PATH = OUTPUTS_DIR / "BSCS_cleaned.csv"
RAW_DATA_PATH = DATA_DIR / "BSCS.csv"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

st.set_page_config(
    page_title="BSCS Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 1.4rem; padding-bottom: 2.5rem;}
        [data-testid="stMetricValue"] {font-size: 1.7rem;}
        [data-testid="stSidebar"] {min-width: 295px; max-width: 295px;}
        .dashboard-subtitle {color: #667085; margin-top: -0.65rem; margin-bottom: 1.1rem;}
        .insight-card {
            border: 1px solid rgba(49, 51, 63, 0.18);
            border-radius: 0.7rem;
            padding: 0.9rem 1rem;
            margin-bottom: 0.7rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    """Format currency using compact Nepalese rupee notation."""
    value = float(value)
    absolute = abs(value)
    if absolute >= 10_000_000:
        return f"NPR {value / 10_000_000:,.2f} Cr"
    if absolute >= 100_000:
        return f"NPR {value / 100_000:,.2f} L"
    if absolute >= 1_000:
        return f"NPR {value / 1_000:,.1f}K"
    return f"NPR {value:,.2f}"


def percent(value: float) -> str:
    return f"{float(value):,.1f}%"


@st.cache_data(show_spinner=False)
def load_sales_data() -> pd.DataFrame:
    """Load the cleaned data, rebuilding it from the raw file when necessary."""
    if CLEAN_DATA_PATH.exists():
        frame = pd.read_csv(CLEAN_DATA_PATH)
    elif RAW_DATA_PATH.exists():
        from bscs_analysis import clean_data

        raw = pd.read_csv(RAW_DATA_PATH)
        frame, _ = clean_data(raw)
    else:
        raise FileNotFoundError(
            "Neither outputs/BSCS_cleaned.csv nor data/BSCS.csv could be found."
        )

    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame = frame.dropna(subset=["Date"]).copy()

    # Ensure dashboard features exist if the cleaned file is replaced manually.
    frame["YearMonth"] = frame.get(
        "YearMonth", frame["Date"].dt.to_period("M").astype(str)
    )
    frame["DayOfWeek"] = frame.get("DayOfWeek", frame["Date"].dt.day_name())
    frame["DayNumber"] = frame.get("DayNumber", frame["Date"].dt.dayofweek)
    frame["IsWeekend"] = frame.get("IsWeekend", frame["Date"].dt.dayofweek >= 5)
    frame["City"] = frame.get(
        "City", frame["Branch"].astype(str).str.split(" - ", n=1).str[0].str.strip()
    )
    return frame


@st.cache_data(show_spinner=False)
def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_baskets(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert line-items into transaction-level baskets."""
    return (
        frame.groupby("TransactionID", as_index=False)
        .agg(
            Date=("Date", "min"),
            Branch=("Branch", "first"),
            City=("City", "first"),
            CustomerID=("CustomerID", "first"),
            CustomerName=("CustomerName", "first"),
            BasketValue=("TotalAmount", "sum"),
            BasketQuantity=("Quantity", "sum"),
            ProductLines=("ProductName", "size"),
        )
    )


def build_sidebar(frame: pd.DataFrame) -> pd.DataFrame:
    """Create sidebar filters and return the filtered frame."""
    st.sidebar.title("Dashboard Filters")
    st.sidebar.caption("All charts and KPIs update automatically.")

    minimum_date = frame["Date"].min().date()
    maximum_date = frame["Date"].max().date()

    def reset_filter_values() -> None:
        st.session_state["date_filter"] = (minimum_date, maximum_date)
        st.session_state["city_filter"] = []
        st.session_state["branch_filter"] = []
        st.session_state["category_filter"] = []
        st.session_state["payment_filter"] = []

    st.sidebar.button(
        "Reset filters",
        on_click=reset_filter_values,
        use_container_width=True,
    )

    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(minimum_date, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
        key="date_filter",
    )

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates

    selected_cities = st.sidebar.multiselect(
        "City",
        options=sorted(frame["City"].dropna().unique()),
        placeholder="All cities",
        key="city_filter",
    )

    branch_options = frame
    if selected_cities:
        branch_options = branch_options[branch_options["City"].isin(selected_cities)]
    selected_branches = st.sidebar.multiselect(
        "Branch",
        options=sorted(branch_options["Branch"].dropna().unique()),
        placeholder="All branches",
        key="branch_filter",
    )

    selected_categories = st.sidebar.multiselect(
        "Product category",
        options=sorted(frame["ProductCategory"].dropna().unique()),
        placeholder="All categories",
        key="category_filter",
    )

    selected_payments = st.sidebar.multiselect(
        "Payment method",
        options=sorted(frame["PaymentMethod"].dropna().unique()),
        placeholder="All payment methods",
        key="payment_filter",
    )

    filtered = frame[
        frame["Date"].dt.date.between(start_date, end_date, inclusive="both")
    ].copy()
    if selected_cities:
        filtered = filtered[filtered["City"].isin(selected_cities)]
    if selected_branches:
        filtered = filtered[filtered["Branch"].isin(selected_branches)]
    if selected_categories:
        filtered = filtered[filtered["ProductCategory"].isin(selected_categories)]
    if selected_payments:
        filtered = filtered[filtered["PaymentMethod"].isin(selected_payments)]

    st.sidebar.divider()
    st.sidebar.metric("Filtered line-items", f"{len(filtered):,}")
    st.sidebar.metric("Filtered transactions", f"{filtered['TransactionID'].nunique():,}")

    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        "Download filtered data",
        data=csv_bytes,
        file_name="BSCS_filtered_sales.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.sidebar.caption("Use Reset filters to return to the full dataset.")

    return filtered


def show_empty_state() -> None:
    st.warning("No records match the current filters. Reset or broaden the selection.")
    st.stop()


def overview_tab(frame: pd.DataFrame, baskets: pd.DataFrame) -> None:
    total_revenue = frame["TotalAmount"].sum()
    avg_basket = baskets["BasketValue"].mean()
    total_quantity = frame["Quantity"].sum()
    customer_count = frame["CustomerID"].nunique()
    transaction_count = frame["TransactionID"].nunique()

    metric_columns = st.columns(5)
    metric_columns[0].metric("Total revenue", money(total_revenue))
    metric_columns[1].metric("Transactions", f"{transaction_count:,}")
    metric_columns[2].metric("Average basket", money(avg_basket))
    metric_columns[3].metric("Quantity sold", f"{total_quantity:,.0f}")
    metric_columns[4].metric("Customers", f"{customer_count:,}")

    monthly = (
        frame.assign(Month=frame["Date"].dt.to_period("M").dt.to_timestamp())
        .groupby("Month", as_index=False)
        .agg(Revenue=("TotalAmount", "sum"), Transactions=("TransactionID", "nunique"))
    )
    monthly["MoMChange"] = monthly["Revenue"].pct_change() * 100

    left, right = st.columns([1.75, 1])
    with left:
        st.subheader("Monthly revenue trend")
        fig = px.line(
            monthly,
            x="Month",
            y="Revenue",
            markers=True,
            hover_data={"Transactions": True, "MoMChange": ":.1f"},
        )
        fig.update_layout(yaxis_title="Revenue (NPR)", xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Revenue by payment method")
        payment = (
            frame.groupby("PaymentMethod", as_index=False)["TotalAmount"]
            .sum()
            .rename(columns={"TotalAmount": "Revenue"})
        )
        fig = px.pie(payment, names="PaymentMethod", values="Revenue", hole=0.52)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Revenue by day of week")
        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        day_summary = (
            frame.groupby("DayOfWeek", as_index=False)["TotalAmount"]
            .sum()
            .rename(columns={"TotalAmount": "Revenue"})
        )
        day_summary["DayOfWeek"] = pd.Categorical(
            day_summary["DayOfWeek"], categories=weekday_order, ordered=True
        )
        day_summary = day_summary.sort_values("DayOfWeek")
        fig = px.bar(day_summary, x="DayOfWeek", y="Revenue", text_auto=".3s")
        fig.update_layout(xaxis_title=None, yaxis_title="Revenue (NPR)")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Weekday vs weekend performance")
        daily = (
            frame.groupby("Date", as_index=False)["TotalAmount"]
            .sum()
            .rename(columns={"TotalAmount": "DailyRevenue"})
        )
        daily["DayType"] = np.where(
            daily["Date"].dt.dayofweek >= 5, "Weekend", "Weekday"
        )
        weekend = (
            daily.groupby("DayType", as_index=False)
            .agg(
                TotalRevenue=("DailyRevenue", "sum"),
                AverageDailyRevenue=("DailyRevenue", "mean"),
                Days=("Date", "nunique"),
            )
        )
        fig = px.bar(
            weekend,
            x="DayType",
            y="AverageDailyRevenue",
            text_auto=".3s",
            hover_data=["TotalRevenue", "Days"],
        )
        fig.update_layout(xaxis_title=None, yaxis_title="Average daily revenue (NPR)")
        st.plotly_chart(fig, use_container_width=True)


def branch_city_tab(frame: pd.DataFrame, baskets: pd.DataFrame) -> None:
    branch_summary = (
        frame.groupby(["City", "Branch"], as_index=False)
        .agg(
            Revenue=("TotalAmount", "sum"),
            Transactions=("TransactionID", "nunique"),
            Quantity=("Quantity", "sum"),
        )
    )
    branch_atv = (
        baskets.groupby("Branch", as_index=False)["BasketValue"]
        .mean()
        .rename(columns={"BasketValue": "AverageBasketValue"})
    )
    branch_summary = branch_summary.merge(branch_atv, on="Branch", how="left")
    branch_summary = branch_summary.sort_values("Revenue", ascending=False)

    city_summary = (
        frame.groupby("City", as_index=False)
        .agg(
            Revenue=("TotalAmount", "sum"),
            Transactions=("TransactionID", "nunique"),
        )
        .sort_values("Revenue", ascending=False)
    )

    first, second = st.columns([1.3, 1])
    with first:
        st.subheader("Branch revenue ranking")
        fig = px.bar(
            branch_summary.sort_values("Revenue"),
            x="Revenue",
            y="Branch",
            orientation="h",
            hover_data=["City", "Transactions", "AverageBasketValue"],
        )
        fig.update_layout(xaxis_title="Revenue (NPR)", yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    with second:
        st.subheader("City contribution")
        fig = px.treemap(city_summary, path=["City"], values="Revenue")
        fig.update_traces(textinfo="label+percent root")
        st.plotly_chart(fig, use_container_width=True)

    first, second = st.columns(2)
    with first:
        st.subheader("Average basket value by branch")
        atv = branch_summary.sort_values("AverageBasketValue", ascending=False)
        fig = px.bar(
            atv,
            x="Branch",
            y="AverageBasketValue",
            text_auto=".3s",
            hover_data=["Revenue", "Transactions"],
        )
        fig.update_layout(
            xaxis_title=None,
            yaxis_title="Average basket value (NPR)",
            xaxis_tickangle=-35,
        )
        st.plotly_chart(fig, use_container_width=True)

    with second:
        st.subheader("Branch revenue vs transaction volume")
        fig = px.scatter(
            branch_summary,
            x="Transactions",
            y="Revenue",
            size="AverageBasketValue",
            color="City",
            hover_name="Branch",
            size_max=38,
        )
        fig.update_layout(
            xaxis_title="Unique transactions", yaxis_title="Revenue (NPR)"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Branch performance table")
    st.dataframe(
        branch_summary.style.format(
            {
                "Revenue": "NPR {:,.2f}",
                "AverageBasketValue": "NPR {:,.2f}",
                "Transactions": "{:,.0f}",
                "Quantity": "{:,.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def product_category_tab(frame: pd.DataFrame) -> None:
    category_summary = (
        frame.groupby("ProductCategory", as_index=False)
        .agg(
            Revenue=("TotalAmount", "sum"),
            Transactions=("TransactionID", "nunique"),
            Quantity=("Quantity", "sum"),
            LineItems=("TransactionID", "size"),
        )
        .sort_values("Revenue", ascending=False)
    )
    category_summary["RevenueShare"] = (
        category_summary["Revenue"] / category_summary["Revenue"].sum() * 100
    )

    product_summary = (
        frame.groupby(["ProductCategory", "ProductName"], as_index=False)
        .agg(
            Revenue=("TotalAmount", "sum"),
            Quantity=("Quantity", "sum"),
            Transactions=("TransactionID", "nunique"),
        )
    )

    first, second = st.columns(2)
    with first:
        st.subheader("Revenue by category")
        fig = px.bar(
            category_summary.sort_values("Revenue"),
            x="Revenue",
            y="ProductCategory",
            orientation="h",
            text="RevenueShare",
            hover_data=["Transactions", "Quantity"],
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(xaxis_title="Revenue (NPR)", yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    with second:
        st.subheader("Category volume vs value")
        fig = px.scatter(
            category_summary,
            x="Transactions",
            y="Revenue",
            size="Quantity",
            hover_name="ProductCategory",
            size_max=42,
        )
        fig.update_layout(xaxis_title="Unique transactions", yaxis_title="Revenue (NPR)")
        st.plotly_chart(fig, use_container_width=True)

    top_n = st.slider("Number of products to display", min_value=5, max_value=20, value=10)
    first, second = st.columns(2)
    with first:
        st.subheader(f"Top {top_n} products by quantity")
        top_quantity = product_summary.nlargest(top_n, "Quantity").sort_values("Quantity")
        fig = px.bar(
            top_quantity,
            x="Quantity",
            y="ProductName",
            orientation="h",
            hover_data=["ProductCategory", "Revenue", "Transactions"],
        )
        fig.update_layout(xaxis_title="Quantity sold", yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    with second:
        st.subheader(f"Top {top_n} products by revenue")
        top_revenue = product_summary.nlargest(top_n, "Revenue").sort_values("Revenue")
        fig = px.bar(
            top_revenue,
            x="Revenue",
            y="ProductName",
            orientation="h",
            hover_data=["ProductCategory", "Quantity", "Transactions"],
        )
        fig.update_layout(xaxis_title="Revenue (NPR)", yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Product performance explorer")
    st.dataframe(
        product_summary.sort_values("Revenue", ascending=False).style.format(
            {"Revenue": "NPR {:,.2f}", "Quantity": "{:,.0f}", "Transactions": "{:,.0f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )


def customer_payment_tab(frame: pd.DataFrame, baskets: pd.DataFrame) -> None:
    customer_summary = (
        frame.groupby(["CustomerID", "CustomerName"], as_index=False)
        .agg(
            TotalSpend=("TotalAmount", "sum"),
            Transactions=("TransactionID", "nunique"),
            Quantity=("Quantity", "sum"),
        )
    )
    customer_atv = (
        baskets.groupby(["CustomerID", "CustomerName"], as_index=False)["BasketValue"]
        .mean()
        .rename(columns={"BasketValue": "AverageBasketValue"})
    )
    customer_summary = customer_summary.merge(
        customer_atv, on=["CustomerID", "CustomerName"], how="left"
    ).sort_values("TotalSpend", ascending=False)

    repeat_customers = int((customer_summary["Transactions"] > 1).sum())
    one_time_customers = int((customer_summary["Transactions"] == 1).sum())
    repeat_rate = repeat_customers / len(customer_summary) * 100 if len(customer_summary) else 0

    first, second, third = st.columns(3)
    first.metric("Repeat customers", f"{repeat_customers:,}")
    second.metric("One-time customers", f"{one_time_customers:,}")
    third.metric("Repeat-customer rate", percent(repeat_rate))

    first, second = st.columns(2)
    with first:
        st.subheader("Top 10 customers by spend")
        top_customers = customer_summary.head(10).sort_values("TotalSpend")
        fig = px.bar(
            top_customers,
            x="TotalSpend",
            y="CustomerName",
            orientation="h",
            hover_data=["CustomerID", "Transactions", "AverageBasketValue"],
        )
        fig.update_layout(xaxis_title="Total spend (NPR)", yaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    with second:
        st.subheader("Average line value by payment method")
        payment = (
            frame.groupby("PaymentMethod", as_index=False)
            .agg(
                AverageLineValue=("TotalAmount", "mean"),
                Revenue=("TotalAmount", "sum"),
                LineItems=("TransactionID", "size"),
            )
            .sort_values("AverageLineValue", ascending=False)
        )
        fig = px.bar(
            payment,
            x="PaymentMethod",
            y="AverageLineValue",
            text_auto=".3s",
            hover_data=["Revenue", "LineItems"],
        )
        fig.update_layout(xaxis_title=None, yaxis_title="Average line value (NPR)")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Payment-method share by branch")
    payment_mix = pd.crosstab(
        frame["Branch"], frame["PaymentMethod"], normalize="index"
    ).mul(100)
    if not payment_mix.empty:
        fig = px.imshow(
            payment_mix,
            labels={"x": "Payment method", "y": "Branch", "color": "Share (%)"},
            aspect="auto",
            text_auto=".1f",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Customer table")
    st.dataframe(
        customer_summary.style.format(
            {
                "TotalSpend": "NPR {:,.2f}",
                "AverageBasketValue": "NPR {:,.2f}",
                "Transactions": "{:,.0f}",
                "Quantity": "{:,.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def quality_model_tab(frame: pd.DataFrame, baskets: pd.DataFrame) -> None:
    cleaning_summary = load_json(OUTPUTS_DIR / "cleaning_summary.json")
    model_metrics = load_json(OUTPUTS_DIR / "model_metrics.json")

    st.subheader("Data-quality summary")
    quality_columns = st.columns(5)
    quality_columns[0].metric(
        "Raw rows", f"{cleaning_summary.get('raw_rows', len(frame)):,}"
    )
    quality_columns[1].metric(
        "Exact duplicates", f"{cleaning_summary.get('exact_duplicate_rows', 0):,}"
    )
    quality_columns[2].metric("Clean rows", f"{len(frame):,}")
    quality_columns[3].metric(
        "Remaining nulls", f"{int(frame.isna().sum().sum()):,}"
    )
    quality_columns[4].metric(
        "Unique transactions", f"{frame['TransactionID'].nunique():,}"
    )

    missing_flag_columns = [
        "CustomerNameWasMissing",
        "ProductCategoryWasMissing",
        "UnitPriceWasMissing",
        "PaymentMethodWasMissing",
    ]
    available_flags = [column for column in missing_flag_columns if column in frame.columns]
    if available_flags:
        flag_summary = pd.DataFrame(
            {
                "Field": [column.replace("WasMissing", "") for column in available_flags],
                "OriginallyMissing": [int(frame[column].astype(bool).sum()) for column in available_flags],
            }
        )
        flag_summary["PercentOfFilteredRows"] = (
            flag_summary["OriginallyMissing"] / len(frame) * 100
        )
        first, second = st.columns([1, 1.5])
        with first:
            st.dataframe(
                flag_summary.style.format({"PercentOfFilteredRows": "{:.2f}%"}),
                use_container_width=True,
                hide_index=True,
            )
        with second:
            fig = px.bar(
                flag_summary,
                x="Field",
                y="OriginallyMissing",
                text_auto=True,
            )
            fig.update_layout(xaxis_title=None, yaxis_title="Rows originally missing")
            st.plotly_chart(fig, use_container_width=True)

    first, second = st.columns(2)
    with first:
        st.subheader("Correlation matrix")
        correlation = frame[["Quantity", "UnitPrice", "TotalAmount"]].corr()
        fig = px.imshow(
            correlation,
            text_auto=".3f",
            zmin=-1,
            zmax=1,
            labels={"color": "Correlation"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with second:
        st.subheader("Transaction basket outliers")
        fig = px.box(baskets, y="BasketValue", points="outliers")
        fig.update_layout(xaxis_title=None, yaxis_title="Basket value (NPR)")
        st.plotly_chart(fig, use_container_width=True)

    q1 = baskets["BasketValue"].quantile(0.25)
    q3 = baskets["BasketValue"].quantile(0.75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    outliers = baskets[baskets["BasketValue"] > upper].sort_values(
        "BasketValue", ascending=False
    )
    st.caption(
        f"IQR upper threshold: {money(upper)} · High-value outlier baskets: {len(outliers):,}"
    )

    st.subheader("Educational predictive model")
    if model_metrics:
        metric_columns = st.columns(4)
        metric_columns[0].metric("Model", model_metrics.get("model", "N/A"))
        metric_columns[1].metric("R²", f"{model_metrics.get('r2', 0):.6f}")
        metric_columns[2].metric("MAE", money(model_metrics.get("mae", 0)))
        metric_columns[3].metric("RMSE", money(model_metrics.get("rmse", 0)))
        st.info(
            "The model score is extremely high because TotalAmount is mathematically defined "
            "as Quantity × UnitPrice. It demonstrates a modelling workflow rather than genuine forecasting."
        )

        importance_path = OUTPUTS_DIR / "model_feature_importance.csv"
        if importance_path.exists():
            importance = pd.read_csv(importance_path)
            fig = px.bar(
                importance.sort_values("RelativeImportancePercent"),
                x="RelativeImportancePercent",
                y="Feature",
                orientation="h",
                text_auto=".2f",
            )
            fig.update_layout(xaxis_title="Relative importance (%)", yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(
            "Model metrics are not available. Run `python src/bscs_analysis.py` first."
        )


def explorer_tab(frame: pd.DataFrame) -> None:
    st.subheader("Filtered data explorer")
    st.caption("Search, sort, inspect, and download the filtered records.")

    default_columns = [
        "TransactionID",
        "Date",
        "Branch",
        "CustomerName",
        "ProductCategory",
        "ProductName",
        "Quantity",
        "UnitPrice",
        "TotalAmount",
        "PaymentMethod",
    ]
    available_default = [column for column in default_columns if column in frame.columns]
    selected_columns = st.multiselect(
        "Columns to display",
        options=list(frame.columns),
        default=available_default,
    )
    display_frame = frame[selected_columns] if selected_columns else frame
    st.dataframe(display_frame, use_container_width=True, hide_index=True, height=520)

    st.download_button(
        "Download displayed table",
        data=display_frame.to_csv(index=False).encode("utf-8"),
        file_name="BSCS_dashboard_table.csv",
        mime="text/csv",
    )


def show_management_insights(frame: pd.DataFrame, baskets: pd.DataFrame) -> None:
    """Display concise, filter-aware management insights."""
    top_branch = frame.groupby("Branch")["TotalAmount"].sum().idxmax()
    top_category = frame.groupby("ProductCategory")["TotalAmount"].sum().idxmax()
    top_product = frame.groupby("ProductName")["TotalAmount"].sum().idxmax()
    peak_month = (
        frame.assign(Month=frame["Date"].dt.to_period("M").astype(str))
        .groupby("Month")["TotalAmount"]
        .sum()
        .idxmax()
    )
    avg_basket = baskets["BasketValue"].mean()

    with st.expander("Management insights from the current filters", expanded=False):
        st.markdown(
            f"""
            <div class="insight-card"><strong>{top_branch}</strong> is the highest-revenue branch in the selected view.</div>
            <div class="insight-card"><strong>{top_category}</strong> is the leading category, while <strong>{top_product}</strong> is the leading product by revenue.</div>
            <div class="insight-card">The strongest month is <strong>{peak_month}</strong>, and the average transaction basket is <strong>{money(avg_basket)}</strong>.</div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    try:
        full_data = load_sales_data()
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        st.stop()

    st.title("🛒 BSCS Sales Analytics Dashboard")
    st.markdown(
        '<p class="dashboard-subtitle">Bhatbhateni 2025 sales performance, customer behaviour, product mix, payment trends, and data quality.</p>',
        unsafe_allow_html=True,
    )

    filtered_data = build_sidebar(full_data)
    if filtered_data.empty:
        show_empty_state()

    baskets = create_baskets(filtered_data)
    show_management_insights(filtered_data, baskets)

    tabs = st.tabs(
        [
            "Overview",
            "Branches & Cities",
            "Products & Categories",
            "Customers & Payments",
            "Data Quality & Model",
            "Data Explorer",
        ]
    )

    with tabs[0]:
        overview_tab(filtered_data, baskets)
    with tabs[1]:
        branch_city_tab(filtered_data, baskets)
    with tabs[2]:
        product_category_tab(filtered_data)
    with tabs[3]:
        customer_payment_tab(filtered_data, baskets)
    with tabs[4]:
        quality_model_tab(filtered_data, baskets)
    with tabs[5]:
        explorer_tab(filtered_data)

    st.divider()
    st.caption(
        "BSCS dashboard · Built with Streamlit, pandas, and Plotly · "
        "Repeated TransactionID values are treated as valid multi-item baskets."
    )


if __name__ == "__main__":
    main()
