from shiny import ui, reactive, render
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from data_store import df_raw, df_cleaned

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
    # 使用reactive.Value来存储特征工程后的数据
    engineered_dataset = reactive.Value(pd.DataFrame())
    original_engineered_dataset = reactive.Value(pd.DataFrame())
    
    # 使用ui_trigger来触发UI更新
    ui_trigger = reactive.Value(0)

    @reactive.Effect
    def initialize_data():
        # 从df_cleaned获取数据，如果df_cleaned为None，则从df_raw获取
        data = df_cleaned.get()
        if data is None:
            data = df_raw.get()
            
        if data is not None:
            # 只保留数值列进行特征工程
            numeric_data = data.select_dtypes(include=['number'])
            if not numeric_data.empty:
                original_engineered_dataset.set(numeric_data.copy())
                engineered_dataset.set(numeric_data.copy())
                update_feature_choices()
            else:
                # 如果没有数值列，使用随机数据作为示例
                np.random.seed(42)
                df = pd.DataFrame({
                    'A': np.random.rand(100),
                    'B': np.random.rand(100),
                    'C': np.random.rand(100)
                })
                original_engineered_dataset.set(df.copy())
                engineered_dataset.set(df.copy())
                update_feature_choices()
        else:
            # 如果没有数据，使用随机数据作为示例
            np.random.seed(42)
            df = pd.DataFrame({
                'A': np.random.rand(100),
                'B': np.random.rand(100),
                'C': np.random.rand(100)
            })
            original_engineered_dataset.set(df.copy())
            engineered_dataset.set(df.copy())
            update_feature_choices()

    @reactive.Calc
    def get_current_data():
        # 使用 ui_trigger 来确保在数据更新时重新计算
        ui_trigger.get()
        return engineered_dataset.get()

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
                selected=choices[1] if len(choices) > 1 else default_selection
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
        if df is not None and not df.empty:
            return df.head(10)
        return pd.DataFrame()

    @output
    @render.text
    def data_summary():
        df = get_current_data()
        if df is not None and not df.empty:
            return (
                f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
                f"Columns: {', '.join(df.columns.tolist())}\n"
                f"Data types: {', '.join([f'{col}: {df[col].dtype}' for col in df.columns])}"
            )
        return "No data available"

    @output
    @render.plot
    def transformationPlot():
        df = get_current_data()
        if df is None or df.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "No data available", ha='center', va='center')
            ax.set_xticks([])
            ax.set_yticks([])
            return fig
            
        try:
            # 创建相关性热图
            corr_matrix = df.corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(corr_matrix, cmap='coolwarm')
            
            # 添加相关性值
            for i in range(len(corr_matrix.columns)):
                for j in range(len(corr_matrix.columns)):
                    text = ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}",
                                ha="center", va="center", color="black")
            
            # 设置坐标轴标签
            ax.set_xticks(np.arange(len(corr_matrix.columns)))
            ax.set_yticks(np.arange(len(corr_matrix.columns)))
            ax.set_xticklabels(corr_matrix.columns)
            ax.set_yticklabels(corr_matrix.columns)
            
            # 旋转x轴标签
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            # 添加标题和颜色条
            ax.set_title("Feature Correlation Heatmap")
            fig.colorbar(im)
            fig.tight_layout()
            
            return fig
        except Exception as e:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, f"Error creating plot: {str(e)}", ha='center', va='center')
            ax.set_xticks([])
            ax.set_yticks([])
            return fig

    @reactive.Effect
    @reactive.event(input.create_ratio_feature)
    def _():
        df = get_current_data()
        feature1 = input.feature1_select()
        feature2 = input.feature2_select()
        
        if df is None or df.empty or feature1 is None or feature2 is None:
            return
            
        if feature1 not in df.columns or feature2 not in df.columns:
            return
            
        try:
            # 创建比率特征
            ratio_name = f"{feature1}_div_{feature2}"
            df_new = df.copy()
            
            # 避免除以零
            df_new[ratio_name] = df_new[feature1] / df_new[feature2].replace(0, np.nan)
            
            # 更新数据集
            engineered_dataset.set(df_new)
            trigger_ui_update()
            update_feature_choices()
        except Exception as e:
            print(f"Error creating ratio feature: {str(e)}")

    @reactive.Effect
    @reactive.event(input.delete_feature)
    def _():
        df = get_current_data()
        feature = input.delete_feature_select()
        
        if df is None or df.empty or feature is None:
            return
            
        if feature not in df.columns:
            return
            
        try:
            # 删除特征
            df_new = df.drop(columns=[feature])
            
            # 更新数据集
            engineered_dataset.set(df_new)
            trigger_ui_update()
            update_feature_choices()
        except Exception as e:
            print(f"Error deleting feature: {str(e)}")

    @reactive.Effect
    @reactive.event(input.apply_transformation)
    def _():
        df = get_current_data()
        if df is None or df.empty:
            return
            
        try:
            # 应用StandardScaler转换
            scaler = StandardScaler()
            df_scaled = pd.DataFrame(
                scaler.fit_transform(df),
                columns=df.columns,
                index=df.index
            )
            
            # 更新数据集
            engineered_dataset.set(df_scaled)
            trigger_ui_update()
        except Exception as e:
            print(f"Error applying transformation: {str(e)}")

    @reactive.Effect
    @reactive.event(input.conduct_pca)
    def _():
        df = get_current_data()
        if df is None or df.empty:
            return
            
        try:
            # 应用PCA转换
            pca = PCA(n_components=2)
            pca_result = pca.fit_transform(df)
            
            # 创建PCA结果数据框
            df_pca = pd.DataFrame(
                data=pca_result,
                columns=['PCA1', 'PCA2'],
                index=df.index
            )
            
            # 更新数据集
            engineered_dataset.set(df_pca)
            trigger_ui_update()
            update_feature_choices()
        except Exception as e:
            print(f"Error conducting PCA: {str(e)}")

    @reactive.Effect
    @reactive.event(input.restore_original)
    def _():
        # 恢复原始数据集
        original_data = original_engineered_dataset.get()
        if original_data is not None:
            engineered_dataset.set(original_data.copy())
            trigger_ui_update()
            update_feature_choices()
