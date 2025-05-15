from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QListWidget, QInputDialog, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
import logging
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainView(QWidget):
    warning_signal = pyqtSignal(str, str)
    info_signal = pyqtSignal(str, str)
    error_signal = pyqtSignal(str)

    start_match_signal = pyqtSignal()
    update_timer_signal = pyqtSignal()
    toggle_timer_signal = pyqtSignal()
    reset_timer_signal = pyqtSignal()
    record_highlight_signal = pyqtSignal()
    delete_highlight_signal = pyqtSignal()
    edit_highlight_inline_signal = pyqtSignal()
    edit_match_time_signal = pyqtSignal()
    save_highlights_signal = pyqtSignal()
    close_signal = pyqtSignal(object)

    def __init__(self):
        super(MainView, self).__init__()

        # self.auto_save_timer = QTimer()
        # self.auto_save_timer.timeout.connect(self.auto_save_highlights)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('하이라이트 메모 프로그램')
        layout = QVBoxLayout()

        self.timer_label = QLabel('00:00', self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.timer_label)

        self.status_label = QLabel('', self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: green;")
        layout.addWidget(self.status_label)

        self.memo_input = QLineEdit(self)
        self.memo_input.setPlaceholderText('하이라이트 설명 입력 (예: 1대4 클러치)')
        self.memo_input.returnPressed.connect(self.record_highlight_signal)
        layout.addWidget(self.memo_input)

        self.start_button = QPushButton('매치 시작', self)
        self.start_button.clicked.connect(self.start_match_signal)
        layout.addWidget(self.start_button)

        self.pause_button = QPushButton('타이머 일시정지', self)
        self.pause_button.clicked.connect(self.toggle_timer_signal)
        layout.addWidget(self.pause_button)

        self.reset_button = QPushButton('타이머 초기화', self)
        self.reset_button.clicked.connect(self.reset_timer_signal)
        layout.addWidget(self.reset_button)

        self.record_button = QPushButton('하이라이트 기록', self)
        self.record_button.clicked.connect(self.record_highlight_signal)
        layout.addWidget(self.record_button)
        logging.debug("Record button explicitly initialized")

        # self.new_match_button = QPushButton('새 매치', self)
        # self.new_match_button.clicked.connect(self.new_match)
        # layout.addWidget(self.new_match_button)
        #
        # self.edit_match_button = QPushButton('매치 번호 수정', self)
        # self.edit_match_button.clicked.connect(self.edit_match_number)
        # layout.addWidget(self.edit_match_button)
        #
        self.edit_time_button = QPushButton('매치 시간 수정', self)
        self.edit_time_button.clicked.connect(self.edit_match_time_signal)
        layout.addWidget(self.edit_time_button)

        self.delete_button = QPushButton('하이라이트 삭제', self)
        self.delete_button.clicked.connect(self.delete_highlight_signal)
        layout.addWidget(self.delete_button)

        self.save_button = QPushButton('메모 저장', self)
        self.save_button.clicked.connect(self.save_highlights_signal)
        layout.addWidget(self.save_button)

        if self.record_button is None:
            logging.error("Record button is None after initUI")
            raise RuntimeError("Failed to initialize record_button")

        self.highlights_view = QListWidget(self)
        self.highlights_view.itemDoubleClicked.connect(self.edit_highlight_inline_signal)
        layout.addWidget(self.highlights_view)

        self.setLayout(layout)
        self.setFixedSize(400, 880)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_signal)

        # F1 핫키를 QShortcut로 대체하여 스레드 문제 방지
        self.f1_shortcut = QShortcut(QKeySequence('F1'), self)
        self.f1_shortcut.activated.connect(self.record_highlight_signal)
        logging.debug("F1 shortcut registered with QShortcut")

        self.warning_signal.connect(self.show_warning)
        self.info_signal.connect(self.show_info)
        self.error_signal.connect(self.show_error)

        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        delete_shortcut.activated.connect(self.delete_highlight_signal)

    def current_highlight_list(self):
        return self.highlights_by_match.setdefault(self.match, [])

    #
    # def auto_save_highlights(self):
    #     try:
    #         if not self.highlights_by_match:
    #             return
    #         os.makedirs('autosaves', exist_ok=True)
    #         with open('autosaves/highlights_autosave.txt', 'w', encoding='utf-8') as f:
    #             for m, lst in self.highlights_by_match.items():
    #                 for h in lst:
    #                     f.write(h.to_display_string() + '\n')
    #         logging.debug("Auto-save completed")
    #     except Exception as e:
    #         logging.error(f"Auto-save failed: {str(e)}")

    def closeEvent(self, event):
        self.close_signal.emit(event)


    # 에러 메시지 표시를 메인 스레드에서 처리
    def show_error(self, message):
        QMessageBox.critical(self, "오류", message)

    def show_warning(self, title, message):
        QMessageBox.warning(self, title, message)

    def show_info(self, title, message):
        QMessageBox.information(self, title, message)

