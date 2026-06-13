# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **framing_global_summary**: {'common_header_ends': [{'header_end': 7, 'family_count': 10, 'family_ratio': 1.0}], 'field_type_counts': {'length': 30, 'transaction_or_counter': 20}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 10}
- **llm_refinement**: {'artifact_type': 'llm_refinement_summary', 'created_at': '2026-06-13T17:24:16.139626+00:00', 'input_patch_count': 4, 'accepted_patch_count': 1, 'rejected_patch_count': 3}

## Evaluation

- Messages: `200000` across `1` sessions
- Corpus assignment coverage: `1` with `10` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `10` of `10`
- Pair hypotheses: `99999` direction_unknown_ratio=`1`
- Relation edges: `6` echo_edges=`6` length_relation_edges=`0`
- Semantic coverage: `10` of `10` families ratio=`1`
- Top semantic labels: `constant`x25, `echoed_request_field`x10, `transaction_id`x8, `length`x5, `transaction_or_correlation_id`x4, `payload`x3, `address_like`x3, `discriminator`x1
- Framing coverage: `10` of `10` families ratio=`1`
- Clustering diagnostics: warning_families=`9` split_candidates=`2` merge_candidates=`24`

### Clustering Diagnostic Warnings

- `family_0` | messages=`39887` split=`0.5` under_split=`0.5` over_split=`0.7488` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_6` | messages=`19944` split=`0.5` under_split=`0.5` over_split=`0` warnings=high latent dispersion, low latent silhouette
- `family_9` | messages=`406` split=`0.3` under_split=`0.3` over_split=`0` warnings=high latent dispersion
- `family_5` | messages=`19944` split=`0.2` under_split=`0.2` over_split=`0.8341` warnings=low latent silhouette, possible over-split merge candidate
- `family_7` | messages=`19943` split=`0.2` under_split=`0.2` over_split=`0.8341` warnings=low latent silhouette, possible over-split merge candidate
- `family_3` | messages=`19944` split=`0.2` under_split=`0.2` over_split=`0.8233` warnings=low latent silhouette, possible over-split merge candidate
- `family_2` | messages=`19944` split=`0.2` under_split=`0.2` over_split=`0.7488` warnings=low latent silhouette, possible over-split merge candidate
- `family_1` | messages=`39888` split=`0.2` under_split=`0.2` over_split=`0.3166` warnings=low latent silhouette, possible over-split merge candidate
- `family_4` | messages=`19944` split=`0.2` under_split=`0.2` over_split=`0` warnings=low latent silhouette

### Clustering Merge Candidates

- `family_5` -> `family_7` distance=`0.0299` score=`0.8341`
- `family_7` -> `family_5` distance=`0.0299` score=`0.8341`
- `family_5` -> `family_3` distance=`0.0319` score=`0.8233`
- `family_3` -> `family_5` distance=`0.0319` score=`0.8233`
- `family_2` -> `family_0` distance=`0.0453` score=`0.7488`
- `family_0` -> `family_2` distance=`0.0453` score=`0.7488`
- `family_3` -> `family_7` distance=`0.0616` score=`0.6581`
- `family_7` -> `family_3` distance=`0.0616` score=`0.6581`
- `family_3` -> `family_1` distance=`0.1232` score=`0.3166`
- `family_1` -> `family_3` distance=`0.1232` score=`0.3166`

### Evaluation Top Relation Edges

- `family_1` -> `family_0` | pairs=`39887` avg_score=`6.9362` support=`1` lift=`2.5071` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_5` -> `family_4` | pairs=`19944` avg_score=`6.9675` support=`1` lift=`5.014` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_3` -> `family_2` | pairs=`19944` avg_score=`6.935` support=`1` lift=`5.014` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_7` -> `family_6` | pairs=`19943` avg_score=`6.9675` support=`1` lift=`5.0142` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_9` -> `family_9` | pairs=`203` avg_score=`6.9976` support=`1` lift=`492.6059` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_8` -> `family_8` | pairs=`78` avg_score=`6.9968` support=`1` lift=`1282.0385` direction=`1` order=`1` echo_fields=`10` length_rules=`0`

## Final Ground Truth Evaluation

- Overall score: `0.7479`
- Verdict: `partial`
- Matched message types: `11` of `11`
- Message type matching: accuracy=`1` precision=`1` recall=`1` f1=`1`
- Field boundary: accuracy=`0.5405` precision=`0.8696` recall=`0.5882` f1=`0.7018`
- Field semantics: accuracy=`0.2391` precision=`0.4783` recall=`0.3235` f1=`0.386`
- Relations: accuracy=`0.8333` precision=`1` recall=`0.8333` f1=`0.9091`

