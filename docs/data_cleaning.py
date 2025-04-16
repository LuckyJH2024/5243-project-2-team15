from shiny import ui, reactive, render
import pandas as pd
import numpy as np
import plotly.express as px
from data_store import df_raw, df_cleaned, error_store
from shinywidgets import output_widget, render_widget

# Data Cleaning UI
data_cleaning_layout = ui.layout_sidebar(
        ui.sidebar(
            ui.div(
                ui.h3("Data Cleaning Tools"),
                ui.input_select("column_select", "Select Column", choices=[]),
                ui.input_select(
                    "cleaning_action", "Select Cleaning Operation",
                    choices=[
                        "Fill Missing Values", "Remove Missing Values", "Remove Outliers", 
                        "Convert to Numeric", "Standardize Text", "One-Hot Encoding"
                    ]
                ),
                ui.panel_conditional(
                    "input.cleaning_action === 'Fill Missing Values'",
                    ui.input_select(
                        "fill_method", "Fill Method",
                        choices=["Mean", "Median", "Mode", "Fixed Value", "Forward Fill", "Backward Fill"]
                    ),
                    ui.panel_conditional(
                        "input.fill_method === 'Fixed Value'",
                        ui.input_text("fill_value", "Fill Value", "0")
                    )
                ),
                ui.panel_conditional(
                    "input.cleaning_action === 'Remove Outliers'",
                    ui.input_slider("outlier_threshold", "Outlier Threshold (Standard Deviations)", 1.5, 5.0, 3.0, step=0.1)
                ),
                ui.br(),
                ui.input_action_button("apply_cleaning", "Apply Cleaning", class_="btn-primary"),
                ui.input_action_button("reset_data", "Reset Data", class_="btn-warning"),
                style="height: calc(100vh - 100px); overflow-y: auto; padding-right: 10px;"
            ),
            width=300
        ),
        ui.layout_columns(
            ui.card(
                ui.h3("Column Information"),
                output_widget("column_distribution", height="300px"),
                ui.output_ui("column_stats")
            ),
            ui.card(
                ui.h3("Data Preview"),
                ui.output_table("cleaned_data_preview"),
                ui.h4("Cleaning Suggestions"),
                ui.output_ui("cleaning_suggestions")
            ),
            col_widths=[12, 12],  # Each card occupies the full row width
            row_heights=[1, 2]    # Data preview card height is twice the column information card
        )
    )

