from model.highlight import Highlight


# Match 클래스
class Match:
    def __init__(self, match_id: int) -> None:
        self.__match_id = match_id
        self.__highlights = []

    def add_highlight(self, highlight: Highlight) -> None:
        self.__highlights.append(highlight)

    def get_highlight_length(self) -> int:
        return len(self.__highlights)

    def get_highlights(self) -> list[Highlight]:
        return self.__highlights

    def get_match_id(self) -> int:
        return self.__match_id

    def update_highlight(self, highlight_id: int, new_highlight: Highlight) -> bool:
        for i, highlight in enumerate(self.__highlights):
            if highlight.id == highlight_id:
                self.__highlights[i] = new_highlight
                return True
        return False

    def delete_highlight(self, highlight_index: int) -> bool:
        if 0 <= highlight_index < len(self.__highlights):
            del self.__highlights[highlight_index]
            return True
        return False

    def __repr__(self) -> str:
        return f"Match({self.__match_id})"