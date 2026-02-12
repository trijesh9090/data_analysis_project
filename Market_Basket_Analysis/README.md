# Market Basket Analysis – Groceries Dataset

This project uses **Market Basket Analysis** on a groceries dataset to understand:
- Which products sell the most
- How sales change over time
- Which products are often bought together (associations)

All code is in:

- `Market Basket Analysis.ipynb`

---

## Goal

- Explore the groceries data and basic sales patterns  
- Identify **top‑selling products** overall and by time (year, month, weekday)  
- Build a **customer–item matrix** and run **Apriori**  
- Generate **association rules** (support, confidence, lift) to find items that are frequently purchased together

---

## Data

### `Groceries_dataset.csv`

This dataset contains transactional data from a grocery store. Each row corresponds to a single item purchased in a specific transaction.

**Columns:**
- `Member_number` (int): Anonymized customer identifier.
- `Date` (date): Purchase date (format: `YYYY-MM-DD`).
- `itemDescription` (string): Name/description of the purchased product.

Typical uses for this dataset include:
- Market basket analysis
- Association rule mining (e.g., Apriori)
- Customer purchasing pattern analysis

---

## What the Notebook Does

1. **Load & prepare data**
   - Read CSV, clean column names, capitalize item names
   - Create `Year`, `Month`, `Week Day` from `Date`

2. **Exploratory analysis**
   - Count total items and unique products
   - Top 15 best‑selling products
   - Total items sold by:
     - Year
     - Month
     - Weekday
   - Top 10 products per month

3. **Market Basket Analysis**
   - Group by `Member_number` and `Item` to get quantities
   - Pivot to a **one‑hot** customer–item matrix (0/1)
   - Run **Apriori** with `min_support = 0.01`
   - Generate **association rules** with `metric="lift"`, `min_threshold=1`
   - Inspect first 100 rules

---

## Main Findings (High Level)

- A small set of products account for much of total sales (top 15 items).  
- Sales volume varies by **year, month, and weekday**, showing clear time patterns.  
- Each month has its own **top products**, useful for monthly planning.  
- Association rules reveal **product pairs/groups that tend to be bought together**, which can be used for:
  - Cross‑selling and recommendations  
  - Bundling and promotions  
  - Shelf / layout decisions  

(Exact item names and metrics are visible in the notebook outputs.)

---

## How to Run

Then open and run:

```text
Market Basket Analysis.ipynb
```

Run all cells in order to reproduce the analysis and rules.

---

## Files

- `Groceries_dataset.csv` – source data  
- `Market Basket Analysis.ipynb` – analysis and model notebook  
- `README.md` – this project summary