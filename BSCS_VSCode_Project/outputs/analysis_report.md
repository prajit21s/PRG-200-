# BSCS — Complete Analysis Answers

## Project overview

The raw dataset contains **18,812 rows and 11 columns**. After removing only exact duplicate rows, the cleaned dataset contains **18,088 line-items** representing **6,000 unique transactions**.

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
TransactionID       Date CustomerID   CustomerName                   Branch ProductCategory          ProductName  Quantity  UnitPrice  TotalAmount PaymentMethod
    TXN101590 2025-05-19   CUST1100 Sujan Shrestha       Pokhara - Lakeside          Bakery Chocolate Cake Slice         2     171.29       342.58        Khalti
    TXN103282 2025-03-07   CUST1005     Milan Lama   Butwal - Traffic Chowk   Personal Care            Dove Soap         3     149.59       448.77         eSewa
    TXN103539 2025-10-05   CUST1130      Alina Rai Bhaktapur - Suryabinayak         Apparel        Winter Jacket         4    2794.25     11177.00        Khalti
    TXN102479 2025-11-12   CUST1057     Neha Karki     Kathmandu - New Road       Household       Surf Excel 1kg         4     399.62      1598.48          Cash
    TXN104408 2025-10-09   CUST1005     Milan Lama   Butwal - Traffic Chowk       Beverages Gorkha Beer (6-pack)         2     281.01       562.02         eSewa
```

### Q3b — Shape

- Rows: **18,812**
- Columns: **11**

### Q3c — Column names

```python
['TransactionID', 'Date', 'CustomerID', 'CustomerName', 'Branch', 'ProductCategory', 'ProductName', 'Quantity', 'UnitPrice', 'TotalAmount', 'PaymentMethod']
```

## Step 4 — Data types and structure (Q4)

### Q4a — Data types

```text
TransactionID          str
Date                   str
CustomerID             str
CustomerName           str
Branch                 str
ProductCategory        str
ProductName            str
Quantity             int64
UnitPrice          float64
TotalAmount        float64
PaymentMethod          str
```

`Date` initially loads as `object` and must be converted to `datetime64[ns]`. The other initial types are suitable: identifiers and categories are objects, `Quantity` is integer, and prices/amounts are floating point numbers.

### Q4b — Numeric summary

```text
       Quantity  UnitPrice  TotalAmount
