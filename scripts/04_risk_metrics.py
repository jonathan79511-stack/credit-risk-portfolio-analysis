import pandas as pd
import numpy as np

print("Loading portfolio dataset...")

# Load filtered portfolio
df = pd.read_csv("data/processed/loans_portfolio.csv", low_memory=False)
print(f"Rows loaded: {len(df):,}")

# ── Standardize interest rate ────────────────────────────────────
if df["int_rate"].dtype == "object":
    df["int_rate"] = (
        df["int_rate"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )
    df["int_rate"] = pd.to_numeric(df["int_rate"], errors="coerce") / 100
elif df["int_rate"].max() > 1:
    df["int_rate"] = df["int_rate"] / 100

# ── Default flag ─────────────────────────────────────────────────
df["default_flag"] = (df["outcome"] == "loss").astype(int)

# ── Core financial metrics ───────────────────────────────────────
df["ead"] = (df["funded_amnt"] - df["total_rec_prncp"]).clip(lower=0)
df["net_recovery"] = df["recoveries"] - df["collection_recovery_fee"]

df["real_loss"] = 0.0
loss_mask = df["default_flag"] == 1

df.loc[loss_mask, "real_loss"] = (
    df.loc[loss_mask, "ead"] - df.loc[loss_mask, "net_recovery"]
).clip(lower=0)

df["interest_collected"] = df["total_rec_int"]

# ── Rate metrics ─────────────────────────────────────────────────
df["yield_rate"] = df["interest_collected"] / df["funded_amnt"]
df["loss_rate"] = df["real_loss"] / df["funded_amnt"]
df["return_rate"] = df["yield_rate"] - df["loss_rate"]

# ── LGD ──────────────────────────────────────────────────────────
df["lgd_ratio"] = 0.0
valid_mask = (df["ead"] > 0) & (df["default_flag"] == 1)

df.loc[valid_mask, "lgd_ratio"] = (
    df.loc[valid_mask, "real_loss"] / df.loc[valid_mask, "ead"]
).clip(0, 1)

# ── Sanity checks ────────────────────────────────────────────────
print("\nSanity checks:")
print("Negative losses:", (df["real_loss"] < 0).sum())
print("Return consistency error:",
      ((df["yield_rate"] - df["loss_rate"]) - df["return_rate"]).abs().max())

# ── Portfolio overview ───────────────────────────────────────────
total_funded = df["funded_amnt"].sum()
total_loss = df["real_loss"].sum()
total_interest = df["interest_collected"].sum()
portfolio_return = total_interest - total_loss

print("\n" + "=" * 60)
print("PORTFOLIO OVERVIEW")
print("=" * 60)

print(f"Total funded      : ${total_funded:,.0f}")
print(f"Total loss        : ${total_loss:,.0f}")
print(f"Total interest    : ${total_interest:,.0f}")
print(f"Net return        : ${portfolio_return:,.0f}")

# ── Weighted rates ───────────────────────────────────────────────
weighted_yield = total_interest / total_funded
weighted_loss = total_loss / total_funded
weighted_return = weighted_yield - weighted_loss

print("\nWeighted rates:")
print(f"Yield   : {weighted_yield:.2%}")
print(f"Loss    : {weighted_loss:.2%}")
print(f"Return  : {weighted_return:.2%}")

# ── Performance by grade ─────────────────────────────────────────
print("\nPerformance by grade:")

grade_report = df.groupby("grade").agg(
    loans=("funded_amnt", "count"),
    default_rate=("default_flag", "mean"),
    avg_yield=("yield_rate", "mean"),
    avg_loss=("loss_rate", "mean"),
    avg_return=("return_rate", "mean"),
)

grade_report[["default_rate", "avg_yield", "avg_loss", "avg_return"]] *= 100
grade_report = grade_report.round(2)

print(grade_report)

# ── Performance by purpose ───────────────────────────────────────
print("\nPerformance by purpose:")

purpose_report = df.groupby("purpose").agg(
    loans=("funded_amnt", "count"),
    capital=("funded_amnt", "sum"),
    default_rate=("default_flag", "mean"),
    avg_return=("return_rate", "mean"),
)

total_capital = purpose_report["capital"].sum()
purpose_report["capital_share_%"] = (
    purpose_report["capital"] / total_capital * 100
)

purpose_report[["default_rate", "avg_return"]] *= 100
purpose_report = purpose_report.round(2).sort_values("capital", ascending=False)

print(purpose_report)

# ── Vintage analysis ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("VINTAGE ANALYSIS")
print("=" * 60)

df["issue_d"] = pd.to_datetime(df["issue_d"], errors="coerce")
df["issue_year"] = df["issue_d"].dt.year

vintage = df.groupby("issue_year").agg(
    loans=("funded_amnt", "count"),
    total_funded=("funded_amnt", "sum"),
    avg_return=("return_rate", "mean"),
    avg_yield=("yield_rate", "mean"),
    avg_loss=("loss_rate", "mean"),
    default_rate=("default_flag", "mean"),
).reset_index()

vintage[["avg_return", "avg_yield", "avg_loss", "default_rate"]] *= 100
vintage = vintage.round(2)

print(vintage)

# ── Vintage × grade ──────────────────────────────────────────────
print("\nVintage × Grade (Return Rate):")

vintage_grade = df.groupby(["issue_year", "grade"]).agg(
    avg_return=("return_rate", "mean"),
    default_rate=("default_flag", "mean"),
).reset_index()

vintage_grade[["avg_return", "default_rate"]] *= 100

pivot_return = vintage_grade.pivot(
    index="issue_year", columns="grade", values="avg_return"
).round(2)

print(pivot_return)

# ── Export outputs ───────────────────────────────────────────────
df.to_csv("data/processed/loans_metrics.csv", index=False)
vintage.to_csv("data/processed/vintage_analysis.csv", index=False)
pivot_return.to_csv("data/processed/vintage_grade_return.csv")

print("\nOutputs saved:")
print("  data/processed/loans_metrics.csv")
print("  data/processed/vintage_analysis.csv")
print("  data/processed/vintage_grade_return.csv")
print("=" * 60)