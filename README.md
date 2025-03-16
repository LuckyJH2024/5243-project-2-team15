# Data Analysis and Feature Engineering Platform

A comprehensive interactive data analysis application built with Python and Shiny, providing a complete data processing workflow from data loading to feature engineering.

## Main Features

- **Data Loading**: Upload CSV, Excel, JSON, or RDS files, or use built-in sample datasets
- **Data Cleaning**: Handle missing values, detect outliers, and convert data types
- **Exploratory Data Analysis**: Perform univariate, bivariate, and multivariate analysis with visualizations
- **Feature Engineering**: Create new features, transform existing ones, and apply dimensionality reduction
- **Data Download**: Export processed data in multiple formats (CSV, Excel, JSON, RDS, TSV, Pickle)
- **User Guide**: Comprehensive documentation on how to use the application

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
cd docs
python app.py
```

The application will start at http://127.0.0.1:8001 or http://localhost:8001

## Application Structure

The application is organized into several modules, each handling a specific aspect of the data analysis workflow:

- **User Guide**: Documentation and instructions for using the application
- **Data Loading**: Upload and initial processing of datasets
- **Data Cleaning**: Tools for handling missing values, outliers, and data type conversions
- **Exploratory Analysis**: Visualization and statistical analysis tools
- **Feature Engineering**: Tools for creating and transforming features
- **Data Download**: Export functionality for processed data

## Project Structure

```
.
├── docs/                    # Main application directory
│   ├── app.py               # Main application file
│   ├── data_store.py        # Data storage module
│   ├── data_loading.py      # Data loading module
│   ├── data_cleaning.py     # Data cleaning module
│   ├── eda.py               # Exploratory data analysis module
│   ├── feature_engineering.py # Feature engineering module
│   ├── data_download.py     # Data download module
│   ├── user_guide.py        # User guide module
│   ├── README.md            # Module-specific documentation
│   └── requirements.txt     # Module-specific dependencies
├── app/                     # Legacy application directory (deprecated)
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

For more detailed information about each module and how to use the application, please refer to the User Guide tab within the application.
