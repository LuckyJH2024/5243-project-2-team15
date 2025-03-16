from shiny import ui, render, reactive
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
from data_store import df_cleaned

# UI Layout
eda_ui = ui.nav_panel(
    "Exploratory Data Analysis (EDA)",
    ui.layout_sidebar(
        ui.sidebar(
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
        ui.layout_columns(
            ui.card(ui.panel_title("Summary"), ui.output_table("summary")),
            ui.card(ui.output_plot("scatter_plot")),
            ui.card(ui.output_plot("heatmap")),
            ui.card(ui.output_plot("histogram")),
            ui.card(ui.output_plot("box_plot")),
            ui.card(ui.output_text("stats"))
        )
    )
)

# Server Logic
def eda_server(input, output, session):
    # 更新 UI 选择项
    @reactive.effect
    def update_ui_choices():
        data = df_cleaned.get()
        if data is None or data.empty:
            ui.update_select("filter_col", choices=[], selected=None)
            return
        
        columns = data.columns.tolist()
        first_col = columns[0] if columns else None
        second_col = columns[1] if len(columns) > 1 else first_col

        ui.update_select("filter_col", choices=columns, selected=first_col)
        ui.update_select("x_col", choices=columns, selected=first_col)
        ui.update_select("y_col", choices=columns, selected=second_col)
        ui.update_select("color_col", choices=[None] + columns, selected=None)
        ui.update_select("size_col", choices=[None] + columns, selected=None)
        ui.update_select("hist_col", choices=columns, selected=first_col)
        ui.update_select("box_col", choices=columns, selected=first_col)

    # 更新筛选值
    @reactive.effect
    @reactive.event(input.filter_col)
    def update_filter_values():
        data = df_cleaned.get()
        if data is None or input.filter_col() is None or input.filter_col() not in data.columns:
            return

        unique_values = data[input.filter_col()].dropna().unique().tolist()
        ui.update_checkbox_group("selected_values", choices=unique_values, selected=unique_values)

    # 获取当前过滤后的数据
    @reactive.calc
    def get_filtered_data():
        data = df_cleaned.get()
        if data is None or not isinstance(data, pd.DataFrame):
            return pd.DataFrame()

        if input.filter_col() and input.selected_values():
            return data[data[input.filter_col()].isin(input.selected_values())]
        return data

    # 计算数据概述
    @output
    @render.table
    def summary():
        data = get_filtered_data()
        return data.describe() if not data.empty else pd.DataFrame()

    # 绘制散点图
    @output
    @render.plot
    def scatter_plot():
        data = get_filtered_data()
        if data.empty or not input.x_col() or not input.y_col():
            return px.scatter(title="No data available")

        if input.x_col() not in data.columns or input.y_col() not in data.columns:
            return px.scatter(title="Selected columns not found")

        return px.scatter(
            data,
            x=input.x_col(),
            y=input.y_col(),
            color=None if input.color_col() == "None" else input.color_col(),
            size=None if input.size_col() == "None" else input.size_col(),
            trendline=input.trendline_option() if input.trendline_option() != "None" else None,
            title=f"{input.y_col()} vs {input.x_col()}"
        )

    # 绘制相关性热图
    @output
    @render.plot
    def heatmap():
        data = get_filtered_data()
        
        # 处理数据为空的情况
        if data is None or data.empty:
            return px.imshow(
                np.zeros((1,1)),  # 传入一个 1x1 矩阵，避免错误
                title="No data available",
                color_continuous_scale="gray"
            )

        # 选择数值型列
        numeric_data = data.select_dtypes(include=['number'])
        
        # 如果没有数值型数据，返回占位图
        if numeric_data.empty:
            return px.imshow(
                np.zeros((1,1)), 
                title="No numeric columns available",
                color_continuous_scale="gray"
            )

        # 计算相关性矩阵
        corr_matrix = numeric_data.corr()

        # 确保相关性矩阵不是空的
        if corr_matrix.empty or corr_matrix.isna().all().all():
            return px.imshow(
                np.zeros((1,1)), 
                title="No valid correlation data",
                color_continuous_scale="gray"
            )

        # 生成相关性热图
        fig = ff.create_annotated_heatmap(
            z=corr_matrix.values, 
            x=corr_matrix.columns, 
            y=corr_matrix.index, 
            annotation_text=np.round(corr_matrix.values, 2).astype(str), 
            colorscale="Viridis"
        )
        
        return fig

    # 绘制直方图
    @output
    @render.plot
    def histogram():
        data = get_filtered_data()
        if data.empty or input.hist_col() is None or input.hist_col() not in data.columns:
            return px.histogram(np.zeros(1), title="No data available")

        return px.histogram(
            data,
            x=input.hist_col(),
            nbins=input.bins(),
            color=None if input.color_col() == "None" else input.color_col(),
            title=f"Histogram of {input.hist_col()}"
        )

    # 绘制箱型图
    @output
    @render.plot
    def box_plot():
        data = get_filtered_data()
        if data.empty or input.box_col() is None or input.box_col() not in data.columns:
            return px.box(y=[0], title="No data available")

        return px.box(
            data,
            y=input.box_col(),
            points="all",
            title=f"Box Plot of {input.box_col()}"
        )

    # 统计数据
    @output
    @render.text
    def stats():
        data = get_filtered_data()
        if data.empty or not input.x_col() or input.x_col() not in data.columns:
            return "No data available for statistics"

        if not pd.api.types.is_numeric_dtype(data[input.x_col()]):
            return f"{input.x_col()} is not a numeric column"

        return (
            f"Statistics for {input.x_col()}:\n"
            f"Mean: {data[input.x_col()].mean():.4f}\n"
            f"Median: {data[input.x_col()].median():.4f}\n"
            f"Std Dev: {data[input.x_col()].std():.4f}\n"
            f"Min: {data[input.x_col()].min():.4f}\n"
            f"Max: {data[input.x_col()].max():.4f}"
        )
