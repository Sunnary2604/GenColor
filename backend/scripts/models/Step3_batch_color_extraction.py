import itertools
import subprocess

#   min_brightness, max_brightness, min saturation
COLOR_FILTER_LIST = [[0.05, 0.99, 0]]

MIN_THRESHOLD_LIST = [0]
TEST_CASE = [
    "../cases/supplemental.txt",
]

STYLE = ["clipart"]
param_combinations = itertools.product(COLOR_FILTER_LIST, MIN_THRESHOLD_LIST, TEST_CASE, STYLE)
for i, (color_filter, min_threshold, test_case, style) in enumerate(param_combinations):
    color_filter_str = ' '.join(map(str, color_filter))
    # 构建命令行参数并运行 represent_color.py
    represent_command = ["python", "represent_color.py", color_filter_str, str(min_threshold), test_case, style]
    print(represent_command)
    subprocess.run(represent_command, check=True)

    # 构建命令行参数并运行 render_color.py
    # render_command = ["python", "render_color.py", test_case, style]
    # subprocess.run(render_command, check=True)
