# BSCS Streamlit Dashboard

## Run on macOS in VS Code

From the `BSCS_VSCode_Project` folder:

```bash
source venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

Streamlit will normally open the dashboard automatically in your browser. If it does not, open the local URL shown in the terminal, usually `http://localhost:8501`.

## Dashboard sections

1. Overview
2. Branches & Cities
3. Products & Categories
4. Customers & Payments
5. Data Quality & Model
6. Data Explorer

The dashboard first uses `outputs/BSCS_cleaned.csv`. If that file is missing, it rebuilds the cleaned data from `data/BSCS.csv` using the cleaning function in `src/bscs_analysis.py`.
