from shiny import ui, reactive, render

# User Guide UI
user_guide_ui = ui.nav_panel(
    "User Guide",
    ui.card(
        ui.card_header(ui.h2("Data Explorer & Comparison Tool - User Guide")),
        ui.card_body(
            ui.h3("Overview"),
            ui.p("This web application is designed to provide an interactive and user-friendly platform for data analysis, enabling users to seamlessly upload, clean, preprocess, engineer features, and explore datasets. The app simplifies data handling and visualization for data scientists and analysts."),
            
            ui.h3("Key Features"),
            ui.tags.ul(
                ui.tags.li(ui.tags.b("Data Upload:"), " Support for CSV, Excel, JSON, and RDS files"),
                ui.tags.li(ui.tags.b("Data Cleaning:"), " Remove duplicates, handle missing values, outliers, normalize/standardize, encode categorical variables, and convert numeric-like columns"),
                ui.tags.li(ui.tags.b("Feature Engineering:"), " Apply mathematical transformations, create custom columns, and rename columns"),
                ui.tags.li(ui.tags.b("Exploratory Data Analysis:"), " Generate interactive histograms, boxplots, bar charts, scatter plots, and correlation heatmaps"),
                ui.tags.li(ui.tags.b("Download:"), " Export the cleaned data in various formats"),
                ui.tags.li(ui.tags.b("Responsive Interface:"), " User-friendly interface for smooth data exploration")
            ),
            
            ui.h3("Navigation"),
            ui.p("Use the tabs at the top to navigate between different sections of the application:"),
            ui.tags.ol(
                ui.tags.li(ui.tags.b("User Guide:"), " This page - provides instructions on how to use the application"),
                ui.tags.li(ui.tags.b("Data Upload:"), " Upload your data files or use sample datasets"),
                ui.tags.li(ui.tags.b("Data Cleaning:"), " Clean and preprocess your data"),
                ui.tags.li(ui.tags.b("Exploratory Analysis:"), " Explore and visualize your data"),
                ui.tags.li(ui.tags.b("Feature Engineering:"), " Create and transform features"),
                ui.tags.li(ui.tags.b("Data Download:"), " Export your processed data in various formats")
            ),
            
            ui.h3("Detailed Instructions"),
            
            # Data Upload Section
            ui.h4("1. Data Upload"),
            ui.p("This section allows you to upload your data files or use sample datasets."),
            ui.tags.ul(
                ui.tags.li(ui.tags.b("Upload Files:"), " Click 'Browse Files' to select a file from your computer. Supported formats include CSV, Excel, JSON, and RDS."),
                ui.tags.li(ui.tags.b("Process Data:"), " After selecting a file, click 'Process Data' to load it into the application."),
                ui.tags.li(ui.tags.b("Sample Datasets:"), " If you don't have your own data, you can use one of the provided sample datasets (Iris, Boston Housing, or Wine)."),
                ui.tags.li(ui.tags.b("Data Preview:"), " Once loaded, you can preview your data, view summary statistics, and check data types.")
            ),
            
            # Data Cleaning Section
            ui.h4("2. Data Cleaning"),
            ui.p("This section helps you clean and preprocess your data."),
            ui.tags.ul(
                ui.tags.li(ui.tags.b("Select Column:"), " Choose a column from your dataset to clean."),
                ui.tags.li(ui.tags.b("Cleaning Operations:"), " Select from various cleaning operations:"),
                ui.tags.ul(
                    ui.tags.li(ui.tags.i("Fill Missing Values:"), " Fill missing values using mean, median, mode, fixed value, forward fill, or backward fill."),
                    ui.tags.li(ui.tags.i("Remove Missing Values:"), " Remove rows with missing values in the selected column."),
                    ui.tags.li(ui.tags.i("Remove Outliers:"), " Remove outliers based on standard deviation threshold."),
                    ui.tags.li(ui.tags.i("Convert to Numeric:"), " Convert text columns to numeric type."),
                    ui.tags.li(ui.tags.i("Standardize Text:"), " Standardize text by converting to lowercase and trimming whitespace."),
                    ui.tags.li(ui.tags.i("One-Hot Encoding:"), " Convert categorical variables into binary columns.")
                ),
                ui.tags.li(ui.tags.b("Apply Cleaning:"), " Click 'Apply Cleaning' to execute the selected operation."),
                ui.tags.li(ui.tags.b("Reset Data:"), " Click 'Reset Data' to revert to the original data."),
                ui.tags.li(ui.tags.b("Column Information:"), " View distribution and statistics for the selected column."),
                ui.tags.li(ui.tags.b("Cleaning Suggestions:"), " The application provides suggestions for cleaning based on the column's characteristics.")
            ),
            
            # Exploratory Analysis Section
            ui.h4("3. Exploratory Analysis"),
            ui.p("This section allows you to explore and visualize your data."),
            ui.tags.ul(
                ui.tags.li(ui.tags.b("Data Filtering:"), " Filter your data based on column values."),
                ui.tags.li(ui.tags.b("Univariate Analysis:"), " Analyze a single variable:"),
                ui.tags.ul(
                    ui.tags.li("Select a column and choose from histogram, boxplot, violin plot, or density plot."),
                    ui.tags.li("Adjust parameters like bin size for histograms."),
                    ui.tags.li("View detailed statistics for the selected variable.")
                ),
                ui.tags.li(ui.tags.b("Bivariate Analysis:"), " Analyze relationships between two variables:"),
                ui.tags.ul(
                    ui.tags.li("Select X and Y variables, with optional color and size variables."),
                    ui.tags.li("Choose from scatter plot, line plot, bar chart, or heatmap."),
                    ui.tags.li("Add trendlines (linear regression or LOWESS)."),
                    ui.tags.li("View statistical relationships between the variables.")
                ),
                ui.tags.li(ui.tags.b("Correlation Analysis:"), " Analyze correlations between multiple numeric variables:"),
                ui.tags.ul(
                    ui.tags.li("Select features for correlation analysis."),
                    ui.tags.li("Choose correlation method (Pearson, Spearman, or Kendall)."),
                    ui.tags.li("View correlation heatmap with values.")
                )
            ),
            
            # Feature Engineering Section
            ui.h4("4. Feature Engineering"),
            ui.p("This section helps you create and transform features."),
            ui.tags.ul(
                ui.tags.li(ui.tags.b("Feature Creation:"), " Create new features based on existing ones:"),
                ui.tags.ul(
                    ui.tags.li("Enter a name for the new feature."),
                    ui.tags.li("Write a Python expression using column names as variables."),
                    ui.tags.li("Click 'Create Feature' to add the new feature to your dataset.")
                ),
                ui.tags.li(ui.tags.b("Feature Transformation:"), " Apply transformations to existing features:"),
                ui.tags.ul(
                    ui.tags.li("Select a column to transform."),
                    ui.tags.li("Choose from various transformations (log, square root, standardization, normalization, etc.)."),
                    ui.tags.li("Click 'Apply Transformation' to transform the feature.")
                ),
                ui.tags.li(ui.tags.b("Feature Selection:"), " Select important features for your analysis:"),
                ui.tags.ul(
                    ui.tags.li("Choose a target variable."),
                    ui.tags.li("Select a feature selection method."),
                    ui.tags.li("Specify the number of features to select."),
                    ui.tags.li("View feature importance scores and visualizations.")
                )
            ),
            
            # Data Download Section
            ui.h4("5. Data Download"),
            ui.p("This section allows you to export your processed data in various formats."),
            ui.tags.ul(
                ui.tags.li(ui.tags.b("Data Status:"), " Check the status of your data before downloading."),
                ui.tags.li(ui.tags.b("Download Formats:"), " Choose from various download formats:"),
                ui.tags.ul(
                    ui.tags.li(ui.tags.i("CSV Format:"), " Comma-separated values file, suitable for most data analysis tools and spreadsheet software."),
                    ui.tags.li(ui.tags.i("Excel Format:"), " Microsoft Excel file, suitable for spreadsheet software."),
                    ui.tags.li(ui.tags.i("JSON Format:"), " JavaScript Object Notation file, suitable for web applications and APIs."),
                    ui.tags.li(ui.tags.i("RDS Format:"), " R Data Storage format, suitable for R language analysis."),
                    ui.tags.li(ui.tags.i("TSV Format:"), " Tab-separated values file, suitable for text processing and specific analysis tools."),
                    ui.tags.li(ui.tags.i("Pickle Format:"), " Python serialization format, suitable for Python data analysis.")
                ),
                ui.tags.li(ui.tags.b("Download Options:"), " Configure options for each format:"),
                ui.tags.ul(
                    ui.tags.li("Include row index in CSV, Excel, and TSV formats."),
                    ui.tags.li("Select JSON orientation type."),
                    ui.tags.li("Choose Pickle protocol version.")
                ),
                ui.tags.li(ui.tags.b("Download Buttons:"), " Click the respective download button to export your data in the selected format.")
            ),
            
            ui.h3("Tips and Best Practices"),
            ui.tags.ul(
                ui.tags.li("Start by uploading your data and exploring it to understand its structure and quality."),
                ui.tags.li("Clean your data to handle missing values, outliers, and inconsistencies before analysis."),
                ui.tags.li("Use exploratory analysis to identify patterns, relationships, and potential insights."),
                ui.tags.li("Create new features to enhance your analysis and improve model performance."),
                ui.tags.li("Export your processed data for further analysis or reporting.")
            ),
            
            ui.h3("Troubleshooting"),
            ui.tags.ul(
                ui.tags.li(ui.tags.b("File Upload Issues:"), " Ensure your file is in a supported format (CSV, Excel, JSON, RDS) and is not corrupted."),
                ui.tags.li(ui.tags.b("Data Processing Errors:"), " Check error messages for specific issues with your data."),
                ui.tags.li(ui.tags.b("Visualization Problems:"), " Some visualizations may not work well with certain data types or large datasets."),
                ui.tags.li(ui.tags.b("Feature Engineering Errors:"), " Ensure your Python expressions are valid and reference existing column names."),
                ui.tags.li(ui.tags.b("Download Issues:"), " Make sure you have processed data before attempting to download.")
            )
        ),
        ui.card_footer(
            ui.p("For more information or assistance, please contact the development team.")
        )
    )
)

def user_guide_server(input, output, session):
    # No server-side logic needed for the user guide
    pass 