import random
from shiny import reactive
from shiny import App, render,  ui, session
from data_loading import data_loading_ui, data_loading_server, data_loading_body
from data_cleaning import data_cleaning_ui, data_cleaning_server, data_cleaning_body
from feature_engineering import feature_engineering_ui, feature_engineering_server, feature_engineering_body
from eda import eda_ui, eda_server, eda_body
from data_download import data_download_ui, data_download_server, data_download_body
from user_guide import user_guide_ui, user_guide_server, user_guide_body
from data_store import df_raw, df_cleaned, df_engineered, error_store
from data_store import user_ab_variant

print("Initializing application...")

# Application title and description
app_title = "Data Analysis and Feature Engineering Platform"
app_description = ""  # Removed the introduction text

print("Creating UI components...")

# Google Analytics 4 snippet
analytics_script = ui.head_content(
    ui.tags.script(async_="true", src="https://www.googletagmanager.com/gtag/js?id=G-LMHG83C2FS"),
    ui.tags.script("""
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-LMHG83C2FS');
    """),
    ui.tags.script("""
        document.addEventListener("DOMContentLoaded", function() {
            document.body.addEventListener("click", function(e) {
                let target = e.target;
                if (target.tagName === "BUTTON" || target.type === "button" || target.classList.contains("btn")) {
                    const label = target.innerText || target.id || "unnamed_button";
                    gtag('event', 'button_click', {
                        'event_category': 'Button',
                        'event_label': label,
                        'value': 1
                    });
                }
            });
        });
    """)
)

# Application UI
app_ui = ui.page_fluid(
    analytics_script, 
    ui.h1(app_title, class_ = "app-title"),
    ui.output_ui("main_ui"))

print("Defining server functions...")

# Server function
def server(input, output, session):
    print("Server function called...")
    
    user_variant = reactive.Value(random.choice(["A","B"]))

    @reactive.Effect
    def assign_ab_variant():
        user_ab_variant.set(user_variant.get())

    current_step = reactive.Value(1)

    # Module sync function
    def sync_module_ui():
        try:
            # Get current step or tab
            if user_variant.get() == "A":
                # Version A uses tab navigation
                if hasattr(input, "navbar"):
                    current_tab = input.navbar()
                    print(f"Version A: Tab changed to {current_tab}")
                    
                    # Synchronize UI based on current tab
                    if current_tab == "Data Cleaning":
                        print("Syncing Data Cleaning UI")
                        from data_cleaning import sync_ui_with_data
                        sync_ui_with_data(input, output, session)
                    elif current_tab == "Exploratory Analysis":
                        print("Syncing EDA UI")
                        from eda import update_column_choices
                        update_column_choices(input, output, session)
                    elif current_tab == "Feature Engineering":
                        print("Syncing Feature Engineering UI")
                        from feature_engineering import initialize_engineered_data, update_feature_choices
                        initialize_engineered_data()
                        update_feature_choices(input, output, session)
            else:
                # Version B uses step navigation
                step = current_step.get()
                print(f"Version B: Step changed to {step}")
                
                # Synchronize UI based on current step
                if step == 3:  # Data Cleaning
                    print("Syncing Data Cleaning UI")
                    from data_cleaning import sync_ui_with_data
                    sync_ui_with_data(input, output, session)
                elif step == 4:  # EDA
                    print("Syncing EDA UI")
                    from eda import update_column_choices
                    update_column_choices(input, output, session)
                elif step == 5:  # Feature Engineering
                    print("Syncing Feature Engineering UI")
                    from feature_engineering import initialize_engineered_data, update_feature_choices
                    initialize_engineered_data()
                    update_feature_choices(input, output, session)
        except Exception as e:
            print(f"Error syncing module UI: {str(e)}")

    # Version A: Listen for tab changes
    @reactive.Effect
    @reactive.event(input.navbar)
    def on_tab_change():
        if user_variant.get() == "A":
            sync_module_ui()

    # Version B: Listen for step changes
    @reactive.Effect
    @reactive.event(current_step)
    def on_step_change():
        if user_variant.get() == "B":
            sync_module_ui()
            
    # Step navigation logic
    @reactive.Effect
    @reactive.event(input.next1)
    def _(): current_step.set(2)
    
    @reactive.Effect
    @reactive.event(input.back1)
    def _(): current_step.set(1)
    
    @reactive.Effect
    @reactive.event(input.next2)
    def _(): current_step.set(3)
    
    @reactive.Effect
    @reactive.event(input.back2)
    def _(): current_step.set(2)
    
    @reactive.Effect
    @reactive.event(input.next3)
    def _(): current_step.set(4)
    
    @reactive.Effect
    @reactive.event(input.back3)
    def _(): current_step.set(3)
    
    @reactive.Effect
    @reactive.event(input.next4)
    def _(): current_step.set(5)
    
    @reactive.Effect
    @reactive.event(input.back4)
    def _(): current_step.set(4)
    
    @reactive.Effect
    @reactive.event(input.next5)
    def _(): current_step.set(6)
    
    @reactive.Effect
    @reactive.event(input.back5)
    def _(): current_step.set(5)
    
    # Initialize server functions for each module
    user_guide_server(input, output, session)
    data_loading_server(input, output, session)
    data_cleaning_server(input, output, session)
    eda_server(input, output, session)
    feature_engineering_server(input, output, session)
    data_download_server(input, output, session)
    print("All module server functions initialized...")
    
    @output
    @render.ui
    def main_ui():
        if user_variant.get()=="A":
            return ui.navset_tab(
                user_guide_ui,
                data_loading_ui,
                data_cleaning_ui,
                eda_ui, 
                feature_engineering_ui,
                data_download_ui
            )
        else:
            step = current_step.get()
            steps = {
                1: ui.card(
                    ui.h3("Step 1: User Guide"),
                    user_guide_body, 
                    ui.input_action_button("next1", "Next", class_ = "btn-primary")
                ),
                2: ui.card(
                    ui.h3("Step 2: Data Loading"),
                    data_loading_body, 
                    ui.input_action_button("back1", "Back"),
                    ui.input_action_button("next2", "Next", class_ = "btn-primary")
                ),
                3: ui.card(
                    ui.h3("Step 3: Data Cleaning"),
                    data_cleaning_body, 
                    ui.input_action_button("back2", "Back"),
                    ui.input_action_button("next3", "Next", class_ = "btn-primary")
                ),
                4: ui.card(
                    ui.h3("Step 4: EDA"),
                    eda_body, 
                    ui.input_action_button("back3", "Back"),
                    ui.input_action_button("next4", "Next", class_ = "btn-primary")
                ),
                5: ui.card(
                    ui.h3("Step 4: Feature Engineering"),
                    feature_engineering_body, 
                    ui.input_action_button("back4", "Back"),
                    ui.input_action_button("next5", "Next", class_ = "btn-primary")
                ),
                6: ui.card(
                    ui.h3("Step 6: Download"),
                    data_download_body,
                    ui.input_action_button("back5", "Back"),
                    ui.p("\U0001F389 You're done!")
                )
            }
            return steps.get(step, ui.p("Invalid step"))

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
