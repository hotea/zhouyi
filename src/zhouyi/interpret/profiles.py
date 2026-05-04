from __future__ import annotations

from zhouyi.domain.models import Interpretation, InterpretationProfile
from zhouyi.infra.i18n import tx


def apply_profile(
    interpretation: Interpretation, profile: InterpretationProfile
) -> Interpretation:
    if profile.profile_id == "classic":
        interpretation.plain_language_summary = "\n".join(
            part
            for part in [
                str(
                    interpretation.primary_texts.get("hexagram", {}).get("judgment")
                    or ""
                ),
                str(
                    interpretation.primary_texts.get("hexagram", {}).get("image") or ""
                ),
                *(item["text"] for item in interpretation.line_texts),
            ]
            if part
        )
    elif profile.profile_id == "modern":
        language = str(interpretation.provenance.get("language", "zh"))
        interpretation.plain_language_summary += tx(language, "modern_profile_suffix")
    interpretation.provenance["interpretation_profile"] = profile.profile_id
    return interpretation
