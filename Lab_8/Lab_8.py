# Если не установлен PyQt, напишите в терминале: pip install PyQt6 numpy

import sys
import math
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QLineEdit, QComboBox, QFileDialog, QMessageBox,
    QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QSizePolicy
)
from PyQt6.QtGui import QImage, QPixmap, QPainter
from PyQt6.QtCore import Qt


class ScalableImageCanvas(QFrame):
    """Виджет отображения картинки, не влияющий на размеры окна."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentPixmap = None
        self.setFrameShape(QFrame.Shape.Box)
        self.setStyleSheet("background-color: #FFFFFF; border: 1px solid #C0C0C0;")
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)

    def setPixmap(self, pixmap):
        self.currentPixmap = pixmap
        self.update()

    def clearPixmap(self):
        self.currentPixmap = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.currentPixmap and not self.currentPixmap.isNull():
            painter = QPainter(self)
            scaledPixmap = self.currentPixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            horizontalOffset = (self.width() - scaledPixmap.width()) // 2
            verticalOffset = (self.height() - scaledPixmap.height()) // 2
            painter.drawPixmap(horizontalOffset, verticalOffset, scaledPixmap)


class ImageProcessingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sourceImageArray = None
        self.resultImageArray = None
        self.initializeUserInterface()

    def initializeUserInterface(self):
        self.setWindowTitle("Лабораторная работа №8")
        self.resize(1100, 750)

        centralContainerWidget = QWidget(self)
        self.setCentralWidget(centralContainerWidget)
        mainVerticalLayout = QVBoxLayout(centralContainerWidget)
        mainVerticalLayout.setSpacing(15)
        mainVerticalLayout.setContentsMargins(20, 20, 20, 20)

        controlPanelLayout = QGridLayout()
        controlPanelLayout.setHorizontalSpacing(15)
        controlPanelLayout.setVerticalSpacing(10)

        # Кнопки Открыть / Сохранить
        self.openImageButton = QPushButton("Открыть")
        self.openImageButton.clicked.connect(self.handleOpenImage)
        controlPanelLayout.addWidget(self.openImageButton, 0, 0)

        self.saveImageButton = QPushButton("Сохранить")
        self.saveImageButton.clicked.connect(self.handleSaveImage)
        controlPanelLayout.addWidget(self.saveImageButton, 0, 1)

        # Параметры преобразования
        self.scaleLabel = QLabel("Масштаб:")
        self.scaleLineEdit = QLineEdit("1.0")
        controlPanelLayout.addWidget(self.scaleLabel, 1, 0)
        controlPanelLayout.addWidget(self.scaleLineEdit, 1, 1)

        self.rotationAngleLabel = QLabel("Угол поворота:")
        self.rotationAngleLineEdit = QLineEdit("0.0")
        controlPanelLayout.addWidget(self.rotationAngleLabel, 1, 2)
        controlPanelLayout.addWidget(self.rotationAngleLineEdit, 1, 3)

        self.shearAngleLabel = QLabel("Угол скоса:")
        self.shearAngleLineEdit = QLineEdit("0.0")
        self.shearAngleLineEdit.setPlaceholderText("по оси X")
        controlPanelLayout.addWidget(self.shearAngleLabel, 1, 4)
        controlPanelLayout.addWidget(self.shearAngleLineEdit, 1, 5)

        # Метод интерполяции и кнопка расчета
        self.interpolationMethodLabel = QLabel("Метод интерполяции:")
        self.interpolationComboBox = QComboBox()
        self.interpolationComboBox.addItems([
            "Ближайший сосед",
            "Билинейная",
            "Бикубическая"
        ])
        controlPanelLayout.addWidget(self.interpolationMethodLabel, 2, 0)
        controlPanelLayout.addWidget(self.interpolationComboBox, 2, 1)

        self.applyTransformationButton = QPushButton("Применить")
        self.applyTransformationButton.clicked.connect(self.handleProcessTransformation)
        controlPanelLayout.addWidget(self.applyTransformationButton, 2, 2)

        mainVerticalLayout.addLayout(controlPanelLayout)

        # Белые рамки для картинок
        imageDisplayLayout = QHBoxLayout()
        imageDisplayLayout.setSpacing(20)

        self.sourceImageCanvas = ScalableImageCanvas(self)
        imageDisplayLayout.addWidget(self.sourceImageCanvas, stretch=1)

        self.resultImageCanvas = ScalableImageCanvas(self)
        imageDisplayLayout.addWidget(self.resultImageCanvas, stretch=1)

        mainVerticalLayout.addLayout(imageDisplayLayout, stretch=1)

    def handleOpenImage(self):
        """Окно открытия и загрузки изображения"""
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Изображения (*.png *.jpg *.jpeg *.bmp *.ppm)"
        )
        if filePath:
            sourceQImage = QImage(filePath)
            if sourceQImage.isNull():
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить выбранное изображение.")
                return

            convertedImage = sourceQImage.convertToFormat(QImage.Format.Format_RGB888)
            imageWidth = convertedImage.width()
            imageHeight = convertedImage.height()

            ptr = convertedImage.bits()
            ptr.setsize(imageHeight * imageWidth * 3)
            self.sourceImageArray = np.array(ptr, dtype=np.uint8).reshape((imageHeight, imageWidth, 3)).copy()

            self.updateCanvas(self.sourceImageArray, self.sourceImageCanvas)
            self.resultImageArray = None
            self.resultImageCanvas.clearPixmap()

    def saveImageAsPpm(self, filePath, imageArray):
        """Сохранение изображения в .ppm"""
        height, width, _ = imageArray.shape
        header = f"P6\n{width} {height}\n255\n".encode("ascii")
        with open(filePath, "wb") as fileStream:
            fileStream.write(header)
            fileStream.write(imageArray.tobytes())

    def handleSaveImage(self):
        if self.resultImageArray is None:
            QMessageBox.warning(self, "Предупреждение", "Нет обработанного изображения для сохранения.")
            return

        filePath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить изображение", "result.ppm", "PPM формат (*.ppm)"
        )
        if filePath:
            if not filePath.lower().endswith(".ppm"):
                filePath += ".ppm"

            try:
                self.saveImageAsPpm(filePath, self.resultImageArray)
                QMessageBox.information(self, "Успех", f"Изображение успешно сохранено в файл:\n{filePath}")
            except Exception as saveError:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {saveError}")

    def convertArrayToQImage(self, imageArray):
        height, width, channels = imageArray.shape
        bytesPerLine = channels * width
        return QImage(imageArray.data, width, height, bytesPerLine, QImage.Format.Format_RGB888).copy()

    def updateCanvas(self, imageArray, targetCanvas):
        qImage = self.convertArrayToQImage(imageArray)
        pixmap = QPixmap.fromImage(qImage)
        targetCanvas.setPixmap(pixmap)

    def handleProcessTransformation(self):
        if self.sourceImageArray is None:
            QMessageBox.warning(self, "Предупреждение", "Сначала откройте исходное изображение.")
            return
        try:
            scaleFactor = float(self.scaleLineEdit.text())
            rotationAngle = math.radians(float(self.rotationAngleLineEdit.text()))
            shearAngle = math.radians(float(self.shearAngleLineEdit.text()))
            if scaleFactor <= 0:
                raise ValueError("Масштаб должен быть больше нуля")
        except ValueError as parsingError:
            QMessageBox.critical(self, "Ошибка параметров", f"Некорректное значение: {parsingError}")
            return

        interpolationMethod = self.interpolationComboBox.currentText()

        scaleMatrix = np.array([
            [scaleFactor, 0.0, 0.0],
            [0.0, scaleFactor, 0.0],
            [0.0, 0.0, 1.0]
        ])

        cosVal = math.cos(rotationAngle)
        sinVal = math.sin(rotationAngle)
        rotationMatrix = np.array([
            [cosVal, -sinVal, 0.0],
            [sinVal, cosVal, 0.0],
            [0.0, 0.0, 1.0]
        ])

        shearX = math.tan(shearAngle)
        shearMatrix = np.array([
            [1.0, shearX, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])

        forwardAffineMatrix = shearMatrix @ rotationMatrix @ scaleMatrix
        sourceHeight, sourceWidth, _ = self.sourceImageArray.shape

        sourceCorners = np.array([
            [0, 0, 1],
            [sourceWidth, 0, 1],
            [sourceWidth, sourceHeight, 1],
            [0, sourceHeight, 1]
        ]).T

        transformedCorners = forwardAffineMatrix @ sourceCorners
        transformedX = transformedCorners[0, :]
        transformedY = transformedCorners[1, :]

        minX, maxX = np.min(transformedX), np.max(transformedX)
        minY, maxY = np.min(transformedY), np.max(transformedY)

        newWidth = max(1, int(np.ceil(maxX - minX)))
        newHeight = max(1, int(np.ceil(maxY - minY)))

        if newWidth > 4000 or newHeight > 4000:
            QMessageBox.warning(self, "Внимание", "Размер результирующего изображения слишком большой. Уменьшите масштаб.")
            return

        shiftToOriginMatrix = np.array([
            [1.0, 0.0, -minX],
            [0.0, 1.0, -minY],
            [0.0, 0.0, 1.0]
        ])

        completeForwardMatrix = shiftToOriginMatrix @ forwardAffineMatrix
        inverseAffineMatrix = np.linalg.inv(completeForwardMatrix)

        self.resultImageArray = self.interpolateImage(
            self.sourceImageArray,
            newWidth,
            newHeight,
            inverseAffineMatrix,
            interpolationMethod
        )

        self.updateCanvas(self.resultImageArray, self.resultImageCanvas)

    def interpolateImage(self, sourceImage, targetWidth, targetHeight, inverseTransformMatrix, interpolationMethod):
        """Интерполяция изображения с использованием заданного метода."""
        sourceHeight, sourceWidth, channels = sourceImage.shape
        resultImage = np.full((targetHeight, targetWidth, channels), 255, dtype=np.uint8)

        gridX, gridY = np.meshgrid(np.arange(targetWidth), np.arange(targetHeight))
        homogeneousCoordinates = np.stack([gridX.ravel(), gridY.ravel(), np.ones(gridX.size)], axis=0)

        sourceCoordinates = inverseTransformMatrix @ homogeneousCoordinates
        sourceCoordX = sourceCoordinates[0, :].reshape((targetHeight, targetWidth))
        sourceCoordY = sourceCoordinates[1, :].reshape((targetHeight, targetWidth))

        # Интерполяция по ближайшему соседу
        if interpolationMethod == "Ближайший сосед":
            nearestX = np.round(sourceCoordX).astype(np.int32)
            nearestY = np.round(sourceCoordY).astype(np.int32)

            validMask = (nearestX >= 0) & (nearestX < sourceWidth) & (nearestY >= 0) & (nearestY < sourceHeight)
            resultImage[validMask] = sourceImage[nearestY[validMask], nearestX[validMask]]

        # Билинейная интерполяция
        elif interpolationMethod == "Билинейная":
            validMask = (sourceCoordX >= 0) & (sourceCoordX < sourceWidth - 1) & \
                        (sourceCoordY >= 0) & (sourceCoordY < sourceHeight - 1)

            validX = sourceCoordX[validMask]
            validY = sourceCoordY[validMask]

            baseL = np.floor(validX).astype(np.int32)
            baseK = np.floor(validY).astype(np.int32)
            alpha = (validX - baseL)[:, np.newaxis]
            beta = (validY - baseK)[:, np.newaxis]

            f_l_k = sourceImage[baseK, baseL].astype(np.float64)
            f_lp1_k = sourceImage[baseK, baseL + 1].astype(np.float64)
            f_l_kp1 = sourceImage[baseK + 1, baseL].astype(np.float64)
            f_lp1_kp1 = sourceImage[baseK + 1, baseL + 1].astype(np.float64)

            interpolatedValues = (
                (1.0 - alpha) * (1.0 - beta) * f_l_k +
                alpha * (1.0 - beta) * f_lp1_k +
                beta * (1.0 - alpha) * f_l_kp1 +
                alpha * beta * f_lp1_kp1
            )

            resultImage[validMask] = np.clip(interpolatedValues, 0, 255).astype(np.uint8)

        # Бикубическая интерполяция
        elif interpolationMethod == "Бикубическая":
            validMask = (sourceCoordX >= 1) & (sourceCoordX < sourceWidth - 2) & \
                        (sourceCoordY >= 1) & (sourceCoordY < sourceHeight - 2)

            validX = sourceCoordX[validMask]
            validY = sourceCoordY[validMask]

            baseL = np.floor(validX).astype(np.int32)
            baseK = np.floor(validY).astype(np.int32)
            paramA = (validX - baseL)[:, np.newaxis]
            paramB = (validY - baseK)[:, np.newaxis]

            c1 = (paramA - 1) * (paramA - 2) * (paramA + 1) * (paramB - 1) * (paramB - 2) * (paramB + 1) / 4.0
            c2 = -paramA * (paramA - 2) * (paramA + 1) * (paramB - 1) * (paramB - 2) * (paramB + 1) / 4.0
            c3 = paramB * (paramA - 1) * (paramA - 2) * (paramA + 1) * (paramB - 2) * (paramB + 1) / 4.0
            c4 = paramA * paramB * (paramA - 2) * (paramA + 1) * (paramB - 2) * (paramB + 1) / 4.0

            c5 = -paramA * (paramA - 1) * (paramA - 2) * (paramB - 1) * (paramB - 2) * (paramB + 1) / 12.0
            c6 = -paramB * (paramA - 1) * (paramA - 2) * (paramA + 1) * (paramB - 1) * (paramB - 2) / 12.0
            c7 = paramA * paramB * (paramA - 1) * (paramA - 2) * (paramB - 2) * (paramB + 1) / 12.0
            c8 = paramA * paramB * (paramA - 2) * (paramA + 1) * (paramB - 1) * (paramB - 2) / 12.0

            c9 = paramA * (paramA - 1) * (paramA + 1) * (paramB - 1) * (paramB - 2) * (paramB + 1) / 12.0
            c10 = paramB * (paramA - 1) * (paramA - 2) * (paramA + 1) * (paramB - 1) * (paramB + 1) / 12.0
            c11 = paramA * paramB * (paramA - 1) * (paramA - 2) * (paramB - 1) * (paramB - 2) / 36.0
            c12 = -paramA * paramB * (paramA - 1) * (paramA + 1) * (paramB - 2) * (paramB + 1) / 12.0

            c13 = -paramA * paramB * (paramA - 2) * (paramA + 1) * (paramB - 1) * (paramB + 1) / 12.0
            c14 = -paramA * paramB * (paramA - 1) * (paramA + 1) * (paramB - 1) * (paramB - 2) / 36.0
            c15 = -paramA * paramB * (paramA - 1) * (paramA - 2) * (paramB - 1) * (paramB + 1) / 36.0
            c16 = paramA * paramB * (paramA - 1) * (paramA + 1) * (paramB - 1) * (paramB + 1) / 36.0

            interpolatedValues = (
                c1  * sourceImage[baseK,     baseL    ].astype(np.float64) +
                c2  * sourceImage[baseK + 1, baseL    ].astype(np.float64) +
                c3  * sourceImage[baseK,     baseL + 1].astype(np.float64) +
                c4  * sourceImage[baseK + 1, baseL + 1].astype(np.float64) +
                c5  * sourceImage[baseK - 1, baseL    ].astype(np.float64) +
                c6  * sourceImage[baseK,     baseL - 1].astype(np.float64) +
                c7  * sourceImage[baseK - 1, baseL + 1].astype(np.float64) +
                c8  * sourceImage[baseK + 1, baseL - 1].astype(np.float64) +
                c9  * sourceImage[baseK + 2, baseL    ].astype(np.float64) +
                c10 * sourceImage[baseK,     baseL + 2].astype(np.float64) +
                c11 * sourceImage[baseK - 1, baseL - 1].astype(np.float64) +
                c12 * sourceImage[baseK + 2, baseL + 1].astype(np.float64) +
                c13 * sourceImage[baseK + 1, baseL + 2].astype(np.float64) +
                c14 * sourceImage[baseK + 2, baseL - 1].astype(np.float64) +
                c15 * sourceImage[baseK - 1, baseL + 2].astype(np.float64) +
                c16 * sourceImage[baseK + 2, baseL + 2].astype(np.float64)
            )

            resultImage[validMask] = np.clip(interpolatedValues, 0, 255).astype(np.uint8)

        return resultImage


if __name__ == "__main__":
    application = QApplication(sys.argv)
    mainWindow = ImageProcessingWindow()
    mainWindow.show()
    sys.exit(application.exec())