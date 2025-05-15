import sys
import time
import os
import logging

from typing import Dict, List

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit,
                             QLabel, QLineEdit, QFileDialog, QListWidget, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QMetaObject, Q_ARG, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut

from highlight import Highlight
from match import Match

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class HighlightRecordManager:
    def __init__(self):
        self.start_time = None
        self.running = False
        self.paused = False
        self.elapsed_time = 0
        self.current_match = 1
        self.highlight_start_time = None
        self.highlights_by_match: Dict[int, Match] = {self.current_match: Match(self.current_match)}
        self.record_button = None

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
        if not self.running:
            self.start_time = time.time()
            self.running = True
            self.paused = False

    def update_timer(self) -> None:
        if self.running and not self.paused:
            self.elapsed_time += 1

    def reset_timer(self) -> None:
        self.elapsed_time = 0
        self.highlight_start_time = None

    def __get_current_match(self) -> Match:
        if self.current_match not in self.highlights_by_match:
            self.highlights_by_match[self.current_match] = Match(self.current_match)
        return self.highlights_by_match[self.current_match]

    def record_highlight(self, status_label:QLabel, record_button:QPushButton, memo_input:QLineEdit, highlight_view:QListWidget) -> None:
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

    def delete_highlight(self, highlight_view:QListWidget) -> None:
        selected_items = highlight_view.selectedItems()
        if not selected_items:
            raise Exception("삭제할 하이라이트를 선택하세요.")
        for item in selected_items:
            row = highlight_view.row(item)
            highlight_view.takeItem(row)
            self.highlights_by_match[self.current_match].delete_highlight(row)
            logging.debug(f"Highlight deleted: {item.text()}")

    def edit_highlight_inline(self, highlight_view:QListWidget, main: QWidget) -> None:
        selected_items = highlight_view.currentItem()
        selected_highlight = self.highlights_by_match[self.current_match].get_highlights()[highlight_view.row(selected_items)]
        if not selected_items:
            raise Exception("수정할 하이라이트를 선택하세요.")

        new_text, ok = QInputDialog.getText(main, '하이라이트 수정', '내용을 수정하세요:', text=selected_highlight.memo)
        if ok and new_text:
            new_highlight = Highlight(
                selected_highlight.start_time,
                selected_highlight.end_time,
                new_text,
                selected_highlight.id
            )
            self.highlights_by_match[self.current_match].update_highlight(selected_highlight.id, new_highlight)
            highlight_view.currentItem().setText(new_highlight.to_display_string())
