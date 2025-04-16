from shiny import ui, reactive, render
from data_store import df_cleaned, error_store
import pandas as pd
import io
import json
import tempfile
import os

# Check if pyreadr library is installed for writing RDS files
try:
    import pyreadr
    HAS_PYREADR = True
except ImportError:
    HAS_PYREADR = False

# Data Download UI
data_download_layout = ui.card_header(ui.h3("Download Processed Data")),
    ui.layout_columns(
        ui.value_box(
            "Data Status",
            ui.output_text("data_status"),
            showcase=ui.output_ui("data_status_icon"),
            theme="bg-success"
        ),
        ui.value_box(
            "Data Size",
            ui.output_text("data_size"),
            showcase=ui.tags.i(class_="fa fa-database"),
            theme="bg-info"
        ),
        ui.value_box(
            "Column Count",
            ui.output_text("column_count"),
            showcase=ui.tags.i(class_="fa fa-table"),
            theme="bg-primary"
        ),
        col_widths=[4, 4, 4]
    ),
    ui.card_body(
        ui.h4("Select Download Format"),
        ui.layout_columns(
            ui.card(
                ui.card_header(ui.h5("CSV Format")),
                ui.card_body(
                    ui.p("Comma-separated values file, suitable for most data analysis tools and spreadsheet software."),
                    ui.input_checkbox("csv_include_index", "Include Row Index", False),
                    ui.download_button("download_csv", "Download CSV File", class_="btn-primary w-100")
                )
            ),
            ui.card(
                ui.card_header(ui.h5("Excel Format")),
                ui.card_body(
                    ui.p("Microsoft Excel file, suitable for spreadsheet software."),
                    ui.input_checkbox("excel_include_index", "Include Row Index", False),
                    ui.download_button("download_excel", "Download Excel File", class_="btn-primary w-100")
                )
            ),
            ui.card(
                ui.card_header(ui.h5("JSON Format")),
                ui.card_body(
                    ui.p("JavaScript Object Notation, suitable for web applications and APIs."),
                    ui.input_select(
                        "json_orient", 
                        "JSON Format Type", 
                        choices=["records", "columns", "index", "split", "table"],
                        selected="records"
                    ),
                    ui.download_button("download_json", "Download JSON File", class_="btn-primary w-100")
                )
            ),
            col_widths=[4, 4, 4]
        ),
        ui.layout_columns(
            ui.card(
                ui.card_header(ui.h5("RDS Format")),
                ui.card_body(
                    ui.p("R Data Storage format, suitable for R language analysis."),
                    ui.output_ui("rds_status"),
                    ui.download_button("download_rds", "Download RDS File", class_="btn-primary w-100")
                )
            ),
            ui.card(
                ui.card_header(ui.h5("TSV Format")),
                ui.card_body(
                    ui.p("Tab-separated values file, suitable for text processing and specific analysis tools."),
                    ui.input_checkbox("tsv_include_index", "Include Row Index", False),
                    ui.download_button("download_tsv", "Download TSV File", class_="btn-primary w-100")
                )
            ),
            ui.card(
                ui.card_header(ui.h5("Pickle Format")),
                ui.card_body(
                    ui.p("Python serialization format, suitable for Python data analysis."),
                    ui.input_select(
                        "pickle_protocol", 
                        "Pickle Protocol Version", 
                        choices=["4", "5"],
                        selected="4"
                    ),
                    ui.download_button("download_pickle", "Download Pickle File", class_="btn-primary w-100")
                )
            ),
            col_widths=[4, 4, 4]
        )
    ),
    ui.card_footer(
        ui.p("Note: The downloaded data is the final data after cleaning and processing. For original data, please return to the Data Loading page and re-upload.")
    )
)


def data_download_server(input, output, session):
    # Data status
    @output
    @render.text
    def data_status():
        data = df_cleaned.get()
        if data is None:
            return "No data loaded"
        elif data.empty:
            return "Data is empty"
        else:
            return "Data is ready"
    
    # Data status icon
    @output
    @render.ui
    def data_status_icon():
        data = df_cleaned.get()
        if data is None or data.empty:
            return ui.tags.i(class_="fa fa-times-circle", style="color: red;")
        else:
            return ui.tags.i(class_="fa fa-check-circle", style="color: green;")
    
    # Data size
    @output
    @render.text
    def data_size():
        data = df_cleaned.get()
        if data is None:
            return "0 rows"
        else:
            return f"{len(data):,} rows"
    
    # Column count
    @output
    @render.text
    def column_count():
        data = df_cleaned.get()
        if data is None:
            return "0 columns"
        else:
            return f"{len(data.columns):,} columns"
    
    # RDS status
    @output
    @render.ui
    def rds_status():
        if not HAS_PYREADR:
            return ui.div(
                ui.p("The pyreadr library is required to download RDS files.", style="color: orange;"),
                ui.p("Installation command: pip install pyreadr")
            )
        return ui.p("Can be downloaded as RDS format for use with R language.")
    
    # Download CSV file
    @render.download(filename=lambda: "cleaned_data.csv")
    async def download_csv():
        data = df_cleaned.get()
        if data is None:
            return "No data available"
        
        include_index = input.csv_include_index()
        csv_data = io.StringIO()
        data.to_csv(csv_data, index=include_index)
        
        return csv_data.getvalue()
    
    # Download Excel file
    @render.download(filename=lambda: "cleaned_data.xlsx")
    async def download_excel():
        data = df_cleaned.get()
        if data is None:
            return "No data available"
        
        include_index = input.excel_include_index()
        excel_data = io.BytesIO()
        data.to_excel(excel_data, index=include_index)
        excel_data.seek(0)
        
        return excel_data.getvalue()
    
    # Download JSON file
    @render.download(filename=lambda: "cleaned_data.json")
    async def download_json():
        data = df_cleaned.get()
        if data is None:
            return "No data available"
        
        orient = input.json_orient()
        json_data = data.to_json(orient=orient)
        
        return json_data
    
    # Download RDS file
    @render.download(filename=lambda: "cleaned_data.rds")
    async def download_rds():
        data = df_cleaned.get()
        if data is None:
            return "No data available"
        
        if not HAS_PYREADR:
            return "The pyreadr library is required to download RDS files."
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.rds', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Write to RDS file
        pyreadr.write_rds(tmp_path, data)
        
        # Read the file content
        with open(tmp_path, 'rb') as f:
            content = f.read()
        
        # Delete the temporary file
        os.unlink(tmp_path)
        
        return content
    
    # Download TSV file
    @render.download(filename=lambda: "cleaned_data.tsv")
    async def download_tsv():
        data = df_cleaned.get()
        if data is None:
            return "No data available"
        
        include_index = input.tsv_include_index()
        tsv_data = io.StringIO()
        data.to_csv(tsv_data, sep='\t', index=include_index)
        
        return tsv_data.getvalue()
    
    # Download Pickle file
    @render.download(filename=lambda: "cleaned_data.pkl")
    async def download_pickle():
        data = df_cleaned.get()
        if data is None:
            return "No data available"
        
        protocol = int(input.pickle_protocol())
        pickle_data = io.BytesIO()
        data.to_pickle(pickle_data, protocol=protocol)
        pickle_data.seek(0)
        
        return pickle_data.getvalue() 

data_download_ui = ui.nav_panel("Data Download", data_download_layout)

data_download_body = data_dowload_layout
