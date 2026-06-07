# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **framing_global_summary**: {'common_header_ends': [{'header_end': 7, 'family_count': 12, 'family_ratio': 1.0}], 'field_type_counts': {'length': 36, 'transaction_or_counter': 22, 'constant': 10, 'discriminator': 4}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 12}
- **llm_refinement**: {'artifact_type': 'llm_refinement_summary', 'created_at': '2026-06-07T17:29:35.691815+00:00', 'input_patch_count': 4, 'accepted_patch_count': 1, 'rejected_patch_count': 3}

## Evaluation

- Messages: `200000` across `1` sessions
- Corpus assignment coverage: `1` with `12` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `12` of `12`
- Pair hypotheses: `99999` direction_unknown_ratio=`1`
- Relation edges: `18` echo_edges=`18` length_relation_edges=`0`
- Semantic coverage: `12` of `12` families ratio=`1`
- Top semantic labels: `discriminator`x29, `constant`x27, `echoed_request_field`x16, `transaction_or_correlation_id`x16, `length`x16, `transaction_id`x8
- Framing coverage: `12` of `12` families ratio=`1`
- Clustering diagnostics: warning_families=`11` split_candidates=`2` merge_candidates=`18`

### Clustering Diagnostic Warnings

- `family_0` | messages=`143751` split=`0.7` under_split=`0.7` over_split=`0` warnings=high latent dispersion, low latent silhouette, mixed length profile
- `family_3` | messages=`6547` split=`0.5` under_split=`0.5` over_split=`0.1` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_6` | messages=`19786` split=`0.4` under_split=`0.4` over_split=`0` warnings=low latent silhouette, mixed length profile
- `family_1` | messages=`2604` split=`0.3` under_split=`0.3` over_split=`0.1` warnings=high latent dispersion, possible over-split merge candidate
- `family_10` | messages=`1246` split=`0.2` under_split=`0.2` over_split=`0.4606` warnings=low latent silhouette, possible over-split merge candidate
- `family_8` | messages=`1725` split=`0.2` under_split=`0.2` over_split=`0.3242` warnings=low latent silhouette, possible over-split merge candidate
- `family_7` | messages=`11094` split=`0.2` under_split=`0.2` over_split=`0.2536` warnings=mixed length profile, possible over-split merge candidate
- `family_9` | messages=`1371` split=`0` under_split=`0` over_split=`0.4606` warnings=possible over-split merge candidate
- `family_5` | messages=`8320` split=`0` under_split=`0` over_split=`0.2606` warnings=possible over-split merge candidate
- `family_4` | messages=`925` split=`0` under_split=`0` over_split=`0.2606` warnings=possible over-split merge candidate

### Clustering Merge Candidates

- `family_10` -> `family_9` distance=`0.4431` score=`0.4606`
- `family_9` -> `family_10` distance=`0.4431` score=`0.4606`
- `family_9` -> `family_8` distance=`0.5551` score=`0.3242`
- `family_8` -> `family_9` distance=`0.5551` score=`0.3242`
- `family_5` -> `family_4` distance=`0.6075` score=`0.2606`
- `family_4` -> `family_5` distance=`0.6075` score=`0.2606`
- `family_8` -> `family_7` distance=`0.6131` score=`0.2536`
- `family_7` -> `family_8` distance=`0.6131` score=`0.2536`
- `family_9` -> `family_7` distance=`0.6274` score=`0.2363`
- `family_7` -> `family_9` distance=`0.6274` score=`0.2363`

### Evaluation Top Relation Edges

- `family_6` -> `family_6` | pairs=`8157` avg_score=`6.9457` support=`0.795` lift=`8.3458` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_3` | pairs=`6524` avg_score=`6.9674` support=`0.0847` lift=`1.2953` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_7` -> `family_7` | pairs=`3119` avg_score=`6.9479` support=`0.4531` lift=`10.7609` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_5` -> `family_5` | pairs=`1962` avg_score=`6.951` support=`0.3418` lift=`13.2512` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_8` | pairs=`1725` avg_score=`6.9676` support=`0.0224` lift=`1.2981` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_6` -> `family_2` | pairs=`1084` avg_score=`6.9676` support=`0.1057` lift=`6.4343` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_9` | pairs=`1074` avg_score=`6.9675` support=`0.0139` lift=`1.0169` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `noise` | pairs=`877` avg_score=`6.9675` support=`0.0114` lift=`1.2361` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_7` -> `family_6` | pairs=`843` avg_score=`6.9674` support=`0.1225` lift=`1.2857` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_5` -> `family_1` | pairs=`697` avg_score=`6.9676` support=`0.1214` lift=`4.6659` direction=`1` order=`1` echo_fields=`10` length_rules=`0`

## Final Ground Truth Evaluation

- Overall score: `0.6721`
- Verdict: `partial`
- Matched message types: `11` of `11`
- Message type matching: accuracy=`0.9167` precision=`0.9167` recall=`1` f1=`0.9565`
- Field boundary: accuracy=`0.5` precision=`0.5909` recall=`0.7647` f1=`0.6667`
- Field semantics: accuracy=`0.2581` precision=`0.3636` recall=`0.4706` f1=`0.4103`
- Relations: accuracy=`0.2105` precision=`0.2353` recall=`0.6667` f1=`0.3478`

## LLM Analysis

- Model: `qwen/qwen3.5-397b-a17b`
- Prompt size: `35901` bytes, `35901` characters, estimated tokens=`8976`

# Protocol Specification Synthesis

## Overview
This is a binary, request-response protocol operating over a client-server model. Analysis of 200,000 messages reveals 12 distinct message families. The protocol utilizes a fixed 7-byte header followed by variable payloads.

## Message Structure
- **Header**: 7 bytes.
  - Bytes 0-1: Sequence/Transaction ID (Mixed Endianness observed).
  - Bytes 2-3: Constant `0x0000`.
  - Bytes 4-5: Length (Big-Endian).
  - Byte 6: Constant `0x01`.
- **Payload**: Starts at offset 7. Commonly contains 32-bit addresses (Big-Endian) or function-specific data.

## Key Interactions
- **Primary Read Pattern**: `family_3` (Request) pairs strongly with `family_0` (Response). The request contains a 32-bit address and a little-endian sequence number. The response echoes the ID and returns status/data.
- **Status/Check Pattern**: `family_7` appears to be a self-contained transaction with explicit function codes and a checksum.
- **Self-Correlated Families**: Several families (6, 5, 7) show high rates of self-correlation, suggesting they may be polling mechanisms or stateless queries where the request and response share the same structural template.

## Conventions
- **Endianness**: The protocol exhibits mixed endianness. Length fields are consistently Big-Endian, while request sequence numbers often appear Little-Endian.
- **Reliability**: Transaction IDs are used to correlate requests and responses. 
- **Integrity**: At least one message type (`family_7`) implements an explicit checksum.

## Family Relations

- Total inferred family edges: `17`
- Strongest edges:
- `family_6` -> `family_6` | pairs=`8157` avg_score=`6.9457` support=`0.795` lift=`8.3458` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_7` | pairs=`3119` avg_score=`6.9479` support=`0.4531` lift=`10.7609` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_5` -> `family_5` | pairs=`1962` avg_score=`6.951` support=`0.3418` lift=`13.2512` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_0` -> `family_8` | pairs=`1725` avg_score=`6.9676` support=`0.0224` lift=`1.2981` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_6` -> `family_2` | pairs=`1084` avg_score=`6.9676` support=`0.1057` lift=`6.4343` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_0` -> `family_9` | pairs=`1074` avg_score=`6.9675` support=`0.0139` lift=`1.0169` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_0` -> `noise` | pairs=`877` avg_score=`6.9675` support=`0.0114` lift=`1.2361` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_6` | pairs=`843` avg_score=`6.9674` support=`0.1225` lift=`1.2857` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_5` -> `family_1` | pairs=`697` avg_score=`6.9676` support=`0.1214` lift=`4.6659` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_5` -> `family_4` | pairs=`378` avg_score=`6.9676` support=`0.0658` lift=`7.118` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_10` | pairs=`311` avg_score=`6.9673` support=`0.0452` lift=`3.6263` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_6` -> `family_10` | pairs=`176` avg_score=`6.9675` support=`0.0172` lift=`1.3767` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_9` | pairs=`156` avg_score=`6.9675` support=`0.0227` lift=`1.6531` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_6` -> `family_9` | pairs=`141` avg_score=`6.9674` support=`0.0137` lift=`1.0024` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_2` | pairs=`137` avg_score=`6.9674` support=`0.0199` lift=`1.2122` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `noise` -> `noise` | pairs=`44` avg_score=`6.9969` support=`1` lift=`108.5765` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_2` -> `family_2` | pairs=`23` avg_score=`6.9967` support=`1` lift=`60.9007` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`

## Families

- Total families: `12`
- Families shown below: `12`

### family_0

- Role: `request`
- Messages: `143751`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_3`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.314798`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.361483` salience=`1.0` mutual_information=`0.143445` contrastive_separation=`0.796875` confidence=`0.573172`
- Top discriminator candidates: offset `8` conf=`0.573172` salience=`1.0`, offset `9` conf=`0.561289` salience=`0.869092`, offset `7` conf=`0.497819` salience=`0.739632`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.608665`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6534`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`11` | kind=`variable` confidence=`0.68580975`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`1.0`
- bytes `8`..`11` | type=`uint32` confidence=`0.9999`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`6` body_start=`6` confidence=`0.9903` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`11` | label=`discriminator` confidence=`0.9999`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `7`..`7` | label=`discriminator` confidence=`0.95`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `143751` (`1.0`)
- Repeated n-gram instances: `181239`
- Top motifs: `0000`x288499, `000000`x144367, `0101`x98475, `0100`x81119, `0006`x77798

