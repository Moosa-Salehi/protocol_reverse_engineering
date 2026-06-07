# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **framing_global_summary**: {'common_header_ends': [{'header_end': 7, 'family_count': 12, 'family_ratio': 1.0}], 'field_type_counts': {'length': 36, 'transaction_or_counter': 22, 'constant': 10, 'discriminator': 4}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 12}
- **llm_refinement**: {'artifact_type': 'llm_refinement_summary', 'created_at': '2026-06-07T12:08:08.684733+00:00', 'input_patch_count': 4, 'accepted_patch_count': 1, 'rejected_patch_count': 3}

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

- `family_0` | messages=`143667` split=`0.7` under_split=`0.7` over_split=`0` warnings=high latent dispersion, low latent silhouette, mixed length profile
- `family_3` | messages=`6550` split=`0.5` under_split=`0.5` over_split=`0.1` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_6` | messages=`19787` split=`0.4` under_split=`0.4` over_split=`0` warnings=low latent silhouette, mixed length profile
- `family_1` | messages=`2609` split=`0.3` under_split=`0.3` over_split=`0.1` warnings=high latent dispersion, possible over-split merge candidate
- `family_10` | messages=`1245` split=`0.2` under_split=`0.2` over_split=`0.4606` warnings=low latent silhouette, possible over-split merge candidate
- `family_8` | messages=`1725` split=`0.2` under_split=`0.2` over_split=`0.3233` warnings=low latent silhouette, possible over-split merge candidate
- `family_5` | messages=`8347` split=`0.2` under_split=`0.2` over_split=`0.2606` warnings=low latent silhouette, possible over-split merge candidate
- `family_7` | messages=`11149` split=`0.2` under_split=`0.2` over_split=`0.2533` warnings=mixed length profile, possible over-split merge candidate
- `family_9` | messages=`1363` split=`0` under_split=`0` over_split=`0.4606` warnings=possible over-split merge candidate
- `family_4` | messages=`925` split=`0` under_split=`0` over_split=`0.2606` warnings=possible over-split merge candidate

### Clustering Merge Candidates

- `family_10` -> `family_9` distance=`0.4323` score=`0.4606`
- `family_9` -> `family_10` distance=`0.4323` score=`0.4606`
- `family_9` -> `family_8` distance=`0.5423` score=`0.3233`
- `family_8` -> `family_9` distance=`0.5423` score=`0.3233`
- `family_5` -> `family_4` distance=`0.5926` score=`0.2606`
- `family_4` -> `family_5` distance=`0.5926` score=`0.2606`
- `family_7` -> `family_8` distance=`0.5984` score=`0.2533`
- `family_8` -> `family_7` distance=`0.5984` score=`0.2533`
- `family_9` -> `family_7` distance=`0.6121` score=`0.2363`
- `family_7` -> `family_9` distance=`0.6121` score=`0.2363`

### Evaluation Top Relation Edges

- `family_6` -> `family_6` | pairs=`8154` avg_score=`6.9457` support=`0.7944` lift=`8.3422` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_3` | pairs=`6528` avg_score=`6.9674` support=`0.0847` lift=`1.2947` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_7` -> `family_7` | pairs=`3174` avg_score=`6.9477` support=`0.463` lift=`10.7838` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_5` -> `family_5` | pairs=`2015` avg_score=`6.9508` support=`0.3526` lift=`13.3958` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_8` | pairs=`1725` avg_score=`6.9676` support=`0.0224` lift=`1.2973` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_6` -> `family_2` | pairs=`1084` avg_score=`6.9676` support=`0.1056` lift=`6.4273` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_9` | pairs=`1066` avg_score=`6.9675` support=`0.0138` lift=`1.0146` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `noise` | pairs=`878` avg_score=`6.9675` support=`0.0114` lift=`1.2353` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_7` -> `family_6` | pairs=`843` avg_score=`6.9674` support=`0.123` lift=`1.2913` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_5` -> `family_1` | pairs=`697` avg_score=`6.9676` support=`0.122` lift=`4.6781` direction=`1` order=`1` echo_fields=`10` length_rules=`0`

## Final Ground Truth Evaluation

- Overall score: `0.5953`
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
- `family_6` -> `family_6` | pairs=`8154` avg_score=`6.9457` support=`0.7944` lift=`8.3422` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_7` | pairs=`3174` avg_score=`6.9477` support=`0.463` lift=`10.7838` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_5` -> `family_5` | pairs=`2015` avg_score=`6.9508` support=`0.3526` lift=`13.3958` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_0` -> `family_8` | pairs=`1725` avg_score=`6.9676` support=`0.0224` lift=`1.2973` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_6` -> `family_2` | pairs=`1084` avg_score=`6.9676` support=`0.1056` lift=`6.4273` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_0` -> `family_9` | pairs=`1066` avg_score=`6.9675` support=`0.0138` lift=`1.0146` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_0` -> `noise` | pairs=`878` avg_score=`6.9675` support=`0.0114` lift=`1.2353` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_6` | pairs=`843` avg_score=`6.9674` support=`0.123` lift=`1.2913` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_5` -> `family_1` | pairs=`697` avg_score=`6.9676` support=`0.122` lift=`4.6781` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_5` -> `family_4` | pairs=`376` avg_score=`6.9676` support=`0.0658` lift=`7.1126` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_10` | pairs=`311` avg_score=`6.9673` support=`0.0454` lift=`3.6435` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_6` -> `family_10` | pairs=`175` avg_score=`6.9674` support=`0.017` lift=`1.3693` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_9` | pairs=`157` avg_score=`6.9675` support=`0.0229` lift=`1.6801` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_6` -> `family_9` | pairs=`140` avg_score=`6.9674` support=`0.0136` lift=`1.0006` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_7` -> `family_2` | pairs=`137` avg_score=`6.9674` support=`0.02` lift=`1.2162` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `noise` -> `noise` | pairs=`44` avg_score=`6.9969` support=`1` lift=`108.4588` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`
- `family_2` -> `family_2` | pairs=`23` avg_score=`6.9967` support=`1` lift=`60.8637` direction=`1` order=`1` flow=`unknown->unknown` echo_fields=`10`

