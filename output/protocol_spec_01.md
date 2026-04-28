# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: data\families.json
- **source_feature_summary**: None
- **source_relations_summary**: data\relations.json
- **source_semantics_summary**: data\semantics.json
- **notes**: Initial auto-generated protocol model assembled from family summaries.

## Family Relations

- Total inferred family edges: `70`
- Strongest edges:
- `family_8` -> `family_8` | pairs=`12233` avg_score=`3.4449` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_14` | pairs=`11545` avg_score=`3.4446` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_11` | pairs=`4230` avg_score=`3.4434` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_0` | pairs=`2488` avg_score=`3.4664` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_0` | pairs=`2120` avg_score=`3.4683` echo_fields=`20` length_rules=`14`
- `family_14` -> `noise` | pairs=`1411` avg_score=`3.4582` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_14` | pairs=`1342` avg_score=`3.2795` echo_fields=`20`
- `family_6` -> `family_8` | pairs=`1010` avg_score=`3.4688` echo_fields=`20` length_rules=`14`
- `noise` -> `family_11` | pairs=`944` avg_score=`3.4397` echo_fields=`17`
- `noise` -> `family_8` | pairs=`927` avg_score=`3.4531` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_3` | pairs=`895` avg_score=`3.4688` echo_fields=`20` length_rules=`14`
- `noise` -> `family_14` | pairs=`892` avg_score=`3.4322` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_14` | pairs=`886` avg_score=`3.4688` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_11` | pairs=`851` avg_score=`3.3544` echo_fields=`20`
- `family_11` -> `family_0` | pairs=`759` avg_score=`3.4688` echo_fields=`20` length_rules=`14`
- `family_8` -> `noise` | pairs=`692` avg_score=`3.4511` echo_fields=`20` length_rules=`14`
- `family_7` -> `family_8` | pairs=`642` avg_score=`3.4375` echo_fields=`20` length_rules=`14`
- `family_9` -> `family_11` | pairs=`529` avg_score=`3.4688` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_1` | pairs=`427` avg_score=`3.4688` echo_fields=`20` length_rules=`14`
- `family_10` -> `family_11` | pairs=`325` avg_score=`3.4375` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_14` | pairs=`308` avg_score=`3.4375` echo_fields=`20` length_rules=`14`
- `family_11` -> `noise` | pairs=`267` avg_score=`3.4688` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_11` | pairs=`200` avg_score=`3.25` echo_fields=`20` length_rules=`14`
- `family_3` -> `family_14` | pairs=`199` avg_score=`3.4688` echo_fields=`20` length_rules=`2`
- `family_7` -> `family_14` | pairs=`183` avg_score=`3.25` echo_fields=`20` length_rules=`14`

## Families

- Total families: `16`
- Families shown below: `16`

### family_14

- Role: `request`
- Messages: `33215`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_3`, `family_4`, `family_5`
- Role hint: `request`
- Semantic confidence: `0.5145`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`1.0`
- bytes `10`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

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
- bytes `9`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`10` | label=`echoed_request_field` confidence=`1.0`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_13 with up to 20 strong offset matches.

### family_8

- Role: `request`
- Messages: `32930`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_3`, `family_4`, `family_5`
- Role hint: `request`
- Semantic confidence: `0.5485`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`1.0`
- bytes `10`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

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
- bytes `7`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`echoed_request_field` confidence=`1.0`

#### Notes

- Echoes request fields from family_6 with up to 20 strong offset matches.
- Response size is tied to request fields from family_6.
- Echoes request fields from family_7 with up to 20 strong offset matches.
- Response size is tied to request fields from family_7.
- Echoes request fields from family_8 with up to 20 strong offset matches.

### family_11

- Role: `response`
- Messages: `14615`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `response`
- Semantic confidence: `0.5566`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`1.0`
- bytes `10`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

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

### family_0

- Role: `response`
- Messages: `5956`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_0`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_5`, `family_8`, `noise`
- Role hint: `response`
- Semantic confidence: `0.9868`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`9` | kind=`variable` confidence=`0.294`
- bytes `10`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`constant` confidence=`1.0`

#### Field Hypotheses

- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9898`
- bytes `0`..`0` | type=`keyword` confidence=`0.9837`
- bytes `1`..`1` | type=`keyword` confidence=`0.957`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9898`
- bytes `0`..`0` | label=`keyword` confidence=`0.9837`
- bytes `1`..`1` | label=`keyword` confidence=`0.957`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.
- Echoes request fields from family_14 with up to 20 strong offset matches.

### noise

- Role: `request`
- Messages: `5770`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_7`, `family_8`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5408`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`1.0`
- bytes `10`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

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

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.
- Echoes request fields from family_13 with up to 20 strong offset matches.

### family_3

- Role: `response`
- Messages: `1109`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_1`, `family_11`, `family_14`, `family_8`
- Role hint: `response`
- Semantic confidence: `0.8159`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`9` | kind=`variable` confidence=`0.2936`
- bytes `10`..`10` | kind=`variable` confidence=`1.0`

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

