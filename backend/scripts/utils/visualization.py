import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from jinja2 import Environment, FileSystemLoader 
import os
import time
import json
import colorsys

CURRENT_TIME = time.strftime(
    '%Y%m%d_%H_%M_%S', time.localtime(int(time.time())))
print(CURRENT_TIME)

#OUTPUT_PARENT_PATH = rf'E:\Test\Testoutput\{CURRENT_TIME}'
#PALETTE_PARENT_DIR = r"E:\Test\Testoutput\palette_12_12"


def plot_hsv_matrix(data, save_path):
    assert data.shape[-1] == 3
    data_df = pd.DataFrame(data, columns=["hue", "saturation", "value"])
    print("The DataFrame generated from the NumPy array is:")
    sns.set_theme(style="ticks")
    sns.pairplot(data_df)
    plt.savefig(save_path)
    print(data_df)



def plot_hue(hue_list, save_dir, base_filename):
    os.makedirs(save_dir, exist_ok=True)
    counts, _ = np.histogram(hue_list, range=(0, 180), bins=60, density=False)
    counts_string = ','.join(map(str, counts))
    
    # 设定 Jinja2 环境，确保模板文件路径正确
    env = Environment(loader=FileSystemLoader('E:\Test\Testcode\GroundSAM\Grounded-Segment-Anything\semantic-color-code-main\scripts\static'))
    template = env.get_template('template.html')  # 确保这里的 'template.html' 是存在的

    # 创建 HTML 文件的完整路径
    html_save_path = os.path.join(save_dir, f"{base_filename}_hue.html")
    with open(html_save_path, 'w+') as fout:
        # 渲染模板并写入文件
        html_content = template.render(data=counts_string)
        fout.write(html_content)

    print(f"Generated HTML at {html_save_path}")  # 打印生成的文件位置，帮助调试




def batch_plot_hue(prompts, src_dir, save_dir):
    for prompt in prompts:
        palette_dir = os.path.join(src_dir)  # 使用os.path.join确保路径正确
        if not os.path.isdir(palette_dir):  # 检查路径是否存在
            print(f"Directory {palette_dir} does not exist. Skipping.")
            continue

        for file_name in os.listdir(palette_dir):  # 遍历目录
            if file_name.endswith("_hsv_values.npy"):  # 查找以_hsv_values.npy结尾的文件
                hsv_file_path = os.path.join(palette_dir, file_name)

                # 加载HSV值
                hsv_points_list = np.load(hsv_file_path)
                hue_list = hsv_points_list[:, 0]

                # 用于保存的文件名基于当前HSV文件的名称
                base_filename = os.path.splitext(file_name)[0]
                hsv_matrix_save_path = os.path.join(palette_dir, f"{base_filename}_hsv_matrix.png")
                hue_save_dir = os.path.join(save_dir, prompt)

                # 绘制并保存HSV矩阵和色相图像
                plot_hsv_matrix(data=hsv_points_list, save_path=hsv_matrix_save_path)
                plot_hue(hue_list, save_dir=hue_save_dir, base_filename=base_filename)

def histogram(datapath, save_path, prompt):
 

    # JSON 数据 (通常你会从文件中读取)
    json_data = None
    with open(datapath, 'r') as f:
        json_data = f.read()
    # 解析 JSON 数据
    data = json.loads(json_data)

    # 提取 RGB 颜色和他们的出现次数
    colors = []
    frequencies = []
    for color, freq in data.items():
        rgb = tuple(map(float, color.split(',')))
        hsv = colorsys.rgb_to_hsv(*rgb)
        colors.append((rgb, hsv))
        frequencies.append(freq)

    # 按照 hue 排序
    sorted_colors = sorted(colors, key=lambda x: x[1][0])
    sorted_frequencies = [frequencies[colors.index(color)] for color in sorted_colors]
    sorted_rgb_colors = [color[0] for color in sorted_colors]

    # 创建一个新的 Figure
    plt.figure(figsize=(8, 4))

    # 生成条形图
    bars = plt.bar(range(len(sorted_frequencies)), sorted_frequencies, color=sorted_rgb_colors)

    # 设置 x 轴的刻度和标签
    # plt.xticks(range(len(sorted_frequencies)), [f'Color {i+1}' for i in range(len(sorted_frequencies))], rotation=90)
    # hide x and y tick
    plt.xticks([])
    plt.yticks([])
    # 添加标题和标签
    plt.title(prompt)
    plt.xlabel('Color')
    plt.ylabel('Frequency')

    # 显示图表
    plt.tight_layout()
    # save the histogram as svg
    plt.savefig(save_path)
    plt.close()


def batch_histogram(prompts, datapath):
    for prompt in prompts:
        prompt_dir = os.path.join(datapath, prompt)
        if not os.path.isdir(prompt_dir):
            print(f"Directory {prompt_dir} does not exist. Skipping.")
            continue
        save_dir = os.path.join(datapath, prompt)

        summary_path = os.path.join(prompt_dir, "summary.json")
        histogram(summary_path, save_dir, prompt)

# main
if __name__ == "__main__":
    # prompts = [
    # "apple", "red_apple",
    # "avocado", "blueberry", "cantaloupe", "grapefruit", "honeydew", "lemon", "lime", "mango", "orange", "raspberry", "strawberry", "watermelon",
    # "apple", "banana", "cherry", "grape", "peach",
    # "carrot", "celery", "corn", "eggplant", "mushroom"]
    base_dir="../../output-color/Case1"
    prompts = os.listdir(base_dir)
    # remove .DS_Store
    if '.DS_Store' in prompts:
        prompts.remove('.DS_Store')
    print(prompts)
    # prompts = ["apple"]
    batch_histogram(prompts, base_dir)
