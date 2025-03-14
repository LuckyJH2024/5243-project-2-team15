from shiny import App, ui
from data_loading import data_loading_ui, data_loading_server
from data_cleaning import data_cleaning_ui, data_cleaning_server
from feature_engineering import feature_engineering_ui, feature_engineering_server
from eda import eda_ui, eda_server
from data_store import df_raw, df_cleaned, error_store

app_ui = ui.page_fluid(
    ui.panel_title("Data Analysis App"),
    ui.navset_tab(
        data_loading_ui,
        data_cleaning_ui,
        feature_engineering_ui,
        eda_ui
    )
)

def server(input, output, session):
    data_loading_server(input, output, session)
    data_cleaning_server(input, output, session)
    feature_engineering_server(input, output, session)
    eda_server(input, output, session)

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
