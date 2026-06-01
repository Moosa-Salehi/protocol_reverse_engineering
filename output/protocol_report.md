# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **framing_global_summary**: {'common_header_ends': [{'header_end': 6, 'family_count': 11, 'family_ratio': 1.0}], 'field_type_counts': {'length': 33, 'transaction_or_counter': 20, 'constant': 5, 'discriminator': 5}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 11}
- **llm_refinement**: {'artifact_type': 'llm_refinement_summary', 'created_at': '2026-06-01T10:14:58.681015+00:00', 'input_patch_count': 0, 'accepted_patch_count': 0, 'rejected_patch_count': 0}

## Evaluation

- Messages: `200000` across `100001` sessions
- Corpus assignment coverage: `1` with `11` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `11` of `11`
- Pair hypotheses: `99999` direction_unknown_ratio=`1`
- Relation edges: `17` echo_edges=`2` length_relation_edges=`0`
- Semantic coverage: `11` of `11` families ratio=`1`
- Top semantic labels: `discriminator`x22, `length`x11, `payload`x11, `constant`x11, `transaction_id`x7
- Framing coverage: `11` of `11` families ratio=`1`
- Clustering diagnostics: warning_families=`5` split_candidates=`0` merge_candidates=`0`

### Clustering Diagnostic Warnings

- `family_1` | messages=`120667` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `family_6` | messages=`38027` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `family_4` | messages=`14904` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `family_5` | messages=`13239` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `noise` | messages=`763` split=`0` under_split=`0` over_split=`0` warnings=noise family

### Evaluation Top Relation Edges

- `family_6` -> `family_6` | pairs=`16660` avg_score=`5.448` support=`0.8624` lift=`4.6096` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_4` -> `family_4` | pairs=`5936` avg_score=`5.4461` support=`0.7472` lift=`10.736` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_5` -> `family_5` | pairs=`5262` avg_score=`5.446` support=`0.7661` lift=`12.0277` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_1` -> `family_9` | pairs=`2345` avg_score=`5.4675` support=`0.0356` lift=`1.2169` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_1` -> `family_7` | pairs=`1736` avg_score=`5.4676` support=`0.0264` lift=`1.5165` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_1` -> `family_3` | pairs=`1536` avg_score=`5.4675` support=`0.0233` lift=`1.1797` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_6` -> `family_8` | pairs=`853` avg_score=`5.4676` support=`0.0442` lift=`1.9826` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_1` -> `noise` | pairs=`675` avg_score=`5.4674` support=`0.0103` lift=`1.427` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_5` -> `family_2` | pairs=`547` avg_score=`5.4677` support=`0.0796` lift=`3.1277` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_6` -> `family_0` | pairs=`527` avg_score=`5.4675` support=`0.0273` lift=`2.8897` direction=`1` order=`1` echo_fields=`0` length_rules=`0`

## Final Ground Truth Evaluation

- Overall score: `0.4527`
- Verdict: `fail`
- Matched message types: `11` of `11`
- Message type matching: accuracy=`1` precision=`1` recall=`1` f1=`1`
- Field boundary: accuracy=`0.3134` precision=`0.3962` recall=`0.6` f1=`0.4773`
- Field semantics: accuracy=`0` precision=`0` recall=`0` f1=`0`
- Relations: accuracy=`0.2` precision=`0.2353` recall=`0.5714` f1=`0.3333`

## LLM Analysis

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `17`
- Strongest edges:
- `family_6` -> `family_6` | pairs=`16660` avg_score=`5.448` support=`0.8624` lift=`4.6096` direction=`1` order=`1` flow=`unknown->unknown`
- `family_4` -> `family_4` | pairs=`5936` avg_score=`5.4461` support=`0.7472` lift=`10.736` direction=`1` order=`1` flow=`unknown->unknown`
- `family_5` -> `family_5` | pairs=`5262` avg_score=`5.446` support=`0.7661` lift=`12.0277` direction=`1` order=`1` flow=`unknown->unknown`
- `family_1` -> `family_9` | pairs=`2345` avg_score=`5.4675` support=`0.0356` lift=`1.2169` direction=`1` order=`1` flow=`unknown->unknown`
- `family_1` -> `family_7` | pairs=`1736` avg_score=`5.4676` support=`0.0264` lift=`1.5165` direction=`1` order=`1` flow=`unknown->unknown`
- `family_1` -> `family_3` | pairs=`1536` avg_score=`5.4675` support=`0.0233` lift=`1.1797` direction=`1` order=`1` flow=`unknown->unknown`
- `family_6` -> `family_8` | pairs=`853` avg_score=`5.4676` support=`0.0442` lift=`1.9826` direction=`1` order=`1` flow=`unknown->unknown`
- `family_1` -> `noise` | pairs=`675` avg_score=`5.4674` support=`0.0103` lift=`1.427` direction=`1` order=`1` flow=`unknown->unknown`
- `family_5` -> `family_2` | pairs=`547` avg_score=`5.4677` support=`0.0796` lift=`3.1277` direction=`1` order=`1` flow=`unknown->unknown`
- `family_6` -> `family_0` | pairs=`527` avg_score=`5.4675` support=`0.0273` lift=`2.8897` direction=`1` order=`1` flow=`unknown->unknown`
- `family_4` -> `family_2` | pairs=`386` avg_score=`5.4674` support=`0.0486` lift=`1.9085` direction=`1` order=`1` flow=`unknown->unknown`
- `family_4` -> `family_9` | pairs=`339` avg_score=`5.4676` support=`0.0427` lift=`1.4569` direction=`1` order=`1` flow=`unknown->unknown`
- `family_4` -> `family_3` | pairs=`257` avg_score=`5.4673` support=`0.0324` lift=`1.6347` direction=`1` order=`1` flow=`unknown->unknown`
- `family_5` -> `family_9` | pairs=`241` avg_score=`5.4673` support=`0.0351` lift=`1.1978` direction=`1` order=`1` flow=`unknown->unknown`
- `family_5` -> `family_3` | pairs=`180` avg_score=`5.4672` support=`0.0262` lift=`1.3241` direction=`1` order=`1` flow=`unknown->unknown`
- `noise` -> `noise` | pairs=`44` avg_score=`5.4969` support=`1` lift=`139.0807` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`2`
- `family_0` -> `family_0` | pairs=`22` avg_score=`5.4966` support=`1` lift=`105.9311` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`2`

## Families

- Total families: `11`
- Families shown below: `11`

### family_1

- Role: `request`
- Messages: `120667`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_3`, `family_7`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.314913`
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.841241` salience=`0.746807` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.493451`
- Top discriminator candidates: offset `7` conf=`0.493451` salience=`0.746807`, offset `0` conf=`0.48592` salience=`1.0`, offset `9` conf=`0.378374` salience=`0.290365`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.608855`
- bytes `2`..`5` | kind=`variable` confidence=`0.8075`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.6868927499999999`
- bytes `11`..`11` | kind=`variable` confidence=`0.7786`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`keyword` confidence=`0.9999`
- bytes `7`..`10` | type=`keyword` confidence=`0.9998`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `11`..`11` | label=`discriminator` confidence=`0.9999`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9998`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`10` | label=`payload` confidence=`0.6`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `120667` (`1.0`)
- Repeated n-gram instances: `151662`
- Top motifs: `0000`x242047, `000000`x121075, `0101`x83129, `0100`x67963, `0006`x66531

