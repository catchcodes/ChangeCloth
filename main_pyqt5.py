# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets


# 读取中文路径
def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)


class mwindow(QWidget):
    def __init__(self):
        super(mwindow, self).__init__()
        self.setupUi(self)
        self.setAcceptDrops(True)
        # 图片
        self.img = None
        self.imghsv = None
        self.aimg = None
        self.HSV = None

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setEnabled(True)
        Dialog.resize(800, 600)
        Dialog.setMinimumSize(QtCore.QSize(800, 600))
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(0, 20, 800, 600))
        self.label.setAcceptDrops(False)
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.label2 = QtWidgets.QLabel(Dialog)
        self.label2.setGeometry(QtCore.QRect(900, 20, 800, 600))
        self.label.setAcceptDrops(False)
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label2")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "ChangeCloth"))
        self.label.setText(_translate("Dialog", "拖拽图片到此处"))
        self.label2.setText(_translate("Dialog", "显示换色后的图片"))

    # 鼠标拖入事件
    def dragEnterEvent(self, evn):
        # 鼠标放开函数事件
        evn.accept()

    # 鼠标放开执行
    def dropEvent(self, evn):
        # 判断文件类型
        if evn.mimeData().hasUrls():
            # 获取文件路径
            file_path = evn.mimeData().urls()[0].toLocalFile()
            # 判断是否是图片
            if file_path.endswith('.jpg') or file_path.endswith('.png'):
                self.img = cv_imread(file_path)
            else:
                # 提示
                QMessageBox.information(self, '提示', '请拖入图片')
                return
            # opencv 转qimage
            qimg = QImage(self.img.data, self.img.shape[1], self.img.shape[0], self.img.shape[1] * self.img.shape[2],
                          QImage.Format_RGB888)
            # 显示图片 自适应
            self.label.setPixmap(
                QPixmap.fromImage(qimg).scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio))

    # def dragMoveEvent(self, evn):
    #     pass

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        pos = event.pos()
        pixmap = self.grab()
        img = pixmap.toImage()
        color = img.pixelColor(pos.x(), pos.y())
        self.HSV = color.getHsv()
        self.showImg()
        tips = "位置在(%s,%s),颜色为：%s,%s,%s" % (pos.x(), pos.y(), color.red(), color.green(), color.blue())
        self.setToolTip(tips)

    def showImg(self):
        print(self.HSV)
        # HSV 的下界限
        lower = np.array([self.HSV[0]/2 - 8, 50, 50])
        # HSV 的上界限
        upper = np.array([self.HSV[0]/2 + 8, 255, 255])

        self.imghsv = cv2.cvtColor(self.img, cv2.COLOR_RGB2HSV)

        mask = cv2.inRange(self.imghsv, lower, upper)
        # 核
        kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]], dtype=np.uint8)
        # 腐蚀图像，除去干扰点
        eroded = cv2.erode(mask, kernel, iterations=1)
        # 膨胀图像
        dilated = cv2.dilate(eroded, kernel, iterations=1)
        rows, cols, _ = self.imghsv.shape

        color = QColorDialog.getColor()
        h = color.getHsv()[0]

        for row in range(rows):
            for col in range(cols):
                if dilated[row, col] == 255:
                    self.imghsv.itemset((row, col, 0), h/2)

        self.aimg = cv2.cvtColor(self.imghsv, cv2.COLOR_HSV2RGB)

        # opencv 转qimage
        qimg = QImage(self.aimg.data, self.aimg.shape[1], self.aimg.shape[0],
                      self.aimg.shape[1] * self.aimg.shape[2],
                      QImage.Format_RGB888)
        # 显示图片 自适应
        self.label2.setPixmap(
            QPixmap.fromImage(qimg).scaled(self.label2.width(), self.label2.height(), Qt.KeepAspectRatio))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 初始化窗口
    m = mwindow()
    m.resize(1680, 720)
    m.show()
    sys.exit(app.exec_())
