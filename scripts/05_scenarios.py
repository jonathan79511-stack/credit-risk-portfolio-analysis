import pandas as pd
import numpy as np

print("Loading dataset...")
df = pd.read_csv("data/processed/loans_metrics.csv", low_memory=False)

df["issue_d"] = pd.to_datetime(df["issue_d"], errors="coerce")
df["issue_year"] = df["issue_d"].dt.year

print(f"Rows loaded: {len(df):,}")

# ── Base portfolio (post-2013) ───────────────────────────────────
post2013 = df[df["issue_year"] > 2013].copy()
print(f"Post-2013 portfolio: {len(post2013):,} loans | ${post2013['funded_amnt'].sum():,.0f}")

# ── Baseline performance ─────────────────────────────────────────
print("\n" + "=" * 60)
print("BASELINE — POST-2013 PERFORMANCE")
print("=" * 60)

base_funded = post2013["funded_amnt"].sum()
base_interest = post2013["interest_collected"].sum()
base_loss = post2013["real_loss"].sum()

base_return = base_interest - base_loss
base_return_rate = base_return / base_funded

print(f"Total funded   : ${base_funded:,.0f}")
print(f"Total interest : ${base_interest:,.0f}")
print(f"Total loss     : ${base_loss:,.0f}")
print(f"Net return     : ${base_return:,.0f}")
print(f"Return rate    : {base_return_rate:.2%}")

# ── Yield vs loss gap by grade ───────────────────────────────────
print("\n" + "=" * 60)
print("YIELD–LOSS GAP BY GRADE")
print("=" * 60)

gap = post2013.groupby("grade").agg(
    avg_yield=("yield_rate", "mean"),
    avg_loss=("loss_rate", "mean"),
    avg_dti=("dti", "mean"),
    avg_fico=("fico_range_low", "mean"),
    total_cap=("funded_amnt", "sum"),
).reset_index()

gap["gap_bps"] = ((gap["avg_loss"] - gap["avg_yield"]) * 10000).round(0)
gap["adj_bps_50pct"] = (gap["gap_bps"] * 0.5).round(0)

gap["avg_yield_pct"] = (gap["avg_yield"] * 100).round(2)
gap["avg_loss_pct"] = (gap["avg_loss"] * 100).round(2)

print(gap[["grade", "avg_yield_pct", "avg_loss_pct", "gap_bps", "adj_bps_50pct"]])

# ── Scenario 1 ───────────────────────────────────────────────────
print("\nScenario 1 — Repricing Grade D")

bps_d = float(gap.loc[gap["grade"] == "D", "adj_bps_50pct"].values[0])
grade_d = post2013[post2013["grade"] == "D"]
cap_d = grade_d["funded_amnt"].sum()

impact_s1 = cap_d * (bps_d / 10000)

print(f"Impact: ${impact_s1:,.0f}")

# ── Scenario 2 ───────────────────────────────────────────────────
print("\nScenario 2 — Reduce F–G + partial repricing")

fg = post2013[post2013["grade"].isin(["F", "G"])]

fg_funded = fg["funded_amnt"].sum()
fg_net = fg["interest_collected"].sum() - fg["real_loss"].sum()

repricing_bps = 200
retained_capital = fg_funded * 0.5

avoided_loss = fg_net * 0.5
additional_yield = retained_capital * (repricing_bps / 10000)

impact_s2 = -avoided_loss + additional_yield

print(f"Impact: ${impact_s2:,.0f}")

# ── Scenario 3 ───────────────────────────────────────────────────
print("\nScenario 3 — Term optimization (60m → 36m)")

post2014 = df[df["issue_year"] > 2014].copy()

mask_60 = (post2014["term"] == 60) & (post2014["grade"].isin(["D", "E", "F", "G"]))
mask_36 = (post2014["term"] == 36) & (post2014["grade"].isin(["D", "E", "F", "G"]))

loans_60 = post2014[mask_60]
loans_36 = post2014[mask_36]

cap_60 = loans_60["funded_amnt"].sum()

ret_60 = (loans_60["interest_collected"].sum() - loans_60["real_loss"].sum()) / cap_60
ret_36 = (loans_36["interest_collected"].sum() - loans_36["real_loss"].sum()) / loans_36["funded_amnt"].sum()

impact_s3 = cap_60 * 0.75 * (ret_36 - ret_60)

print(f"Impact: ${impact_s3:,.0f}")

# ── Scenario 4 ───────────────────────────────────────────────────
print("\nScenario 4 — Underwriting overlay")

eg = post2013[post2013["grade"].isin(["E", "F", "G"])].copy()

dti_p75 = eg.groupby("grade")["dti"].quantile(0.75)
fico_cutoff = 680

eg.loc[:, "dti_p75"] = eg["grade"].map(dti_p75)

high_risk = eg[
    (eg["dti"] > eg["dti_p75"]) &
    (eg["fico_range_low"] < fico_cutoff)
]

hr_net = high_risk["interest_collected"].sum() - high_risk["real_loss"].sum()

impact_s4 = -hr_net

print(f"Impact: ${impact_s4:,.0f}")

# ── Summary ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SCENARIO SUMMARY")
print("=" * 60)

print(f"1. Repricing D       : ${impact_s1:,.0f}")
print(f"2. Reduce F–G        : ${impact_s2:,.0f}")
print(f"3. Term optimization : ${impact_s3:,.0f}")
print(f"4. Underwriting      : ${impact_s4:,.0f}")

# ── Export ───────────────────────────────────────────────────────
results = pd.DataFrame({
    "scenario": [
        "Repricing Grade D",
        "Reduce F–G",
        "Term optimization",
        "Underwriting overlay"
    ],
    "impact_usd": [
        round(impact_s1),
        round(impact_s2),
        round(impact_s3),
        round(impact_s4)
    ]
})

results.to_csv("data/processed/scenario_analysis.csv", index=False)

print("\nOutput saved: data/processed/scenario_analysis.csv")