#Если не установлен PyQt, напишите в терминале pip Install PyQt6

import sys
import math
import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QGroupBox, QMessageBox,
    QScrollArea
)
from PyQt6.QtGui import QImage, QPixmap, QColor, QPainter, QPen
from PyQt6.QtCore import Qt


# Алгоритмы растеризации

def rasterize_dda(x1: float, y1: float, x2: float, y2: float) -> list[tuple[int, int]]:
    """Алгоритм ЦДА (Цифровой дифференциальный анализатор)."""
    points = []
    if x1 == x2 and y1 == y2:
        return [(math.floor(x1), math.floor(y1))]
    
    dx = x2 - x1
    dy = y2 - y1
    length = max(abs(dx), abs(dy))
    
    if length == 0:
        return [(math.floor(x1), math.floor(y1))]
        
    x_inc = dx / length
    y_inc = dy / length
    
    x = x1 + 0.5 * (1 if x_inc > 0 else (-1 if x_inc < 0 else 0))
    y = y1 + 0.5 * (1 if y_inc > 0 else (-1 if y_inc < 0 else 0))
    
    for _ in range(int(round(length)) + 1):
        points.append((math.floor(x), math.floor(y)))
        x += x_inc
        y += y_inc
        
    return points


def rasterize_brezenham_float(x1: float, y1: float, x2: float, y2: float) -> list[tuple[int, int]]:
    """Вещественный алгоритм Брезенхема."""
    points = []
    if x1 == x2 and y1 == y2:
        return [(math.floor(x1), math.floor(y1))]
        
    sx = 1 if x2 > x1 else (-1 if x2 < x1 else 0)
    sy = 1 if y2 > y1 else (-1 if y2 < y1 else 0)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    x, y = x1, y1
    flag = 0
    
    if dy > dx:
        dx, dy = dy, dx
        flag = 1
        
    e = (dy / dx) - 0.5 if dx != 0 else 0
    
    for _ in range(int(round(dx)) + 1):
        points.append((math.floor(x), math.floor(y)))
        if e >= 0:
            if flag == 1:
                x += sx
            else:
                y += sy
            e -= 1.0
        if flag == 1:
            y += sy
        else:
            x += sx
        e += (dy / dx) if dx != 0 else 0
        
    return points


def rasterize_brezenham_int(x1: float, y1: float, x2: float, y2: float) -> list[tuple[int, int]]:
    """Целочисленный алгоритм Брезенхема."""
    points = []
    ix1, iy1, ix2, iy2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
    
    if ix1 == ix2 and iy1 == iy2:
        return [(ix1, iy1)]
        
    sx = 1 if ix2 > ix1 else (-1 if ix2 < ix1 else 0)
    sy = 1 if iy2 > iy1 else (-1 if iy2 < iy1 else 0)
    dx = abs(ix2 - ix1)
    dy = abs(iy2 - iy1)
    
    x, y = ix1, iy1
    flag = 0
    
    if dy > dx:
        dx, dy = dy, dx
        flag = 1
        
    e = 2 * dy - dx
    
    for _ in range(dx + 1):
        points.append((x, y))
        if e >= 0:
            if flag == 1:
                x += sx
            else:
                y += sy
            e -= 2 * dx
        if flag == 1:
            y += sy
        else:
            x += sx
        e += 2 * dy
        
    return points


