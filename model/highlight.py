# Highlight 클래스
# 그냥 Immutable로 만들죠?
from dataclasses import dataclass

@dataclass(frozen=True)
class Highlight:
    start_time: int
    end_time: int
    memo: str
    id: int

    def to_display_string(self):
        return f"{self.start_time//60:02}:{self.start_time%60:02}~{self.end_time//60:02}:{self.end_time%60:02}, {self.memo}"