### family_6

- Role: `request`
- Messages: `19786`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_10`, `family_2`, `family_6`, `family_7`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.515`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.485475` max=`3.027169` mean=`2.35261`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.465807` salience=`1.0` mutual_information=`0.143445` contrastive_separation=`0.796875` confidence=`0.57416`
- Top discriminator candidates: offset `8` conf=`0.57416` salience=`1.0`, offset `9` conf=`0.53575` salience=`0.869092`, offset `7` conf=`0.499822` salience=`0.739632`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.61256`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6523`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`11` | kind=`variable` confidence=`0.6823802499999999`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.9997`
- bytes `8`..`11` | type=`uint32` confidence=`0.9994`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `7`..`7` | label=`discriminator` confidence=`0.95`
- bytes `8`..`11` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Echoes request fields from family_6 with up to 10 strong offset matches.
- Echoes request fields from family_7 with up to 10 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `19786` (`1.0`)
- Repeated n-gram instances: `24152`
- Top motifs: `0000`x39700, `000000`x19866, `0101`x12000, `0006`x10525, `0601`x10292

### family_7

- Role: `request`
- Messages: `11094`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_10`, `family_2`, `family_6`, `family_7`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5941`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.896241` max=`3.027169` mean=`2.382777`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.322557` salience=`1.0` mutual_information=`0.143445` contrastive_separation=`0.796875` confidence=`0.56769`
- Top discriminator candidates: offset `8` conf=`0.56769` salience=`1.0`, offset `9` conf=`0.560604` salience=`0.869092`, offset `7` conf=`0.500557` salience=`0.739632`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.619875`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6539`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`11` | kind=`variable` confidence=`0.5980249999999999`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.9995`
- bytes `8`..`11` | type=`uint32` confidence=`0.9993`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `7`..`7` | label=`discriminator` confidence=`0.95`
- bytes `8`..`11` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Echoes request fields from family_7 with up to 10 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `11094` (`1.0`)
- Repeated n-gram instances: `12693`
- Top motifs: `0000`x22230, `000000`x11099, `000006`x6966, `000601`x6966, `0006`x6966

