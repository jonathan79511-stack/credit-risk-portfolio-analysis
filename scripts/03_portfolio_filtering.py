import pandas as pd

print("Loading cleaned dataset...")

# Load preprocessed dataset
df = pd.read_csv("loans_cleaned.csv", low_memory=False)
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

# Classify loan outcome: loss vs paid
df["outcome"] = df["loan_status"].apply(
    lambda x: "loss" if x in LOSS_STATUSES else "paid"
)

# ── Validation ───────────────────────────────────────────────────

total_loans = len(df)
loss_loans = (df["outcome"] == "loss").sum()
paid_loans = (df["outcome"] == "paid").sum()

print("\nClosed loan summary:")
print(f"Total loans      : {total_loans:,}")
print(f"Loss loans       : {loss_loans:,} ({loss_loans/total_loans:.2%})")
print(f"Paid loans       : {paid_loans:,} ({paid_loans/total_loans:.2%})")

print("\nLoan status distribution:")
print(df["loan_status"].value_counts())

# Sanity check: ensure only expected statuses are present
unexpected = df[~df["loan_status"].isin(CLOSED_STATUSES)]
print(f"\nUnexpected records: {len(unexpected)}")

# ── Save filtered dataset ────────────────────────────────────────

df.to_csv("loans_portfolio.csv", index=False)

print("\nOutput saved: loans_portfolio.csv")