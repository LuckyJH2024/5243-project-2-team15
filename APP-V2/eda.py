from shiny import ui, reactive, render
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from data_store import df_cleaned, error_store
from shinywidgets import output_widget, render_widget

# Exploratory Data Analysis UI
eda_ui = ui.nav_panel(
    "Exploratory Analysis",
    ui.layout_sidebar(
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
)

def eda_server(input, output, session):
    # 更新列选择下拉框
    @reactive.effect
    def update_column_choices():
        data = df_cleaned.get()
        if data is not None:
            # 获取所有列
            all_columns = data.columns.tolist()
            
            # 获取数值列
            numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
            
            # 获取分类列
            categorical_columns = data.select_dtypes(exclude=['number']).columns.tolist()
            
            # 更新下拉选择框
            ui.update_select("filter_col", choices=all_columns, selected=all_columns[0] if all_columns else None)
            ui.update_select("univariate_col", choices=all_columns, selected=all_columns[0] if all_columns else None)
            ui.update_select("x_col", choices=all_columns, selected=numeric_columns[0] if numeric_columns else all_columns[0] if all_columns else None)
            ui.update_select("y_col", choices=all_columns, selected=numeric_columns[1] if len(numeric_columns) > 1 else numeric_columns[0] if numeric_columns else all_columns[0] if all_columns else None)
            
            # 颜色和大小变量可以为空
            color_choices = [None] + all_columns
            ui.update_select("color_col", choices=color_choices, selected=None)
            ui.update_select("size_col", choices=color_choices, selected=None)
            
            # 更新相关性分析的特征选择
            ui.update_checkbox_group("correlation_features", choices=numeric_columns, selected=numeric_columns[:min(5, len(numeric_columns))])
    
    # 动态生成筛选值UI
    @output
    @render.ui
    def filter_values_ui():
        data = df_cleaned.get()
        col = input.filter_col()
        
        if data is None or col not in data.columns:
            return ui.p("No data available or column")
        
        # 获取列的唯一值
        unique_values = data[col].dropna().unique()
        
        # 如果唯一值太多，使用范围滑块
        if len(unique_values) > 10 and pd.api.types.is_numeric_dtype(data[col]):
            min_val = data[col].min()
            max_val = data[col].max()
            step = (max_val - min_val) / 100 if max_val > min_val else 0.1
            
            return ui.input_slider(
                "filter_range", "Select Range",
                min=min_val, max=max_val,
                value=[min_val, max_val],
                step=step
            )
        else:
            # 对于分类变量或唯一值较少的数值变量，使用复选框
            return ui.input_checkbox_group(
                "filter_values", "Select Values",
                choices=unique_values,
                selected=unique_values
            )
    
    # 获取筛选后的数据
    @reactive.calc
    def get_filtered_data():
        data = df_cleaned.get()
        if data is None:
            return pd.DataFrame()
        
        col = input.filter_col()
        if col not in data.columns:
            return data
        
        # 根据UI类型进行筛选
        try:
            if hasattr(input, "filter_range"):
                min_val, max_val = input.filter_range()
                return data[(data[col] >= min_val) & (data[col] <= max_val)]
            elif hasattr(input, "filter_values"):
                filter_values = input.filter_values()
                if filter_values:
                    return data[data[col].isin(filter_values)]
            
            return data
        except:
            return data
    
    # 数据摘要
    @output
    @render.table
    def summary_stats():
        data = get_filtered_data()
        if data.empty:
            return pd.DataFrame({"message": ["No data available"]})
        
        # 只对数值列计算统计摘要
        numeric_data = data.select_dtypes(include=['number'])
        if numeric_data.empty:
            return pd.DataFrame({"message": ["No numeric columns available for summary"]})
        
        return numeric_data.describe().reset_index()
    
    # 单变量分析图表
    @render_widget
    def univariate_plot():
        data = get_filtered_data()
        col = input.univariate_col()
        plot_type = input.univariate_plot_type()
        
        if data.empty or col not in data.columns:
            fig = px.scatter(title="No data available or column")
            return fig
        
        # 根据数据类型和图表类型创建不同的图表
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
            # 对于分类变量，显示条形图
            value_counts = data[col].value_counts().reset_index()
            value_counts.columns = ['value', 'count']
            
            fig = px.bar(
                value_counts, 
                x='value', 
                y='count',
                title=f"{col} Value Distribution",
                template="plotly_white"
            )
        
        # 设置图表高度和宽度
        fig.update_layout(height=400, width=None)
        
        return fig
    
    # 单变量统计信息
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
    
    # 双变量分析图表
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
        
        # 检查颜色和大小列是否存在
        if color_col and color_col not in data.columns:
            color_col = None
        if size_col and size_col not in data.columns:
            size_col = None
        
        try:
            # 根据图表类型创建不同的图表
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
                # 对于柱状图，我们需要对数据进行聚合
                if pd.api.types.is_numeric_dtype(data[y_col]):
                    # 如果Y是数值，计算每个X值的平均Y值
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
                    # 如果Y不是数值，计算每个X-Y组合的计数
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
                # 对于热力图，我们需要对数据进行聚合
                if pd.api.types.is_numeric_dtype(data[y_col]):
                    # 如果Y是数值，计算每个X值的平均Y值
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
                    # 如果Y不是数值，计算每个X-Y组合的计数
                    pivot_data = pd.crosstab(data[x_col], data[y_col])
                    fig = px.imshow(
                        pivot_data,
                        title=f"{y_col} vs {x_col} (Count)",
                        template="plotly_white"
                    )
        except Exception as e:
            # 如果出现任何错误，返回一个带有错误信息的空图表
            fig = px.scatter(title=f"Chart Generation Error: {str(e)}")
            return fig
        
        # 设置图表高度和宽度
        fig.update_layout(height=400, width=None)
        
        return fig
    
    # 双变量统计信息
    @output
    @render.ui
    def bivariate_stats():
        data = get_filtered_data()
        x_col = input.x_col()
        y_col = input.y_col()
        
        if data.empty or x_col not in data.columns or y_col not in data.columns:
            return ui.p("No data available or column")
        
        stats = []
        
        # 如果两个变量都是数值型，计算相关性
        if pd.api.types.is_numeric_dtype(data[x_col]) and pd.api.types.is_numeric_dtype(data[y_col]):
            # 计算相关系数
            pearson_corr = data[[x_col, y_col]].corr().iloc[0, 1]
            spearman_corr = data[[x_col, y_col]].corr(method='spearman').iloc[0, 1]
            
            stats.append(ui.h4(f"{x_col} and {y_col} Relationship"))
            stats.append(ui.p(f"Pearson Correlation Coefficient: {pearson_corr:.4f}"))
            stats.append(ui.p(f"Spearman Correlation Coefficient: {spearman_corr:.4f}"))
            
            # 简单的线性回归
            from sklearn.linear_model import LinearRegression
            X = data[x_col].values.reshape(-1, 1)
            y = data[y_col].values
            
            # 删除缺失值
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
        
        # 如果一个是分类变量，一个是数值变量，计算每个类别的统计信息
        elif (pd.api.types.is_numeric_dtype(data[x_col]) and not pd.api.types.is_numeric_dtype(data[y_col])) or \
             (not pd.api.types.is_numeric_dtype(data[x_col]) and pd.api.types.is_numeric_dtype(data[y_col])):
            
            # 确定哪个是分类变量，哪个是数值变量
            cat_col, num_col = (y_col, x_col) if pd.api.types.is_numeric_dtype(data[x_col]) else (x_col, y_col)
            
            stats.append(ui.h4(f"{cat_col} and {num_col} Relationship"))
            
            # 计算每个类别的统计信息
            group_stats = data.groupby(cat_col)[num_col].agg(['mean', 'median', 'std', 'count']).reset_index()
            
            # 显示每个类别的统计信息
            stats.append(ui.p("Each Category Statistics:"))
            for _, row in group_stats.iterrows():
                stats.append(ui.p(f"- {row[cat_col]}: Mean={row['mean']:.4g}, Median={row['median']:.4g}, Std={row['std']:.4g}, Count={row['count']}"))
            
            # 计算ANOVA
            from scipy import stats as scipy_stats
            
            # 准备ANOVA的数据
            groups = []
            for category in data[cat_col].unique():
                group_data = data[data[cat_col] == category][num_col].dropna()
                if len(group_data) > 0:
                    groups.append(group_data)
            
            if len(groups) > 1 and all(len(g) > 0 for g in groups):
                f_val, p_val = scipy_stats.f_oneway(*groups)
                stats.append(ui.p(f"ANOVA Test: F Value={f_val:.4g}, p Value={p_val:.4g}"))
                stats.append(ui.p(f"Conclusion: {'Categories have significant differences' if p_val < 0.05 else 'Categories have no significant differences'}"))
        
        # 如果两个都是分类变量，计算卡方检验
        else:
            # 创建列联表
            contingency_table = pd.crosstab(data[x_col], data[y_col])
            
            stats.append(ui.h4(f"{x_col} and {y_col} Relationship"))
            
            # 计算卡方检验
            from scipy import stats as scipy_stats
            
            # 确保列联表中的每个单元格都有足够的观测值
            if contingency_table.size > 0 and (contingency_table > 5).all().all():
                chi2, p, dof, expected = scipy_stats.chi2_contingency(contingency_table)
                stats.append(ui.p(f"Chi-Square Test: χ²={chi2:.4g}, p Value={p:.4g}, Degrees of Freedom={dof}"))
                stats.append(ui.p(f"Conclusion: {'Variables have significant association' if p < 0.05 else 'Variables have no significant association'}"))
            else:
                stats.append(ui.p("Cannot perform Chi-Square Test: Some cells have insufficient observations"))
        
        return ui.div(*stats)
    
    # 相关性分析图表
    @render_widget
    def correlation_plot():
        data = get_filtered_data()
        features = input.correlation_features()
        method = input.correlation_method().lower()

        # **1️⃣ Data Check: If data is empty or features are not selected**
        if data is None or data.empty or not features:
            fig = px.imshow(
                np.zeros((1,1)),  # Pass 1x1 matrix to prevent imshow() from crashing
                title="No data available or features",
                color_continuous_scale="gray"
            )
            return fig

        try:
            # **2️⃣ Check all selected features are in the data**
            valid_features = [f for f in features if f in data.columns]
            if not valid_features:
                fig = px.imshow(
                    np.zeros((1,1)),
                    title="All selected features do not exist",
                    color_continuous_scale="gray"
                )
                return fig

            # **3️⃣ Calculate Correlation Matrix**
            corr_matrix = data[valid_features].corr(method=method)

            # **4️⃣ Ensure correlation matrix is not empty**
            if corr_matrix.empty or corr_matrix.isna().all().all():
                fig = px.imshow(
                    np.zeros((1,1)),
                    title="No valid correlation data",
                    color_continuous_scale="gray"
                )
                return fig

            # **5️⃣ Create Correlation Heatmap**
            fig = ff.create_annotated_heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns.tolist(),
                y=corr_matrix.index.tolist(),
                annotation_text=np.round(corr_matrix.values, 2).astype(str),
                colorscale="RdBu_r"
            )

            # **6️⃣ Update Layout**
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
                    titleside="right",
                    thickness=15,
                    len=0.9
                )

            return fig

        except Exception as e:
            # **7️⃣ Handle Exception, Avoid imshow() Directly Crashing**
            fig = px.imshow(
                np.zeros((1,1)),
                title=f"Correlation Analysis Error: {str(e)}",
                color_continuous_scale="gray"
            )
            return fig