### family_5

- Role: `request`
- Messages: `8320`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_1`, `family_4`, `family_5`
- Role hint: `request`
- Semantic confidence: `0.6075`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.846439` max=`3.027169` mean=`2.409528`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.193847` salience=`1.0` mutual_information=`0.143445` contrastive_separation=`0.796875` confidence=`0.563956`
- Top discriminator candidates: offset `8` conf=`0.563956` salience=`1.0`, offset `9` conf=`0.558292` salience=`0.869092`, offset `7` conf=`0.501868` salience=`0.739632`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.62339`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6554`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`11` | kind=`variable` confidence=`0.6971812499999999`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `8`..`11` | type=`uint32` confidence=`0.9995`
- bytes `7`..`7` | type=`uint8` confidence=`0.9994`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `7`..`7` | label=`discriminator` confidence=`0.95`
- bytes `8`..`11` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Echoes request fields from family_5 with up to 10 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `8320` (`1.0`)
- Repeated n-gram instances: `8978`
- Top motifs: `0000`x16642, `000000`x8320, `000006`x5742, `000601`x5742, `0006`x5742

### family_3

- Role: `response`
- Messages: `6547`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_0`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.020608`
- Candidate discriminator offset: `9` cardinality=`9` entropy=`0.04671` salience=`0.869092` mutual_information=`0.225617` contrastive_separation=`0.890625` confidence=`0.500427`
- Top discriminator candidates: offset `9` conf=`0.500427` salience=`0.869092`, offset `10` conf=`0.399166` salience=`0.543579`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6215849999999999`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6685`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.6682`
- bytes `10`..`10` | kind=`variable` confidence=`0.7229`
- bytes `11`..`11` | kind=`constant` confidence=`0.8654`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.9997`
- bytes `8`..`9` | type=`uint16` confidence=`0.9986`
- bytes `10`..`10` | type=`uint8` confidence=`0.995`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.95` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `7`..`7` | label=`discriminator` confidence=`0.9997`
- bytes `8`..`9` | label=`discriminator` confidence=`0.9986`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `6547` (`1.0`)
- Repeated n-gram instances: `6591`
- Top motifs: `0000`x13116, `000000`x6569, `000005`x6529, `000501`x6529, `010402`x6529

