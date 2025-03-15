from shiny import ui, reactive, render
from data_store import df_raw, error_store
import time
import pandas as pd
import json

# Table styling
table_styles = ui.tags.style("""
	table {
		border-collapse: collapse;
		width: 100%;
	}
	th, td {
		border: 1px solid black;
		padding: 8px;
		text-align: center;
	}
	th {
		background-color: #f2f2f2;
		font-weight: bold;
	}
"""
)

# UI for data loading
data_loading_ui = ui.nav_panel(
	"Data Loading",
	table_styles, 
	ui.layout_sidebar(
	    ui.sidebar(
		ui.input_file("file",
			"Upload CSV or JSON File",
			multiple = False,
			accept = [".csv",".json"],
			width = "100%", 
			button_label = "Browse files", 
			placeholder = "No file selected",
		),
		ui.input_action_button("process", "Process Data"),
		ui.output_ui("progress"),
		ui.output_text("file_name"),
		ui.output_text("error_message", inline=True)
	),
	ui.card(ui.output_text("error_message_main"),
	ui.card(ui.panel_title("Dataframe preview"), ui.output_table("data_preview")),
	ui.card(ui.panel_title("Summary Statistics"),ui.p("this is for preliminary consideration only"), ui.output_table("summary_stats")),
	ui.card(ui.panel_title("Data Types of Each Column"),ui.output_table("data_types")),	
	width = 350
	) 
)
)

def data_loading_server(input, output, session):
	df_raw = reactive.value(None)
	error_store = reactive.value("")
	
	@output
	@render.text
	def file_name():
		file_info = input.file()
		if file_info: 
			return f"Selected file: {file_info[0]["name"]}"
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
	def _():
		file_info = input.file()
		if file_info and len(file_info) > 0:
			try: 
				file_ext = file_info[0]["name"].split(".")[-1].lower()
				file_path = file_info[0]["datapath"]		
				
				with ui.Progress(min=0, max=100) as p:
					p.set(10, "Processing file...")
					start_time = time.time()
	
					if file_ext == "csv":
						df = pd.read_csv(file_path)
	  
					elif file_ext == "json":
						with open(file_path, "r", encoding = "utf-8") as f:
							json_data = json.load(f)

						if isinstance(json_data, dict):
							normalized_data = []
							for key, value in json_data.items():
								if isinstance(value, dict):
									flattened_dict = {f"{key}.{subkey}":subvalue for subkey, subvalue in value.items()}
									normalized_data.append(flattened_dict)
								else:
									normalized_data.append({key:value})
							df = pd.DataFrame(normalized_data)

						elif isinstance(json_data, list):
							df = pd.DataFrame(json_data)
						else: 
							raise ValueError("Unsupported JSON format")

					else:
						error_store.set("Unsupported file type")
						df_store.set(None)
						return

					df_raw.set(df)
					print("df_raw sucessfully set")
					error_store.set("")
					
					p.set(100, "Reading Complete!")

			except Exception as e:
				error_store.set(f"Error loading file: {str(e)}")
				df_raw.set(None)	
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
			return df.describe().reset_index()
		return pd.DataFrame()

	@output
	@render.table
	def data_types():
		df = df_raw.get()
		if df is not None:
			return pd.DataFrame(df.dtypes, columns = ["Data Type"]).reset_index().rename(columns = {"index":"Column"})
		return pd.DataFrame()