count  18812.00   18441.00     18812.00
mean       2.51     728.80      1819.99
std        1.11     766.35      2241.97
min        1.00      40.14        40.61
25%        2.00     240.16       488.40
50%        3.00     416.78       989.00
75%        3.00     848.32      2142.54
max        4.00    3499.28     13997.12
```

The summary shows that quantities range from **1 to 4**. The line-item amount ranges from **NPR 40.61 to NPR 13,997.12**. The mean line value is **NPR 1,819.99**, while the median is **NPR 989.00**, indicating that expensive products raise the average above the median.

## Step 5 — Detect data-quality issues (Q5)

### Q5a — Missing values

- `CustomerName`: 568 missing (3.02%)
- `ProductCategory`: 282 missing (1.50%)
- `UnitPrice`: 371 missing (1.97%)
- `PaymentMethod`: 468 missing (2.49%)

All other raw columns have zero missing values.

### Q5b — Exact duplicates

There are **724 fully duplicated rows**.

### Q5c — Genuine line-items versus duplicates

`TransactionID` is not a unique row key. The cleaned data contains **6,000 transaction IDs**, and **4,823** of them contain more than one line-item. The largest basket has **5 line-items**. Therefore, a row is removed only when *all columns* are identical. Repeated transaction IDs with different products, quantities, or prices are retained.

### Q5d — Illogical totals

Using a tolerance of one paisa:

```python
mismatch = (df["TotalAmount"] - df["Quantity"] * df["UnitPrice"]).abs() > 0.01
```

There are **0 mismatches** after missing unit prices are recovered. This means the available totals are logically consistent with `Quantity × UnitPrice`.

## Step 6 — Remove duplicate rows (Q6)

```python
before = len(df)
df = df.drop_duplicates(keep="first").copy()
after = len(df)
print("Rows removed:", before - after)
```

Rows changed from **18,812** to **18,088**, so **724 rows** were removed.

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

The final cleaned dataset has **0 remaining missing values**.

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

The category table is saved as `outputs/category_summary.csv`. The most common category by line-items is **Grocery** with **3,065 line-items**.

### Q9b — Branch distribution

The branch with the most line-items is **Kathmandu - Kupondole** with **3,241 line-items**.

### Q9c — Most common payment method

**Cash** is the most common payment method, appearing in **6,218 line-items (34.38%)**.

### Q9d — Distribution of TotalAmount

The skewness is **2.46**, so `TotalAmount` is **positively/right skewed**. Most sales lines are relatively modest, while electronics and apparel create a smaller number of high-value lines.

## Step 10 — Sales trend analysis (Q10)

### Q10a — Month-over-month revenue

Revenue is highest in **2025-10** at **NPR 4,717,670.71** and lowest in **2025-05** at **NPR 1,804,819.74**. Full values and month-over-month changes are in `outputs/monthly_revenue.csv` and the chart `images/monthly_revenue_trend.png`.

### Q10b — Weekends versus weekdays

- Weekday total revenue: **NPR 23,705,495.89**; average per day: **NPR 90,825.65**
- Weekend total revenue: **NPR 9,298,649.75**; average per day: **NPR 89,410.09**

Total weekday revenue is naturally larger because there are more weekdays. On a fair average-daily basis, **weekdays generate higher sales**.

### Q10c — Best day of week

**Thursday** generates the highest total revenue at **NPR 4,876,393.65**.

## Step 11 — Branch and city performance (Q11)

### Q11a — Highest-revenue branch

**Kathmandu - Kupondole** ranks first with **NPR 5,988,126.62** in revenue.

### Q11b — Average transaction value by branch

Basket value is calculated after summing all line-items within each `TransactionID`. The highest average transaction value is at **Kathmandu - Kupondole**, averaging **NPR 5,719.32** per basket. The complete comparison is in `outputs/branch_summary.csv`.

### Q11c — Highest-revenue city

**Kathmandu** contributes the most revenue at **NPR 10,629,157.12**. Kathmandu includes two branches and therefore benefits from combined coverage.

## Step 12 — Product analysis (Q12)

### Q12a — Category revenue versus transactions

- Highest revenue category: **Electronics** — **NPR 10,419,134.62**
- Most unique transactions: **Grocery** — **2,519 transactions**

This distinction matters because a category may sell frequently without generating the highest value.

### Q12b — Best-selling product by quantity

The top product is **Wall Clock**, with **1,215 units sold**. The top 10 are in `outputs/product_quantity.csv`.

### Q12c — Top product by revenue

The highest-revenue product is **Wall Clock**, generating **NPR 2,459,453.52**. The top 10 are in `outputs/product_revenue.csv`.

## Step 13 — Customer analysis (Q13)

### Q13a — Highest-spending customer

**Kritika Bhattarai (CUST1002)** is the top customer, spending **NPR 1,286,840.72** across **221 transactions**.

### Q13b — Repeat versus one-time customers

- Repeat customers: **144**
- One-time customers: **3**

A repeat customer is defined as a `CustomerID` appearing in more than one distinct `TransactionID`.

### Q13c — Average spend per customer

The average total spend per customer, used as a simple customer-lifetime-value proxy for this one-year dataset, is **NPR 224,518.00**.

## Step 14 — Payment-method analysis (Q14)

### Q14a — Payment method by branch

`outputs/payment_branch_share.csv` contains row percentages for each branch. It shows which branches are more cash-heavy or digital-heavy. Because payment methods vary across some line-items within the same transaction ID, this analysis is explicitly line-item based and should not be interpreted as a definitive basket-level tender record.

### Q14b — Average value by payment method

The `Unknown` group has the highest observed average line value at **NPR 1,918.80**, but it is a missing-data category rather than a real tender type. Among known methods, **Khalti** has the highest average line value at **NPR 1,881.37**. The full comparison is in `outputs/payment_summary.csv`.

## Step 15 — Correlation and outliers (Q15)

### Q15a — Correlation

```text
             Quantity  UnitPrice  TotalAmount
