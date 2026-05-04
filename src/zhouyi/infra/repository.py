from __future__ import annotations

import json
import threading
from functools import cached_property
from importlib.resources import files

from zhouyi.domain.enums import Element, LineState, TrigramId
from zhouyi.domain.models import Hexagram, InterpretationProfile, TrigramInfo
from zhouyi.domain.services import trigram_from_lines


LINE_TEXTS = {
    1: "初爻之始，主事情起端与动机。",
    2: "二爻近内，主条件渐成与位置安稳。",
    3: "三爻多变，主过渡、风险与转折。",
    4: "四爻近外，主环境互动与机会显露。",
    5: "五爻居中，主核心决策与主导力量。",
    6: "上爻之终，主局势收束、过极或反转。",
}


LINE_TEXTS_EN = {
    1: "The first line marks the beginning of the matter, including its motive and initial impulse.",
    2: "The second line sits near the inner center, showing conditions taking shape and stabilizing.",
    3: "The third line is volatile, often marking transition, risk, and a turning point.",
    4: "The fourth line meets the outer field, highlighting interaction with circumstances and emerging openings.",
    5: "The fifth line occupies the center of authority, pointing to the core decision or guiding force.",
    6: "The top line marks closure, excess, exhaustion, or reversal at the end of the process.",
}


SUMMARY_BY_INDEX = {
    1: "元亨利贞，宜主动、刚健、自我承担。",
    2: "厚德载物，宜顺势承接、稳步推进。",
    3: "刚柔始交而难生，宜屯聚蓄力、待机而动。",
    4: "山下出泉，宜启蒙教化、循序渐进。",
    5: "云上于天，宜待时而动、以逸待劳。",
    6: "天与水违行，宜慎言避讼、以和为贵。",
    7: "地中有水，宜行险而顺、以众服人。",
    8: "地上有水，宜亲比求辅、择善而交。",
    9: "风行天上，宜小有蓄积、蓄力待发。",
    10: "上天下泽，宜循礼而行、谨守分寸。",
    11: "上下交通，主通达与配合。",
    12: "天地不交，主闭塞与停滞。",
    13: "天与火，宜同人于野、光明正大。",
    14: "火在天上，宜遏恶扬善、顺天休命。",
    15: "地中有山，宜裒多益寡、称物平施。",
    16: "雷出地奋，宜顺以动、豫防未然。",
    17: "泽中有雷，宜随时而动、顺势而为。",
    18: "山下有风，宜振蛊起衰、革新除弊。",
    19: "泽上有地，宜教思无穷、容保民无疆。",
    20: "风行地上，宜省方观民、设教施教。",
    21: "雷电噬嗑，宜明罚敕法、以正纲纪。",
    22: "山下有火，宜文明以止、饰外扬中。",
    23: "山附于地，宜厚下安宅、防微杜渐。",
    24: "雷在地中，宜闭关静养、反身修德。",
    25: "天下雷行，宜无妄而动、守正得福。",
    26: "天在山中，宜以懿文德、蓄力待时。",
    27: "山下有雷，宜慎言语、节饮食以养正。",
    28: "泽灭木，宜独立不惧、遁世无闷。",
    29: "水洊至，宜常德行、习教事以避险。",
    30: "明两作，宜大人以继明照于四方。",
    31: "山上有泽，宜以虚受人、感而遂通。",
    32: "雷风恒，宜久于其道、天下化成。",
    33: "天下有山，宜远小人、不恶而严。",
    34: "雷在天上，宜壮勿妄动、非礼弗履。",
    35: "明出地上，宜自昭明德、顺而上行。",
    36: "明入地中，宜莅众用晦、以明内治。",
    37: "风自火出，宜正家而天下定。",
    38: "上火下泽，宜同而异、以柔遇刚。",
    39: "山上有水，宜反身修德、以济蹇难。",
    40: "雷雨作，宜赦过宥罪、解险释难。",
    41: "山下有泽，宜惩忿窒欲、损下益上。",
    42: "风雷益，宜见善则迁、有过则改。",
    43: "泽上于天，宜施禄及下、居德则忌。",
    44: "天下有风，宜施命诰四方、遇刚则慎。",
    45: "泽上于地，宜除戎器、戒不虞以聚。",
    46: "地中生木，宜顺而积小、以高大升。",
    47: "泽无水，宜致命遂志、处困而不失。",
    48: "木上有水，宜劳民劝相、井养而不穷。",
    49: "革故鼎新，主变革、去旧与调整秩序。",
    50: "木上有火，宜正位凝命、鼎新而立。",
    51: "洊雷震，宜恐惧修省、以震远迩。",
    52: "兼山艮，宜思不出其位、止于其所。",
    53: "山上有木，宜居贤德善俗、渐进以正。",
    54: "泽上有雷，宜永终知敝、归妹以时。",
    55: "雷电皆至，宜折狱致刑、明以动丰。",
    56: "山上有火，宜明慎用刑、不留狱以旅。",
    57: "随风巽，宜申命行事、重巽以申。",
    58: "丽泽兑，宜朋友讲习、相悦以成。",
    59: "风行水上，宜先王享于帝立庙、涣以聚之。",
    60: "泽上有水，宜制数度、议德行以节。",
    61: "泽上有风，宜议狱缓死、中孚以信。",
    62: "山上有雷，宜过乎恭、丧过乎哀、用过乎俭。",
    63: "事已成形，宜守成、慎终。",
    64: "未至成局，宜准备、校正与收敛。",
}


