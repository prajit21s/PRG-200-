"""BSCS — Bhatbhateni Sales Cleaning & Solutions

A complete VS Code-ready data cleaning, exploratory analysis, visualization,
and predictive modelling project.

Run from the project root:
    python src/bscs_analysis.py
"""

from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

warnings.filterwarnings("ignore", category=FutureWarning)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "BSCS.csv"
IMAGES_DIR = PROJECT_ROOT / "images"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def money(value: float) -> str:
    """Format a numeric value as Nepalese rupees."""
    return f"NPR {value:,.2f}"


def save_current_figure(filename: str) -> None:
    """Save the active Matplotlib figure and close it."""
    plt.tight_layout()
    plt.savefig(IMAGES_DIR / filename, dpi=200, bbox_inches="tight")
    plt.close()


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the raw CSV file."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Place BSCS.csv inside the data folder."
        )
    return pd.read_csv(path)


def data_quality_table(df: pd.DataFrame, stage: str) -> pd.DataFrame:
    """Create a column-level missing-value summary."""
    missing_count = df.isna().sum()
    return pd.DataFrame(
        {
            "Stage": stage,
            "Column": missing_count.index,
            "MissingCount": missing_count.values,
            "MissingPercent": (missing_count.values / len(df) * 100).round(2),
        }
    )


