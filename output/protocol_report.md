# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: D:\tez\practical\protocol_re\data\05_families_labeled.json
- **source_feature_summary**: D:\tez\practical\protocol_re\data\03_family_features.json
- **source_keyword_summary**: D:\tez\practical\protocol_re\data\07_keywords.json
- **source_framing_summary**: D:\tez\practical\protocol_re\data\04_framing.json
- **source_relations_summary**: D:\tez\practical\protocol_re\data\08_relations_validated.json
- **source_semantics_summary**: D:\tez\practical\protocol_re\data\09_semantics.json
- **framing_global_summary**: {'common_header_ends': [{'header_end': 6, 'family_count': 11, 'family_ratio': 1.0}], 'field_type_counts': {'length': 33, 'transaction_or_counter': 20, 'constant': 5, 'discriminator': 5}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 11}
- **notes**: Initial auto-generated protocol model assembled from family summaries.
- **llm_refinement**: {'artifact_type': 'llm_refinement_summary', 'created_at': '2026-06-01T06:34:44.753869+00:00', 'input_patch_count': 0, 'accepted_patch_count': 0, 'rejected_patch_count': 0}

## Evaluation

- Messages: `200000` across `1` sessions
- Corpus assignment coverage: `1` with `11` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `11` of `11`
- Pair hypotheses: `100000` direction_unknown_ratio=`1`
- Relation edges: `18` echo_edges=`1` length_relation_edges=`1`
- Semantic coverage: `11` of `11` families ratio=`1`
- Top semantic labels: `discriminator`x22, `length`x11, `payload`x11, `constant`x11, `transaction_id`x7, `echoed_request_field`x1, `transaction_or_correlation_id`x1, `response_size_selector`x1
- Framing coverage: `11` of `11` families ratio=`1`
- Clustering diagnostics: warning_families=`5` split_candidates=`0` merge_candidates=`0`

### Clustering Diagnostic Warnings

- `family_1` | messages=`120667` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `family_6` | messages=`38027` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `family_4` | messages=`14904` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `family_5` | messages=`13239` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `noise` | messages=`763` split=`0` under_split=`0` over_split=`0` warnings=noise family

### Evaluation Top Relation Edges

