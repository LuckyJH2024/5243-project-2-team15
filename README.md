# Feature Engineering Application

This is a Shiny application for data analysis, built with Python and Shiny.

## Setup and Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app/app.py
```

The application will be available at http://127.0.0.1:8000

## Implemented Features (in feature_engineering.py)

The feature engineering module currently implements:
- Interactive data preview with summary statistics
- Create ratio features from any two selected columns
- Delete existing features
- Apply StandardScaler transformation to selected features
- Conduct PCA analysis (2 components)
- Correlation heatmap visualization
- Restore original dataset functionality

## Project Structure and Development

```
.
├── app/
│   ├── app.py                  # Main application file
│   ├── feature_engineering.py  # Feature engineering module (implemented)
│   ├── data_cleaning.py       # Data cleaning module (to be implemented)
│   └── eda.py                # Exploratory data analysis module (to be implemented)
├── requirements.txt
└── README.md
```

## Development Guide

1. Current Implementation:
   - Feature engineering functionality is in `feature_engineering.py`
   - Uses a modular design with separate UI and server logic
   - Implements reactive data handling for real-time updates

2. To Continue Development:
   - Data Cleaning (`data_cleaning.py`): 
     * Can implement data preprocessing
     * Handle missing values
     * Remove outliers
     * Format data types
   
   - Exploratory Data Analysis (`eda.py`):
     * Add visualization tools
     * Statistical analysis
     * Distribution plots
     * Custom analysis methods

3. Adding New Features:
   - Each module can be developed independently
   - Follow the same pattern as in `feature_engineering.py`
   - Create a UI section (`module_ui`) and server function (`module_server`)
   - Add new module to main app.py

## Note

The application currently uses sample random data. To use your own dataset, modify the `initialize_data` function in `feature_engineering.py`.

## Contributing

Feel free to:
- Implement the data cleaning module
- Add EDA functionality
- Enhance existing features
- Add new feature engineering methods
- Improve visualizations

You can either follow the existing structure or implement your own approach in the designated Python files.
