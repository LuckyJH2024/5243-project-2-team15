import random
from shiny import reactive
from shiny import App, ui, session
from data_loading import data_loading_ui, data_loading_server
from data_cleaning import data_cleaning_ui, data_cleaning_server
from feature_engineering import feature_engineering_ui, feature_engineering_server
from eda import eda_ui, eda_server
from data_download import data_download_ui, data_download_server
from user_guide import user_guide_ui, user_guide_server
from data_store import df_raw, df_cleaned, df_engineered, error_store
from data_store import user_ab_variant

print("Initializing application...")

# Application title and description
app_title = "Data Analysis and Feature Engineering Platform"
app_description = ""  # Removed the introduction text

print("Creating UI components...")

# Application UI
app_ui = ui.page_fluid(
    ui.tags.style("""
        .app-title {
            font-size: 28px;
            font-weight: bold;
            color: #000000;
            margin-bottom: 10px;
        }
        
        /* Main navigation bar styles */
        .nav-tabs {
            background-color: #000000;
        }
        
        .nav-tabs > li > a {
            color: #FFFFFF;
        }
        
        .nav-tabs > li > a:hover {
            background-color: #333333;
            color: #FFFFFF;
        }
        
        /* Active tab in main navigation */
        .nav-tabs > li.active > a, 
        .nav-tabs > li.active > a:focus, 
        .nav-tabs > li.active > a:hover {
            background-color: #444444;
            color: #FFFFFF;
            font-weight: bold;
        }
        
        /* Ensure sub-navigation bar remains unchanged */
        .tab-content .nav-tabs {
            background-color: transparent;
        }
        
        .tab-content .nav-tabs > li > a {
            color: #007bff;
        }
        
        .tab-content .nav-tabs > li > a:hover {
            background-color: #f8f9fa;
            color: #0056b3;
        }
        
        .tab-content .nav-tabs > li.active > a,
        .tab-content .nav-tabs > li.active > a:focus,
        .tab-content .nav-tabs > li.active > a:hover {
            background-color: #FFFFFF;
            color: #495057;
            font-weight: normal;
        }
    """),
    ui.div(
        ui.div(
            ui.h1("Data Analysis and Feature Engineering Platform", class_="app-title"),
            class_="col-12"
        ),
        class_="row"
    ),
    
    # Navigation bar
    ui.navset_tab(
        user_guide_ui,
        data_loading_ui,
        data_cleaning_ui,
        eda_ui,
        feature_engineering_ui,
        data_download_ui
    )
)

print("Defining server functions...")

# Server function
def server(input, output, session):
    print("Server function called...")
    
    user_variant = reactive.Value(random.choice(["A","B"]))
    
    def assign_ab_variant():
        user_ab_variant.set(user_variant.get())
    
    # Initialize server functions for each module
    user_guide_server(input, output, session)
    data_loading_server(input, output, session)
    data_cleaning_server(input, output, session)
    eda_server(input, output, session)
    feature_engineering_server(input, output, session)
    data_download_server(input, output, session)
    print("All module server functions initialized...")

# Create application
print("Creating application instance...")
app = App(app_ui, server)

# Run application
if __name__ == "__main__":
    print("Starting Data Analysis and Feature Engineering Platform...")
    try:
        print("Application will be available at: http://127.0.0.1:8001")
        print("Please access the application using the above URL in your browser")
        app.run(host="127.0.0.1", port=8001)
    except Exception as e:
        print(f"Application failed to start: {str(e)}")
        # If port is already in use, suggest using a different port
        if "address already in use" in str(e).lower() or "10048" in str(e):
            print("Port 8001 is already in use. Try using a different port:")
            print("Example: app.run(host='127.0.0.1', port=8002)")
            print("Or stop other running Python processes and try again.") 
