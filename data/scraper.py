#!/usr/bin/env python3
"""
scrape_and_export.py

Fetch FSBO/sold listings from HomeHarvest with full detail,
inspect the DataFrame, parse nested lists, and export to CSV.
"""

import os
import ast
from datetime import datetime
import pandas as pd
from homeharvest import scrape_property
from dotenv import load_dotenv
from pathlib import Path

# -----------------------------------------------------------------------------
# 1. Load environment variables (if you keep any in a .env file)
# -----------------------------------------------------------------------------
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# -----------------------------------------------------------------------------
# 2. Parameters for your run
# -----------------------------------------------------------------------------
LOCATION     = os.getenv("HH_LOCATION", "San Diego, CA")
LISTING_TYPE = os.getenv("HH_LISTING_TYPE", "sold")   # sold, for_sale, for_rent, pending
PAST_DAYS    = int(os.getenv("HH_PAST_DAYS", 30))
RETURN_TYPE  = os.getenv("HH_RETURN_TYPE", "pandas") # pandas, raw, pydantic

# Build output filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_CSV    = f"HomeHarvest_{LOCATION.replace(',','').replace(' ','_')}_{timestamp}.csv"

# -----------------------------------------------------------------------------
# 3. Scrape with extra detail enabled
# -----------------------------------------------------------------------------
print(f"Scraping properties in '{LOCATION}' ({LISTING_TYPE}, last {PAST_DAYS} days)...")
properties = scrape_property(
    location=LOCATION,
    listing_type=LISTING_TYPE,
    past_days=PAST_DAYS,
    extra_property_data=True,  # fetch full detail (photos, tax history, etc)
    return_type=RETURN_TYPE     # DataFrame / raw dicts / Pydantic models
)

# -----------------------------------------------------------------------------
# 4. Inspect what you got
# -----------------------------------------------------------------------------
if RETURN_TYPE == "pandas":
    print("DataFrame loaded. Columns:")
    print(properties.columns.tolist())
    print("\nAll entries (transposed):")
    transposed_df = properties.T
    pd.set_option('display.max_rows', None)  # Show all rows
    pd.set_option('display.max_columns', None)  # Show all columns
    print(transposed_df)
    # Reset display options to default
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
else:
    # if raw/pydantic, show first item structure
    first = properties.iloc[0]
    print("First item structure:")
    if RETURN_TYPE == "raw":
        import json
        print(json.dumps(first, indent=2))
    else:  # pydantic
        print(first.json(indent=2))

# -----------------------------------------------------------------------------
# 5. Parse stringified lists back into real lists (only for pandas + CSV)
# -----------------------------------------------------------------------------
if RETURN_TYPE == "pandas":
    # Columns known to hold Python literal lists/dicts in string form
    list_columns = ["alt_photos", "nearby_schools", "agent_phones", "alt_photos"]
    for col in list_columns:
        if col in properties.columns:
            print(f"Parsing column '{col}' back into Python lists...")
            properties[col] = properties[col].apply(
                lambda v: ast.literal_eval(v) if isinstance(v, str) and v.startswith("[") else v
            )

    # -----------------------------------------------------------------------------
    # 6. Export full DataFrame to CSV
    # -----------------------------------------------------------------------------
    print(f"Exporting to CSV: {OUT_CSV}")
    properties.to_csv(OUT_CSV, index=False)
    print("Done!")
else:
    # If raw or pydantic, convert to pandas before CSV, or serialize JSON
    if RETURN_TYPE in ("raw", "pydantic"):
        print("ℹConverting list of dicts/models to DataFrame before CSV...")
        if RETURN_TYPE == "pydantic":
            records = [item.dict() for item in properties]
        else:
            records = properties
        df = pd.DataFrame.from_records(records)
        print("Columns:", df.columns.tolist())
        print(f"Exporting DataFrame to CSV: {OUT_CSV}")
        df.to_csv(OUT_CSV, index=False)
        print("Done!")

# End of script
