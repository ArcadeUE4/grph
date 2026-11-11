# Если не установлен PyQt, напишите в терминале: pip install PyQt6 numpy

import sys
from PyQt6.QtWidgets import QApplication
from MainWindow import MainWindow


if __name__ == "__main__":
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())