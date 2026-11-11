import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
from PyQt6.QtWidgets import QWidget

from CurveAlgorithms import CurveAlgorithms


class CurveCanvas(QWidget):
    """Интерактивный холст для отображения и редактирования кривых."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pointRadius = 6
        self.selectedPointIndex = -1

        # Изначально холст чист
        self.controlPoints = []

        # Параметры алгоритмов
        self.activeAlgorithm = "Безье"
        self.bezierDegree = 3
        self.parameterT = 0.5
        self.currentStepIndex = 0
        self.isFullBuildMode = False
        self.chaikinIterations = 3

        # Флаги отображения
        self.showIntermediatePoints = True
        self.showControlPoints = True

        self.setMouseTracking(True)
        self.setMinimumSize(700, 480)
        self.setStyleSheet("background-color: #1E1E1E; border: 1px solid #333333; border-radius: 4px;")

    def mousePressEvent(self, mouseEvent):
        clickPos = mouseEvent.position()
        if mouseEvent.button() == Qt.MouseButton.LeftButton:
            for idx, pt in enumerate(self.controlPoints):
                if math.hypot(pt.x() - clickPos.x(), pt.y() - clickPos.y()) <= self.pointRadius + 5:
                    self.selectedPointIndex = idx
                    return
            # Добавление новой точки кликом
            self.controlPoints.append(QPointF(clickPos.x(), clickPos.y()))
            self.update()

        elif mouseEvent.button() == Qt.MouseButton.RightButton:
            # Удаление точки правым кликом
            for idx, pt in enumerate(self.controlPoints):
                if math.hypot(pt.x() - clickPos.x(), pt.y() - clickPos.y()) <= self.pointRadius + 5:
                    self.controlPoints.pop(idx)
                    self.selectedPointIndex = -1
                    self.update()
                    return

    def mouseMoveEvent(self, mouseEvent):
        if self.selectedPointIndex != -1 and (mouseEvent.buttons() & Qt.MouseButton.LeftButton):
            self.controlPoints[self.selectedPointIndex] = mouseEvent.position()
            self.update()

    def mouseReleaseEvent(self, mouseEvent):
        if mouseEvent.button() == Qt.MouseButton.LeftButton:
            self.selectedPointIndex = -1

    def paintEvent(self, paintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Текстовая подсказка при пустом холсте
        if not self.controlPoints:
            painter.setPen(QPen(QColor("#666666")))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Холст пуст. Кликните ЛКМ, чтобы поставить первую контрольную точку"
            )
            return

        requiredCount = self.bezierDegree + 1
        activePoints = self.controlPoints[:requiredCount] if self.activeAlgorithm == "Безье" else self.controlPoints

        
        if len(self.controlPoints) > 1:
            dashedPen = QPen(QColor("#757575"), 1.2, Qt.PenStyle.DashLine)
            painter.setPen(dashedPen)
            for i in range(len(self.controlPoints) - 1):
                painter.drawLine(self.controlPoints[i], self.controlPoints[i + 1])

        # Отрисовка Чайкина 
        if self.activeAlgorithm == "Чайкина":
            chaikinCurve = CurveAlgorithms.computeChaikinPoints(self.controlPoints, self.chaikinIterations)
            if len(chaikinCurve) > 1:
                painter.setPen(QPen(QColor("#64B5F6"), 2.2))
                path = QPainterPath()
                path.moveTo(chaikinCurve[0])
                for pt in chaikinCurve[1:]:
                    path.lineTo(pt)
                painter.drawPath(path)

                if self.showIntermediatePoints:
                    painter.setBrush(QBrush(QColor("#64B5F6")))
                    painter.setPen(Qt.PenStyle.NoPen)
                    for pt in chaikinCurve:
                        painter.drawEllipse(pt, 3, 3)

        # Отрисовка Безье 
        elif self.activeAlgorithm == "Безье" and len(activePoints) >= 2:
            levels = CurveAlgorithms.computeDeCasteljauPyramid(activePoints, self.parameterT)
            stepColors = [QColor("#81C784"), QColor("#FFB74D"), QColor("#BA68C8")]

            # Промежуточные уровни де Кастельжо
            if self.showIntermediatePoints:
                maxLevelToShow = len(levels) if self.isFullBuildMode else min(self.currentStepIndex + 2, len(levels))
                for lvl in range(1, maxLevelToShow - 1):
                    color = stepColors[(lvl - 1) % len(stepColors)]
                    painter.setPen(QPen(color, 1.3, Qt.PenStyle.SolidLine))
                    for i in range(len(levels[lvl]) - 1):
                        painter.drawLine(levels[lvl][i], levels[lvl][i + 1])

                    painter.setBrush(QBrush(color))
                    for pt in levels[lvl]:
                        painter.drawEllipse(pt, 3.5, 3.5)

            # Точка на кривой при текущем t
            if len(levels[-1]) == 1 and (self.isFullBuildMode or self.currentStepIndex >= len(levels) - 2):
                pointOnCurve = levels[-1][0]
                painter.setBrush(QBrush(QColor("#EF5350")))
                painter.setPen(QPen(QColor("#FFFFFF"), 1.2))
                painter.drawEllipse(pointOnCurve, 5, 5)

            # Полная непрерывная кривая
            if self.isFullBuildMode:
                smoothCurve = CurveAlgorithms.computeBezierPoints(activePoints, 120)
                if len(smoothCurve) > 1:
                    painter.setPen(QPen(QColor("#42A5F5"), 2.2))
                    path = QPainterPath()
                    path.moveTo(smoothCurve[0])
                    for pt in smoothCurve[1:]:
                        path.lineTo(pt)
                    painter.drawPath(path)

        # Контрольные точки с подписями
        if self.showControlPoints:
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            for idx, pt in enumerate(self.controlPoints):
                painter.setBrush(QBrush(QColor("#E53935")))
                painter.setPen(QPen(QColor("#FFCDD2"), 1.2))
                painter.drawEllipse(pt, self.pointRadius, self.pointRadius)

                painter.setPen(QPen(QColor("#ECEFF1")))
                painter.drawText(QPointF(pt.x() - 8, pt.y() - 10), f"P{idx}")