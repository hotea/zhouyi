from zhouyi.infra.repository import DataRepository


def test_lookup_hexagram_49_is_ge() -> None:
    repo = DataRepository()
    hexagram = repo.get_hexagram_by_index(49)
    assert hexagram.name_zh == "革"
    assert hexagram.upper_trigram.value == "dui"
    assert hexagram.lower_trigram.value == "li"


def test_build_hexagram_from_lines_respects_bottom_up_order() -> None:
    repo = DataRepository()
    hexagram = repo.get_hexagram_by_index(63)
    rebuilt = repo.build_hexagram_from_lines(hexagram.lines)
    assert rebuilt.king_wen_index == 63


def test_primary_texts_and_specific_line_texts_are_available() -> None:
    repo = DataRepository()
    primary = repo.get_primary_texts(repo.get_hexagram_by_index(49))
    lines = repo.get_line_texts(49, (1, 6))
    assert primary["hexagram"]["judgment"] == "革：己日乃孚。元亨利贞，悔亡。"
    assert primary["hexagram"]["tuan"] is not None
    assert "旧秩序已经难以继续" in primary["hexagram"]["editorial"]
    assert lines[0]["source"] == "specific"
    assert lines[1]["text"] == "上六：君子豹变，小人革面；征凶，居贞吉。"
    assert lines[0]["image"] is not None


def test_primary_texts_localize_hexagram_name_in_english() -> None:
    repo = DataRepository()
    primary = repo.get_primary_texts(repo.get_hexagram_by_index(49), "en")
    assert primary["hexagram"]["display_name"] == "Skinning"
    assert primary["trigrams"]["upper"]["display_name"] == "Dui"


def test_primary_texts_have_expanded_english_classic_coverage() -> None:
    repo = DataRepository()
    primary = repo.get_primary_texts(repo.get_hexagram_by_index(11), "en")
    assert primary["hexagram"]["judgment"].startswith("Tai:")
    assert primary["hexagram"]["image"] is not None


def test_english_line_texts_use_specific_translations_when_available() -> None:
    repo = DataRepository()
    lines = repo.get_line_texts(50, (2,), "en")
    assert lines[0]["source"] == "translated"
    assert lines[0]["text"].startswith("There is substance in the cauldron")
    assert lines[0]["image"] is not None


def test_english_line_texts_fallback_to_generic_when_untranslated() -> None:
    repo = DataRepository()
    lines = repo.get_line_texts(30, (6,), "en")
    assert lines[0]["source"] == "generic"
    assert lines[0]["image"] is None


def test_primary_texts_have_third_batch_richer_chinese_editorial() -> None:
    repo = DataRepository()
    primary = repo.get_primary_texts(repo.get_hexagram_by_index(13), "zh")
    assert "公开协作" in primary["hexagram"]["editorial"]
