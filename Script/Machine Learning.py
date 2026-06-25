import sqlite3
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    confusion_matrix, classification_report,
    ConfusionMatrixDisplay, accuracy_score,
)
from matplotlib.patches import Patch

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "RAW data", "Green_Consumption_Behavior_2024.db")
OUT_DIR  = os.path.join(BASE_DIR, "Output")
os.makedirs(OUT_DIR, exist_ok=True)

# ── 1. Load Data from SQLite ──────────────────────────────────────────────────
con = sqlite3.connect(DB_PATH)
df  = pd.read_sql_query("SELECT * FROM green_consumption_behavior", con)
con.close()

print(f"Loaded {len(df):,} rows from database.")

# ── 2. Feature Engineering ────────────────────────────────────────────────────
# Ordinal-encode Income_Level (Low=0, Medium=1, High=2 — natural order)
income_encoder = OrdinalEncoder(categories=[["Low", "Medium", "High"]])
df["Income_Level_Enc"] = income_encoder.fit_transform(df[["Income_Level"]])

FEATURES = [
    "Age",
    "Income_Level_Enc",
    "Emotional_Guilt_Score",
    "Social_Influence_Score",
    "Green_Knowledge_Level",
    "Session_Duration_Minutes",
]
FEATURE_LABELS = [
    "Age",
    "Income Level",
    "Emotional Guilt",
    "Social Influence",
    "Green Knowledge",
    "Session Duration",
]
TARGET = "Green_Purchase_Made"

X = df[FEATURES]
y = df[TARGET]

print(f"\nTarget distribution:")
print(y.value_counts().rename({0: "No Purchase (0)", 1: "Purchase (1)"}).to_string())

# ── 3. Train / Test Split (75 / 25, stratified) ────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# ── 4. Train Models ────────────────────────────────────────────────────────────
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest":       RandomForestClassifier(n_estimators=200, random_state=42),
}

results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    results[name] = {
        "model":  model,
        "y_pred": y_pred,
        "acc":    accuracy_score(y_test, y_pred),
        "cm":     confusion_matrix(y_test, y_pred),
        "report": classification_report(y_test, y_pred, target_names=["No Buy", "Buy"]),
    }
    print(f"\n{'-'*55}")
    print(f"  {name}  -  Accuracy: {results[name]['acc']:.2%}")
    print(f"{'-'*55}")
    print(results[name]["report"])

# ── 5. Confusion Matrices ─────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Confusion Matrices — Green Purchase Prediction", fontsize=14, fontweight="bold")

for ax, (name, res) in zip(axes, results.items()):
    disp = ConfusionMatrixDisplay(res["cm"], display_labels=["No Buy (0)", "Buy (1)"])
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(f"{name}\nAccuracy: {res['acc']:.2%}", fontsize=11)

plt.tight_layout()
cm_path = os.path.join(OUT_DIR, "confusion_matrices.png")
plt.savefig(cm_path, dpi=150, bbox_inches="tight")
plt.show()
print(f"\nSaved: {cm_path}")

# ── 6. Feature Importance ─────────────────────────────────────────────────────
lr_model = results["Logistic Regression"]["model"]
rf_model = results["Random Forest"]["model"]

# LR: absolute coefficients (normalised); RF: mean decrease impurity (normalised)
lr_raw  = np.abs(lr_model.coef_[0])
rf_raw  = rf_model.feature_importances_
lr_norm = lr_raw / lr_raw.sum()
rf_norm = rf_raw / rf_raw.sum()

importance_df = pd.DataFrame({
    "Feature":             FEATURE_LABELS,
    "Logistic Regression": lr_norm,
    "Random Forest":       rf_norm,
}).sort_values("Random Forest", ascending=True)

DEMO_FEATURES = {"Age", "Income Level"}
COLOUR_MAP    = lambda features: [
    "#E07B54" if f in DEMO_FEATURES else "#5B8DB8" for f in features
]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Feature Importance — What Drives Green Purchases?", fontsize=14, fontweight="bold")

for ax, col in zip(axes, ["Logistic Regression", "Random Forest"]):
    bars = ax.barh(
        importance_df["Feature"],
        importance_df[col],
        color=COLOUR_MAP(importance_df["Feature"]),
        edgecolor="white",
        height=0.6,
    )
    ax.set_xlabel("Normalised Importance", fontsize=10)
    ax.set_title(col, fontsize=12, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    for bar, val in zip(bars, importance_df[col]):
        ax.text(
            bar.get_width() + 0.003,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1%}",
            va="center", fontsize=9,
        )

legend_handles = [
    Patch(facecolor="#E07B54", label="Demographic  (Age · Income Level)"),
    Patch(facecolor="#5B8DB8", label="Psychographic  (Guilt · Social · Knowledge · Session)"),
]
fig.legend(handles=legend_handles, loc="lower center", ncol=2,
           fontsize=10, frameon=False, bbox_to_anchor=(0.5, -0.05))

plt.tight_layout()
fi_path = os.path.join(OUT_DIR, "feature_importance.png")
plt.savefig(fi_path, dpi=150, bbox_inches="tight")
plt.show()
print(f"Saved: {fi_path}")

# ── 7. Verdict: Demographic vs. Psychographic ─────────────────────────────────
print("\n" + "=" * 60)
print("  VERDICT: Demographic vs. Psychographic Drivers")
print("=" * 60)

for model_name, norm_imp in [("Logistic Regression", lr_norm), ("Random Forest", rf_norm)]:
    demo_share   = sum(v for f, v in zip(FEATURE_LABELS, norm_imp) if f in DEMO_FEATURES)
    psycho_share = 1.0 - demo_share
    top_feature  = FEATURE_LABELS[int(np.argmax(norm_imp))]
    winner       = "DEMOGRAPHIC" if demo_share > psycho_share else "PSYCHOGRAPHIC"

    print(f"\n  [{model_name}]")
    print(f"    Demographic share   : {demo_share:.1%}  (Age + Income Level)")
    print(f"    Psychographic share : {psycho_share:.1%}  (Guilt + Social + Knowledge + Session)")
    print(f"    Top single feature  : {top_feature}")
    print(f"    >> Model leans on   : {winner} signals")

print("""
  Marketing Implication
  ---------------------
  Retargeting campaigns should be built around psychographic
  segments. Customers with high Emotional Guilt scores, strong
  Social Influence exposure, and deeper Green Knowledge convert
  at higher rates regardless of age or income bracket.

  Actionable retargeting levers:
    * High Guilt Score  -> eco-impact messaging ("you can make a difference")
    * High Social Inf.  -> social proof & community-driven ads
    * High Knowledge    -> detailed product sustainability credentials
    * Long Session Time -> remarketing with the exact viewed products
""")
print("=" * 60)
