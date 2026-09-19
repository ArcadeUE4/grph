#Если не установлен PyQt, напишите в терминале pip Install PyQt6

import sys
import numpy as np
from PIL import Image

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
 QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, 
 QMessageBox, QGroupBox, QComboBox, QDoubleSpinBox
 )
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

# Функция свертки 2D с произвольным ядром
def customConvolve2D(imageArray, kernel):
    kHeight, kWidth = kernel.shape
    padH = kHeight // 2
    padW = kWidth // 2

    kernelFlipped = np.flip(kernel)

    if imageArray.ndim == 2:
        padded = np.pad(imageArray, ((padH, padH), (padW, padW)), mode='reflect')
        out = np.zeros_like(imageArray, dtype=np.float32)
        h, w = imageArray.shape

        for i in range(h):
            for j in range(w):
                region = padded[i:i + kHeight, j:j + kWidth]
                out[i, j] = np.sum(region * kernelFlipped)
        return out

    elif imageArray.ndim == 3:
        padded = np.pad(imageArray, ((padH, padH), (padW, padW), (0, 0)), mode='reflect')
        out = np.zeros_like(imageArray, dtype=np.float32)
        h, w, c = imageArray.shape

        for ch in range(c):
            for i in range(h):
                for j in range(w):
                    region = padded[i:i + kHeight, j:j + kWidth, ch]
                    out[i, j, ch] = np.sum(region * kernelFlipped)
        return out

