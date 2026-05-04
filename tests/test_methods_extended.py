from zhouyi.domain.models import CastRequest
from zhouyi.infra.repository import DataRepository
from zhouyi.methods.coin import CoinMethod
from zhouyi.methods.meihua_object import MeihuaObjectMethod
from zhouyi.methods.meihua_person import MeihuaPersonMethod
from zhouyi.methods.meihua_static import MeihuaStaticMethod


def test_coin_method_generates_six_lines() -> None:
    result = CoinMethod(DataRepository()).cast(CastRequest(seed=3))
    assert len(result.primary_hexagram.lines) == 6
    assert len(result.steps) == 6


def test_meihua_object_method() -> None:
    result = MeihuaObjectMethod(DataRepository()).cast(
        CastRequest(extras={"object_type": "flower", "count": 3, "hour": "you"})
    )
    assert result.primary_hexagram.king_wen_index > 0


def test_meihua_person_method() -> None:
    result = MeihuaPersonMethod(DataRepository()).cast(
        CastRequest(extras={"person_type": "merchant", "count": 2, "hour": "zi"})
    )
    assert result.primary_hexagram.king_wen_index > 0


def test_meihua_static_method() -> None:
    result = MeihuaStaticMethod(DataRepository()).cast(
        CastRequest(extras={"item_type": "stone", "count": 4, "hour": "mao"})
    )
    assert result.primary_hexagram.king_wen_index > 0
