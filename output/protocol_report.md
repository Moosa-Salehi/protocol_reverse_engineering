# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **framing_global_summary**: {'common_header_ends': [{'header_end': 7, 'family_count': 11, 'family_ratio': 1.0}], 'field_type_counts': {'length': 33, 'transaction_or_counter': 20, 'constant': 10, 'discriminator': 5}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 11}
- **llm_refinement**: {'artifact_type': 'llm_refinement_summary', 'created_at': '2026-06-06T15:26:53.587998+00:00', 'input_patch_count': 0, 'accepted_patch_count': 0, 'rejected_patch_count': 0}

## Evaluation

- Messages: `200000` across `1` sessions
- Corpus assignment coverage: `1` with `11` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `11` of `11`
- Pair hypotheses: `100000` direction_unknown_ratio=`1`
- Relation edges: `18` echo_edges=`18` length_relation_edges=`1`
- Semantic coverage: `11` of `11` families ratio=`1`
- Top semantic labels: `constant`x25, `echoed_request_field`x23, `transaction_or_correlation_id`x21, `discriminator`x15, `payload`x11, `length`x9, `transaction_id`x7, `response_size_selector`x1
- Framing coverage: `11` of `11` families ratio=`1`
- Clustering diagnostics: warning_families=`5` split_candidates=`0` merge_candidates=`0`

### Clustering Diagnostic Warnings

- `family_1` | messages=`120667` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `family_6` | messages=`38027` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `family_4` | messages=`14904` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `family_5` | messages=`13239` split=`0.2` under_split=`0.2` over_split=`0` warnings=mixed length profile
- `noise` | messages=`763` split=`0` under_split=`0` over_split=`0` warnings=noise family

### Evaluation Top Relation Edges

- `family_6` -> `family_6` | pairs=`16624` avg_score=`5.2102` support=`0.8886` lift=`4.5996` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_4` -> `family_4` | pairs=`5900` avg_score=`5.1794` support=`0.8477` lift=`10.671` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_5` -> `family_5` | pairs=`5210` avg_score=`5.1828` support=`0.818` lift=`11.9072` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_9` -> `family_1` | pairs=`2353` avg_score=`5.4451` support=`0.8033` lift=`1.2211` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_7` -> `family_1` | pairs=`1737` avg_score=`5.4468` support=`0.9983` lift=`1.5174` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_3` -> `family_1` | pairs=`1539` avg_score=`5.4445` support=`0.7777` lift=`1.1821` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_8` -> `family_6` | pairs=`852` avg_score=`5.4468` support=`0.3826` lift=`1.9803` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `noise` -> `family_1` | pairs=`719` avg_score=`5.3887` support=`1` lift=`1.52` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_2` -> `family_5` | pairs=`547` avg_score=`5.4451` support=`0.2148` lift=`3.1273` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_6` | pairs=`545` avg_score=`5.4156` support=`0.5767` lift=`2.9852` direction=`1` order=`1` echo_fields=`10` length_rules=`0`

## Final Ground Truth Evaluation

- Overall score: `0.5164`
- Verdict: `partial`
- Matched message types: `10` of `11`
- Message type matching: accuracy=`0.8333` precision=`0.9091` recall=`0.9091` f1=`0.9091`
- Field boundary: accuracy=`0.3404` precision=`0.5714` recall=`0.4571` f1=`0.5079`
- Field semantics: accuracy=`0.0678` precision=`0.1429` recall=`0.1143` f1=`0.127`
- Relations: accuracy=`0.3529` precision=`0.375` recall=`0.8571` f1=`0.5217`

## LLM Analysis

- Model: `gpt-5.5`
- Prompt size: `31870` bytes, `31870` characters, estimated tokens=`7968`

# Protocol Specification

## Overview

The analyzed corpus contains 200,000 messages clustered into 11 protocol families. The protocol appears to be a binary, transaction-based request/response protocol with a common framing structure.

## Common Structure

