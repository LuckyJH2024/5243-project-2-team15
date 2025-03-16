from shiny import reactive

# 原始数据
df_raw = reactive.Value(None)

# 清洗后的数据
df_cleaned = reactive.Value(None)

# 特征工程后的数据
df_engineered = reactive.Value(None)

# 错误信息
error_store = reactive.Value("")

# 当前选择的模型
selected_model = reactive.Value(None)

# 模型评估结果
model_results = reactive.Value(None) 