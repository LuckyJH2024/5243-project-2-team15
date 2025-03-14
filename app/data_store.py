from shiny import reactive

df_raw = reactive.Value(None)  # Holds the DataFrame

df_cleaned = reactive.Value(None) #for cleaned df

error_store = reactive.Value("")  # Stores error messages