A highly consistent 6-byte header is present across all major families:

- Bytes 0-1: transaction identifier or sequence counter
- Bytes 2-5: 4-byte big-endian length field

Request messages typically contain:

- Constant byte 0x01 at offset 6
- A 4-byte operation discriminator at offsets 7-10
- A 1-byte subtype or parameter field at offset 11

Response messages typically contain:

- A response discriminator at offsets 6-9
- A status or result byte near the end of the message
- Frequently a trailing constant byte 0x00

## Message Families

Four major request families (family_1, family_4, family_5, family_6) share nearly identical layouts but differ in discriminator values. Several response families (family_2, family_3, family_8, family_9) likewise share a common response layout.

## Correlation

The strongest transaction-correlation candidate is the 2-byte field at offset 0. Response families show nearly one unique value per message, which is consistent with transaction identifiers.

## Framing and Encoding

The protocol appears to use big-endian integer encoding and length-prefixed framing. All inferred fields are byte-aligned. No checksum or CRC was identified.

## Confidence Assessment

Header structure, length encoding, and family separation are strongly supported. Application semantics, operation meanings, and request/response pairing remain only partially resolved because semantic-labeling and relation-validation stages did not contribute additional validated findings.

## Family Relations

- Total inferred family edges: `16`
- Strongest edges:
- `family_6` -> `family_6` | pairs=`16624` avg_score=`5.2102` support=`0.8886` lift=`4.5996` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_4` -> `family_4` | pairs=`5900` avg_score=`5.1794` support=`0.8477` lift=`10.671` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_5` -> `family_5` | pairs=`5210` avg_score=`5.1828` support=`0.818` lift=`11.9072` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_9` -> `family_1` | pairs=`2353` avg_score=`5.4451` support=`0.8033` lift=`1.2211` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_1` | pairs=`1737` avg_score=`5.4468` support=`0.9983` lift=`1.5174` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_3` -> `family_1` | pairs=`1539` avg_score=`5.4445` support=`0.7777` lift=`1.1821` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_8` -> `family_6` | pairs=`852` avg_score=`5.4468` support=`0.3826` lift=`1.9803` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_2` -> `family_5` | pairs=`547` avg_score=`5.4451` support=`0.2148` lift=`3.1273` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_0` -> `family_6` | pairs=`545` avg_score=`5.4156` support=`0.5767` lift=`2.9852` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_2` -> `family_4` | pairs=`389` avg_score=`5.4443` support=`0.1528` lift=`1.9233` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_9` -> `family_4` | pairs=`337` avg_score=`5.4467` support=`0.1151` lift=`1.4483` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_3` -> `family_4` | pairs=`260` avg_score=`5.4394` support=`0.1314` lift=`1.6538` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_9` -> `family_5` | pairs=`239` avg_score=`5.4468` support=`0.0816` lift=`1.1877` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_3` -> `family_5` | pairs=`180` avg_score=`5.4467` support=`0.091` lift=`1.3239` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_6` -> `family_0` | pairs=`20` avg_score=`5.4668` support=`0.0011` lift=`4.8594` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_4` -> `family_3` | pairs=`2` avg_score=`5.4642` support=`0.0003` lift=`4.7893` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`1` length_rules=`1`

## Families

- Total families: `11`
- Families shown below: `11`

### family_1

- Role: `response`
- Messages: `120667`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_3`, `family_7`, `family_9`
- Role hint: `response`
- Semantic confidence: `0.9931`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.314913`
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.841241` salience=`0.749936` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.494389`
- Top discriminator candidates: offset `7` conf=`0.494389` salience=`0.749936`, offset `0` conf=`0.48592` salience=`1.0`, offset `9` conf=`0.380225` salience=`0.296533`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.608855`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6535`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.6868927499999999`
- bytes `11`..`11` | kind=`variable` confidence=`0.7786`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`uint8` confidence=`0.9999`
- bytes `7`..`10` | type=`uint32` confidence=`0.9998`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`6` body_start=`6` confidence=`0.9905` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `11`..`11` | label=`discriminator` confidence=`0.9999`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9998`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Echoes request fields from family_3 with up to 10 strong offset matches.
- Echoes request fields from family_7 with up to 10 strong offset matches.
- Echoes request fields from family_9 with up to 10 strong offset matches.
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
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.98095` salience=`0.749936` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.498635`
- Top discriminator candidates: offset `7` conf=`0.498635` salience=`0.749936`, offset `8` conf=`0.369271` salience=`0.354868`, offset `9` conf=`0.312789` salience=`0.296533`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6103749999999999`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6521`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.6774165`
- bytes `11`..`11` | kind=`variable` confidence=`0.7738`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`uint8` confidence=`0.9997`
- bytes `7`..`10` | type=`uint32` confidence=`0.9986`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9986`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Echoes request fields from family_6 with up to 10 strong offset matches.
- Echoes request fields from family_8 with up to 10 strong offset matches.
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
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.941612` salience=`0.749936` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.498371`
- Top discriminator candidates: offset `7` conf=`0.498371` salience=`0.749936`, offset `8` conf=`0.367933` salience=`0.354868`, offset `9` conf=`0.355181` salience=`0.296533`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.636405`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6524`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.6802142499999999`
- bytes `11`..`11` | kind=`variable` confidence=`0.7778`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`uint8` confidence=`0.9996`
- bytes `7`..`10` | type=`uint32` confidence=`0.9975`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9975`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Echoes request fields from family_2 with up to 10 strong offset matches.
- Echoes request fields from family_3 with up to 10 strong offset matches.
- Echoes request fields from family_4 with up to 10 strong offset matches.
- Echoes request fields from family_9 with up to 10 strong offset matches.
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
- Candidate discriminator offset: `7` cardinality=`5` entropy=`1.93922` salience=`0.749936` mutual_information=`0.093383` contrastive_separation=`0.828125` confidence=`0.498138`
- Top discriminator candidates: offset `7` conf=`0.498138` salience=`0.749936`, offset `8` conf=`0.368784` salience=`0.354868`, offset `9` conf=`0.341082` salience=`0.296533`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.631655`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6522`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.67858975`
- bytes `11`..`11` | kind=`variable` confidence=`0.7765`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`uint8` confidence=`0.9997`
- bytes `7`..`10` | type=`uint32` confidence=`0.9974`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9974`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Echoes request fields from family_2 with up to 10 strong offset matches.
- Echoes request fields from family_3 with up to 10 strong offset matches.
- Echoes request fields from family_5 with up to 10 strong offset matches.
- Echoes request fields from family_9 with up to 10 strong offset matches.
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
- Candidate discriminator offset: `10` cardinality=`17` entropy=`3.463243` salience=`0.347193` mutual_information=`0.308526` contrastive_separation=`1.0` confidence=`0.356681`
- Top discriminator candidates: offset `10` conf=`0.356681` salience=`0.347193`, offset `9` conf=`0.340362` salience=`0.296533`, offset `8` conf=`0.329793` salience=`0.354868`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.638115`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6686`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.7069899999999999`
- bytes `11`..`11` | kind=`constant` confidence=`0.8654`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`10` | type=`uint32` confidence=`0.9935`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.95` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9935`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`

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
- Candidate discriminator offset: `10` cardinality=`23` entropy=`3.122259` salience=`0.347193` mutual_information=`0.308526` contrastive_separation=`1.0` confidence=`0.329939`
- Top discriminator candidates: offset `10` conf=`0.329939` salience=`0.347193`, offset `8` conf=`0.329724` salience=`0.354868`, offset `9` conf=`0.318834` salience=`0.296533`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.642485`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6688`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.7153499999999999`
- bytes `11`..`11` | kind=`constant` confidence=`0.8652`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `7`..`10` | type=`uint32` confidence=`0.9898`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.95` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9898`
- bytes `0`..`1` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`

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
- Candidate discriminator offset: `9` cardinality=`7` entropy=`0.30222` salience=`0.296533` mutual_information=`0.184592` contrastive_separation=`0.859375` confidence=`0.335805`
- Top discriminator candidates: offset `9` conf=`0.335805` salience=`0.296533`, offset `10` conf=`0.329415` salience=`0.347193`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6476149999999999`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`10` | kind=`variable` confidence=`0.71877`