## LLM Analysis

- Model: `qwen/qwen3.5-397b-a17b`
- Prompt size: `28170` bytes, `28170` characters, estimated tokens=`7043`

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

- Total inferred family edges: `5`
- Strongest edges:
- `family_5` -> `family_4` | pairs=`19944` avg_score=`6.9675` support=`1` lift=`5.014` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_3` -> `family_2` | pairs=`19944` avg_score=`6.935` support=`1` lift=`5.014` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_6` | pairs=`19943` avg_score=`6.9675` support=`1` lift=`5.0142` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_9` -> `family_9` | pairs=`203` avg_score=`6.9976` support=`1` lift=`492.6059` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_8` -> `family_8` | pairs=`78` avg_score=`6.9968` support=`1` lift=`1282.0385` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`

## Families

- Total families: `10`
- Families shown below: `10`

### family_1

- Role: `request`
- Messages: `39888`
- Template: `?? ?? 00 00 00 06 01 01 00 ?? 00 01`
- Related families: `family_0`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.729574` max=`2.221252` mean=`2.214693`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.610185`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`0.8763`
- bytes `8`..`11` | kind=`variable` confidence=`0.6329`

#### Field Hypotheses

- bytes `8`..`11` | type=`uint32` confidence=`0.9999`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_be` confidence=`0.8643` endian=`big`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.9668` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`11` | label=`address_like` confidence=`0.91`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `8`..`11` | label=`payload` confidence=`0.6`

#### Feature Summary

- Messages with repetition: `39888` (`1.0`)
- Repeated n-gram instances: `40513`
- Top motifs: `0000`x79934, `000000`x40046, `0100`x40037, `000006`x39888, `000601`x39888

### family_0

- Role: `response`
- Messages: `39887`
- Template: `?? ?? 00 00 00 04 01 01 01 00`
- Related families: `family_1`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.485475` max=`2.046439` mean=`2.039969`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.610185`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`0.85`
- bytes `8`..`9` | kind=`constant` confidence=`0.6013`

#### Field Hypotheses

- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`9` | type=`uint16` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_be` confidence=`0.8643` endian=`big`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.9668` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`9` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_1 with up to 10 strong offset matches.

#### Feature Summary

- Messages with repetition: `39887` (`1.0`)
- Repeated n-gram instances: `80240`
- Top motifs: `0000`x79932, `0101`x79774, `000000`x40045, `0100`x40036, `0004`x39888

### family_2

- Role: `response`
- Messages: `19944`
- Template: `?? ?? 00 00 00 04 01 02 01 00`
- Related families: `family_3`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.721928` max=`2.370951` mean=`2.315659`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.612465`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`9` | kind=`variable` confidence=`0.6688`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.9999`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.9327` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_3 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field

#### Feature Summary

- Messages with repetition: `19944` (`1.0`)
- Repeated n-gram instances: `20169`
- Top motifs: `0000`x39963, `000000`x20019, `000004`x19944, `000401`x19944, `010201`x19944

### family_3

- Role: `request`
- Messages: `19944`
- Template: `?? ?? 00 00 00 06 01 02 00 08 00 01`
- Related families: `family_2`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.950826` max=`2.450826` mean=`2.443359`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.612465`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`11` | kind=`constant` confidence=`0.8185`

#### Field Hypotheses

- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`11` | type=`uint32` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.9327` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.9594` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`11` | label=`constant` confidence=`0.99`
- bytes `8`..`11` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Feature Summary

- Messages with repetition: `19944` (`1.0`)
- Repeated n-gram instances: `20258`
- Top motifs: `0000`x39963, `0800`x20026, `0200`x20025, `000000`x20019, `0601`x19945

### family_4

- Role: `response`
- Messages: `19944`
- Template: `?? ?? 00 00 00 05 01 03 02 00 ??`
- Related families: `family_5`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.222192` max=`2.732159` mean=`2.704875`
- Candidate discriminator offset: `10` cardinality=`16` entropy=`3.755839` salience=`0.67643` mutual_information=`0.4089` contrastive_separation=`1.0` confidence=`0.487497`
- Top discriminator candidates: offset `10` conf=`0.487497` salience=`0.67643`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.612465`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`9` | kind=`constant` confidence=`0.8488`
- bytes `10`..`10` | kind=`variable` confidence=`0.7358`

#### Field Hypotheses

- bytes `10`..`10` | type=`uint8` confidence=`0.9992`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`9` | type=`uint16` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.9327` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`9` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`discriminator` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Echoes request fields from family_5 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `19944` (`1.0`)
- Repeated n-gram instances: `21150`
- Top motifs: `0000`x39963, `0005`x20914, `0200`x20028, `000000`x20019, `0501`x19945

