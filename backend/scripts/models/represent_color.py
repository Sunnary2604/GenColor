import numpy as np
from PIL import Image
import multiprocessing
import matplotlib.pyplot as plt
import os
import time
import sys
import json
from skimage.color import rgb2hsv, rgb2lab, lab2rgb
from pathlib import Path
import argparse
import warnings
from pyciede2000 import ciede2000
import csv
import math

warnings.filterwarnings("ignore")

COLOR_FILTERS = []
MIN_THRESHOLD = None
TEST_CASE = None
COLOR_NUM = 1

# 获取项目根目录的路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(project_root)


def color_filter(colors, COLOR_FILTERS, img_path, save_path):
    bins = {}
    min_brightness = COLOR_FILTERS[0]
    max_brightness = COLOR_FILTERS[1]
    min_saturation = COLOR_FILTERS[2]

    for count, pixel in colors:
        h, s, v = rgb2hsv(np.array([pixel[0] / 255, pixel[1] / 255, pixel[2] / 255]).reshape(1, 1, 3))[0, 0, :]
        l, _, _ = rgb2lab(np.array([pixel[0] / 255, pixel[1] / 255, pixel[2] / 255]).reshape(1, 1, 3))[0, 0, :] / 100

        # remove black and white

        # if v < min_brightness:
        #     continue
        if l > max_brightness:
            continue
        if l <= min_brightness:
            continue

        bins[pixel] = count
    return bins


def color_extraction_with_filter(img_path, COLOR_FILTERS, save_path):
    image = Image.open(img_path)
    image = remove_alpha_channel(image, thumbnail=True)

    colors = image.getcolors(100 * 100) or []  # 获取图像中所有颜色
    filtered_colors = color_filter(colors, COLOR_FILTERS, img_path, save_path)

    return filtered_colors


def find_representative_colors(rgb_points_list, color_num, save_path=None, img_path=None, type=None, id=None, center=None):
    if save_path is not None:
        bins, bin_size, channels, dataArray, K, bin_range = init_palette(rgb_points_list, color_num + 1, 8)
        calculate_palette(dataArray, bins, bin_size, channels)

        return save_palette(bins, bin_range, save_path, img_path, type=type, id=id)
    bins, bin_size, channels, dataArray, K, bin_range = init_palette(rgb_points_list, color_num + 1, 16)
    calculate_palette(dataArray, bins, bin_size, channels)

    colors_with_counts = kmeans(bins, bin_range, K, center=center)
    return colors_with_counts


def save_palette(bins, bin_range, save_path, img_path, type=None, id=None):
    # save color to histogram
    color_with_count = []
    bin_size = 256 / bin_range

    for i in range(bin_range):
        for j in range(bin_range):
            for k in range(bin_range):
                tmp = bins[f'r{i}g{j}b{k}']

                if tmp['color'][0] <= 16 and tmp['color'][1] <= 16 and tmp['color'][2] <= 16:
                    continue
                if tmp['color'][0] >= 240 and tmp['color'][1] >= 240 and tmp['color'][2] >= 240:
                    # print(tmp['color'][0])
                    continue
                color_with_count.append((tmp['color'], tmp['count']))
    # # remove black if all <16
    # print(tmp['color'])
    # color_with_count = [x for x in color_with_count if (x[0][0] > 16 and x[0][1] > 16 and x[0][2] > 16)]
    # # >240
    # color_with_count = [x for x in color_with_count if (x[0][0] < 248 and x[0][1] < 248 and x[0][2] < 248)]
    color_with_count.sort(key=lambda x: x[1], reverse=True)

    color_with_count = color_with_count[:20]
    # # 对于每个颜色，计算颜色距离，如果小于阈值，则合并
    # for i in range(len(color_with_count)):
    #      color_with_count = [x for x in color_with_count if x[1] > 0]
    #     for j in range(i + 1, len(color_with_count)):

    #         c1 = (color_with_count[j][0][0], color_with_count[j][0][1], color_with_count[j][0][2]), color_with_count[j][1]
    #         c2 = (color_with_count[i][0][0], color_with_count[i][0][1], color_with_count[i][0][2]), color_with_count[i][1]

    #         distance = ciede2000(rgb2lab(np.uint8([[c1[0]]]))[0][0], rgb2lab(np.uint8([[c2[0]]]))[0][0])["delta_E_00"]
    #         if distance < 6:

    #             merge_color = ((color_with_count[i][0][0] + color_with_count[j][0][0]) / 2, (color_with_count[i][0][1] + color_with_count[j][0][1]) / 2,
    #                            (color_with_count[i][0][2] + color_with_count[j][0][2]) / 2)
    #             color_with_count[j] = (merge_color, color_with_count[i][1] + color_with_count[j][1])
    #             color_with_count[i] = ((0, 0, 0), 0)
    # delete i

    # color_with_count.sort(key=lambda x: x[1], reverse=True)
    color = np.array([x[0] for x in color_with_count])
    count = np.array([x[1] for x in color_with_count])

    # draw bar chart
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(color)), count, color=color / 255)
    plt.xlabel("Color")
    plt.ylabel("Count")
    if type == None:

        p = os.path.join(save_path, os.path.basename(img_path).split('.')[0] + "_hist.png")
    else:
        p = os.path.join(save_path, id + "_overall_hist.png")
    plt.savefig(p)
    # return the top color_num colors, in thr format of original bins
    return color_with_count[:1]


