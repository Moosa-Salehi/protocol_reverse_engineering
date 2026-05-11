# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: D:\tez\practical\protocol_re\data\04_families.json
- **source_feature_summary**: D:\tez\practical\protocol_re\data\03_family_features.json
- **source_keyword_summary**: D:\tez\practical\protocol_re\data\06_keywords.json
- **source_relations_summary**: D:\tez\practical\protocol_re\data\08_relations.json
- **source_semantics_summary**: D:\tez\practical\protocol_re\data\09_semantics.json
- **notes**: Initial auto-generated protocol model assembled from family summaries.

## Evaluation

- Messages: `100000` across `23565` sessions
- Corpus assignment coverage: `1` with `16` families
- Clustering sample: `100000` messages ratio=`1`
- Parseable families: `16` of `16`
- Pair hypotheses: `47732` direction_unknown_ratio=`1`
- Relation edges: `37` echo_edges=`37` length_relation_edges=`34`
- Semantic coverage: `16` of `16` families ratio=`1`
- Top semantic labels: `keyword`x46, `echoed_request_field`x42, `response_size_selector`x23, `constant`x17, `blob`x15, `length`x4

### Evaluation Top Relation Edges

- `family_8` -> `family_8` | pairs=`12233` avg_score=`3.4449` support=`0.6798` lift=`2.1907` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_14` | pairs=`11545` avg_score=`3.4446` support=`0.7072` lift=`2.1912` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_11` | pairs=`4230` avg_score=`3.4434` support=`0.7331` lift=`4.8305` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_0` | pairs=`2488` avg_score=`3.4664` support=`0.1383` lift=`1.2289` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_0` | pairs=`2120` avg_score=`3.4683` support=`0.1299` lift=`1.1542` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_14` -> `noise` | pairs=`1411` avg_score=`3.4582` support=`0.0864` lift=`1.6548` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_6` -> `family_8` | pairs=`1010` avg_score=`3.4688` support=`1` lift=`3.2225` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `noise` -> `family_11` | pairs=`944` avg_score=`3.4397` support=`0.3215` lift=`2.1186` direction=`1` order=`1` echo_fields=`17` length_rules=`0`
- `noise` -> `family_8` | pairs=`927` avg_score=`3.4531` support=`0.3157` lift=`1.0175` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_3` | pairs=`895` avg_score=`3.4688` support=`0.0497` lift=`2.6525` direction=`1` order=`1` echo_fields=`20` length_rules=`14`

## Final Ground Truth Evaluation

- Overall score: `0.3063`
- Verdict: `fail`
- Matched message types: `11` of `11`
- Message type matching: accuracy=`0.6875` precision=`0.6875` recall=`1` f1=`0.8148`
- Field boundary: accuracy=`0.2581` precision=`0.2927` recall=`0.6857` f1=`0.4103`
- Field semantics: accuracy=`0` precision=`0` recall=`0` f1=`0`
- Relations: accuracy=`0` precision=`0` recall=`0` f1=`0`

## LLM Analysis

- Model: `deepseek-r1:8b`
- Prompt size: `150733` bytes, `150733` characters, estimated tokens=`37684`

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `37`
- Strongest edges:
- `family_8` -> `family_8` | pairs=`12233` avg_score=`3.4449` support=`0.6798` lift=`2.1907` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_14` | pairs=`11545` avg_score=`3.4446` support=`0.7072` lift=`2.1912` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_11` | pairs=`4230` avg_score=`3.4434` support=`0.7331` lift=`4.8305` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_0` | pairs=`2488` avg_score=`3.4664` support=`0.1383` lift=`1.2289` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_0` | pairs=`2120` avg_score=`3.4683` support=`0.1299` lift=`1.1542` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_14` -> `noise` | pairs=`1411` avg_score=`3.4582` support=`0.0864` lift=`1.6548` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_6` -> `family_8` | pairs=`1010` avg_score=`3.4688` support=`1` lift=`3.2225` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `noise` -> `family_11` | pairs=`944` avg_score=`3.4397` support=`0.3215` lift=`2.1186` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`17`
- `noise` -> `family_8` | pairs=`927` avg_score=`3.4531` support=`0.3157` lift=`1.0175` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_3` | pairs=`895` avg_score=`3.4688` support=`0.0497` lift=`2.6525` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_14` | pairs=`886` avg_score=`3.4688` support=`0.9877` lift=`3.0607` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_0` | pairs=`759` avg_score=`3.4688` support=`0.1315` lift=`1.1692` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_7` -> `family_8` | pairs=`642` avg_score=`3.4375` support=`0.6681` lift=`2.1528` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_9` -> `family_11` | pairs=`529` avg_score=`3.4688` support=`1` lift=`6.5892` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_1` | pairs=`427` avg_score=`3.4688` support=`0.074` lift=`7.92` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_10` -> `family_11` | pairs=`325` avg_score=`3.4375` support=`1` lift=`6.5892` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_14` | pairs=`308` avg_score=`3.4375` support=`0.4746` lift=`1.4706` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_11` | pairs=`200` avg_score=`3.25` support=`0.3082` lift=`2.0306` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_3` -> `family_14` | pairs=`199` avg_score=`3.4688` support=`0.9851` lift=`3.0527` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`2`
- `family_14` -> `family_4` | pairs=`150` avg_score=`3.4688` support=`0.0092` lift=`2.7756` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_13` | pairs=`140` avg_score=`3.25` support=`0.0078` lift=`1.7192` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_5` | pairs=`115` avg_score=`3.4688` support=`0.007` lift=`2.6474` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_12` | pairs=`104` avg_score=`3.25` support=`0.0058` lift=`1.642` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_2` | pairs=`87` avg_score=`3.4688` support=`0.0151` lift=`8.2724` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_10` | pairs=`76` avg_score=`3.25` support=`0.1171` lift=`30.3781` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`20` length_rules=`14`

