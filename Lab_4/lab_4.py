#Если не установлен PyQt, напишите в терминале pip Install PyQt6

import math
import sys
import xml.etree.ElementTree as ET

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)


class CircleSquareApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №4")
        self.resize(950, 700)

        self.canvasImage = None
        self.svgLines = []

        self.initUi()
        self.createCanvas(500, 500)

    def initUi(self):
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QVBoxLayout(mainWidget)

        # Верхняя панель с настройками и действиями
        topLayout = QHBoxLayout()

        # 1. Настройки холста
        groupCanvas = QGroupBox("Настройки холста")
        layoutCanvas = QHBoxLayout()

        labelWidth = QLabel("Ширина:")
        self.inputWidth = QLineEdit("500")
        self.inputWidth.setFixedWidth(45)

        labelHeight = QLabel("Высота:")
        self.inputHeight = QLineEdit("500")
        self.inputHeight.setFixedWidth(45)

        buttonCreateCanvas = QPushButton("Создать")
        buttonCreateCanvas.clicked.connect(self.onCreateCanvasClick)

        layoutCanvas.addWidget(labelWidth)
        layoutCanvas.addWidget(self.inputWidth)
        layoutCanvas.addWidget(labelHeight)
        layoutCanvas.addWidget(self.inputHeight)
        layoutCanvas.addWidget(buttonCreateCanvas)
        groupCanvas.setLayout(layoutCanvas)

        # 2. Параметры фигуры
        centerVerticalLayout = QVBoxLayout()

        groupSquare = QGroupBox("Параметры фигуры")
        layoutSquare = QHBoxLayout()

        labelCenterX = QLabel("Центр X:")
        self.inputCenterX = QLineEdit("250")
        self.inputCenterX.setFixedWidth(40)

        labelCenterY = QLabel("Y:")
        self.inputCenterY = QLineEdit("250")
        self.inputCenterY.setFixedWidth(40)

        labelSide = QLabel("Сторона a:")
        self.inputSide = QLineEdit("200")
        self.inputSide.setFixedWidth(40)

        layoutSquare.addWidget(labelCenterX)
        layoutSquare.addWidget(self.inputCenterX)
        layoutSquare.addWidget(labelCenterY)
        layoutSquare.addWidget(self.inputCenterY)
        layoutSquare.addWidget(labelSide)
        layoutSquare.addWidget(self.inputSide)
        groupSquare.setLayout(layoutSquare)

        # Действия
        groupActions = QGroupBox("Действия")
        layoutActions = QHBoxLayout()

        buttonSaveBmp = QPushButton("Сохранить BMP")
        buttonSaveBmp.clicked.connect(self.saveBmp)

        buttonSavePbm = QPushButton("Сохранить PBM")
        buttonSavePbm.clicked.connect(self.savePbm)

        buttonClear = QPushButton("Очистить")
        buttonClear.clicked.connect(self.clearCanvas)

        layoutActions.addWidget(buttonSaveBmp)
        layoutActions.addWidget(buttonSavePbm)
        layoutActions.addWidget(buttonClear)
        groupActions.setLayout(layoutActions)

        centerVerticalLayout.addWidget(groupSquare)
        centerVerticalLayout.addWidget(groupActions)

        # 3. Загрузка из SVG
        groupSvg = QGroupBox("Загрузка из SVG")
        layoutSvg = QVBoxLayout()

        buttonLoadSvg = QPushButton("Загрузить SVG")
        buttonLoadSvg.clicked.connect(self.loadSvg)

        self.labelSvgStatus = QLabel("SVG не загружен")
        self.labelSvgStatus.setStyleSheet("color: red;")
        self.labelSvgStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        buttonApplySvg = QPushButton("Применить параметры")
        buttonApplySvg.clicked.connect(self.drawSvgLines)

        layoutSvg.addWidget(buttonLoadSvg)
        layoutSvg.addWidget(self.labelSvgStatus)
        layoutSvg.addWidget(buttonApplySvg)
        groupSvg.setLayout(layoutSvg)

        # 4. Алгоритмы рисования
        groupAlgos = QGroupBox("Алгоритмы рисования")
        layoutAlgos = QVBoxLayout()

        rowFirst = QHBoxLayout()
        buttonEquation = QPushButton("Уравнение")
        buttonParametric = QPushButton("Параметрически")
        buttonEquation.clicked.connect(lambda: self.drawScene("equation"))
        buttonParametric.clicked.connect(lambda: self.drawScene("param"))
        rowFirst.addWidget(buttonEquation)
        rowFirst.addWidget(buttonParametric)

        rowSecond = QHBoxLayout()
        buttonBresenham = QPushButton("Брезенхем")
        buttonBuiltin = QPushButton("Встроенный")
        buttonBresenham.clicked.connect(lambda: self.drawScene("bresenham"))
        buttonBuiltin.clicked.connect(lambda: self.drawScene("builtin"))
        rowSecond.addWidget(buttonBresenham)
        rowSecond.addWidget(buttonBuiltin)

        layoutAlgos.addLayout(rowFirst)
        layoutAlgos.addLayout(rowSecond)
        groupAlgos.setLayout(layoutAlgos)

        # Добавление на верхнюю панель
        topLayout.addWidget(groupCanvas)
        topLayout.addLayout(centerVerticalLayout)
        topLayout.addWidget(groupSvg)
        topLayout.addWidget(groupAlgos)

        mainLayout.addLayout(topLayout)

        # Нижняя панель
        self.scrollArea = QScrollArea()
        self.scrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scrollArea.setStyleSheet("background-color: #f0f0f0;")

        self.canvasLabel = QLabel()
        self.canvasLabel.setStyleSheet("border: 2px solid black;")

        self.scrollArea.setWidget(self.canvasLabel)
        mainLayout.addWidget(self.scrollArea, stretch=1)

    # Создание холста
    def onCreateCanvasClick(self):
        try:
            canvasWidth = int(self.inputWidth.text())
            canvasHeight = int(self.inputHeight.text())
            self.createCanvas(canvasWidth, canvasHeight)
        except ValueError:
            pass

    def createCanvas(self, width, height):
        self.canvasImage = QImage(width, height, QImage.Format.Format_ARGB32)
        self.clearCanvas()

    def clearCanvas(self):
        if self.canvasImage:
            self.canvasImage.fill(Qt.GlobalColor.white)
            self.updateCanvasDisplay()

    def updateCanvasDisplay(self):
        pixmap = QPixmap.fromImage(self.canvasImage)
        self.canvasLabel.setPixmap(pixmap)
        self.canvasLabel.setFixedSize(pixmap.size())

    # Растеризация окружности
    def drawCirclePixels(self, centerX, centerY, radius, method, color):
        if radius <= 0:
            return

        if method == "builtin":
            painter = QPainter(self.canvasImage)
            painter.setPen(QPen(color, 1))
            painter.drawEllipse(
                centerX - radius, centerY - radius, 2 * radius, 2 * radius
            )
            painter.end()
            return

        def putEightPixels(cx, cy, px, py):
            pixelPoints = [
                (cx + px, cy + py),
                (cx - px, cy + py),
                (cx + px, cy - py),
                (cx - px, cy - py),
                (cx + py, cy + px),
                (cx - py, cy + px),
                (cx + py, cy - px),
                (cx - py, cy - px),
            ]
            imageWidth = self.canvasImage.width()
            imageHeight = self.canvasImage.height()
            for pointX, pointY in pixelPoints:
                if 0 <= pointX < imageWidth and 0 <= pointY < imageHeight:
                    self.canvasImage.setPixelColor(pointX, pointY, color)

        if method == "equation":
            pixelLimit = math.ceil(radius / math.sqrt(2))
            for currentX in range(0, pixelLimit + 1):
                currentY = round(math.sqrt(radius * radius - currentX * currentX))
                putEightPixels(centerX, centerY, currentX, currentY)

        elif method == "param":
            angleStep = 1.0 / radius
            angleParam = 0.0
            while angleParam <= math.pi / 4:
                currentX = round(radius * math.cos(angleParam))
                currentY = round(radius * math.sin(angleParam))
                putEightPixels(centerX, centerY, currentX, currentY)
                angleParam += angleStep

        elif method == "bresenham":
            currentX = 0
            currentY = radius
            deltaValue = 2 - 2 * radius
            while currentY >= currentX:
                putEightPixels(centerX, centerY, currentX, currentY)
                if deltaValue < 0:
                    firstCheck = 2 * deltaValue + 2 * currentY - 1
                    if firstCheck <= 0:
                        currentX += 1
                        deltaValue += 2 * currentX + 1
                    else:
                        currentX += 1
                        currentY -= 1
                        deltaValue += 2 * currentX - 2 * currentY + 2
                elif deltaValue > 0:
                    secondCheck = 2 * deltaValue - 2 * currentX - 1
                    if secondCheck <= 0:
                        currentX += 1
                        currentY -= 1
                        deltaValue += 2 * currentX - 2 * currentY + 2
                    else:
                        currentY -= 1
                        deltaValue -= 2 * currentY - 1
                else:
                    currentX += 1
                    currentY -= 1
                    deltaValue += 2 * currentX - 2 * currentY + 2

    # Отрисовка
    def drawScene(self, method):
        try:
            centerX = int(self.inputCenterX.text())
            centerY = int(self.inputCenterY.text())
            sideLength = float(self.inputSide.text())
        except ValueError:
            return

        self.clearCanvas()

        # Расчет радиусов для квадрата со стороной a
        radiusInscribed = round(sideLength / 2)  # Вписанная
        radiusCircumscribed = round(
            sideLength * math.sqrt(2) / 2
        )  # Описанная

        # Отрисовка квадрата
        painter = QPainter(self.canvasImage)
        painter.setPen(QPen(QColor(150, 150, 150), 1, Qt.PenStyle.DashLine))
        halfSide = round(sideLength / 2)
        painter.drawRect(
            centerX - halfSide,
            centerY - halfSide,
            round(sideLength),
            round(sideLength),
        )
        painter.end()

        # Отрисовка окружностей
        self.drawCirclePixels(
            centerX, centerY, radiusInscribed, method, QColor(0, 0, 255)
        )  # Вписанная
        self.drawCirclePixels(
            centerX, centerY, radiusCircumscribed, method, QColor(255, 0, 0)
        )  # Описанная

        self.updateCanvasDisplay()

    # Загрузка из SVG
    def loadSvg(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Открыть SVG", "", "SVG Files (*.svg)"
        )
        if not filePath:
            return

        try:
            xmlTree = ET.parse(filePath)
            xmlRoot = xmlTree.getroot()

            self.svgLines.clear()
            self.svgCircles = []  

            for xmlElement in xmlRoot.iter():
                if xmlElement.tag.endswith("line"):
                    lineX1 = float(xmlElement.attrib.get("x1", 0))
                    lineY1 = float(xmlElement.attrib.get("y1", 0))
                    lineX2 = float(xmlElement.attrib.get("x2", 0))
                    lineY2 = float(xmlElement.attrib.get("y2", 0))
                    self.svgLines.append((lineX1, lineY1, lineX2, lineY2))

                # Парсинг окружностей
                elif xmlElement.tag.endswith("circle"):
                    circleCx = float(xmlElement.attrib.get("cx", 0))
                    circleCy = float(xmlElement.attrib.get("cy", 0))
                    circleR = float(xmlElement.attrib.get("r", 0))
                    strokeColor = xmlElement.attrib.get("stroke", "#000000")
                    self.svgCircles.append(
                        (circleCx, circleCy, circleR, strokeColor)
                    )

            totalElements = len(self.svgLines) + len(self.svgCircles)
            self.labelSvgStatus.setText(
                f"Загружено элементов: {totalElements}"
            )
            self.labelSvgStatus.setStyleSheet("color: green;")
        except Exception as errorException:
            self.labelSvgStatus.setText("Ошибка SVG")
            self.labelSvgStatus.setStyleSheet("color: red;")

    def drawSvgLines(self):
        if not self.svgLines and not getattr(self, "svgCircles", None):
            return

        self.clearCanvas()
        painter = QPainter(self.canvasImage)

        # 1. Отрисовка отрезков (квадрата)
        painter.setPen(QPen(QColor(136, 136, 136), 1))
        for lineX1, lineY1, lineX2, lineY2 in self.svgLines:
            painter.drawLine(
                round(lineX1), round(lineY1), round(lineX2), round(lineY2)
            )

        for circleCx, circleCy, circleR, strokeColor in getattr(
            self, "svgCircles", []
        ):
            painter.setPen(QPen(QColor(strokeColor), 1))
            painter.drawEllipse(
                round(circleCx - circleR),
                round(circleCy - circleR),
                round(2 * circleR),
                round(2 * circleR),
            )

        painter.end()
        self.updateCanvasDisplay()

    # Сохранение в BMP
    def saveBmp(self):
        filePath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить BMP", "", "BMP Files (*.bmp)"
        )
        if filePath:
            self.canvasImage.save(filePath, "BMP")

    # Сохранение в PBM
    def savePbm(self):
        """Экспорт в текстовый формат PBM (Portable BitMap, ASCII / P1)."""
        filePath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить PBM", "", "PBM Files (*.pbm)"
        )
        if not filePath:
            return

        imageWidth = self.canvasImage.width()
        imageHeight = self.canvasImage.height()

        # Формирование PBM файла
        pbmHeader = f"P1\n# Generated by CircleSquareApp\n{imageWidth} {imageHeight}\n"
        pbmContentLines = [pbmHeader]

        for pixelY in range(imageHeight):
            rowPixels = []
            for pixelX in range(imageWidth):
                pixelColor = self.canvasImage.pixelColor(pixelX, pixelY)
                if (
                    pixelColor.red() < 250
                    or pixelColor.green() < 250
                    or pixelColor.blue() < 250
                ):
                    rowPixels.append("1")
                else:
                    rowPixels.append("0")
            pbmContentLines.append(" ".join(rowPixels) + "\n")

        with open(filePath, "w", encoding="ascii") as fileOutput:
            fileOutput.writelines(pbmContentLines)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = CircleSquareApp()
    mainWindow.show()
    sys.exit(app.exec())