def clean_data(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean duplicates, nulls, data types, and validate calculated totals."""
    df = raw_df.copy()
    raw_rows = len(df)
    exact_duplicates = int(df.duplicated().sum())

    # Q6: Remove only fully identical rows. Repeated TransactionID values are valid
    # because one basket can contain several line-items.
    df = df.drop_duplicates(keep="first").copy()
    rows_after_duplicates = len(df)

    # Preserve missingness flags before imputation for auditing.
    df["CustomerNameWasMissing"] = df["CustomerName"].isna()
    df["ProductCategoryWasMissing"] = df["ProductCategory"].isna()
    df["UnitPriceWasMissing"] = df["UnitPrice"].isna()
    df["PaymentMethodWasMissing"] = df["PaymentMethod"].isna()

    # Q7a: CustomerID maps consistently to one CustomerName in the observed data.
    customer_map = (
        df.dropna(subset=["CustomerName"])
        .groupby("CustomerID")["CustomerName"]
        .agg(lambda values: values.mode().iloc[0])
    )
    df["CustomerName"] = df["CustomerName"].fillna(df["CustomerID"].map(customer_map))
    df["CustomerName"] = df["CustomerName"].fillna("Unknown Customer")

    # Q7b: Every ProductName has one consistent observed ProductCategory.
    product_category_map = (
        df.dropna(subset=["ProductCategory"])
        .groupby("ProductName")["ProductCategory"]
        .agg(lambda values: values.mode().iloc[0])
    )
    df["ProductCategory"] = df["ProductCategory"].fillna(
        df["ProductName"].map(product_category_map)
    )
    df["ProductCategory"] = df["ProductCategory"].fillna("Unknown Category")

    # Q7c: TotalAmount and Quantity allow an exact recovery of missing UnitPrice.
    recoverable_price = np.where(
        (df["UnitPrice"].isna()) & (df["Quantity"] > 0),
        df["TotalAmount"] / df["Quantity"],
        np.nan,
    )
    df["UnitPrice"] = df["UnitPrice"].fillna(pd.Series(recoverable_price, index=df.index))

    # Fallbacks are included for robustness even though all missing prices in this
    # dataset are recoverable from TotalAmount / Quantity.
    product_price_median = df.groupby("ProductName")["UnitPrice"].transform("median")
    category_price_median = df.groupby("ProductCategory")["UnitPrice"].transform("median")
    df["UnitPrice"] = df["UnitPrice"].fillna(product_price_median)
    df["UnitPrice"] = df["UnitPrice"].fillna(category_price_median)
    df["UnitPrice"] = df["UnitPrice"].fillna(df["UnitPrice"].median())

    # Q7d: Keep the sales record and explicitly flag missing payment information.
    df["PaymentMethod"] = df["PaymentMethod"].fillna("Unknown")

    # Q8a: Convert date and create useful time features.
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if df["Date"].isna().any():
        raise ValueError("Some Date values could not be converted to datetime.")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["MonthName"] = df["Date"].dt.month_name()
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
    df["DayOfWeek"] = df["Date"].dt.day_name()
    df["DayNumber"] = df["Date"].dt.dayofweek
    df["IsWeekend"] = df["DayNumber"] >= 5

    # Q8b: Branch values follow "City - Location".
    df["City"] = df["Branch"].str.split(" - ", n=1).str[0].str.strip()

    # Q5d/Q8c: Validate TotalAmount against Quantity * UnitPrice.
    df["CalculatedTotal"] = (df["Quantity"] * df["UnitPrice"]).round(2)
    df["TotalDifference"] = (df["TotalAmount"] - df["CalculatedTotal"]).round(2)
    mismatches_before_correction = int((df["TotalDifference"].abs() > 0.01).sum())
    if mismatches_before_correction:
        df.loc[df["TotalDifference"].abs() > 0.01, "TotalAmount"] = df.loc[
            df["TotalDifference"].abs() > 0.01, "CalculatedTotal"
        ]
        df["TotalDifference"] = (df["TotalAmount"] - df["CalculatedTotal"]).round(2)

    remaining_missing = int(df.isna().sum().sum())

    cleaning_summary = {
        "raw_rows": raw_rows,
        "raw_columns": raw_df.shape[1],
        "exact_duplicate_rows": exact_duplicates,
        "rows_after_duplicate_removal": rows_after_duplicates,
        "rows_removed": raw_rows - rows_after_duplicates,
        "unique_transaction_ids": int(df["TransactionID"].nunique()),
        "multi_line_transaction_ids": int((df.groupby("TransactionID").size() > 1).sum()),
        "maximum_lines_in_one_transaction": int(df.groupby("TransactionID").size().max()),
        "total_mismatches_before_correction": mismatches_before_correction,
        "remaining_missing_values": remaining_missing,
    }
    return df, cleaning_summary


def build_analysis_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Produce all tables required by Q9–Q15."""
    category_summary = (
        df.groupby("ProductCategory")
        .agg(
            LineItems=("TransactionID", "size"),
            UniqueTransactions=("TransactionID", "nunique"),
            QuantitySold=("Quantity", "sum"),
            Revenue=("TotalAmount", "sum"),
        )
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )
    category_summary["LineItemSharePercent"] = (
        category_summary["LineItems"] / len(df) * 100
    ).round(2)
    category_summary["RevenueSharePercent"] = (
        category_summary["Revenue"] / df["TotalAmount"].sum() * 100
    ).round(2)

    branch_summary = (
        df.groupby("Branch")
        .agg(
            LineItems=("TransactionID", "size"),
            UniqueTransactions=("TransactionID", "nunique"),
            Revenue=("TotalAmount", "sum"),
        )
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )

    # Basket-level transaction values for a correct average transaction value.
    basket_values = (
        df.groupby(["TransactionID", "Branch", "City", "Date"], as_index=False)
        .agg(BasketValue=("TotalAmount", "sum"), BasketItems=("Quantity", "sum"))
    )
    branch_atv = (
        basket_values.groupby("Branch")
        .agg(
            Transactions=("TransactionID", "nunique"),
            AverageTransactionValue=("BasketValue", "mean"),
            MedianTransactionValue=("BasketValue", "median"),
        )
        .sort_values("AverageTransactionValue", ascending=False)
        .reset_index()
    )
    branch_summary = branch_summary.merge(branch_atv, on="Branch", how="left")

    city_summary = (
        df.groupby("City")
        .agg(
            LineItems=("TransactionID", "size"),
            UniqueTransactions=("TransactionID", "nunique"),
            Revenue=("TotalAmount", "sum"),
        )
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )

    payment_summary = (
        df.groupby("PaymentMethod")
        .agg(
            LineItems=("TransactionID", "size"),
            Revenue=("TotalAmount", "sum"),
            AverageLineValue=("TotalAmount", "mean"),
            MedianLineValue=("TotalAmount", "median"),
        )
        .sort_values("LineItems", ascending=False)
        .reset_index()
    )
    payment_summary["UsageSharePercent"] = (
        payment_summary["LineItems"] / len(df) * 100
    ).round(2)

    payment_branch_counts = pd.crosstab(df["Branch"], df["PaymentMethod"])
    payment_branch_share = (
        pd.crosstab(df["Branch"], df["PaymentMethod"], normalize="index") * 100
    ).round(2)

    monthly_revenue = (
        df.groupby("YearMonth", as_index=False)["TotalAmount"]
        .sum()
        .rename(columns={"TotalAmount": "Revenue"})
        .sort_values("YearMonth")
    )
    monthly_revenue["MoMChangePercent"] = monthly_revenue["Revenue"].pct_change().mul(100).round(2)

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_revenue = (
        df.groupby("DayOfWeek")["TotalAmount"]
        .sum()
        .reindex(weekday_order)
        .reset_index(name="Revenue")
    )
    daily_totals = df.groupby("Date", as_index=False).agg(Revenue=("TotalAmount", "sum"))
    daily_totals["DayType"] = np.where(daily_totals["Date"].dt.dayofweek >= 5, "Weekend", "Weekday")
    weekend_weekday = (
        daily_totals.groupby("DayType")
        .agg(
            NumberOfDays=("Date", "nunique"),
            TotalRevenue=("Revenue", "sum"),
            AverageDailyRevenue=("Revenue", "mean"),
            MedianDailyRevenue=("Revenue", "median"),
        )
        .reset_index()
    )

    product_quantity = (
        df.groupby("ProductName", as_index=False)
        .agg(QuantitySold=("Quantity", "sum"), Revenue=("TotalAmount", "sum"))
        .sort_values("QuantitySold", ascending=False)
    )
    product_revenue = product_quantity.sort_values("Revenue", ascending=False)

    customer_summary = (
        df.groupby(["CustomerID", "CustomerName"], as_index=False)
        .agg(
            Transactions=("TransactionID", "nunique"),
            LineItems=("TransactionID", "size"),
            TotalSpend=("TotalAmount", "sum"),
            AverageBasketValue=("TotalAmount", lambda x: np.nan),
        )
    )
    customer_baskets = (
        df.groupby(["CustomerID", "CustomerName", "TransactionID"], as_index=False)
        .agg(BasketValue=("TotalAmount", "sum"))
    )
    customer_atv = (
        customer_baskets.groupby(["CustomerID", "CustomerName"], as_index=False)
        .agg(AverageBasketValue=("BasketValue", "mean"))
    )
    customer_summary = customer_summary.drop(columns=["AverageBasketValue"]).merge(
        customer_atv, on=["CustomerID", "CustomerName"], how="left"
    )
    customer_summary = customer_summary.sort_values("TotalSpend", ascending=False)

    correlation = df[["Quantity", "UnitPrice", "TotalAmount"]].corr()

    # IQR outliers at line-item level.
    line_q1 = df["TotalAmount"].quantile(0.25)
    line_q3 = df["TotalAmount"].quantile(0.75)
    line_iqr = line_q3 - line_q1
    line_lower = line_q1 - 1.5 * line_iqr
    line_upper = line_q3 + 1.5 * line_iqr
    line_outliers = df[(df["TotalAmount"] < line_lower) | (df["TotalAmount"] > line_upper)].copy()

    # Basket-level outliers to support the wording "outlier transactions".
    basket_q1 = basket_values["BasketValue"].quantile(0.25)
    basket_q3 = basket_values["BasketValue"].quantile(0.75)
    basket_iqr = basket_q3 - basket_q1
    basket_lower = basket_q1 - 1.5 * basket_iqr
    basket_upper = basket_q3 + 1.5 * basket_iqr
    basket_outliers = basket_values[
        (basket_values["BasketValue"] < basket_lower)
        | (basket_values["BasketValue"] > basket_upper)
    ].copy()

    return {
        "category_summary": category_summary,
        "branch_summary": branch_summary,
        "city_summary": city_summary,
        "payment_summary": payment_summary,
        "payment_branch_counts": payment_branch_counts,
        "payment_branch_share": payment_branch_share,
        "monthly_revenue": monthly_revenue,
        "day_revenue": day_revenue,
        "weekend_weekday": weekend_weekday,
        "product_quantity": product_quantity,
        "product_revenue": product_revenue,
        "customer_summary": customer_summary,
        "correlation": correlation,
        "line_outliers": line_outliers,
        "basket_values": basket_values,
        "basket_outliers": basket_outliers,
        "outlier_thresholds": pd.DataFrame(
            [
                {
                    "Level": "Line item",
                    "Q1": line_q1,
                    "Q3": line_q3,
                    "IQR": line_iqr,
                    "LowerBound": line_lower,
                    "UpperBound": line_upper,
                    "OutlierCount": len(line_outliers),
                },
                {
                    "Level": "Transaction basket",
                    "Q1": basket_q1,
                    "Q3": basket_q3,
                    "IQR": basket_iqr,
                    "LowerBound": basket_lower,
                    "UpperBound": basket_upper,
                    "OutlierCount": len(basket_outliers),
                },
            ]
        ),
    }


def create_visualizations(df: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> None:
    """Create portfolio-ready charts using Matplotlib defaults."""
    monthly = tables["monthly_revenue"]
    plt.figure(figsize=(10, 5.5))
    plt.plot(monthly["YearMonth"], monthly["Revenue"], marker="o")
    plt.title("Monthly Revenue Trend — 2025")
    plt.xlabel("Month")
    plt.ylabel("Revenue (NPR)")
    plt.xticks(rotation=45)
    plt.grid(axis="y", alpha=0.25)
    save_current_figure("monthly_revenue_trend.png")

    branch = tables["branch_summary"].sort_values("Revenue")
    plt.figure(figsize=(10, 6))
    plt.barh(branch["Branch"], branch["Revenue"])
    plt.title("Revenue by Branch")
    plt.xlabel("Revenue (NPR)")
    plt.ylabel("Branch")
    save_current_figure("branch_revenue.png")

    category = tables["category_summary"].sort_values("Revenue")
    plt.figure(figsize=(9, 5.5))
    plt.barh(category["ProductCategory"], category["Revenue"])
    plt.title("Revenue by Product Category")
    plt.xlabel("Revenue (NPR)")
    plt.ylabel("Product Category")
    save_current_figure("category_revenue.png")

    payment = tables["payment_summary"]
    plt.figure(figsize=(8.5, 5.5))
    plt.bar(payment["PaymentMethod"], payment["LineItems"])
    plt.title("Payment Method Usage")
    plt.xlabel("Payment Method")
    plt.ylabel("Number of Line Items")
    plt.xticks(rotation=30, ha="right")
    save_current_figure("payment_method_usage.png")

    plt.figure(figsize=(9, 5.5))
    plt.hist(df["TotalAmount"], bins=40)
    plt.title("Distribution of Line-item Total Amount")
    plt.xlabel("TotalAmount (NPR)")
    plt.ylabel("Frequency")
    save_current_figure("total_amount_distribution.png")

    day = tables["day_revenue"]
    plt.figure(figsize=(9, 5.5))
    plt.bar(day["DayOfWeek"], day["Revenue"])
    plt.title("Revenue by Day of Week")
    plt.xlabel("Day")
    plt.ylabel("Revenue (NPR)")
    plt.xticks(rotation=30)
    save_current_figure("revenue_by_day.png")

    top_products = tables["product_revenue"].head(10).sort_values("Revenue")
    plt.figure(figsize=(10, 6))
    plt.barh(top_products["ProductName"], top_products["Revenue"])
    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue (NPR)")
    plt.ylabel("Product")
    save_current_figure("top_products_revenue.png")


def train_model(df: pd.DataFrame) -> tuple[Pipeline, dict, pd.DataFrame]:
    """Train a Random Forest model and calculate original-feature importance."""
    features = ["Quantity", "UnitPrice", "Branch", "ProductCategory"]
    target = "TotalAmount"
    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    numeric_features = ["Quantity", "UnitPrice"]
    categorical_features = ["Branch", "ProductCategory"]
    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", "passthrough", numeric_features),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_features,
            ),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=1,
    )
    pipeline = Pipeline(
        steps=[("preprocessing", preprocessing), ("model", model)]
    )
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    rmse = math.sqrt(mean_squared_error(y_test, predictions))
    metrics = {
        "model": "RandomForestRegressor",
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "r2": float(r2_score(y_test, predictions)),
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(rmse),
    }

    perm = permutation_importance(
        pipeline,
        X_test,
        y_test,
        scoring="r2",
        n_repeats=5,
        random_state=42,
        n_jobs=-1,
    )
    importance = pd.DataFrame(
        {
            "Feature": X_test.columns,
            "ImportanceMean": perm.importances_mean,
            "ImportanceStd": perm.importances_std,
        }
    ).sort_values("ImportanceMean", ascending=False)
    positive_total = importance["ImportanceMean"].clip(lower=0).sum()
    importance["RelativeImportancePercent"] = np.where(
        positive_total > 0,
        importance["ImportanceMean"].clip(lower=0) / positive_total * 100,
        0,
    )

    return pipeline, metrics, importance


