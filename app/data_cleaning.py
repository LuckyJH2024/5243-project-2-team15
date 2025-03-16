from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_store import df_raw, df_cleaned

data_cleaning_ui = ui.nav_panel(
    "Data Cleaning",
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("column_select", "Select Column", choices=[]),
            ui.input_select(
                "cleaning_action", "Select Cleaning Action",
                choices=[
                    "Fill Missing Values", "Remove Outliers", "Convert to Numeric",
                    "Standardize Text", "One-Hot Encode"
                ]
            ),
            ui.output_ui("cleaning_suggestions"),
            ui.input_action_button("apply_cleaning", "Apply Cleaning")
        ),
        ui.layout_columns(
            ui.card(ui.panel_title("Cleaned Data Preview"), ui.output_table("cleaned_data_table")),
            ui.card(ui.panel_title("Column-Based Cleaning Suggestions"), ui.output_ui("column_suggestions"))
        )
    )
)

def data_cleaning_server(input, output, session):
    @reactive.effect
    def initialize_cleaned_data():
        raw_data = df_raw.get()
        if raw_data is not None and df_cleaned.get() is None:
            df_cleaned.set(raw_data.copy())

    @reactive.effect
    def update_column_choices():
        df = df_raw.get()
        if df is not None:
            print("df_raw successfully retrieved")
            columns = df.columns.tolist()
            ui.update_select(
                id="column_select",
                choices=columns,
                selected=columns[0] if columns else None
            )

    @output
    @render.ui
    def column_suggestions():
        df = df_raw.get()
        if df is None or input.column_select() is None:
            return ui.p("No column selected.")

        col = input.column_select()
        if col not in df.columns:
            return ui.p("Selected column not found in dataset.")
            
        dtype = df[col].dtype
        suggestions = []

        if dtype == "object":
            suggestions.append("This is a categorical column. Consider standardizing text or one-hot encoding.")
        elif dtype in ["int64", "float64"]:
            if df[col].isnull().sum() > 0:
                suggestions.append("This column has missing values. Consider filling with mean or median.")
            if df[col].nunique() < 10:
                suggestions.append("This column has few unique values. Consider treating it as categorical.")
            else:
                suggestions.append("This is a numerical column. Consider handling outliers and normalizing data.")

        return ui.card(*[ui.p(suggestion) for suggestion in suggestions])

    @output
    @render.table
    def cleaned_data_table():
        cleaned_data = df_cleaned.get()
        if cleaned_data is not None:
            return cleaned_data.head(10)
        return pd.DataFrame()

    @reactive.effect
    @reactive.event(input.apply_cleaning)
    def clean_data():
        raw_data = df_raw.get()
        if raw_data is None or input.column_select() is None:
            return
            
        col = input.column_select()
        if col not in raw_data.columns:
            return
            
        if df_cleaned.get() is None:
            df_cleaned.set(raw_data.copy())
            
        cleaned_data = df_cleaned.get().copy()
        action = input.cleaning_action()
        
        if action == "Fill Missing Values":
            if cleaned_data[col].dtype in ["int64", "float64"]:
                cleaned_data[col] = cleaned_data[col].fillna(cleaned_data[col].mean())
            else:
                cleaned_data[col] = cleaned_data[col].fillna(cleaned_data[col].mode()[0])
        elif action == "Remove Outliers":
            if cleaned_data[col].dtype in ["int64", "float64"]:
                q1 = cleaned_data[col].quantile(0.25)
                q3 = cleaned_data[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                cleaned_data = cleaned_data[(cleaned_data[col] >= lower_bound) & (cleaned_data[col] <= upper_bound)]
        elif action == "Convert to Numeric":
            try:
                cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
            except:
                pass
        elif action == "Standardize Text":
            if cleaned_data[col].dtype == "object":
                cleaned_data[col] = cleaned_data[col].str.lower().str.strip()
        elif action == "One-Hot Encode":
            if cleaned_data[col].dtype == "object":
                dummies = pd.get_dummies(cleaned_data[col], prefix=col)
                cleaned_data = pd.concat([cleaned_data.drop(col, axis=1), dummies], axis=1)
        
        df_cleaned.set(cleaned_data)

