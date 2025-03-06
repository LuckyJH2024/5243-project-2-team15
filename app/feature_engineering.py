from shiny import ui, reactive, render
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# UI for feature engineering
feature_engineering_ui = ui.nav_panel(
    "Feature Engineering",
    ui.row(
        ui.column(4,
            ui.panel_well(
                ui.h4("Feature Selection"),
                ui.input_select("feature1_select", "Select Feature 1", choices=[]),
                ui.input_select("feature2_select", "Select Feature 2", choices=[]),
                ui.input_action_button("create_ratio_feature", "Create Ratio Feature"),
                ui.br(),
                ui.br(),
                ui.input_select("delete_feature_select", "Select Feature to Delete", choices=[]),
                ui.input_action_button("delete_feature", "Delete Feature"),
            )
        ),
        ui.column(8,
            ui.panel_well(
                ui.h4("Data Preview"),
                ui.output_text("data_summary"),
                ui.output_table("featureEngineeredTable"),
            )
        )
    ),
    ui.row(
        ui.column(12,
            ui.panel_well(
                ui.h4("Feature Engineering Tools"),
                ui.input_action_button("apply_transformation", "Apply Transformation"),
                ui.input_action_button("conduct_pca", "Conduct PCA"),
                ui.input_action_button("restore_original", "Restore Original Dataset"),
                ui.output_plot("transformationPlot")
            )
        )
    )
)

def feature_engineering_server(input, output, session):
    original_dataset = reactive.Value(pd.DataFrame())
    dataset = reactive.Value(pd.DataFrame())

    @reactive.Effect
    def initialize_data():
        np.random.seed(42)
        df = pd.DataFrame({
            'A': np.random.rand(100),
            'B': np.random.rand(100),
            'C': np.random.rand(100)
        })
        
        original_dataset.set(df.copy())
        dataset.set(df.copy())
        
        choices = df.columns.tolist()
        try:
            ui.update_select(
                id="feature1_select",
                choices=choices,
                selected=choices[0]
            )
            ui.update_select(
                id="feature2_select",
                choices=choices,
                selected=choices[1]
            )
            ui.update_select(
                id="delete_feature_select",
                choices=choices,
                selected=choices[0]
            )
        except Exception as e:
            print(f"Error setting initial choices: {str(e)}")

    # 使用 reactive.Value 来触发UI更新
    ui_trigger = reactive.Value(0)

    @reactive.Calc
    def get_current_data():
        # 使用 ui_trigger 来确保在数据更新时重新计算
        ui_trigger.get()
        return dataset.get()

    def update_feature_choices():
        df = get_current_data()
        choices = df.columns.tolist()
        default_selection = choices[0] if choices else None

        try:
            ui.update_select(
                id="feature1_select",
                choices=choices,
                selected=default_selection
            )
            ui.update_select(
                id="feature2_select",
                choices=choices,
                selected=default_selection if len(choices) > 1 else None
            )
            ui.update_select(
                id="delete_feature_select",
                choices=choices,
                selected=default_selection
            )
        except Exception as e:
            print(f"Error updating feature choices: {str(e)}")

    def trigger_ui_update():
        # 增加触发器的值来强制UI更新
        ui_trigger.set(ui_trigger.get() + 1)

    @output
    @render.table
    def featureEngineeredTable():
        df = get_current_data()
        if df.empty:
            return pd.DataFrame(columns=["No data available"])
        return df.head(10).round(4)

    @output
    @render.text
    def data_summary():
        df = get_current_data()
        if df.empty:
            return "No data available"

        summary = [
            f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns",
            f"Features: {', '.join(df.columns)}",
            f"Missing Values: {df.isnull().sum().sum()}"
        ]

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary.append("<br><b>Numerical Features Summary:</b>")
            stats = df[numeric_cols].describe().round(2)
            for col in stats.columns:
                summary.extend([
                    f"<br><b>{col}</b>:",
                    f" Mean: {stats.at['mean', col]}",
                    f" Std: {stats.at['std', col]}",
                    f" Min: {stats.at['min', col]}",
                    f" Max: {stats.at['max', col]}"
                ])

        return "<br>".join(summary)

    @output
    @render.plot
    def transformationPlot():
        df = get_current_data()
        if df.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            return fig

        fig, ax = plt.subplots(figsize=(10, 8))
        if 'PC1' in df.columns and 'PC2' in df.columns:
            ax.scatter(df['PC1'], df['PC2'], alpha=0.5)
            ax.set_title('PCA Result')
            ax.set_xlabel('PC1')
            ax.set_ylabel('PC2')
        else:
            corr = df.corr()
            cax = ax.matshow(corr, cmap='coolwarm')
            fig.colorbar(cax)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=45, ha='right')
            ax.set_yticks(range(len(corr.columns)))
            ax.set_yticklabels(corr.columns)
            ax.set_title('Feature Correlation Heatmap')
            plt.tight_layout()

        return fig

    @reactive.Effect
    @reactive.event(input.create_ratio_feature)
    def _():
        df = dataset.get()
        feature1 = input.feature1_select()
        feature2 = input.feature2_select()
        
        if not feature1 or not feature2:
            ui.notification_show("Please select both features", type="warning")
            return
        
        if feature1 == feature2:
            ui.notification_show("Please select different features", type="warning")
            return
        
        try:
            new_feature_name = f'{feature1}_{feature2}_Ratio'
            df = df.copy()
            df[new_feature_name] = df[feature1] / df[feature2]
            dataset.set(df)
            trigger_ui_update()
            update_feature_choices()
            ui.notification_show(f"Created new feature: {new_feature_name}", type="message")
        except Exception as e:
            ui.notification_show(f"Error creating ratio: {str(e)}", type="error")

    @reactive.Effect
    @reactive.event(input.delete_feature)
    def _():
        df = dataset.get()
        feature_to_delete = input.delete_feature_select()
        if feature_to_delete in df.columns:
            df = df.drop(columns=[feature_to_delete])
            dataset.set(df)
            trigger_ui_update()
            update_feature_choices()
            ui.notification_show(f"Deleted feature: {feature_to_delete}", type="message")

    @reactive.Effect
    @reactive.event(input.apply_transformation)
    def _():
        df = dataset.get()
        feature = input.feature1_select()
        if feature in df.columns:
            scaler = StandardScaler()
            df = df.copy()
            df[feature] = scaler.fit_transform(df[[feature]])
            dataset.set(df)
            trigger_ui_update()
            ui.notification_show(f"Applied StandardScaler to {feature}", type="message")

    @reactive.Effect
    @reactive.event(input.conduct_pca)
    def _():
        df = dataset.get()
        if not df.empty and len(df.columns) >= 2:
            try:
                pca = PCA(n_components=2)
                components = pca.fit_transform(df.select_dtypes(include=[np.number]))
                df_pca = pd.DataFrame(components, columns=['PC1', 'PC2'])
                dataset.set(df_pca)
                trigger_ui_update()
                update_feature_choices()
                ui.notification_show("PCA applied successfully", type="message")
            except Exception as e:
                ui.notification_show(f"PCA failed: {str(e)}", type="error")
        else:
            ui.notification_show("Not enough numerical features for PCA", type="warning")

    @reactive.Effect
    @reactive.event(input.restore_original)
    def _():
        dataset.set(original_dataset.get().copy())
        trigger_ui_update()
        update_feature_choices()
        ui.notification_show("Dataset restored to original", type="message")