def export_outputs(
    raw_df: pd.DataFrame,
    clean_df: pd.DataFrame,
    cleaning_summary: dict,
    tables: dict[str, pd.DataFrame],
    model_metrics: dict,
    feature_importance: pd.DataFrame,
) -> None:
    """Write cleaned data and all result tables to the outputs folder."""
    clean_df.to_csv(OUTPUTS_DIR / "BSCS_cleaned.csv", index=False)

    quality = pd.concat(
        [
            data_quality_table(raw_df, "Raw"),
            data_quality_table(clean_df, "Cleaned"),
        ],
        ignore_index=True,
    )
    quality.to_csv(OUTPUTS_DIR / "data_quality_summary.csv", index=False)

    for name, table in tables.items():
        if name == "basket_values":
            table.to_csv(OUTPUTS_DIR / "transaction_baskets.csv", index=False)
        elif isinstance(table, pd.DataFrame):
            table.to_csv(OUTPUTS_DIR / f"{name}.csv", index=True if name in {"correlation", "payment_branch_counts", "payment_branch_share"} else False)

    feature_importance.to_csv(OUTPUTS_DIR / "model_feature_importance.csv", index=False)
    with open(OUTPUTS_DIR / "model_metrics.json", "w", encoding="utf-8") as file:
        json.dump(model_metrics, file, indent=2)
    with open(OUTPUTS_DIR / "cleaning_summary.json", "w", encoding="utf-8") as file:
        json.dump(cleaning_summary, file, indent=2)