## Families

- Total families: `16`
- Families shown below: `16`

### family_14

- Role: `request`
- Messages: `33215`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_12`, `family_13`, `family_14`, `family_3`, `family_4`, `family_5`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5415`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.337998`
- Candidate keyword offset: `9` cardinality=`7` entropy=`2.151`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7041`
- bytes `1`..`1` | kind=`variable` confidence=`0.6428`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7887`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7774`
- bytes `8`..`8` | kind=`variable` confidence=`0.7887`
- bytes `9`..`9` | kind=`variable` confidence=`0.7717`
- bytes `10`..`10` | kind=`variable` confidence=`0.7632`
- bytes `11`..`11` | kind=`variable` confidence=`0.779`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `7`..`7` | type=`keyword` confidence=`0.9998`
- bytes `9`..`9` | type=`keyword` confidence=`0.9998`
- bytes `11`..`11` | type=`keyword` confidence=`0.9998`
- bytes `10`..`10` | type=`keyword` confidence=`0.9997`
- bytes `0`..`0` | type=`keyword` confidence=`0.9988`
- bytes `1`..`1` | type=`keyword` confidence=`0.9923`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_13 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `33215` (`1.0`)
- Repeated n-gram instances: `40665`
- Top motifs: `0000`x66700, `000000`x33341, `0101`x20160, `0006`x18239, `000006`x18111

### family_8

- Role: `request`
- Messages: `32930`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_12`, `family_13`, `family_3`, `family_6`, `family_7`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5171`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.521928` max=`2.732159` mean=`2.335913`
- Candidate keyword offset: `9` cardinality=`7` entropy=`2.1583`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7038`
- bytes `1`..`1` | kind=`variable` confidence=`0.6428`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7885`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7775`
- bytes `8`..`8` | kind=`variable` confidence=`0.7885`
- bytes `9`..`9` | kind=`variable` confidence=`0.7715`
- bytes `10`..`10` | kind=`variable` confidence=`0.7624`
- bytes `11`..`11` | kind=`variable` confidence=`0.7788`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `11`..`11` | type=`keyword` confidence=`0.9999`
- bytes `7`..`7` | type=`keyword` confidence=`0.9998`
- bytes `9`..`9` | type=`keyword` confidence=`0.9998`
- bytes `10`..`10` | type=`keyword` confidence=`0.9997`
- bytes `0`..`0` | type=`keyword` confidence=`0.9988`
- bytes `1`..`1` | type=`keyword` confidence=`0.9922`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`0.9999`

#### Notes

- Echoes request fields from family_6 with up to 20 strong offset matches.
- Response size is tied to request fields from family_6.
- Echoes request fields from family_7 with up to 20 strong offset matches.
- Response size is tied to request fields from family_7.
- Echoes request fields from family_8 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `32930` (`1.0`)
- Repeated n-gram instances: `40304`
- Top motifs: `0000`x66172, `000000`x33062, `0101`x20232, `0006`x17973, `0601`x17861

