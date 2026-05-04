from __future__ import annotations

from zhouyi.infra.repository import DataRepository
from zhouyi.methods.coin import CoinMethod
from zhouyi.methods.dayan_zhu_xi import DayanZhuXiMethod
from zhouyi.methods.meihua_number import MeihuaNumberMethod
from zhouyi.methods.meihua_object import MeihuaObjectMethod
from zhouyi.methods.meihua_person import MeihuaPersonMethod
from zhouyi.methods.meihua_sound import MeihuaSoundMethod
from zhouyi.methods.meihua_static import MeihuaStaticMethod
from zhouyi.methods.meihua_time import MeihuaTimeMethod
from zhouyi.methods.meihua_word import MeihuaWordMethod


def build_method_registry(repository: DataRepository) -> dict[str, object]:
    return {
        "dayan": DayanZhuXiMethod(repository),
        "coin": CoinMethod(repository),
        "meihua-time": MeihuaTimeMethod(repository),
        "meihua-number": MeihuaNumberMethod(repository),
        "meihua-sound": MeihuaSoundMethod(repository),
        "meihua-word": MeihuaWordMethod(repository),
        "meihua-object": MeihuaObjectMethod(repository),
        "meihua-person": MeihuaPersonMethod(repository),
        "meihua-static": MeihuaStaticMethod(repository),
    }
