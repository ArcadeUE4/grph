# Если не установлен PyQt, напишите в терминале: pip install PyQt6 numpy

import sys
from PyQt6.QtWidgets import QApplication
from mainWindow import MainWindow


def startApplication():
    applicationInstance = QApplication(sys.argv)
    applicationWindow = MainWindow()
    applicationWindow.show()
    sys.exit(applicationInstance.exec())


if __name__ == "__main__":
    startApplication()