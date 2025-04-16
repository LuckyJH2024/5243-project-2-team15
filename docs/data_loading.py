from shiny import ui, reactive, render
from data_store import df_raw, df_cleaned, error_store
import time
import pandas as pd
import numpy as np
import json
import os

# Check if pyreadr library is installed for reading RDS files
try:
    import pyreadr
    HAS_PYREADR = True
except ImportError:
    HAS_PYREADR = False

# Table styles
table_styles = ui.tags.style("""
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    tr:hover {
        background-color: #f1f1f1;
    }
    .card {
        margin-bottom: 20px;
    }
""")

# Data Loading UI
data_loading_layout = ui.layout_sidebar(
        ui.sidebar(
            ui.h3("Upload Data"),
            ui.input_file("file",
                "Upload Data File",
                multiple=False,
                accept=[".csv", ".json", ".xlsx", ".xls", ".rds"],
                width="100%",
                button_label="Browse Files",
                placeholder="No file selected",
            ),
            ui.input_action_button("process", "Process Data", class_="btn-primary"),
            ui.br(),
            ui.br(),
            ui.output_ui("progress"),
            ui.output_text("file_name"),
            ui.output_text("error_message", inline=True),
            ui.hr(),
            ui.h4("Sample Datasets"),
            ui.p("If you don't have your own data, you can use the following sample datasets:"),
            ui.input_action_button("load_iris", "Iris Dataset", class_="btn-secondary"),
            ui.input_action_button("load_boston", "Boston Housing Dataset", class_="btn-secondary"),
            ui.input_action_button("load_wine", "Wine Dataset", class_="btn-secondary"),
            width=300
        ),
        ui.card(
            ui.h3("Data Preview"),
            ui.output_text("error_message_main"),
            ui.card(ui.panel_title("Data Preview"), ui.output_table("data_preview")),
            ui.card(ui.panel_title("Data Types"), ui.output_table("data_types")),
        )
    )
)