## Families

- Total families: `12`
- Families shown below: `12`

### family_0

- Role: `request`
- Messages: `143667`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_3`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.314781`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.36067` salience=`1.0` mutual_information=`0.143064` contrastive_separation=`0.796875` confidence=`0.573042`
- Top discriminator candidates: offset `8` conf=`0.573042` salience=`1.0`, offset `7` conf=`0.498845` salience=`0.743093`, offset `9` conf=`0.475707` salience=`0.583835`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.608665`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6534`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`11` | kind=`variable` confidence=`0.6859`

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

- Messages with repetition: `143667` (`1.0`)
- Repeated n-gram instances: `181099`
- Top motifs: `0000`x288327, `000000`x144283, `0101`x98396, `0100`x81057, `0006`x77846

### family_6

- Role: `request`
- Messages: `19787`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_10`, `family_2`, `family_6`, `family_7`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.515`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.485475` max=`3.027169` mean=`2.352618`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.465606` salience=`1.0` mutual_information=`0.143064` contrastive_separation=`0.796875` confidence=`0.574055`
- Top discriminator candidates: offset `8` conf=`0.574055` salience=`1.0`, offset `7` conf=`0.500851` salience=`0.743093`, offset `9` conf=`0.450142` salience=`0.583835`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.61256`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6523`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`11` | kind=`variable` confidence=`0.6824705`

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

- Messages with repetition: `19787` (`1.0`)
- Repeated n-gram instances: `24147`
- Top motifs: `0000`x39702, `000000`x19867, `0101`x11995, `0006`x10530, `0601`x10297

### family_7

- Role: `request`
- Messages: `11149`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_10`, `family_2`, `family_6`, `family_7`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5929`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.896241` max=`3.027169` mean=`2.382713`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.331912` salience=`1.0` mutual_information=`0.143064` contrastive_separation=`0.796875` confidence=`0.56793`
- Top discriminator candidates: offset `8` conf=`0.56793` salience=`1.0`, offset `7` conf=`0.501647` salience=`0.743093`, offset `9` conf=`0.475099` salience=`0.583835`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6196849999999999`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6538`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`11` | kind=`variable` confidence=`0.59755`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.9996`
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

