from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QRadioButton,
    QSlider,
    QLabel,
    QPushButton,
    QCheckBox
)

from CurveCanvas import CurveCanvas

class MainWindow(QMainWindow):
    """Главное окно приложения с верхней панелью и нижним холстом."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Построение кривых Безье и Чайкина")
        self.resize(1180, 780)
        self.initUserInterface()

    def initUserInterface(self):
        rootWidget = QWidget()
        self.setCentralWidget(rootWidget)

        # Темная тема со переключателями
        self.setStyleSheet("""
            QWidget {
                background-color: #252526;
                color: #CCCCCC;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-size: 11px;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 10px;
                background-color: #2D2D30;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #333337;
                color: #E0E0E0;
                border: 1px solid #434346;
                border-radius: 3px;
                padding: 4px 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3E3E42;
                border: 1px solid #5A5A5C;
            }
            QPushButton:pressed {
                background-color: #1E1E1E;
            }

            /* Квадратные RadioButton вместо круглых */
            QRadioButton {
                color: #CCCCCC;
                font-size: 11px;
                spacing: 6px;
            }
            QRadioButton::indicator {
                width: 12px;
                height: 12px;
                border: 1px solid #555555;
                background-color: #1E1E1E;
                border-radius: 0px; /* Убираем скругление — строгий квадрат */
            }
            QRadioButton::indicator:hover {
                border-color: #007ACC;
            }
            QRadioButton::indicator:checked {
                background-color: #007ACC;
                border: 2px solid #1E1E1E; /* Внутренний аккуратный квадратный маркер */
                outline: 1px solid #007ACC;
            }

            /* Квадратные CheckBox */
            QCheckBox {
                color: #CCCCCC;
                font-size: 11px;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 12px;
                height: 12px;
                border: 1px solid #555555;
                background-color: #1E1E1E;
                border-radius: 0px;
            }
            QCheckBox::indicator:hover {
                border-color: #007ACC;
            }
            QCheckBox::indicator:checked {
                background-color: #007ACC;
                border: 2px solid #1E1E1E;
                outline: 1px solid #007ACC;
            }

            QLabel {
                color: #CCCCCC;
                font-size: 11px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #3E3E42;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #007ACC;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #CCCCCC;
                border: 1px solid #555555;
                width: 12px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 2px; /* Квадратный бегунок слайдера */
            }
            QSlider::handle:horizontal:hover {
                background: #FFFFFF;
            }
        """)

        rootLayout = QVBoxLayout(rootWidget)
        rootLayout.setContentsMargins(12, 12, 12, 12)
        rootLayout.setSpacing(12)

        # Верхняя панель с настройками
        topPanelsLayout = QHBoxLayout()
        topPanelsLayout.setSpacing(10)

        # Тип кривой
        self.curveTypeGroupBox = QGroupBox("Тип кривой")
        curveTypeLayout = QVBoxLayout(self.curveTypeGroupBox)
        curveTypeLayout.setSpacing(5)

        self.quadraticRadioButton = QRadioButton("Квадратичная (3 точки)")
        self.quadraticRadioButton.toggled.connect(self.onBezierTypeChanged)
        curveTypeLayout.addWidget(self.quadraticRadioButton)

        self.cubicRadioButton = QRadioButton("Кубическая (4 точки)")
        self.cubicRadioButton.setChecked(True)
        self.cubicRadioButton.toggled.connect(self.onBezierTypeChanged)
        curveTypeLayout.addWidget(self.cubicRadioButton)

        paramRowLayout = QHBoxLayout()
        paramLabel = QLabel("Параметр t:")
        paramRowLayout.addWidget(paramLabel)
        self.parameterDisplayLabel = QLabel("0.50")
        self.parameterDisplayLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        paramRowLayout.addWidget(self.parameterDisplayLabel)
        curveTypeLayout.addLayout(paramRowLayout)

        self.parameterSlider = QSlider(Qt.Orientation.Horizontal)
        self.parameterSlider.setRange(0, 100)
        self.parameterSlider.setValue(50)
        self.parameterSlider.valueChanged.connect(self.onParameterSliderMoved)
        curveTypeLayout.addWidget(self.parameterSlider)

        stepButtonsLayout = QHBoxLayout()
        self.nextStepButton = QPushButton("Следующий шаг")
        self.nextStepButton.clicked.connect(self.onNextStepClicked)
        stepButtonsLayout.addWidget(self.nextStepButton)

        self.fullBuildButton = QPushButton("Полное построение")
        self.fullBuildButton.clicked.connect(self.onFullBuildClicked)
        stepButtonsLayout.addWidget(self.fullBuildButton)
        curveTypeLayout.addLayout(stepButtonsLayout)

        topPanelsLayout.addWidget(self.curveTypeGroupBox, stretch=2)

        # Кривая Чайкина
        self.chaikinGroupBox = QGroupBox("Кривая Чайкина")
        chaikinLayout = QVBoxLayout(self.chaikinGroupBox)
        chaikinLayout.setSpacing(6)

        chaikinRowLayout = QHBoxLayout()
        chaikinLabel = QLabel("Итерации:")
        chaikinRowLayout.addWidget(chaikinLabel)
        self.iterationsDisplayLabel = QLabel("3")
        self.iterationsDisplayLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chaikinRowLayout.addWidget(self.iterationsDisplayLabel)
        chaikinLayout.addLayout(chaikinRowLayout)

        self.chaikinSlider = QSlider(Qt.Orientation.Horizontal)
        self.chaikinSlider.setRange(1, 7)
        self.chaikinSlider.setValue(3)
        self.chaikinSlider.valueChanged.connect(self.onChaikinSliderMoved)
        chaikinLayout.addWidget(self.chaikinSlider)

        self.buildChaikinButton = QPushButton("Построить Чайкина")
        self.buildChaikinButton.clicked.connect(self.onBuildChaikinClicked)
        chaikinLayout.addWidget(self.buildChaikinButton)
        chaikinLayout.addStretch()

        topPanelsLayout.addWidget(self.chaikinGroupBox, stretch=1)

        # Управление точками
        self.pointsManagementGroupBox = QGroupBox("Управление точками")
        pointsLayout = QVBoxLayout(self.pointsManagementGroupBox)
        pointsLayout.setSpacing(6)

        self.addPointButton = QPushButton("Добавить точку")
        self.addPointButton.clicked.connect(self.onAddPointClicked)
        pointsLayout.addWidget(self.addPointButton)

        self.deleteLastPointButton = QPushButton("Удалить последнюю")
        self.deleteLastPointButton.clicked.connect(self.onDeleteLastPointClicked)
        pointsLayout.addWidget(self.deleteLastPointButton)

        self.clearAllPointsButton = QPushButton("Очистить все точки")
        self.clearAllPointsButton.clicked.connect(self.onClearAllPointsClicked)
        pointsLayout.addWidget(self.clearAllPointsButton)
        pointsLayout.addStretch()

        topPanelsLayout.addWidget(self.pointsManagementGroupBox, stretch=1)

        # Настройка отображения
        self.displaySettingsGroupBox = QGroupBox("Настройка отображения")
        displayLayout = QVBoxLayout(self.displaySettingsGroupBox)
        displayLayout.setSpacing(8)

        self.showIntermediateCheckBox = QCheckBox("Показывать промежуточные точки")
        self.showIntermediateCheckBox.setChecked(True)
        self.showIntermediateCheckBox.toggled.connect(self.onShowIntermediateToggled)
        displayLayout.addWidget(self.showIntermediateCheckBox)

        self.showControlCheckBox = QCheckBox("Показывать контрольные точки")
        self.showControlCheckBox.setChecked(True)
        self.showControlCheckBox.toggled.connect(self.onShowControlToggled)
        displayLayout.addWidget(self.showControlCheckBox)
        displayLayout.addStretch()

        topPanelsLayout.addWidget(self.displaySettingsGroupBox, stretch=1)

        rootLayout.addLayout(topPanelsLayout)

        
        self.canvasWidget = CurveCanvas()
        rootLayout.addWidget(self.canvasWidget, stretch=1)

    # Обработчик событий 
    def onBezierTypeChanged(self):
        if self.quadraticRadioButton.isChecked():
            self.canvasWidget.bezierDegree = 2
        else:
            self.canvasWidget.bezierDegree = 3
        self.canvasWidget.activeAlgorithm = "Безье"
        self.canvasWidget.currentStepIndex = 0
        self.canvasWidget.update()

    def onParameterSliderMoved(self, value):
        param = value / 100.0
        self.parameterDisplayLabel.setText(f"{param:.2f}")
        self.canvasWidget.parameterT = param
        self.canvasWidget.update()

    def onNextStepClicked(self):
        self.canvasWidget.activeAlgorithm = "Безье"
        self.canvasWidget.isFullBuildMode = False
        maxSteps = max(1, self.canvasWidget.bezierDegree)
        self.canvasWidget.currentStepIndex = (self.canvasWidget.currentStepIndex + 1) % maxSteps
        self.canvasWidget.update()

    def onFullBuildClicked(self):
        self.canvasWidget.activeAlgorithm = "Безье"
        self.canvasWidget.isFullBuildMode = True
        self.canvasWidget.update()

    def onChaikinSliderMoved(self, value):
        self.iterationsDisplayLabel.setText(str(value))
        self.canvasWidget.chaikinIterations = value
        if self.canvasWidget.activeAlgorithm == "Чайкина":
            self.canvasWidget.update()

    def onBuildChaikinClicked(self):
        self.canvasWidget.activeAlgorithm = "Чайкина"
        self.canvasWidget.update()

    def onAddPointClicked(self):
        if self.canvasWidget.controlPoints:
            lastPoint = self.canvasWidget.controlPoints[-1]
            newPoint = QPointF(
                lastPoint.x() + 90,
                lastPoint.y() + (60 if len(self.canvasWidget.controlPoints) % 2 == 0 else -60)
            )
        else:
            newPoint = QPointF(120, 260)
        self.canvasWidget.controlPoints.append(newPoint)
        self.canvasWidget.update()

    def onDeleteLastPointClicked(self):
        if self.canvasWidget.controlPoints:
            self.canvasWidget.controlPoints.pop()
            self.canvasWidget.update()

    def onClearAllPointsClicked(self):
        self.canvasWidget.controlPoints.clear()
        self.canvasWidget.update()

    def onShowIntermediateToggled(self, isChecked):
        self.canvasWidget.showIntermediatePoints = isChecked
        self.canvasWidget.update()

    def onShowControlToggled(self, isChecked):
        self.canvasWidget.showControlPoints = isChecked
        self.canvasWidget.update()
