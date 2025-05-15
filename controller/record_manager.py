import os
import time
import logging

from typing import Dict

from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QLineEdit, QListWidget, QInputDialog, QApplication,
                             QMessageBox, QFileDialog)

from model.highlight import Highlight
from model.match import Match
from view.main_view import MainView
from controller.IhighlightSave import HighlightSaveAll

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



class HighlightRecordController:
    def __init__(self, app: QApplication) -> None:
        self._app = app
        self._saveManager = HighlightSaveAll()

        self._match_model: Match = Match(1)
        self._view = MainView()

        self.start_time = None
        self.running = False
        self.paused = False
        self.elapsed_time = 0
        self.current_match = 1
        self.highlight_start_time = None
        self.highlights_by_match: Dict[int, Match] = {self.current_match: Match(self.current_match)}
        self.record_button = None

        self.init()

    def init(self):
        self._view.start_match_signal.connect(self.start_match)
        self._view.update_timer_signal.connect(self.update_timer)
        self._view.toggle_timer_signal.connect(self.toggle_timer)
        self._view.reset_timer_signal.connect(self.reset_timer)
        self._view.record_highlight_signal.connect(self.record_highlight)
        self._view.delete_highlight_signal.connect(self.delete_highlight)
        self._view.edit_highlight_inline_signal.connect(self.edit_highlight_inline)
        self._view.edit_match_time_signal.connect(self.edit_match_time)
        self._view.save_highlights_signal.connect(self.save_highlights)
        self._view.close_signal.connect(self.close)

    def run(self):
        self._view.show()
        return self._app.exec_()


    def get_elapsed_time(self) -> int:
        return self.elapsed_time

    def is_paused(self) -> bool:
        return self.paused

    def is_running(self) -> bool:
        return self.running

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def get_minutes_and_second(self):
        return [self.elapsed_time // 60, self.elapsed_time % 60]

    def get_minutes_and_seconds_text(self) -> str:
        return self.__make_time_label(self.elapsed_time)

    def __make_time_label(self, time: int) -> str:
        minutes = time // 60
        seconds = time % 60
        return f"{minutes:02}:{seconds:02}"

    def start_match(self) -> None:
        try:
            if not self.running:
                self.start_time = time.time()
                self.running = True
                self.paused = False
                self._view.timer.start(1000)
                self._view.status_label.setText("매치 시작됨")
        except Exception as e:
            logging.error(f"Error starting match: {e}")
            QMessageBox.critical(self._view, "오류", f"매치 시작 중 오류: {str(e)}")

    def toggle_timer(self):
        try:
            if self.running:
                self.toggle_pause()
                self._view.pause_button.setText('타이머 재개' if self.is_paused() else '타이머 일시정지')
                logging.debug(f"Timer {'paused' if self.is_paused() else 'resumed'}")
        except Exception as e:
            logging.error(f"Error in toggle_timer: {str(e)}")
            self._view.error_signal.emit(f"타이머 토글 중 오류: {str(e)}")

    def update_timer(self) -> None:
        if self.running and not self.paused:
            self.elapsed_time += 1
            self._view.timer_label.setText(self.__make_time_label(self.elapsed_time))

    def reset_timer(self) -> None:
        try:
            if self.running:
                self.elapsed_time = 0
                self.highlight_start_time = None
                self._view.timer_label.setText("00:00")
                self._view.status_label.setText("타이머 초기화됨")
                if self._view.record_button is None:
                    logging.error("record_button is None in reset_timer")
                    raise RuntimeError("Record button not initialized in reset_timer")
                self._view.record_button.setText('하이라이트 기록')
                logging.debug("record_button text set to '하이라이트 기록' in reset_timer")
        except Exception as e:
            logging.error(f"Error resetting timer: {e}")
            self._view.error_signal.emit(f"타이머 초기화 중 오류: {str(e)}")

    def __get_current_match(self) -> Match:
        if self.current_match not in self.highlights_by_match:
            self.highlights_by_match[self.current_match] = Match(self.current_match)
        return self.highlights_by_match[self.current_match]

    def record_highlight(self):
        try:
            if not self.running:
                self._view.warning_signal.emit("매치를 먼저 시작하세요.")
                logging.warning("Attempted to record highlight without starting match")
                return

            if self._view.record_button is None:
                logging.error("record_button is None in record_highlight")
                self._view.error_signal.emit("하이라이트 기록 버튼이 초기화되지 않았습니다.")
                return
            else:
                try:
                    self.__record_highlight(self._view.status_label, self._view.record_button, self._view.memo_input,self._view.highlights_view)
                except Exception as e:
                    logging.error(f"Error in start_highlight: {str(e)}")
                    self._view.warning_signal.emit("하이라이트 기간은 0초보다 길어야 합니다.")
                    return

        except Exception as e:
            logging.error(f"Error in record_highlight: {str(e)}")
            self._view.error_signal.emit( f"하이라이트 기록 중 오류: {str(e)}")

    def __record_highlight(self, status_label:QLabel, record_button:QPushButton, memo_input:QLineEdit, highlight_view:QListWidget) -> None:
        if self.highlight_start_time is None:
            self.highlight_start_time = self.elapsed_time
            status_label.setText(f"기록 시작: {self.__make_time_label(self.highlight_start_time)} (Recording...)")
            record_button.setText('기록 중지')
            logging.debug(f"Highlight started at {self.highlight_start_time}")
        else:
            start = self.highlight_start_time
            end  = self.elapsed_time
            if start >= end:
                raise Exception("Start time must be less than end time")
            memo = memo_input.text().strip() or '하이라이트'
            highlight = Highlight(start, end, memo, len(self.highlights_by_match[self.current_match].get_highlights()))
            self.highlights_by_match[self.current_match].add_highlight(highlight)
            logging.debug(f"Highlight recorded: {highlight}")
            highlight_view.addItem(highlight.to_display_string())

            self.highlight_start_time = None
            memo_input.clear()
            status_label.setText("하이라이트 기록됨")
            record_button.setText('하이라이트 기록')

    def delete_highlight(self) -> None:
        try:
            selected_items = self._view.highlights_view.selectedItems()
            if not selected_items:
                raise Exception("삭제할 하이라이트를 선택하세요.")
            for item in selected_items:
                row = self._view.highlights_view.row(item)
                self._view.highlights_view.takeItem(row)
                self.highlights_by_match[self.current_match].delete_highlight(row)
                logging.debug(f"Highlight deleted: {item.text()}")
        except Exception as e:
            logging.error(f"Error in delete_highlight: {str(e)}")
            self._view.error_signal.emit(f"하이라이트 삭제 중 오류: {str(e)}")

    def edit_highlight_inline(self) -> None:

        try:
            selected_items = self._view.highlights_view.currentItem()
            selected_highlight = self.highlights_by_match[self.current_match].get_highlights()[self._view.highlights_view.row(selected_items)]

            selected_items = self._view.highlights_view.currentItem()
            selected_highlight = self.highlights_by_match[self.current_match].get_highlights()[self._view.highlights_view.row(selected_items)]
            if not selected_items:
                raise Exception("수정할 하이라이트를 선택하세요.")

            new_text, ok = QInputDialog.getText(self._view, '하이라이트 수정', '내용을 수정하세요:', text=selected_highlight.memo)
            if ok and new_text:
                new_highlight = Highlight(
                    selected_highlight.start_time,
                    selected_highlight.end_time,
                    new_text,
                    selected_highlight.id
                )
                self.highlights_by_match[self.current_match].update_highlight(selected_highlight.id, new_highlight)
                self._view.highlights_view.currentItem().setText(new_highlight.to_display_string())
        except Exception as e:
            logging.error(f"Error in edit_highlight_inline: {str(e)}")
            self._view.error_signal.emit(f"하이라이트 수정 중 오류: {str(e)}")

    def edit_match_time(self):
        try:
            if self.running:
                new_time, ok = QInputDialog.getText(self._view, '매치 시간 수정', '새 경기 시간을 입력하세요 (MM:SS 형식):')
                if ok and new_time:
                    minutes, seconds = map(int, new_time.split(':'))
                    self.elapsed_time = minutes * 60 + seconds
                    self._view.timer_label.setText(f"{minutes:02}:{seconds:02}")
                    self._view.status_label.setText("시간 수정됨")
                    logging.debug(f"Match time edited to {minutes:02}:{seconds:02}")
        except ValueError:
            self._view.warning_signal.emit("입력 오류", "올바른 형식(MM:SS)으로 입력하세요.")
            logging.warning("Invalid time format in edit_match_time")
        except Exception as e:
            logging.error(f"Error in edit_match_time: {str(e)}")
            self._view.error_signal.emit("오류", f"매치 시간 수정 중 오류: {str(e)}")

    def save_highlights(self):
        try:
            dir, _ = QFileDialog.getSaveFileName(self._view, "하이라이트 저장할 폴더 선택", os.getcwd())
            success = self._saveManager.save_highlights(self.highlights_by_match.values(), dir)
            if success:
                self._view.status_label.setText("파일 저장됨")
                logging.debug("Highlights saved successfully")
        except Exception as e:
            logging.error(f"Error in save_highlights: {str(e)}")
            self._view.error_signal.emit("오류", f"하이라이트 저장 중 오류: {str(e)}")

    def close(self, event):
        try:
            if any(self.highlights_by_match.values()):
                logging
                self.save_highlights()
        except Exception as e:
            logging.error(f"Error in closeEvent: {str(e)}")
            self._view.error_signal.emit("오류", f"종료 중 오류: {str(e)}")
        finally:
            event.accept()
            logging.debug("Close event accepted")