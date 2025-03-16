# Data Analysis and Feature Engineering Platform

A comprehensive interactive data analysis application built with Python and Shiny, providing a complete data processing workflow from data loading to feature engineering.

## Main Features

- **Data Loading**: Upload CSV, Excel, JSON, or RDS files, or use built-in sample datasets
- **Data Cleaning**: Handle missing values, detect outliers, and convert data types
- **Exploratory Data Analysis**: Perform univariate, bivariate, and multivariate analysis with visualizations
- **Feature Engineering**: Create new features, transform existing ones, and apply dimensionality reduction
- **Data Download**: Export processed data in multiple formats (CSV, Excel, JSON, RDS, TSV, Pickle)

## Quick Start

### Requirements

- Python 3.8 or higher
- Dependencies: See requirements.txt

### Installation

1. Clone or download this project
2. Create and activate a virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
python app.py
```

The application will start at http://127.0.0.1:8001 or http://localhost:8001

## User Guide

### Data Loading
- Upload your data file or select a sample dataset
- Click "Process Data" to load the data
- View data preview and summary statistics

### Data Cleaning
- Select columns to clean
- Choose cleaning operations (fill missing values, remove outliers, etc.)
- Apply cleaning operations and view the results

### Exploratory Analysis
- Perform univariate analysis: View distributions and statistics for individual variables
- Perform bivariate analysis: Explore relationships between pairs of variables
- View correlation heatmaps to understand relationships between multiple variables

### Feature Engineering
- Create new features (ratios, differences, products)
- Transform features (standardization, normalization, log transform, etc.)
- Apply batch transformations to multiple features
- Perform dimensionality reduction with PCA

### Data Download
- Select your preferred format (CSV, Excel, JSON, RDS, TSV, Pickle)
- Download the processed data for further analysis or reporting

## Project Structure

```
docs/
├── app.py                  # Main application file
├── data_store.py           # Data storage module
├── data_loading.py         # Data loading module
├── data_cleaning.py        # Data cleaning module
├── eda.py                  # Exploratory data analysis module
├── feature_engineering.py  # Feature engineering module
├── data_download.py        # Data download module
├── user_guide.py           # User guide module
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## References and Acknowledgments

This project is inspired by the functionality of [Shiny-Data-Pipeline-and-Feature-Engineering-Platform](https://wenbo0528.shinyapps.io/Shiny-Data-Pipeline-and-Feature-Engineering-Platform/) and is reimplemented using Python Shiny. 