### family_11

- Role: `response`
- Messages: `14615`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_13`, `family_2`, `family_4`, `family_5`, `family_9`, `noise`
- Role hint: `response`
- Semantic confidence: `0.5338`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.336032`
- Candidate keyword offset: `9` cardinality=`7` entropy=`2.1445`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7249`
- bytes `1`..`1` | kind=`variable` confidence=`0.6463`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7879`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7776`
- bytes `8`..`8` | kind=`variable` confidence=`0.7879`
- bytes `9`..`9` | kind=`variable` confidence=`0.7719`
- bytes `10`..`10` | kind=`variable` confidence=`0.7615`
- bytes `11`..`11` | kind=`variable` confidence=`0.776`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9998`
- bytes `7`..`7` | type=`keyword` confidence=`0.9997`
- bytes `11`..`11` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9995`
- bytes `10`..`10` | type=`keyword` confidence=`0.9995`
- bytes `0`..`0` | type=`keyword` confidence=`0.9984`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9825`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`0.9998`
- bytes `7`..`7` | label=`keyword` confidence=`0.9997`
- bytes `11`..`11` | label=`keyword` confidence=`0.9997`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_11 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `14615` (`1.0`)
- Repeated n-gram instances: `18187`
- Top motifs: `0000`x29358, `000000`x14671, `0101`x9333, `0100`x7719, `0006`x7583

### family_0

- Role: `response`
- Messages: `5956`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_11`, `family_13`, `family_14`, `family_8`
- Role hint: `response`
- Semantic confidence: `0.988`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.450826` max=`3.027169` mean=`3.013184`
- Candidate keyword offset: `10` cardinality=`61` entropy=`4.6186`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6823`
- bytes `1`..`1` | kind=`variable` confidence=`0.6557`
- bytes `2`..`9` | kind=`variable` confidence=`0.4303`
- bytes `10`..`10` | kind=`variable` confidence=`0.7198`
- bytes `11`..`11` | kind=`constant` confidence=`0.8665`

#### Field Hypotheses

- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9898`
- bytes `0`..`0` | type=`keyword` confidence=`0.9837`
- bytes `1`..`1` | type=`keyword` confidence=`0.957`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9898`
- bytes `0`..`0` | label=`keyword` confidence=`0.9837`
- bytes `1`..`1` | label=`keyword` confidence=`0.957`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.
- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.
- Echoes request fields from family_8 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `5956` (`1.0`)
- Repeated n-gram instances: `6007`
- Top motifs: `0000`x11937, `000000`x5981, `000005`x5890, `000501`x5890, `010402`x5890

### noise

- Role: `request`
- Messages: `5770`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_10`, `family_11`, `family_12`, `family_14`, `family_8`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5794`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.729574` max=`3.027169` mean=`2.611084`
- Candidate keyword offset: `10` cardinality=`50` entropy=`2.6282`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6873`
- bytes `1`..`1` | kind=`variable` confidence=`0.6571`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7978`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7832`
- bytes `8`..`8` | kind=`variable` confidence=`0.7978`
- bytes `9`..`9` | kind=`variable` confidence=`0.7789`
- bytes `10`..`10` | kind=`variable` confidence=`0.764`
- bytes `11`..`11` | kind=`variable` confidence=`0.7756`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9997`
- bytes `7`..`7` | type=`keyword` confidence=`0.9993`
- bytes `11`..`11` | type=`keyword` confidence=`0.9981`
- bytes `9`..`9` | type=`keyword` confidence=`0.9971`
- bytes `10`..`10` | type=`keyword` confidence=`0.9913`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9821`
- bytes `1`..`1` | type=`keyword` confidence=`0.9556`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`0.9997`
- bytes `7`..`7` | label=`keyword` confidence=`0.9993`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.

#### Feature Summary

- Messages with repetition: `5770` (`1.0`)
- Repeated n-gram instances: `5929`
- Top motifs: `0000`x11596, `000000`x5826, `0006`x3213, `000006`x3212, `000601`x3212

### family_3

- Role: `response`
- Messages: `1109`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_14`, `family_8`
- Role hint: `response`
- Semantic confidence: `0.8181`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.594907` max=`3.027169` mean=`3.015693`
- Candidate keyword offset: `10` cardinality=`6` entropy=`2.2699`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.739`
- bytes `1`..`1` | kind=`variable` confidence=`0.725`
- bytes `2`..`9` | kind=`variable` confidence=`0.4318`
- bytes `10`..`10` | kind=`variable` confidence=`0.7709`

