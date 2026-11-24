
class UiStyles:
    """Набор стилей для элементов интерфейса."""

    viewportStyle = "background-color: #3B6EB5; border-radius: 4px;"

    buttonStyle = """
            QPushButton {
                background-color: #3B6EB5;
                color: white;
                font-weight: 500;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4C82CF;
            }
            QPushButton:pressed {
                background-color: #2F5893;
            }
        """

    comboBoxStyle = """
            QComboBox {
                padding: 6px;
                border: 1px solid #3B6EB5;
                border-radius: 4px;
            }
        """

    sliderStyle = """
            QSlider::groove:horizontal {
                height: 6px;
                background: #C4D3E9;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #3B6EB5;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #234B80;
                width: 16px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 8px;
            }
        """