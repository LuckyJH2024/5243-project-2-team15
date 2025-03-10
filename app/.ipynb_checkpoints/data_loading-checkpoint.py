from shiny import ui, reactive

# UI for data loading
data_loading_ui = ui.nav_panel(
    "Data Loading",
    ui.sidebar(
        ui.input_file("file", "Upload CSV or JSON File"),
        ui.input_action_button("process", "Process Data")
    )
)

def data_loading_server(input, output, session):
    @reactive.Effect
    @reactive.event(input.process)
    def _():
        file_info = input.file()
        if file_info is not None:
		file_ext = file_info["name"].split(".")[-1].lower()
            with file_info["datapath"].open("rb") as f:
                file_content = f.read()
            if file_ext == "csv":
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_ext == "json":
                df = pd.read_json(io.BytesIO(file_content))
        else:
            print("Unsupported file type")
        print(df.head())