# Главный GUI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная работа № 3")
        
        self.img_width = 800
        self.img_height = 500
        self.segments = []  
        self.svg_file_path = None  
        self.current_algo = "dda" 
        
        self.init_ui()
        self.create_canvas()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Группа параметры холста
        box_canvas = QGroupBox("Параметры холста")
        layout_canvas = QHBoxLayout()
        layout_canvas.addWidget(QLabel("Ширина:"))
        self.edit_width = QLineEdit("800")
        self.edit_width.setFixedWidth(60)
        layout_canvas.addWidget(self.edit_width)
        
        layout_canvas.addWidget(QLabel("Высота:"))
        self.edit_height = QLineEdit("500")
        self.edit_height.setFixedWidth(60)
        layout_canvas.addWidget(self.edit_height)
        
        self.btn_create_canvas = QPushButton("Создать холст")
        self.btn_create_canvas.clicked.connect(self.create_canvas)
        layout_canvas.addWidget(self.btn_create_canvas)
        layout_canvas.addStretch()
        box_canvas.setLayout(layout_canvas)
        main_layout.addWidget(box_canvas)

        # Блок загрузки 
        box_svg = QGroupBox("Загрузка SVG")
        layout_svg = QHBoxLayout()
        self.btn_load_svg = QPushButton("Загрузить SVG")
        self.btn_load_svg.clicked.connect(self.load_svg)
        layout_svg.addWidget(self.btn_load_svg)
        
        self.lbl_svg_status = QLabel("SVG не загружен")
        self.lbl_svg_status.setStyleSheet("color: red; font-weight: bold;")
        layout_svg.addWidget(self.lbl_svg_status)
        layout_svg.addStretch()
        box_svg.setLayout(layout_svg)
        main_layout.addWidget(box_svg)

        # Параметры прямоугольника
        box_rect = QGroupBox("Параметры прямоугольника")
        layout_rect = QHBoxLayout()
        
        layout_rect.addWidget(QLabel("Левый верхний: X1:"))
        self.edit_x1 = QLineEdit("100")
        self.edit_x1.setFixedWidth(50)
        layout_rect.addWidget(self.edit_x1)
        
        layout_rect.addWidget(QLabel("Y1:"))
        self.edit_y1 = QLineEdit("100")
        self.edit_y1.setFixedWidth(50)
        layout_rect.addWidget(self.edit_y1)
        
        layout_rect.addWidget(QLabel("Правый нижний: X2:"))
        self.edit_x2 = QLineEdit("400")
        self.edit_x2.setFixedWidth(50)
        layout_rect.addWidget(self.edit_x2)
        
        layout_rect.addWidget(QLabel("Y2:"))
        self.edit_y2 = QLineEdit("300")
        self.edit_y2.setFixedWidth(50)
        layout_rect.addWidget(self.edit_y2)
        
        layout_rect.addStretch()
        box_rect.setLayout(layout_rect)
        main_layout.addWidget(box_rect)

        # Алгоритмы растеризации
        box_algo = QGroupBox("Алгоритмы растеризации")
        layout_algo = QHBoxLayout()
        
        self.btn_dda = QPushButton("ЦДА")
        self.btn_brez = QPushButton("Брезенхем")
        self.btn_brez_int = QPushButton("Целочисленный")
        self.btn_native = QPushButton("Встроенные средства")
        
        self.btn_dda.clicked.connect(lambda: self.set_algo("dda"))
        self.btn_brez.clicked.connect(lambda: self.set_algo("brezenham_float"))
        self.btn_brez_int.clicked.connect(lambda: self.set_algo("brezenham_int"))
        self.btn_native.clicked.connect(lambda: self.set_algo("native"))
        
        layout_algo.addWidget(self.btn_dda)
        layout_algo.addWidget(self.btn_brez)
        layout_algo.addWidget(self.btn_brez_int)
        layout_algo.addWidget(self.btn_native)
        box_algo.setLayout(layout_algo)
        main_layout.addWidget(box_algo)

        # Управление
        box_control = QGroupBox("Управление")
        layout_control = QHBoxLayout()
        
        self.btn_save_bmp = QPushButton("Сохранить BMP")
        self.btn_save_pbm = QPushButton("Сохранить PBM")
        self.btn_clear = QPushButton("Очистить")
        self.btn_draw = QPushButton("Нарисовать")
        self.btn_draw_svg = QPushButton("Нарисовать SVG")
        
        self.btn_save_bmp.clicked.connect(self.save_bmp)
        self.btn_save_pbm.clicked.connect(self.save_pbm)
        self.btn_clear.clicked.connect(self.clear_canvas)
        self.btn_draw.clicked.connect(self.draw_from_inputs)
        self.btn_draw_svg.clicked.connect(self.draw_from_svg)
        
        layout_control.addWidget(self.btn_save_bmp)
        layout_control.addWidget(self.btn_save_pbm)
        layout_control.addWidget(self.btn_clear)
        layout_control.addWidget(self.btn_draw)
        layout_control.addWidget(self.btn_draw_svg)
        box_control.setLayout(layout_control)
        main_layout.addWidget(box_control)

        # Область холста
        scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.image_label.setStyleSheet("background-color: white; border: 1px solid black;")
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

    #Создание холста
    def create_canvas(self):
        """Создание пустого холста заданных размеров."""
        try:
            self.img_width = int(self.edit_width.text())
            self.img_height = int(self.edit_height.text())
            self.image = QImage(self.img_width, self.img_height, QImage.Format.Format_RGB32)
            self.image.fill(QColor(255, 255, 255))
            self.update_display()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректные числовые значения размеров холста!")

    # Уствановка алгоритма
    def set_algo(self, algo_name):
        self.current_algo = algo_name
        self.redraw()

    # Обновление изображения
    def update_display(self):
        self.image_label.setPixmap(QPixmap.fromImage(self.image))

    # Очистка холста
    def clear_canvas(self):
        self.segments = []
        self.image.fill(QColor(255, 255, 255))
        self.update_display()

    # Загрузка SVG
    def load_svg(self):
        """Выбор файла SVG и обновление информации интерфейса."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть SVG", "", "SVG Files (*.svg)")
        if not file_path:
            return

        self.svg_file_path = file_path
        self.lbl_svg_status.setText("SVG загружен")
        self.lbl_svg_status.setStyleSheet("color: green; font-weight: bold;")
        self.parse_and_fill_svg()

    def parse_and_fill_svg(self):
        """Парсинг файла SVG, заполнение полей ввода и подготовка отрезков."""
        if not self.svg_file_path:
            return False

        try:
            tree = ET.parse(self.svg_file_path)
            root = tree.getroot()
            
            rect_elem = root.find('.//{http://www.w3.org/2000/svg}rect')
            if rect_elem is None:
                rect_elem = root.find('rect')
        
            if rect_elem is not None:
                x1 = float(rect_elem.attrib.get('x', 0))
                y1 = float(rect_elem.attrib.get('y', 0))
                w = float(rect_elem.attrib.get('width', 100))
                h = float(rect_elem.attrib.get('height', 100))
                
                x2 = x1 + w
                y2 = y1 + h

                # Заполнение текстовых полей
                self.edit_x1.setText(str(int(x1)))
                self.edit_y1.setText(str(int(y1)))
                self.edit_x2.setText(str(int(x2)))
                self.edit_y2.setText(str(int(y2)))

                # Построение 4 отрезков прямоугольника
                self.segments = [
                    (x1, y1, x2, y1),
                    (x2, y1, x2, y2),
                    (x2, y2, x1, y2),
                    (x1, y2, x1, y1)
                ]
                return True
            else:
                QMessageBox.warning(self, "Ошибка", "Элемент <rect> не найден в SVG!")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка чтения SVG: {e}")
            return False

    def draw_from_svg(self):
        """Считывание данных из SVG и отрисовка на холсте."""
        if not self.svg_file_path:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите SVG-файл с помощью кнопки 'Загрузить SVG'!")
            return

        if self.parse_and_fill_svg():
            self.redraw()

    def draw_from_inputs(self):
        """Считывание введенных вручную координат и отрисовка."""
        try:
            x1 = float(self.edit_x1.text())
            y1 = float(self.edit_y1.text())
            x2 = float(self.edit_x2.text())
            y2 = float(self.edit_y2.text())

            self.segments = [
                (x1, y1, x2, y1),
                (x2, y1, x2, y2),
                (x2, y2, x1, y2),
                (x1, y2, x1, y1)
            ]
            self.redraw()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Координаты должны быть числами!")

    def redraw(self):
        """Отрисовка отрезков на QImage выбранным алгоритмом."""
        self.image.fill(QColor(255, 255, 255))
        if not self.segments:
            self.update_display()
            return

        pen_color = QColor(0, 0, 0)

        if self.current_algo == "native":
            painter = QPainter(self.image)
            painter.setPen(QPen(pen_color, 1))
            for x1, y1, x2, y2 in self.segments:
                painter.drawLine(int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)))
            painter.end()
        else:
            for x1, y1, x2, y2 in self.segments:
                if self.current_algo == "dda":
                    pts = rasterize_dda(x1, y1, x2, y2)
                elif self.current_algo == "brezenham_float":
                    pts = rasterize_brezenham_float(x1, y1, x2, y2)
                elif self.current_algo == "brezenham_int":
                    pts = rasterize_brezenham_int(x1, y1, x2, y2)

                for px, py in pts:
                    if 0 <= px < self.img_width and 0 <= py < self.img_height:
                        self.image.setPixelColor(px, py, pen_color)

        self.update_display()

    def save_bmp(self):
        """Сохранение изображения в формат BMP."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить BMP", "output.bmp", "BMP Files (*.bmp)")
        if file_path:
            self.image.save(file_path, "BMP")
            QMessageBox.information(self, "Успех", f"Изображение успешно сохранено в BMP:\n{file_path}")

    def save_pbm(self):
        """Сохранение изображения в текстовый формат PBM (Netpbm - P1 ASCII)."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить PBM", "output.pbm", "PBM Files (*.pbm)")
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("P1\n")
                f.write("# Created by PyQt6 Rasterizer\n")
                f.write(f"{self.img_width} {self.img_height}\n")
                
                for y in range(self.img_height):
                    line = []
                    for x in range(self.img_width):
                        color = self.image.pixelColor(x, y)
                        bit = "1" if color.red() < 128 else "0"
                        line.append(bit)
                    f.write(" ".join(line) + "\n")
                    
            QMessageBox.information(self, "Успех", f"Изображение успешно сохранено в PBM:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())