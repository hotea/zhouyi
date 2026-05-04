from __future__ import annotations

from zhouyi.domain.models import CastResult, Interpretation
from zhouyi.infra.i18n import tx
from zhouyi.infra.repository import DataRepository
from zhouyi.interpret.meihua_body_use import analyze_body_use
from zhouyi.interpret.profiles import apply_profile
from zhouyi.interpret.summarizer import summarize
from zhouyi.interpret.zhouyi_text import changing_line_texts, primary_texts


class InterpretationPipeline:
    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def interpret(
        self, result: CastResult, profile_id: str = "balanced", language: str = "zh"
    ) -> Interpretation:
        body_use = analyze_body_use(result, self.repository, language)
        line_texts = changing_line_texts(
            self.repository,
            result.primary_hexagram,
            result.changing_lines,
            language,
            relating_hexagram=result.relating_hexagram,
        )
        primary = primary_texts(self.repository, result.primary_hexagram, language)
        moving_count = len(result.changing_lines)
        decision_rule = tx(language, f"moving_rule_{moving_count}")
        selected_texts = [item["text"] for item in line_texts]
        if not selected_texts and primary["hexagram"].get("judgment"):
            selected_texts = [str(primary["hexagram"]["judgment"])]
        interpretation = Interpretation(
            primary_texts=primary,
            line_texts=line_texts,
            method_specific_analysis={
                "method_id": result.method_id,
                "method_version": result.method_version,
                "moving_line_rule": decision_rule,
                "selected_texts": selected_texts,
                "mutual_hexagram": result.mutual_hexagram.to_dict()
                if result.mutual_hexagram
                else None,
                "relating_hexagram": result.relating_hexagram.to_dict()
                if result.relating_hexagram
                else None,
            },
            body_use_analysis=body_use,
            timing_notes=[
                tx(language, "timing_note_1"),
                tx(language, "timing_note_2"),
                decision_rule,
            ],
            plain_language_summary=summarize(
                result, body_use, decision_rule, selected_texts, language
            ),
            confidence_notes=[
                tx(language, "confidence_1"),
                tx(language, "confidence_2"),
            ],
            provenance={
                "method_id": result.method_id,
                "method_version": result.method_version,
                "language": language,
            },
        )
        interpretation = apply_profile(
            interpretation, self.repository.get_interpretation_profile(profile_id)
        )
        profile_text = next(
            (
                item
                for item in self.repository.list_interpretation_profiles_text(language)
                if item["profile_id"] == profile_id
            ),
            None,
        )
        if profile_text is not None:
            interpretation.method_specific_analysis["interpretation_profile"] = profile_text
        return interpretation
