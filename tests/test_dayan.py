from zhouyi.domain.enums import LineState
from zhouyi.domain.models import CastRequest
from zhouyi.infra.repository import DataRepository
from zhouyi.methods.dayan_zhu_xi import DayanZhuXiMethod, _she_remainder


def test_she_remainder() -> None:
    assert _she_remainder(1) == 1
    assert _she_remainder(2) == 2
    assert _she_remainder(3) == 3
    assert _she_remainder(4) == 4
    assert _she_remainder(5) == 1
    assert _she_remainder(8) == 4
    assert _she_remainder(12) == 4


def test_dayan_produces_valid_line_states_and_steps() -> None:
    repo = DataRepository()
    result = DayanZhuXiMethod(repo).cast(CastRequest(seed=7, show_steps=True))
    assert len(result.primary_hexagram.lines) == 6
    assert len(result.steps) == 6
    assert all(int(line) in {6, 7, 8, 9} for line in result.primary_hexagram.lines)
    assert all("steps" in step for step in result.steps)


def test_dayan_three_bian_remaining_in_standard_range() -> None:
    repo = DataRepository()
    result = DayanZhuXiMethod(repo).cast(CastRequest(seed=42, show_steps=True))
    for step in result.steps:
        last_remaining = step["steps"][-1]["remaining"]
        assert last_remaining in {24, 28, 32, 36}, f"remaining={last_remaining} not in standard range"


def test_dayan_yao_values_match_remaining() -> None:
    repo = DataRepository()
    result = DayanZhuXiMethod(repo).cast(CastRequest(seed=42, show_steps=True))
    for step in result.steps:
        yao = step["yao"]
        last_remaining = step["steps"][-1]["remaining"]
        assert yao == last_remaining // 4
        assert yao in {6, 7, 8, 9}


def test_dayan_produces_all_four_line_types() -> None:
    repo = DataRepository()
    method = DayanZhuXiMethod(repo)
    seen = set()
    for seed in range(200):
        result = method.cast(CastRequest(seed=seed))
        for line in result.primary_hexagram.lines:
            seen.add(int(line))
        if seen == {6, 7, 8, 9}:
            break
    assert seen == {6, 7, 8, 9}, f"only produced line types: {seen}"


def test_dayan_guayi_included_in_remainder() -> None:
    repo = DataRepository()
    result = DayanZhuXiMethod(repo).cast(CastRequest(seed=0, show_steps=True))
    for step in result.steps:
        for bian in step["steps"]:
            assert bian["guayi"] == 1
            remainder = bian["remainder"]
            left_rem = bian["left_rem"]
            right_rem = bian["right_rem"]
            assert remainder == 1 + left_rem + right_rem