#### Field Hypotheses

- bytes `10`..`10` | type=`keyword` confidence=`0.9946`
- bytes `0`..`0` | type=`keyword` confidence=`0.9856`
- bytes `1`..`1` | type=`blob` confidence=`0.5`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`keyword` confidence=`0.9946`
- bytes `0`..`0` | label=`keyword` confidence=`0.9856`
- bytes `1`..`1` | label=`blob` confidence=`0.5`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_8 with up to 20 strong offset matches.
- Response size is tied to request fields from family_8.

#### Feature Summary

- Messages with repetition: `1109` (`1.0`)
- Repeated n-gram instances: `1111`
- Top motifs: `0000`x2219, `000000`x1110, `000005`x1109, `000501`x1109, `010402`x1109

### family_12

- Role: `request`
- Messages: `1066`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_14`, `family_7`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `0.8419`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.284159` max=`2.450826` mean=`2.448793`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7263`
- bytes `1`..`1` | kind=`variable` confidence=`0.726`
- bytes `2`..`11` | kind=`constant` confidence=`0.6358`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9775`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9775`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_7 with up to 20 strong offset matches.
- Response size is tied to request fields from family_7.
- Echoes request fields from family_8 with up to 20 strong offset matches.
- Response size is tied to request fields from family_8.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `1066` (`1.0`)
- Repeated n-gram instances: `1072`
- Top motifs: `0000`x2132, `2300`x1072, `000000`x1066, `000006`x1066, `000601`x1066

### family_6

- Role: `request`
- Messages: `1010`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_8`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.284159` max=`2.450826` mean=`2.448516`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7288`
- bytes `1`..`1` | kind=`variable` confidence=`0.7306`
- bytes `2`..`11` | kind=`constant` confidence=`0.6358`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9792`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9792`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Feature Summary

- Messages with repetition: `1010` (`1.0`)
- Repeated n-gram instances: `1015`
- Top motifs: `0000`x2020, `2300`x1015, `000000`x1010, `000006`x1010, `000601`x1010

### family_7

- Role: `request`
- Messages: `967`
- Template: `?? ?? 00 00 00 06 01 01 00 19 00 01`
- Related families: `family_12`, `family_13`, `family_8`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.825011` max=`2.221252` mean=`2.211363`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7295`
- bytes `1`..`1` | kind=`variable` confidence=`0.7344`
- bytes `2`..`11` | kind=`constant` confidence=`0.6548`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9783`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9783`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Feature Summary

- Messages with repetition: `967` (`1.0`)
- Repeated n-gram instances: `970`
- Top motifs: `0000`x1934, `1900`x970, `000000`x967, `000006`x967, `000601`x967

### family_13

- Role: `request`
- Messages: `945`
- Template: `?? ?? 00 00 00 06 01 01 00 19 00 01`
- Related families: `family_0`, `family_10`, `family_11`, `family_14`, `family_7`, `family_8`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.7515`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.221252` mean=`2.219488`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7304`
- bytes `1`..`1` | kind=`variable` confidence=`0.7366`
- bytes `2`..`11` | kind=`constant` confidence=`0.6548`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9778`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9778`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_7 with up to 20 strong offset matches.
- Response size is tied to request fields from family_7.
- Echoes request fields from family_8 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `945` (`1.0`)
- Repeated n-gram instances: `949`
- Top motifs: `0000`x1890, `1900`x949, `000000`x945, `000006`x945, `000601`x945

### family_9

- Role: `request`
- Messages: `657`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_11`, `family_12`, `family_13`, `noise`
- Role hint: `request`
- Semantic confidence: `0.8921`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.284159` max=`2.450826` mean=`2.44905`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7431`
- bytes `1`..`1` | kind=`variable` confidence=`0.7785`
- bytes `2`..`11` | kind=`constant` confidence=`0.6358`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9756`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9756`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_13 with up to 20 strong offset matches.
- Response size is tied to request fields from family_13.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `657` (`1.0`)
- Repeated n-gram instances: `659`
- Top motifs: `0000`x1314, `2300`x659, `000000`x657, `000006`x657, `000601`x657

### family_10

