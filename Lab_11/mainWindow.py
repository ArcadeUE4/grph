from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QSlider,
    QFrame
)
from PyQt6.QtCore import Qt

from graphicsViewportWidget import GraphicsViewportWidget
from UiStyles import UiStyles


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа № 11")
        self.resize(1050, 700)
        self.initUserInterface()

    def initUserInterface(self):
        centralContainer = QWidget(self)
        self.setCentralWidget(centralContainer)

        mainLayout = QHBoxLayout(centralContainer)
        mainLayout.setContentsMargins(16, 16, 16, 16)
        mainLayout.setSpacing(16)

        # Область визуализации
        self.graphicsViewport = GraphicsViewportWidget(self)
        mainLayout.addWidget(self.graphicsViewport, stretch=4)

        # Инспектор управления с центрированием
        inspectorLayout = QVBoxLayout()
        inspectorLayout.setSpacing(12)


        # Отступ сверху для центрирования
        inspectorLayout.addStretch()

        # Выбор фигуры
        self.figureSelectionLabel = QLabel("Выбор фигуры:")
        self.figureSelectionComboBox = QComboBox()
        self.figureSelectionComboBox.addItems(["Тетраэдр", "Октаэдр"])
        self.figureSelectionComboBox.setStyleSheet(UiStyles.comboBoxStyle)
        self.figureSelectionComboBox.currentTextChanged.connect(self.onFigureChanged)

        inspectorLayout.addWidget(self.figureSelectionLabel)
        inspectorLayout.addWidget(self.figureSelectionComboBox)

        # Выбор проекции
        self.projectionSelectionLabel = QLabel("Тип проекции:")
        self.projectionSelectionComboBox = QComboBox()
        self.projectionSelectionComboBox.addItems(["Центральная", "Ортогональная"])
        self.projectionSelectionComboBox.setStyleSheet(UiStyles.comboBoxStyle)
        self.projectionSelectionComboBox.currentTextChanged.connect(self.onProjectionChanged)

        inspectorLayout.addWidget(self.projectionSelectionLabel)
        inspectorLayout.addWidget(self.projectionSelectionComboBox)

        inspectorLayout.addWidget(self.createSeparator())

        # Ползунок расстояния до плоскости
        self.distanceValueLabel = QLabel("Расстояние до плоскости d: 4.0")
        self.planeDistanceSlider = QSlider(Qt.Orientation.Horizontal)
        self.planeDistanceSlider.setRange(15, 120)
        self.planeDistanceSlider.setValue(40)
        self.planeDistanceSlider.setStyleSheet(UiStyles.sliderStyle)
        self.planeDistanceSlider.valueChanged.connect(self.onPlaneDistanceSliderMoved)

        inspectorLayout.addWidget(self.distanceValueLabel)
        inspectorLayout.addWidget(self.planeDistanceSlider)

        # Ползунок масштаба
        self.scaleValueLabel = QLabel("Масштаб отображения: 1.00x")
        self.viewportScaleSlider = QSlider(Qt.Orientation.Horizontal)
        self.viewportScaleSlider.setRange(30, 250)
        self.viewportScaleSlider.setValue(100)
        self.viewportScaleSlider.setStyleSheet(UiStyles.sliderStyle)
        self.viewportScaleSlider.valueChanged.connect(self.onViewportScaleSliderMoved)

        inspectorLayout.addWidget(self.scaleValueLabel)
        inspectorLayout.addWidget(self.viewportScaleSlider)

        inspectorLayout.addWidget(self.createSeparator())

        # Кнопка Сброс
        self.resetButton = QPushButton("Сброс")
        self.resetButton.setStyleSheet(UiStyles.buttonStyle)
        self.resetButton.clicked.connect(self.onResetClicked)
        inspectorLayout.addWidget(self.resetButton)

        # Отступ снизу для центрирования
        inspectorLayout.addStretch()

        inspectorContainerWidget = QWidget()
        inspectorContainerWidget.setLayout(inspectorLayout)
        inspectorContainerWidget.setFixedWidth(240)

        mainLayout.addWidget(inspectorContainerWidget, stretch=1)

    def createSeparator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def onFigureChanged(self, figureName):
        self.graphicsViewport.setFigureType(figureName)

    def onProjectionChanged(self, projectionName):
        self.graphicsViewport.setProjectionType(projectionName)
        isPerspective = (projectionName == "Центральная")
        self.planeDistanceSlider.setEnabled(isPerspective)
        self.distanceValueLabel.setEnabled(isPerspective)

    def onPlaneDistanceSliderMoved(self, sliderValue):
        calculatedDistance = sliderValue / 10.0
        self.distanceValueLabel.setText(f"Расстояние до плоскости d: {calculatedDistance:.1f}")
        self.graphicsViewport.setPlaneDistance(calculatedDistance)

    def onViewportScaleSliderMoved(self, sliderValue):
        calculatedScale = sliderValue / 100.0
        self.scaleValueLabel.setText(f"Масштаб отображения: {calculatedScale:.2f}x")
        self.graphicsViewport.setDisplayScaleFactor(calculatedScale)

    def onResetClicked(self):
        self.planeDistanceSlider.setValue(40)
        self.viewportScaleSlider.setValue(100)
        self.graphicsViewport.resetView()