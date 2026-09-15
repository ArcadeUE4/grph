# Для установки Qt, напишите в терминале pip install PyQt6

import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QPoint


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №2")
        self.setFixedSize(920, 520)

        # Хранение изображений
        self.imageLeft_data = None   
        self.imageRight_data = None  

        self._initUI()

    def _initUI(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        
        # Поля размеров для создания нового изображения
        lblW1 = QLabel("Ширина 1", centralWidget)
        lblW1.setGeometry(60, 15, 50, 20)
        self.edit6 = QLineEdit("300", centralWidget)
        self.edit6.setGeometry(115, 15, 55, 22)

        lblH1 = QLabel("Высота 1", centralWidget)
        lblH1.setGeometry(60, 42, 50, 20)
        self.edit7 = QLineEdit("300", centralWidget)
        self.edit7.setGeometry(115, 42, 55, 22)

        self.btnCreate = QPushButton("Создать 1", centralWidget)
        self.btnCreate.setGeometry(185, 15, 75, 25)
        self.btnCreate.clicked.connect(self.createCanvas)

        self.btnOpen = QPushButton("Открыть 2", centralWidget)
        self.btnOpen.setGeometry(270, 15, 75, 25)
        self.btnOpen.clicked.connect(self.openImage)

        lblW2Title = QLabel("Ширина 2", centralWidget)
        lblW2Title.setGeometry(220, 40, 50, 18)
        self.lbl6 = QLabel("0", centralWidget)
        self.lbl6.setGeometry(275, 40, 60, 18)

        lblH2Title = QLabel("Высота 2", centralWidget)
        lblH2Title.setGeometry(220, 58, 50, 18)
        self.lbl8 = QLabel("0", centralWidget)
        self.lbl8.setGeometry(275, 58, 60, 18)

        # Поля параметров переноса 
        lblX1 = QLabel("x1", centralWidget)
        lblX1.setGeometry(370, 15, 20, 20)
        self.edit1 = QLineEdit("100", centralWidget)
        self.edit1.setGeometry(390, 15, 50, 22)

        lblY1 = QLabel("y1", centralWidget)
        lblY1.setGeometry(370, 42, 20, 20)
        self.edit2 = QLineEdit("70", centralWidget)
        self.edit2.setGeometry(390, 42, 50, 22)

        lblR = QLabel("R", centralWidget)
        lblR.setGeometry(460, 15, 15, 20)
        self.edit3 = QLineEdit("100", centralWidget)
        self.edit3.setGeometry(480, 15, 50, 22)

        lblX2 = QLabel("x2", centralWidget)
        lblX2.setGeometry(550, 15, 20, 20)
        self.edit4 = QLineEdit("200", centralWidget)
        self.edit4.setGeometry(570, 15, 50, 22)

        lblY2 = QLabel("y2", centralWidget)
        lblY2.setGeometry(550, 42, 20, 20)
        self.edit5 = QLineEdit("150", centralWidget)
        self.edit5.setGeometry(570, 42, 50, 22)

        self.btnPost = QPushButton("Перенести", centralWidget)
        self.btnPost.setGeometry(650, 15, 75, 25)
        self.btnPost.clicked.connect(self.transferFragment)

        self.btnCoord = QPushButton("Координаты", centralWidget)
        self.btnCoord.setGeometry(735, 15, 80, 25)
        self.btnCoord.clicked.connect(self.drawCoordinates)

        self.btnSave = QPushButton("Сохранить", centralWidget)
        self.btnSave.setGeometry(825, 15, 75, 25)
        self.btnSave.clicked.connect(self.saveCanvas)

        self.btnSin = QPushButton("Sinx", centralWidget)
        self.btnSin.setGeometry(735, 45, 80, 25)
        self.btnSin.clicked.connect(self.drawSinx)

        # Область отображения изображении
        self.imageLeft = QLabel(centralWidget)
        self.imageLeft.setGeometry(20, 95, 360, 390)
        self.imageLeft.setStyleSheet("border: 1px solid #777; background-color: #ffffff;")
        self.imageLeft.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.imageRight = QLabel(centralWidget)
        self.imageRight.setGeometry(470, 95, 430, 390)
        self.imageRight.setStyleSheet("border: 1px solid #777; background-color: #ffffff;")
        self.imageRight.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)


    # Создание нового изображения
    def createCanvas(self):
        """ Создает белое изображение заданного размера """
        try:
            w = int(self.edit6.text())
            h = int(self.edit7.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректные размеры холста!")
            return

        self.imageLeft_data = QImage(w, h, QImage.Format.Format_RGB888)
        self.imageLeft_data.fill(QColor(255, 255, 255))
        self._updateImageLeftDisplay()

    # Открытие изображения с проводника
    def openImage(self):
        """ Открывает изображение с проводника """
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Открыть картинку", "", "Картинки (*.bmp *.png *.jpg *.jpeg *.pbm)"
        )
        if filePath:
            loaded = QImage(filePath)
            if loaded.isNull():
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить картинку.")
                return

            self.imageRight_data = loaded.convertToFormat(QImage.Format.Format_RGB888)
            self.lbl6.setText(str(self.imageRight_data.width()))
            self.lbl8.setText(str(self.imageRight_data.height()))
            self._updateImageRightDisplay()

    # Перенес фрагмента изображения по окружности
    def transferFragment(self):
        """ Попиксельный перенос фрагмента по окружности """
        if not self.imageLeft_data or not self.imageRight_data:
            QMessageBox.warning(self, "Ошибка", "Сначала создайте новое изображение и откройте исходное!")
            return

        try:
            x1 = int(self.edit1.text())
            y1 = int(self.edit2.text())
            r = int(self.edit3.text())
            x2 = int(self.edit4.text())
            y2 = int(self.edit5.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Проверьте числовые значения параметров!")
            return

        dx = x1 - x2
        dy = y1 - y2

        w1 = self.imageLeft_data.width()
        h1 = self.imageLeft_data.height()
        w2 = self.imageRight_data.width()
        h2 = self.imageRight_data.height()

        painter2 = QPainter(self.imageRight_data)

        for py in range(h1):
            for px in range(w1):
                dist = round(math.sqrt((py - y1) ** 2 + (px - x1) ** 2))
                
                if dist < r:
                    srcX = px - dx
                    srcY = py - dy
                    if 0 <= srcX < w2 and 0 <= srcY < h2:
                        color = self.imageRight_data.pixelColor(srcX, srcY)
                        self.imageLeft_data.setPixelColor(px, py, color)
                    else:
                        self.imageLeft_data.setPixelColor(px, py, QColor(0, 0, 0))

                elif dist == r:
                    self.imageLeft_data.setPixelColor(px, py, QColor(127, 255, 127))
                    srcX = px - dx
                    srcY = py - dy
                    if 0 <= srcX < w2 and 0 <= srcY < h2:
                        painter2.setPen(QPen(QColor(255, 127, 127), 1))
                        painter2.drawPoint(srcX, srcY)

        painter2.end()
        self._updateImageLeftDisplay()
        self._updateImageRightDisplay()

    def drawCoordinates(self):
        """ Рисует декартову сетку осей координат с отсечками """
        if not self.imageLeft_data:
            QMessageBox.warning(self, "Ошибка", "Сначала нажмите 'Создать 1'")
            return

        w = self.imageLeft_data.width()
        h = self.imageLeft_data.height()

        painter = QPainter(self.imageLeft_data)
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setFont(QFont("Arial", 8))

        # Ось OY и стрелка
        painter.drawPolyline([QPoint(10, h - 10), QPoint(10, 10)])
        painter.drawPolyline([QPoint(5, 20), QPoint(10, 10), QPoint(15, 20)])

        # Ось OX и стрелка
        cy = h // 2
        painter.drawPolyline([QPoint(8, cy), QPoint(w - 10, cy)])
        painter.drawPolyline([QPoint(w - 20, cy - 5), QPoint(w - 10, cy), QPoint(w - 20, cy + 5)])

        # Засечки по OY
        for i in range((h - 40) // 20):
            painter.drawPolyline([QPoint(10, i * 10 + cy), QPoint(8, i * 10 + cy)])
            painter.drawPolyline([QPoint(10, cy - i * 10), QPoint(8, cy - i * 10)])

        # Засечки по OX
        for i in range((w - 40) // 10):
            painter.drawPolyline([QPoint((i + 1) * 10, cy), QPoint((i + 1) * 10, cy + 2)])

        # Текстовые метки
        painter.drawText(1, cy + 12, "0")
        painter.drawText(w - 20, cy + 18, "x")
        painter.drawText(20, 12, "y")

        painter.end()
        self._updateImageLeftDisplay()

    # Отображение по синусу
    def drawSinx(self):
        """ Рисует график функции y = sin(x) """
        if not self.imageLeft_data:
            QMessageBox.warning(self, "Ошибка", "Сначала нажмите 'Создать 1'")
            return

        w = self.imageLeft_data.width()
        h = self.imageLeft_data.height()

        painter = QPainter(self.imageLeft_data)
        painter.setPen(QPen(QColor(127, 127, 255), 1))
        painter.setFont(QFont("Arial", 9))

        # 1. Заголовок графика
        painter.drawText(w // 2, 15, "y=sin(x)")

        cy = h // 2
        amplitude = 50  # Амплитуда волны в пикселях (высота)
        frequency = 0.05 # Масштаб частоты по оси X

        # 2. Построение синусоиды
        points = []
        for i in range(0, w - 20):
            x = i * frequency
            val = math.sin(x)  # Чистый sin(x)
            py = cy - round(val * amplitude)
            points.append(QPoint(i + 10, py))

        if points:
            painter.drawPolyline(points)

        painter.end()
        self._updateImageLeftDisplay()

    # Сохранение изображения в BMP или PBM
    def saveCanvas(self):
        """ Сохраняет imageLeft в BMP или PBM """
        if not self.imageLeft_data:
            QMessageBox.warning(self, "Ошибка", "Нет созданного изображения для сохранения!")
            return

        filePath, selectedFilter = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Bitmap (*.bmp);;Portable BitMap (*.pbm);;Все файлы (*.*)"
        )

        if filePath:
            ext = filePath.split('.')[-1].lower()
            if ext == "pbm" or "pbm" in selectedFilter.lower():
                monoImg = self.imageLeft_data.convertToFormat(QImage.Format.Format_Mono)
                success = monoImg.save(filePath, "PBM")
            else:
                success = self.imageLeft_data.save(filePath, "BMP")

            if success:
                QMessageBox.information(self, "Готово", f"Файл сохранен: {filePath}")

    # Вспомогательные методы для обновления отображения изображений
    def _updateImageLeftDisplay(self):
        if self.imageLeft_data:
            pix = QPixmap.fromImage(self.imageLeft_data)
            self.imageLeft.setPixmap(pix)

    def _updateImageRightDisplay(self):
        if self.imageRight_data:
            pix = QPixmap.fromImage(self.imageRight_data)
            scaledPix = pix.scaled(
                self.imageRight.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.imageRight.setPixmap(scaledPix)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())