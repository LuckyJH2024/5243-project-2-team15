from shiny import ui, reactive, render
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from data_store import df_cleaned, error_store, user_ab_variant
from shinywidgets import output_widget, render_widget

# Exploratory Data Analysis UI
eda_layout = ui.layout_sidebar(
        ui.sidebar(
            ui.div(  # Add a div container with fixed height and scrollbar
                ui.h3("Data Analysis Tools"),
                ui.accordion(
                    ui.accordion_panel(
                        "Data Filtering",
                        ui.input_select("filter_col", "Select Filter Column", choices=[]),
                        ui.output_ui("filter_values_ui"),
                    ),
                    ui.accordion_panel(
                        "Univariate Analysis",
                        ui.input_select("univariate_col", "Select Analysis Column", choices=[]),
                        ui.input_select(
                            "univariate_plot_type", "Chart Type",
                            choices=["Histogram", "Box Plot", "Violin Plot", "Density Plot"]
                        ),
                        ui.panel_conditional(
                            "input.univariate_plot_type === 'Histogram'",
                            ui.input_slider("bins", "Number of Bins", 5, 50, 20, step=1)
                        ),
                    ),
                    ui.accordion_panel(
                        "Bivariate Analysis",
                        ui.input_select("x_col", "Select X-axis Variable", choices=[]),
                        ui.input_select("y_col", "Select Y-axis Variable", choices=[]),
                        ui.input_select("color_col", "Select Color Variable (Optional)", choices=[None]),
                        ui.input_select("size_col", "Select Size Variable (Optional)", choices=[None]),
                        ui.input_select(
                            "bivariate_plot_type", "Chart Type",
                            choices=["Scatter Plot", "Line Plot", "Bar Chart", "Heatmap"]
                        ),
                        ui.input_select(
                            "trendline_type", "Trendline Type",
                            choices=["None", "Linear Regression (OLS)", "Locally Weighted Regression (LOWESS)"]
                        ),
                    ),
                    ui.accordion_panel(
                        "Multivariate Analysis",
                        ui.input_checkbox_group(
                            "correlation_features", "Select Features for Correlation Analysis",
                            choices=[]
                        ),
                        ui.input_select(
                            "correlation_method", "Correlation Method",
                            choices=["Pearson", "Spearman", "Kendall"]
                        ),
                    ),
                    open=True
                ),
                style="height: calc(100vh - 100px); overflow-y: auto; padding-right: 10px;"  # Set height and scrollbar
            ),
            width=300
        ),
        ui.navset_tab(  # Use tab navigation instead of the original layout
            ui.nav_panel(
                "Data Summary",
                ui.card(
                    ui.h3("Data Summary"),
                    ui.output_table("summary_stats")
                )
            ),
            ui.nav_panel(
                "Univariate Analysis",
                ui.card(
                    ui.h3("Univariate Analysis"),
                    output_widget("univariate_plot", height="500px"),
                    ui.output_ui("univariate_stats")
                )
            ),
            ui.nav_panel(
                "Bivariate Analysis",
                ui.card(
                    ui.h3("Bivariate Analysis"),
                    output_widget("bivariate_plot", height="500px"),
                    ui.output_ui("bivariate_stats")
                )
            ),
            ui.nav_panel(
                "Correlation Analysis",
                ui.card(
                    ui.h3("Correlation Analysis"),
                    output_widget("correlation_plot", height="600px")
                )
            ),
            id="analysis_tabs"  # Add ID for potential future interaction control
        )
    )

