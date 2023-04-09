#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :main.py
# @Time      :2023/4/7 19:46
# @Author    :Ouyang Bin

import cv2
import numpy as np

# 不存在的HSV值
HSV = [0, 0, 256]
newHSV = [0, 0, 256]


def bgr2hsv(b, g, r):
    # 限定像素BGR值的范围
    assert (0 <= r < 256 and 0 <= g < 256 and 0 <= b < 256)

    r, g, b = r / 255.0, g / 255.0, b / 255.0
    Max = max(r, g, b)
    Min = min(r, g, b)
    D = Max - Min

    HSV[2] = int(Max * 255)

    HSV[1] = int(255 * (D / Max)) if Max != 0 else 0

    if D == 0:
        HSV[0] = 0
    elif Max == r:
        HSV[0] = (60 * ((g - b) / D)) % 360
    elif Max == g:
        HSV[0] = (120 + 60 * ((b - r) / D)) % 360
    elif Max == b:
        HSV[0] = (240 + 60 * ((r - g) / D)) % 360

    HSV[0] = int(HSV[0] / 2)
    return HSV


# 回调函数
def get_color_BGR(envent, x, y, flags, param):
    if envent == cv2.EVENT_LBUTTONDOWN:
        # 注意：opencv的行列与坐标相反(row, col) -> (y, x)
        BGR = img[y, x].tolist()
        bgr2hsv(BGR[0], BGR[1], BGR[2])


img = cv2.imread(r"C:\Users\19941\Pictures\cloth.jpg")
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
rows, cols, _ = img_hsv.shape

cv2.namedWindow("ChangeColor")
cv2.resizeWindow("ChangeColor", rows, cols)
cv2.setMouseCallback("ChangeColor", get_color_BGR)

cv2.createTrackbar('H', 'ChangeColor', 140, 180, lambda x: None)
# cv2.createTrackbar('S', 'ChangeColor', 100, 255, lambda x: None)
# cv2.createTrackbar('V', 'ChangeColor', 100, 255, lambda x: None)

times = 0

while True:
    cv2.imshow('ChangeColor', img)

    if newHSV != HSV:
        if times == 0:
            # HSV 的下界限
            lower = np.array([HSV[0] - 7, 50, 50])
            # HSV 的上界限
            upper = np.array([HSV[0] + 7, 255, 255])
            mask = cv2.inRange(img_hsv, lower, upper)

            # 核
            kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=np.uint8)
            # 腐蚀图像，除去干扰点
            eroded = cv2.erode(mask, kernel, iterations=1)
            # 膨胀图像
            dilated = cv2.dilate(eroded, kernel, iterations=1)

            times += 1

        h = cv2.getTrackbarPos('H', 'ChangeColor')
        # s = cv2.getTrackbarPos('S', 'ChangeColor')
        # v = cv2.getTrackbarPos('V', 'ChangeColor')

        for row in range(rows):
            for col in range(cols):
                if dilated[row, col] == 255:
                    img_hsv.itemset((row, col, 0), h)
                    # img_hsv.itemset((row, col, 1), s)
                    # img_hsv.itemset((row, col, 2), v)

        img = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
        cv2.imshow("ChangeColor", img)
    else:
        img = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
        cv2.imshow("ChangeColor", img)

    if cv2.waitKey(1) & 0xff == 27:
        break

cv2.destroyAllWindows()
