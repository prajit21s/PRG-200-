# BSCS — Bhatbhateni Sales Cleaning & Solutions: Project Questions
### Dataset: `BSCS.csv` (18,812 rows | 11 columns | contains injected nulls + duplicate rows)

---

## Step 1: Load Your Libraries
**Q1.** Which Python libraries do you need to load, explore, clean, visualize, and model this dataset?

---

## Step 2: Load Your Dataset
**Q2.** How do you load `BS.csv` into a pandas DataFrame?

---

## Step 3: Inspect Your Dataset
**Q3a.** What do the first five rows look like?
**Q3b.** How many rows and columns does the dataset have?
**Q3c.** What are the column names?

---

## Step 4: Understand Data Types and Structure
**Q4a.** What are the data types of each column, and does anything need converting?
**Q4b.** What do the summary statistics of the numeric columns tell you?

---

## Step 5: Detect Data Quality Issues
**Q5a.** Are there any missing values in the dataset? Which columns are affected, and by how much (count and %)?
**Q5b.** Are there any fully duplicated rows? How many?
**Q5c.** `TransactionID` can repeat for the same order (multi-item baskets). How do you distinguish genuine repeat line-items from true duplicate rows?
**Q5d.** Are there any illogical values, e.g. `TotalAmount` not equal to `Quantity * UnitPrice`?

---

## Step 6: Handle Duplicate Rows
**Q6a.** How do you remove exact duplicate rows while keeping one copy of each?
**Q6b.** How do you verify that the duplicates were removed correctly (before/after row counts)?

---

## Step 7: Handle Missing Values
**Q7a.** For `CustomerName` (categorical, identity field), what's a sensible way to handle nulls?
**Q7b.** For `ProductCategory` (categorical), how could you fill missing values using other information in the row (e.g., `ProductName`)?
**Q7c.** For `UnitPrice` (numeric), how do you impute missing values sensibly (e.g., using `TotalAmount / Quantity`, or category-level median)?
**Q7d.** For `PaymentMethod` (categorical), should you impute, flag as "Unknown", or drop? Justify your choice.
**Q7e.** After cleaning, how do you confirm there are no remaining missing values?

---

## Step 8: Data Cleaning & Feature Engineering
**Q8a.** How do you convert `Date` into a proper datetime column and extract useful time features?
**Q8b.** How do you split `Branch` into a `City` column for city-level aggregation?
**Q8c.** How do you recompute or validate `TotalAmount` after fixing missing `UnitPrice` values?

---

## Step 9: Univariate Analysis
**Q9a.** What is the distribution of transactions across product categories (post-cleaning)?
**Q9b.** What is the distribution of transactions across branches?
**Q9c.** Which payment method is most commonly used?
**Q9d.** What does the distribution of `TotalAmount` look like — is it skewed?

---

## Step 10: Sales Trend Analysis (Time Series)
**Q10a.** How does total revenue trend month-over-month across 2025?
**Q10b.** Are sales higher on weekends vs. weekdays?
**Q10c.** Which day of the week generates the most revenue?

---

## Step 11: Branch & City Performance Analysis
**Q11a.** Which branch generates the highest total revenue?
**Q11b.** How does average transaction value (basket size) differ by branch?
**Q11c.** Which city contributes the most to overall revenue?

---

## Step 12: Product Category & Product Analysis
**Q12a.** Which product category generates the most revenue vs. the most transactions?
**Q12b.** What are the top 10 best-selling products by quantity sold?
**Q12c.** What are the top 10 products by total revenue generated?

---

## Step 13: Customer Analysis
**Q13a.** Who are the top 10 customers by total spend?
**Q13b.** How many repeat customers are there vs. one-time shoppers?
**Q13c.** What is the average spend per customer (customer lifetime value proxy)?

---

## Step 14: Payment Method Analysis
**Q14a.** Does payment method vary by branch (cash-heavy vs. digital-heavy branches)?
**Q14b.** Is there a difference in average transaction value across payment methods?

---

## Step 15: Correlation & Outlier Detection
**Q15a.** How are `Quantity`, `UnitPrice`, and `TotalAmount` correlated?
**Q15b.** Are there any outlier transactions in `TotalAmount` (e.g., using IQR)?

---

## Step 16: Predictive Modeling (Optional Advanced Step)
**Q16a.** Can you build a simple model to predict `TotalAmount` from `Quantity`, `UnitPrice`, `Branch`, and `ProductCategory`?
**Q16b.** Which features matter most in predicting transaction value?

---

## Step 17: Business Insights & Recommendations
**Q17.** Based on the analysis above, what actionable insights and recommendations can you write for management — including a note on the data quality issues you found and how you resolved them?

---

## Step 18: Documentation Checklist (For Your Portfolio/GitHub)
- [ ] Add a project README explaining the raw data had nulls and duplicates, and document your cleaning decisions
- [ ] Include a "Data Cleaning" section in the notebook, separate from the "Analysis" section
- [ ] Add before/after row counts and null counts as a quick data-quality summary table
- [ ] Add 3–5 key visualizations to the README (branch revenue, monthly trend, category mix)
- [ ] Push to GitHub with a clean folder structure: `/data`, `/notebooks`, `/images`, `README.md`
