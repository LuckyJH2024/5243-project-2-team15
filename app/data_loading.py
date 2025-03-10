from shiny import ui, reactive, render
import pandas as pd
import json

# UI for data loading
data_loading_ui = ui.nav_panel(
	"Data Loading",
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
		ui.output_text("file_name"),
		ui.output_text("error_message", inline=True)
	),
	ui.card(
		ui.output_text("error_message_main"),
		ui.output_table("data_preview")
	),	
	width = 350
	) 
)

def data_loading_server(input, output, session):
	df_store = reactive.value(None)
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
				df_store.set(df)
				error_store.set("")

			except Exception as e:
				error_store.set(f"Error loading file: {str(e)}")
				df_store.set(None)	
	@output
	@render.table
	def data_preview():
		df = df_store.get()
		if df is not None: 
			return df.head()
		return pd.DataFrame()