### family_1

- Role: `response`
- Messages: `2604`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_5`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.02003`
- Candidate discriminator offset: `9` cardinality=`8` entropy=`0.05094` salience=`0.869092` mutual_information=`0.225617` contrastive_separation=`0.875` confidence=`0.507629`
- Top discriminator candidates: offset `9` conf=`0.507629` salience=`0.869092`, offset `10` conf=`0.396137` salience=`0.543579`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.64182`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6688`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.6687`
- bytes `10`..`10` | kind=`variable` confidence=`0.7506`
- bytes `11`..`11` | kind=`constant` confidence=`0.8652`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.9992`
- bytes `8`..`9` | type=`uint16` confidence=`0.9969`
- bytes `10`..`10` | type=`uint8` confidence=`0.9916`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.95` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `7`..`7` | label=`discriminator` confidence=`0.9992`
- bytes `8`..`9` | label=`discriminator` confidence=`0.9969`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_5 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `2604` (`1.0`)
- Repeated n-gram instances: `2624`
- Top motifs: `0000`x5218, `000000`x2614, `000005`x2600, `000501`x2600, `010402`x2600

### family_8

- Role: `response`
- Messages: `1725`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_0`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.025483`
- Candidate discriminator offset: `9` cardinality=`7` entropy=`0.048316` salience=`0.869092` mutual_information=`0.225617` contrastive_separation=`0.859375` confidence=`0.514807`
- Top discriminator candidates: offset `9` conf=`0.514807` salience=`0.869092`, offset `10` conf=`0.394137` salience=`0.543579`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.65911`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`9` | kind=`variable` confidence=`0.669`
- bytes `10`..`10` | kind=`variable` confidence=`0.7551`

#### Field Hypotheses

- bytes `8`..`9` | type=`uint16` confidence=`0.9959`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `10`..`10` | type=`uint8` confidence=`0.9878`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.891` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `8`..`9` | label=`discriminator` confidence=`0.9959`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `1725` (`1.0`)
- Repeated n-gram instances: `1725`
- Top motifs: `0000`x3450, `000000`x1725, `000005`x1725, `000501`x1725, `010402`x1725

### family_2

- Role: `response`
- Messages: `1665`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ?? 00`
- Related families: `family_2`, `family_6`, `family_7`
- Role hint: `response`
- Semantic confidence: `0.9818`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.40401` max=`3.027169` mean=`2.994328`
- Candidate discriminator offset: `9` cardinality=`12` entropy=`0.597283` salience=`0.869092` mutual_information=`0.225617` contrastive_separation=`0.9375` confidence=`0.484031`
- Top discriminator candidates: offset `9` conf=`0.484031` salience=`0.869092`, offset `10` conf=`0.392405` salience=`0.543579`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6611049999999999`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.667`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.6615`
- bytes `10`..`10` | kind=`variable` confidence=`0.7529`
- bytes `11`..`11` | kind=`constant` confidence=`0.8687`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.9988`
- bytes `8`..`9` | type=`uint16` confidence=`0.9928`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `10`..`10` | type=`uint8` confidence=`0.985`
- bytes `0`..`1` | type=`uint16_be` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `7`..`7` | label=`discriminator` confidence=`0.9988`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Echoes request fields from family_2 with up to 10 strong offset matches.
- Echoes request fields from family_6 with up to 10 strong offset matches.
- Echoes request fields from family_7 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `1665` (`1.0`)
- Repeated n-gram instances: `1675`
- Top motifs: `0000`x3334, `000000`x1669, `0005`x1620, `0104`x1620, `000005`x1619

### family_9

- Role: `response`
- Messages: `1371`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ??`
- Related families: `family_0`, `family_6`, `family_7`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.222192` max=`3.027169` mean=`2.994004`
- Candidate discriminator offset: `9` cardinality=`10` entropy=`0.504003` salience=`0.869092` mutual_information=`0.225617` contrastive_separation=`0.90625` confidence=`0.49764`
- Top discriminator candidates: offset `9` conf=`0.49764` salience=`0.869092`, offset `10` conf=`0.397135` salience=`0.543579`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6678499999999999`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.6645`
- bytes `10`..`10` | kind=`variable` confidence=`0.7379`

#### Field Hypotheses

- bytes `7`..`7` | type=`uint8` confidence=`0.9985`
- bytes `8`..`9` | type=`uint16` confidence=`0.9927`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `10`..`10` | type=`uint8` confidence=`0.9745`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.95` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `7`..`7` | label=`discriminator` confidence=`0.9985`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`length` confidence=`0.95`
- bytes `8`..`9` | label=`discriminator` confidence=`0.95`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Echoes request fields from family_6 with up to 10 strong offset matches.
- Echoes request fields from family_7 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `1371` (`1.0`)
- Repeated n-gram instances: `1423`
- Top motifs: `0000`x2767, `000000`x1396, `000005`x1371, `000501`x1371, `0005`x1371

