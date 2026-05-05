import pandas as pd

print("Loading cleaned dataset...")

# Load preprocessed dataset
df = pd.read_csv("data/processed/loans_cleaned.csv", low_memory=False)
print(f"Initial rows: {len(df):,}")

# ── Filter closed loans only ─────────────────────────────────────

CLOSED_STATUSES = [
    "Charged Off",
    "Default",
    "Does not meet the credit policy. Status:Charged Off",
    "Fully Paid",
    "Does not meet the credit policy. Status:Fully Paid",
]

df = df[df["loan_status"].isin(CLOSED_STATUSES)].copy()

# ── Outcome classification ───────────────────────────────────────

LOSS_STATUSES = [
    "Charged Off",
    "Default",
    "Does not meet the credit policy. Status:Charged Off",
]

df["outcome"] = df["loan_status"].apply(
    lambda x: "loss" if x in LOSS_STATUSES else "paid"
)

# ── Validation ───────────────────────────────────────────────────

total_loans = len(df)
loss_loans = (df["outcome"] == "loss").sum()
paid_loans = (df["outcome"] == "paid").sum()

print("\nClosed loan summary:")
print(f"Total loans : {total_loans:,}")
print(f"Loss loans  : {loss_loans:,} ({loss_loans/total_loans:.2%})")
print(f"Paid loans  : {paid_loans:,} ({paid_loans/total_loans:.2%})")

print("\nLoan status distribution:")
print(df["loan_status"].value_counts())

# ── Save filtered dataset ────────────────────────────────────────

df.to_csv("data/processed/loans_portfolio.csv", index=False)

print("\nOutput saved: data/processed/loans_portfolio.csv")