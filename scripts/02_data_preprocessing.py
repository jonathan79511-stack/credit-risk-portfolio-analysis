import pandas as pd

print("Loading dataset for preprocessing...")

# Load extracted dataset
df = pd.read_csv("loans_extracted.csv", low_memory=False)
print(f"Initial rows: {len(df):,}")

# ── Remove duplicates ────────────────────────────────────────────
df = df.drop_duplicates()
print(f"Rows after deduplication: {len(df):,}")

# ── Handle missing values ────────────────────────────────────────

# Employment length: treat missing as unknown category
df["emp_length"] = df["emp_length"].fillna("Unknown")

# Monetary fields: missing values treated as zero
monetary_cols = [
    "recoveries",
    "total_rec_prncp",
    "total_rec_int",
    "collection_recovery_fee",
]

for col in monetary_cols:
    df[col] = df[col].fillna(0)

# ── Standardize interest rate ────────────────────────────────────
# Convert percentage string to numeric (e.g., "13.56%" → 13.56)
df["int_rate"] = (
    df["int_rate"]
    .astype(str)
    .str.replace("%", "", regex=False)
)
df["int_rate"] = pd.to_numeric(df["int_rate"], errors="coerce")

# ── Standardize loan term ────────────────────────────────────────
# Extract numeric term in months (e.g., "36 months" → 36)
df["term"] = df["term"].astype(str).str.extract(r"(\d+)")
df["term"] = pd.to_numeric(df["term"], errors="coerce")

# ── Convert date fields ──────────────────────────────────────────
df["issue_d"] = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce")
df["last_pymnt_d"] = pd.to_datetime(df["last_pymnt_d"], format="%b-%Y", errors="coerce")

# ── Drop critical missing values ─────────────────────────────────
critical_cols = [
    "loan_amnt",
    "funded_amnt",
    "loan_status",
    "int_rate",
    "issue_d",
    "term",
]

df = df.dropna(subset=critical_cols)
print(f"Rows after dropping critical nulls: {len(df):,}")

# ── Save cleaned dataset ─────────────────────────────────────────
df.to_csv("loans_cleaned.csv", index=False)

print("-" * 40)
print("Preprocessing completed successfully")
print(f"Output file: loans_cleaned.csv")
print(f"Final columns: {len(df.columns)}")
print("-" * 40)