### family_6

- Role: `request`
- Messages: `38027`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_6`, `family_8`
- Role hint: `request`
- Semantic confidence: `0.5199`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.485475` max=`3.027169` mean=`2.389712`
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.98095` salience=`0.746807` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.497696`
- Top discriminator candidates: offset `7` conf=`0.497696` salience=`0.746807`, offset `8` conf=`0.371024` salience=`0.360711`, offset `9` conf=`0.310938` salience=`0.290365`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6103749999999999`
- bytes `2`..`5` | kind=`variable` confidence=`0.8075`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.6774165`
- bytes `11`..`11` | kind=`variable` confidence=`0.7738`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`keyword` confidence=`0.9997`
- bytes `7`..`10` | type=`keyword` confidence=`0.9986`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9986`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`
- bytes `7`..`10` | label=`payload` confidence=`0.6`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `38027` (`1.0`)
- Repeated n-gram instances: `45619`
- Top motifs: `0000`x76283, `000000`x38136, `0101`x21262, `0006`x19674, `0601`x19441

### family_4

- Role: `request`
- Messages: `14904`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_2`, `family_3`, `family_4`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5382`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`3.027169` mean=`2.379388`
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.941612` salience=`0.746807` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.497433`
- Top discriminator candidates: offset `7` conf=`0.497433` salience=`0.746807`, offset `8` conf=`0.369686` salience=`0.360711`, offset `9` conf=`0.35333` salience=`0.290365`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.636405`
- bytes `2`..`5` | kind=`variable` confidence=`0.8075`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.6802142499999999`
- bytes `11`..`11` | kind=`variable` confidence=`0.7778`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`keyword` confidence=`0.9996`
- bytes `7`..`10` | type=`keyword` confidence=`0.9975`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`10` | label=`discriminator` confidence=`0.95`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`
- bytes `7`..`10` | label=`payload` confidence=`0.6`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `14904` (`1.0`)
- Repeated n-gram instances: `18144`
- Top motifs: `0000`x30047, `000000`x15110, `0101`x8267, `000006`x7951, `000601`x7951

### family_5

- Role: `request`
- Messages: `13239`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_2`, `family_3`, `family_5`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5421`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.846439` max=`3.027169` mean=`2.402529`
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.93922` salience=`0.746807` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.497199`
- Top discriminator candidates: offset `7` conf=`0.497199` salience=`0.746807`, offset `8` conf=`0.370537` salience=`0.360711`, offset `9` conf=`0.339231` salience=`0.290365`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.631655`
- bytes `2`..`5` | kind=`variable` confidence=`0.8075`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.67858975`
- bytes `11`..`11` | kind=`variable` confidence=`0.7765`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`keyword` confidence=`0.9997`
- bytes `7`..`10` | type=`keyword` confidence=`0.9974`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`10` | label=`discriminator` confidence=`0.95`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`
- bytes `7`..`10` | label=`payload` confidence=`0.6`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `13239` (`1.0`)
- Repeated n-gram instances: `15569`
- Top motifs: `0000`x26488, `000000`x13239, `0101`x7474, `000006`x6875, `000601`x6875

### family_9

- Role: `response`
- Messages: `2933`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_1`, `family_4`, `family_5`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.020272`
- Candidate discriminator offset: `10` cardinality=`17` entropy=`3.463243` salience=`0.345561` mutual_information=`0.308526` contrastive_separation=`1.0` confidence=`0.356191`
- Top discriminator candidates: offset `10` conf=`0.356191` salience=`0.345561`, offset `9` conf=`0.338512` salience=`0.290365`, offset `8` conf=`0.331546` salience=`0.360711`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.638115`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7442`
- bytes `11`..`11` | kind=`constant` confidence=`0.8654`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `6`..`9` | type=`keyword` confidence=`0.998`
- bytes `10`..`10` | type=`keyword` confidence=`0.9942`
- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`1` | type=`counter_or_transaction_id` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`9` | label=`discriminator` confidence=`0.998`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `6`..`9` | label=`payload` confidence=`0.6`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `2933` (`1.0`)
- Repeated n-gram instances: `2953`
- Top motifs: `0000`x5876, `000000`x2943, `000005`x2925, `000501`x2925, `010402`x2925

### family_2

- Role: `response`
- Messages: `2548`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_4`, `family_5`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.02023`
- Candidate discriminator offset: `8` cardinality=`2` entropy=`0.016887` salience=`0.360711` mutual_information=`0.093933` contrastive_separation=`0.78125` confidence=`0.331477`
- Top discriminator candidates: offset `8` conf=`0.331477` salience=`0.360711`, offset `10` conf=`0.329449` salience=`0.345561`, offset `9` conf=`0.316983` salience=`0.290365`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.642485`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.753`
- bytes `11`..`11` | kind=`constant` confidence=`0.8652`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `6`..`9` | type=`keyword` confidence=`0.9965`
- bytes `10`..`10` | type=`keyword` confidence=`0.991`
- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`1` | type=`counter_or_transaction_id` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`9` | label=`discriminator` confidence=`0.9965`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `6`..`9` | label=`payload` confidence=`0.6`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `2548` (`1.0`)
- Repeated n-gram instances: `2568`
- Top motifs: `0000`x5106, `000000`x2558, `000005`x2544, `000501`x2544, `010402`x2544

### family_8

- Role: `response`
- Messages: `2227`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ??`
- Related families: `family_6`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.550341` max=`3.027169` mean=`3.017568`
- Candidate discriminator offset: `9` cardinality=`7` entropy=`0.30222` salience=`0.290365` mutual_information=`0.184592` contrastive_separation=`0.859375` confidence=`0.333955`
- Top discriminator candidates: offset `9` conf=`0.333955` salience=`0.290365`, offset `10` conf=`0.328925` salience=`0.345561`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6476149999999999`
- bytes `2`..`5` | kind=`constant` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7566`

#### Field Hypotheses

- bytes `6`..`9` | type=`keyword` confidence=`0.9969`
- bytes `10`..`10` | type=`keyword` confidence=`0.9915`
- bytes `2`..`5` | type=`constant` confidence=`0.99`
- bytes `0`..`1` | type=`counter_or_transaction_id` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`9` | label=`discriminator` confidence=`0.9969`
- bytes `2`..`5` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `6`..`9` | label=`payload` confidence=`0.6`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `2227` (`1.0`)
- Repeated n-gram instances: `2245`
- Top motifs: `0000`x4463, `000000`x2236, `000005`x2227, `000501`x2227, `010402`x2227

### family_3

- Role: `response`
- Messages: `1985`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_1`, `family_4`, `family_5`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.018191`
- Candidate discriminator offset: `10` cardinality=`9` entropy=`2.726791` salience=`0.345561` mutual_information=`0.308526` contrastive_separation=`0.890625` confidence=`0.405768`
- Top discriminator candidates: offset `10` conf=`0.405768` salience=`0.345561`, offset `9` conf=`0.353055` salience=`0.290365`, offset `8` conf=`0.331745` salience=`0.360711`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6524599999999999`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7603`
- bytes `11`..`11` | kind=`constant` confidence=`0.8658`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `6`..`9` | type=`keyword` confidence=`0.998`
- bytes `10`..`10` | type=`keyword` confidence=`0.9955`
- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`1` | type=`counter_or_transaction_id` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`9` | label=`discriminator` confidence=`0.998`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `6`..`9` | label=`payload` confidence=`0.6`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `1985` (`1.0`)
- Repeated n-gram instances: `2001`
- Top motifs: `0000`x3978, `000000`x1993, `000005`x1973, `000501`x1973, `010402`x1973

### family_7

- Role: `response`
- Messages: `1740`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_1`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.732159` max=`3.027169` mean=`3.023486`
- Candidate discriminator offset: `9` cardinality=`5` entropy=`0.02806` salience=`0.290365` mutual_information=`0.184592` contrastive_separation=`0.828125` confidence=`0.345612`
- Top discriminator candidates: offset `9` conf=`0.345612` salience=`0.290365`, offset `10` conf=`0.334878` salience=`0.345561`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.660725`
- bytes `2`..`5` | kind=`constant` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7547`

#### Field Hypotheses

- bytes `6`..`9` | type=`keyword` confidence=`0.9971`
- bytes `2`..`5` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9891`
- bytes `0`..`1` | type=`counter_or_transaction_id` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`9` | label=`discriminator` confidence=`0.9971`
- bytes `2`..`5` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `6`..`9` | label=`payload` confidence=`0.6`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `1740` (`1.0`)
- Repeated n-gram instances: `1744`
- Top motifs: `0000`x3482, `000000`x1742, `000005`x1740, `000501`x1740, `010402`x1740

