import os
from PIL import Image, ImageDraw, ImageFont
import argparse

TEST_CASE = "../cases/fruits.txt"


# 存储拼接的图像
# read the prompt frim file, return a list of prompts
def read_prompt_from_file(file_path):
    prompts = []
    with open(file_path, 'r') as f:
        for line in f:
            prompts.append(line.strip())
    return prompts


def concatenate_each_img():
    global TEST_CASE, STYLE
    name = TEST_CASE.split("/")[2].split(".")[0] + "_" + STYLE
    basepath = "../../output-color/" + name
    prompts = read_prompt_from_file(TEST_CASE)
    # 遍历所有的文件
    for file in prompts:
        file = file.replace(" ", "_")
        subpath = os.path.join(basepath, file)
        concatenated_images = []
        # 存储已经出现过的index
        seen_indices = set()
        if not os.path.exists(subpath):
            continue
        
        if os.path.isdir(subpath) and os.path.exists(subpath):
            count = 0
            for filename in os.listdir(subpath):
                if count > 50:
                    break
                count += 1
                if filename == ".DS_Store":
                    continue
                file_index = filename.split("_")[0]
                if file_index == "concatenated":
                    continue
                if "summary" in filename:
                    continue
                if "hist" in filename:
                    continue
                # 只拼接file_index第一次出现的图像
                if file_index not in seen_indices:
                    seen_indices.add(file_index)
                    image_path = os.path.join(subpath, filename)
                    image = Image.open(image_path)
                    concatenated_images.append(image)
            # 拼接图像
            if concatenated_images:
                widths, heights = zip(*(image.size for image in concatenated_images))

                # 定义每行的图像数量
                images_per_row = 10

                max_width = max(widths)
                max_height = max(heights)

                # 计算新图像的总宽度和总高度
                total_width = max_width * images_per_row
                total_height = max_height * ((len(concatenated_images) + images_per_row - 1) // images_per_row)

                new_image = Image.new('RGB', (total_width, total_height))

                x_offset = 0
                y_offset = 0

                for i, image in enumerate(concatenated_images):
                    new_image.paste(image, (x_offset, y_offset))
                    x_offset += max_width

                    # 如果达到每行的最大图像数量，换行
                    if (i + 1) % images_per_row == 0:
                        x_offset = 0
                        y_offset += max_height

                # 拼接图像到结果文件夹
                p = f"../../results/{name}/"
                os.makedirs(p, exist_ok=True)
                # 如果存在concatenated_image.jpg，则覆盖
                if os.path.exists(os.path.join(p, file + "_concatenated.jpg")):
                    os.remove(os.path.join(p, file + "_concatenated.jpg"))
                new_image.save(os.path.join(p, file + "_concatenated.jpg"))
            else:
                print("没有找到任何图像进行拼接")


def concate_dominent_color():
    global TEST_CASE, STYLE
    name = TEST_CASE.split("/")[2].split(".")[0] + "_" + STYLE
    basepath = "../../output-color/" + name
    prompts = read_prompt_from_file(TEST_CASE)

    # 定义字体大小
    font_size = 80
    # 尝试使用默认字体
    try:
        font = ImageFont.truetype("../settings/arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    concatenated_images = []
    image_labels = []

    for file in prompts:
        file = file.replace(" ", "_")
        subpath = os.path.join(basepath, file)
        if not os.path.exists(subpath):
            break   
        for filename in os.listdir(subpath):
            if "summary" in filename:
                image_path = os.path.join(subpath, filename)
                image = Image.open(image_path)
                concatenated_images.append(image)
                # 更改标签格式，按照_分割，把第一个元素放在最后,二，三个元素放在前面 （可能没有三）
                f = file.split("_")
                if len(f) == 3:
                    lable = f[1] + " " + f[2] + " " + f[0]
                elif len(f) == 2:
                    lable = f[1] + " " + f[0]
                else:
                    lable = f[0]
                image_labels.append(lable)

    if concatenated_images:
        widths, heights = zip(*(image.size for image in concatenated_images))
        # 定义每行的图像数量
        images_per_row = 5
        if TEST_CASE == "../cases/fruits.txt":
            images_per_row = 5
        else:
            images_per_row = 8

        max_width = max(widths)
        max_height = max(heights) + font_size + 10  # 增加字体高度和间距

        # 计算新图像的总宽度和总高度
        total_width = max_width * images_per_row
        total_height = max_height * ((len(concatenated_images) + images_per_row - 1) // images_per_row)

        new_image = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(new_image)

        x_offset = 0
        y_offset = 0

        for i, image in enumerate(concatenated_images):
            # 绘制文字
            draw.text((x_offset, y_offset), image_labels[i], font=font, fill=(0, 0, 0))
            new_image.paste(image, (x_offset, y_offset + font_size + 10))

            x_offset += max_width

            # 如果达到每行的最大图像数量，换行
            if (i + 1) % images_per_row == 0:
                x_offset = 0
                y_offset += max_height
        name = TEST_CASE.split("/")[2].split(".")[0] + "_" + STYLE
        p = f"../../results/{name}/"
        os.makedirs(p, exist_ok=True)

        # 保存拼接后的图像，到原来的文件夹
        concatenated_image_path = os.path.join(p, "_summary.jpg")
        if os.path.exists(concatenated_image_path):
            os.remove(concatenated_image_path)

        new_image.save(concatenated_image_path)
        print(f"拼接后的图像已保存为{concatenated_image_path}")


def main():
    global TEST_CASE, STYLE

    parser = argparse.ArgumentParser(description='Render color processing.')
    parser.add_argument('test_case', type=str, help='Path to test case file')
    parser.add_argument('style', type=str, help='photo or clipart')
    args = parser.parse_args()

    TEST_CASE = args.test_case
    STYLE = args.style
    concatenate_each_img()
    concate_dominent_color()
    print("Done!")


if __name__ == "__main__":
    main()
