from shiny import ui, reactive, render
import pandas as pd

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
		ui.output_text("file_name")
	    ),
		width = 350
	), 
	ui.output_table("data_preview")
)

def data_loading_server(input, output, session):
	df_store = reactive.value(None)
	
	@output
	@render.text
	def file_name():
		file_info = input.file()
		if file_info: 
			return f"Selected file: {file_info[0]["name"]}"
		return "No file selected"

	@reactive.Effect
	@reactive.event(input.process)
	def _():
		file_info = input.file()
		if file_info and len(file_info) > 0:
			try: 
				file_ext = file_info[0]["name"].split(".")[-1].lower()
				if file_ext == "csv":
					df = pd.read_csv(file_info[0]["datapath"])  
				elif file_ext == "json":
					df = pd.read_json(file_info["datapath"])
				else:
					print("Unsupported file type")
					return
				df_store.set(df)
			except Exception as e:
				print(f"Error loading file:{e}")  
	
	@output
	@render.table
	def data_preview():
		df = df_store.get()
		if df is not None: 
			return df.head()
		return pd.DataFrame()
