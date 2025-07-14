import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import ast

# 将字符串转换为RGB格式
def convert_to_rgb(color_str):
    color_tuple = ast.literal_eval(color_str)
    return tuple([c / 255.0 for c in color_tuple])

# 加载CSV文件
file_path = "/Users/sunnary/Github/semantic-color-code/frontend/public/all.csv"
df = pd.read_csv(file_path)


# 风格到列的映射
style_to_column = {
    'design': 'D',
    'photo': 'AP',
    'clipart': 'AC'
}

# 固定色块大小，自动调整图片尺寸
rect_size = 1  # 色块大小固定
spacing = 0.2  # 色块之间的水平间隔
vertical_spacing = 0.2  # 色块上下的额外间隔

concept_count = len(df['concept'].unique())

# 不限制图片高度，Matplotlib 会自动调整
fig, ax = plt.subplots(figsize=(8, concept_count * (rect_size + vertical_spacing) / 2))

# 设置网格布局
rows = df['concept'].unique()
columns = ['D', 'AP', 'AC']

# 绘制彩色方块
for i, concept in enumerate(rows):
    for j, style in enumerate(columns):
        color_value = df[(df['concept'] == concept) & (df['style'] == list(style_to_column.keys())[j])]['color_dominant'].values
        if color_value:
            rgb_color = convert_to_rgb(color_value[0])
            x_position = j * (rect_size + spacing)  # 水平方向的位置
            y_position = i * (rect_size + vertical_spacing)  # 垂直方向的位置（从上往下绘制）
            ax.add_patch(mpatches.Rectangle((x_position, y_position), rect_size, rect_size, color=rgb_color))

# 设置轴的限制
ax.set_xlim(-spacing, len(columns) * (rect_size + spacing) - spacing)
ax.set_ylim(-vertical_spacing, concept_count * (rect_size + vertical_spacing))
ax.set_aspect('equal')  # 保持方块为正方形

# 设置刻度和标签
ax.set_xticks([rect_size / 2 + i * (rect_size + spacing) for i in range(len(columns))])
ax.set_xticklabels(columns, fontsize=12)
ax.set_yticks([rect_size / 2 + i * (rect_size + vertical_spacing) for i in range(concept_count)])
ax.set_yticklabels(rows, fontsize=10, ha='right')

# 移除刻度线
ax.tick_params(axis='both', which='both', length=0)

# 移动D AP AC标签到图形上方
ax.xaxis.tick_top()

# 隐藏网格线和轴线
ax.grid(False)
ax.spines[:].set_visible(False)

# 保存为SVG格式
output_file = r'/Users/sunnary/Github/semantic-color-code/frontend/public/output.svg'
plt.savefig(output_file, format='svg')

# 显示绘图
plt.show()


