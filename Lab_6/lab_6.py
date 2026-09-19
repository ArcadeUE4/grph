#Если не установлен PyQt, напишите в терминале pip Install PyQt6

import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QGroupBox, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QImage, QPixmap, QColor
from PyQt6.QtCore import Qt


class ImageProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа № 6")
        self.resize(1100, 800)

        self.srcImage: QImage = None
        self.affineDirectImg: QImage = None
        self.affineInverseImg: QImage = None
        self.funcTransformedImg: QImage = None

        self.initUi()

    # Инициализация пользовательского интерфейса
    def initUi(self):
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QVBoxLayout(mainWidget)

        controlPanel = QHBoxLayout()
        
        controlPanel.addWidget(QLabel("Угол поворота (град):"))
        self.editAngle = QLineEdit("30")
        self.editAngle.setFixedWidth(60)
        controlPanel.addWidget(self.editAngle)

        controlPanel.addWidget(QLabel("Масштаб (k):"))
        self.editScale = QLineEdit("2.0")
        self.editScale.setFixedWidth(60)
        controlPanel.addWidget(self.editScale)

        self.lblInfo = QLabel("Размер: - x - px")
        controlPanel.addWidget(self.lblInfo)
        controlPanel.addStretch()

        mainLayout.addLayout(controlPanel)

        gridLayout = QGridLayout()

        boxSrc, self.lblSrc = self.createImageBox(
            "Исходное изображение",
            [("Загрузить изображение", self.loadImage)]
        )
        gridLayout.addWidget(boxSrc, 0, 0)

        boxAff1, self.lblAff1 = self.createImageBox(
            "Прямое аффинное", 
            [("Выполнить прямое", self.processAffineDirect), ("Сохранить", self.saveAffineDirect)]
        )
        gridLayout.addWidget(boxAff1, 0, 1)

        boxAff2, self.lblAff2 = self.createImageBox(
            "Обратное аффинное", 
            [("Выполнить обратное", self.processAffineInverse), ("Сохранить", self.saveAffineInverse)]
        )
        gridLayout.addWidget(boxAff2, 1, 0)

        boxFunc, self.lblFunc = self.createImageBox(
            "Функциональное преобразование", 
            [("Выполнить функц.", self.processFunctional), ("Сохранить", self.saveFunctional)]
        )
        gridLayout.addWidget(boxFunc, 1, 1)

        mainLayout.addLayout(gridLayout)

    def createImageBox(self, title, buttons=None):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)

        lbl = QLabel("Нет изображения")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("border: 1px dashed #aaa; background-color: #f9f9f9;")
        lbl.setMinimumSize(320, 240)
        layout.addWidget(lbl)

        if buttons:
            btnLayout = QHBoxLayout()
            for text, callback in buttons:
                b = QPushButton(text)
                b.clicked.connect(callback)
                btnLayout.addWidget(b)
            layout.addLayout(btnLayout)

        return group, lbl

    # Вспомогательный метод с сохранением пропорций
    def displayQImage(self, qImg: QImage, targetLabel: QLabel):
        if qImg is None or qImg.isNull():
            targetLabel.setText("Нет изображения")
            return
        
        pixmap = QPixmap.fromImage(qImg)
        scaledPixmap = pixmap.scaled(
            320, 240, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        targetLabel.setPixmap(scaledPixmap)

    # Загрузка изображения
    def loadImage(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", "", "Изображения ( *.png *.jpg *.jpeg)"
        )
        if filePath:
            img = QImage(filePath)
            if img.isNull():
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение")
                return
            
            self.srcImage = img.convertToFormat(QImage.Format.Format_RGB32)
            
            w = self.srcImage.width()
            h = self.srcImage.height()
            self.lblInfo.setText(f"Размер: {w} x {h} px")
            self.displayQImage(self.srcImage, self.lblSrc)

    # Прямое аффинное преобразование
    def processAffineDirect(self):
        if self.srcImage is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите исходное изображение в блоке 1!")
            return

        try:
            angleDeg = float(self.editAngle.text())
            scale = float(self.editScale.text())
            if scale <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Некорректный угол или масштаб !")
            return

        phi = math.radians(angleDeg)
        w = self.srcImage.width()
        h = self.srcImage.height()
        cx, cy = w // 2, h // 2

        destImg = QImage(w, h, QImage.Format.Format_RGB32)
        destImg.fill(QColor(255, 255, 255))

        cosPhi = math.cos(phi)
        sinPhi = math.sin(phi)

        for i in range(w):
            dx = i - cx
            for j in range(h):
                dy = j - cy

                i1 = round(((dx * cosPhi - dy * sinPhi) / scale) + cx)
                j1 = round(((dx * sinPhi + dy * cosPhi) / scale) + cy)

                if 0 <= i1 < w and 0 <= j1 < h:
                    pixelColor = self.srcImage.pixelColor(i1, j1)
                    destImg.setPixelColor(i, j, pixelColor)

        self.affineDirectImg = destImg
        self.displayQImage(self.affineDirectImg, self.lblAff1)

    # Обратное аффинное преобразование
    def processAffineInverse(self):
        if self.affineDirectImg is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните прямое аффинное преобразование")
            return

        try:
            angleDeg = float(self.editAngle.text())
            scale = float(self.editScale.text())
            if scale <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Некорректный угол или масштаб!")
            return

        phi = math.radians(angleDeg)
        w = self.affineDirectImg.width()
        h = self.affineDirectImg.height()
        cx, cy = w // 2, h // 2

        destImg = QImage(w, h, QImage.Format.Format_RGB32)
        destImg.fill(QColor(255, 255, 255))

        cosPhi = math.cos(-phi)
        sinPhi = math.sin(-phi)

        for i in range(w):
            dx = i - cx
            for j in range(h):
                dy = j - cy

                i1 = round(((dx * cosPhi - dy * sinPhi) * scale) + cx)
                j1 = round(((dx * sinPhi + dy * cosPhi) * scale) + cy)

                if 0 <= i1 < w and 0 <= j1 < h:
                    pixelColor = self.affineDirectImg.pixelColor(i1, j1)
                    destImg.setPixelColor(i, j, pixelColor)

        self.affineInverseImg = destImg
        self.displayQImage(self.affineInverseImg, self.lblAff2)

    # Процесс функционального преобразования
    def processFunctional(self):
        if self.srcImage is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите исходное изображение в блоке 1")
            return

        w = self.srcImage.width()
        h = self.srcImage.height()

        destImg = QImage(w, h, QImage.Format.Format_RGB32)
        destImg.fill(QColor(255, 255, 255))

        for i in range(w):
            for j in range(h):
                i1 = round(i - 20 * math.sin(j * math.pi / 64.0))
                j1 = round(j)

                if 0 <= i1 < w and 0 <= j1 < h:
                    pixelColor = self.srcImage.pixelColor(i1, j1)
                    destImg.setPixelColor(i, j, pixelColor)

        self.funcTransformedImg = destImg
        self.displayQImage(self.funcTransformedImg, self.lblFunc)

    # Сохранение изображения 
    def saveImage(self, qImg: QImage):
        if qImg is None or qImg.isNull():
            QMessageBox.warning(self, "Ошибка", "Нет изображения для сохранения")
            return
        
        filePath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить изображение в PBM", "", "Portable Bitmap (*.pbm)"
        )
        if filePath:
            if not filePath.lower().endswith('.pbm'):
                filePath += '.pbm'
            
            pbmImage = qImg.convertToFormat(QImage.Format.Format_Mono)
            if not pbmImage.save(filePath, "PBM"):
                QMessageBox.critical(self, "Ошибка", "Не удалось сохранить файл в формате .pbm")

    # Cохранение прямого аффинного преобразования
    def saveAffineDirect(self):
        self.saveImage(self.affineDirectImg)
    # Cохранение обратного аффинного преобразования
    def saveAffineInverse(self):
        self.saveImage(self.affineInverseImg)
    # Cохранение функционального преобразования
    def saveFunctional(self):
        self.saveImage(self.funcTransformedImg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessingApp()
    window.show()
    sys.exit(app.exec())