- Role: `request`
- Messages: `647`
- Template: `?? ?? 00 00 00 06 01 01 00 19 00 01`
- Related families: `family_11`, `family_13`, `noise`
- Role hint: `request`
- Semantic confidence: `0.742`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.221252` mean=`2.219449`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7431`
- bytes `1`..`1` | kind=`variable` confidence=`0.7793`
- bytes `2`..`11` | kind=`constant` confidence=`0.6548`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9768`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9768`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_13 with up to 20 strong offset matches.
- Response size is tied to request fields from family_13.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `647` (`1.0`)
- Repeated n-gram instances: `650`
- Top motifs: `0000`x1294, `1900`x650, `000000`x647, `000006`x647, `000601`x647

### family_1

- Role: `response`
- Messages: `645`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_11`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.023786`
- Candidate keyword offset: `10` cardinality=`3` entropy=`1.3759`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7506`
- bytes `1`..`1` | kind=`variable` confidence=`0.7813`
- bytes `2`..`9` | kind=`constant` confidence=`0.6115`
- bytes `10`..`10` | kind=`variable` confidence=`0.7907`

#### Field Hypotheses

- bytes `10`..`10` | type=`keyword` confidence=`0.9953`
- bytes `2`..`9` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9829`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `10`..`10` | label=`keyword` confidence=`0.9953`
- bytes `2`..`9` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9829`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.

#### Feature Summary

- Messages with repetition: `645` (`1.0`)
- Repeated n-gram instances: `645`
- Top motifs: `0000`x1290, `000000`x645, `000005`x645, `000501`x645, `010402`x645

### family_4

- Role: `response`
- Messages: `189`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_11`, `family_14`
- Role hint: `response`
- Semantic confidence: `0.8571`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`3.027169` max=`3.027169` mean=`3.027169`
- Candidate keyword offset: `10` cardinality=`6` entropy=`1.7547`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7695`
- bytes `1`..`1` | kind=`variable` confidence=`0.8553`
- bytes `2`..`9` | kind=`constant` confidence=`0.6115`
- bytes `10`..`10` | kind=`variable` confidence=`0.7919`

#### Field Hypotheses

- bytes `2`..`9` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9683`
- bytes `0`..`0` | type=`keyword` confidence=`0.9259`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9683`
- bytes `2`..`9` | label=`response_size_selector` confidence=`0.96`
- bytes `0`..`0` | label=`keyword` confidence=`0.9259`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.

#### Feature Summary

- Messages with repetition: `189` (`1.0`)
- Repeated n-gram instances: `189`
- Top motifs: `0000`x378, `000000`x189, `000005`x189, `000501`x189, `010402`x189

### family_5

- Role: `response`
- Messages: `164`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_11`, `family_14`
- Role hint: `response`
- Semantic confidence: `0.777`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.022734`
- Candidate keyword offset: `10` cardinality=`7` entropy=`1.1389`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7832`
- bytes `1`..`1` | kind=`variable` confidence=`0.8537`
- bytes `2`..`9` | kind=`variable` confidence=`0.4339`
- bytes `10`..`10` | kind=`variable` confidence=`0.8097`

#### Field Hypotheses

- bytes `10`..`10` | type=`keyword` confidence=`0.9573`
- bytes `0`..`0` | type=`keyword` confidence=`0.9268`
- bytes `1`..`1` | type=`blob` confidence=`0.5`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`keyword` confidence=`0.9573`
- bytes `0`..`0` | label=`keyword` confidence=`0.9268`
- bytes `1`..`1` | label=`blob` confidence=`0.5`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.

#### Feature Summary

- Messages with repetition: `164` (`1.0`)
- Repeated n-gram instances: `164`
- Top motifs: `0000`x328, `000000`x164, `000005`x164, `000501`x164, `010402`x164

### family_2

- Role: `response`
- Messages: `115`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_11`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.024007`
- Candidate keyword offset: `10` cardinality=`2` entropy=`0.2956`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7803`
- bytes `1`..`1` | kind=`variable` confidence=`0.8546`
- bytes `2`..`10` | kind=`variable` confidence=`0.4238`

#### Field Hypotheses

- bytes `0`..`0` | type=`keyword` confidence=`0.9391`
- bytes `1`..`1` | type=`blob` confidence=`0.5`
- bytes `2`..`10` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`keyword` confidence=`0.9391`
- bytes `1`..`1` | label=`blob` confidence=`0.5`
- bytes `2`..`10` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.

#### Feature Summary

- Messages with repetition: `115` (`1.0`)
- Repeated n-gram instances: `115`
- Top motifs: `0000`x230, `000000`x115, `000005`x115, `000501`x115, `010402`x115