#### Field Hypotheses

- bytes `7`..`10` | type=`uint32` confidence=`0.9901`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_be` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9901`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `7`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Detected common protocol pattern: transaction ID, discriminator

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
- Candidate discriminator offset: `10` cardinality=`9` entropy=`2.726791` salience=`0.347193` mutual_information=`0.308526` contrastive_separation=`0.890625` confidence=`0.406257`
- Top discriminator candidates: offset `10` conf=`0.406257` salience=`0.347193`, offset `9` conf=`0.354905` salience=`0.296533`, offset `8` conf=`0.329992` salience=`0.354868`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6524599999999999`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6684`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.722285`
- bytes `11`..`11` | kind=`constant` confidence=`0.8658`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`10` | type=`uint32` confidence=`0.995`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.95` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`10` | label=`discriminator` confidence=`0.995`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`

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
- Candidate discriminator offset: `9` cardinality=`5` entropy=`0.02806` salience=`0.296533` mutual_information=`0.184592` contrastive_separation=`0.828125` confidence=`0.347463`
- Top discriminator candidates: offset `9` conf=`0.347463` salience=`0.296533`, offset `10` conf=`0.335368` salience=`0.347193`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.660725`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`10` | kind=`variable` confidence=`0.716965`

#### Field Hypotheses

- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`10` | type=`uint32` confidence=`0.9891`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.95` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`10` | label=`discriminator` confidence=`0.9891`
- bytes `0`..`1` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `7`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Detected common protocol pattern: transaction ID, discriminator

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
- Candidate discriminator offset: `10` cardinality=`17` entropy=`2.492763` salience=`0.347193` mutual_information=`0.308526` contrastive_separation=`1.0` confidence=`0.347391`
- Top discriminator candidates: offset `10` conf=`0.347391` salience=`0.347193`, offset `8` conf=`0.33236` salience=`0.354868`, offset `9` conf=`0.314676` salience=`0.296533`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.69977`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6663`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.73169`
- bytes `11`..`11` | kind=`constant` confidence=`0.8711`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `7`..`10` | type=`uint32` confidence=`0.9793`
- bytes `0`..`1` | type=`uint16_be` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `7`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_6 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `967` (`1.0`)
- Repeated n-gram instances: `981`
- Top motifs: `0000`x1940, `000000`x973, `0005`x924, `0104`x924, `000005`x923

### noise

- Role: `request`
- Messages: `763`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 00`
- Role hint: `request`
- Semantic confidence: `0.9423`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.450826` max=`3.027169` mean=`2.958612`
- Candidate discriminator offset: `8` cardinality=`2` entropy=`0.515799` salience=`0.354868` mutual_information=`0.093933` contrastive_separation=`0.78125` confidence=`0.336549`
- Top discriminator candidates: offset `8` conf=`0.336549` salience=`0.354868`, offset `10` conf=`0.324443` salience=`0.347193`, offset `9` conf=`0.29309` salience=`0.296533`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.7014799999999999`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6637`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`10` | kind=`variable` confidence=`0.6955567500000001`
- bytes `11`..`11` | kind=`constant` confidence=`0.8806`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_be` confidence=`0.9423` endian=`big`
- bytes `7`..`10` | type=`uint32` confidence=`0.9109`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `7`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `7`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `763` (`1.0`)
- Repeated n-gram instances: `797`
- Top motifs: `0000`x1542, `000000`x779, `000005`x675, `000501`x675, `010402`x675