class DataRepository:
    _lock = threading.Lock()

    def _english_hexagram_summary(self, index: int, name_en: str | None) -> str:
        translated = self.translations_en.get("hexagram_summaries", {}).get(str(index))
        if translated:
            return translated
        display_name = name_en or f"Hexagram {index}"
        return (
            f"{display_name} suggests reading the situation through the changing lines "
            "together with the upper and lower trigrams."
        )

    @cached_property
    def zhouyi_texts(self) -> dict[str, object]:
        return json.loads(
            (files("zhouyi.data") / "zhouyi_texts.json").read_text(encoding="utf-8")
        )

    @cached_property
    def zhouyi_full_texts(self) -> dict[str, object]:
        return json.loads(
            (files("zhouyi.data") / "zhouyi_full_texts.json").read_text(
                encoding="utf-8"
            )
        )

    @cached_property
    def translations_en(self) -> dict[str, object]:
        return json.loads(
            (files("zhouyi.data") / "translations_en.json").read_text(encoding="utf-8")
        )

    @cached_property
    def trigram_records(self) -> dict[TrigramId, TrigramInfo]:
        raw = json.loads(
            (files("zhouyi.data") / "trigrams.json").read_text(encoding="utf-8")
        )
        result: dict[TrigramId, TrigramInfo] = {}
        for item in raw:
            trigram_id = TrigramId(item["id"])
            trigram_en = self.translations_en.get("trigrams", {}).get(item["id"], {})
            result[trigram_id] = TrigramInfo(
                trigram_id=trigram_id,
                name_zh=item["name_zh"],
                name_en=trigram_en.get("name"),
                number=item["number"],
                element=Element(item["element"]),
                symbol=item["symbol"],
                lines=tuple(item["lines"]),
                image=item["image"],
                image_en=trigram_en.get("image"),
            )
        return result

    @cached_property
    def hexagram_records(self) -> list[dict[str, object]]:
        return json.loads(
            (files("zhouyi.data") / "hexagrams.json").read_text(encoding="utf-8")
        )

    @cached_property
    def meihua_rules(self) -> dict[str, str]:
        return json.loads(
            (files("zhouyi.data") / "meihua_rules.json").read_text(encoding="utf-8")
        )

    @cached_property
    def interpretation_profiles(self) -> dict[str, InterpretationProfile]:
        raw = json.loads(
            (files("zhouyi.data") / "interpreter_profiles.json").read_text(
                encoding="utf-8"
            )
        )
        return {
            key: InterpretationProfile(
                profile_id=value["profile_id"],
                name=value["name"],
                summary_style=value["summary_style"],
            )
            for key, value in raw.items()
        }

    @cached_property
    def meihua_cases(self) -> list[dict[str, object]]:
        return json.loads(
            (files("zhouyi.data") / "cases_meihua.json").read_text(encoding="utf-8")
        )

    @cached_property
    def hexagram_lookup(self) -> dict[tuple[TrigramId, TrigramId], dict[str, object]]:
        with self._lock:
            if hasattr(self, "_hexagram_lookup_cache"):
                return self._hexagram_lookup_cache
            result: dict[tuple[TrigramId, TrigramId], dict[str, object]] = {}
            for item in self.hexagram_records:
                key = (TrigramId(item["upper"]), TrigramId(item["lower"]))
                if key in result:
                    raise ValueError(f"duplicate hexagram mapping for {key}")
                result[key] = item
            if len(result) != 64:
                raise ValueError(
                    f"hexagram mapping incomplete: expected 64, got {len(result)}"
                )
            self._hexagram_lookup_cache = result
            return result

    def list_methods_text(self, language: str = "zh") -> list[dict[str, str]]:
        result = [
            {
                "id": "dayan",
                "version": "dayan_zhu_xi_v1",
                "description": "大衍筮法，三变成一爻，可回放每步归奇。alias: dayan",
            },
            {
                "id": "meihua-time",
                "version": "meihua_time_v1",
                "description": "年月日时起卦，支持 civil 与 lunar 两种历法模式。alias: meihua time",
            },
            {
                "id": "meihua-number",
                "version": "meihua_number_v1",
                "description": "数字起卦，支持两数法与三数法。alias: meihua number",
            },
            {
                "id": "meihua-sound",
                "version": "meihua_sound_v1",
                "description": "声音或次数起卦，加时成下卦。alias: meihua sound",
            },
            {
                "id": "meihua-word",
                "version": "meihua_word_v1",
                "description": "字占，按字数拆分上下卦并取动爻。alias: meihua word",
            },
            {
                "id": "coin",
                "version": "coin_three_v1",
                "description": "三钱法，六次掷钱生成六爻。alias: coin",
            },
            {
                "id": "meihua-object",
                "version": "meihua_object_v1",
                "description": "物数占，根据物类与数量取象成卦。alias: meihua object",
            },
            {
                "id": "meihua-person",
                "version": "meihua_person_v1",
                "description": "为人占，根据人物类别与数量起卦。alias: meihua person",
            },
            {
                "id": "meihua-static",
                "version": "meihua_static_v1",
                "description": "静物占，根据静物类别与数量起卦。alias: meihua static",
            },
        ]
        if language == "en":
            descriptions = self.translations_en["method_descriptions"]
            return [
                {
                    **item,
                    "description": descriptions.get(item["id"], item["description"]),
                }
                for item in result
            ]
        return result

    def method_field_schema(
        self, language: str = "zh"
    ) -> dict[str, list[dict[str, str]]]:
        en_help = self.translations_en.get("field_help", {})
        zh_help = {
            "numbers": "用空格分隔的数字，例如 3 5 或 3 5 2。",
            "text": "用于字占或声音占的文本。",
            "seed": "用于复现随机起卦的可选种子。",
            "hour": "地支时辰，例如 zi、mao、you、hai。",
            "count": "声音、物数、人物、静物法使用的观测数量。",
            "object_type": "观测到的物体类型，如 flower、tree、stone。",
            "person_type": "观测到的人物类型，如 merchant、scholar、woman。",
            "item_type": "观测到的静物类型，如 stone、lamp、table。",
        }
        h = en_help if language == "en" else zh_help
        return {
            "dayan": [{"name": "seed", "type": "number", "help": h["seed"]}],
            "coin": [{"name": "seed", "type": "number", "help": h["seed"]}],
            "meihua-number": [
                {"name": "numbers", "type": "text", "help": h["numbers"]}
            ],
            "meihua-word": [{"name": "text", "type": "text", "help": h["text"]}],
            "meihua-sound": [
                {"name": "text", "type": "text", "help": h["text"]},
                {"name": "count", "type": "number", "help": h["count"]},
                {"name": "hour", "type": "text", "help": h["hour"]},
            ],
            "meihua-object": [
                {"name": "object_type", "type": "text", "help": h["object_type"]},
                {"name": "count", "type": "number", "help": h["count"]},
                {"name": "hour", "type": "text", "help": h["hour"]},
            ],
            "meihua-person": [
                {"name": "person_type", "type": "text", "help": h["person_type"]},
                {"name": "count", "type": "number", "help": h["count"]},
                {"name": "hour", "type": "text", "help": h["hour"]},
            ],
            "meihua-static": [
                {"name": "item_type", "type": "text", "help": h["item_type"]},
                {"name": "count", "type": "number", "help": h["count"]},
                {"name": "hour", "type": "text", "help": h["hour"]},
            ],
            "meihua-time": [{"name": "hour", "type": "text", "help": h["hour"]}],
        }

    def get_trigram(self, trigram_id: TrigramId) -> TrigramInfo:
        return self.trigram_records[trigram_id]

    def resolve_trigram_id(self, value: str) -> TrigramId:
        normalized = value.strip().lower()
        aliases = {
            "乾": TrigramId.QIAN,
            "qian": TrigramId.QIAN,
            "1": TrigramId.QIAN,
            "兑": TrigramId.DUI,
            "dui": TrigramId.DUI,
            "2": TrigramId.DUI,
            "离": TrigramId.LI,
            "li": TrigramId.LI,
            "3": TrigramId.LI,
            "震": TrigramId.ZHEN,
            "zhen": TrigramId.ZHEN,
            "4": TrigramId.ZHEN,
            "巽": TrigramId.XUN,
            "xun": TrigramId.XUN,
            "5": TrigramId.XUN,
            "坎": TrigramId.KAN,
            "kan": TrigramId.KAN,
            "6": TrigramId.KAN,
            "艮": TrigramId.GEN,
            "gen": TrigramId.GEN,
            "7": TrigramId.GEN,
            "坤": TrigramId.KUN,
            "kun": TrigramId.KUN,
            "8": TrigramId.KUN,
        }
        try:
            return aliases[normalized]
        except KeyError as exc:
            raise ValueError(f"unsupported trigram: {value}") from exc

    def list_trigrams(self) -> list[TrigramInfo]:
        return list(self.trigram_records.values())

    def list_interpretation_profiles(self) -> list[InterpretationProfile]:
        return list(self.interpretation_profiles.values())

    def list_interpretation_profiles_text(
        self, language: str = "zh"
    ) -> list[dict[str, object]]:
        items = [profile.to_dict() for profile in self.list_interpretation_profiles()]
        if language != "en":
            return items
        translations = self.translations_en.get("profiles", {})
        return [
            {
                **item,
                "name": translations.get(item["profile_id"], {}).get(
                    "name", item["name"]
                ),
                "summary_style": translations.get(item["profile_id"], {}).get(
                    "summary_style", item["summary_style"]
                ),
            }
            for item in items
        ]

    def get_interpretation_profile(self, profile_id: str) -> InterpretationProfile:
        try:
            return self.interpretation_profiles[profile_id]
        except KeyError as exc:
            raise ValueError(
                f"unsupported interpretation profile: {profile_id}"
            ) from exc

    def list_meihua_cases(self) -> list[dict[str, object]]:
        return self.meihua_cases

    def list_meihua_cases_text(self, language: str = "zh") -> list[dict[str, object]]:
        if language != "en":
            return self.meihua_cases
        titles = self.translations_en.get("case_titles", {})
        return [
            {**item, "title": titles.get(str(item["case_id"]), item["title"])}
            for item in self.meihua_cases
        ]

    def moving_line_rule(self, moving_count: int) -> str:
        return self.zhouyi_texts["moving_line_rules"].get(
            str(moving_count), "动爻规则未定义。"
        )

    def get_hexagram_text_record(self, index: int) -> dict[str, object]:
        full = self.zhouyi_full_texts.get("hexagrams", {}).get(str(index), {})
        partial = self.zhouyi_texts.get("hexagrams", {}).get(str(index), {})
        return {**full, **partial}

    def build_hexagram_from_lines(self, lines: tuple[LineState, ...]) -> Hexagram:
        if len(lines) != 6:
            raise ValueError("hexagram must have six lines")
        binary = tuple(1 if line.is_yang else 0 for line in lines)
        lower = trigram_from_lines(binary[:3])
        upper = trigram_from_lines(binary[3:])
        item = self.hexagram_lookup[(upper, lower)]
        symbol = self.get_trigram(upper).symbol + self.get_trigram(lower).symbol
        index = int(item["king_wen_index"])
        name_en = self.translations_en.get("hexagram_names", {}).get(str(index))
        return Hexagram(
            lines=lines,
            king_wen_index=index,
            name_zh=str(item["name_zh"]),
            name_en=name_en,
            unicode_symbol=symbol,
            upper_trigram=upper,
            lower_trigram=lower,
            summary=SUMMARY_BY_INDEX.get(
                index,
                f"{item['name_zh']}卦，宜结合动爻与上下卦判断。",
            ),
            summary_en=self._english_hexagram_summary(index, name_en),
        )

    def get_hexagram_by_index(self, index: int) -> Hexagram:
        for item in self.hexagram_records:
            if int(item["king_wen_index"]) == index:
                lower = self.get_trigram(TrigramId(item["lower"]))
                upper = self.get_trigram(TrigramId(item["upper"]))
                name_en = self.translations_en.get("hexagram_names", {}).get(str(index))
                lines = tuple(
                    [
                        LineState.YOUNG_YANG if bit else LineState.YOUNG_YIN
                        for bit in (lower.lines + upper.lines)
                    ]
                )
                return Hexagram(
                    lines=lines,
                    king_wen_index=index,
                    name_zh=str(item["name_zh"]),
                    name_en=name_en,
                    unicode_symbol=upper.symbol + lower.symbol,
                    upper_trigram=upper.trigram_id,
                    lower_trigram=lower.trigram_id,
                    summary=SUMMARY_BY_INDEX.get(
                        index, f"{item['name_zh']}卦，宜结合动爻与上下卦判断。"
                    ),
                    summary_en=self._english_hexagram_summary(index, name_en),
                )
        raise KeyError(f"hexagram {index} not found")

    def get_primary_texts(
        self, hexagram: Hexagram, language: str = "zh"
    ) -> dict[str, object]:
        text_record = self.get_hexagram_text_record(hexagram.king_wen_index)
        if language == "en":
            english_record = self.translations_en.get("classic_texts", {}).get(
                str(hexagram.king_wen_index), {}
            )
            text_record = {
                "judgment": english_record.get("judgment"),
                "image": english_record.get("image"),
                "tuan": english_record.get("tuan"),
                "editorial": english_record.get("editorial")
                or hexagram.display_summary(language),
            }
        upper = self.get_trigram(hexagram.upper_trigram)
        lower = self.get_trigram(hexagram.lower_trigram)
        return {
            "hexagram": {
                "index": hexagram.king_wen_index,
                "name_zh": hexagram.name_zh,
                "name_en": hexagram.name_en,
                "display_name": hexagram.display_name(language),
                "summary": hexagram.display_summary(language),
                "summary_zh": hexagram.summary,
                "summary_en": hexagram.summary_en,
                "judgment": text_record.get("judgment"),
                "image": text_record.get("image"),
                "tuan": text_record.get("tuan"),
                "editorial": text_record.get(
                    "editorial", hexagram.display_summary(language)
                ),
            },
            "trigrams": {
                "upper": {
                    **upper.to_dict(),
                    "display_name": upper.display_name(language),
                    "display_image": upper.display_image(language),
                },
                "lower": {
                    **lower.to_dict(),
                    "display_name": lower.display_name(language),
                    "display_image": lower.display_image(language),
                },
            },
        }

    def get_line_texts(
        self, hexagram_index: int, changing_lines: tuple[int, ...], language: str = "zh"
    ) -> list[dict[str, object]]:
        specific = self.zhouyi_texts.get("line_texts", {}).get(str(hexagram_index), {})
        full_record = self.zhouyi_full_texts.get("hexagrams", {}).get(
            str(hexagram_index), {}
        )
        full_lines = full_record.get("line_texts", [])
        full_images = full_record.get("line_images", [])
        translated = self.translations_en.get("classic_texts", {}).get(
            str(hexagram_index), {}
        )
        translated_lines = translated.get("line_texts", [])
        translated_images = translated.get("line_images", [])
        return [
            {
                "line": line,
                "text": translated_lines[line - 1]
                if language == "en" and line - 1 < len(translated_lines)
                else (
                    LINE_TEXTS_EN[line]
                    if language == "en"
                    else specific.get(
                        str(line),
                        full_lines[line - 1]
                        if line - 1 < len(full_lines)
                        else LINE_TEXTS[line],
                    )
                ),
                "image": translated_images[line - 1]
                if language == "en" and line - 1 < len(translated_images)
                else (
                    None
                    if language == "en"
                    else (
                        full_images[line - 1] if line - 1 < len(full_images) else None
                    )
                ),
                "source": "specific"
                if language != "en" and str(line) in specific
                else (
                    "translated"
                    if language == "en" and line - 1 < len(translated_lines)
                    else (
                        "generic"
                        if language == "en"
                        else ("full" if line - 1 < len(full_lines) else "generic")
                    )
                ),
            }
            for line in changing_lines
        ]

    def chinese_editorial(self, hexagram_index: int) -> str:
        record = self.zhouyi_texts.get("hexagrams", {}).get(str(hexagram_index), {})
        return str(
            record.get(
                "editorial",
                SUMMARY_BY_INDEX.get(
                    hexagram_index,
                    f"第{hexagram_index}卦宜结合动爻、上下卦与时位来判断。",
                ),
            )
        )

    def get_yong_text(
        self, hexagram_index: int, language: str = "zh"
    ) -> dict[str, object]:
        if hexagram_index == 1:
            text = "用九：见群龙无首，吉。" if language == "zh" else "Use of Nine: Seeing a flock of dragons without a head, good fortune."
            image = "用九，天德不可为首也。" if language == "zh" else "Use of Nine: The virtue of Heaven cannot take the lead."
        elif hexagram_index == 2:
            text = "用六：利永贞。" if language == "zh" else "Use of Six: Favorable for long constancy."
            image = "用六永贞，以大终也。" if language == "zh" else "Use of Six: Long constancy, to bring about the great end."
        else:
            text = ""
            image = None
        return {
            "line": "yong",
            "text": text,
            "image": image,
            "source": "yong",
        }
