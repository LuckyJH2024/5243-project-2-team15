from shiny import ui, reactive, render
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.decomposition import PCA
from data_store import df_cleaned, df_engineered, error_store
from shinywidgets import output_widget, render_widget

# Feature Engineering UI
feature_engineering_layout = ui.layout_sidebar(
        ui.sidebar(
            ui.div(  # Add a div container with fixed height and scrollbar
                ui.h3("Feature Engineering Tools"),
                ui.accordion(
                    ui.accordion_panel(
                        "Feature Creation",
                        ui.input_select("feature1_select", "Select Feature 1", choices=[]),
                        ui.input_select("feature2_select", "Select Feature 2", choices=[]),
                        ui.input_action_button("create_ratio_feature", "Create Ratio Feature", class_="btn-primary"),
                        ui.input_action_button("create_diff_feature", "Create Difference Feature", class_="btn-primary"),
                        ui.input_action_button("create_product_feature", "Create Product Feature", class_="btn-primary"),
                        ui.br(),
                        ui.br(),
                        ui.input_select("delete_feature_select", "Select Feature to Delete", choices=[]),
                        ui.input_action_button("delete_feature", "Delete Feature", class_="btn-danger"),
                    ),
                    ui.accordion_panel(
                        "Feature Transformation",
                        ui.input_select("transform_feature_select", "Select Feature to Transform", choices=[]),
                        ui.input_select(
                            "transform_method", "Transformation Method",
                            choices=["Standardization (StandardScaler)", "Normalization (MinMaxScaler)", "Log Transform", "Square Root Transform", "Square Transform", "Cube Transform", "Binarization"]
                        ),
                        ui.panel_conditional(
                            "input.transform_method === 'Binarization'",
                            ui.input_numeric("binarize_threshold", "Binarization Threshold", 0)
                        ),
                        ui.input_action_button("apply_transform", "Apply Transformation", class_="btn-primary"),
                    ),
                    ui.accordion_panel(
                        "Batch Processing",
                        ui.input_checkbox_group(
                            "numeric_features", "Select Numeric Features",
                            choices=[]
                        ),
                        ui.input_select(
                            "batch_transform_method", "Batch Transformation Method",
                            choices=["Standardization (StandardScaler)", "Normalization (MinMaxScaler)", "Robust Scaling (RobustScaler)"]
                        ),
                        ui.input_action_button("apply_batch_transform", "Apply Batch Transformation", class_="btn-primary"),
                    ),
                    ui.accordion_panel(
                        "Dimensionality Reduction",
                        ui.input_slider("pca_components", "Number of PCA Components", 2, 10, 2, step=1),
                        ui.input_checkbox_group(
                            "pca_features", "Select Features for PCA",
                            choices=[]
                        ),
                        ui.input_action_button("apply_pca", "Apply PCA", class_="btn-primary"),
                    ),
                    open=True
                ),
                ui.hr(),
                ui.input_action_button("restore_original", "Restore Original Data", class_="btn-warning"),
                ui.input_action_button("use_engineered", "Use Engineered Features", class_="btn-success"),
                style="height: calc(100vh - 100px); overflow-y: auto; padding-right: 10px;"  # Set height and scrollbar
            ),
            width=350
        ),
        ui.navset_tab(
            ui.nav_panel(
                "Data Preview",
                ui.card(
                    ui.h3("Data Preview"),
                    ui.output_text("data_summary"),
                    ui.output_table("engineered_data_preview")
                )
            ),
            ui.nav_panel(
                "Feature Visualization",
                ui.card(
                    ui.h3("Feature Visualization"),
                    ui.input_select("viz_feature1", "X-axis Feature", choices=[]),
                    ui.input_select("viz_feature2", "Y-axis Feature", choices=[]),
                    output_widget("feature_plot", height="600px")
                )
            ),
            ui.nav_panel(
                "Feature Correlation",
                ui.card(
                    ui.h3("Feature Correlation"),
                    output_widget("correlation_heatmap", height="600px")
                )
            ),
            id="feature_engineering_tabs"
        )
    )

