# Если не установлен PyQt, напишите в терминале: pip install PyQt6 numpy

import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
    QLineEdit, QComboBox, QListWidget, QTextEdit, QHBoxLayout, 
    QVBoxLayout, QGridLayout, QGroupBox, QMessageBox
)
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from PyQt6.QtCore import Qt, QRectF, QPointF

# Битовые маски для классификации положения точек относительно границ окна
INSIDE_REGION = 0  
LEFT_REGION = 1    
RIGHT_REGION = 2   
BOTTOM_REGION = 4  
TOP_REGION = 8     


class ClippingCanvas(QWidget):
    """Холст для визуализации отсекающего окна и отрезков."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clipRect = QRectF(150, 100, 300, 250)
        self.originalSegments = []
        self.clippedSegments = []
        self.setMinimumSize(520, 420)
        self.setStyleSheet("background-color: #26282B; border: 1px solid #44474D; border-radius: 4px;")

    def setClipRect(self, xMin, yMin, width, height):
        self.clipRect = QRectF(xMin, yMin, width, height)
        self.update()

    def setSegments(self, segments):
        self.originalSegments = segments
        self.clippedSegments = []
        self.update()

    def setClippedResults(self, results):
        self.clippedSegments = results
        self.update()

    def clearAll(self):
        self.originalSegments = []
        self.clippedSegments = []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        
        rectBrush = QBrush(QColor(30, 60, 90, 110))
        painter.fillRect(self.clipRect, rectBrush)

        
        windowBorderPen = QPen(QColor(0, 180, 255), 2, Qt.PenStyle.DashLine)
        painter.setPen(windowBorderPen)
        painter.drawRect(self.clipRect)

        
        painter.setPen(QColor(170, 200, 230))
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        painter.drawText(int(self.clipRect.left()) + 6, int(self.clipRect.top()) - 6, "Top")
        painter.drawText(int(self.clipRect.left()) - 22, int(self.clipRect.bottom()) - 6, "Left")
        painter.drawText(int(self.clipRect.right()) + 6, int(self.clipRect.bottom()) - 6, "Right")
        painter.drawText(int(self.clipRect.left()) + 6, int(self.clipRect.bottom()) + 16, "Bottom")

        
        originalPen = QPen(QColor(160, 160, 160, 150), 1, Qt.PenStyle.DashDotLine)
        painter.setPen(originalPen)
        painter.setBrush(QBrush(QColor(180, 180, 180)))
        for segment in self.originalSegments:
            p1 = QPointF(segment['x1'], segment['y1'])
            p2 = QPointF(segment['x2'], segment['y2'])
            painter.drawLine(p1, p2)
            painter.drawEllipse(p1, 2.5, 2.5)
            painter.drawEllipse(p2, 2.5, 2.5)

        
        clippedPen = QPen(QColor(0, 240, 120), 3, Qt.PenStyle.SolidLine)
        painter.setPen(clippedPen)
        painter.setBrush(QBrush(QColor(255, 220, 0)))
        for segment in self.clippedSegments:
            if segment:
                p1 = QPointF(segment['x1'], segment['y1'])
                p2 = QPointF(segment['x2'], segment['y2'])
                painter.drawLine(p1, p2)
                painter.drawEllipse(p1, 3.5, 3.5)
                painter.drawEllipse(p2, 3.5, 3.5)


class ClippingApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа №9")
        self.resize(1150, 760)
        self.segmentListStorage = []
        self.initUserInterface()

    def initUserInterface(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        mainLayout = QGridLayout(centralWidget)
        mainLayout.setSpacing(10)

        
        self.algorithmGroupBox = QGroupBox("Выбор алгоритма")
        algorithmLayout = QVBoxLayout()
        self.algorithmSelector = QComboBox()
        self.algorithmSelector.addItems([
            "Простой алгоритм",
            "Алгоритм Сазерленда-Коэна",
            "Алгоритм разбиения средней точкой"
        ])
        algorithmLayout.addWidget(self.algorithmSelector)
        self.algorithmGroupBox.setLayout(algorithmLayout)
        mainLayout.addWidget(self.algorithmGroupBox, 0, 0)

        
        self.clippingWindowGroupBox = QGroupBox("Параметры окна отсечения")
        windowParametersLayout = QGridLayout()
        self.windowXMinInput = QLineEdit("150")
        self.windowYMinInput = QLineEdit("100")
        self.windowWidthInput = QLineEdit("300")
        self.windowHeightInput = QLineEdit("250")
        self.applyWindowButton = QPushButton("Применить окно")
        self.applyWindowButton.clicked.connect(self.handleUpdateWindowBounds)

        windowParametersLayout.addWidget(QLabel("X:"), 0, 0)
        windowParametersLayout.addWidget(self.windowXMinInput, 0, 1)
        windowParametersLayout.addWidget(QLabel("Y:"), 0, 2)
        windowParametersLayout.addWidget(self.windowYMinInput, 0, 3)
        windowParametersLayout.addWidget(QLabel("W:"), 1, 0)
        windowParametersLayout.addWidget(self.windowWidthInput, 1, 1)
        windowParametersLayout.addWidget(QLabel("H:"), 1, 2)
        windowParametersLayout.addWidget(self.windowHeightInput, 1, 3)
        windowParametersLayout.addWidget(self.applyWindowButton, 2, 0, 1, 4)
        self.clippingWindowGroupBox.setLayout(windowParametersLayout)
        mainLayout.addWidget(self.clippingWindowGroupBox, 0, 1)

        
        self.addSegmentGroupBox = QGroupBox("Добавление отрезков")
        segmentInputLayout = QGridLayout()
        self.segmentXStartInput = QLineEdit("60")
        self.segmentYStartInput = QLineEdit("80")
        self.segmentXEndInput = QLineEdit("420")
        self.segmentYEndInput = QLineEdit("330")
        self.addManualSegmentButton = QPushButton("Добавить отрезок")
        self.addManualSegmentButton.clicked.connect(self.handleAddManualSegment)

        segmentInputLayout.addWidget(QLabel("X1:"), 0, 0)
        segmentInputLayout.addWidget(self.segmentXStartInput, 0, 1)
        segmentInputLayout.addWidget(QLabel("Y1:"), 0, 2)
        segmentInputLayout.addWidget(self.segmentYStartInput, 0, 3)
        segmentInputLayout.addWidget(QLabel("X2:"), 1, 0)
        segmentInputLayout.addWidget(self.segmentXEndInput, 1, 1)
        segmentInputLayout.addWidget(QLabel("Y2:"), 1, 2)
        segmentInputLayout.addWidget(self.segmentYEndInput, 1, 3)
        segmentInputLayout.addWidget(self.addManualSegmentButton, 2, 0, 1, 4)
        self.addSegmentGroupBox.setLayout(segmentInputLayout)
        mainLayout.addWidget(self.addSegmentGroupBox, 0, 2)

        
        actionButtonContainer = QWidget()
        actionButtonLayout = QVBoxLayout(actionButtonContainer)
        self.generateRandomSegmentsButton = QPushButton("Добавить три случайных отрезка")
        self.performSingleClippingButton = QPushButton("Выполнить отсечение")
        self.performFullClippingButton = QPushButton("Отсечь все")
        self.clearAllSegmentsButton = QPushButton("Очистить все")

        self.generateRandomSegmentsButton.clicked.connect(self.handleGenerateRandomSegments)
        self.performSingleClippingButton.clicked.connect(self.handleClipSelectedSegment)
        self.performFullClippingButton.clicked.connect(self.handleClipAllSegments)
        self.clearAllSegmentsButton.clicked.connect(self.handleClearAll)

        actionButtonLayout.addWidget(self.generateRandomSegmentsButton)
        actionButtonLayout.addWidget(self.performSingleClippingButton)
        actionButtonLayout.addWidget(self.performFullClippingButton)
        actionButtonLayout.addWidget(self.clearAllSegmentsButton)
        mainLayout.addWidget(actionButtonContainer, 0, 3)

        
        self.segmentsListGroupBox = QGroupBox("Список отрезков")
        segmentsListLayout = QVBoxLayout()
        self.segmentDisplayList = QListWidget()
        segmentsListLayout.addWidget(self.segmentDisplayList)
        self.segmentsListGroupBox.setLayout(segmentsListLayout)
        mainLayout.addWidget(self.segmentsListGroupBox, 1, 0, 1, 1)

        
        self.informationGroupBox = QGroupBox("Информация")
        informationLayout = QVBoxLayout()
        self.informationLog = QTextEdit()
        self.informationLog.setReadOnly(True)
        informationLayout.addWidget(self.informationLog)
        self.informationGroupBox.setLayout(informationLayout)
        mainLayout.addWidget(self.informationGroupBox, 2, 0, 1, 1)

        
        self.displayCanvas = ClippingCanvas()
        mainLayout.addWidget(self.displayCanvas, 1, 1, 2, 3)

        
        self.legendGroupBox = QGroupBox("Легенда")
        legendLayout = QHBoxLayout()
        legendLayout.addWidget(QLabel("🟦 Окно отсечения"))
        legendLayout.addWidget(QLabel("⚪ Исходный отрезок"))
        legendLayout.addWidget(QLabel("🟩 Сохраненный отрезок"))
        legendLayout.addWidget(QLabel("🟡 Границы отсечения"))
        self.legendGroupBox.setLayout(legendLayout)
        mainLayout.addWidget(self.legendGroupBox, 3, 0, 1, 4)

        
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 1)
        mainLayout.setRowStretch(1, 3)
        mainLayout.setRowStretch(2, 2)

    def computeCohenSutherlandCode(self, px, py, xMin, yMin, xMax, yMax):
        """Вычисляет 4-битовый код положения точки относительно прямоугольного окна."""
        code = INSIDE_REGION
        if px < xMin:
            code |= LEFT_REGION
        elif px > xMax:
            code |= RIGHT_REGION
        if py < yMin:
            code |= TOP_REGION
        elif py > yMax:
            code |= BOTTOM_REGION
        return code

    def isPointInsideWindow(self, px, py, xMin, yMin, xMax, yMax, epsilon=1e-5):
        """Проверяет, лежит ли точка внутри или на границе окна отсечения."""
        return (xMin - epsilon <= px <= xMax + epsilon) and (yMin - epsilon <= py <= yMax + epsilon)

    
    def simpleClippingAlgorithm(self, x1, y1, x2, y2, xMin, yMin, xMax, yMax):
        """Алгоритм простого отсечения отрезка по границам прямоугольного окна."""
        
        logReport = [f"Старт простого алгоритма: P1({x1:.1f}, {y1:.1f}), P2({x2:.1f}, {y2:.1f})"]

        code1 = self.computeCohenSutherlandCode(x1, y1, xMin, yMin, xMax, yMax)
        code2 = self.computeCohenSutherlandCode(x2, y2, xMin, yMin, xMax, yMax)

        if code1 == 0 and code2 == 0:
            logReport.append("Отрезок тривиально видим.")
            return {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}, "\n".join(logReport)

        if (code1 & code2) != 0:
            logReport.append(f"Отрезок тривиально невидим (код: {code1 & code2:04b}).")
            return None, "\n".join(logReport)

        dx = x2 - x1
        dy = y2 - y1
        intersectionCandidates = []

        if self.isPointInsideWindow(x1, y1, xMin, yMin, xMax, yMax):
            intersectionCandidates.append((x1, y1))
        if self.isPointInsideWindow(x2, y2, xMin, yMin, xMax, yMax):
            intersectionCandidates.append((x2, y2))

        # Пересечение с левой стороной
        if abs(dx) > 1e-7:
            t = (xMin - x1) / dx
            if 0.0 <= t <= 1.0:
                yInter = y1 + t * dy
                if yMin - 1e-5 <= yInter <= yMax + 1e-5:
                    intersectionCandidates.append((xMin, yInter))
                    logReport.append(f"Пересечение с левой гранью: ({xMin:.1f}, {yInter:.1f})")

        # Пересечение с правой стороной
        if abs(dx) > 1e-7:
            t = (xMax - x1) / dx
            if 0.0 <= t <= 1.0:
                yInter = y1 + t * dy
                if yMin - 1e-5 <= yInter <= yMax + 1e-5:
                    intersectionCandidates.append((xMax, yInter))
                    logReport.append(f"Пересечение с правой гранью: ({xMax:.1f}, {yInter:.1f})")

        # Пересечение с верхней стороной
        if abs(dy) > 1e-7:
            t = (yMin - y1) / dy
            if 0.0 <= t <= 1.0:
                xInter = x1 + t * dx
                if xMin - 1e-5 <= xInter <= xMax + 1e-5:
                    intersectionCandidates.append((xInter, yMin))
                    logReport.append(f"Пересечение с верхней гранью: ({xInter:.1f}, {yMin:.1f})")

        # Пересечение с нижней стороной
        if abs(dy) > 1e-7:
            t = (yMax - y1) / dy
            if 0.0 <= t <= 1.0:
                xInter = x1 + t * dx
                if xMin - 1e-5 <= xInter <= xMax + 1e-5:
                    intersectionCandidates.append((xInter, yMax))
                    logReport.append(f"Пересечение с нижней гранью: ({xInter:.1f}, {yMax:.1f})")

        # Удаление совпадающих точек
        uniquePoints = []
        for point in intersectionCandidates:
            if not any(abs(point[0] - u[0]) < 1e-4 and abs(point[1] - u[1]) < 1e-4 for u in uniquePoints):
                uniquePoints.append(point)

        if len(uniquePoints) >= 2:
            if abs(dx) > abs(dy):
                uniquePoints.sort(key=lambda p: (p[0] - x1) / dx)
            else:
                uniquePoints.sort(key=lambda p: (p[1] - y1) / dy)
            pStart, pEnd = uniquePoints[0], uniquePoints[-1]
            logReport.append(f" Итог отсечения: ({pStart[0]:.1f}, {pStart[1]:.1f}) - ({pEnd[0]:.1f}, {pEnd[1]:.1f})")
            return {'x1': pStart[0], 'y1': pStart[1], 'x2': pEnd[0], 'y2': pEnd[1]}, "\n".join(logReport)
        else:
            logReport.append(" Отрезок лежит вне окна отсечения.")
            return None, "\n".join(logReport)

    def cohenSutherlandClip(self, x1, y1, x2, y2, xMin, yMin, xMax, yMax):
        """Алгоритм Сазерленда-Коэна для отсечения отрезка по прямоугольному окну."""

        code1 = self.computeCohenSutherlandCode(x1, y1, xMin, yMin, xMax, yMax)
        code2 = self.computeCohenSutherlandCode(x2, y2, xMin, yMin, xMax, yMax)
        accept = False
        logReport = [f"Старт Сазерленда-Коэна: P1({x1:.1f}, {y1:.1f}) [{code1:04b}], P2({x2:.1f}, {y2:.1f}) [{code2:04b}]"]

        for _ in range(8):
            if code1 == 0 and code2 == 0:
                accept = True
                logReport.append("Отрезок тривиально видим.")
                break
            elif (code1 & code2) != 0:
                logReport.append(f"Отрезок тривиально невидим (битовое И = {code1 & code2:04b}).")
                break
            else:
                outCode = code1 if code1 != 0 else code2
                dx = x2 - x1
                dy = y2 - y1
                x, y = 0.0, 0.0

                if outCode & TOP_REGION:
                    x = x1 + dx * (yMin - y1) / dy if dy != 0 else x1
                    y = yMin
                    logReport.append(f"Пересечение с верхней гранью: ({x:.1f}, {y:.1f})")
                elif outCode & BOTTOM_REGION:
                    x = x1 + dx * (yMax - y1) / dy if dy != 0 else x1
                    y = yMax
                    logReport.append(f"Пересечение с нижней гранью: ({x:.1f}, {y:.1f})")
                elif outCode & RIGHT_REGION:
                    y = y1 + dy * (xMax - x1) / dx if dx != 0 else y1
                    x = xMax
                    logReport.append(f"Пересечение с правой гранью: ({x:.1f}, {y:.1f})")
                elif outCode & LEFT_REGION:
                    y = y1 + dy * (xMin - x1) / dx if dx != 0 else y1
                    x = xMin
                    logReport.append(f"Пересечение с левой гранью: ({x:.1f}, {y:.1f})")

                if outCode == code1:
                    x1, y1 = x, y
                    code1 = self.computeCohenSutherlandCode(x1, y1, xMin, yMin, xMax, yMax)
                else:
                    x2, y2 = x, y
                    code2 = self.computeCohenSutherlandCode(x2, y2, xMin, yMin, xMax, yMax)

        clippedResult = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2} if accept else None
        return clippedResult, "\n".join(logReport)

    
    def midpointSubdivisionClip(self, x1, y1, x2, y2, xMin, yMin, xMax, yMax, epsilon=0.5):
        """Алгоритм разбиения средней точкой для отсечения отрезка по прямоугольному окну."""
        code1 = self.computeCohenSutherlandCode(x1, y1, xMin, yMin, xMax, yMax)
        code2 = self.computeCohenSutherlandCode(x2, y2, xMin, yMin, xMax, yMax)
        logReport = [f"Старт деления средней точкой: P1({x1:.1f}, {y1:.1f}), P2({x2:.1f}, {y2:.1f})"]

        if (code1 & code2) != 0:
            logReport.append("Отрезок тривиально невидим.")
            return None, "\n".join(logReport)

        if code1 == 0 and code2 == 0:
            logReport.append("Отрезок тривиально видим.")
            return {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}, "\n".join(logReport)

        segmentLength = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
        if segmentLength <= epsilon:
            return None, "\n".join(logReport)

        def binarySearchEdge(pInside, pOutside):
            """Бинарный поиск точки пересечения с ребром."""
            pNear = pInside
            pFar = pOutside
            while ((pNear[0] - pFar[0])**2 + (pNear[1] - pFar[1])**2)**0.5 > epsilon:
                pMid = ((pNear[0] + pFar[0]) / 2.0, (pNear[1] + pFar[1]) / 2.0)
                cMid = self.computeCohenSutherlandCode(pMid[0], pMid[1], xMin, yMin, xMax, yMax)
                if cMid == 0:
                    pNear = pMid
                else:
                    pFar = pMid
            return pNear

        if code1 != 0 and code2 == 0:
            resP1 = binarySearchEdge((x2, y2), (x1, y1))
            return {'x1': resP1[0], 'y1': resP1[1], 'x2': x2, 'y2': y2}, "\n".join(logReport)
        elif code1 == 0 and code2 != 0:
            resP2 = binarySearchEdge((x1, y1), (x2, y2))
            return {'x1': x1, 'y1': y1, 'x2': resP2[0], 'y2': resP2[1]}, "\n".join(logReport)
        else:
            pMid = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
            cMid = self.computeCohenSutherlandCode(pMid[0], pMid[1], xMin, yMin, xMax, yMax)
            if cMid == 0:
                resP1 = binarySearchEdge(pMid, (x1, y1))
                resP2 = binarySearchEdge(pMid, (x2, y2))
                return {'x1': resP1[0], 'y1': resP1[1], 'x2': resP2[0], 'y2': resP2[1]}, "\n".join(logReport)
            else:
                part1, _ = self.midpointSubdivisionClip(x1, y1, pMid[0], pMid[1], xMin, yMin, xMax, yMax, epsilon)
                part2, _ = self.midpointSubdivisionClip(pMid[0], pMid[1], x2, y2, xMin, yMin, xMax, yMax, epsilon)
                if part1 and part2:
                    return {'x1': part1['x1'], 'y1': part1['y1'], 'x2': part2['x2'], 'y2': part2['y2']}, "\n".join(logReport)
                return (part1 or part2), "\n".join(logReport)

    def handleUpdateWindowBounds(self):
        """Обновляет границы окна отсечения на основе пользовательского ввода."""
        try:
            xMin = float(self.windowXMinInput.text())
            yMin = float(self.windowYMinInput.text())
            width = float(self.windowWidthInput.text())
            height = float(self.windowHeightInput.text())
            self.displayCanvas.setClipRect(xMin, yMin, width, height)
            self.informationLog.append(f"Окно: X={xMin}, Y={yMin}, W={width}, H={height}")
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Некорректные параметры окна отсечения.")

    def handleAddManualSegment(self):
        """Добавляет отрезок, введенный пользователем."""
        try:
            x1 = float(self.segmentXStartInput.text())
            y1 = float(self.segmentYStartInput.text())
            x2 = float(self.segmentXEndInput.text())
            y2 = float(self.segmentYEndInput.text())
            segment = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
            self.segmentListStorage.append(segment)
            self.segmentDisplayList.addItem(f"Отрезок: ({x1:.1f}, {y1:.1f})  ({x2:.1f}, {y2:.1f})")
            self.displayCanvas.setSegments(self.segmentListStorage)
            self.informationLog.append(f"Добавлен отрезок: ({x1}, {y1})  ({x2}, {y2})")
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Координаты должны быть числами.")

    def handleGenerateRandomSegments(self):
        """Генерирует случайные отрезки."""
        canvasWidth = max(self.displayCanvas.width(), 500)
        canvasHeight = max(self.displayCanvas.height(), 400)
        for _ in range(3):
            x1 = random.randint(30, canvasWidth - 50)
            y1 = random.randint(30, canvasHeight - 50)
            x2 = random.randint(30, canvasWidth - 50)
            y2 = random.randint(30, canvasHeight - 50)
            segment = {'x1': float(x1), 'y1': float(y1), 'x2': float(x2), 'y2': float(y2)}
            self.segmentListStorage.append(segment)
            self.segmentDisplayList.addItem(f"Отрезок: ({x1:.1f}, {y1:.1f})  ({x2:.1f}, {y2:.1f})")
        self.displayCanvas.setSegments(self.segmentListStorage)
        self.informationLog.append("Сгенерированы 3 случайных отрезка.")

    def executeAlgorithm(self, segment):
        """Выполняет выбранный алгоритм отсечения для данного отрезка."""
        rect = self.displayCanvas.clipRect
        xMin, yMin, xMax, yMax = rect.left(), rect.top(), rect.right(), rect.bottom()
        chosenAlgorithmIndex = self.algorithmSelector.currentIndex()

        if chosenAlgorithmIndex == 0:
            return self.simpleClippingAlgorithm(segment['x1'], segment['y1'], segment['x2'], segment['y2'], xMin, yMin, xMax, yMax)
        elif chosenAlgorithmIndex == 1:
            return self.cohenSutherlandClip(segment['x1'], segment['y1'], segment['x2'], segment['y2'], xMin, yMin, xMax, yMax)
        else:
            return self.midpointSubdivisionClip(segment['x1'], segment['y1'], segment['x2'], segment['y2'], xMin, yMin, xMax, yMax)

    def handleClipSelectedSegment(self):
        """Отсечение выбранного отрезка из списка."""
        currentIndex = self.segmentDisplayList.currentRow()
        if currentIndex < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите отрезок из списка.")
            return
        segment = self.segmentListStorage[currentIndex]
        clipped, logText = self.executeAlgorithm(segment)
        self.informationLog.append(f"\n Отсечение выбранного ({self.algorithmSelector.currentText()}) ")
        self.informationLog.append(logText)
        self.displayCanvas.setClippedResults([clipped] if clipped else [])

    def handleClipAllSegments(self):
        """Отсечение всех отрезков из списка."""
        if not self.segmentListStorage:
            QMessageBox.warning(self, "Предупреждение", "Список отрезков пуст.")
            return
        clippedResults = []
        self.informationLog.append(f"\n=== Отсечение всех отрезков ({self.algorithmSelector.currentText()}) ===")
        for index, segment in enumerate(self.segmentListStorage):
            clipped, logText = self.executeAlgorithm(segment)
            if clipped:
                clippedResults.append(clipped)
            self.informationLog.append(f"[{index + 1}] " + logText)
        self.displayCanvas.setClippedResults(clippedResults)

    def handleClearAll(self):
        self.segmentListStorage.clear()
        self.segmentDisplayList.clear()
        self.informationLog.clear()
        self.displayCanvas.clearAll()
        self.informationLog.append("Все данные очищены.")


if __name__ == "__main__":
    application = QApplication(sys.argv)
    mainWindow = ClippingApplication()
    mainWindow.show()
    sys.exit(application.exec())