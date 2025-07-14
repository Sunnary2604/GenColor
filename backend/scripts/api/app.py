# note: this file is used to run the api, but currently not used
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import csv
import os
import sys
from pyciede2000 import ciede2000
from skimage.color import rgb2lab, rgb2hsv, hsv2rgb, lab2lch, lch2lab, lab2rgb

app = Flask(__name__)

CORS(app)

current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目的根目录
project_root = os.path.abspath(os.path.join(current_dir, '..'))
# 将项目的根目录添加到模块搜索路径
sys.path.append(project_root)

print(os.path.abspath(os.path.join(current_dir, '..')))


#######################
# Step1: Generate image
# [POST] /generate
# [Request] {"prompts": ["apple", "banana"]}
# [Response] {"image_list": ["path/to/image1", "path/to/image2"]}
#######################
@app.route("/generate", methods=("GET", "POST"))
def test():
    from backend.scripts.models.Step1_image_generation import (single_image_generation)
    if request.method == 'POST':
        data = request.get_data().decode("utf-8")
        result = json.loads(data)
        prompts = result["prompts"]
        save_dir = '/hpc2hdd/home/yhou073/projects/semantic-color-code/output-image'
        image_list = single_image_generation(prompts, save_dir=save_dir)
        return image_list


#######################
# Step2: Segment image
# [POST] /segment
# [Request] {"prompts": ["apple", "banana"]}
# [Response] {"image_list": ["path/to/image1", "path/to/image2"]}
#######################
@app.route("/segment", methods=("GET", "POST"))
def segment_image():
    from backend.scripts.models.Step2_segmentation import (batch_segment)
    if request.method == 'POST':
        data = request.get_data().decode("utf-8")
        result = json.loads(data)
        print(result)
        prompts = result["prompts"]
        image_list = batch_segment(prompts,
                                   src_dir='/hpc2hdd/home/yhou073/projects/semantic-color-code/output-image',
                                   save_dir='/hpc2hdd/home/yhou073/projects/semantic-color-code/output-segmented')
        return image_list


#######################
# Step3: Extract color, return a distribution of color
# [GET] /color
# [Response] {"color_list": [{"color": "#fff", "value": 0.5}, {"color": "#000", "value": 0.3}]}
#######################
@app.route("/color", methods=("GET", "POST"))
def extract():
    if request.method == 'GET':
        # call module to extract color

        return 0


#######################
# Get one image
# [POST] /images
# [Request] {"filename": "path/to/image"}
# [Response] image binary data
#######################
@app.route("/images", methods=("GET", "POST"))
def get_image():
    if request.method == 'POST':
        data = request.get_data().decode("utf-8")
        result = json.loads(data)
        filename = result["filename"]
        try:
            # current project root
            project_root = os.path.abspath(os.path.join(current_dir, '../..'))
            # concat the path, absolute path
            print("filename", filename)
            return send_file(project_root + filename, mimetype='image/jpeg')
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': 'Image not found', 'detail': str(e)}), 404


@app.route("/getFileNames", methods=("GET", "POST"))
def getFileNames():
    if request.method == 'POST':
        data = request.get_data().decode("utf-8")
        result = json.loads(data)
        base_dir = result["base_dir"]
        file_type = result["file_type"]
        image_names = []
        project_root = os.path.abspath(os.path.join(current_dir, '../..'))
        base_dir = os.path.join(project_root, base_dir)
        print("bbbb", base_dir)
        for file_name in os.listdir(base_dir):
            # if is path, return the path
            if os.path.isdir(os.path.join(base_dir, file_name)):
                image_names.append(file_name)
            elif file_name.endswith(file_type):
                image_names.append(file_name)
        return jsonify(image_names)


@app.route("/getConcepts", methods=("GET", "POST"))
def getConcepts():
    if request.method == 'POST':
        data = request.get_data().decode("utf-8")
        result = json.loads(data)
        threthold = result["threthold"]
        color = result["color"]

        path = "../../../frontend/public/all.csv"
        # read csv, turn to json
        with open(path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9999, debug='True')
