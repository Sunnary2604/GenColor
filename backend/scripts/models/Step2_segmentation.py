import cv2
import os
import numpy as np
import glob
import supervision as sv
import torch
import torchvision
import time
import sys
from pathlib import Path
from segment_anything import sam_model_registry, SamPredictor
from groundingdino.util.inference import Model, predict
import warnings
warnings.filterwarnings("ignore")

# 自动获取项目根目录路径
BASE_DIR = str(Path(__file__).parent.parent.parent.parent.absolute())
print(f"项目根目录: {BASE_DIR}")
# ...其他代码...
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("开始了", DEVICE)
# GroundingDINO config and checkpoint
GROUNDING_DINO_CONFIG_PATH = os.path.join(BASE_DIR, "backend/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py")
GROUNDING_DINO_CHECKPOINT_PATH = os.path.join(BASE_DIR, "backend/GroundingDINO/weights/groundingdino_swint_ogc.pth")

# Segment-Anything checkpoint
SAM_ENCODER_VERSION = "vit_h"
SAM_CHECKPOINT_PATH = os.path.join(BASE_DIR, "backend/segment-anything/sam_vit_h_4b8939.pth")

# Building GroundingDINO inference model
print("Building GroundingDINO inference model Start")
grounding_dino_model = Model(model_config_path=GROUNDING_DINO_CONFIG_PATH, model_checkpoint_path=GROUNDING_DINO_CHECKPOINT_PATH)
print("Building GroundingDINO inference model Done")
# Building SAM Model and SAM Predictor
print("Building SAM Model and SAM Predictor Start")
sam = sam_model_registry[SAM_ENCODER_VERSION](checkpoint=SAM_CHECKPOINT_PATH)
sam.to(device=DEVICE)
sam_predictor = SamPredictor(sam)
print("Building SAM Model and SAM Predictor Done")
# Predict classes and hyper-param for GroundingDINo
CLASSES = None
BOX_THRESHOLD = 0.4
TEXT_THRESHOLD = 0.4
NMS_THRESHOLD = 0.7
print("设置结束")

# 使用检测到的框激活SAM来生成掩码的函数
def segment(sam_predictor: SamPredictor, image: np.ndarray, xyxy: np.ndarray) -> np.ndarray:
    sam_predictor.set_image(image)
    result_masks = []
    # print("到segment了")
    for box in xyxy:
        masks, scores, logits = sam_predictor.predict(
            box=box,
            multimask_output=False
        )
        index = np.argmax(scores)
        result_masks.append(masks[index])
        # result_masks.extend(masks)
    return np.array(result_masks)

# 保存分割后的掩码和图像的函数
def save_masked_objects(image, masks, classes, detection_classes, output_folder, original_name):
    os.makedirs(output_folder, exist_ok=True)
    # print(f"mask的classes: {classes}, detection的类 {detection_classes}")

    class_index = 0
    for class_id in detection_classes:
        if class_id < len(classes):
            class_name = classes[class_id]
            combined_mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
            
            # 合并当前类别的所有掩码
            for mask, detected_class_id in zip(masks, detection_classes):
                if detected_class_id == class_id:
                    combined_mask = np.maximum(combined_mask, mask)

            # 创建包含 Alpha 通道的图像
            class_mask_with_alpha = np.zeros((image.shape[0], image.shape[1], 4), dtype=image.dtype)
            mask_alpha = combined_mask * 255  # 将掩码转换为 Alpha 通道值
            class_mask_with_alpha[..., :3][mask_alpha > 0] = image[mask_alpha > 0]  # 设置颜色
            class_mask_with_alpha[..., 3][mask_alpha > 0] = mask_alpha[mask_alpha > 0]  # 设置 Alpha 通道

            class_image_path = os.path.join(output_folder, f"{original_name}_mask_{class_name}.png")
            print(f"Saving mask image for class '{class_name}' with alpha: {class_image_path}")
            class_mask_with_alpha_bgr = cv2.cvtColor(class_mask_with_alpha, cv2.COLOR_RGBA2BGRA)
            cv2.imwrite(class_image_path, class_mask_with_alpha_bgr)
        else:
            print(f"Warning: Detected class_id {class_id} is out of range. Skipping this mask.")
        class_index += 1