- Messages with repetition: `11149` (`1.0`)
- Repeated n-gram instances: `12786`
- Top motifs: `0000`x22342, `000000`x11154, `000006`x6939, `000601`x6939, `0006`x6939

### family_5

- Role: `request`
- Messages: `8347`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_1`, `family_4`, `family_5`
- Role hint: `request`
- Semantic confidence: `0.6051`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.846439` max=`3.027169` mean=`2.409017`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.206195` salience=`1.0` mutual_information=`0.143064` contrastive_separation=`0.796875` confidence=`0.564185`
- Top discriminator candidates: offset `8` conf=`0.564185` salience=`1.0`, offset `7` conf=`0.502865` salience=`0.743093`, offset `9` conf=`0.472883` salience=`0.583835`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.623485`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6553`
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

- Messages with repetition: `8347` (`1.0`)
- Repeated n-gram instances: `9029`
- Top motifs: `0000`x16698, `000000`x8347, `000006`x5716, `000601`x5716, `0006`x5716

### family_3

- Role: `response`
- Messages: `6550`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_0`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.020656`
- Candidate discriminator offset: `9` cardinality=`9` entropy=`0.046691` salience=`0.583835` mutual_information=`0.225435` contrastive_separation=`0.890625` confidence=`0.414806`
- Top discriminator candidates: offset `9` conf=`0.414806` salience=`0.583835`, offset `10` conf=`0.356624` salience=`0.401347`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6215849999999999`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6685`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.6682`
- bytes `10`..`10` | kind=`variable` confidence=`0.7228`
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

- Messages with repetition: `6550` (`1.0`)
- Repeated n-gram instances: `6592`
- Top motifs: `0000`x13121, `000000`x6571, `000005`x6532, `000501`x6532, `010402`x6532

### family_1

- Role: `response`
- Messages: `2609`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_5`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.617492` max=`3.027169` mean=`3.019931`
- Candidate discriminator offset: `9` cardinality=`8` entropy=`0.050854` salience=`0.583835` mutual_information=`0.225435` contrastive_separation=`0.875` confidence=`0.422008`
- Top discriminator candidates: offset `9` conf=`0.422008` salience=`0.583835`, offset `10` conf=`0.353581` salience=`0.401347`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.641725`
- bytes `2`..`3` | kind=`constant` confidence=`0.8763`
- bytes `4`..`5` | kind=`variable` confidence=`0.6688`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.6687`
- bytes `10`..`10` | kind=`variable` confidence=`0.7504`
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

- Messages with repetition: `2609` (`1.0`)
- Repeated n-gram instances: `2631`
- Top motifs: `0000`x5229, `000000`x2620, `000005`x2605, `000501`x2605, `010402`x2605

### family_8

- Role: `response`
- Messages: `1725`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_0`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.025483`
- Candidate discriminator offset: `9` cardinality=`7` entropy=`0.048316` salience=`0.583835` mutual_information=`0.225435` contrastive_separation=`0.859375` confidence=`0.429186`
- Top discriminator candidates: offset `9` conf=`0.429186` salience=`0.583835`, offset `10` conf=`0.351566` salience=`0.401347`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.65911`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`constant` confidence=`1.0`
- bytes `8`..`9` | kind=`variable` confidence=`0.669`
- bytes `10`..`10` | kind=`variable` confidence=`0.755`

#### Field Hypotheses

- bytes `8`..`9` | type=`uint16` confidence=`0.9959`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `10`..`10` | type=`uint8` confidence=`0.9884`
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
- Messages: `1666`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ?? 00`
- Related families: `family_2`, `family_6`, `family_7`
- Role hint: `response`
- Semantic confidence: `0.9818`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.40401` max=`3.027169` mean=`2.994239`
- Candidate discriminator offset: `9` cardinality=`12` entropy=`0.599428` salience=`0.583835` mutual_information=`0.225435` contrastive_separation=`0.9375` confidence=`0.398443`
- Top discriminator candidates: offset `9` conf=`0.398443` salience=`0.583835`, offset `10` conf=`0.34984` salience=`0.401347`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.66101`
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