### family_12

- Role: `request`
- Messages: `1066`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_0`, `family_10`, `family_11`, `family_14`, `family_7`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `0.8423`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`11` | kind=`constant` confidence=`0.3377`

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

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_7 with up to 20 strong offset matches.
- Response size is tied to request fields from family_7.
- Echoes request fields from family_8 with up to 20 strong offset matches.

### family_6

- Role: `request`
- Messages: `1010`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_8`
- Role hint: `request`
- Semantic confidence: `1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`11` | kind=`constant` confidence=`0.3377`

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

### family_7

- Role: `request`
- Messages: `967`
- Template: `?? ?? 00 00 00 06 01 01 00 19 00 01`
- Related families: `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`11` | kind=`constant` confidence=`0.3724`

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

### family_13

- Role: `request`
- Messages: `945`
- Template: `?? ?? 00 00 00 06 01 01 00 19 00 01`
- Related families: `family_0`, `family_10`, `family_11`, `family_14`, `family_7`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `0.7503`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`11` | kind=`constant` confidence=`0.3724`

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

### family_9

- Role: `request`
- Messages: `657`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_11`, `family_12`, `family_13`, `family_14`, `family_7`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `0.8052`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`11` | kind=`constant` confidence=`0.3377`

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
- Echoes request fields from family_14 with up to 20 strong offset matches.

### family_10

- Role: `request`
- Messages: `647`
- Template: `?? ?? 00 00 00 06 01 01 00 19 00 01`
- Related families: `family_0`, `family_11`, `family_12`, `family_13`, `family_14`, `family_5`, `family_7`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `0.6385`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`11` | kind=`constant` confidence=`0.3724`

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

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_13 with up to 20 strong offset matches.

### family_1

- Role: `response`
- Messages: `645`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_11`, `family_14`, `family_3`, `family_8`, `noise`
- Role hint: `response`
- Semantic confidence: `1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`9` | kind=`constant` confidence=`0.2936`
- bytes `10`..`10` | kind=`variable` confidence=`1.0`

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
- Echoes request fields from family_14 with up to 19 strong offset matches.
- Echoes request fields from family_3 with up to 20 strong offset matches.
- Response size is tied to request fields from family_3.

### family_4

- Role: `response`
- Messages: `189`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_11`, `family_14`, `family_8`
- Role hint: `response`
- Semantic confidence: `0.8634`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`9` | kind=`constant` confidence=`0.2936`
- bytes `10`..`10` | kind=`variable` confidence=`1.0`

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
- Echoes request fields from family_8 with up to 20 strong offset matches.
- Response size is tied to request fields from family_8.

### family_5

- Role: `response`
- Messages: `164`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_0`, `family_10`, `family_11`, `family_14`, `family_8`
- Role hint: `response`
- Semantic confidence: `0.784`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`9` | kind=`variable` confidence=`0.2936`
- bytes `10`..`10` | kind=`variable` confidence=`1.0`

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
- Echoes request fields from family_8 with up to 20 strong offset matches.
- Response size is tied to request fields from family_8.

### family_2

- Role: `response`
- Messages: `115`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_11`
- Role hint: `response`
- Semantic confidence: `1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`1.0`
- bytes `1`..`1` | kind=`variable` confidence=`1.0`
- bytes `2`..`10` | kind=`variable` confidence=`0.2746`

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
