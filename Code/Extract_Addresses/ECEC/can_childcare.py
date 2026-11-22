import os
from pathlib import Path
import pandas as pd 
import numpy as np

wd = Path(__file__).resolve().parents[3]
os.chdir(wd)

data = pd.read_csv("Addresses/ECEC/raw_data/ODEF_v3.0.1/odef_v3_0_1.csv")

isced = ["ISCED010", "ISCED020"]
data[isced] = data[isced].apply(pd.to_numeric, errors="coerce")
data = data[(data["ISCED010"] == 1) | (data["ISCED020"] == 1)].assign(type=lambda d: np.select([(d["ISCED010"] == 1) & (d["ISCED020"] == 1), d["ISCED010"] == 1, d["ISCED020"] == 1], ["ISCED0", "ISCED 01", "ISCED 02"], default=""))

data = data[["facility_name", "full_address", "postalCode", "addressLocality",
             "province_code", "type", "geometry"]]

# Removing addresses that are P.O. boxes ----------------------------------------------------------------
mask = data["full_address"].astype(str).str.strip().str.startswith(("P.O.", "P. O.", "PO", "Box", "BOX"))
print(f"Rows with full_address starting with 'P.O.', 'P. O.', 'PO', 'Box', 'BOX': {mask.sum()}")
print(data.loc[mask, "province_code"].value_counts())
data = data[~mask]

# Rows with full_address starting with 'P.O.', 'P. O.', 'PO', 'Box', 'BOX': 1089
# province_code
# SK    362
# AB    352
# MB    191
# NL    123
# BC     35
# NT     22
# YT      4

# Removing rows with no full address and no geometry ----------------------------
no_address = data["full_address"].isna() | data["full_address"].astype(str).str.strip().isin(["..", ""])
no_geometry = data["geometry"].isna() | data["geometry"].astype(str).str.strip().eq("")
bad_rows = no_address & no_geometry

print(f"Rows with full_address '..', '' or NA and geometry '' or NA: {bad_rows.sum()}")
print(data.loc[bad_rows, "province_code"].value_counts())

# Rows with full_address '..', '' or NA and geometry '' or NA: 0

data = data[~bad_rows]

# -------------------------------------------------------------------------------

data.to_csv("Addresses/ECEC/can_childcare.csv", index=False)