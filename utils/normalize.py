import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# --- Helper: Normalize column mapping ---
def normalize_column_mapping(df):
    df.columns = [col.lower().replace(" ", "").replace("_", "") for col in df.columns]
    col_map = {}
    for col in df.columns:
        if any(k in col for k in ["custname", "customername", "customer", "custno", "custnumber"]):
            if "name" in col:
                col_map["customername"] = col
            elif "no" in col or "number" in col:
                col_map["customerno"] = col
        elif col in ["component", "item", "part"]:
            col_map["component"] = col
        elif col in ["laborprice", "labourprice"]:
            col_map["laborprice"] = col
        elif col in ["certprice", "certificateprice"]:
            col_map["certprice"] = col
        elif col in ["type", "producttype"]:
            col_map["type"] = col
        elif col in ["quantity", "qty"]:
            col_map["quantity"] = col
        elif col in ["price", "unitprice", "cost"]:
            col_map["price"] = col
    return col_map