### family_0

- Role: `response`
- Messages: `967`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ?? 00`
- Related families: `family_0`, `family_6`
- Role hint: `response`
- Semantic confidence: `0.9615`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.40401` max=`3.027169` mean=`2.97951`
- Candidate discriminator offset: `10` cardinality=`17` entropy=`2.492763` salience=`0.345561` mutual_information=`0.308526` contrastive_separation=`1.0` confidence=`0.346901`
- Top discriminator candidates: offset `10` conf=`0.346901` salience=`0.345561`, offset `8` conf=`0.334112` salience=`0.360711`, offset `9` conf=`0.312825` salience=`0.290365`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.69977`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7702`
- bytes `11`..`11` | kind=`constant` confidence=`0.8711`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `6`..`9` | type=`keyword` confidence=`0.9897`
- bytes `10`..`10` | type=`keyword` confidence=`0.9824`
- bytes `0`..`1` | type=`counter_or_transaction_id` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `6`..`9` | label=`discriminator` confidence=`0.95`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `6`..`9` | label=`payload` confidence=`0.6`

#### Notes

- Echoes request fields from family_0 with up to 2 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `967` (`1.0`)
- Repeated n-gram instances: `981`
- Top motifs: `0000`x1940, `000000`x973, `0005`x924, `0104`x924, `000005`x923

