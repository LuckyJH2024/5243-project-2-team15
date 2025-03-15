from shiny import ui
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import streamlit as st
import numpy as np

# UI for exploratory data analysis (EDA)
eda_ui = ui.nav_panel(
    "Exploratory Data Analysis",
    ui.output_plot("edaPlot")
)

def eda_server(input, output, session):
    # Logic for exploratory data analysis
    pass 

# Load data (df_cleaned)
st.title("Exploratory Data Analysis (EDA)")

# Dataset Filtering
st.header("Dataset Filtering")
filter_col = st.selectbox("Select column to filter", df_cleaned.columns)
unique_values = df_cleaned[filter_col].unique()
selected_values = st.multiselect("Select values to include", unique_values, default=unique_values[:5])
df_filtered = df_cleaned[df_cleaned[filter_col].isin(selected_values)]

# Display summary statistics
st.header("Dataset Summary")
st.write(df_filtered.describe())

# Select features for scatter plot
st.header("Scatter Plot Analysis")
x_col = st.selectbox("Select X-axis feature", df_filtered.columns)
y_col = st.selectbox("Select Y-axis feature", df_filtered.columns)
color_col = st.selectbox("Select color feature", [None] + list(df_filtered.columns))
size_col = st.selectbox("Select size feature", [None] + list(df_filtered.columns))
trendline_option = st.selectbox("Select trendline type", [None, "ols", "lowess"])

# Create scatter plot
fig = px.scatter(df_filtered, x=x_col, y=y_col, color=color_col, size=size_col,
                 opacity=0.6, trendline=trendline_option)
fig.update_layout(title="Scatterplot of Selected Features")
st.plotly_chart(fig)

# Display feature summaries
st.header("Feature Summaries")
st.write("**Response Feature Summary:**")
st.write(df_filtered[x_col].describe())
st.write("**Explanatory Feature Summary:**")
st.write(df_filtered[y_col].describe())

# Heatmap
st.header("Correlation Heatmap")
corr_matrix = df_filtered.corr()
heatmap_fig = ff.create_annotated_heatmap(z=corr_matrix.values,
                                          x=list(corr_matrix.columns),
                                          y=list(corr_matrix.index),
                                          annotation_text=np.round(corr_matrix.values, 2),
                                          colorscale="Viridis")
st.plotly_chart(heatmap_fig)

# Histogram
st.header("Feature Histogram")
hist_col = st.selectbox("Select a feature for histogram", df_filtered.columns)
bins = st.slider("Select number of bins", min_value=5, max_value=50, value=20)
hist_fig = px.histogram(df_filtered, x=hist_col, nbins=bins, marginal="rug", color=color_col)
hist_fig.update_layout(title=f"Histogram of {hist_col}")
st.plotly_chart(hist_fig)

# Box Plot for Outlier Detection
st.header("Box Plot Analysis")
box_col = st.selectbox("Select a feature for box plot", df_filtered.columns)
box_fig = px.box(df_filtered, y=box_col, points="all")
box_fig.update_layout(title=f"Box Plot of {box_col}")
st.plotly_chart(box_fig)

# Dynamic Insights
st.header("Dynamic Statistical Insights")
st.write(f"**Mean of {x_col}:**", df_filtered[x_col].mean())
st.write(f"**Median of {x_col}:**", df_filtered[x_col].median())
st.write(f"**Standard Deviation of {x_col}:**", df_filtered[x_col].std())
st.write(f"**Mean of {y_col}:**", df_filtered[y_col].mean())
st.write(f"**Median of {y_col}:**", df_filtered[y_col].median())
st.write(f"**Standard Deviation of {y_col}:**", df_filtered[y_col].std())
