from __future__ import annotations


DEFAULT_LANGUAGE = "zh"


TEXTS = {
    "zh": {
        "no_moving": "无动爻，宜以本卦整体气象为主。",
        "focus_prefix": "可重点留意：",
        "no_relating": "无变卦参考。",
        "moving_line_text": "动爻在第{lines}爻，判断时宜把这些位置作为主轴。",
        "relating_text": "变卦见第{index}卦{name}，多提示后续走向与局面转折。",
        "summary_text": "本卦为第{index}卦{name}，{hexagram_editorial}。{line_text}{relating}{decision_rule}",
        "body_use_text": "体用关系上，{relation_text}",
        "modern_profile_suffix": "建议把此结果作为决策参考框架，而非单点结论。",
        "timing_note_1": "互卦可作过程参考，变卦可作后势参考。",
        "timing_note_2": "涉及现实决策时，宜结合问题背景而非只看单条文字。",
        "confidence_1": "程序输出为结构化辅助，不构成确定性结论。",
        "confidence_2": "不同历法与取数口径会影响梅花起卦结果。",
        "moving_rule_0": "当前没有动爻，重点不在局部变化，而在整体格局是否稳固、顺畅、可持续。宜读本卦卦辞。",
        "moving_rule_1": "一爻发动，主旨最集中，读该动爻爻辞，再以本卦卦辞为背景。",
        "moving_rule_2": "两爻同动，读本卦两动爻爻辞，以上爻为主。",
        "moving_rule_3": "三爻发动，读本卦卦辞，参看变卦卦辞，本卦为当前处境，变卦为下一阶段。",
        "moving_rule_4": "四爻发动，读变卦两不动爻爻辞，以下爻为主。",
        "moving_rule_5": "五爻发动，读变卦唯一不动爻爻辞。",
        "moving_rule_6": "六爻尽动，乾坤看用辞，余卦读变卦卦辞。整局翻面，重在改势之后的新秩序。",
    },
    "en": {
        "no_moving": "No changing lines; read the overall structure of the primary hexagram first.",
        "focus_prefix": "Current focus: ",
        "no_relating": "No relating hexagram reference.",
        "moving_line_text": "Changing lines appear at line {lines}; these positions deserve the closest attention.",
        "relating_text": "The relating hexagram is #{index} {name}, which can be read as the next-stage tendency.",
        "summary_text": "The primary hexagram is #{index} {name}. {hexagram_editorial} {line_text}{relating}{decision_rule}",
        "body_use_text": "Body / Function relation: {relation_text}",
        "modern_profile_suffix": "Use this result as a decision framework rather than as a single-point verdict.",
        "timing_note_1": "The mutual hexagram suggests the internal process, while the relating hexagram suggests the later trend.",
        "timing_note_2": "For real decisions, always combine the reading with the actual context instead of relying on a single phrase.",
        "confidence_1": "This output is structured guidance rather than a deterministic conclusion.",
        "confidence_2": "Different calendar conventions and counting rules can change Meihua casting results.",
        "moving_rule_0": "When there are no changing lines, read the judgment of the primary hexagram as a whole.",
        "moving_rule_1": "With one changing line, read that line's text first, then the primary hexagram judgment for context.",
        "moving_rule_2": "With two changing lines, read both moving lines' texts, with the upper line as primary.",
        "moving_rule_3": "With three changing lines, read the primary hexagram judgment and reference the relating hexagram judgment.",
        "moving_rule_4": "With four changing lines, read the two unmoving lines' texts in the relating hexagram, with the lower line as primary.",
        "moving_rule_5": "With five changing lines, read the single unmoving line's text in the relating hexagram.",
        "moving_rule_6": "With six changing lines, for Qian/Kun read the 'Use' text; for others read the relating hexagram judgment.",
        "same": "Body and function share the same phase; the matter tends to advance through alignment and stability.",
        "body_generates_use": "The body generates the function; the self tends to spend more energy to support the process.",
        "use_generates_body": "The function generates the body; external conditions nourish and support the self.",
        "body_controls_use": "The body controls the function; the self can take command, though pressure and hard choices remain.",
        "use_controls_body": "The function controls the body; outside pressure is stronger, so caution and restraint are advised.",
    },
}


def tx(language: str, key: str) -> str:
    return TEXTS.get(language, TEXTS[DEFAULT_LANGUAGE]).get(key, key)
