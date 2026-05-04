# 周易术语中英对照表

本表用于统一项目中的 CLI、API、Web、文档与代码命名。

原则：

- 基础《易经》术语优先采用较稳定的英文译法
- 流派名与强传统专名优先采用 `拼音 + 英文解释`
- 代码字段尽量使用稳定英文；方法 ID 可以保留拼音

## 核心经典术语

| 中文 | 推荐英文 | 常见变体 | 建议用法 |
|---|---|---|---|
| 易经 / 周易 | I Ching / Yijing / Book of Changes | Zhou Yi | 文档首屏可写 `Yijing (I Ching)` |
| 八卦 | Eight Trigrams | trigrams | 代码与 UI 里用 `trigram` / `trigrams` |
| 六十四卦 | Sixty-Four Hexagrams | hexagrams | 文档中可写 `64 hexagrams` |
| 卦 | hexagram | gua | 不建议核心字段使用 `gua` |
| 爻 | line | yao | 核心模型统一用 `line` |
| 动爻 | changing line | moving line | 推荐 `changing line` |
| 本卦 | primary hexagram | original hexagram | 推荐 `primary_hexagram` |
| 变卦 / 之卦 | relating hexagram | transformed hexagram | 推荐 `relating_hexagram` |
| 互卦 | mutual hexagram | nuclear hexagram | 推荐 `mutual_hexagram` |
| 上卦 | upper trigram | upper gua | 推荐 `upper_trigram` |
| 下卦 | lower trigram | lower gua | 推荐 `lower_trigram` |
| 卦辞 | Judgment | hexagram statement | UI 首次出现可写 `Judgment (卦辞)` |
| 爻辞 | line statement | line text | 推荐 `line_text` 或 `line statement` |
| 彖传 | Commentary on the Decision | Tuan Commentary | 推荐 `tuan commentary` |
| 象传 | Commentary on the Image | Xiang Commentary | 推荐 `image commentary` |
| 大象 | Great Image | Image | 推荐 `image` |
| 小象 | Lesser Image | line image commentary | 推荐 `line image` |
| 系辞 | Great Treatise | Appended Statements | 两者都常见 |
| 文言 | Commentary on the Words | Wenyan | 文档首次出现可双写 |
| 说卦 | Discussion of the Trigrams | Shuogua | 文档首次出现可双写 |
| 序卦 | Sequence of the Hexagrams | Xugua | 文档首次出现可双写 |
| 杂卦 | Miscellaneous Hexagrams | Zagua | 文档首次出现可双写 |

## 起卦与解释术语

| 中文 | 推荐英文 | 常见变体 | 建议用法 |
|---|---|---|---|
| 起卦 | cast a hexagram | divination casting | CLI 用 `cast` |
| 解卦 | interpret a hexagram | divination reading | CLI 用 `interpret` |
| 占问 | divination query | question | UI 中优先用 `question` |
| 会话 | session | cast session | 推荐 `session` |
| 推导过程 | derivation steps | casting steps | 推荐 `steps` |
| 回放 | replay | explain | CLI 已使用 `explain` |
| 导出 | export | serialize | CLI 用 `export` |
| 经典文本 | canonical text | classic text | 推荐 `classic texts` |
| 白话摘要 | plain-language summary | plain summary | 推荐 `plain_language_summary` |
| 体用 | body and function | host and guest | UI 可写 `Body / Function (体用)` |
| 生克 | generation and control | productive / controlling relationship | 推荐解释层用 `generation/control` |
| 比和 | same-element harmony | harmony | 可写 `same-element harmony` |
| 克应 | correlative response | responsive correspondence | 无唯一标准，建议双语说明 |

## 流派与方法术语

| 中文 | 推荐英文 | 备注 | 建议用法 |
|---|---|---|---|
| 大衍筮法 | Dayan divination | 也可解释为 `milfoil stalk divination` | 方法 ID 保留 `dayan` |
| 朱熹筮仪 | Zhu Xi divination procedure | 非常适合双写 | `dayan_zhu_xi_v1` |
| 梅花易数 | Meihua Yishu | 常见英文是拼音保留 | 文档可写 `Meihua Yishu (Plum Blossom Numerology)` |
| 时间起卦 | time-based casting | meihua time method | `meihua-time` |
| 数字起卦 | number-based casting | numeric casting | `meihua-number` |
| 声音占 | sound-based casting | sound divination | `meihua-sound` |
| 字占 | word-based casting | text-based casting | `meihua-word` |
| 物数占 | object-based casting | object numerology | `meihua-object` |
| 为人占 | person-based casting | person divination | `meihua-person` |
| 静物占 | static-object casting | inanimate-object casting | `meihua-static` |
| 钱币法 / 三钱法 | three-coin method | coin casting | `coin` |

## 五行与象数术语

| 中文 | 推荐英文 | 建议用法 |
|---|---|---|
| 五行 | Five Phases | 优先不用 `five elements` 作为唯一术语 |
| 木 | Wood | `wood` |
| 火 | Fire | `fire` |
| 土 | Earth | `earth` |
| 金 | Metal | `metal` |
| 水 | Water | `water` |
| 先天八卦 | Earlier Heaven Trigrams | 文档级术语 |
| 后天八卦 | Later Heaven Trigrams | 文档级术语 |

## 项目命名建议

### 代码字段

- `primary_hexagram`
- `relating_hexagram`
- `mutual_hexagram`
- `changing_lines`
- `upper_trigram`
- `lower_trigram`
- `plain_language_summary`
- `body_use_analysis`
- `interpretation_profile`

### 方法 ID

- `dayan_zhu_xi_v1`
- `coin_three_v1`
- `meihua_time_v1`
- `meihua_number_v1`
- `meihua_sound_v1`
- `meihua_word_v1`
- `meihua_object_v1`
- `meihua_person_v1`
- `meihua_static_v1`

### UI/文档推荐写法

- `Primary Hexagram (本卦)`
- `Relating Hexagram (变卦)`
- `Mutual Hexagram (互卦)`
- `Judgment (卦辞)`
- `Tuan Commentary (彖传)`
- `Image Commentary (象传)`
- `Body / Function (体用)`
- `Meihua Yishu (梅花易数)`
- `Dayan Divination (大衍筮法)`

## 不建议

- 在核心模型里混用 `gua`、`hexagram`
- 把所有专名都强行翻成生硬英文
- 把没有统一译法的词伪装成“唯一标准翻译”

## 最稳妥的落地策略

- 基础概念：英文为主
- 强传统专名：拼音保留
- 首次出现：双语并列
- 代码命名：稳定英文
- 方法命名：可保留拼音
