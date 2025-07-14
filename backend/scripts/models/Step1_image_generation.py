from torch import autocast
from diffusers import StableDiffusion3Pipeline
import os
from pathlib import Path
import torch
import random
from concurrent.futures import ThreadPoolExecutor

# 自动获取项目根目录路径
BASE_DIR = str(Path(__file__).parent.parent.parent.parent.absolute())
print(f"项目根目录: {BASE_DIR}")

# 加载模型，只执行一次
CKPT = "stabilityai/stable-diffusion-3-medium-diffusers"
pipe = StableDiffusion3Pipeline.from_pretrained(
    CKPT, 
    torch_dtype=torch.float16
).to("mps")
# pipe.enable_model_cpu_offload()


def clear_folder(folder_path):
    folder = Path(folder_path)
    if folder.exists() and folder.is_dir():
        for file in folder.glob("*"):
            file.unlink()  # 删除文件
        folder.rmdir()  # 删除目录

def generate_subfolder(prompt):
    comma_index = prompt.find(',')
    if comma_index != -1:
        prompt = prompt[:comma_index]
    subfolder = prompt.replace(" ", "_")
    return subfolder

def save_images(images, subfolder_path, total_generated, scale, seed):
    for idx, image in enumerate(images):
        image_idx = total_generated + idx
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
        image.save(f"{subfolder_path}/{image_idx}_{scale}_{seed}.png")

def single_image_generation(prompt, save_dir, n_samples=50, batch_size=5, scales=[20], seeds=[42]):
    subfolder = generate_subfolder(prompt)
    subfolder_path = f"{save_dir}/{subfolder}"

    # 清除子文件夹
    clear_folder(subfolder_path)
    if not isinstance(scales, list):
        scales = [scales]
    if not isinstance(seeds, list):
        seeds = [seeds]
    if not isinstance(prompt, list):
        prompt = [prompt]

    # enhanced_prompt = f"a {prompt[0]}, natural light, realistic photo"
    # negative_prompts = "cropped, out of frame, cartoon, unreal, artwork, worst quality, blurry"
    enhanced_prompt = f"a {prompt[0]}. simple flat design"
    negative_prompts = "Cropped, Out of frame, photo, 3d"
    prompts = [enhanced_prompt] * batch_size

    total_generated = 0
    with ThreadPoolExecutor() as executor:
        while total_generated < n_samples:
            with autocast("mps"):
                seed = random.randint(1, 2147483647)
                # seed = 2147483647
                scale = round(random.uniform(3, 6), 2)
                images = pipe(prompts, guidance_scale=scale, num_inference_steps=30, negative_prompt=negative_prompts, generator=torch.manual_seed(seed), height=1024, width=1024).images
                # 使用线程池并行保存图像
                executor.submit(save_images, images, subfolder_path, total_generated, scale, seed)
                total_generated += batch_size

def batch_image_generation(prompts, save_dir, n_samples=10, batch_size=1, scale=7):
    for prompt in prompts:
        single_image_generation(prompt=prompt, save_dir=save_dir, n_samples=n_samples, batch_size=batch_size)

def read_prompt_from_file(file_path):
    with open(file_path, 'r') as f:
        prompts = [line.strip() for line in f]
    return prompts

if __name__ == '__main__':
    base_dir = "../cases"
    test_case = ["base"]
    for case in test_case:
        prompts = read_prompt_from_file(os.path.join(base_dir, f'{case}.txt'))
        print(prompts)
    
        save_dir = f'{BASE_DIR}/backend/output-image/{case}_clipart/'
        batch_image_generation(prompts, save_dir=save_dir)