def eda_server(input, output, session):
    # Update column selection dropdown
    @reactive.effect
    def update_column_choices():
        data = df_cleaned.get()
        if data is not None:
            # Get all columns
            all_columns = data.columns.tolist()
            
            # Get numeric columns
            numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
            
            # Get categorical columns
            categorical_columns = data.select_dtypes(exclude=['number']).columns.tolist()
            
            # Update dropdown selection box
            ui.update_select("filter_col", choices=all_columns, selected=all_columns[0] if all_columns else None)
            ui.update_select("univariate_col", choices=all_columns, selected=all_columns[0] if all_columns else None)
            ui.update_select("x_col", choices=all_columns, selected=numeric_columns[0] if numeric_columns else all_columns[0] if all_columns else None)
            ui.update_select("y_col", choices=all_columns, selected=numeric_columns[1] if len(numeric_columns) > 1 else numeric_columns[0] if numeric_columns else all_columns[0] if all_columns else None)
            
            # Color and size variables can be empty
            color_choices = [None] + all_columns
            ui.update_select("color_col", choices=color_choices, selected=None)
            ui.update_select("size_col", choices=color_choices, selected=None)
            
            # Update feature selection for correlation analysis
            ui.update_checkbox_group("correlation_features", choices=numeric_columns, selected=numeric_columns[:min(5, len(numeric_columns))])
            
            print(f"EDA: Updated column choices with {len(all_columns)} columns")

    # Dynamically generate filter value UI
    @output
    @render.ui
    def filter_values_ui():
        data = df_cleaned.get()
        col = input.filter_col()
        
        if data is None or col not in data.columns:
            return ui.p("No data available or column")
        
        # Get unique values of the column
        unique_values = data[col].dropna().unique()
        
        # If there are too many unique values, use a range slider
        if len(unique_values) > 10 and pd.api.types.is_numeric_dtype(data[col]):
            min_val = float(data[col].min())
            max_val = float(data[col].max())
            
            # Handle infinity values
            if np.isinf(min_val) or np.isnan(min_val):
                min_val = -1000
            if np.isinf(max_val) or np.isnan(max_val):
                max_val = 1000
                
            step = (max_val - min_val) / 100 if max_val > min_val else 0.1
            
            return ui.input_slider(
                "filter_range", "Select Range",
                min=min_val, max=max_val,
                value=[min_val, max_val],
                step=step
            )
        else:
            # Convert numpy array to dictionary format
            # Handle possible non-string values
            choices_dict = {}
            for val in unique_values:
                # Handle NaN and infinity values
                if pd.isna(val) or (isinstance(val, float) and (np.isinf(val) or np.isnan(val))):
                    continue
                # Ensure keys are strings
                str_val = str(val)
                choices_dict[str_val] = str_val
            
            # If no valid values, display a message
            if not choices_dict:
                return ui.p("No valid values available for filtering")
                
            return ui.input_checkbox_group(
                "filter_values", "Select Values",
                choices=choices_dict,
                selected=list(choices_dict.keys())
            )
    
    # Get filtered data
    @reactive.calc
    def get_filtered_data():
        data = df_cleaned.get()
        if data is None:
            return pd.DataFrame()
        
        col = input.filter_col()
        if col not in data.columns:
            return data
        
        # Filter based on UI type
        try:
            if hasattr(input, "filter_range"):
                min_val, max_val = input.filter_range()
                return data[(data[col] >= min_val) & (data[col] <= max_val)]
            elif hasattr(input, "filter_values"):
                filter_values = input.filter_values()
                if filter_values:
                    # Handle string format filter values
                    if pd.api.types.is_numeric_dtype(data[col]):
                        # For numeric columns, convert strings back to numbers
                        numeric_values = []
                        for val in filter_values:
                            try:
                                if '.' in val:
                                    numeric_values.append(float(val))
                                else:
                                    numeric_values.append(int(val))
                            except ValueError:
                                # If conversion fails, keep original string
                                numeric_values.append(val)
                        return data[data[col].isin(numeric_values)]
                    else:
                        # For non-numeric columns, use string values directly
                        return data[data[col].astype(str).isin(filter_values)]
            
            return data
        except Exception as e:
            print(f"Error in filtering: {e}")
            return data
    
    # Data summary
    @output
    @render.table
    def summary_stats():
        data = get_filtered_data()
        if data.empty:
            return pd.DataFrame({"message": ["No data available"]})
        
        # Calculate statistical summary for numeric columns
        numeric_data = data.select_dtypes(include=['number'])
        if numeric_data.empty:
            return pd.DataFrame({"message": ["No numeric columns available for summary"]})
        
        return numeric_data.describe().reset_index()
    
    # Univariate analysis charts
    @render_widget
    def univariate_plot():
        data = get_filtered_data()
        col = input.univariate_col()
        plot_type = input.univariate_plot_type()
        
        if data.empty or col not in data.columns:
            fig = px.scatter(title="No data available or column")
            return fig
        
        # Create different charts based on data type and chart type
        if pd.api.types.is_numeric_dtype(data[col]):
            if plot_type == "Histogram":
                fig = px.histogram(
                    data, 
                    x=col,
                    nbins=input.bins(),
                    title=f"{col} Histogram",
                    template="plotly_white"
                )
            
            elif plot_type == "Box Plot":
                fig = px.box(
                    data, 
                    y=col,
                    title=f"{col} Box Plot",
                    template="plotly_white"
                )
            
            elif plot_type == "Violin Plot":
                fig = px.violin(
                    data, 
                    y=col,
                    title=f"{col} Violin Plot",
                    template="plotly_white"
                )
            
            elif plot_type == "Density Plot":
                fig = ff.create_distplot(
                    [data[col].dropna()], 
                    [col],
                    show_hist=False,
                    show_rug=True
                )
                fig.update_layout(
                    title=f"{col} Density Plot",
                    template="plotly_white"
                )
        else:
            #For categorical variables, display a bar chart
            value_counts = data[col].value_counts().reset_index()
            value_counts.columns = ['value', 'count']
            
            fig = px.bar(
                value_counts, 
                x='value', 
                y='count',
                title=f"{col} Value Distribution",
                template="plotly_white"
            )
        
        # Set chart height and width
        fig.update_layout(height=400, width=None)
        
        return fig
    
    # Univariate statistical information
    @output
    @render.ui
    def univariate_stats():
        data = get_filtered_data()
        col = input.univariate_col()
        
        if data.empty or col not in data.columns:
            return ui.p("No data available or column")
        
        stats = []
        stats.append(ui.h4(f"Column: {col}"))
        stats.append(ui.p(f"Data Type: {data[col].dtype}"))
        stats.append(ui.p(f"Non-null Value Count: {data[col].count()} / {len(data[col])}"))
        stats.append(ui.p(f"Missing Value Count: {data[col].isna().sum()} ({data[col].isna().mean():.2%})"))
        
        if pd.api.types.is_numeric_dtype(data[col]):
            stats.append(ui.p(f"Minimum: {data[col].min():.4g}"))
            stats.append(ui.p(f"Maximum: {data[col].max():.4g}"))
            stats.append(ui.p(f"Mean: {data[col].mean():.4g}"))
            stats.append(ui.p(f"Median: {data[col].median():.4g}"))
            stats.append(ui.p(f"Standard Deviation: {data[col].std():.4g}"))
            stats.append(ui.p(f"Skewness: {data[col].skew():.4g}"))
            stats.append(ui.p(f"Kurtosis: {data[col].kurtosis():.4g}"))
        else:
            stats.append(ui.p(f"Unique Value Count: {data[col].nunique()}"))
            value_counts = data[col].value_counts().head(5)
            stats.append(ui.p("Top 5 Value Frequencies:"))
            for val, count in value_counts.items():
                stats.append(ui.p(f"- {val}: {count} ({count/len(data[col]):.2%})"))
        
        return ui.div(*stats)
    
    # Bivariate analysis charts
    @render_widget
    def bivariate_plot():
        data = get_filtered_data()
        x_col = input.x_col()
        y_col = input.y_col()
        color_col = input.color_col() if input.color_col() != "None" else None
        size_col = input.size_col() if input.size_col() != "None" else None
        plot_type = input.bivariate_plot_type()
        trendline_type = input.trendline_type()
        
        if data.empty or x_col not in data.columns or y_col not in data.columns:
            fig = px.scatter(title="No data available or column")
            return fig
        
        # Check whether the color and size columns exist
        if color_col and color_col not in data.columns:
            color_col = None
        if size_col and size_col not in data.columns:
            size_col = None
        
        try:
            # Create different charts based on the chart type
            if plot_type == "Scatter Plot":
                trendline = None
                if trendline_type == "Linear Regression (OLS)":
                    trendline = "ols"
                elif trendline_type == "Locally Weighted Regression (LOWESS)":
                    trendline = "lowess"
                
                fig = px.scatter(
                    data, 
                    x=x_col, 
                    y=y_col,
                    color=color_col,
                    size=size_col,
                    trendline=trendline,
                    title=f"{y_col} vs {x_col}",
                    template="plotly_white"
                )
            
            elif plot_type == "Line Plot":
                fig = px.line(
                    data, 
                    x=x_col, 
                    y=y_col,
                    color=color_col,
                    title=f"{y_col} vs {x_col}",
                    template="plotly_white"
                )
            
            elif plot_type == "Bar Chart":
                # For bar charts, we need to aggregate the data
                if pd.api.types.is_numeric_dtype(data[y_col]):
                    #If Y is numeric, calculate the average Y value for each X value
                    agg_data = data.groupby(x_col)[y_col].mean().reset_index()
                    fig = px.bar(
                        agg_data, 
                        x=x_col, 
                        y=y_col,
                        color=color_col if color_col in agg_data.columns else None,
                        title=f"{y_col} vs {x_col} (Mean)",
                        template="plotly_white"
                    )
                else:
                    # If Y is not numeric, count the occurrences of each X-Y combination
                    agg_data = data.groupby([x_col, y_col]).size().reset_index(name='count')
                    fig = px.bar(
                        agg_data, 
                        x=x_col, 
                        y='count',
                        color=y_col,
                        title=f"{y_col} vs {x_col} (Count)",
                        template="plotly_white"
                    )
            
            elif plot_type == "Heatmap":
                # For heatmaps, we need to aggregate the data
                if pd.api.types.is_numeric_dtype(data[y_col]):
                    #If Y is numeric, calculate the average Y value for each X value
                    pivot_data = data.pivot_table(
                        values=y_col, 
                        index=x_col, 
                        columns=color_col if color_col else None,
                        aggfunc='mean'
                    )
                    fig = px.imshow(
                        pivot_data,
                        title=f"{y_col} vs {x_col} (Mean)",
                        template="plotly_white"
                    )
                else:
                    # If Y is not numeric, count each X-Y combination
                    pivot_data = pd.crosstab(data[x_col], data[y_col])
                    fig = px.imshow(
                        pivot_data,
                        title=f"{y_col} vs {x_col} (Count)",
                        template="plotly_white"
                    )
        except Exception as e:
            # If any error occurs, return an empty chart with an error message
            fig = px.scatter(title=f"Chart Generation Error: {str(e)}")
            return fig
        
        # Set chart height and width
        fig.update_layout(height=400, width=None)
        
        return fig
    
    #Bivariate statistical information
    @output
    @render.ui
    def bivariate_stats():
        data = get_filtered_data()
        x_col = input.x_col()
        y_col = input.y_col()
        
        if data.empty or x_col not in data.columns or y_col not in data.columns:
            return ui.p("No data available or column")
        
        stats = []
        
        # If both variables are numerical, calculate the correlation
        if pd.api.types.is_numeric_dtype(data[x_col]) and pd.api.types.is_numeric_dtype(data[y_col]):
            # Calculate correlation coefficient.
            pearson_corr = data[[x_col, y_col]].corr().iloc[0, 1]
            spearman_corr = data[[x_col, y_col]].corr(method='spearman').iloc[0, 1]
            
            stats.append(ui.h4(f"{x_col} and {y_col} Relationship"))
            stats.append(ui.p(f"Pearson Correlation Coefficient: {pearson_corr:.4f}"))
            stats.append(ui.p(f"Spearman Correlation Coefficient: {spearman_corr:.4f}"))
            
            # Simple linear regression
            from sklearn.linear_model import LinearRegression
            X = data[x_col].values.reshape(-1, 1)
            y = data[y_col].values
            
            #Remove missing values.
            mask = ~np.isnan(X.flatten()) & ~np.isnan(y)
            X = X[mask].reshape(-1, 1)
            y = y[mask]
            
            if len(X) > 0:
                model = LinearRegression()
                model.fit(X, y)
                r2 = model.score(X, y)
                
                stats.append(ui.p(f"Linear Regression Coefficient: {model.coef_[0]:.4f}"))
                stats.append(ui.p(f"Linear Regression Intercept: {model.intercept_:.4f}"))
                stats.append(ui.p(f"R²: {r2:.4f}"))
        
        #If one is a categorical variable and the other is a numerical variable, compute the statistics for each category
        elif (pd.api.types.is_numeric_dtype(data[x_col]) and not pd.api.types.is_numeric_dtype(data[y_col])) or \
             (not pd.api.types.is_numeric_dtype(data[x_col]) and pd.api.types.is_numeric_dtype(data[y_col])):
            
            # Determine which is the categorical variable and which is the numerical variable
            cat_col, num_col = (y_col, x_col) if pd.api.types.is_numeric_dtype(data[x_col]) else (x_col, y_col)
            
            stats.append(ui.h4(f"{cat_col} and {num_col} Relationship"))
            
            #Calculate statistics for each category
            group_stats = data.groupby(cat_col)[num_col].agg(['mean', 'median', 'std', 'count']).reset_index()
            
            #Display statistics for each category
            stats.append(ui.p("Each Category Statistics:"))
            for _, row in group_stats.iterrows():
                stats.append(ui.p(f"- {row[cat_col]}: Mean={row['mean']:.4g}, Median={row['median']:.4g}, Std={row['std']:.4g}, Count={row['count']}"))
            
            # Perform ANOVA (Analysis of Variance)
            from scipy import stats as scipy_stats
            
            # Prepare data for ANOVA (Analysis of Variance)
            groups = []
            for category in data[cat_col].unique():
                group_data = data[data[cat_col] == category][num_col].dropna()
                if len(group_data) > 0:
                    groups.append(group_data)
            
            if len(groups) > 1 and all(len(g) > 0 for g in groups):
                f_val, p_val = scipy_stats.f_oneway(*groups)
                stats.append(ui.p(f"ANOVA Test: F Value={f_val:.4g}, p Value={p_val:.4g}"))
                stats.append(ui.p(f"Conclusion: {'Categories have significant differences' if p_val < 0.05 else 'Categories have no significant differences'}"))
        
        # If both variables are categorical, compute the Chi-square test
        else:
            # Create a contingency table
            contingency_table = pd.crosstab(data[x_col], data[y_col])
            
            stats.append(ui.h4(f"{x_col} and {y_col} Relationship"))
            
            #Calculate the chi-square test
            from scipy import stats as scipy_stats
            
            # Ensure that each cell in the contingency table has sufficient observations
            if contingency_table.size > 0 and (contingency_table > 5).all().all():
                chi2, p, dof, expected = scipy_stats.chi2_contingency(contingency_table)
                stats.append(ui.p(f"Chi-Square Test: χ²={chi2:.4g}, p Value={p:.4g}, Degrees of Freedom={dof}"))
                stats.append(ui.p(f"Conclusion: {'Variables have significant association' if p < 0.05 else 'Variables have no significant association'}"))
            else:
                stats.append(ui.p("Cannot perform Chi-Square Test: Some cells have insufficient observations"))
        
        return ui.div(*stats)
    
    # Correlation analysis chart
    @render_widget
    def correlation_plot():
        data = get_filtered_data()
        features = input.correlation_features()
        method = input.correlation_method().lower()

        # ** Data Check: If data is empty or features are not selected**
        if data is None or data.empty or not features:
            fig = px.imshow(
                np.zeros((1,1)),  # Pass 1x1 matrix to prevent imshow() from crashing
                title="No data available or features",
                color_continuous_scale="gray"
            )
            return fig

        try:
            # **Check all selected features are in the data**
            valid_features = [f for f in features if f in data.columns]
            if not valid_features:
                fig = px.imshow(
                    np.zeros((1,1)),
                    title="All selected features do not exist",
                    color_continuous_scale="gray"
                )
                return fig

            # Preprocess data, replace infinity values and NaN
            numeric_data = data[valid_features].select_dtypes(include=['number'])
            # Replace infinity values with NaN
            numeric_data = numeric_data.replace([np.inf, -np.inf], np.nan)
            # Fill NaN with median for each column
            for col in numeric_data.columns:
                median_val = numeric_data[col].median()
                if pd.isna(median_val):  # If median is also NaN, fill with 0
                    numeric_data[col] = numeric_data[col].fillna(0)
                else:
                    numeric_data[col] = numeric_data[col].fillna(median_val)

            # ** Calculate Correlation Matrix**
            corr_matrix = numeric_data.corr(method=method)

            # ** Ensure correlation matrix is not empty**
            if corr_matrix.empty or corr_matrix.isna().all().all():
                fig = px.imshow(
                    np.zeros((1,1)),
                    title="No valid correlation data",
                    color_continuous_scale="gray"
                )
                return fig

            # Ensure no NaN values in correlation matrix
            corr_matrix = corr_matrix.fillna(0)

            # ** Create Correlation Heatmap**
            # Ensure annotation text doesn't contain NaN or infinity
            annotation_text = np.round(corr_matrix.values, 2)
            # Convert any possible NaN or infinity values to string "N/A"
            annotation_text = np.where(np.isfinite(annotation_text), annotation_text.astype(str), "N/A")
            
            fig = ff.create_annotated_heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns.tolist(),
                y=corr_matrix.index.tolist(),
                annotation_text=annotation_text,
                colorscale="RdBu_r"
            )

            # ** Update Layout**
            fig.update_layout(
                title=f"{method.capitalize()} Correlation Heatmap",
                xaxis_title="Features",
                yaxis_title="Features",
                height=500,
                width=None
            )
            
            # Add color scale
            fig.update_layout(coloraxis_showscale=True)
            
            # Ensure heatmap shows color scale
            if len(fig.data) > 0:
                fig.data[0].showscale = True
                # Set color scale title and position
                fig.data[0].colorbar = dict(
                    title="Correlation Coefficient",
                    thickness=15,
                    len=0.9
                )

            return fig

        except Exception as e:
            # ** Handle Exception, Avoid imshow() Directly Crashing**
            print(f"Correlation plot error: {str(e)}")
            fig = px.imshow(
                np.zeros((1,1)),
                title=f"Correlation Analysis Error: {str(e)}",
                color_continuous_scale="gray"
            )
            return fig