### noise

- Role: `response`
- Messages: `763`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 00`
- Related families: `family_1`, `noise`
- Role hint: `response`
- Semantic confidence: `0.9423`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.450826` max=`3.027169` mean=`2.958612`
- Candidate discriminator offset: `8` cardinality=`2` entropy=`0.515799` salience=`0.360711` mutual_information=`0.093933` contrastive_separation=`0.78125` confidence=`0.338302`
- Top discriminator candidates: offset `8` conf=`0.338302` salience=`0.360711`, offset `10` conf=`0.323953` salience=`0.345561`, offset `9` conf=`0.29124` salience=`0.290365`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.7014799999999999`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.745655`
- bytes `10`..`10` | kind=`variable` confidence=`0.7707`
- bytes `11`..`11` | kind=`constant` confidence=`0.8806`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `6`..`9` | type=`keyword` confidence=`0.9777`
- bytes `0`..`1` | type=`counter_or_transaction_id` confidence=`0.9423` endian=`big`
- bytes `10`..`10` | type=`keyword` confidence=`0.9201`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `6`..`9` | label=`discriminator` confidence=`0.95`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `6`..`9` | label=`payload` confidence=`0.6`

#### Notes

- Echoes request fields from noise with up to 2 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `763` (`1.0`)
- Repeated n-gram instances: `797`
- Top motifs: `0000`x1542, `000000`x779, `000005`x675, `000501`x675, `010402`x675
