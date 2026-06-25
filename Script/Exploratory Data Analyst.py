import sqlite3
import pandas as pd

DB_PATH = r"c:\Users\user\OneDrive\Project\ROI and Green Marketing\RAW data\Green_Consumption_Behavior_2024.db"

con = sqlite3.connect(DB_PATH)


def run(title: str, sql: str) -> pd.DataFrame:
    result = pd.read_sql_query(sql, con)
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)
    print(result.to_string(index=False))
    return result


# ── Psychology Question ────────────────────────────────────────
# Compare avg Emotional_Guilt_Score and avg Green_Knowledge_Level
# for buyers (Green_Purchase_Made = 1) vs. non-buyers (0).

run(
    "Psychology: Avg Emotional_Guilt_Score by Purchase Decision",
    """
    SELECT
        Green_Purchase_Made                                  AS Purchased,
        ROUND(AVG(Emotional_Guilt_Score), 4)                AS Avg_Guilt_Score,
        COUNT(*)                                             AS Users
    FROM green_consumption_behavior
    GROUP BY Green_Purchase_Made
    ORDER BY Green_Purchase_Made DESC
    """,
)

run(
    "Psychology: Avg Green_Knowledge_Level by Purchase Decision",
    """
    SELECT
        Green_Purchase_Made                                  AS Purchased,
        ROUND(AVG(Green_Knowledge_Level), 4)                AS Avg_Knowledge_Level,
        COUNT(*)                                             AS Users
    FROM green_consumption_behavior
    GROUP BY Green_Purchase_Made
    ORDER BY Green_Purchase_Made DESC
    """,
)

run(
    "Psychology: Delta Impact - Guilt Score vs Knowledge Level (normalised)",
    """
    WITH stats AS (
        SELECT
            ROUND(AVG(CASE WHEN Green_Purchase_Made = 1 THEN Emotional_Guilt_Score  END), 4) AS guilt_buy,
            ROUND(AVG(CASE WHEN Green_Purchase_Made = 0 THEN Emotional_Guilt_Score  END), 4) AS guilt_nobuy,
            ROUND(AVG(CASE WHEN Green_Purchase_Made = 1 THEN Green_Knowledge_Level  END), 4) AS know_buy,
            ROUND(AVG(CASE WHEN Green_Purchase_Made = 0 THEN Green_Knowledge_Level  END), 4) AS know_nobuy,
            ROUND(MAX(Emotional_Guilt_Score) - MIN(Emotional_Guilt_Score), 4)                AS guilt_range,
            ROUND(MAX(Green_Knowledge_Level) - MIN(Green_Knowledge_Level), 4)                AS know_range
        FROM green_consumption_behavior
    ),
    combined AS (
        SELECT
            'Emotional_Guilt_Score'                                                      AS Factor,
            guilt_buy                                                                    AS Avg_Buyers,
            guilt_nobuy                                                                  AS Avg_NonBuyers,
            ROUND(guilt_buy  - guilt_nobuy,  4)                                         AS Raw_Delta,
            ROUND((guilt_buy - guilt_nobuy) / guilt_range, 4)                           AS Normalised_Delta
        FROM stats
        UNION ALL
        SELECT
            'Green_Knowledge_Level',
            know_buy,
            know_nobuy,
            ROUND(know_buy  - know_nobuy,  4),
            ROUND((know_buy - know_nobuy) / know_range, 4)
        FROM stats
    )
    SELECT * FROM combined ORDER BY ABS(Normalised_Delta) DESC
    """,
)

# ── Traffic Question ───────────────────────────────────────────
# Conversion rate per Referral_Source.

run(
    "Traffic: Conversion Rate by Referral_Source",
    """
    SELECT
        Referral_Source,
        COUNT(*)                                                         AS Total_Users,
        SUM(Green_Purchase_Made)                                         AS Conversions,
        ROUND(100.0 * SUM(Green_Purchase_Made) / COUNT(*), 2)           AS Conversion_Rate_Pct
    FROM green_consumption_behavior
    GROUP BY Referral_Source
    ORDER BY Conversion_Rate_Pct DESC
    """,
)

# ── Demographic Question ───────────────────────────────────────
# Does Income_Level or Green_Knowledge_Level drive green purchases?

run(
    "Demographic: Conversion Rate by Income_Level",
    """
    SELECT
        Income_Level,
        COUNT(*)                                                         AS Total_Users,
        SUM(Green_Purchase_Made)                                         AS Conversions,
        ROUND(100.0 * SUM(Green_Purchase_Made) / COUNT(*), 2)           AS Conversion_Rate_Pct,
        ROUND(AVG(Green_Knowledge_Level), 4)                            AS Avg_Knowledge_Level
    FROM green_consumption_behavior
    GROUP BY Income_Level
    ORDER BY Conversion_Rate_Pct DESC
    """,
)

run(
    "Demographic: Conversion Rate by Income x Knowledge (High vs Low Knowledge)",
    """
    SELECT
        Income_Level,
        CASE WHEN Green_Knowledge_Level >= 7 THEN 'High (>=7)'
             ELSE 'Low (<7)'
        END                                                              AS Knowledge_Tier,
        COUNT(*)                                                         AS Total_Users,
        SUM(Green_Purchase_Made)                                         AS Conversions,
        ROUND(100.0 * SUM(Green_Purchase_Made) / COUNT(*), 2)           AS Conversion_Rate_Pct
    FROM green_consumption_behavior
    GROUP BY Income_Level,
             CASE WHEN Green_Knowledge_Level >= 7 THEN 'High (>=7)' ELSE 'Low (<7)' END
    ORDER BY Income_Level, Knowledge_Tier DESC
    """,
)

run(
    "Demographic: Does High Knowledge Override Low Income?",
    """
    WITH segmented AS (
        SELECT
            Income_Level,
            CASE WHEN Green_Knowledge_Level >= 7 THEN 'High Knowledge (>=7)'
                 ELSE 'Low Knowledge (<7)'
            END                                                          AS Knowledge_Tier,
            Green_Purchase_Made
        FROM green_consumption_behavior
        WHERE Income_Level IN ('Low', 'High')
    )
    SELECT
        Income_Level,
        Knowledge_Tier,
        COUNT(*)                                                         AS Total_Users,
        SUM(Green_Purchase_Made)                                         AS Conversions,
        ROUND(100.0 * SUM(Green_Purchase_Made) / COUNT(*), 2)           AS Conversion_Rate_Pct
    FROM segmented
    GROUP BY Income_Level, Knowledge_Tier
    ORDER BY Income_Level DESC, Knowledge_Tier DESC
    """,
)

con.close()
