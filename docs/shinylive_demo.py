from shiny import App, ui, render
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Create sample data
def generate_sample_data():
    np.random.seed(42)
    n = 100
    data = {
        'feature1': np.random.normal(0, 1, n),
        'feature2': np.random.normal(5, 2, n),
        'feature3': np.random.exponential(2, n),
        'target': np.random.randint(0, 2, n)
    }
    return pd.DataFrame(data)

# Application UI
app_ui = ui.page_fluid(
    ui.h1("Data Analysis Demo"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("Controls"),
            ui.input_select(
                "x_var", "X Variable:",
                {"feature1": "Feature 1", "feature2": "Feature 2", "feature3": "Feature 3"}
            ),
            ui.input_select(
                "y_var", "Y Variable:",
                {"feature1": "Feature 1", "feature2": "Feature 2", "feature3": "Feature 3"}
            ),
            ui.input_checkbox_group(
                "color_by", "Color by:",
                {"target": "Target"}
            ),
            ui.input_slider("alpha", "Transparency:", 0.1, 1.0, 0.7, step=0.1),
            ui.input_slider("point_size", "Point Size:", 10, 100, 50, step=10),
            ui.hr(),
            ui.p("This is a simplified demo of the full Data Analysis and Feature Engineering Platform."),
            width=300
        ),
        ui.card(
            ui.h3("Data Visualization"),
            ui.output_plot("scatter_plot", height="400px"),
            ui.h3("Data Summary"),
            ui.output_table("data_summary")
        )
    )
)

# Server logic
def server(input, output, session):
    # Load sample data
    df = generate_sample_data()
    
    @output
    @render.plot
    def scatter_plot():
        x_var = input.x_var()
        y_var = input.y_var()
        alpha = input.alpha()
        point_size = input.point_size()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if "target" in input.color_by():
            colors = ['blue', 'red']
            for i, group in df.groupby('target'):
                ax.scatter(
                    group[x_var], 
                    group[y_var], 
                    alpha=alpha, 
                    s=point_size,
                    color=colors[i], 
                    label=f'Target {i}'
                )
            ax.legend()
        else:
            ax.scatter(df[x_var], df[y_var], alpha=alpha, s=point_size, color='blue')
        
        ax.set_xlabel(input.x_var())
        ax.set_ylabel(input.y_var())
        ax.set_title(f'{input.y_var()} vs {input.x_var()}')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        return fig
    
    @output
    @render.table
    def data_summary():
        return df.describe().round(2)

# Create application
app = App(app_ui, server)

# Run application
if __name__ == "__main__":
    app.run() 