def data_cleaning_server(input, output, session):
    # Initialize cleaned data
    @reactive.effect
    def initialize_cleaned_data():
        raw_data = df_raw.get()
        if raw_data is not None and df_cleaned.get() is None:
            df_cleaned.set(raw_data.copy())

    # Update column selection dropdown
    @reactive.effect
    def update_column_choices():
        data = df_cleaned.get()
        if data is not None:
            columns = data.columns.tolist()
            ui.update_select(
                id="column_select",
                choices=columns,
                selected=columns[0] if columns else None
            )

    # Get currently selected column
    @reactive.calc
    def get_selected_column():
        data = df_cleaned.get()
        col = input.column_select()
        if data is not None and col in data.columns:
            return data[col]
        return None

    # Column statistics
    @output
    @render.ui
    def column_stats():
        col_data = get_selected_column()
        if col_data is None:
            return ui.p("No column selected or data is empty")
        
        # Create a title row
        stats = [ui.h4(f"Column: {input.column_select()}")]
        
        # Create a three-column layout row
        rows = []
        
        if pd.api.types.is_numeric_dtype(col_data):
            # Basic information row for numeric columns
            row1 = ui.layout_columns(
                ui.div(ui.p(f"Data Type: {col_data.dtype}")),
                ui.div(ui.p(f"Non-null Values: {col_data.count()}/{len(col_data)}")),
                ui.div(ui.p(f"Missing Values: {col_data.isna().sum()} ({col_data.isna().mean():.2%})")),
                col_widths=[4, 4, 4]
            )
            rows.append(row1)
            
            # Numeric statistics row
            row2 = ui.layout_columns(
                ui.div(ui.p(f"Minimum: {col_data.min():.4g}")),
                ui.div(ui.p(f"Maximum: {col_data.max():.4g}")),
                ui.div(ui.p(f"Mean: {col_data.mean():.4g}")),
                col_widths=[4, 4, 4]
            )
            rows.append(row2)
            
            # Additional statistics row
            row3 = ui.layout_columns(
                ui.div(ui.p(f"Median: {col_data.median():.4g}")),
                ui.div(ui.p(f"Standard Deviation: {col_data.std():.4g}")),
                ui.div(),  # Empty div to maintain symmetry
                col_widths=[4, 4, 4]
            )
            rows.append(row3)
        else:
            # Basic information row for categorical columns
            row1 = ui.layout_columns(
                ui.div(ui.p(f"Data Type: {col_data.dtype}")),
                ui.div(ui.p(f"Non-null Values: {col_data.count()}/{len(col_data)}")),
                ui.div(ui.p(f"Missing Values: {col_data.isna().sum()} ({col_data.isna().mean():.2%})")),
                col_widths=[4, 4, 4]
            )
            rows.append(row1)
            
            # Unique value information row
            row2 = ui.layout_columns(
                ui.div(ui.p(f"Unique Value Count: {col_data.nunique()}")),
                ui.div(),  # Empty div to maintain symmetry
                ui.div(),  # Empty div to maintain symmetry
                col_widths=[4, 4, 4]
            )
            rows.append(row2)
            
            if col_data.nunique() < 10:
                rows.append(ui.p("Top 5 Value Frequencies:"))
                value_counts = col_data.value_counts().head(5)
                for val, count in value_counts.items():
                    rows.append(ui.p(f"- {val}: {count} ({count/len(col_data):.2%})"))
        
        # Combine title and all rows
        return ui.div(stats[0], *rows)

    # Column distribution chart
    @render_widget
    def column_distribution():
        col_data = get_selected_column()
        if col_data is None:
            fig = px.scatter(title="No column selected or data is empty")
            return fig
        
        try:
            if pd.api.types.is_numeric_dtype(col_data):
                # Display histogram for numeric columns
                fig = px.histogram(
                    x=col_data,
                    title=f"Distribution of {input.column_select()}",
                    labels={"x": input.column_select()},
                    template="plotly_white"
                )
            else:
                # Display bar chart for categorical columns
                value_counts = col_data.value_counts().reset_index()
                value_counts.columns = ["value", "count"]
                
                # Limit to top 20 categories if there are too many
                if len(value_counts) > 20:
                    value_counts = value_counts.head(20)
                    title = f"Top 20 Categories in {input.column_select()}"
                else:
                    title = f"Categories in {input.column_select()}"
                
                fig = px.bar(
                    value_counts,
                    x="value",
                    y="count",
                    title=title,
                    labels={"value": input.column_select(), "count": "Count"},
                    template="plotly_white"
                )
            
            # Update layout
            fig.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis_title=input.column_select(),
                yaxis_title="Count"
            )
            return fig
        except Exception as e:
            # Return empty figure with error message
            fig = px.scatter(title=f"Error generating chart: {str(e)}")
            return fig

    # Cleaning suggestions
    @output
    @render.ui
    def cleaning_suggestions():
        col_data = get_selected_column()
        if col_data is None:
            return ui.p("No column selected or data is empty")
        
        suggestions = []
        
        # Check for missing values
        missing_rate = col_data.isna().mean()
        if missing_rate > 0:
            if missing_rate > 0.5:
                suggestions.append(ui.p(f"⚠️ This column has a high missing value rate of {missing_rate:.2%}, consider removing this column"))
            else:
                suggestions.append(ui.p(f"⚠️ This column has {missing_rate:.2%} missing values, consider filling or removing them"))
        
        # Suggestions for numeric columns
        if pd.api.types.is_numeric_dtype(col_data):
            # Check for outliers
            q1 = col_data.quantile(0.25)
            q3 = col_data.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
            if len(outliers) > 0:
                suggestions.append(ui.p(f"⚠️ Detected {len(outliers)} outliers ({len(outliers)/len(col_data):.2%}), consider handling them"))
            
            # Check if standardization is needed
            if col_data.std() > 10 * col_data.mean():
                suggestions.append(ui.p("⚠️ Data has a wide range, consider standardization or normalization"))
        
        # Suggestions for categorical columns
        else:
            # Check for high cardinality
            unique_count = col_data.nunique()
            if unique_count > 100:
                suggestions.append(ui.p(f"⚠️ This column has high cardinality ({unique_count} unique values), consider grouping or encoding"))
            
            # Check for potential numeric columns
            if col_data.dtype == 'object':
                # Try to convert to numeric
                numeric_conversion = pd.to_numeric(col_data, errors='coerce')
                if numeric_conversion.notna().mean() > 0.8:  # If more than 80% can be converted
                    suggestions.append(ui.p("⚠️ This column appears to contain numeric values, consider converting to numeric type"))
        
        if not suggestions:
            suggestions.append(ui.p("✅ No specific cleaning suggestions for this column"))
        
        return ui.div(*suggestions)

    # Data preview
    @output
    @render.table
    def cleaned_data_preview():
        data = df_cleaned.get()
        if data is not None:
            return data.head(10)
        return pd.DataFrame()

    # Reset data
    @reactive.effect
    @reactive.event(input.reset_data)
    def reset_data():
        raw_data = df_raw.get()
        if raw_data is not None:
            df_cleaned.set(raw_data.copy())
            error_store.set("Data has been reset to original state")

    # Apply cleaning operation
    @reactive.effect
    @reactive.event(input.apply_cleaning)
    def apply_cleaning_operation():
        data = df_cleaned.get()
        col = input.column_select()
        action = input.cleaning_action()
        
        if data is None or col not in data.columns:
            error_store.set("No data or column selected")
            return
        
        try:
            cleaned_data = data.copy()
            
            # Fill missing values
            if action == "Fill Missing Values":
                method = input.fill_method()
                
                if method == "Mean" and pd.api.types.is_numeric_dtype(cleaned_data[col]):
                    cleaned_data[col] = cleaned_data[col].fillna(cleaned_data[col].mean())
                
                elif method == "Median" and pd.api.types.is_numeric_dtype(cleaned_data[col]):
                    cleaned_data[col] = cleaned_data[col].fillna(cleaned_data[col].median())
                
                elif method == "Mode":
                    mode_value = cleaned_data[col].mode()[0] if not cleaned_data[col].mode().empty else None
                    cleaned_data[col] = cleaned_data[col].fillna(mode_value)
                
                elif method == "Fixed Value":
                    fill_value = input.fill_value()
                    # Try to convert to numeric if the column is numeric
                    if pd.api.types.is_numeric_dtype(cleaned_data[col]):
                        try:
                            fill_value = float(fill_value)
                        except ValueError:
                            pass
                    cleaned_data[col] = cleaned_data[col].fillna(fill_value)
                
                elif method == "Forward Fill":
                    cleaned_data[col] = cleaned_data[col].ffill()
                
                elif method == "Backward Fill":
                    cleaned_data[col] = cleaned_data[col].bfill()
            
            # Remove missing values
            elif action == "Remove Missing Values":
                cleaned_data = cleaned_data.dropna(subset=[col])
            
            # Remove outliers
            elif action == "Remove Outliers" and pd.api.types.is_numeric_dtype(cleaned_data[col]):
                threshold = input.outlier_threshold()
                mean = cleaned_data[col].mean()
                std = cleaned_data[col].std()
                lower_bound = mean - threshold * std
                upper_bound = mean + threshold * std
                cleaned_data = cleaned_data[(cleaned_data[col] >= lower_bound) & (cleaned_data[col] <= upper_bound)]
            
            # Convert to numeric
            elif action == "Convert to Numeric":
                cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
            
            # Standardize text
            elif action == "Standardize Text" and cleaned_data[col].dtype == 'object':
                cleaned_data[col] = cleaned_data[col].str.lower().str.strip()
            
            # One-hot encoding
            elif action == "One-Hot Encoding" and cleaned_data[col].dtype == 'object':
                # Get unique values
                unique_values = cleaned_data[col].dropna().unique()
                
                # Create a new column for each unique value
                for value in unique_values:
                    new_col = f"{col}_{value}"
                    cleaned_data[new_col] = (cleaned_data[col] == value).astype(int)
                
                # Remove original column
                cleaned_data = cleaned_data.drop(columns=[col])
            
            # Update cleaned data
            df_cleaned.set(cleaned_data)
            
        except Exception as e:
            error_store.set(f"Cleaning operation failed: {str(e)}") 

data_cleaning_ui = ui.nav_panel("Data Cleaning", data_cleaning_layout)

data_cleaning_body = data_cleaning_layout