### family_5

- Role: `request`
- Messages: `19944`
- Template: `?? ?? 00 00 00 06 01 03 00 08 00 01`
- Related families: `family_4`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.896241` max=`2.450826` mean=`2.443464`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.612465`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`11` | kind=`constant` confidence=`0.8185`

#### Field Hypotheses

- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`11` | type=`uint32` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.9327` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.9594` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `8`..`11` | label=`payload` confidence=`0.6`

#### Feature Summary

- Messages with repetition: `19944` (`1.0`)
- Repeated n-gram instances: `20242`
- Top motifs: `0000`x39963, `000000`x20019, `0300`x20018, `0800`x20016, `0001`x19945

### family_6

- Role: `response`
- Messages: `19944`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ??`
- Related families: `family_7`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.049452` max=`3.027169` mean=`2.99683`
- Candidate discriminator offset: `9` cardinality=`18` entropy=`1.222633` salience=`1.0` mutual_information=`0.621806` contrastive_separation=`1.0` confidence=`0.594348`
- Top discriminator candidates: offset `9` conf=`0.594348` salience=`1.0`, offset `10` conf=`0.45846` salience=`0.67643`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.612465`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`0.62244`

#### Field Hypotheses

- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.9327` endian=`little`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`
- bytes `8`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Echoes request fields from family_7 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field

#### Feature Summary

- Messages with repetition: `19944` (`1.0`)
- Repeated n-gram instances: `20582`
- Top motifs: `0000`x40439, `000000`x20027, `0005`x19945, `0104`x19945, `000005`x19944

### family_7

- Role: `request`
- Messages: `19943`
- Template: `?? ?? 00 00 00 06 01 04 00 08 00 01`
- Related families: `family_6`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.780672` max=`2.450826` mean=`2.443191`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.612465`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`11` | kind=`constant` confidence=`0.8185`

#### Field Hypotheses

- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`11` | type=`uint32` confidence=`0.99`
- bytes `0`..`1` | type=`uint16_le` confidence=`0.9327` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `8`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`11` | label=`constant` confidence=`0.99`
- bytes `8`..`11` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `0`..`1` | label=`transaction_id` confidence=`0.85`

#### Notes

- Detected common protocol pattern: transaction ID, length field

#### Feature Summary

- Messages with repetition: `19943` (`1.0`)
- Repeated n-gram instances: `20265`
- Top motifs: `0000`x39969, `000000`x20026, `0800`x20021, `0400`x20019, `010400`x19944

### family_9

- Role: `unknown`
- Messages: `406`
- Template: `?? ?? 00 00 00 06 01 06 00 08 00 ??`
- Related families: `family_9`
- Role hint: `unknown`
- Semantic confidence: `0.5`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.450826` mean=`2.316514`
- Candidate discriminator offset: `11` cardinality=`15` entropy=`2.017045` salience=`0.489782` mutual_information=`0.027679` contrastive_separation=`0.984375` confidence=`0.314386`
- Top discriminator candidates: offset `11` conf=`0.314386` salience=`0.489782`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.736725`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`11` | kind=`variable` confidence=`0.748505`

#### Field Hypotheses

- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`11` | type=`uint32` confidence=`0.9631`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.9293` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`11` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `8`..`11` | label=`address_like` confidence=`0.91`

#### Notes

- Echoes request fields from family_9 with up to 10 strong offset matches.

#### Feature Summary

- Messages with repetition: `406` (`1.0`)
- Repeated n-gram instances: `706`
- Top motifs: `0000`x814, `0008`x686, `0006`x418, `0800`x410, `000000`x408

### family_8

- Role: `unknown`
- Messages: `156`
- Template: `?? ?? 00 00 00 06 01 05 00 ?? ff 00`
- Related families: `family_8`
- Role hint: `unknown`
- Semantic confidence: `0.5`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.450826` max=`2.617492` mean=`2.611082`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.7581`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`11` | kind=`variable` confidence=`0.6358`

#### Field Hypotheses

- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`11` | type=`uint32` confidence=`0.9872`
- bytes `0`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `8`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`11` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `8`..`11` | label=`address_like` confidence=`0.91`

#### Notes

- Echoes request fields from family_8 with up to 10 strong offset matches.

#### Feature Summary

- Messages with repetition: `156` (`1.0`)
- Repeated n-gram instances: `158`
- Top motifs: `0000`x312, `0500`x158, `000000`x156, `000006`x156, `000601`x156
