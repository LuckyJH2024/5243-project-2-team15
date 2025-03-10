from shiny import ui, reactive, render
import time
import pandas as pd
import json

# Sidebar styling
floating_sidebar_style = ui.tags.style("""
    .sidebar-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 350px;  
        height: 100vh;  
        background: white;  
        z-index: 1000;
        overflow-y: auto;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        padding: 15px;
    }
    .main-content {
        margin-left: 370px;
        padding: 15px;
    }
""")

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
	ui.tag.div(
		ui.layout_sidebar(
			ui.sidebar(
			ui.input_file("file",
				"Upload CSV or JSON File",
				multiple = False,
				accept = [".csv",".json"],
				width = "100%", 
				button_label = "Browse files", 
				placeholder = "No file selected"),
			ui.input_action_button("process", "Process Data"),
			ui.output_ui("progress"),
			ui.output_ui("transpose_button"),
			ui.output_ui("confirm_transpose_button"),
			ui.output_text("file_name"),
			ui.output_text("error_message", inline=True))
		),
		class_="sidebar-container"),
	ui.card(ui.output_text("error_message_main"),
	ui.card(ui.panel_title("Dataframe preview"), ui.output_table("data_preview")),
	ui.card(ui.panel_title("Summary Statistics"),
		ui.p("this is for preliminary consideration only"), 
		ui.output_table("summary_stats")),
	ui.card(ui.panel_title("Data Types of Each Column"),
		ui.output_table("data_types")),
	ui.output_ui("comparison_card")	
	)
)

def data_loading_server(input, output, session):
	df_store = reactive.value(None)
	error_store = reactive.value("")
	transposed_store = reactive.value(None)
	show_transpose = reactive.value(False)
	show_comparison = reactive.value(False)
	show_confirm_button = reactive.value(False)	
	
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

					df_store.set(df)
					transposed_store.set(None)
					show_transpose.set(True)
					show_comparison.set(False)
					show_confirm_button.set(False)
					error_store.set("")
					
					p.set(100, "Reading Complete!")

			except Exception as e:
				error_store.set(f"Error loading file: {str(e)}")
				df_store.set(None)	
	@output
	@render.ui
	def transpose_button():
		if show_transpose.get():
			return ui.input_action_button("transpose", "Transpose Data")
		return ""

	@reactive.Effect
	@reactive.event(input.transpose)
	def transpose_data():
		df = df_store.get()
		if df is not None:
			with ui.Progress(min=0, max=100) as p:
				p.set(10, "Transposing data...")
				time.sleep(1)
				transposed_store.set(df.T)
				show_comparison.set(True)
				show_confirm_button.set(True)
				p.set(100, "Transposing Complete!")

	@output
	@render.ui
	def confirm_transpose_button():
		if show_confirm_button.get():
			return ui.input_action_button("confirm_transpose", "Confirm Transposed Data")
		return ""

	@reactive.Effect
	@reactive.event(input.confirm_transpose)
	def confirm_transposed_data():
		df_transposed = transposed_store.get()
		if df_transposed is not None:
			df_store.set(df_transposed)
			show_comparison.set(False)
			show_confirm_button.set(False)

	@output
	@render.ui
	def comparison_card():
		if show_comparison.get():
			return ui.card(
				ui.panel_title("Preview of the Transposed Dataframe"),
				ui.p("If the transposed dataframe is what you want, pleaase remember to press the confirm button so we move forwards with your transposed data."),
				ui.card(ui.panel_title("Original Data"), ui.output_table("original_data_preview")),
				ui.card(ui.panel_title("Transposed Data"), ui.output_table("transposed_data")),
			)
		return ""	


	@output
	@render.table
	def data_preview():
		df = df_store.get()
		if df is not None: 
			return df.head()
		return pd.DataFrame()

	@output
	@render.table
	def summary_stats():
		df = df_store.get()
		if df is not None:
			return df.describe().reset_index()
		return pd.DataFrame()

	@output
	@render.table
	def data_types():
		df = df_store.get()
		if df is not None:
			return pd.DataFrame(df.dtypes, columns = ["Data Type"]).reset_index().rename(columns = {"index":"Column"})
		return pd.DataFrame()
	@output
	@render.table
	def original_data_preview():
		df = df_store.get()
		if df is not None:
			return df.head()
		return pd.DataFrame()

	@output
	@render.table
	def transposed_data():
		df_transposed = transposed_store.get()
		if df_transposed is not None:
			return df_transposed
		return pd.DataFrame()
