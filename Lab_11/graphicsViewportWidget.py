import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QMouseEvent
from PyQt6.QtCore import Qt, QPointF

from geometryDataBuilder import GeometryDataBuilder
from UiStyles import UiStyles

class GraphicsViewportWidget(QWidget):
    """Виджет отображения трехмерных каркасных моделей и координатных осей."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figureType = "Тетраэдр"
        self.projectionType = "Центральная"

        # Начальные углы вращения модели
        self.defaultAngleX = 25.0
        self.defaultAngleY = -35.0
        self.angleX = self.defaultAngleX
        self.angleY = self.defaultAngleY

        # Параметры проекции и масштаба
        self.planeDistance = 4.0
        self.displayScaleFactor = 1.0
        self.baseViewScale = 160.0

        # Длина координатных осей в мировых единицах
        self.axesLength = 1.6

        self.lastMousePosition = None
        self.setStyleSheet("background-color: #3B6EB5; border-radius: 4px;")

    def setFigureType(self, figureName):
        self.figureType = figureName
        self.update()

    def setProjectionType(self, projectionName):
        self.projectionType = projectionName
        self.update()

    def setPlaneDistance(self, distanceValue):
        self.planeDistance = max(1.0, float(distanceValue))
        self.update()

    def setDisplayScaleFactor(self, scaleFactor):
        self.displayScaleFactor = float(scaleFactor)
        self.update()

    def resetView(self):
        """Сброс углов поворота к исходному ракурсу."""
        self.angleX = self.defaultAngleX
        self.angleY = self.defaultAngleY
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastMousePosition = event.position()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton and self.lastMousePosition:
            currentPosition = event.position()
            deltaX = currentPosition.x() - self.lastMousePosition.x()
            deltaY = currentPosition.y() - self.lastMousePosition.y()

            self.angleY += deltaX * 0.6
            self.angleX += deltaY * 0.6
            self.lastMousePosition = currentPosition
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.lastMousePosition = None

    def transformVertex(self, vertexCoordinates):
        """Матричные преобразования поворота вокруг осей X и Y."""
        x, y, z = vertexCoordinates
        radX = math.radians(self.angleX)
        radY = math.radians(self.angleY)

        # Поворот вокруг оси Y
        rotatedX = x * math.cos(radY) + z * math.sin(radY)
        rotatedY = y
        rotatedZ = -x * math.sin(radY) + z * math.cos(radY)

        # Поворот вокруг оси X
        finalX = rotatedX
        finalY = rotatedY * math.cos(radX) - rotatedZ * math.sin(radX)
        finalZ = rotatedY * math.sin(radX) + rotatedZ * math.cos(radX)

        return finalX, finalY, finalZ

    def projectVertex(self, transformedVertex, viewportCenter):
        """Проецирование 3D-точки на плоскость экрана."""
        x, y, z = transformedVertex
        centerX, centerY = viewportCenter
        currentScale = self.baseViewScale * self.displayScaleFactor

        if self.projectionType == "Центральная":
            depthDistance = z + self.planeDistance
            if depthDistance <= 0.1:
                depthDistance = 0.1
            perspectiveFactor = self.planeDistance / depthDistance
            screenX = centerX + x * perspectiveFactor * currentScale
            screenY = centerY - y * perspectiveFactor * currentScale
        else:
            screenX = centerX + x * currentScale
            screenY = centerY - y * currentScale

        return QPointF(screenX, screenY)

    def drawCoordinateAxes(self, painter, viewportCenter):
        """Отрисовка координатных осей."""
        origin3D = [0.0, 0.0, 0.0]
        xAxisEnd3D = [self.axesLength, 0.0, 0.0]
        yAxisEnd3D = [0.0, self.axesLength, 0.0]
        zAxisEnd3D = [0.0, 0.0, self.axesLength]

        screenOrigin = self.projectVertex(self.transformVertex(origin3D), viewportCenter)
        screenXEnd = self.projectVertex(self.transformVertex(xAxisEnd3D), viewportCenter)
        screenYEnd = self.projectVertex(self.transformVertex(yAxisEnd3D), viewportCenter)
        screenZEnd = self.projectVertex(self.transformVertex(zAxisEnd3D), viewportCenter)

        axesDefinitions = [
            (screenXEnd, QColor(229, 57, 53), "X"),    # Красный - X
            (screenYEnd, QColor(67, 160, 71), "Y"),    # Зеленый - Y
            (screenZEnd, QColor(30, 136, 229), "Z")    # Синий - Z
        ]

        labelFont = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(labelFont)

        for endPoint, axisColor, labelText in axesDefinitions:
            axisPen = QPen(axisColor, 3)
            painter.setPen(axisPen)
            painter.drawLine(screenOrigin, endPoint)

            # Текстовая метка оси со смещением
            painter.drawText(int(endPoint.x() + 6), int(endPoint.y() + 4), labelText)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.figureType == "Тетраэдр":
            vertices, edges = GeometryDataBuilder.createTetrahedron()
        else:
            vertices, edges = GeometryDataBuilder.createOctahedron()

        viewportCenter = (self.width() / 2.0, self.height() / 2.0)

        
        self.drawCoordinateAxes(painter, viewportCenter)

        
        projectedScreenPoints = []
        for vertex in vertices:
            transformedPoint = self.transformVertex(vertex)
            screenPoint = self.projectVertex(transformedPoint, viewportCenter)
            projectedScreenPoints.append(screenPoint)

        
        edgePen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(edgePen)
        for startIndex, endIndex in edges:
            painter.drawLine(projectedScreenPoints[startIndex], projectedScreenPoints[endIndex])

        
        vertexPen = QPen(QColor(255, 215, 0), 6)
        painter.setPen(vertexPen)
        for point in projectedScreenPoints:
            painter.drawPoint(point)