- `family_6` -> `family_6` | pairs=`16624` avg_score=`5.2102` support=`0.8886` lift=`4.5996` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_4` -> `family_4` | pairs=`5900` avg_score=`5.1794` support=`0.8477` lift=`10.671` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_5` -> `family_5` | pairs=`5210` avg_score=`5.1828` support=`0.818` lift=`11.9072` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_9` -> `family_1` | pairs=`2353` avg_score=`5.4451` support=`0.8033` lift=`1.2211` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_7` -> `family_1` | pairs=`1737` avg_score=`5.4468` support=`0.9983` lift=`1.5174` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_3` -> `family_1` | pairs=`1539` avg_score=`5.4445` support=`0.7777` lift=`1.1821` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_8` -> `family_6` | pairs=`852` avg_score=`5.4468` support=`0.3826` lift=`1.9803` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `noise` -> `family_1` | pairs=`719` avg_score=`5.3887` support=`1` lift=`1.52` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_2` -> `family_5` | pairs=`547` avg_score=`5.4451` support=`0.2148` lift=`3.1273` direction=`1` order=`1` echo_fields=`0` length_rules=`0`
- `family_0` -> `family_6` | pairs=`545` avg_score=`5.4156` support=`0.5767` lift=`2.9852` direction=`1` order=`1` echo_fields=`0` length_rules=`0`

## Final Ground Truth Evaluation

- Overall score: `0.515`
- Verdict: `partial`
- Matched message types: `11` of `11`
- Message type matching: accuracy=`1` precision=`1` recall=`1` f1=`1`
- Field boundary: accuracy=`0.3333` precision=`0.4151` recall=`0.6286` f1=`0.5`
- Field semantics: accuracy=`0` precision=`0` recall=`0` f1=`0`
- Relations: accuracy=`0.3889` precision=`0.3889` recall=`1` f1=`0.56`

## LLM Analysis

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `18`
- Strongest edges:
- `family_6` -> `family_6` | pairs=`16624` avg_score=`5.2102` support=`0.8886` lift=`4.5996` direction=`1` order=`1` flow=`unknown->unknown`
- `family_4` -> `family_4` | pairs=`5900` avg_score=`5.1794` support=`0.8477` lift=`10.671` direction=`1` order=`1` flow=`unknown->unknown`
- `family_5` -> `family_5` | pairs=`5210` avg_score=`5.1828` support=`0.818` lift=`11.9072` direction=`1` order=`1` flow=`unknown->unknown`
- `family_9` -> `family_1` | pairs=`2353` avg_score=`5.4451` support=`0.8033` lift=`1.2211` direction=`1` order=`1` flow=`unknown->unknown`
- `family_7` -> `family_1` | pairs=`1737` avg_score=`5.4468` support=`0.9983` lift=`1.5174` direction=`1` order=`1` flow=`unknown->unknown`
- `family_3` -> `family_1` | pairs=`1539` avg_score=`5.4445` support=`0.7777` lift=`1.1821` direction=`1` order=`1` flow=`unknown->unknown`
- `family_8` -> `family_6` | pairs=`852` avg_score=`5.4468` support=`0.3826` lift=`1.9803` direction=`1` order=`1` flow=`unknown->unknown`
- `noise` -> `family_1` | pairs=`719` avg_score=`5.3887` support=`1` lift=`1.52` direction=`1` order=`1` flow=`unknown->unknown`
- `family_2` -> `family_5` | pairs=`547` avg_score=`5.4451` support=`0.2148` lift=`3.1273` direction=`1` order=`1` flow=`unknown->unknown`
- `family_0` -> `family_6` | pairs=`545` avg_score=`5.4156` support=`0.5767` lift=`2.9852` direction=`1` order=`1` flow=`unknown->unknown`
- `family_2` -> `family_4` | pairs=`389` avg_score=`5.4443` support=`0.1528` lift=`1.9233` direction=`1` order=`1` flow=`unknown->unknown`
- `family_9` -> `family_4` | pairs=`337` avg_score=`5.4467` support=`0.1151` lift=`1.4483` direction=`1` order=`1` flow=`unknown->unknown`
- `family_3` -> `family_4` | pairs=`260` avg_score=`5.4394` support=`0.1314` lift=`1.6538` direction=`1` order=`1` flow=`unknown->unknown`
- `family_9` -> `family_5` | pairs=`239` avg_score=`5.4468` support=`0.0816` lift=`1.1877` direction=`1` order=`1` flow=`unknown->unknown`
- `family_3` -> `family_5` | pairs=`180` avg_score=`5.4467` support=`0.091` lift=`1.3239` direction=`1` order=`1` flow=`unknown->unknown`
- `family_1` -> `noise` | pairs=`44` avg_score=`5.4665` support=`0.0008` lift=`1.8222` direction=`1` order=`1` flow=`unknown->unknown`
- `family_6` -> `family_0` | pairs=`20` avg_score=`5.4668` support=`0.0011` lift=`4.8594` direction=`1` order=`1` flow=`unknown->unknown`
- `family_4` -> `family_3` | pairs=`2` avg_score=`5.4642` support=`0.0003` lift=`4.7893` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`1` length_rules=`1`

## Families

- Total families: `11`
- Families shown below: `11`

### family_1

- Role: `response`
- Messages: `120667`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_3`, `family_7`, `family_9`, `noise`
- Role hint: `response`
- Semantic confidence: `0.9931`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.314913`
- Candidate discriminator offset: `0` cardinality=`197` entropy=`7.562829` salience=`1.0` mutual_information=`0.109894` contrastive_separation=`1.0` confidence=`0.48592`
- Top discriminator candidates: offset `0` conf=`0.48592` salience=`1.0`, offset `9` conf=`0.313845` salience=`0.075267`, offset `7` conf=`0.303386` salience=`0.11326`
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

- Role: `response`
- Messages: `38027`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_6`, `family_8`
- Role hint: `response`
- Semantic confidence: `0.5199`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.485475` max=`3.027169` mean=`2.389712`
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.98095` salience=`0.11326` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.307632`
- Top discriminator candidates: offset `7` conf=`0.307632` salience=`0.11326`, offset `8` conf=`0.297921` salience=`0.117035`, offset `9` conf=`0.246409` salience=`0.075267`
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

- Role: `response`
- Messages: `14904`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_2`, `family_3`, `family_4`, `family_9`
- Role hint: `response`
- Semantic confidence: `0.5385`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`3.027169` mean=`2.379388`
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.941612` salience=`0.11326` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.307369`
- Top discriminator candidates: offset `7` conf=`0.307369` salience=`0.11326`, offset `8` conf=`0.296583` salience=`0.117035`, offset `9` conf=`0.288801` salience=`0.075267`
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
- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `2`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
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

- Role: `response`
- Messages: `13239`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_2`, `family_3`, `family_5`, `family_9`
- Role hint: `response`
- Semantic confidence: `0.5424`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.846439` max=`3.027169` mean=`2.402529`
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.93922` salience=`0.11326` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.307135`
- Top discriminator candidates: offset `7` conf=`0.307135` salience=`0.11326`, offset `8` conf=`0.297434` salience=`0.117035`, offset `9` conf=`0.274702` salience=`0.075267`
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