def data_loading_server(input, output, session):
    @output
    @render.text
    def file_name():
        file_info = input.file()
        if file_info:
            return f"Selected file: {file_info[0]['name']}"
        return "No file selected"
    
    @output
    @render.text
    def error_message():
        return error_store.get()
    
    @output
    @render.text
    def error_message_main():
        return error_store.get()

    @reactive.Effect
    @reactive.event(input.process)
    def process_uploaded_file():
        file_info = input.file()
        if file_info and len(file_info) > 0:
            try:
                file_ext = file_info[0]["name"].split(".")[-1].lower()
                file_path = file_info[0]["datapath"]
                
                with ui.Progress(min=0, max=100) as p:
                    p.set(10, "Processing file...")
                    
                if file_ext == "csv":
                    df = pd.read_csv(file_path)
                
                elif file_ext == "json":
                    with open(file_path, "r", encoding="utf-8") as f:
                        json_data = json.load(f)

                    if isinstance(json_data, dict):
                        normalized_data = []
                        for key, value in json_data.items():
                            if isinstance(value, dict):
                                flattened_dict = {f"{key}.{subkey}": subvalue for subkey, subvalue in value.items()}
                                normalized_data.append(flattened_dict)
                            else:
                                normalized_data.append({key: value})
                        df = pd.DataFrame(normalized_data)

                    elif isinstance(json_data, list):
                        df = pd.DataFrame(json_data)
                    else:
                        raise ValueError("Unsupported JSON format")
                
                elif file_ext in ["xlsx", "xls"]:
                    # Read Excel file
                    df = pd.read_excel(file_path)
                
                elif file_ext == "rds":
                    # Read RDS file
                    if not HAS_PYREADR:
                        error_store.set("Missing pyreadr library, cannot read RDS files. Please install: pip install pyreadr")
                        df_raw.set(None)
                        return
                    
                    # Use pyreadr to read RDS file
                    result = pyreadr.read_r(file_path)
                    # RDS files usually contain one dataframe, we get the first one
                    if result:
                        df = next(iter(result.values()))
                    else:
                        raise ValueError("RDS file is empty or format is incorrect")

                else:
                    error_store.set(f"Unsupported file type: {file_ext}. Supported formats: CSV, JSON, Excel, RDS")
                    df_raw.set(None)
                    return

                # Check if data is empty
                if df.empty:
                    error_store.set("Uploaded data is empty")
                    df_raw.set(None)
                    return
                
                # Set original data and cleaned data
                df_raw.set(df)
                df_cleaned.set(df.copy())
                error_store.set("")
                
                p.set(100, "Read completed!")

            except Exception as e:
                error_store.set(f"Error loading file: {str(e)}")
                df_raw.set(None)
                df_cleaned.set(None)
    
    @reactive.Effect
    @reactive.event(input.load_iris)
    def load_iris_dataset():
        try:
            from sklearn.datasets import load_iris
            data = load_iris()
            df = pd.DataFrame(data.data, columns=data.feature_names)
            df['target'] = data.target
            
            df_raw.set(df)
            df_cleaned.set(df.copy())
            error_store.set("")
        except Exception as e:
            error_store.set(f"Error loading Iris dataset: {str(e)}")
    
    @reactive.Effect
    @reactive.event(input.load_boston)
    def load_boston_dataset():
        try:
            # Since the Boston housing dataset in sklearn has been deprecated, we manually create a simplified version
            np.random.seed(42)
            n_samples = 100
            df = pd.DataFrame({
                'CRIM': np.random.exponential(0.5, n_samples),
                'ZN': np.random.choice([0, 20, 40, 60, 80, 100], n_samples),
                'INDUS': np.random.uniform(0, 20, n_samples),
                'CHAS': np.random.choice([0, 1], n_samples),
                'NOX': np.random.uniform(0.4, 0.8, n_samples),
                'RM': np.random.normal(6, 1, n_samples),
                'AGE': np.random.uniform(20, 90, n_samples),
                'DIS': np.random.exponential(3, n_samples),
                'RAD': np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 24], n_samples),
                'TAX': np.random.uniform(200, 700, n_samples),
                'PTRATIO': np.random.uniform(12, 22, n_samples),
                'B': np.random.uniform(0, 400, n_samples),
                'LSTAT': np.random.exponential(7, n_samples),
                'MEDV': np.random.normal(22, 9, n_samples)
            })
            
            df_raw.set(df)
            df_cleaned.set(df.copy())
            error_store.set("")
        except Exception as e:
            error_store.set(f"Error loading Boston housing dataset: {str(e)}")
    
    @reactive.Effect
    @reactive.event(input.load_wine)
    def load_wine_dataset():
        try:
            from sklearn.datasets import load_wine
            data = load_wine()
            df = pd.DataFrame(data.data, columns=data.feature_names)
            df['target'] = data.target
            
            df_raw.set(df)
            df_cleaned.set(df.copy())
            error_store.set("")
        except Exception as e:
            error_store.set(f"Error loading wine dataset: {str(e)}")
    
    @output
    @render.table
    def data_preview():
        df = df_raw.get()
        if df is not None:
            return df.head()
        return pd.DataFrame()

    @output
    @render.table
    def summary_stats():
        df = df_raw.get()
        if df is not None:
            # Only calculate statistical summary for numeric columns
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                return numeric_df.describe().reset_index()
            else:
                return pd.DataFrame({'message': ['No numeric columns to calculate statistical summary']})
        return pd.DataFrame()

    @output
    @render.table
    def data_types():
        df = df_raw.get()
        if df is not None:
            return pd.DataFrame(df.dtypes, columns=["Data Type"]).reset_index().rename(columns={"index": "Column Name"})
        return pd.DataFrame() 

data_loading_ui = ui.nav_panel(
    "Data Loading",
    table_styles, data_loading_layout)
data_loading_body = data_loading_layout