#Ядро Гаусса
def createGaussianKernel(size, sigma=1.0):
    ax = np.linspace(-(size // 2), size // 2, size)
    gauss = np.exp(-0.5 * np.square(ax) / np.square(sigma))
    kernel = np.outer(gauss, gauss)
    return kernel / np.sum(kernel)

#Фильтер низких частот ФНЧ и ФВЧ в одном приложении
class ImageFilterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.imageNp = None      
        self.resultLpf = None    
        self.resultHpf = None    

    #Отображение пользовательского интерфейса
    def initUI(self):
        self.setWindowTitle('Лабораторная работа № 7')
        self.setGeometry(50, 50, 1300, 700)

        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QHBoxLayout(mainWidget)

        groupOrig = QGroupBox("Исходное изображение")
        layoutOrig = QVBoxLayout()
        
        self.lblOrig = QLabel("Загрузите изображение")
        self.lblOrig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblOrig.setStyleSheet("border: 1px solid #444;")
        layoutOrig.addWidget(self.lblOrig, stretch=1)

        self.btnLoad = QPushButton("Загрузить изображение")
        self.btnLoad.clicked.connect(self.loadImage)
        layoutOrig.addWidget(self.btnLoad)

        self.lblInfo = QLabel("Размер: - x -")
        self.lblInfo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layoutOrig.addWidget(self.lblInfo)

        groupOrig.setLayout(layoutOrig)

        groupLpf = QGroupBox("Фильтрация ФНЧ")
        layoutLpf = QVBoxLayout()

        self.lblLpf = QLabel("Результат ФНЧ появится здесь")
        self.lblLpf.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblLpf.setStyleSheet("border: 1px solid #444;")
        layoutLpf.addWidget(self.lblLpf, stretch=1)

        paramLpfLayout = QHBoxLayout()
        paramLpfLayout.addWidget(QLabel("Размер ядра ФНЧ:"))
        self.comboKernelSize = QComboBox()
        self.comboKernelSize.addItems(["3x3", "5x5", "7x7", "9x9", "11x11"])
        paramLpfLayout.addWidget(self.comboKernelSize)
        layoutLpf.addLayout(paramLpfLayout)

        self.btnApplyLpf = QPushButton("Применить ФНЧ")
        self.btnApplyLpf.setEnabled(False)
        self.btnApplyLpf.clicked.connect(self.applyLpf)
        layoutLpf.addWidget(self.btnApplyLpf)

        self.btnSaveLpf = QPushButton("Сохранить ФНЧ")
        self.btnSaveLpf.setEnabled(False)
        self.btnSaveLpf.clicked.connect(lambda: self.saveImage(self.resultLpf))
        layoutLpf.addWidget(self.btnSaveLpf)

        groupLpf.setLayout(layoutLpf)

        groupHpf = QGroupBox("Фильтрация ФВЧ")
        layoutHpf = QVBoxLayout()

        self.lblHpf = QLabel("Результат ФВЧ появится здесь")
        self.lblHpf.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblHpf.setStyleSheet("border: 1px solid #444;")
        layoutHpf.addWidget(self.lblHpf, stretch=1)

        paramHpfLayout = QHBoxLayout()
        paramHpfLayout.addWidget(QLabel("Сила ФВЧ:"))
        self.spinHpfStrength = QDoubleSpinBox()
        self.spinHpfStrength.setRange(0.1, 10.0)
        self.spinHpfStrength.setSingleStep(0.2)
        self.spinHpfStrength.setValue(1.0)
        paramHpfLayout.addWidget(self.spinHpfStrength)
        layoutHpf.addLayout(paramHpfLayout)

        self.btnApplyHpf = QPushButton("Применить ФВЧ")
        self.btnApplyHpf.setEnabled(False)
        self.btnApplyHpf.clicked.connect(self.applyHpf)
        layoutHpf.addWidget(self.btnApplyHpf)

        self.btnSaveHpf = QPushButton("Сохранить ФВЧ")
        self.btnSaveHpf.setEnabled(False)
        self.btnSaveHpf.clicked.connect(lambda: self.saveImage(self.resultHpf))
        layoutHpf.addWidget(self.btnSaveHpf)

        groupHpf.setLayout(layoutHpf)

        mainLayout.addWidget(groupOrig, stretch=1)
        mainLayout.addWidget(groupLpf, stretch=1)
        mainLayout.addWidget(groupHpf, stretch=1)

    #Загрузка изображения
    def loadImage(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.pbm)"
        )
        if filePath:
            try:
                pilImg = Image.open(filePath).convert('RGB')
                self.imageNp = np.array(pilImg, dtype=np.uint8)
                
                h, w, c = self.imageNp.shape
                self.lblInfo.setText(f"Размер: {w} x {h}")
                
                self.displayImage(self.imageNp, self.lblOrig)
                
                self.btnApplyLpf.setEnabled(True)
                self.btnApplyHpf.setEnabled(True)
                
                self.resultLpf = None
                self.resultHpf = None
                self.btnSaveLpf.setEnabled(False)
                self.btnSaveHpf.setEnabled(False)
                self.lblLpf.setText("Нажмите 'Применить ФНЧ'")
                self.lblHpf.setText("Нажмите 'Применить ФВЧ'")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")

    #Добавить методы для применения ФНЧ и ФВЧ
    def applyLpf(self):
        if self.imageNp is None:
            return

        sizeStr = self.comboKernelSize.currentText()
        kSize = int(sizeStr.split('x')[0])

        h, w, c = self.imageNp.shape
        mid = w // 2

        leftPart = self.imageNp[:, :mid].astype(np.float32)
        rightPart = self.imageNp[:, mid:].astype(np.float32)

        # ФНЧ Усреднение
        kernelBlur = np.ones((kSize, kSize), dtype=np.float32) / float(kSize * kSize)
        leftFiltered = customConvolve2D(leftPart, kernelBlur)

        # ФНЧ Гаусс
        kernelGauss = createGaussianKernel(kSize, sigma=max(1.0, kSize / 3.0))
        rightFiltered = customConvolve2D(rightPart, kernelGauss)

        resFloat = np.hstack((leftFiltered, rightFiltered))
        self.resultLpf = np.clip(resFloat, 0, 255).astype(np.uint8)

        self.displayImage(self.resultLpf, self.lblLpf)
        self.btnSaveLpf.setEnabled(True)

    # Применение ФВЧ с выбранным коэффициентом усиления
    def applyHpf(self):
        if self.imageNp is None:
            return

        strength = self.spinHpfStrength.value()

        gray = np.dot(self.imageNp[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.float32)
        h, w = gray.shape
        mid = w // 2

        # Прюитт
        leftPart = gray[:, :mid]
        px = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
        py = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
        
        gxP = customConvolve2D(leftPart, px)
        gyP = customConvolve2D(leftPart, py)
        gradPrewitt = np.sqrt(gxP**2 + gyP**2) * strength
        gradPrewitt = np.clip(gradPrewitt, 0, 255).astype(np.uint8)

        # Собел 
        rightPart = gray[:, mid:]
        sx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
        sy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
        
        gxS = customConvolve2D(rightPart, sx)
        gyS = customConvolve2D(rightPart, sy)
        gradSobel = np.sqrt(gxS**2 + gyS**2) * strength
        gradSobel = np.clip(gradSobel, 0, 255).astype(np.uint8)

        resGray = np.hstack((gradPrewitt, gradSobel))
        self.resultHpf = np.stack((resGray, resGray, resGray), axis=-1)

        self.displayImage(self.resultHpf, self.lblHpf)
        self.btnSaveHpf.setEnabled(True)

    # Отображение изображения 
    def displayImage(self, imgRgb, label):
        """ Вывод изображения в QLabel """
        h, w, ch = imgRgb.shape
        bytesPerLine = ch * w
        
        qtImg = QImage(imgRgb.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qtImg)
        
        label.setPixmap(pixmap.scaled(
            label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))

    #Сохранение изображения
    def saveImage(self, imgArray):
        if imgArray is not None:
            filePath, selectedFilter = QFileDialog.getSaveFileName(
                self, "Сохранить изображение", "", "PBM Files (*.pbm)"
            )
            if filePath:
                try:
                    if imgArray.ndim == 3:
                        gray = np.dot(imgArray[..., :3], [0.2989, 0.5870, 0.1140])
                    else:
                        gray = imgArray

                    bw = (gray > 128).astype(np.uint8)

                    h, w = bw.shape
                    
                    with open(filePath, 'w') as f:
                        f.write(f"P1\n{w} {h}\n")
                        for row in bw:
                            f.write(" ".join(map(str, row)) + "\n")

                    QMessageBox.information(self, "Успех", "Изображение успешно сохранено в PBM.")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageFilterApp()
    window.show()
    sys.exit(app.exec())