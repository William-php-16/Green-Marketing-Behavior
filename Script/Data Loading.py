import pandas as pd
import sqlite3

csv_path = r'C:\Users\user\OneDrive\Project\ROI and Green Marketing\RAW data\Green_Consumption_Behavior_2024.csv'
db_path  = r'C:\Users\user\OneDrive\Project\ROI and Green Marketing\RAW data\Green_Consumption_Behavior_2024.db'

# ── 1. LOAD ────────────────────────────────────────────────────────────────────
print("Reading CSV file...")
df = pd.read_csv(csv_path)
print(f"  Loaded {len(df):,} rows × {len(df.columns)} columns")

# ── 2. CLEAN ───────────────────────────────────────────────────────────────────
print("\nCleaning data...")

# Remove duplicate User_IDs, keep first occurrence
before = len(df)
df.drop_duplicates(subset='User_ID', keep='first', inplace=True)
print(f"  Duplicates removed: {before - len(df)}")

# Drop rows missing critical fields
critical_cols = ['User_ID', 'Age', 'Gender', 'Income_Level', 'Green_Purchase_Made']
before = len(df)
df.dropna(subset=critical_cols, inplace=True)
print(f"  Rows dropped (missing critical fields): {before - len(df)}")

# Strip whitespace and normalize casing on categorical columns
str_cols = ['Gender', 'Income_Level', 'Device_Type', 'Referral_Source', 'Product_Category']
for col in str_cols:
    df[col] = df[col].str.strip().str.title()

# Fill remaining numeric nulls with the column median
numeric_cols = df.select_dtypes(include='number').columns.tolist()
for col in numeric_cols:
    nulls = df[col].isnull().sum()
    if nulls:
        df[col].fillna(df[col].median(), inplace=True)
        print(f"  Filled {nulls} nulls in '{col}' with median")

print(f"  Final shape: {len(df):,} rows × {len(df.columns)} columns")

# ── 3. PUSH TO SQLite ──────────────────────────────────────────────────────────
print("\nPushing data to the database...")
conn = sqlite3.connect(db_path)
df.to_sql('green_consumption_behavior', conn, if_exists='replace', index=False)
print("  Data pushed successfully.")

# ── 4. VERIFY SQLite ACCESS ────────────────────────────────────────────────────
print("\nVerifying SQLite access...")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print(f"  Tables in database: {tables}")

cursor.execute("SELECT COUNT(*) FROM green_consumption_behavior;")
print(f"  Row count in table: {cursor.fetchone()[0]:,}")

cursor.execute("PRAGMA table_info(green_consumption_behavior);")
print("  Columns:")
for col in cursor.fetchall():
    print(f"    [{col[0]}] {col[1]} ({col[2]})")

conn.close()
print("\nDone.")