def write_report(
    raw_df: pd.DataFrame,
    clean_df: pd.DataFrame,
    cleaning_summary: dict,
    tables: dict[str, pd.DataFrame],
    model_metrics: dict,
    feature_importance: pd.DataFrame,
) -> None:
    """Generate a complete markdown answer report for Q1–Q17."""
    raw_missing = raw_df.isna().sum()
    raw_missing_pct = raw_missing.div(len(raw_df)).mul(100)
    numeric_summary = raw_df[["Quantity", "UnitPrice", "TotalAmount"]].describe().round(2)

    category = tables["category_summary"]
    branch = tables["branch_summary"]
    city = tables["city_summary"]
    payment = tables["payment_summary"]
    monthly = tables["monthly_revenue"]
    day = tables["day_revenue"]
    week = tables["weekend_weekday"]
    customers = tables["customer_summary"]
    correlation = tables["correlation"]
    thresholds = tables["outlier_thresholds"]

    most_used_payment = payment.iloc[0]
    top_branch = branch.iloc[0]
    top_city = city.iloc[0]
    top_revenue_category = category.iloc[0]
    top_transaction_category = category.sort_values("UniqueTransactions", ascending=False).iloc[0]
    top_quantity_product = tables["product_quantity"].iloc[0]
    top_revenue_product = tables["product_revenue"].iloc[0]
    top_customer = customers.iloc[0]
    most_revenue_day = day.loc[day["Revenue"].idxmax()]
    skewness = clean_df["TotalAmount"].skew()
    repeat_count = int((customers["Transactions"] > 1).sum())
    one_time_count = int((customers["Transactions"] == 1).sum())
    average_customer_spend = customers["TotalSpend"].mean()
    highest_atv_branch = branch.sort_values("AverageTransactionValue", ascending=False).iloc[0]
    highest_payment_avg = payment.sort_values("AverageLineValue", ascending=False).iloc[0]
    known_payment = payment[payment["PaymentMethod"] != "Unknown"]
    highest_known_payment_avg = known_payment.sort_values("AverageLineValue", ascending=False).iloc[0]
    peak_month = monthly.loc[monthly["Revenue"].idxmax()]
    low_month = monthly.loc[monthly["Revenue"].idxmin()]

    weekday_row = week.loc[week["DayType"] == "Weekday"].iloc[0]
    weekend_row = week.loc[week["DayType"] == "Weekend"].iloc[0]
    daily_comparison = (
        "weekends"
        if weekend_row["AverageDailyRevenue"] > weekday_row["AverageDailyRevenue"]
        else "weekdays"
    )

    missing_lines = "\n".join(
        f"- `{column}`: {int(raw_missing[column]):,} missing ({raw_missing_pct[column]:.2f}%)"
        for column in raw_df.columns
        if raw_missing[column] > 0
    )

    report = f"""# BSCS — Complete Analysis Answers

## Project overview

The raw dataset contains **{len(raw_df):,} rows and {raw_df.shape[1]} columns**. After removing only exact duplicate rows, the cleaned dataset contains **{len(clean_df):,} line-items** representing **{clean_df['TransactionID'].nunique():,} unique transactions**.

## Step 1 — Load libraries (Q1)

Use `pandas` and `numpy` for loading, cleaning, transformation, and aggregation; `matplotlib` for visualisation; and `scikit-learn` for preprocessing, modelling, and evaluation. `pathlib` is used for safe file paths.

```python
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
```

## Step 2 — Load dataset (Q2)

```python
data_path = Path("data/BSCS.csv")
df = pd.read_csv(data_path)
```

The assignment text refers to both `BSCS.csv` and `BS.csv`. This project standardises the filename as `data/BSCS.csv`.

## Step 3 — Inspect dataset (Q3)

### Q3a — First five rows

```text
{raw_df.head().to_string(index=False)}
```

### Q3b — Shape

- Rows: **{len(raw_df):,}**
- Columns: **{raw_df.shape[1]}**

### Q3c — Column names

```python
{raw_df.columns.tolist()}
```

## Step 4 — Data types and structure (Q4)

### Q4a — Data types

```text
{raw_df.dtypes.to_string()}
```

`Date` initially loads as `object` and must be converted to `datetime64[ns]`. The other initial types are suitable: identifiers and categories are objects, `Quantity` is integer, and prices/amounts are floating point numbers.

### Q4b — Numeric summary

```text
{numeric_summary.to_string()}
```

The summary shows that quantities range from **{int(raw_df['Quantity'].min())} to {int(raw_df['Quantity'].max())}**. The line-item amount ranges from **{money(raw_df['TotalAmount'].min())} to {money(raw_df['TotalAmount'].max())}**. The mean line value is **{money(raw_df['TotalAmount'].mean())}**, while the median is **{money(raw_df['TotalAmount'].median())}**, indicating that expensive products raise the average above the median.

## Step 5 — Detect data-quality issues (Q5)

### Q5a — Missing values

{missing_lines}

All other raw columns have zero missing values.

### Q5b — Exact duplicates

There are **{cleaning_summary['exact_duplicate_rows']:,} fully duplicated rows**.

### Q5c — Genuine line-items versus duplicates

`TransactionID` is not a unique row key. The cleaned data contains **{cleaning_summary['unique_transaction_ids']:,} transaction IDs**, and **{cleaning_summary['multi_line_transaction_ids']:,}** of them contain more than one line-item. The largest basket has **{cleaning_summary['maximum_lines_in_one_transaction']} line-items**. Therefore, a row is removed only when *all columns* are identical. Repeated transaction IDs with different products, quantities, or prices are retained.

### Q5d — Illogical totals

Using a tolerance of one paisa:

```python
mismatch = (df["TotalAmount"] - df["Quantity"] * df["UnitPrice"]).abs() > 0.01
```

There are **{cleaning_summary['total_mismatches_before_correction']} mismatches** after missing unit prices are recovered. This means the available totals are logically consistent with `Quantity × UnitPrice`.

## Step 6 — Remove duplicate rows (Q6)

```python
before = len(df)
df = df.drop_duplicates(keep="first").copy()
after = len(df)
print("Rows removed:", before - after)
```

Rows changed from **{cleaning_summary['raw_rows']:,}** to **{cleaning_summary['rows_after_duplicate_removal']:,}**, so **{cleaning_summary['rows_removed']:,} rows** were removed.

## Step 7 — Handle missing values (Q7)

### Q7a — CustomerName

Each observed `CustomerID` maps consistently to one name, so missing names are filled from the ID-to-name mapping. This is better than using the most common customer name because it preserves identity.

### Q7b — ProductCategory

Every observed `ProductName` maps consistently to one category. Missing categories are therefore filled with the modal category for the same product.

### Q7c — UnitPrice

Because quantity is never zero, missing prices are recovered as:

```python
df.loc[df["UnitPrice"].isna(), "UnitPrice"] = (
    df["TotalAmount"] / df["Quantity"]
)
```

Product-level, category-level, and global medians are included only as fallbacks.

### Q7d — PaymentMethod

Missing payment methods are changed to `Unknown`. Dropping those rows would discard valid revenue, while guessing a popular payment method would distort the payment analysis. A missingness flag is also retained.

### Q7e — Verification

```python
print(df.isna().sum())
print("Total missing:", df.isna().sum().sum())
```

The final cleaned dataset has **{cleaning_summary['remaining_missing_values']} remaining missing values**.

## Step 8 — Cleaning and feature engineering (Q8)

### Q8a — Date features

```python
df["Date"] = pd.to_datetime(df["Date"])
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["MonthName"] = df["Date"].dt.month_name()
df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
df["DayOfWeek"] = df["Date"].dt.day_name()
df["IsWeekend"] = df["Date"].dt.dayofweek >= 5
```

### Q8b — City

```python
df["City"] = df["Branch"].str.split(" - ", n=1).str[0].str.strip()
```

### Q8c — Total validation

```python
df["CalculatedTotal"] = (df["Quantity"] * df["UnitPrice"]).round(2)
df["TotalDifference"] = (df["TotalAmount"] - df["CalculatedTotal"]).round(2)
```

No inconsistent totals remained after recovering unit prices.

## Step 9 — Univariate analysis (Q9)

### Q9a — Product-category distribution

The category table is saved as `outputs/category_summary.csv`. The most common category by line-items is **{category.sort_values('LineItems', ascending=False).iloc[0]['ProductCategory']}** with **{int(category.sort_values('LineItems', ascending=False).iloc[0]['LineItems']):,} line-items**.

### Q9b — Branch distribution

The branch with the most line-items is **{branch.sort_values('LineItems', ascending=False).iloc[0]['Branch']}** with **{int(branch.sort_values('LineItems', ascending=False).iloc[0]['LineItems']):,} line-items**.

### Q9c — Most common payment method

**{most_used_payment['PaymentMethod']}** is the most common payment method, appearing in **{int(most_used_payment['LineItems']):,} line-items ({most_used_payment['UsageSharePercent']:.2f}%)**.

### Q9d — Distribution of TotalAmount

The skewness is **{skewness:.2f}**, so `TotalAmount` is **positively/right skewed**. Most sales lines are relatively modest, while electronics and apparel create a smaller number of high-value lines.

## Step 10 — Sales trend analysis (Q10)

### Q10a — Month-over-month revenue

Revenue is highest in **{peak_month['YearMonth']}** at **{money(peak_month['Revenue'])}** and lowest in **{low_month['YearMonth']}** at **{money(low_month['Revenue'])}**. Full values and month-over-month changes are in `outputs/monthly_revenue.csv` and the chart `images/monthly_revenue_trend.png`.

### Q10b — Weekends versus weekdays

- Weekday total revenue: **{money(weekday_row['TotalRevenue'])}**; average per day: **{money(weekday_row['AverageDailyRevenue'])}**
- Weekend total revenue: **{money(weekend_row['TotalRevenue'])}**; average per day: **{money(weekend_row['AverageDailyRevenue'])}**

Total weekday revenue is naturally larger because there are more weekdays. On a fair average-daily basis, **{daily_comparison} generate higher sales**.

### Q10c — Best day of week

**{most_revenue_day['DayOfWeek']}** generates the highest total revenue at **{money(most_revenue_day['Revenue'])}**.

## Step 11 — Branch and city performance (Q11)

### Q11a — Highest-revenue branch

**{top_branch['Branch']}** ranks first with **{money(top_branch['Revenue'])}** in revenue.

### Q11b — Average transaction value by branch

Basket value is calculated after summing all line-items within each `TransactionID`. The highest average transaction value is at **{highest_atv_branch['Branch']}**, averaging **{money(highest_atv_branch['AverageTransactionValue'])}** per basket. The complete comparison is in `outputs/branch_summary.csv`.

### Q11c — Highest-revenue city

**{top_city['City']}** contributes the most revenue at **{money(top_city['Revenue'])}**. Kathmandu includes two branches and therefore benefits from combined coverage.

## Step 12 — Product analysis (Q12)

### Q12a — Category revenue versus transactions

- Highest revenue category: **{top_revenue_category['ProductCategory']}** — **{money(top_revenue_category['Revenue'])}**
- Most unique transactions: **{top_transaction_category['ProductCategory']}** — **{int(top_transaction_category['UniqueTransactions']):,} transactions**

This distinction matters because a category may sell frequently without generating the highest value.

### Q12b — Best-selling product by quantity

The top product is **{top_quantity_product['ProductName']}**, with **{int(top_quantity_product['QuantitySold']):,} units sold**. The top 10 are in `outputs/product_quantity.csv`.

### Q12c — Top product by revenue

The highest-revenue product is **{top_revenue_product['ProductName']}**, generating **{money(top_revenue_product['Revenue'])}**. The top 10 are in `outputs/product_revenue.csv`.

## Step 13 — Customer analysis (Q13)

### Q13a — Highest-spending customer

**{top_customer['CustomerName']} ({top_customer['CustomerID']})** is the top customer, spending **{money(top_customer['TotalSpend'])}** across **{int(top_customer['Transactions'])} transactions**.

### Q13b — Repeat versus one-time customers

- Repeat customers: **{repeat_count:,}**
- One-time customers: **{one_time_count:,}**

A repeat customer is defined as a `CustomerID` appearing in more than one distinct `TransactionID`.

### Q13c — Average spend per customer

The average total spend per customer, used as a simple customer-lifetime-value proxy for this one-year dataset, is **{money(average_customer_spend)}**.

## Step 14 — Payment-method analysis (Q14)

### Q14a — Payment method by branch

`outputs/payment_branch_share.csv` contains row percentages for each branch. It shows which branches are more cash-heavy or digital-heavy. Because payment methods vary across some line-items within the same transaction ID, this analysis is explicitly line-item based and should not be interpreted as a definitive basket-level tender record.

### Q14b — Average value by payment method

The `Unknown` group has the highest observed average line value at **{money(highest_payment_avg['AverageLineValue'])}**, but it is a missing-data category rather than a real tender type. Among known methods, **{highest_known_payment_avg['PaymentMethod']}** has the highest average line value at **{money(highest_known_payment_avg['AverageLineValue'])}**. The full comparison is in `outputs/payment_summary.csv`.

## Step 15 — Correlation and outliers (Q15)

### Q15a — Correlation

```text
{correlation.round(3).to_string()}
```

`TotalAmount` has a strong relationship with `UnitPrice` because amount is mathematically determined by price and quantity. Quantity also raises total value, but its linear correlation can be lower because product prices vary substantially.

### Q15b — IQR outliers

At line-item level, the upper IQR boundary is **{money(thresholds.loc[thresholds['Level']=='Line item','UpperBound'].iloc[0])}**, producing **{int(thresholds.loc[thresholds['Level']=='Line item','OutlierCount'].iloc[0]):,} outlier lines**. At complete basket level, the upper boundary is **{money(thresholds.loc[thresholds['Level']=='Transaction basket','UpperBound'].iloc[0])}**, producing **{int(thresholds.loc[thresholds['Level']=='Transaction basket','OutlierCount'].iloc[0]):,} outlier transactions**. These are not automatically errors; many represent legitimate expensive products or large baskets.

## Step 16 — Predictive modelling (Q16)

### Q16a — Model performance

A `RandomForestRegressor` predicts line-item `TotalAmount` from `Quantity`, `UnitPrice`, `Branch`, and `ProductCategory` using an 80/20 train-test split.

- R²: **{model_metrics['r2']:.4f}**
- MAE: **{money(model_metrics['mae'])}**
- RMSE: **{money(model_metrics['rmse'])}**

The very high performance is expected because `TotalAmount` is defined by `Quantity × UnitPrice`; this is a demonstration model rather than a real forecasting model.

### Q16b — Feature importance

```text
{feature_importance.round(4).to_string(index=False)}
```

`UnitPrice` and `Quantity` are expected to dominate. Branch and category contribute little after the direct pricing variables are known.

## Step 17 — Business insights and recommendations (Q17)

1. **Prioritise the strongest branch and city while protecting growth elsewhere.** {top_branch['Branch']} leads revenue, and {top_city['City']} leads at city level. Management should compare stock availability, floor space, customer traffic, and promotional activity to determine whether the performance can be replicated.
2. **Separate volume categories from value categories.** {top_transaction_category['ProductCategory']} has the broadest transaction reach, while {top_revenue_category['ProductCategory']} creates the greatest revenue. Volume categories can support traffic and cross-selling; high-value categories deserve inventory protection, security, and targeted promotions.
3. **Use the monthly pattern for staffing and inventory planning.** Prepare higher staffing levels and safety stock before {peak_month['YearMonth']}, while using the lower-demand period around {low_month['YearMonth']} for maintenance, training, and clearance campaigns.
4. **Strengthen digital-payment adoption using branch-level evidence.** The payment mix table identifies cash-heavy branches where signage, staff prompts, loyalty incentives, and reliable QR/card infrastructure could improve customer convenience.
5. **Develop customer retention programmes.** The customer table can support tiered loyalty rewards, personalised offers, and reactivation campaigns. CustomerID should be treated as the identity key because names are not unique.
6. **Investigate outliers rather than deleting them automatically.** High-value lines and baskets may be legitimate electronics, apparel, or multi-item purchases. Review the outlier list for fraud, entry error, returns, or valuable customer segments.
7. **Improve source-system controls.** The raw file contained {cleaning_summary['exact_duplicate_rows']:,} exact duplicates and missing values in four fields. Add validation rules, required fields, unique line identifiers, and controlled category/product master data. Retain explicit missingness flags so future analysts can audit imputation decisions.

## Generated files

- `outputs/BSCS_cleaned.csv`
- `outputs/data_quality_summary.csv`
- All analysis summary tables in `outputs/`
- Model metrics and feature importance
- Seven charts in `images/`
"""
    (OUTPUTS_DIR / "analysis_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    print("Loading dataset...")
    raw_df = load_data()
    print(f"Raw shape: {raw_df.shape}")

    print("Cleaning dataset...")
    clean_df, cleaning_summary = clean_data(raw_df)
    print(f"Cleaned shape: {clean_df.shape}")

    print("Building analysis tables...")
    tables = build_analysis_tables(clean_df)

    print("Creating visualizations...")
    create_visualizations(clean_df, tables)

    print("Training predictive model...")
    _, model_metrics, feature_importance = train_model(clean_df)

    print("Exporting outputs...")
    export_outputs(
        raw_df,
        clean_df,
        cleaning_summary,
        tables,
        model_metrics,
        feature_importance,
    )
    write_report(
        raw_df,
        clean_df,
        cleaning_summary,
        tables,
        model_metrics,
        feature_importance,
    )

    print("\nAnalysis complete.")
    print(f"Cleaned data: {OUTPUTS_DIR / 'BSCS_cleaned.csv'}")
    print(f"Answer report: {OUTPUTS_DIR / 'analysis_report.md'}")
    print(f"Charts folder: {IMAGES_DIR}")
    print("Model metrics:", json.dumps(model_metrics, indent=2))


if __name__ == "__main__":
    main()
