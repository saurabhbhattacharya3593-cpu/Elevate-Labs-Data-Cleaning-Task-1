"""
Elevate Labs — Data Analyst Internship
Task 1: Data Cleaning and Preprocessing
Dataset: Netflix Movies and TV Shows (Kaggle: shivamb/netflix-shows)

Run:
    pip install -r requirements.txt
    python data_cleaning.py

If netflix_titles.csv is not in this folder, the script downloads a public
mirror of the Kaggle dataset and saves the untouched source CSV first.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW_FILE = ROOT / "netflix_titles.csv"
CLEAN_FILE = ROOT / "netflix_cleaned.csv"
REPORT_FILE = ROOT / "cleaning_summary.txt"

DATA_URL = "https://raw.githubusercontent.com/japnitahuja/netflix-data-analysis/main/netflix_titles.csv"


def main():
    if not RAW_FILE.exists():
        print("Downloading raw dataset...")
        raw = pd.read_csv(DATA_URL)
        raw.to_csv(RAW_FILE, index=False)
    else:
        raw = pd.read_csv(RAW_FILE)

    raw_rows, raw_cols = raw.shape
    missing_before = raw.isna().sum()
    df = raw.copy()

    # Standardize column headers.
    df.columns = (
        df.columns.astype(str).str.strip().str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )

    # Trim strings; empty strings should be treated as missing.
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip().replace("", pd.NA)

    # Remove exact duplicate rows.
    duplicate_rows = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Parse date_added safely. Invalid dates become NaT, not invented dates.
    df["date_added"] = pd.to_datetime(
        df["date_added"], errors="coerce", format="mixed"
    )

    # Convert release_year to a nullable integer.
    df["release_year"] = pd.to_numeric(
        df["release_year"], errors="coerce"
    ).astype("Int64")

    # Normalize categorical text.
    df["type"] = df["type"].str.strip().str.title()
    df["rating"] = df["rating"].str.strip().str.upper()

    # Parse duration (e.g., "90 min", "2 Seasons") into numeric value and unit.
    parsed = df["duration"].str.extract(
        r"^\s*(\d+)\s*(min|season|seasons)\s*$", expand=True
    )
    df["duration_value"] = pd.to_numeric(
        parsed[0], errors="coerce"
    ).astype("Int64")
    df["duration_unit"] = (
        parsed[1].str.lower().replace({"seasons": "season"}).astype("string")
    )
    df["duration"] = df["duration"].str.replace(r"\s+", " ", regex=True)

    # Fill selected descriptive fields with an explicit, transparent label.
    # Dates and duration are left missing where unknown rather than guessed.
    for col in ["director", "cast", "country", "rating"]:
        df[col] = df[col].fillna("Unknown")

    # Validate and export.
    remaining_duplicates = int(df.duplicated().sum())
    missing_after = df.isna().sum()
    df.to_csv(CLEAN_FILE, index=False, date_format="%Y-%m-%d")

    report = [
        "ELEVATE LABS — TASK 1: DATA CLEANING SUMMARY",
        "Dataset: Netflix Movies and TV Shows",
        "Original Kaggle source: https://www.kaggle.com/datasets/shivamb/netflix-shows",
        "",
        f"Raw dimensions: {raw_rows} rows x {raw_cols} columns",
        f"Exact duplicate rows removed: {duplicate_rows}",
        f"Cleaned dimensions: {df.shape[0]} rows x {df.shape[1]} columns",
        f"Duplicate rows remaining: {remaining_duplicates}",
        "",
        "Missing values BEFORE cleaning:",
        missing_before.to_string(),
        "",
        "Missing values AFTER cleaning:",
        missing_after.to_string(),
        "",
        "Steps performed:",
        "1. Standardized headers to lowercase and underscores.",
        "2. Trimmed text whitespace and treated blank strings as missing.",
        "3. Removed exact duplicate rows.",
        "4. Converted date_added to datetime.",
        "5. Converted release_year to nullable integer.",
        "6. Standardized type and rating labels.",
        "7. Extracted duration_value and duration_unit from duration.",
        "8. Replaced missing director, cast, country, and rating with 'Unknown'.",
        "9. Preserved missing dates and durations rather than guessing values.",
        "10. Exported netflix_cleaned.csv.",
    ]
    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")

    print("Cleaning complete.")
    print(f"Raw shape: {raw.shape}")
    print(f"Duplicates removed: {duplicate_rows}")
    print(f"Cleaned shape: {df.shape}")
    print(f"Cleaned data: {CLEAN_FILE}")
    print(f"Summary report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