- Role: `request`
- Messages: `2933`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_1`, `family_4`, `family_5`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.020272`
- Candidate discriminator offset: `10` cardinality=`17` entropy=`3.463243` salience=`0.078001` mutual_information=`0.308526` contrastive_separation=`1.0` confidence=`0.275923`
- Top discriminator candidates: offset `10` conf=`0.275923` salience=`0.078001`, offset `9` conf=`0.273982` salience=`0.075267`, offset `8` conf=`0.258443` salience=`0.117035`
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

- Role: `request`
- Messages: `2548`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_4`, `family_5`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.02023`
- Candidate discriminator offset: `8` cardinality=`2` entropy=`0.016887` salience=`0.117035` mutual_information=`0.093933` contrastive_separation=`0.78125` confidence=`0.258374`
- Top discriminator candidates: offset `8` conf=`0.258374` salience=`0.117035`, offset `9` conf=`0.252454` salience=`0.075267`, offset `10` conf=`0.249181` salience=`0.078001`
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

- Role: `request`
- Messages: `2227`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ??`
- Related families: `family_6`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.550341` max=`3.027169` mean=`3.017568`
- Candidate discriminator offset: `9` cardinality=`7` entropy=`0.30222` salience=`0.075267` mutual_information=`0.184592` contrastive_separation=`0.859375` confidence=`0.269426`
- Top discriminator candidates: offset `9` conf=`0.269426` salience=`0.075267`, offset `10` conf=`0.248657` salience=`0.078001`
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

- Role: `request`
- Messages: `1985`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_1`, `family_4`, `family_5`
- Role hint: `request`
- Semantic confidence: `0.999`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.018191`
- Candidate discriminator offset: `10` cardinality=`9` entropy=`2.726791` salience=`0.078001` mutual_information=`0.308526` contrastive_separation=`0.890625` confidence=`0.3255`
- Top discriminator candidates: offset `10` conf=`0.3255` salience=`0.078001`, offset `9` conf=`0.288525` salience=`0.075267`, offset `8` conf=`0.258642` salience=`0.117035`
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

- Echoes request fields from family_4 with up to 1 strong offset matches.
- Response size is tied to request fields from family_4.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `1985` (`1.0`)
- Repeated n-gram instances: `2001`
- Top motifs: `0000`x3978, `000000`x1993, `000005`x1973, `000501`x1973, `010402`x1973

### family_7

- Role: `request`
- Messages: `1740`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_1`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.732159` max=`3.027169` mean=`3.023486`
- Candidate discriminator offset: `9` cardinality=`5` entropy=`0.02806` salience=`0.075267` mutual_information=`0.184592` contrastive_separation=`0.828125` confidence=`0.281083`
- Top discriminator candidates: offset `9` conf=`0.281083` salience=`0.075267`, offset `10` conf=`0.25461` salience=`0.078001`
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

- Role: `request`
- Messages: `967`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ?? 00`
- Related families: `family_6`
- Role hint: `request`
- Semantic confidence: `0.9646`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.40401` max=`3.027169` mean=`2.97951`
- Candidate discriminator offset: `10` cardinality=`17` entropy=`2.492763` salience=`0.078001` mutual_information=`0.308526` contrastive_separation=`1.0` confidence=`0.266634`
- Top discriminator candidates: offset `10` conf=`0.266634` salience=`0.078001`, offset `8` conf=`0.26101` salience=`0.117035`, offset `9` conf=`0.248296` salience=`0.075267`
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

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `967` (`1.0`)
- Repeated n-gram instances: `981`
- Top motifs: `0000`x1940, `000000`x973, `0005`x924, `0104`x924, `000005`x923

### noise

- Role: `request`
- Messages: `763`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 00`
- Related families: `family_1`
- Role hint: `request`
- Semantic confidence: `0.9423`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.450826` max=`3.027169` mean=`2.958612`
- Candidate discriminator offset: `8` cardinality=`2` entropy=`0.515799` salience=`0.117035` mutual_information=`0.093933` contrastive_separation=`0.78125` confidence=`0.2652`
- Top discriminator candidates: offset `8` conf=`0.2652` salience=`0.117035`, offset `10` conf=`0.243685` salience=`0.078001`, offset `9` conf=`0.22671` salience=`0.075267`
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

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `763` (`1.0`)
- Repeated n-gram instances: `797`
- Top motifs: `0000`x1542, `000000`x779, `000005`x675, `000501`x675, `010402`x675