- Messages with repetition: `1666` (`1.0`)
- Repeated n-gram instances: `1676`
- Top motifs: `0000`x3336, `000000`x1670, `0005`x1621, `0104`x1621, `000005`x1620

### family_9

- Role: `response`
- Messages: `1363`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ??`
- Related families: `family_0`, `family_6`, `family_7`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.222192` max=`3.027169` mean=`2.993993`
- Candidate discriminator offset: `9` cardinality=`10` entropy=`0.481044` salience=`0.583835` mutual_information=`0.225435` contrastive_separation=`0.90625` confidence=`0.411694`
- Top discriminator candidates: offset `9` conf=`0.411694` salience=`0.583835`, offset `10` conf=`0.354522` salience=`0.401347`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.6679449999999999`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.6648`
- bytes `10`..`10` | kind=`variable` confidence=`0.7384`

#### Field Hypotheses

- bytes `7`..`7` | type=`uint8` confidence=`0.9985`
- bytes `8`..`9` | type=`uint16` confidence=`0.9927`
- bytes `2`..`6` | type=`bytes` confidence=`0.99`
- bytes `10`..`10` | type=`uint8` confidence=`0.9743`
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

- Messages with repetition: `1363` (`1.0`)
- Repeated n-gram instances: `1415`
- Top motifs: `0000`x2751, `000000`x1388, `000005`x1363, `000501`x1363, `0005`x1363

### family_10

- Role: `response`
- Messages: `1245`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_6`, `family_7`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.010959`
- Candidate discriminator offset: `9` cardinality=`9` entropy=`0.098715` salience=`0.583835` mutual_information=`0.225435` contrastive_separation=`0.890625` confidence=`0.415098`
- Top discriminator candidates: offset `9` conf=`0.415098` salience=`0.583835`, offset `10` conf=`0.349219` salience=`0.401347`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`1` | kind=`variable` confidence=`0.68172`
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

- Messages with repetition: `1245` (`1.0`)
- Repeated n-gram instances: `1245`
- Top motifs: `0000`x2490, `000000`x1245, `000005`x1245, `000501`x1245, `010402`x1245

### noise

- Role: `response`
- Messages: `967`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 00`
- Related families: `family_0`, `noise`
- Role hint: `response`
- Semantic confidence: `0.9545`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.450826` max=`3.027169` mean=`2.959562`
- Candidate discriminator offset: `9` cardinality=`17` entropy=`1.214338` salience=`0.583835` mutual_information=`0.225435` contrastive_separation=`1.0` confidence=`0.367046`
- Top discriminator candidates: offset `9` conf=`0.367046` salience=`0.583835`, offset `10` conf=`0.350112` salience=`0.401347`
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
- bytes `10`..`10` | type=`uint8` confidence=`0.9359`

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

- Messages with repetition: `967` (`1.0`)
- Repeated n-gram instances: `1009`
- Top motifs: `0000`x1954, `000000`x987, `000005`x879, `000501`x879, `010402`x879

### family_4

- Role: `response`
- Messages: `925`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_5`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.732159` max=`3.027169` mean=`3.023386`
- Candidate discriminator offset: `9` cardinality=`5` entropy=`0.058876` salience=`0.583835` mutual_information=`0.225435` contrastive_separation=`0.828125` confidence=`0.443642`
- Top discriminator candidates: offset `9` conf=`0.443642` salience=`0.583835`, offset `10` conf=`0.420578` salience=`0.401347`
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
