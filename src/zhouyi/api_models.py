from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class MethodInfoModel(BaseModel):
    id: str
    version: str
    description: str


class MethodFieldSchemaItemModel(BaseModel):
    name: str
    type: str
    help: str


class MethodsResponseModel(BaseModel):
    language: str
    items: list[MethodInfoModel]
    field_schema: dict[str, list[MethodFieldSchemaItemModel]]


class ProfileModel(BaseModel):
    profile_id: str
    name: str
    summary_style: str


class ProfilesResponseModel(BaseModel):
    language: str
    items: list[ProfileModel]


class TrigramModel(BaseModel):
    trigram_id: str
    name_zh: str
    name_en: str | None = None
    number: int
    element: str
    symbol: str
    lines: list[int]
    image: str
    image_en: str | None = None
    display_name: str | None = None
    display_image: str | None = None


class HexagramModel(BaseModel):
    lines: list[int]
    binary_lines: list[int]
    king_wen_index: int
    name_zh: str
    name_en: str | None = None
    unicode_symbol: str
    upper_trigram: str
    lower_trigram: str
    changing_lines: list[int]
    summary: str
    summary_en: str | None = None


class HexagramTextModel(BaseModel):
    index: int
    name_zh: str
    name_en: str | None = None
    display_name: str
    summary: str
    summary_zh: str
    summary_en: str | None = None
    judgment: str | None = None
    image: str | None = None
    tuan: str | None = None
    editorial: str | None = None


class TrigramPairModel(BaseModel):
    upper: TrigramModel
    lower: TrigramModel


class PrimaryTextsModel(BaseModel):
    hexagram: HexagramTextModel
    trigrams: TrigramPairModel


class LineTextModel(BaseModel):
    line: int
    text: str
    image: str | None = None
    source: str


class BodyUseAnalysisModel(BaseModel):
    moving_line: int
    moving_count: int
    body_side: str
    use_side: str
    body_side_label: str
    use_side_label: str
    body_trigram: TrigramModel
    use_trigram: TrigramModel
    relation: str
    relation_text: str


class MethodSpecificAnalysisModel(BaseModel):
    method_id: str
    method_version: str
    moving_line_rule: str
    selected_texts: list[str]
    mutual_hexagram: HexagramModel | None = None
    relating_hexagram: HexagramModel | None = None
    interpretation_profile: ProfileModel | None = None


class InterpretationModel(BaseModel):
    primary_texts: PrimaryTextsModel
    line_texts: list[LineTextModel]
    method_specific_analysis: MethodSpecificAnalysisModel
    body_use_analysis: BodyUseAnalysisModel
    timing_notes: list[str]
    plain_language_summary: str
    confidence_notes: list[str]
    provenance: dict[str, Any]


class CastResultModel(BaseModel):
    session_id: str
    question: str | None = None
    method_id: str
    method_version: str
    created_at: str
    timezone: str
    calendar_mode: str | None = None
    seed: int | None = None
    primary_hexagram: HexagramModel
    relating_hexagram: HexagramModel | None = None
    mutual_hexagram: HexagramModel | None = None
    changing_lines: list[int]
    steps: list[dict[str, Any]]
    raw_inputs: dict[str, Any]
    raw_derivation: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)


class HexagramResponseModel(BaseModel):
    language: str
    hexagram: HexagramModel
    primary_texts: PrimaryTextsModel


class CastMetaModel(BaseModel):
    method: str
    profile: str


class CastPayloadModel(BaseModel):
    question: str | None = None
    datetime_value: str | None = None
    raw_numbers: list[int] = Field(default_factory=list)
    raw_text: str | None = None
    seed: int | None = None
    show_steps: bool = False
    extras: dict[str, Any] = Field(default_factory=dict)
    language: str | None = None
    save_session: bool | None = None
    interpretation_profile: str = "balanced"


class CastResponseModel(BaseModel):
    language: str
    meta: CastMetaModel
    cast_result: CastResultModel
    interpretation: InterpretationModel


class SessionSummaryModel(BaseModel):
    session_id: str
    created_at: str
    method_id: str
    hexagram: str
    hexagram_index: int | None = None
    question: str | None = None


class SessionsResponseModel(BaseModel):
    language: str
    items: list[SessionSummaryModel]


class SessionDetailResponseModel(BaseModel):
    language: str
    cast_result: CastResultModel
    interpretation: InterpretationModel


class CaseModel(BaseModel):
    case_id: str
    title: str
    method: str
    input: dict[str, Any]
    expected: dict[str, Any]


class CasesResponseModel(BaseModel):
    language: str
    items: list[CaseModel]