eda_ui = ui.nav_panel("Exploratory Analysis", eda_layout)

eda_body = eda_layout

# Export a standalone version of update_column_choices for external calling
def update_column_choices(input=None, output=None, session=None):
    data = df_cleaned.get()
    if data is not None:
        # Get all columns
        all_columns = data.columns.tolist()
        
        # Get numeric columns
        numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
        
        # Update dropdown selection box
        ui.update_select("filter_col", choices=all_columns, selected=all_columns[0] if all_columns else None)
        ui.update_select("univariate_col", choices=all_columns, selected=all_columns[0] if all_columns else None)
        ui.update_select("x_col", choices=all_columns, selected=numeric_columns[0] if numeric_columns else all_columns[0] if all_columns else None)
        ui.update_select("y_col", choices=all_columns, selected=numeric_columns[1] if len(numeric_columns) > 1 else numeric_columns[0] if numeric_columns else all_columns[0] if all_columns else None)
        
        # Color and size variables can be empty
        color_choices = [None] + all_columns
        ui.update_select("color_col", choices=color_choices, selected=None)
        ui.update_select("size_col", choices=color_choices, selected=None)
        
        # Update feature selection for correlation analysis
        ui.update_checkbox_group("correlation_features", choices=numeric_columns, selected=numeric_columns[:min(5, len(numeric_columns))])
        
        print(f"EDA externally synced: {len(all_columns)} columns")
