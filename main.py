import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QListWidget, QInputDialog, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
import logging
from controller.record_manager import HighlightRecordController
from view.main_view import MainView

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    app = QApplication(sys.argv)
    controller = HighlightRecordController(app)
    sys.exit(controller.run())


if __name__ == '__main__':
    main()