import pandas as pd

# Shared inventory dataframe
inventory_df = None


def load_data_new():
    """
    Loads the deduplicated vehicle inventory into memory.
    Called lazily by tools.
    """
    global inventory_df

    if inventory_df is not None:
        return True

    try:
        inventory_df = pd.read_json(
            "../Api/data/CAR_UNIQUE_DATA.json"
        )
        return True
    except Exception as e:
        print("❌ Error loading CAR_UNIQUE_DATA.json:", e)
        return False
