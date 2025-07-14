from pyciede2000 import ciede2000
import numpy as np
from skimage.color import rgb2lab

def cal_LAB_CIEDE2000_distance(RGB1, RGB2):
	# RGB1 is a list, /255 for each element
	RGB1 = [x / 255 for x in RGB1]
	# change from string to number
	RGB2 = [float(x) for x in RGB2]
	# Convert RGB to LAB
	Lab1 = rgb2lab(np.array(RGB1).reshape(1, 1, 3))[0, 0, :]
	Lab2 = rgb2lab(np.array(RGB2).reshape(1, 1, 3))[0, 0, :]
	distance=ciede2000(Lab1, Lab2)["delta_E_00"]
	return distance