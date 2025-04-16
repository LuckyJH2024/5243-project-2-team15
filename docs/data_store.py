from shiny import reactive

# A/B testing variant 
user_ab_variant = reactive.Value(None)

# Raw data
df_raw = reactive.Value(None)

# Cleaned data
df_cleaned = reactive.Value(None)

# Data after feature engineering
df_engineered = reactive.Value(None)

# Error messages
error_store = reactive.Value("")

# Currently selected model
selected_model = reactive.Value(None)

# Model evaluation results
model_results = reactive.Value(None) 
