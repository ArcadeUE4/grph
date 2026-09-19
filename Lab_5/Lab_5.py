import sys
import colorsys
import numpy as np
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt


class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.firstImage = None
        self.secondImage = None
        self.processedImage = None
        self.blendedImage = None

        self.canvasWidth = 320
        self.canvasHeight = 220

        self.initUi()

    def initUi(self):
        self.setWindowTitle("Лабораторная работа №5")
        self.resize(850, 560)

        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setSpacing(15)

        
        topLayout = QHBoxLayout()

        self.firstInputLabel = self.createImageFrame()
        self.firstOutputLabel = self.createImageFrame()

        topButtonLayout = QVBoxLayout()
        topButtonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.openFirstButton = QPushButton("Открыть изображение")
        self.openFirstButton.clicked.connect(self.loadFirstImage)

        self.processButton = QPushButton("Преобразовать")
        self.processButton.clicked.connect(self.processFirstImage)

        self.saveFirstButton = QPushButton("Сохранить")
        self.saveFirstButton.clicked.connect(self.saveFirstToPbm)

        topButtonLayout.addWidget(self.openFirstButton)
        topButtonLayout.addWidget(self.processButton)
        topButtonLayout.addWidget(self.saveFirstButton)

        topLayout.addWidget(self.firstInputLabel)
        topLayout.addLayout(topButtonLayout)
        topLayout.addWidget(self.firstOutputLabel)

        bottomLayout = QHBoxLayout()

        self.secondInputLabel = self.createImageFrame()
        self.secondOutputLabel = self.createImageFrame()

        bottomButtonLayout = QVBoxLayout()
        bottomButtonLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.openSecondButton = QPushButton("Открыть изображение")
        self.openSecondButton.clicked.connect(self.loadSecondImage)

        self.blendButton = QPushButton("Наложить")
        self.blendButton.clicked.connect(self.blendImages)

        self.saveSecondButton = QPushButton("Сохранить")
        self.saveSecondButton.clicked.connect(self.saveSecondToPbm)

        bottomButtonLayout.addWidget(self.openSecondButton)
        bottomButtonLayout.addWidget(self.blendButton)
        bottomButtonLayout.addWidget(self.saveSecondButton)

        bottomLayout.addWidget(self.secondInputLabel)
        bottomLayout.addLayout(bottomButtonLayout)
        bottomLayout.addWidget(self.secondOutputLabel)

        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(bottomLayout)

    # Создание рамки для отображения изображения
    def createImageFrame(self):
        label = QLabel()
        label.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        label.setStyleSheet("background-color: white;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFixedSize(self.canvasWidth, self.canvasHeight)
        label.setScaledContents(False)
        return label

    # Вписывание изображения в размер холста
    def displayScaledImage(self, qImage, targetLabel):
        pixmap = QPixmap.fromImage(qImage)
        scaledPixmap = pixmap.scaled(
            targetLabel.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        targetLabel.setPixmap(scaledPixmap)

    # Загрузка первого изображения
    def loadFirstImage(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Выберите первое изображение", "", "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if filePath:
            self.firstImage = QImage(filePath).convertToFormat(QImage.Format.Format_RGB888)
            self.displayScaledImage(self.firstImage, self.firstInputLabel)

    # Загрузка второго изображения
    def loadSecondImage(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Выберите второе изображение", "", "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if filePath:
            self.secondImage = QImage(filePath).convertToFormat(QImage.Format.Format_RGB888)
            self.displayScaledImage(self.secondImage, self.secondInputLabel)

    # Преобразование первого изображения
    def processFirstImage(self):
        
        if not self.firstImage:
            QMessageBox.warning(self, "Ошибка", "Загрузите первое изображение!")
            return

        width = self.firstImage.width()
        height = self.firstImage.height()
        resultImage = QImage(width, height, QImage.Format.Format_RGB888)

        for currentY in range(height):
            for currentX in range(width):
                pixelColor = self.firstImage.pixelColor(currentX, currentY)
                redComponent = pixelColor.red() / 255.0
                greenComponent = pixelColor.green() / 255.0
                blueComponent = pixelColor.blue() / 255.0

                hueComponent, saturationComponent, valueComponent = colorsys.rgb_to_hsv(
                    redComponent, greenComponent, blueComponent
                )

                if valueComponent > 0.5:
                    saturationComponent = min(1.0, saturationComponent * 1.30)

                newRed, newGreen, newBlue = colorsys.hsv_to_rgb(
                    hueComponent, saturationComponent, valueComponent
                )

                pixelColor.setRgb(
                    int(newRed * 255),
                    int(newGreen * 255),
                    int(newBlue * 255)
                )
                resultImage.setPixelColor(currentX, currentY, pixelColor)

        self.processedImage = resultImage
        self.displayScaledImage(self.processedImage, self.firstOutputLabel)

    # Аддитивное наложение изображения
    def blendImages(self):
        if not self.processedImage or not self.secondImage:
            QMessageBox.warning(
                self, "Ошибка", "Сначала обработайте 1 фото и загрузите 2 фото!"
            )
            return

        targetWidth = min(self.processedImage.width(), self.secondImage.width())
        targetHeight = min(self.processedImage.height(), self.secondImage.height())

        resultImage = QImage(targetWidth, targetHeight, QImage.Format.Format_RGB888)

        for currentY in range(targetHeight):
            for currentX in range(targetWidth):
                firstColor = self.processedImage.pixelColor(currentX, currentY)
                secondColor = self.secondImage.pixelColor(currentX, currentY)

                additiveRed = min(255, firstColor.red() + secondColor.red())
                additiveGreen = min(255, firstColor.green() + secondColor.green())
                additiveBlue = min(255, firstColor.blue() + secondColor.blue())

                firstColor.setRgb(additiveRed, additiveGreen, additiveBlue)
                resultImage.setPixelColor(currentX, currentY, firstColor)

        self.blendedImage = resultImage
        self.displayScaledImage(self.blendedImage, self.secondOutputLabel)

    #Сохраниение в .pbm
    def exportImageToPbm(self, qImage):
        filePath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл как PBM", "", "Portable Bitmap (*.pbm)"
        )
        if filePath:
            if not filePath.endswith(".pbm"):
                filePath += ".pbm"

            targetWidth = qImage.width()
            targetHeight = qImage.height()
            pixelBuffer = np.zeros((targetHeight, targetWidth), dtype=np.uint8)

            for currentY in range(targetHeight):
                for currentX in range(targetWidth):
                    pixelColor = qImage.pixelColor(currentX, currentY)
                    luminance = (
                        0.299 * pixelColor.red() +
                        0.587 * pixelColor.green() +
                        0.114 * pixelColor.blue()
                    )
                    pixelBuffer[currentY, currentX] = 255 if luminance > 128 else 0

            pilImage = Image.fromarray(pixelBuffer).convert("1")
            # Заменяем format="PBM" на format="PPM"
            pilImage.save(filePath, format="PPM")
            QMessageBox.information(self, "Успех", f"Файл сохранен: {filePath}")

    #Сохранение первого изображения в .pbm
    def saveFirstToPbm(self):
        if not self.processedImage:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните преобразование!")
            return
        self.exportImageToPbm(self.processedImage)
        
    #Сохранение второго изображения в .pbm
    def saveSecondToPbm(self):
        if not self.blendedImage:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните наложение!")
            return
        self.exportImageToPbm(self.blendedImage)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec())