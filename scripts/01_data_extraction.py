import pandas as pd

# Selected columns required for portfolio and risk analysis
TARGET_COLUMNS = [
    "loan_amnt",
    "funded_amnt",
    "term",
    "int_rate",
    "installment",
    "grade",
    "home_ownership",
    "annual_inc",
    "loan_status",
    "purpose",
    "issue_d",
    "dti",
    "fico_range_low",
    "emp_length",
    "delinq_2yrs",
    "revol_util",
    "inq_last_6mths",
    "recoveries",
    "total_rec_prncp",
    "total_rec_int",
    "collection_recovery_fee",
    "last_pymnt_d",
    "addr_state",
]

print("Reading dataset with selected columns...")

# Load dataset using only required fields to optimize memory usage
df = pd.read_csv(
    "accepted_2007_to_2018Q4.csv",
    usecols=TARGET_COLUMNS,
    low_memory=False
)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")

# Validate that all expected columns are present
missing_cols = set(TARGET_COLUMNS) - set(df.columns)
if missing_cols:
    print(f"Warning: missing columns detected -> {missing_cols}")

# Persist cleaned dataset for downstream processing
df.to_csv("data/processed/loans_extracted.csv", index=False)

print("Output saved: data/processed/loans_extracted.csv")