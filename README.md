# Decoding the psychology of the green consumer

## Background and problem

Consumers say they want to buy sustainably. They often don't. The marketing team for a sustainable consumer goods brand had behavioral and psychological data from website visitors and didn't know what to do with it. Three questions drove this analysis:

1. Which psychological triggers — guilt, knowledge, or social influence — actually push someone to buy?
2. Which referral channels bring in visitors who are most likely to convert?
3. Can a model predict, from a single session, whether someone will buy?

---

## Dataset

- **Source:** `Green_Consumption_Behavior_2024.csv`
- **Size:** 1,200 users, 19 columns
- **Target:** `Green_Purchase_Made` (1 = purchased, 0 = did not)
- **Overall conversion rate:** 56.42% (677 out of 1,200 visitors)

Key features used in the analysis:

| Feature | Type | Description |
|---|---|---|
| `Emotional_Guilt_Score` | Psychographic | How guilty the user feels about environmental harm (1–10) |
| `Social_Influence_Score` | Psychographic | Social pressure toward eco-friendly behavior (1–10) |
| `Green_Knowledge_Level` | Psychographic | Self-reported knowledge of green products (1–10) |
| `Session_Duration_Minutes` | Behavioral | Time spent on site during the session |
| `Referral_Source` | Traffic | Social Media / Ads / Email / Organic Search |
| `Income_Level` | Demographic | Low / Medium / High |
| `Age` | Demographic | User's age |

---

## Methodology

### 1. Data pipeline

The raw CSV was cleaned and pushed into SQLite. That involved removing duplicate `User_ID` entries, dropping rows missing critical fields, normalizing casing on categorical columns, and filling remaining numeric nulls with column medians.

### 2. Exploratory data analysis

SQL queries ran directly against the SQLite database. The analysis covered three areas: psychological triggers, referral traffic, and demographics.

### 3. Machine learning

Two classifiers were trained to predict purchase intent from session and psychographic features:

- Logistic Regression (interpretable baseline)
- Random Forest (200 estimators)

Train/test split: 75/25, stratified by target class. Features: Age, Income Level, Emotional Guilt Score, Social Influence Score, Green Knowledge Level, Session Duration.

### 4. Output

Confusion matrices and feature importance charts were saved to `/Output/`. A ten-sheet Excel workbook was also built to feed a three-tab Power BI dashboard (Traffic Funnel, Buyer Psychology, Predictive Targeting).

---

## Findings

### Q1 — Which psychological trigger drives purchases?

Emotional guilt, and it's not close.

| Factor | Avg score (buyers) | Avg score (non-buyers) | Delta |
|---|---|---|---|
| Emotional Guilt Score | 6.58 | 4.19 | +2.39 |
| Green Knowledge Level | 6.00 | 4.72 | +1.28 |
| Social Influence Score | 6.00 | 4.97 | +1.03 |

Buyers score 2.4 points higher on guilt than non-buyers. That gap is nearly double the knowledge gap and more than double the social influence gap. Both models agree: emotional guilt ranked as the top single feature, accounting for 52.3% of logistic regression's weight and 26.6% of random forest's.

Messaging that ties a purchase to personal environmental impact — "your choice makes a real difference" — will likely outperform purely informational or social proof approaches. The data points that way pretty clearly.

---

### Q2 — Which referral channel converts best?

| Referral source | Visitors | Conversions | Conversion rate |
|---|---|---|---|
| Social Media | 308 | 191 | 62.01% |
| Ads | 321 | 189 | 58.88% |
| Email | 303 | 158 | 52.15% |
| Organic Search | 268 | 139 | 51.87% |

Social Media wins on conversion rate at 62%. Ads drives more raw traffic (321 visitors) but converts 3 points lower. Email and Organic Search both sit just above 52%, roughly 10 points behind social.

The gap likely reflects visitor intent: someone clicking through from a social feed has probably already seen the product in a context that resonated with them. That pre-existing exposure is hard to replicate with a search ad or a newsletter blast. For email specifically, the Q1 results suggest guilt-focused personalization could close some of that gap.

---

### Q3 — Can we predict who will buy in a single session?

Both models beat a naive baseline, though neither is a precision instrument:

| Model | Accuracy | Buy precision | Buy recall |
|---|---|---|---|
| Logistic Regression | 67.00% | 69% | 75% |
| Random Forest | 65.67% | 69% | 72% |

They're better at catching actual buyers (recall 72–75%) than at avoiding false positives. That makes them more useful for broad remarketing than for tight precision targeting — you'd remarket to a wider audience and let the creative filter from there.

Here's what each model actually relies on:

| Feature | Random Forest | Logistic Regression |
|---|---|---|
| Emotional Guilt | 26.6% | 52.3% |
| Session Duration | 22.6% | 1.8% |
| Green Knowledge | 14.0% | 25.2% |
| Social Influence | 13.4% | 18.0% |
| Age | 18.2% | 0.4% |
| Income Level | 5.1% | 2.4% |

Psychographic features account for 76.6% of random forest's decisions and 97.2% of logistic regression's. Demographic signals barely move the needle, especially in the LR model — age and income together contribute less than 3%.

---

### Bonus finding — does income matter?

Barely, as it turns out:

| Income level | Conversion rate |
|---|---|
| Low | 57.69% |
| High | 56.47% |
| Medium | 55.63% |

All three income tiers sit within 2 percentage points of each other. But cut by knowledge level and the picture shifts:

- Low income + high knowledge (score >= 7): **69.50%** conversion
- Low income + low knowledge: 50.22%
- High income + high knowledge: **68.82%** conversion
- High income + low knowledge: 48.20%

Knowledge determines whether someone converts. Income doesn't. A low-income visitor who scores high on green knowledge converts at essentially the same rate as a high-income one. Any targeting strategy built around income brackets is likely filtering out real buyers.

---

## Marketing implications

| Signal | What to do |
|---|---|
| High Emotional Guilt Score | Lead with eco-impact messaging ("your choice makes a real difference") |
| High Social Influence Score | Use social proof, community metrics, and peer-driven creative |
| High Green Knowledge Level | Highlight sustainability credentials and certifications in detail |
| Long Session Duration | Remarket with the exact products the user viewed |
| Social Media referral | Invest here — these visitors convert at 62% |
| Low Income + High Knowledge | Don't filter on income; these users convert as well as high-income ones |

---

## Project structure

```
ROI and Green Marketing/
├── RAW data/
│   ├── Green_Consumption_Behavior_2024.csv   # Original dataset (1,200 rows)
│   └── Green_Consumption_Behavior_2024.db    # SQLite version post-cleaning
├── Script/
│   ├── Data Loading.py                       # CSV → SQLite ETL + cleaning
│   ├── Data Checking.sql                     # Schema validation & null checks
│   ├── Exploratory Data Analyst.py           # SQL-based EDA (psychology, traffic, demographics)
│   ├── Machine Learning.py                   # Model training, evaluation, visualizations
│   └── Build PowerBI Data.py                 # Generates Excel workbook for Power BI
└── Output/
    ├── confusion_matrices.png                # Side-by-side confusion matrix chart
    ├── feature_importance.png                # Feature importance comparison chart
    └── PowerBI_Data.xlsx                     # 10-sheet workbook for dashboard
```

## Tech stack

- Python 3 (pandas, scikit-learn, matplotlib)
- SQLite
- Power BI (three-tab dashboard: Traffic Funnel, Buyer Psychology, Predictive Targeting)
- Excel (intermediate data layer between Python and Power BI)
