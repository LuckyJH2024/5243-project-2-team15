from shiny import ui
import pandas as pd
import plotly.express as px
import streamlit as st

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

# Display summary statistics
st.header("Dataset Summary")
st.write(df_cleaned.describe())

# Select features for scatter plot
st.header("Scatter Plot Analysis")
x_col = st.selectbox("Select X-axis feature", df_cleaned.columns)
y_col = st.selectbox("Select Y-axis feature", df_cleaned.columns)
add_marginal = st.checkbox("Add Marginal Distributions")
add_lm = st.checkbox("Add Linear Regression Line")

# Create scatter plot
fig = px.scatter(df_cleaned, x=x_col, y=y_col, opacity=0.6, trendline="ols" if add_lm else None,
                 marginal_x="histogram" if add_marginal else None,
                 marginal_y="histogram" if add_marginal else None)
fig.update_layout(title="Scatterplot of Selected Features")
st.plotly_chart(fig)

# Display feature summaries
st.header("Feature Summaries")
st.write("**Response Feature Summary:**")
st.write(df_cleaned[x_col].describe())
st.write("**Explanatory Feature Summary:**")
st.write(df_cleaned[y_col].describe())

