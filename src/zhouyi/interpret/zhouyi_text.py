from __future__ import annotations

from zhouyi.domain.models import Hexagram
from zhouyi.infra.repository import DataRepository


def primary_texts(
    repository: DataRepository, hexagram: Hexagram, language: str = "zh"
) -> dict[str, object]:
    return repository.get_primary_texts(hexagram, language)


def changing_line_texts(
    repository: DataRepository,
    hexagram: Hexagram,
    changing_lines: tuple[int, ...],
    language: str = "zh",
    relating_hexagram: Hexagram | None = None,
) -> list[dict[str, object]]:
    moving_count = len(changing_lines)
    if moving_count == 0:
        return []
    if moving_count <= 3:
        return repository.get_line_texts(
            hexagram.king_wen_index, changing_lines, language
        )
    if moving_count == 6:
        return _six_moving_texts(repository, hexagram, language)
    unmoving = tuple(i for i in range(1, 7) if i not in changing_lines)
    if relating_hexagram is None:
        return []
    if moving_count == 4:
        return repository.get_line_texts(
            relating_hexagram.king_wen_index, unmoving, language
        )
    if moving_count == 5:
        return repository.get_line_texts(
            relating_hexagram.king_wen_index, unmoving, language
        )
    return []


def _six_moving_texts(
    repository: DataRepository, hexagram: Hexagram, language: str = "zh"
) -> list[dict[str, object]]:
    if hexagram.king_wen_index == 1:
        return [repository.get_yong_text(1, language)]
    if hexagram.king_wen_index == 2:
        return [repository.get_yong_text(2, language)]
    return []
