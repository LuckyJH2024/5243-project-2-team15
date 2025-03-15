from shiny import ui
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np

# UI for exploratory data analysis (EDA)
eda_ui = ui.nav_panel(
    "Exploratory Data Analysis",
    ui.output_plot("edaPlot")
)

def eda_server(input, output, session):
    # Logic for exploratory data analysis
    pass 

# UI Layout
def eda_ui():
    return ui.page_fluid(
        ui.panel_title("Exploratory Data Analysis (EDA)"),
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.input_select("filter_col", "Select column to filter", []),
                ui.input_checkbox_group("selected_values", "Select values to include", []),
                ui.input_select("x_col", "Select X-axis feature", []),
                ui.input_select("y_col", "Select Y-axis feature", []),
                ui.input_select("color_col", "Select color feature", [None]),
                ui.input_select("size_col", "Select size feature", [None]),
                ui.input_select("trendline_option", "Select trendline type", [None, "ols", "lowess"]),
                ui.input_select("hist_col", "Select a feature for histogram", []),
                ui.input_slider("bins", "Select number of bins", 5, 50, 20),
                ui.input_select("box_col", "Select a feature for box plot", []),
            ),
            ui.panel_main(
                ui.output_table("summary"),
                ui.output_plot("scatter_plot"),
                ui.output_plot("heatmap"),
                ui.output_plot("histogram"),
                ui.output_plot("box_plot"),
                ui.output_text("stats")
            )
        )
    )

# Server Logic
def eda_server(input, output, session):
    df_cleaned = pd.read_csv("your_dataset.csv")  # Load dataset
    
    @render.ui
    def filter_col():
        return ui.update_select("filter_col", choices=df_cleaned.columns.tolist())

    @render.ui
    def selected_values():
        return ui.update_checkbox_group("selected_values", choices=df_cleaned[input.filter_col()].unique().tolist())
    
    @render.table
    def summary():
        return df_cleaned.describe()

    @render.plot
    def scatter_plot():
        fig = px.scatter(df_cleaned, x=input.x_col(), y=input.y_col(), color=input.color_col(), size=input.size_col(), trendline=input.trendline_option())
        return fig

    @render.plot
    def heatmap():
        corr_matrix = df_cleaned.corr()
        return ff.create_annotated_heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.index, annotation_text=np.round(corr_matrix.values, 2), colorscale="Viridis")

    @render.plot
    def histogram():
        return px.histogram(df_cleaned, x=input.hist_col(), nbins=input.bins(), color=input.color_col())

    @render.plot
    def box_plot():
        return px.box(df_cleaned, y=input.box_col(), points="all")
    
    @render.text
    def stats():
        return f"Mean of {input.x_col()}: {df_cleaned[input.x_col()].mean()}\nMedian: {df_cleaned[input.x_col()].median()}\nStd Dev: {df_cleaned[input.x_col()].std()}"