def feature_engineering_server(input, output, session):
    # Initialize feature engineering data
    @reactive.effect
    def initialize_engineered_data():
        cleaned_data = df_cleaned.get()
        if cleaned_data is not None and df_engineered.get() is None:
            # Only keep numeric columns for feature engineering
            numeric_data = cleaned_data.select_dtypes(include=['number'])
            if not numeric_data.empty:
                df_engineered.set(numeric_data.copy())
            else:
                # If no numeric columns, use original data
                df_engineered.set(cleaned_data.copy())
    
    # React to changes in cleaned data
    @reactive.effect
    @reactive.event(df_cleaned)
    def update_engineered_data_when_cleaned_changes():
        cleaned_data = df_cleaned.get()
        if cleaned_data is not None:
            # Only keep numeric columns for feature engineering
            numeric_data = cleaned_data.select_dtypes(include=['number'])
            if not numeric_data.empty:
                df_engineered.set(numeric_data.copy())
            else:
                # If no numeric columns, use original data
                df_engineered.set(cleaned_data.copy())
            # Clear any error messages
            error_store.set("")
    
    # Update feature selection dropdowns
    @reactive.effect
    def update_feature_choices():
        data = df_engineered.get()
        if data is not None:
            # Get all columns
            all_columns = data.columns.tolist()
            
            # Get numeric columns
            numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
            
            # Update dropdown selection boxes
            ui.update_select("feature1_select", choices=all_columns, selected=all_columns[0] if all_columns else None)
            ui.update_select("feature2_select", choices=all_columns, selected=all_columns[1] if len(all_columns) > 1 else all_columns[0] if all_columns else None)
            ui.update_select("delete_feature_select", choices=all_columns, selected=all_columns[0] if all_columns else None)
            ui.update_select("transform_feature_select", choices=numeric_columns, selected=numeric_columns[0] if numeric_columns else None)
            ui.update_select("viz_feature1", choices=numeric_columns, selected=numeric_columns[0] if numeric_columns else None)
            ui.update_select("viz_feature2", choices=numeric_columns, selected=numeric_columns[1] if len(numeric_columns) > 1 else numeric_columns[0] if numeric_columns else None)
            
            # Update checkbox groups
            ui.update_checkbox_group("numeric_features", choices=numeric_columns, selected=numeric_columns)
            ui.update_checkbox_group("pca_features", choices=numeric_columns, selected=numeric_columns[:min(5, len(numeric_columns))])
    
    # Get current engineered data
    @reactive.calc
    def get_current_data():
        return df_engineered.get()
    
    # Data preview
    @output
    @render.table
    def engineered_data_preview():
        data = get_current_data()
        if data is not None:
            return data.head(10)
        return pd.DataFrame()
    
    # Data summary
    @output
    @render.text
    def data_summary():
        data = get_current_data()
        if data is not None:
            return f"Data Shape: {data.shape[0]} rows × {data.shape[1]} columns\nNumeric Columns: {len(data.select_dtypes(include=['number']).columns)}"
        return "No data available"
    
    # Feature visualization
    @render_widget
    def feature_plot():
        data = get_current_data()
        if data is None:
            fig = px.scatter(title="No data available")
            return fig
        
        feature1 = input.viz_feature1()
        feature2 = input.viz_feature2()
        
        if not feature1 or not feature2 or feature1 not in data.columns or feature2 not in data.columns:
            fig = px.scatter(title="Please select valid features for visualization")
            return fig
        
        try:
            # Create scatter plot
            fig = px.scatter(
                data, 
                x=feature1, 
                y=feature2, 
                title=f"{feature2} vs {feature1}",
                trendline="ols"
            )
            
            # Add trend line
            fig.update_layout(
                xaxis_title=feature1,
                yaxis_title=feature2,
                height=600
            )
            
            return fig
        except Exception as e:
            # If any error occurs, return an empty plot with an error message
            fig = px.scatter(title=f"Feature Visualization Error: {str(e)}")
            return fig
    
    # Correlation heatmap
    @render_widget
    def correlation_heatmap():
        data = get_current_data()
        if data is None:
            fig = px.imshow(title="No data available")
            return fig
        
        try:
            # Only select numeric columns for correlation analysis
            numeric_data = data.select_dtypes(include=['number'])
            if numeric_data.empty:
                fig = px.imshow(title="No numeric columns available for correlation analysis")
                return fig
            
            # Calculate correlation matrix
            corr_matrix = numeric_data.corr()
            
            # Create heatmap
            fig = px.imshow(
                corr_matrix,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1,
                title="Feature Correlation Heatmap"
            )
            
            fig.update_layout(
                height=600,
                xaxis_title="Features",
                yaxis_title="Features"
            )
            
            return fig
        except Exception as e:
            # If any error occurs, return an empty plot with an error message
            fig = px.imshow(title=f"Correlation Heatmap Error: {str(e)}")
            return fig
    
    # Create ratio feature
    @reactive.effect
    @reactive.event(input.create_ratio_feature)
    def create_ratio_feature():
        data = get_current_data()
        if data is None:
            error_store.set("No data available")
            return
        
        feature1 = input.feature1_select()
        feature2 = input.feature2_select()
        
        if not feature1 or not feature2:
            error_store.set("Please select two features")
            return
        
        try:
            # Create new data frame
            new_data = data.copy()
            
            # Create ratio feature
            ratio_name = f"{feature1}_div_{feature2}"
            
            # Avoid division by zero
            new_data[ratio_name] = new_data[feature1] / new_data[feature2].replace(0, np.nan)
            
            # Update data
            df_engineered.set(new_data)
            error_store.set("")
        except Exception as e:
            error_store.set(f"Error creating ratio feature: {str(e)}")
    
    # Create difference feature
    @reactive.effect
    @reactive.event(input.create_diff_feature)
    def create_diff_feature():
        data = get_current_data()
        if data is None:
            error_store.set("No data available")
            return
        
        feature1 = input.feature1_select()
        feature2 = input.feature2_select()
        
        if not feature1 or not feature2:
            error_store.set("Please select two features")
            return
        
        try:
            # Create new data frame
            new_data = data.copy()
            
            # Create difference feature
            diff_name = f"{feature1}_minus_{feature2}"
            new_data[diff_name] = new_data[feature1] - new_data[feature2]
            
            # Update data
            df_engineered.set(new_data)
            error_store.set("")
        except Exception as e:
            error_store.set(f"Error creating difference feature: {str(e)}")
    
    # Create product feature
    @reactive.effect
    @reactive.event(input.create_product_feature)
    def create_product_feature():
        data = get_current_data()
        if data is None:
            error_store.set("No data available")
            return
        
        feature1 = input.feature1_select()
        feature2 = input.feature2_select()
        
        if not feature1 or not feature2:
            error_store.set("Please select two features")
            return
        
        try:
            # Create new data frame
            new_data = data.copy()
            
            # Create product feature
            product_name = f"{feature1}_times_{feature2}"
            new_data[product_name] = new_data[feature1] * new_data[feature2]
            
            # Update data
            df_engineered.set(new_data)
            error_store.set("")
        except Exception as e:
            error_store.set(f"Error creating product feature: {str(e)}")
    
    # Delete feature
    @reactive.effect
    @reactive.event(input.delete_feature)
    def delete_feature():
        data = get_current_data()
        if data is None:
            error_store.set("No data available")
            return
        
        feature = input.delete_feature_select()
        
        if not feature:
            error_store.set("Please select a feature to delete")
            return
        
        try:
            # Create new data frame, delete selected feature
            new_data = data.drop(columns=[feature])
            
            # Update data
            df_engineered.set(new_data)
            error_store.set("")
        except Exception as e:
            error_store.set(f"Error deleting feature: {str(e)}")
    
    # Apply feature transformation
    @reactive.effect
    @reactive.event(input.apply_transform)
    def apply_transform():
        data = get_current_data()
        if data is None:
            error_store.set("No data available")
            return
        
        feature = input.transform_feature_select()
        method = input.transform_method()
        
        if not feature or not method:
            error_store.set("Please select a feature and transformation method")
            return
        
        try:
            # Create new data frame
            new_data = data.copy()
            
            # Apply selected transformation
            if method == "Standardization (StandardScaler)":
                scaler = StandardScaler()
                new_data[f"{feature}_scaled"] = scaler.fit_transform(new_data[[feature]])
            
            elif method == "Normalization (MinMaxScaler)":
                scaler = MinMaxScaler()
                new_data[f"{feature}_norm"] = scaler.fit_transform(new_data[[feature]])
            
            elif method == "Log Transform":
                # Ensure data is positive
                min_val = new_data[feature].min()
                if min_val <= 0:
                    offset = abs(min_val) + 1
                    new_data[f"{feature}_log"] = np.log(new_data[feature] + offset)
                else:
                    new_data[f"{feature}_log"] = np.log(new_data[feature])
            
            elif method == "Square Root Transform":
                # Ensure data is positive
                min_val = new_data[feature].min()
                if min_val < 0:
                    offset = abs(min_val) + 1
                    new_data[f"{feature}_sqrt"] = np.sqrt(new_data[feature] + offset)
                else:
                    new_data[f"{feature}_sqrt"] = np.sqrt(new_data[feature])
            
            elif method == "Square Transform":
                new_data[f"{feature}_squared"] = new_data[feature] ** 2
            
            elif method == "Cube Transform":
                new_data[f"{feature}_cubed"] = new_data[feature] ** 3
            
            elif method == "Binarization":
                threshold = input.binarize_threshold()
                new_data[f"{feature}_binary"] = (new_data[feature] > threshold).astype(int)
            
            # Update data
            df_engineered.set(new_data)
            error_store.set("")
        except Exception as e:
            error_store.set(f"Error applying transformation: {str(e)}")
    
    # Apply batch transformation
    @reactive.effect
    @reactive.event(input.apply_batch_transform)
    def apply_batch_transform():
        data = get_current_data()
        if data is None:
            error_store.set("No data available")
            return
        
        features = input.numeric_features()
        method = input.batch_transform_method()
        
        if not features or not method:
            error_store.set("Please select features and a transformation method")
            return
        
        # Check all selected features exist
        missing_features = [f for f in features if f not in data.columns]
        if missing_features:
            error_store.set(f"Cannot apply transformation: The following features do not exist: {', '.join(missing_features)}")
            return
        
        try:
            # Create new data frame
            new_data = data.copy()
            
            # Apply selected transformation
            if method == "Standardization (StandardScaler)":
                scaler = StandardScaler()
                new_data[features] = scaler.fit_transform(new_data[features])
            
            elif method == "Normalization (MinMaxScaler)":
                scaler = MinMaxScaler()
                new_data[features] = scaler.fit_transform(new_data[features])
            
            elif method == "Robust Scaling (RobustScaler)":
                scaler = RobustScaler()
                new_data[features] = scaler.fit_transform(new_data[features])
            
            # Update data
            df_engineered.set(new_data)
            error_store.set("")
        except Exception as e:
            error_store.set(f"Error applying batch transformation: {str(e)}")
    
    # Apply PCA
    @reactive.effect
    @reactive.event(input.apply_pca)
    def apply_pca():
        data = get_current_data()
        if data is None:
            error_store.set("No data available")
            return
        
        features = input.pca_features()
        n_components = input.pca_components()
        
        if not features:
            error_store.set("Please select features for PCA")
            return
        
        # Check all selected features exist
        missing_features = [f for f in features if f not in data.columns]
        if missing_features:
            error_store.set(f"Cannot apply PCA: The following features do not exist: {', '.join(missing_features)}")
            return
        
        # Ensure component count does not exceed feature count
        n_components = min(n_components, len(features))
        
        try:
            # Create new data frame
            new_data = data.copy()
            
            # Apply PCA
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(new_data[features])
            
            # Create PCA result data frame
            pca_df = pd.DataFrame(
                data=pca_result,
                columns=[f'PC{i+1}' for i in range(n_components)]
            )
            
            # Preserve non-PCA features
            for col in new_data.columns:
                if col not in features:
                    pca_df[col] = new_data[col].values
            
            # Update data
            df_engineered.set(pca_df)
            
            # Display explained variance ratio
            explained_variance = pca.explained_variance_ratio_
            explained_variance_msg = "PCA Explained Variance Ratio:\n" + "\n".join([f"PC{i+1}: {var:.4f}" for i, var in enumerate(explained_variance)])
            error_store.set(explained_variance_msg)
        except Exception as e:
            error_store.set(f"Error applying PCA: {str(e)}")
    
    # Restore original data
    @reactive.effect
    @reactive.event(input.restore_original)
    def restore_original():
        cleaned_data = df_cleaned.get()
        if cleaned_data is not None:
            # Only keep numeric columns for feature engineering
            numeric_data = cleaned_data.select_dtypes(include=['number'])
            if not numeric_data.empty:
                df_engineered.set(numeric_data.copy())
            else:
                df_engineered.set(cleaned_data.copy())
            error_store.set("")
    
    # Use engineered features
    @reactive.effect
    @reactive.event(input.use_engineered)
    def use_engineered():
        # This function might be called when the engineered features are passed to the model training module
        # In this example, we just display a message
        error_store.set("Feature engineering completed, next step can be performed") 

feature_engineering_ui = ui.nav_panel("Feature Engineering", feature_engineering_layout)

feature_engineering_body = feature_engineering_layout