### family_10

- Role: `response`
- Messages: `1246`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_6`, `family_7`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.010826`
- Candidate discriminator offset: `9` cardinality=`9` entropy=`0.098646` salience=`0.869092` mutual_information=`0.225617` contrastive_separation=`0.890625` confidence=`0.500718`
- Top discriminator candidates: offset `9` conf=`0.500718` salience=`0.869092`, offset `10` conf=`0.391801` salience=`0.543579`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.681625`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`9` | kind=`variable` confidence=`0.6691`
- bytes `10`..`10` | kind=`variable` confidence=`0.7536`

#### Field Hypotheses

- bytes `8`..`9` | type=`uint16` confidence=`0.9928`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `10`..`10` | type=`uint8` confidence=`0.9815`
- bytes `0`..`1` | type=`uint16_be` confidence=`0.95` endian=`big`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`9` | label=`discriminator` confidence=`0.95`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_6 with up to 10 strong offset matches.
- Echoes request fields from family_7 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `1246` (`1.0`)
- Repeated n-gram instances: `1246`
- Top motifs: `0000`x2492, `000000`x1246, `000005`x1246, `000501`x1246, `010402`x1246

### noise

- Role: `response`
- Messages: `966`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 00`
- Related families: `family_0`, `noise`
- Role hint: `response`
- Semantic confidence: `0.9544`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.450826` max=`3.027169` mean=`2.959492`
- Candidate discriminator offset: `9` cardinality=`17` entropy=`1.215276` salience=`0.869092` mutual_information=`0.225617` contrastive_separation=`1.0` confidence=`0.452679`
- Top discriminator candidates: offset `9` conf=`0.452679` salience=`0.869092`, offset `10` conf=`0.392672` salience=`0.543579`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.68552`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6644`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.6537`
- bytes `10`..`10` | kind=`variable` confidence=`0.7568`
- bytes `11`..`11` | kind=`constant` confidence=`0.8773`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.9979`
- bytes `2`..`3` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `8`..`9` | type=`uint16` confidence=`0.9824`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.95` endian=`little`
- bytes `10`..`10` | type=`uint8` confidence=`0.9358`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `7`..`7` | label=`discriminator` confidence=`0.9979`
- bytes `2`..`3` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `2`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Echoes request fields from noise with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `966` (`1.0`)
- Repeated n-gram instances: `1008`
- Top motifs: `0000`x1952, `000000`x986, `000005`x878, `000501`x878, `010402`x878

### family_4

- Role: `response`
- Messages: `925`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_5`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.732159` max=`3.027169` mean=`3.023386`
- Candidate discriminator offset: `9` cardinality=`5` entropy=`0.058876` salience=`0.869092` mutual_information=`0.225617` contrastive_separation=`0.828125` confidence=`0.529263`
- Top discriminator candidates: offset `9` conf=`0.529263` salience=`0.869092`, offset `10` conf=`0.463149` salience=`0.543579`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.69198`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`9` | kind=`variable` confidence=`0.6693`
- bytes `10`..`10` | kind=`variable` confidence=`0.7767`

#### Field Hypotheses

- bytes `8`..`9` | type=`uint16` confidence=`0.9946`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `10`..`10` | type=`uint8` confidence=`0.9892`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.95` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `8`..`9` | label=`discriminator` confidence=`0.9946`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_5 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `925` (`1.0`)
- Repeated n-gram instances: `929`
- Top motifs: `0000`x1852, `000000`x927, `000005`x925, `000501`x925, `010402`x925
