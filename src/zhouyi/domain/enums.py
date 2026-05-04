from __future__ import annotations

from enum import Enum, IntEnum


class LineState(IntEnum):
    OLD_YIN = 6
    YOUNG_YANG = 7
    YOUNG_YIN = 8
    OLD_YANG = 9

    @property
    def is_yang(self) -> bool:
        return self in {LineState.YOUNG_YANG, LineState.OLD_YANG}

    @property
    def is_yin(self) -> bool:
        return not self.is_yang

    @property
    def is_moving(self) -> bool:
        return self in {LineState.OLD_YIN, LineState.OLD_YANG}

    @property
    def changed(self) -> "LineState":
        if self == LineState.OLD_YIN:
            return LineState.YOUNG_YANG
        if self == LineState.OLD_YANG:
            return LineState.YOUNG_YIN
        return self


class TrigramId(str, Enum):
    QIAN = "qian"
    DUI = "dui"
    LI = "li"
    ZHEN = "zhen"
    XUN = "xun"
    KAN = "kan"
    GEN = "gen"
    KUN = "kun"


class Element(str, Enum):
    WOOD = "wood"
    FIRE = "fire"
    EARTH = "earth"
    METAL = "metal"
    WATER = "water"


class CalendarMode(str, Enum):
    CIVIL_SIMPLIFIED = "civil-simplified"
    CLASSICAL_LUNISOLAR = "classical-lunisolar"


class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"
    MARKDOWN = "markdown"
