print("Testing imports...")

try:
    print("Importing data_store...")
    from data_store import df_raw, df_cleaned, error_store
    print("data_store imported successfully")
except Exception as e:
    print(f"Error importing data_store: {str(e)}")

try:
    print("Importing data_loading...")
    from data_loading import data_loading_ui, data_loading_server
    print("data_loading imported successfully")
except Exception as e:
    print(f"Error importing data_loading: {str(e)}")

try:
    print("Importing data_cleaning...")
    from data_cleaning import data_cleaning_ui, data_cleaning_server
    print("data_cleaning imported successfully")
except Exception as e:
    print(f"Error importing data_cleaning: {str(e)}")

try:
    print("Importing feature_engineering...")
    from feature_engineering import feature_engineering_ui, feature_engineering_server
    print("feature_engineering imported successfully")
except Exception as e:
    print(f"Error importing feature_engineering: {str(e)}")

try:
    print("Importing eda...")
    from eda import eda_ui, eda_server
    print("eda imported successfully")
except Exception as e:
    print(f"Error importing eda: {str(e)}")

print("Import tests completed") 