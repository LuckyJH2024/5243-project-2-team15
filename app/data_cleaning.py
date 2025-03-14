from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_store import df_raw, df_cleaned 

data_cleaning_ui = ui.nav_panel(
	"Data Cleaning",
	ui.layout_sidebar(ui.sidebar(
		ui.input_select("column_select", "Select Column", choices=[]),
		ui.input_select("cleaning_action", "Select Cleaning Action", choices=["Fill Missing Values", "Remove Outliers", "Convert to Numeric", "Standardize Text", "One-Hot Encode"]),
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
    def update_column_choices():
        df = df_raw.get()
        print("df_raw successfuly retreived")
	if df is not None:
	    session.send_input("column_select", {"choices": df.columns.tolist()})

    @output
    @render.ui
    def column_suggestions():
	df = df_raw.get() 
	if df is None or input.column_select() is None:
	    return ui.p("No column selected.")
        
        col = input.column_select()
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

    @reactive.effect
    def clean_data():
        df = df_raw.get() 
        if df is None or input.column_select() is None:
            return

        col = input.column_select()
        action = input.cleaning_action()

        if action == "Fill Missing Values":
            df[col] = df[col].fillna(df[col].median() if df[col].dtype in ["int64", "float64"] else "missing")
        elif action == "Remove Outliers":
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            df = df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]
        elif action == "Convert to Numeric":
            df[col] = pd.to_numeric(df[col], errors='coerce')
        elif action == "Standardize Text":
            df[col] = df[col].str.lower() if df[col].dtype == 'object' else df[col]
        elif action == "One-Hot Encode":
            df = pd.get_dummies(df, columns=[col], drop_first=True)

        df_cleaned.set(df)

    @output
    @render.table
    def cleaned_data_table():
        df = df_cleaned.get() 
        if df is None:
            return pd.DataFrame()
        return df.head()