def init_palette(img, K, bin_range):
    bins = {}
    bin_size = 256 / bin_range
    channels = 3
    dataArray = img.flatten()
    for i in range(bin_range):
        for j in range(bin_range):
            for k in range(bin_range):
                color = [(i + 0.5) * bin_size, (j + 0.5) * bin_size, (k + 0.5) * bin_size]
                lab = rgb2lab(np.uint8([[color]]))[0][0]
                bins[f'r{i}g{j}b{k}'] = {'color': color, 'count': 0, 'idx': -1, 'Lab': lab}
    return bins, bin_size, channels, dataArray, K, bin_range


def calculate_palette(dataArray, bins, bin_size, channels):
    l = len(dataArray)
    for i in range(0, l, channels):
        R = dataArray[i]
        G = dataArray[i + 1]
        B = dataArray[i + 2]
        ri = int(R // bin_size)
        gi = int(G // bin_size)
        bi = int(B // bin_size)
        bins[f'r{ri}g{gi}b{bi}']['count'] += 1


def kmeans_first(bins, bin_size, K, center=None):
    centers = [[0, 0, 0]]
    if center is not None:
        centers = [center]
    #black as the first center [bin_size / 2, bin_size / 2, bin_size / 2], [255 - bin_size / 2, 255 - bin_size / 2, 255 - bin_size / 2]
    centers_lab = [rgb2lab(np.uint8([[centers[0]]]))[0][0]]
    bins_copy = {i: bins[i]['count'] for i in bins}

    for p in range(K):
        tmp = None
        maxc = -1
        for i in bins_copy:
            # filter out low count colors
            d2 = distance2(bins[i]['Lab'], centers_lab[p])
            factor = 1 - np.exp(-d2 / 6400)  # sigma_a:80
            bins_copy[i] *= factor
            if bins_copy[i] > maxc:
                maxc = bins_copy[i]
                tmp = bins[i]['color'][:]
        centers.append(tmp)
        centers_lab.append(rgb2lab(np.uint8([[tmp]]))[0][0])

    return centers_lab


def kmeans(bins, bin_range, K, center=None):
    centers = kmeans_first(bins, 256 / bin_range, K, center=center)
    no_change = False
    while not no_change:
        no_change = True
        sum_bins = [{'color': [0, 0, 0], 'count': 0} for _ in range(K + 1)]
        for i in range(bin_range):
            for j in range(bin_range):
                for k in range(bin_range):
                    tmp = bins[f'r{i}g{j}b{k}']
                    lab = tmp['Lab']
                    mind = float('inf')
                    mini = -1
                    for p in range(K + 1):
                        d = distance2(centers[p], lab)
                        if mind > d:
                            mind = d
                            mini = p
                    if mini != tmp['idx']:
                        tmp['idx'] = mini
                        no_change = False
                    m = sca_mul(tmp['Lab'], tmp['count'])
                    sum_bins[mini]['color'] = add(sum_bins[mini]['color'], m)
                    sum_bins[mini]['count'] += tmp['count']
        for i in range(1, K + 1):
            if sum_bins[i]['count']:
                for j in range(3):
                    centers[i][j] = sum_bins[i]['color'][j] / sum_bins[i]['count']

    centers = np.array(centers).reshape(-1, 1, 3)
    lab_colors = [(centers[i].tolist(), sum_bins[i]['count']) for i in range(len(centers))]
    lab_colors_sorted = sorted(lab_colors, key=lambda x: x[0][0])
    # 去除黑色
    lab_colors_sorted = lab_colors_sorted[1:]
    # 去除白色
    # lab_colors_sorted = lab_colors_sorted[:-1]
    rgb_colors = [((lab2rgb(np.array(color[0]).reshape(1, 1, 3)) * 255).astype(int).reshape(-1).tolist(), count) for color, count in lab_colors_sorted]
    return rgb_colors


def save_representative_color_image(original_image, rgb_colors, save_path, MIN_THRESHOLD):
    min_threshold = MIN_THRESHOLD
    total_count = sum(count for _, count in rgb_colors)
    if total_count == 0:
        return
    # 如果original_image为None，只保存代表性颜色条;summary
    if original_image is None:
        color_height = 100
        result_image = Image.new("RGB", (1000, color_height))
        current_x = 0
        for rgb_color, count in rgb_colors:
            rgb_color_normalized = tuple(int(x) for x in rgb_color)  # 将颜色值转换为整数
            percentage = count / total_count
            if percentage < min_threshold:
                continue
            color_width = int((percentage) * 1000)
            color_block = Image.new("RGB", (color_width, color_height), rgb_color_normalized)
            result_image.paste(color_block, (current_x, 0))
            current_x += color_width
        result_image.save(save_path)
        return

    color_height = original_image.height // 5  # 代表性颜色条的高度
    result_image = Image.new("RGB", (original_image.width, original_image.height + color_height))
    result_image.paste(original_image, (0, 0))

    # 绘制代表性颜色条
    current_x = 0
    for rgb_color, count in rgb_colors:
        rgb_color_normalized = tuple(int(x) for x in rgb_color)  # 将颜色值转换为整数
        if count / total_count > min_threshold:
            color_width = int((count / total_count) * original_image.width)
            color_block = Image.new("RGB", (color_width, color_height), rgb_color_normalized)
            result_image.paste(color_block, (current_x, original_image.height))
            current_x += color_width

    result_image.save(save_path)


def remove_alpha_channel(image, thumbnail=False):
    if thumbnail:
        # 下采样 100x100
        image.thumbnail((100, 100))
    # 如果图像有 alpha 通道
    if image.mode == 'RGBA':
        # 获取图像数据
        data = image.getdata()
        # 创建一个新的列表用于存储修改后的像素
        new_data = []

        for item in data:
            # 检查 alpha 通道值
            if item[3] == 0:
                # 如果 alpha 为 0，替换为黑色 (0, 0, 0, 255)
                new_data.append((0, 0, 0, 255))
            else:
                # 否则保留原有像素
                new_data.append(item)

        # 替换图像数据
        image.putdata(new_data)
    # 将图像转换为RGB，不再有透明度
    image = image.convert("RGB")
    return image


# 在批处理函数中调用以上函数
def process_image_representative_color(prompt, img_path, save_path, COLOR_FILTERS, MIN_THRESHOLD, STYLE):
    prompt = prompt.replace(" ", "_")
    prompt = prompt.split(",")[0]
    # 检查image文件夹是否存在
    if not os.path.exists(os.path.join(img_path, prompt)):
        return
    clear_folder(os.path.join(save_path, prompt))

    prompt_dir = os.path.join(img_path, prompt)
    print(f"Processing prompt {prompt}")
    id = 0
    all_colors = []
    os.makedirs(os.path.join(save_path, prompt), exist_ok=True)

    for file_name in os.listdir(prompt_dir):
        if id > 50:
            break

        if not file_name.endswith(".png"):
            continue
        img_path = os.path.join(prompt_dir, file_name)
        base_filename = os.path.splitext(file_name)[0]
        try:
            rgb = color_extraction_with_filter(img_path, COLOR_FILTERS, os.path.join(save_path, prompt))
            if not rgb:
                print(f"No valid colors found in image {img_path}. Skipping.")
                continue
            result_list = []
            for rgb_point, count in rgb.items():
                for _ in range(count):
                    result_list.append(rgb_point)
            # get the highest count color
            tmp = find_representative_colors(np.array(result_list), 1, save_path=os.path.join(save_path, prompt), img_path=img_path)
            tmp.sort(key=lambda x: x[1], reverse=True)

            representative_color = tmp
            all_colors.append({"origginal_color": result_list, "represent": representative_color, "id": id})
            #
            original_image = remove_alpha_channel(Image.open(img_path))
            save_dir = os.path.join(save_path, prompt, base_filename + ".png")
            save_representative_color_image(original_image, representative_color, save_dir, MIN_THRESHOLD)
        
            id += 1

        except Exception as e:
            print(f"Error processing image {img_path}: {e}. Skipping.")
    print(f"Processing prompt {prompt} finished, {id} colors found in total.")

    dominant_palettes = compute_all_colors(all_colors, STYLE, save_path=os.path.join(save_path, prompt), img_path=img_path)

    palette_id = 0
    print(f"Processing prompt {prompt} finished, {len(dominant_palettes)} palettes found in total.")
    for palette in dominant_palettes:
        c = str(palette["count"])
        save_dir = os.path.join(save_path, prompt, f"{prompt}_{palette_id}_{c}_summary.png")
        save_representative_color_image(None, palette["color_palette"], save_dir, MIN_THRESHOLD)
        save_dir = os.path.join(save_path, prompt, f"{prompt}_{palette_id}_{c}_primary_summary.png")
        save_representative_color_image(None, palette["color_palette_1"], save_dir, MIN_THRESHOLD)
        palette_id += 1
        update_result(palette, prompt, STYLE)


def update_result(palette, prompt, STYLE):
    item = {}
    title = ["concept", "style"]
    item["concept"] = prompt
    item["style"] = STYLE

    for color in palette["color_palette"]:
        index = palette["color_palette"].index(color)
        item[f"color_{index}"] = color[0]
        item[f"count_{index}"] = color[1]
        title.append(f"color_{index}")
        title.append(f"count_{index}")

    if "color_palette_1" in palette and len(palette["color_palette_1"]) > 0:
        item["color_dominant"] = palette["color_palette_1"][0][0]
        title.append("color_dominant")

    # 检查是否已存在文件，如果不存在则写入表头
    file_path = "../../../frontend/public/all1.csv"
    file_exists = os.path.exists(file_path)

    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=title)
        if not file_exists:
            writer.writeheader()
        writer.writerow(item)


def compute_all_colors(all_colors, STYLE, threshold=12, save_path=None, img_path=None):
    color_groups = []
    for item in all_colors:
        item_represent = item["represent"]
        found_group = False
        min_diff = 20000
        min_diff_group = None
        # Check if this color is close to any existing group
        for group in color_groups:
            group_index = color_groups.index(group)
            group_represents = group['represent']
            distance = []
            for group_represent in group_represents:
                distance.append(distance_palettes(group_represent, item_represent))

            ave_diff = sum(distance) / len(distance)

            if ave_diff > threshold:
                continue
            elif ave_diff < min_diff:
                min_diff = ave_diff
                min_diff_group = group_index
                found_group = True
        if found_group:
            color_groups[min_diff_group]['items'].append(item)
            color_groups[min_diff_group]['represent'].append(item_represent)
            color_groups[min_diff_group]['count'] += 1
        else:
            color_groups.append({'represent': [item_represent], 'items': [item], 'count': 1, 'color_palette': None, 'color_palette_1': None})

    for group in color_groups:
        group_index = color_groups.index(group)
        original_colors = []
        for item in group['items']:
            copy = item['origginal_color'].copy()
            original_colors.extend(copy)
        # 把所有颜色保存成一张图
        original_colors = np.array(original_colors)
        original_colors = original_colors.reshape(-1, 3)
        original_colors = np.concatenate(original_colors, axis=0)
        original_colors = original_colors.reshape(-1, 3)

        dominant_center = find_representative_colors(np.array(original_colors),
                                                     1,
                                                     save_path=save_path,
                                                     img_path=img_path,
                                                     type="overall",
                                                     id=str(group["count"]) + "_" + str(group_index))

        group_primary = []
        group_accent = []
        for color in original_colors:
            distance = cal_LAB_CIEDE2000_distance(color, dominant_center[0][0])
            if distance > 7:
                # continue
                group_accent.append(color)
            else:
                group_primary.append(color)

        # dominent_colors_1 = dominant_center
        dominent_colors_1 = find_representative_colors(np.array(group_primary), 1, center=dominant_center[0][0])
        dominent_colors = find_representative_colors(np.array(group_accent), 5)
        group["dominant_count"] = dominant_center[0][1]
        # 从dominent_colors中移除和dominent_colors_1相似的颜色
        closest_color = None
        closest_index = -1
        for color in dominent_colors:
            distance = cal_LAB_CIEDE2000_distance(color[0], dominent_colors_1[0][0])
            if closest_color is None or distance < closest_color:
                closest_color = distance
                closest_index = dominent_colors.index(color)
        if closest_index != -1:
            dominent_colors.pop(closest_index)

        group['color_palette'] = dominent_colors
        # dominent_colors_1 排序
        dominent_colors_1 = sorted(dominent_colors_1, key=lambda x: x[1], reverse=True)
        group['color_palette_1'] = dominent_colors_1

    minimum_items = 3
    if STYLE == "design":
        minimum_items = 1

    color_groups = [group for group in color_groups if group['count'] > minimum_items]
    color_groups_sorted = sorted(color_groups, key=lambda x: x['count'], reverse=True)
    if len(color_groups_sorted) == 0:
        return []
    # max_count = color_groups_sorted[0]['count']
    # color_groups_max = [group for group in color_groups_sorted if group['count'] == max_count]
    color_groups_max = sorted(color_groups_sorted, key=lambda x: x['dominant_count'], reverse=True)
    # print(color_groups_sorted[0]["color_palette"], color_groups_sorted[1]["color_palette"])
    # max_count = color_groups_sorted[0]['count']
    # color_groups_max = [group for group in color_groups_sorted if group['count'] == max_count]
    # # filter out groups with less than 3 items

    # if top two have same count, compare the number of pixels
    # if len(color_groups_max) > 1:
    #     # print("same count")
    #     # print(color_groups_sorted[0]["color_palette_1"][0][1])
    #     # print(color_groups_sorted[1]["color_palette_1"][0][1])
    #     color_groups_max = sorted(color_groups_max, key=lambda x: x['color_palette_1'][0][1], reverse=True)
    # # return top 2 if there are more than 3 groups
    result_len = 5

    if len(color_groups_max) > result_len:
        # pop the top 3
        color_groups_max = color_groups_max[:result_len]
        
    return color_groups_max


def distance_palettes(palette1, palette2):
    if len(palette1) != len(palette2):
        raise ValueError("Palettes must be of the same length")
    distance_total = 0
    distance_min = 1000
    num = 0
    for (color1, _) in palette1:
        for (color2, _) in palette2:
            # scale 0.5 to L channel
            color1 = [color1[0] * 0.5, color1[1], color1[2]]
            color2 = [color2[0] * 0.5, color2[1], color2[2]]
            d = cal_LAB_CIEDE2000_distance(color1, color2)
            if d < distance_min:
                distance_min = d
        num += 1
        distance_total += distance_min
    return distance_total / num


def cal_LAB_CIEDE2000_distance(RGB1, RGB2):
    RGB1 = [x / 255 for x in RGB1]
    RGB2 = [x / 255 for x in RGB2]
    Lab1 = rgb2lab(np.array(RGB1).reshape(1, 1, 3))[0, 0, :]
    Lab2 = rgb2lab(np.array(RGB2).reshape(1, 1, 3))[0, 0, :]
    distance = ciede2000(Lab1, Lab2)["delta_E_00"]
    return distance


def batch_representative_color(prompts, src_img_dir, save_dir):
    # 进程数量 = CPU核心数 -1
    process_count = multiprocessing.cpu_count() - 2
    with multiprocessing.Pool(process_count) as pool:
        pool.starmap(process_image_representative_color, [(prompt, src_img_dir, save_dir, COLOR_FILTERS, MIN_THRESHOLD, STYLE) for prompt in prompts])


def clear_folder(folder_path):
    folder = Path(folder_path)
    if folder.exists() and folder.is_dir():
        for file in folder.glob("*"):
            file.unlink()
        folder.rmdir()


def read_prompt_from_file(file_path):
    prompts = []
    with open(file_path, 'r') as f:
        for line in f:
            prompts.append(line.strip())
    return prompts


def distance2(c1, c2):
    # give different weight to l, a, b
    weight = [0.5, 1, 1]
    distance = math.sqrt((c1[0] - c2[0])**2 * weight[0] + (c1[1] - c2[1])**2 * weight[1] + (c1[2] - c2[2])**2 * weight[2])
    return distance


def add(c1, c2):
    res = []
    for i in range(len(c1)):
        # print(c1[i], c2[i])
        res.append(c1[i] + c2[i])
    return res


def sca_mul(lab, count):
    return [component * count for component in lab]


def initialize_globals(args):
    global COLOR_FILTERS, MIN_THRESHOLD, TEST_CASE, STYLE
    COLOR_FILTERS = list(map(float, args.color_filter.split()))
    MIN_THRESHOLD = args.min_threshold
    TEST_CASE = args.test_case
    STYLE = args.style


def parse_arguments():
    parser = argparse.ArgumentParser(description='Render color processing.')
    parser.add_argument('color_filter', type=str, help='Color filter as space-separated string')
    parser.add_argument('min_threshold', type=float, help='Minimum threshold')
    parser.add_argument('test_case', type=str, help='Path to test case file')
    parser.add_argument('style', type=str, help='photo or clipart')
    return parser.parse_args()


def main():
    args = parse_arguments()
    initialize_globals(args)
    name = TEST_CASE.split("/")[2].split(".")[0] + "_" + STYLE
    base_dir = "../../output-segmented/" + name
    save_dir = "../../output-color/" + name
    test_case = TEST_CASE

    # 开始计时
    start_time = time.time()
    prompts = read_prompt_from_file(test_case)
    batch_representative_color(prompts, base_dir, save_dir)

    # 结束计时并打印，转为分钟
    end_time = time.time()

    # 写入参数到文件
    os.makedirs(f"../../results/{name}", exist_ok=True)
    with open(f"../../results/{name}/parameters.json", 'w') as f:
        json.dump({"COLOR_FILTERS": COLOR_FILTERS, "MIN_THRESHOLD": MIN_THRESHOLD, "TEST_CASE": TEST_CASE, "time": (end_time - start_time) / 60}, f)
    print("Time used: ", (end_time - start_time) / 60, " minutes")


if __name__ == "__main__":
    main()
