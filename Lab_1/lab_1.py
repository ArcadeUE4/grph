# Для установки Qt, напишите в терминале pip install PyQt6

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, 
    QLabel, QFileDialog, QHBoxLayout, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QImage, QPixmap, QColor
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Обработка пикселей")
        self.resize(600, 400)
        
        self.image = None
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Элементы управления
        self.btn_open = QPushButton("Открыть")
        self.btn_process = QPushButton("Обработать")
        self.btn_save_png = QPushButton("Сохранить в PNG")
        self.btn_save_pbm = QPushButton("Сохранить в PBM")
        

        # Подключение кнопок
        self.btn_open.clicked.connect(self.open_image)
        self.btn_process.clicked.connect(self.process_image)
        self.btn_save_png.clicked.connect(self.save_png)
        self.btn_save_pbm.clicked.connect(self.save_pbm)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_process)
        btn_layout.addWidget(self.btn_save_png)
        btn_layout.addWidget(self.btn_save_pbm)


        # Главный макет
        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.image_label) 

        # Контейнер для центрального виджета
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    # Открытие изображения PNG
    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Изображение PNG", "", "Images (*.png )")

        if file_path:
            self.image = QImage(file_path)
            self.update_display()
    # Обработка изображения
    def process_image(self):
        if self.image is None or self.image.isNull():
            return

        width = self.image.width()
        height = self.image.height()

        # Верхний левый угол (0, 0, 0)
        self.image.setPixelColor(0, 0, QColor(0, 0, 0)) 

        # Центр верхней строки (255, 0, 0)
        self.image.setPixelColor(width // 2, 0, QColor(255, 0, 0))

        # Центр левого столбца (0, 255, 0)
        self.image.setPixelColor(0, height // 2, QColor(0, 255, 0))

        self.update_display()
    # Сохранение изображения в формате PNG
    def save_png(self):
        if self.image is None or self.image.isNull():
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить в PNG", "", "Images (*.png)")

        if file_path:
            self.image.save(file_path, "PNG")
    # Сохранение изображения в формате PBM
    def save_pbm(self):
        if self.image is None or self.image.isNull():
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить в PBM", "", "Images (*.pbm)")

        if file_path:
            if not file_path.endswith('.pbm'):
                file_path += '.pbm'

            pbm_image = self.image.convertToFormat(QImage.Format.Format_Mono)
            pbm_image.save(file_path, "PBM")
    # Обновление отображения изображения в QLabel
    def update_display(self):
        if self.image and not self.image.isNull():
            pixmap = QPixmap.fromImage(self.image)
            self.image_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())