def process_image(image_file, prompt, save_dir):
    try:
        original_name=image_file.split("/")[-1].split(".png")[0]
        print(f"正在处理图片：{image_file}")
        image = cv2.imread(image_file)
        if image is None:
            print(f"无法读取图片：{image_file}")
            return
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        print(f"使用提示词：{prompt}")
        global CLASSES
        CLASSES = [prompt]
        output_folder = os.path.join(save_dir,prompt.replace(" ","_"))
        os.makedirs(output_folder, exist_ok=True)

        detections = grounding_dino_model.predict_with_classes(
            image=image_rgb,
            classes=CLASSES,
            box_threshold=BOX_THRESHOLD,
            text_threshold=TEXT_THRESHOLD
        )
        # print(f"检测结果: {detections}")
        print(f"NMS 之前：{len(detections.xyxy)} 个框")
        box_annotator = sv.BoxAnnotator()
        # 对 class_id 进行有效性检查
        for i, cid in enumerate(detections.class_id):
            if cid is None or cid >= len(CLASSES):
                print(f"警告：检测到无效的 class_id '{cid}' 在索引 {i}。")
                detections.class_id[i] = -1  # 将无效的 class_id 设置为 -1
        labels = [f"{CLASSES[class_id]} {confidence:0.2f}" for _, _, confidence, class_id, _, _ in detections if class_id >= 0]
        # print(f"lables, {labels}")
        if labels!=[]:
            annotated_frame = box_annotator.annotate(scene=image.copy(), detections=detections, labels=labels)

            # 保存绘制了检测框的图像
            output_image_path = os.path.join(output_folder, f"{original_name}_detected.jpg")
            cv2.imwrite(output_image_path, annotated_frame)
            print(f"检测框结果已保存到：{output_image_path}")


        
        # 执行 NMS
        if len(detections.xyxy) > 0:
            nms_idx = torchvision.ops.nms(
                torch.from_numpy(detections.xyxy),
                torch.from_numpy(detections.confidence),
                NMS_THRESHOLD
            ).numpy()

            # 过滤掉 NMS 结果中的无效 class_id
            valid_nms_idx = [idx for idx in nms_idx if detections.class_id[idx] != -1]
            
            if not valid_nms_idx:
                print("NMS 之后没有有效的 class_id。")
                return

            detections.xyxy = detections.xyxy[valid_nms_idx]
            detections.confidence = detections.confidence[valid_nms_idx]
            detections.class_id = detections.class_id[valid_nms_idx]
        else:
            print("没有检测到需要用 NMS 处理的结果。")
            return
        
        print(f"NMS 之后：{len(detections.xyxy)} 个框")

        # 执行分割并保存带掩模的对象
        detections.mask = segment(
            sam_predictor=sam_predictor,
            image=image_rgb,
            xyxy=detections.xyxy
        )
        # print (detections)
        
        save_masked_objects(
            image=image_rgb,
            masks=detections.mask,
            classes=CLASSES,
            detection_classes=detections.class_id,
            output_folder=output_folder,
            original_name = original_name
        )
    except Exception as e:
        print(f"处理图片 {image_file} 时发生错误：{e}")
    
def desaturate_image(image, factor=0.5):
    """ Reduce the saturation of an image by a given factor. """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv_image[..., 2] *= factor
    return cv2.cvtColor(hsv_image.astype(np.uint8), cv2.COLOR_HSV2BGR)


def batch_segment(prompts, src_dir, save_dir):
    print("开始批量处理图片")

    for prompt in prompts:
        prompt_dir = os.path.join(src_dir, prompt.replace(" ","_"))
        image_files = glob.glob(os.path.join(prompt_dir, '*.png'))
        mask_dir= os.path.join(save_dir, prompt.replace(" ","_"))
        if os.path.exists(mask_dir):
            clear_folder(mask_dir)
        print(f"在目录 {prompt_dir} 下发现 {len(image_files)} 张图片")

        if image_files:
            for image_file in image_files:
                try:
                    process_image(image_file, prompt, save_dir)
                except Exception as e:
                    print(f"处理图片 {image_file} 时发生错误：{e}")
                    print("跳过该图片，继续处理下一张。")
        else:
            print(f"目录 {prompt_dir} 下没有找到 PNG 图片。")
        
        mask_dir=Path(mask_dir)
    #     image_list = [str(file) for file in mask_dir.rglob('*.png')]
    # return image_list

def clear_folder(folder_path):
    folder = Path(folder_path)
    for file in folder.glob("*"):
        file.unlink()  # Delete file
    folder.rmdir()  # Remove the directory
# read the prompt frim file, return a list of prompts
def read_prompt_from_file(file_path):
    prompts = []
    with open(file_path, 'r') as f:
        for line in f:
            prompts.append(line.strip())
    return prompts

if __name__ == "__main__":
    base_dir="../cases"
    # test_case=["one"]
    test_case=["represent_environments"]
    for case in test_case:
        prompts = read_prompt_from_file(os.path.join(base_dir, f'{case}.txt'))
        batch_segment(prompts, src_dir=f'{BASE_DIR}/backend/output-image/{case}_photo', save_dir=f'{BASE_DIR}/backend/output-segmented/{case}_photo')