Quantity        1.000     -0.005        0.361
UnitPrice      -0.005      1.000        0.848
TotalAmount     0.361      0.848        1.000
```

`TotalAmount` has a strong relationship with `UnitPrice` because amount is mathematically determined by price and quantity. Quantity also raises total value, but its linear correlation can be lower because product prices vary substantially.

### Q15b — IQR outliers

At line-item level, the upper IQR boundary is **NPR 4,648.61**, producing **1,763 outlier lines**. At complete basket level, the upper boundary is **NPR 16,855.11**, producing **165 outlier transactions**. These are not automatically errors; many represent legitimate expensive products or large baskets.

## Step 16 — Predictive modelling (Q16)

### Q16a — Model performance

A `RandomForestRegressor` predicts line-item `TotalAmount` from `Quantity`, `UnitPrice`, `Branch`, and `ProductCategory` using an 80/20 train-test split.

- R²: **1.0000**
- MAE: **NPR 1.10**
- RMSE: **NPR 2.74**

The very high performance is expected because `TotalAmount` is defined by `Quantity × UnitPrice`; this is a demonstration model rather than a real forecasting model.

### Q16b — Feature importance

```text
        Feature  ImportanceMean  ImportanceStd  RelativeImportancePercent
      UnitPrice          1.7634         0.0304                    75.6366
       Quantity          0.5680         0.0124                    24.3634
         Branch          0.0000         0.0000                     0.0000
ProductCategory          0.0000         0.0000                     0.0000
```

`UnitPrice` and `Quantity` are expected to dominate. Branch and category contribute little after the direct pricing variables are known.

## Step 17 — Business insights and recommendations (Q17)

1. **Prioritise the strongest branch and city while protecting growth elsewhere.** Kathmandu - Kupondole leads revenue, and Kathmandu leads at city level. Management should compare stock availability, floor space, customer traffic, and promotional activity to determine whether the performance can be replicated.
2. **Separate volume categories from value categories.** Grocery has the broadest transaction reach, while Electronics creates the greatest revenue. Volume categories can support traffic and cross-selling; high-value categories deserve inventory protection, security, and targeted promotions.
3. **Use the monthly pattern for staffing and inventory planning.** Prepare higher staffing levels and safety stock before 2025-10, while using the lower-demand period around 2025-05 for maintenance, training, and clearance campaigns.
4. **Strengthen digital-payment adoption using branch-level evidence.** The payment mix table identifies cash-heavy branches where signage, staff prompts, loyalty incentives, and reliable QR/card infrastructure could improve customer convenience.
5. **Develop customer retention programmes.** The customer table can support tiered loyalty rewards, personalised offers, and reactivation campaigns. CustomerID should be treated as the identity key because names are not unique.
6. **Investigate outliers rather than deleting them automatically.** High-value lines and baskets may be legitimate electronics, apparel, or multi-item purchases. Review the outlier list for fraud, entry error, returns, or valuable customer segments.
7. **Improve source-system controls.** The raw file contained 724 exact duplicates and missing values in four fields. Add validation rules, required fields, unique line identifiers, and controlled category/product master data. Retain explicit missingness flags so future analysts can audit imputation decisions.

## Generated files

- `outputs/BSCS_cleaned.csv`
- `outputs/data_quality_summary.csv`
- All analysis summary tables in `outputs/`
- Model metrics and feature importance
- Seven charts in `images/`
