import sys
import time
import os
from typing import List, Dict
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit,
                             QLabel, QLineEdit, QFileDialog, QListWidget, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QMetaObject, Q_ARG, Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
import keyboard
import logging
from highlight import Highlight
from record_manager import HighlightRecordManager
from IhighlightSave import HighlightSaveAll

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class HighlightRecorder(QWidget):
    warning_signal = pyqtSignal(str, str)
    info_signal = pyqtSignal(str, str)
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.manager = HighlightRecordManager()
        self.saveManager = HighlightSaveAll()

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
        self.memo_input.returnPressed.connect(self.record_highlight)
        layout.addWidget(self.memo_input)

        self.start_button = QPushButton('매치 시작', self)
        self.start_button.clicked.connect(self.start_match)
        layout.addWidget(self.start_button)

        self.pause_button = QPushButton('타이머 일시정지', self)
        self.pause_button.clicked.connect(self.toggle_timer)
        layout.addWidget(self.pause_button)

        self.reset_button = QPushButton('타이머 초기화', self)
        self.reset_button.clicked.connect(self.reset_timer)
        layout.addWidget(self.reset_button)

        self.record_button = QPushButton('하이라이트 기록', self)
        self.record_button.clicked.connect(self.record_highlight)
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
        # self.edit_time_button = QPushButton('매치 시간 수정', self)
        # self.edit_time_button.clicked.connect(self.edit_match_time)
        # layout.addWidget(self.edit_time_button)

        self.delete_button = QPushButton('하이라이트 삭제', self)
        self.delete_button.clicked.connect(self.delete_highlight)
        layout.addWidget(self.delete_button)

        self.save_button = QPushButton('메모 저장', self)
        self.save_button.clicked.connect(self.save_highlights)
        layout.addWidget(self.save_button)

        if self.record_button is None:
            logging.error("Record button is None after initUI")
            raise RuntimeError("Failed to initialize record_button")

        self.highlights_view = QListWidget(self)
        self.highlights_view.itemDoubleClicked.connect(self.edit_highlight_inline)
        layout.addWidget(self.highlights_view)

        self.setLayout(layout)
        self.setFixedSize(400, 880)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        # F1 핫키를 QShortcut로 대체하여 스레드 문제 방지
        self.f1_shortcut = QShortcut(QKeySequence('F1'), self)
        self.f1_shortcut.activated.connect(self.record_highlight)
        logging.debug("F1 shortcut registered with QShortcut")

        self.warning_signal.connect(self.show_warning)
        self.info_signal.connect(self.show_info)
        self.error_signal.connect(self.show_error)

        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        delete_shortcut.activated.connect(self.delete_highlight)

    def current_highlight_list(self):
        return self.highlights_by_match.setdefault(self.match, [])

    def start_match(self):
        try:
            if not self.manager.is_running():
                self.manager.start_match()
                self.timer.start(1000)
                # self.auto_save_timer.start(60000)
                self.status_label.setText("매치 시작됨")
                logging.debug("Match started")
        except Exception as e:
            logging.error(f"Error in start_match: {str(e)}")
            QMessageBox.critical(self, "오류", f"매치 시작 중 오류: {str(e)}")

    def update_timer(self):
        try:
            if not self.manager.is_paused():
                self.manager.update_timer()
                self.timer_label.setText(f"{self.manager.get_minutes_and_seconds_text()}")
        except Exception as e:
            logging.error(f"Error in update_timer: {str(e)}")
            self.warning_signal.emit("오류", f"타이머 업데이트 중 오류: {str(e)}")

    def toggle_timer(self):
        try:
            if self.manager.is_running():
                self.manager.toggle_pause()
                self.pause_button.setText('타이머 재개' if self.manager.is_paused() else '타이머 일시정지')
                logging.debug(f"Timer {'paused' if self.manager.is_paused() else 'resumed'}")
        except Exception as e:
            logging.error(f"Error in toggle_timer: {str(e)}")
            self.error.emit(f"타이머 토글 중 오류: {str(e)}")

    def reset_timer(self):
        try:
            if self.manager.is_running():
                self.manager.reset_timer()
                self.timer_label.setText("00:00")
                self.status_label.setText("타이머 초기화됨")
                if self.record_button is None:
                    logging.error("record_button is None in reset_timer")
                    raise RuntimeError("Record button not initialized in reset_timer")
                self.record_button.setText('하이라이트 기록')
                logging.debug("record_button text set to '하이라이트 기록' in reset_timer")
        except Exception as e:
            logging.error(f"Error in reset_timer: {str(e)}")
            self.status_label.setText("타이머 초기화 중 오류")

    def record_highlight(self):
        try:
            if not self.manager.is_running():
                self.warning_signal.emit("오류", "매치를 먼저 시작하세요.")

                logging.warning("Attempted to record highlight without starting match")
                return

            if self.record_button is None:
                logging.error("record_button is None in record_highlight")

                self.error_signal.emit("오류", "하이라이트 기록 버튼이 초기화되지 않았습니다.")

                return

            else:
                try:
                    self.manager.record_highlight(self.status_label, self.record_button, self.memo_input,
                                                  self.highlights_view)
                except Exception as e:
                    logging.error(f"Error in start_highlight: {str(e)}")

                    self.warning_signal.emit("오류", "하이라이트 기간은 0초보다 길어야 합니다.")

                    return


        except Exception as e:
            logging.error(f"Error in record_highlight: {str(e)}")
            self.error_signal.emit("오류", f"하이라이트 기록 중 오류: {str(e)}")

    def delete_highlight(self):
        try:
            self.manager.delete_highlight(self.highlights_view)
        except Exception as e:
            logging.error(f"Error in delete_highlight: {str(e)}")

            self.error_signal.emit("오류", f"하이라이트 삭제 중 오류: {str(e)}")

    def edit_match_time(self):
        try:
            if self.running:
                new_time, ok = QInputDialog.getText(self, '매치 시간 수정', '새 경기 시간을 입력하세요 (MM:SS 형식):')
                if ok and new_time:
                    minutes, seconds = map(int, new_time.split(':'))
                    self.elapsed_time = minutes * 60 + seconds
                    self.timer_label.setText(f"{minutes:02}:{seconds:02}")
                    self.status_label.setText("시간 수정됨")
                    logging.debug(f"Match time edited to {minutes:02}:{seconds:02}")
        except ValueError:
            self.warning_signal.emit("입력 오류", "올바른 형식(MM:SS)으로 입력하세요.")

            logging.warning("Invalid time format in edit_match_time")
        except Exception as e:
            logging.error(f"Error in edit_match_time: {str(e)}")
            self.error_signal.emit("오류", f"매치 시간 수정 중 오류: {str(e)}")

    def edit_highlight_inline(self):
        try:
            self.manager.edit_highlight_inline(self.highlights_view, self)
        except Exception as e:
            logging.error(f"Error in edit_highlight_inline: {str(e)}")
            self.error_signal.emit("오류", f"하이라이트 수정 중 오류: {str(e)}")

    def save_highlights(self):
        try:
            dir, _ = QFileDialog.getSaveFileName(self, "하이라이트 저장할 폴더 선택", os.getcwd())
            success = self.saveManager.save_highlights(self.manager.highlights_by_match.values(), dir)
            if success:
                self.status_label.setText("파일 저장됨")
                logging.debug("Highlights saved successfully")
        except Exception as e:
            logging.error(f"Error in save_highlights: {str(e)}")
            self.status_label.setText(f"하이라이트 저장 중 오류: {str(e)}")

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
        try:
            if not any(self.manager.highlights_by_match.values()):
                event.accept()
                return

            reply = QMessageBox.question(self, '종료 확인',
                                         '하이라이트가 저장되지 않았습니다. 저장 후 종료하시겠습니까?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.save_highlights()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
            logging.debug("Close event handled")
        except Exception as e:
            logging.error(f"Error in closeEvent: {str(e)}")
            self.error_signal.emit("오류", f"종료 처리 중 오류: {str(e)}")

    # 에러 메시지 표시를 메인 스레드에서 처리
    def show_error(self, message):
        QMessageBox.critical(self, "오류", message)

    def show_warning(self, title, message):
        QMessageBox.warning(self, title, message)

    def show_info(self, title, message):
        QMessageBox.information(self, title, message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    recorder = HighlightRecorder()
    recorder.show()
    sys.exit(app.exec_())
