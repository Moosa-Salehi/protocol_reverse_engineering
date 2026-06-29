# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **framing_global_summary**: {'common_header_ends': [{'header_end': 7, 'family_count': 31, 'family_ratio': 0.9394}, {'header_end': 24, 'family_count': 1, 'family_ratio': 0.0303}, {'header_end': 16, 'family_count': 1, 'family_ratio': 0.0303}], 'field_type_counts': {'length': 101, 'transaction_or_counter': 56, 'discriminator': 41, 'constant': 37}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 33}
- **llm_refinement**: {'artifact_type': 'llm_refinement_summary', 'created_at': '2026-06-29T19:00:30.850936+00:00', 'input_patch_count': 0, 'accepted_patch_count': 0, 'rejected_patch_count': 0}

## Evaluation

- Messages: `200000` across `214` sessions
- Corpus assignment coverage: `0.9996` with `33` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `33` of `33`
- Pair hypotheses: `99634` direction_unknown_ratio=`0`
- Relation edges: `27` echo_edges=`27` length_relation_edges=`6`
- Semantic coverage: `33` of `33` families ratio=`1`
- Top semantic labels: `constant`x70, `discriminator`x63, `length`x41, `echoed_request_field`x35, `transaction_or_correlation_id`x24, `payload`x18, `transaction_id`x12, `count_like`x3
- Framing coverage: `33` of `33` families ratio=`1`
- Clustering diagnostics: warning_families=`30` split_candidates=`8` merge_candidates=`94`

### Clustering Diagnostic Warnings

- `family_5` | messages=`26553` split=`0.7` under_split=`0.7` over_split=`0` warnings=high latent dispersion, low latent silhouette, mixed length profile
- `family_14` | messages=`12465` split=`0.7` under_split=`0.7` over_split=`0` warnings=high latent dispersion, low latent silhouette, mixed length profile
- `family_19` | messages=`10298` split=`0.7` under_split=`0.7` over_split=`0` warnings=high latent dispersion, low latent silhouette, mixed length profile
- `family_10` | messages=`313` split=`0.7` under_split=`0.7` over_split=`0` warnings=high latent dispersion, low latent silhouette, mixed length profile
- `family_8` | messages=`201` split=`0.7` under_split=`0.7` over_split=`0` warnings=high latent dispersion, low latent silhouette, mixed length profile
- `family_16` | messages=`40` split=`0.5` under_split=`0.5` over_split=`0.6999` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_7` | messages=`18768` split=`0.5` under_split=`0.5` over_split=`0` warnings=high latent dispersion, low latent silhouette
- `family_2` | messages=`2284` split=`0.5` under_split=`0.5` over_split=`0` warnings=high latent dispersion, low latent silhouette
- `family_25` | messages=`654` split=`0.2` under_split=`0.2` over_split=`0.9928` warnings=low latent silhouette, possible over-split merge candidate
- `family_23` | messages=`941` split=`0.2` under_split=`0.2` over_split=`0.9917` warnings=low latent silhouette, possible over-split merge candidate

### Clustering Merge Candidates

- `family_25` -> `family_26` distance=`0.0115` score=`0.9928`
- `family_26` -> `family_25` distance=`0.0115` score=`0.9928`
- `family_23` -> `family_24` distance=`0.0133` score=`0.9917`
- `family_24` -> `family_23` distance=`0.0133` score=`0.9917`
- `family_26` -> `family_27` distance=`0.0157` score=`0.9902`
- `family_27` -> `family_26` distance=`0.0157` score=`0.9902`
- `family_24` -> `family_25` distance=`0.0186` score=`0.9884`
- `family_25` -> `family_24` distance=`0.0186` score=`0.9884`
- `family_25` -> `family_27` distance=`0.0251` score=`0.9844`
- `family_27` -> `family_25` distance=`0.0251` score=`0.9844`

### Evaluation Top Relation Edges

- `family_4` -> `family_5` | pairs=`26303` avg_score=`7.5039` support=`0.9654` lift=`3.6245` direction=`1` order=`1` echo_fields=`10` length_rules=`2`
- `family_6` -> `family_7` | pairs=`18106` avg_score=`6.9849` support=`0.9512` lift=`5.1559` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_22` | pairs=`10474` avg_score=`6.3552` support=`0.377` lift=`1.4623` direction=`1` order=`1` echo_fields=`10` length_rules=`1`
- `family_19` -> `family_22` | pairs=`6864` avg_score=`5.176` support=`0.6665` lift=`2.5855` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_14` -> `family_22` | pairs=`6864` avg_score=`5.176` support=`0.5535` lift=`2.147` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_29` | pairs=`6864` avg_score=`5.9025` support=`0.247` lift=`2.39` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_0` -> `family_31` | pairs=`6864` avg_score=`5.9025` support=`0.247` lift=`2.39` direction=`1` order=`1` echo_fields=`10` length_rules=`0`
- `family_19` -> `family_31` | pairs=`3434` avg_score=`5.6765` support=`0.3335` lift=`3.2261` direction=`1` order=`1` echo_fields=`9` length_rules=`0`
- `family_14` -> `family_29` | pairs=`3434` avg_score=`5.6765` support=`0.2769` lift=`2.679` direction=`1` order=`1` echo_fields=`9` length_rules=`0`
- `family_14` -> `family_15` | pairs=`2103` avg_score=`7.8239` support=`0.1696` lift=`8.0338` direction=`1` order=`1` echo_fields=`10` length_rules=`8`

## Final Ground Truth Evaluation

- Overall score: `0.7462`
- Verdict: `partial`
- Matched message types: `33` of `34`
- Message type matching: accuracy=`0.9429` precision=`0.9706` recall=`0.9706` f1=`0.9706`
- Field boundary: accuracy=`0.6496` precision=`0.8352` recall=`0.7451` f1=`0.7876`
- Field semantics: accuracy=`0.3403` precision=`0.5385` recall=`0.4804` f1=`0.5078`
- Relations: accuracy=`0.4412` precision=`0.5556` recall=`0.6818` f1=`0.6122`

## LLM Analysis

- Prompt size: `39758` bytes, `39758` characters, estimated tokens=`9940`

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `27`
- Strongest edges:
- `family_4` -> `family_5` | pairs=`26303` avg_score=`7.5039` support=`0.9654` lift=`3.6245` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10` length_rules=`2`
- `family_6` -> `family_7` | pairs=`18106` avg_score=`6.9849` support=`0.9512` lift=`5.1559` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_0` -> `family_22` | pairs=`10474` avg_score=`6.3552` support=`0.377` lift=`1.4623` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10` length_rules=`1`
- `family_19` -> `family_22` | pairs=`6864` avg_score=`5.176` support=`0.6665` lift=`2.5855` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_14` -> `family_22` | pairs=`6864` avg_score=`5.176` support=`0.5535` lift=`2.147` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_0` -> `family_29` | pairs=`6864` avg_score=`5.9025` support=`0.247` lift=`2.39` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_0` -> `family_31` | pairs=`6864` avg_score=`5.9025` support=`0.247` lift=`2.39` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_19` -> `family_31` | pairs=`3434` avg_score=`5.6765` support=`0.3335` lift=`3.2261` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`9`
- `family_14` -> `family_29` | pairs=`3434` avg_score=`5.6765` support=`0.2769` lift=`2.679` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`9`
- `family_14` -> `family_15` | pairs=`2103` avg_score=`7.8239` support=`0.1696` lift=`8.0338` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10` length_rules=`8`
- `family_0` -> `family_1` | pairs=`1866` avg_score=`7.9111` support=`0.0672` lift=`3.5858` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10` length_rules=`12`
- `family_2` -> `family_3` | pairs=`1302` avg_score=`7.89` support=`0.5807` lift=`44.4367` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10` length_rules=`10`
- `family_2` -> `family_23` | pairs=`626` avg_score=`6.2004` support=`0.2792` lift=`29.5929` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`9`
- `family_4` -> `family_24` | pairs=`626` avg_score=`6.2002` support=`0.023` lift=`2.435` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_0` -> `family_25` | pairs=`327` avg_score=`5.9028` support=`0.0118` lift=`1.7956` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_6` -> `family_25` | pairs=`325` avg_score=`6.1939` support=`0.0171` lift=`2.6051` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`9`
- `family_8` -> `family_22` | pairs=`128` avg_score=`5.7005` support=`0.6432` lift=`2.495` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_10` -> `family_22` | pairs=`128` avg_score=`5.6998` support=`0.4103` lift=`1.5914` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_10` -> `family_11` | pairs=`118` avg_score=`7.9857` support=`0.3782` lift=`319.3173` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_10` -> `family_27` | pairs=`66` avg_score=`6.1888` support=`0.2115` lift=`108.6337` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`9`
- `family_8` -> `family_26` | pairs=`65` avg_score=`6.2269` support=`0.3266` lift=`168.6087` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`9`
- `family_16` -> `family_17` | pairs=`37` avg_score=`7.7727` support=`0.925` lift=`2490.675` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10` length_rules=`6`
- `family_20` -> `family_32` | pairs=`29` avg_score=`6.1544` support=`0.9355` lift=`3213.7742` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_18` -> `family_30` | pairs=`23` avg_score=`6.1929` support=`0.92` lift=`3985.08` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`10`
- `family_12` -> `family_13` | pairs=`6` avg_score=`7.3282` support=`0.6` lift=`9962.7` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`7`

## Families

- Total families: `33`
- Families shown below: `33`

### family_0

- Role: `request`
- Messages: `27807`
- Template: `?? ?? 00 00 00 06 ?? 01 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??`
- Related families: `family_1`, `family_22`, `family_25`, `family_29`, `family_31`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`8` max=`260` distinct=`9`
- Entropy summary: min=`0.816689` max=`7.296721` mean=`1.653837`
- Candidate discriminator offset: `8` cardinality=`10` entropy=`0.134259` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.90625` confidence=`0.523159`
- Top discriminator candidates: offset `8` conf=`0.523159` salience=`0.623838`, offset `7` conf=`0.474057` salience=`0.498041`, offset `11` conf=`0.472369` salience=`0.607503`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `6`..`6` | type=`uint8` confidence=`0.9998`
- bytes `11`..`11` | type=`uint8` confidence=`0.9994`
- bytes `4`..`5` | type=`uint16_be` confidence=`0.9989` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.9958`
- bytes `0`..`3` | type=`uint32` confidence=`0.9349`
- bytes `8`..`10` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`5` length, `2`..`5` constant, `4`..`5` length, `5`..`5` length, `6`..`6` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`5` constant, `4`..`5` length, `5`..`5` length, `6`..`6` discriminator
- header_end=`6` body_start=`6` confidence=`0.9993` fields=`2`..`5` length, `2`..`5` constant, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`10` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`0.9989`
- bytes `8`..`10` | label=`response_size_selector` confidence=`0.982`
- bytes `0`..`3` | label=`discriminator` confidence=`0.95`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `7`..`7` | label=`opcode` confidence=`0.95`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `27807` (`1.0`)
- Repeated n-gram instances: `112582`
- Top motifs: `0000`x110526, `000000`x55628, `0006`x27943, `000006`x27881, `0100`x27197

### family_4

- Role: `request`
- Messages: `27256`
- Template: `?? ?? 00 00 00 06 ?? 03 ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??`
- Related families: `family_24`, `family_5`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`260` distinct=`4`
- Entropy summary: min=`1.207519` max=`7.253159` mean=`2.448498`
- Candidate discriminator offset: `11` cardinality=`46` entropy=`1.823303` salience=`0.607503` mutual_information=`0.560184` contrastive_separation=`1.0` confidence=`0.484649`
- Top discriminator candidates: offset `11` conf=`0.484649` salience=`0.607503`, offset `8` conf=`0.450862` salience=`0.623838`, offset `6` conf=`0.38093` salience=`0.420727`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `6`..`6` | type=`uint8` confidence=`0.9998`
- bytes `11`..`11` | type=`uint8` confidence=`0.9983`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`3` | type=`uint32` confidence=`0.5`
- bytes `8`..`10` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`5` length, `2`..`5` constant, `4`..`5` length, `5`..`5` length, `6`..`6` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`5` constant, `4`..`5` length, `5`..`5` length, `6`..`6` discriminator, `7`..`7` constant
- header_end=`6` body_start=`6` confidence=`0.8944` fields=`2`..`5` length, `2`..`5` constant, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`10` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `27256` (`1.0`)
- Repeated n-gram instances: `63794`
- Top motifs: `0000`x77367, `000000`x38552, `0006`x26620, `000006`x26554, `0300`x24294

### family_5

- Role: `response`
- Messages: `26553`
- Template: `?? ?? 00 00 00 ?? ?? 03 ?? ?? ?? 00 ?? 00 ?? 00 00 00 ?? 00 ?? 00 ?? 00 00 00 00 00 00 ?? ?? 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??`
- Related families: `family_4`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`259` distinct=`41`
- Entropy summary: min=`0.0` max=`5.648011` mean=`2.229684`
- Candidate discriminator offset: `12` cardinality=`98` entropy=`0.615358` salience=`0.907081` mutual_information=`0.364686` contrastive_separation=`1.0` confidence=`0.503497`
- Top discriminator candidates: offset `12` conf=`0.503497` salience=`0.907081`, offset `20` conf=`0.488038` salience=`1.0`, offset `8` conf=`0.479202` salience=`0.623838`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`
- bytes `9`..`10` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `6`..`6` | type=`uint8` confidence=`0.9997`
- bytes `9`..`10` | type=`keyword` confidence=`0.9963`
- bytes `7`..`7` | type=`uint8` confidence=`0.9956`
- bytes `8`..`8` | type=`uint8` confidence=`0.9911` endian=`big`
- bytes `0`..`3` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `6`..`6` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `6`..`6` discriminator, `7`..`7` constant
- header_end=`6` body_start=`6` confidence=`0.8837` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `8`..`8` | label=`length` confidence=`0.9911`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `7`..`7` | label=`opcode` confidence=`0.95`
- bytes `8`..`8` | label=`discriminator` confidence=`0.7`

#### Notes

- Echoes request fields from family_4 with up to 10 strong offset matches.
- Response size is tied to request fields from family_4.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `26553` (`1.0`)
- Repeated n-gram instances: `1923927`
- Top motifs: `0000`x952387, `000000`x856334, `0103`x21857, `0013`x18130, `000013`x18128

### family_22

- Role: `response`
- Messages: `25685`
- Template: `00 aa 00 00 00 03 01 81 ??`
- Related families: `family_0`, `family_10`, `family_14`, `family_19`, `family_8`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`2.281036` mean=`2.130419`
- Candidate discriminator offset: `8` cardinality=`4` entropy=`0.929253` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.8125` confidence=`0.585265`
- Top discriminator candidates: offset `8` conf=`0.585265` salience=`0.623838`, offset `1` conf=`0.233219` salience=`0.204449`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `8`..`8` | type=`uint8` confidence=`0.9998`
- bytes `0`..`3` | type=`uint32` confidence=`0.9993`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.8848` fields=`0`..`7` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`0.8533` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `0`..`3` | label=`discriminator` confidence=`0.9993`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`discriminator` confidence=`0.95`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_10 with up to 10 strong offset matches.
- Echoes request fields from family_14 with up to 10 strong offset matches.
- Echoes request fields from family_19 with up to 10 strong offset matches.

#### Feature Summary

- Messages with repetition: `25685` (`1.0`)
- Repeated n-gram instances: `26062`
- Top motifs: `0000`x51528, `000000`x25843, `0003`x25746, `000003`x25685, `000301`x25685

### family_6

- Role: `request`
- Messages: `19098`
- Template: `?? ?? 00 00 00 06 ?? 04 ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??`
- Related families: `family_25`, `family_7`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`260` distinct=`13`
- Entropy summary: min=`1.207519` max=`7.31022` mean=`2.829087`
- Candidate discriminator offset: `8` cardinality=`8` entropy=`2.225548` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.875` confidence=`0.578666`
- Top discriminator candidates: offset `8` conf=`0.578666` salience=`0.623838`, offset `11` conf=`0.457358` salience=`0.607503`, offset `6` conf=`0.389094` salience=`0.420727`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `6`..`6` | type=`uint8` confidence=`0.9998`
- bytes `11`..`11` | type=`uint8` confidence=`0.9984`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `4`..`5` | type=`uint16_be` confidence=`0.9564` endian=`big`
- bytes `0`..`3` | type=`uint32_le` confidence=`0.8745` endian=`little`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.95`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`length` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `19098` (`1.0`)
- Repeated n-gram instances: `44507`
- Top motifs: `0000`x46264, `000000`x23184, `0006`x20417, `000006`x20356, `06ff`x19897

### family_7

- Role: `response`
- Messages: `18768`
- Template: `?? ?? 00 00 00 ?? ff 04 ?? ?? ?? ?? ?? 00 ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? 00 00 00 ?? ?? ?? ?? 00 00 00 00 ?? ?? 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? ?? ?? 00 ?? 00 00 ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`
- Related families: `family_6`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`422` distinct=`54`
- Entropy summary: min=`0.208915` max=`7.265281` mean=`1.133816`
- Candidate discriminator offset: `12` cardinality=`163` entropy=`2.33339` salience=`0.907081` mutual_information=`0.364686` contrastive_separation=`1.0` confidence=`0.516289`
- Top discriminator candidates: offset `12` conf=`0.516289` salience=`0.907081`, offset `11` conf=`0.501867` salience=`0.607503`, offset `20` conf=`0.487425` salience=`1.0`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`
- bytes `9`..`208` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `6`..`6` | type=`uint8` confidence=`0.9999`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `4`..`5` | type=`uint16_be` confidence=`0.9551` endian=`big`
- bytes `8`..`8` | type=`uint8` confidence=`0.9551` endian=`big`
- bytes `0`..`3` | type=`uint32_le` confidence=`0.8958` endian=`little`
- bytes `9`..`208` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `6`..`6` | label=`discriminator` confidence=`0.9999`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.95`
- bytes `4`..`5` | label=`length` confidence=`0.95`
- bytes `8`..`8` | label=`length` confidence=`0.95`
- bytes `8`..`8` | label=`discriminator` confidence=`0.7`
- bytes `9`..`208` | label=`payload` confidence=`0.6`

#### Notes

- Echoes request fields from family_6 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `18768` (`1.0`)
- Repeated n-gram instances: `6527275`
- Top motifs: `0000`x2716862, `000000`x2672292, `ff04`x19369, `cbff`x16225, `00cb`x16130

### family_14

- Role: `request`
- Messages: `12465`
- Template: `?? ?? 00 00 00 ?? ?? 0f ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??`
- Related families: `family_15`, `family_22`, `family_29`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`260` distinct=`25`
- Entropy summary: min=`1.14511` max=`7.305899` mean=`5.56877`
- Candidate discriminator offset: `12` cardinality=`7` entropy=`2.088176` salience=`0.907081` mutual_information=`0.364686` contrastive_separation=`0.859375` confidence=`0.631345`
- Top discriminator candidates: offset `12` conf=`0.631345` salience=`0.907081`, offset `11` conf=`0.546968` salience=`0.607503`, offset `20` conf=`0.530343` salience=`1.0`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`96` | kind=`variable` confidence=`1.0`
- bytes `97`..`97` | kind=`variable` confidence=`1.0`
- bytes `98`..`237` | kind=`variable` confidence=`1.0`
- bytes `238`..`239` | kind=`variable` confidence=`1.0`
- bytes `240`..`259` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `6`..`6` | type=`uint8` confidence=`0.9998`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `97`..`97` | type=`uint8` confidence=`0.9802`
- bytes `4`..`5` | type=`uint16_be` confidence=`0.9711` endian=`big`
- bytes `238`..`239` | type=`uint16` confidence=`0.9319`
- bytes `0`..`3` | type=`uint32` confidence=`0.8351`
- bytes `8`..`96` | type=`bytes` confidence=`0.5`
- bytes `98`..`237` | type=`bytes` confidence=`0.5`
- bytes `240`..`259` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` discriminator
- header_end=`6` body_start=`6` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`96` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`96` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `97`..`97` | label=`discriminator` confidence=`0.9802`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`length` confidence=`0.95`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `12465` (`1.0`)
- Repeated n-gram instances: `33046`
- Top motifs: `0000`x31192, `000000`x15347, `010f`x10331, `0f00`x8372, `0001`x5219

### family_31

- Role: `response`
- Messages: `10300`
- Template: `00 ?? 00 00 00 03 01 97 ??`
- Related families: `family_0`, `family_19`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`2.281036` mean=`2.071999`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`0.920727` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.796875` confidence=`0.574918`
- Top discriminator candidates: offset `8` conf=`0.574918` salience=`0.623838`, offset `1` conf=`0.287216` salience=`0.204449`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `6`..`6` | type=`uint8` confidence=`0.9998`
- bytes `8`..`8` | type=`uint8` confidence=`0.9997`
- bytes `0`..`3` | type=`uint32` confidence=`0.9983`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.9406` fields=`0`..`0` constant, `2`..`5` length, `2`..`7` constant, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`0.9151` fields=`0`..`0` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`discriminator` confidence=`0.9998`
- bytes `0`..`3` | label=`discriminator` confidence=`0.9983`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`discriminator` confidence=`0.95`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Echoes request fields from family_19 with up to 9 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `10300` (`1.0`)
- Repeated n-gram instances: `13518`
- Top motifs: `0000`x21888, `000000`x11588, `0003`x10942, `000003`x10300, `000301`x10298

### family_19

- Role: `request`
- Messages: `10298`
- Template: `00 ?? 00 00 00 ?? 01 17 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??`
- Related families: `family_22`, `family_31`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`260` distinct=`11`
- Entropy summary: min=`1.207519` max=`7.302527` mean=`6.175196`
- Candidate discriminator offset: `12` cardinality=`6` entropy=`1.923552` salience=`0.907081` mutual_information=`0.364686` contrastive_separation=`0.84375` confidence=`0.632057`
- Top discriminator candidates: offset `12` conf=`0.632057` salience=`0.907081`, offset `11` conf=`0.566397` salience=`0.607503`, offset `20` conf=`0.532126` salience=`1.0`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`96` | kind=`variable` confidence=`1.0`
- bytes `97`..`97` | kind=`variable` confidence=`1.0`
- bytes `98`..`237` | kind=`variable` confidence=`1.0`
- bytes `238`..`239` | kind=`variable` confidence=`1.0`
- bytes `240`..`259` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `0`..`3` | type=`uint32` confidence=`0.9984`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `97`..`97` | type=`uint8` confidence=`0.976`
- bytes `238`..`239` | type=`uint16` confidence=`0.9175`
- bytes `8`..`96` | type=`bytes` confidence=`0.5`
- bytes `98`..`237` | type=`bytes` confidence=`0.5`
- bytes `240`..`259` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `0`..`3` | label=`discriminator` confidence=`0.9984`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `97`..`97` | label=`discriminator` confidence=`0.976`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `10298` (`1.0`)
- Repeated n-gram instances: `24455`
- Top motifs: `0000`x25754, `000000`x13075, `0117`x10328, `17ff`x5196, `1700`x5153

### family_29

- Role: `response`
- Messages: `10298`
- Template: `00 ?? 00 00 00 03 01 8f ??`
- Related families: `family_0`, `family_14`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`2.281036` mean=`2.071718`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`0.920792` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.796875` confidence=`0.574922`
- Top discriminator candidates: offset `8` conf=`0.574922` salience=`0.623838`, offset `1` conf=`0.295954` salience=`0.204449`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `8`..`8` | type=`uint8` confidence=`0.9997`
- bytes `0`..`3` | type=`uint32` confidence=`0.9984`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `2`..`7` constant, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `0`..`3` | label=`discriminator` confidence=`0.9984`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`discriminator` confidence=`0.95`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Echoes request fields from family_14 with up to 9 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `10298` (`1.0`)
- Repeated n-gram instances: `13531`
- Top motifs: `0000`x21890, `000000`x11592, `0003`x10943, `000003`x10298, `000301`x10298

### family_2

- Role: `request`
- Messages: `2284`
- Template: `?? ?? 00 00 00 ?? ?? 02 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??`
- Related families: `family_23`, `family_3`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`260` distinct=`11`
- Entropy summary: min=`1.207519` max=`7.269239` mean=`2.804109`
- Candidate discriminator offset: `11` cardinality=`16` entropy=`2.910565` salience=`0.607503` mutual_information=`0.560184` contrastive_separation=`1.0` confidence=`0.518995`
- Top discriminator candidates: offset `11` conf=`0.518995` salience=`0.607503`, offset `10` conf=`0.451708` salience=`0.433342`, offset `9` conf=`0.422464` salience=`0.327371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `6`..`6` | type=`uint8` confidence=`0.9982`
- bytes `11`..`11` | type=`uint8` confidence=`0.993`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `4`..`5` | type=`uint16_be` confidence=`0.9729` endian=`big`
- bytes `0`..`3` | type=`uint32` confidence=`0.5`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` discriminator
- header_end=`6` body_start=`6` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`length` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.9`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `2284` (`1.0`)
- Repeated n-gram instances: `7424`
- Top motifs: `0000`x7413, `000000`x3692, `0200`x1938, `0006`x1700, `000006`x1638

### family_15

- Role: `response`
- Messages: `2106`
- Template: `?? ?? 00 00 00 06 ff 0f 00 ?? 00 ?? ?? ?? 00 00 00 ?? ff ?? ?? ?? 00 ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 ?? ?? ?? 00 00 00 00 00 00 00 ?? 00 00 ?? ?? 00 00 ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? 00 00 ?? ?? ?? ?? ?? ?? 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 ?? ?? ?? ?? ?? ?? 00 00 ?? ?? 00 00 ?? ?? 00 ?? 00 ?? 00 00 00 ?? 00 00 00 00 00 00 00 00 00 00 ?? ?? ?? ?? 00 ?? 00 00 00 00 00 00 ?? ?? ?? ?? 00 ?? 00 00 ?? ?? ?? ?? 00 ?? 00 00 00 00 00 00 ?? ?? ?? ?? 00 ?? 00 00 ?? 00 ?? ?? 00 ?? 00 00 00 00 00 00 ?? 00 ?? ?? 00 ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 ?? ?? 00 00 00 ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ?? ?? 00 00 00 ?? ?? ?? ?? 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 64 61 69 6d 00 6e 00 00 31 30 31 31 36 30 00 00 00 00 00 00 00 00 00 00 00 00 64 61 69 6d 00 6e 00 00 03 e7`
- Related families: `family_14`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`390` distinct=`25`
- Entropy summary: min=`1.382228` max=`3.443856` mean=`2.554838`
- Candidate discriminator offset: `11` cardinality=`5` entropy=`1.064671` salience=`0.607503` mutual_information=`0.560184` contrastive_separation=`0.828125` confidence=`0.578465`
- Top discriminator candidates: offset `11` conf=`0.578465` salience=`0.607503`, offset `9` conf=`0.422386` salience=`0.327371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `6`..`6` | type=`uint8` confidence=`0.9991`
- bytes `11`..`11` | type=`uint8` confidence=`0.9976`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`3` | type=`uint32_le` confidence=`0.9454` endian=`little`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`0.9004` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.8295` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `6`..`6` | label=`discriminator` confidence=`0.9991`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.95`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`
- bytes `4`..`5` | label=`length` confidence=`0.9276`
- bytes `8`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Echoes request fields from family_14 with up to 10 strong offset matches.
- Response size is tied to request fields from family_14.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `2106` (`1.0`)
- Repeated n-gram instances: `16864`
- Top motifs: `0000`x9584, `000000`x6156, `0006`x2722, `0f00`x2524, `000006`x2518

### family_1

- Role: `response`
- Messages: `1866`
- Template: `?? ?? 00 00 00 ?? ff 01 ?? ?? ?? ?? ?? ?? 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 ?? ?? ?? 00 00 00 ?? ?? ?? 00 ?? 00 ?? 00 00 00 00 00 00 00 ?? ?? 00 00 00 ?? ?? ?? ?? 00 00 00 00`
- Related families: `family_0`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`66` distinct=`10`
- Entropy summary: min=`0.956766` max=`4.186569` mean=`2.421225`
- Candidate discriminator offset: `8` cardinality=`5` entropy=`0.952536` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.828125` confidence=`0.570772`
- Top discriminator candidates: offset `8` conf=`0.570772` salience=`0.623838`, offset `9` conf=`0.409201` salience=`0.327371`, offset `6` conf=`0.386179` salience=`0.420727`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `6`..`6` | type=`uint8` confidence=`0.9979`
- bytes `9`..`9` | type=`uint8` confidence=`0.9941`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `4`..`5` | type=`uint16_be` confidence=`0.9753` endian=`big`
- bytes `8`..`8` | type=`uint8` confidence=`0.9753` endian=`big`
- bytes `0`..`3` | type=`uint32_le` confidence=`0.95` endian=`little`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`length` confidence=`0.9753`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.95`
- bytes `4`..`5` | label=`length` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `9`..`9` | label=`discriminator` confidence=`0.95`
- bytes `8`..`8` | label=`discriminator` confidence=`0.7`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Response size is tied to request fields from family_0.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `1866` (`1.0`)
- Repeated n-gram instances: `3383`
- Top motifs: `0000`x4154, `000000`x2109, `0101`x2107, `ff01`x1844, `0004`x1471

### family_3

- Role: `response`
- Messages: `1309`
- Template: `?? ?? 00 00 00 ?? ff 02 ?? ?? ?? ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? 00 ?? 00 ?? ?? ?? 00 ?? ?? ?? ?? ?? 00 ?? 00 ?? 00 00 00 ?? ?? 00 00 00 07 ff 02 04 00 00 00 00 f2 00 00 00 07 ff 02 04 00 00 00 00`
- Related families: `family_2`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`77` distinct=`12`
- Entropy summary: min=`1.568025` max=`3.443856` mean=`2.491872`
- Candidate discriminator offset: `10` cardinality=`5` entropy=`0.657199` salience=`0.433342` mutual_information=`0.264546` contrastive_separation=`0.828125` confidence=`0.446041`
- Top discriminator candidates: offset `10` conf=`0.446041` salience=`0.433342`, offset `9` conf=`0.354792` salience=`0.327371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`
- bytes `9`..`10` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `9`..`10` | type=`keyword` confidence=`0.9847`
- bytes `0`..`3` | type=`uint32_le` confidence=`0.95` endian=`little`
- bytes `4`..`5` | type=`uint16_be` confidence=`0.9396` endian=`big`
- bytes `8`..`8` | type=`uint8` confidence=`0.9396` endian=`big`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.95`
- bytes `4`..`5` | label=`length` confidence=`0.95`
- bytes `8`..`8` | label=`length` confidence=`0.95`

#### Notes

- Echoes request fields from family_2 with up to 10 strong offset matches.
- Response size is tied to request fields from family_2.
- Detected common protocol pattern: transaction ID, length field

#### Feature Summary

- Messages with repetition: `1309` (`1.0`)
- Repeated n-gram instances: `5125`
- Top motifs: `0000`x4360, `000000`x2671, `0202`x1494, `ff02`x1336, `0005`x1130

### family_23

- Role: `response`
- Messages: `941`
- Template: `00 ?? 00 00 00 03 01 82 ??`
- Related families: `family_2`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`2.281036` mean=`2.072316`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`0.93721` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.796875` confidence=`0.574935`
- Top discriminator candidates: offset `8` conf=`0.574935` salience=`0.623838`, offset `1` conf=`0.295898` salience=`0.204449`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `8`..`8` | type=`uint8` confidence=`0.9968`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`3` | type=`uint32` confidence=`0.983`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `2`..`7` constant, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`discriminator` confidence=`0.983`
- bytes `8`..`8` | label=`discriminator` confidence=`0.95`

#### Notes

- Echoes request fields from family_2 with up to 9 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `941` (`1.0`)
- Repeated n-gram instances: `1234`
- Top motifs: `0000`x2000, `000000`x1059, `0003`x998, `000003`x941, `000301`x941

### family_24

- Role: `response`
- Messages: `940`
- Template: `00 ?? 00 00 00 03 01 83 ??`
- Related families: `family_4`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`2.281036` mean=`2.069689`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`0.937584` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.796875` confidence=`0.574957`
- Top discriminator candidates: offset `8` conf=`0.574957` salience=`0.623838`, offset `1` conf=`0.295766` salience=`0.204449`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `8`..`8` | type=`uint8` confidence=`0.9968`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`3` | type=`uint32` confidence=`0.983`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `2`..`7` constant, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`discriminator` confidence=`0.983`
- bytes `8`..`8` | label=`discriminator` confidence=`0.95`

#### Notes

- Echoes request fields from family_4 with up to 10 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `940` (`1.0`)
- Repeated n-gram instances: `1248`
- Top motifs: `0000`x2004, `000000`x1064, `0003`x1000, `000003`x940, `000301`x940

### family_25

- Role: `response`
- Messages: `654`
- Template: `00 ?? 00 00 00 03 01 84 ??`
- Related families: `family_0`, `family_6`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`2.281036` mean=`2.154912`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.516867` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.796875` confidence=`0.586107`
- Top discriminator candidates: offset `8` conf=`0.586107` salience=`0.623838`, offset `1` conf=`0.294953` salience=`0.204449`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `8`..`8` | type=`uint8` confidence=`0.9954`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`3` | type=`uint32` confidence=`0.9755`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `2`..`7` constant, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`discriminator` confidence=`0.9755`
- bytes `8`..`8` | label=`discriminator` confidence=`0.95`

#### Notes

- Echoes request fields from family_0 with up to 10 strong offset matches.
- Echoes request fields from family_6 with up to 9 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `654` (`1.0`)
- Repeated n-gram instances: `847`
- Top motifs: `0000`x1386, `000000`x732, `0003`x691, `000003`x654, `000301`x654

### family_10

- Role: `request`
- Messages: `313`
- Template: `?? ?? 00 00 00 ?? ?? 06 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??`
- Related families: `family_11`, `family_22`, `family_27`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`260` distinct=`5`
- Entropy summary: min=`1.040852` max=`7.218296` mean=`2.940413`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.406016` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.796875` confidence=`0.582135`
- Top discriminator candidates: offset `8` conf=`0.582135` salience=`0.623838`, offset `11` conf=`0.573878` salience=`0.607503`, offset `9` conf=`0.432175` salience=`0.327371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `6`..`6` | type=`uint8` confidence=`0.9904`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.9712`
- bytes `0`..`3` | type=`uint32` confidence=`0.5`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` discriminator
- header_end=`6` body_start=`6` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.9`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `313` (`1.0`)
- Repeated n-gram instances: `651`
- Top motifs: `0000`x805, `000000`x374, `06ff`x212, `0106`x195, `0600`x187

### family_8

- Role: `request`
- Messages: `201`
- Template: `00 ?? 00 00 00 ?? 01 05 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ??`
- Related families: `family_22`, `family_26`, `family_9`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`260` distinct=`4`
- Entropy summary: min=`1.207519` max=`7.223085` mean=`3.228578`
- Candidate discriminator offset: `11` cardinality=`4` entropy=`1.98489` salience=`0.607503` mutual_information=`0.560184` contrastive_separation=`0.8125` confidence=`0.611696`
- Top discriminator candidates: offset `11` conf=`0.611696` salience=`0.607503`, offset `8` conf=`0.585959` salience=`0.623838`, offset `9` conf=`0.440897` salience=`0.327371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.9851`
- bytes `11`..`11` | type=`uint8` confidence=`0.9801`
- bytes `0`..`3` | type=`uint32` confidence=`0.9154`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`discriminator` confidence=`0.95`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `201` (`1.0`)
- Repeated n-gram instances: `513`
- Top motifs: `0000`x569, `000000`x269, `0105`x196, `05ff`x97, `0105ff`x96

### family_27

- Role: `response`
- Messages: `195`
- Template: `00 ?? 00 00 00 03 01 86 ??`
- Related families: `family_10`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`2.281036` mean=`2.067604`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`0.989647` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.796875` confidence=`0.575222`
- Top discriminator candidates: offset `8` conf=`0.575222` salience=`0.623838`, offset `1` conf=`0.295416` salience=`0.204449`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`8` | type=`uint8` confidence=`0.9846`
- bytes `0`..`3` | type=`uint32` confidence=`0.9179`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `2`..`7` constant, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`discriminator` confidence=`0.95`
- bytes `8`..`8` | label=`discriminator` confidence=`0.95`

#### Notes

- Echoes request fields from family_10 with up to 9 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `195` (`1.0`)
- Repeated n-gram instances: `263`
- Top motifs: `0000`x418, `000000`x223, `0003`x207, `000003`x195, `000301`x195

### family_26

- Role: `response`
- Messages: `194`
- Template: `00 ?? 00 00 00 03 01 85 ??`
- Related families: `family_8`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`2.281036` mean=`2.071784`
- Candidate discriminator offset: `1` cardinality=`16` entropy=`3.998901` salience=`0.204449` mutual_information=`0.180786` contrastive_separation=`1.0` confidence=`0.295394`
- Top discriminator candidates: offset `1` conf=`0.295394` salience=`0.204449`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`8` | type=`uint8` confidence=`0.9897`
- bytes `0`..`3` | type=`uint32` confidence=`0.9175`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `2`..`7` constant, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `1`..`1` discriminator, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`discriminator` confidence=`0.9897`
- bytes `0`..`3` | label=`discriminator` confidence=`0.95`

#### Notes

- Echoes request fields from family_8 with up to 9 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `194` (`1.0`)
- Repeated n-gram instances: `254`
- Top motifs: `0000`x412, `000000`x218, `0003`x206, `000003`x194, `000301`x194

### family_11

- Role: `response`
- Messages: `118`
- Template: `?? ?? 00 00 00 06 ff 06 ?? ?? 00 ??`
- Related families: `family_10`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.551098` max=`2.751629` mean=`2.378573`
- Candidate discriminator offset: `11` cardinality=`6` entropy=`2.170739` salience=`0.607503` mutual_information=`0.560184` contrastive_separation=`0.84375` confidence=`0.591263`
- Top discriminator candidates: offset `11` conf=`0.591263` salience=`0.607503`, offset `9` conf=`0.458498` salience=`0.327371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.9831`
- bytes `0`..`3` | type=`uint32_be` confidence=`0.95` endian=`big`
- bytes `11`..`11` | type=`uint8` confidence=`0.9492`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `1`..`1` transaction_or_counter, `1`..`2` transaction_or_counter, `1`..`4` transaction_or_counter, `2`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `1`..`1` transaction_or_counter, `1`..`2` transaction_or_counter, `1`..`4` transaction_or_counter, `2`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `1`..`1` transaction_or_counter, `1`..`2` transaction_or_counter, `1`..`4` transaction_or_counter, `2`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`discriminator` confidence=`0.9831`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.95`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`
- bytes `8`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Echoes request fields from family_10 with up to 10 strong offset matches.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `118` (`1.0`)
- Repeated n-gram instances: `169`
- Top motifs: `0000`x285, `0006`x119, `000000`x118, `000006`x118, `0006ff`x116

### family_20

- Role: `request`
- Messages: `43`
- Template: `00 ?? 00 00 00 ?? ?? 2b 0e ?? ?? ?? b7 00 00 00 00 00`
- Related families: `family_32`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`18` distinct=`3`
- Entropy summary: min=`1.207519` max=`2.450826` mean=`1.858138`
- Candidate discriminator offset: `9` cardinality=`4` entropy=`1.202785` salience=`0.327371` mutual_information=`0.38445` contrastive_separation=`0.8125` confidence=`0.440425`
- Top discriminator candidates: offset `9` conf=`0.440425` salience=`0.327371`, offset `6` conf=`0.418429` salience=`0.420727`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`
- bytes `9`..`10` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`3` | type=`uint32` confidence=`0.9535`
- bytes `8`..`8` | type=`uint8` confidence=`0.9535`
- bytes `9`..`10` | type=`uint16` confidence=`0.907`
- bytes `6`..`6` | type=`uint8` confidence=`0.8837`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`discriminator` confidence=`0.9535`
- bytes `0`..`3` | label=`discriminator` confidence=`0.95`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `9`..`10` | label=`count_like` confidence=`0.88`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `43` (`1.0`)
- Repeated n-gram instances: `227`
- Top motifs: `0000`x178, `000000`x131, `2b0e`x41, `0100`x40, `000005`x35

### family_16

- Role: `request`
- Messages: `40`
- Template: `?? ?? 00 00 00 ?? ?? 10 ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 20 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 30 ?? ?? ?? 30 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 10 00 ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 6f 1b 00 00 00 25 ff 10 00 63 00 0f 1e 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 6f 1c 00 00 00 19 ff 10 00 59 00 09 12 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20`
- Related families: `family_17`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`13` max=`204` distinct=`7`
- Entropy summary: min=`1.14511` max=`4.502733` mean=`2.602109`
- Candidate discriminator offset: `11` cardinality=`6` entropy=`1.153056` salience=`0.607503` mutual_information=`0.560184` contrastive_separation=`0.84375` confidence=`0.568178`
- Top discriminator candidates: offset `11` conf=`0.568178` salience=`0.607503`, offset `8` conf=`0.560914` salience=`0.623838`, offset `9` conf=`0.418201` salience=`0.327371`
- Framing hypothesis: header=`0`..`23` body_start=`24` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`9` | kind=`variable` confidence=`1.0`
- bytes `10`..`11` | kind=`variable` confidence=`1.0`
- bytes `12`..`12` | kind=`variable` confidence=`1.0`
- bytes `13`..`14` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`3` | type=`uint32_le` confidence=`0.95` endian=`little`
- bytes `4`..`5` | type=`uint16_be` confidence=`0.925` endian=`big`
- bytes `6`..`6` | type=`uint8` confidence=`0.925`
- bytes `12`..`12` | type=`uint8` confidence=`0.925` endian=`big`
- bytes `10`..`11` | type=`uint16` confidence=`0.85`
- bytes `8`..`9` | type=`uint16` confidence=`0.825`
- bytes `13`..`14` | type=`uint16` confidence=`0.5`

#### Framing Hypotheses

- header_end=`24` body_start=`24` confidence=`1.0` fields=`0`..`0` discriminator, `0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `1`..`1` transaction_or_counter, `1`..`2` transaction_or_counter, `1`..`4` transaction_or_counter
- header_end=`25` body_start=`25` confidence=`1.0` fields=`0`..`0` discriminator, `0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `1`..`1` transaction_or_counter, `1`..`2` transaction_or_counter, `1`..`4` transaction_or_counter
- header_end=`26` body_start=`26` confidence=`1.0` fields=`0`..`0` discriminator, `0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `1`..`1` transaction_or_counter, `1`..`2` transaction_or_counter, `1`..`4` transaction_or_counter

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.95`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`length` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `10`..`11` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `12`..`12` | label=`length` confidence=`0.925`
- bytes `10`..`11` | label=`transaction_id` confidence=`0.9`

#### Notes

- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `40` (`1.0`)
- Repeated n-gram instances: `491`
- Top motifs: `0000`x181, `000000`x93, `2020`x91, `202020`x85, `1000`x45

### family_17

- Role: `response`
- Messages: `38`
- Template: `?? ?? 00 00 00 06 ?? 10 ?? ?? 00 ?? ?? ?? 00 00 00 06 ff 10 00 ?? 00 ?? ?? ?? 00 00 00 06 ff ?? 00 ?? 00 ?? 6f ?? 00 00 00 ?? ff ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 ?? ?? ?? 00 ?? ?? ?? 30 30 30 30 30 30 30 30 30 33 30 38 36 38 35 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 05 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 00 00 00 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 07 bc 00 00 07 be 00 00 35 60 00 01 00 01 00 00 00 28 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 68 61 6e 75 00 74 00 00 00 00 00 00 00 00 00 00 00 00 00 00 68 61 6e 75 00 74 00 00 00 00 00 00 00 00 00 00 00 00 00 00 68 00 6e 75 00 74 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 84`
- Related families: `family_16`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`243` distinct=`4`
- Entropy summary: min=`1.959148` max=`3.06732` mean=`2.243772`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`0.689509` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.796875` confidence=`0.562809`
- Top discriminator candidates: offset `8` conf=`0.562809` salience=`0.623838`, offset `6` conf=`0.387791` salience=`0.420727`
- Framing hypothesis: header=`0`..`15` body_start=`16` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `0`..`3` | type=`uint32_le` confidence=`0.95` endian=`little`
- bytes `6`..`6` | type=`uint8` confidence=`0.9211`
- bytes `11`..`11` | type=`uint8` confidence=`0.8684`
- bytes `8`..`10` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`16` body_start=`16` confidence=`1.0` fields=`0`..`0` discriminator, `0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `1`..`1` transaction_or_counter, `1`..`2` transaction_or_counter, `1`..`4` transaction_or_counter
- header_end=`17` body_start=`17` confidence=`1.0` fields=`0`..`0` discriminator, `0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `1`..`1` transaction_or_counter, `1`..`2` transaction_or_counter, `1`..`4` transaction_or_counter
- header_end=`26` body_start=`26` confidence=`1.0` fields=`0`..`0` discriminator, `0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `1`..`1` transaction_or_counter, `1`..`2` transaction_or_counter, `1`..`4` transaction_or_counter

#### Semantic Labels

- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_id` confidence=`0.95`
- bytes `4`..`5` | label=`length` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `11`..`11` | label=`discriminator` confidence=`0.95`
- bytes `11`..`11` | label=`length` confidence=`0.8158`

#### Notes

- Echoes request fields from family_16 with up to 10 strong offset matches.
- Response size is tied to request fields from family_16.
- Detected common protocol pattern: transaction ID, length field, discriminator

#### Feature Summary

- Messages with repetition: `38` (`1.0`)
- Repeated n-gram instances: `524`
- Top motifs: `0000`x276, `000000`x182, `0006`x49, `000006`x47, `1000`x42

### family_18

- Role: `request`
- Messages: `31`
- Template: `00 00 00 00 00 ?? ?? 11 ?? 00 ?? ?? 69 6e 67 70 61 74 68 20 4c 69 6d 69 74 65 64`
- Related families: `family_30`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`8` max=`27` distinct=`3`
- Entropy summary: min=`1.207519` max=`3.93027` mean=`1.817935`
- Candidate discriminator offset: `6` cardinality=`3` entropy=`1.140046` salience=`0.420727` mutual_information=`0.15832` contrastive_separation=`0.796875` confidence=`0.43615`
- Top discriminator candidates: offset `6` conf=`0.43615` salience=`0.420727`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16_be` confidence=`1.0` endian=`big`
- bytes `0`..`3` | type=`uint32` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.9032`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` discriminator
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `0`..`3` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `4`..`5` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `31` (`1.0`)
- Repeated n-gram instances: `165`
- Top motifs: `0000`x130, `000000`x97, `000002`x25, `0002`x25, `0111`x21

### family_32

- Role: `response`
- Messages: `29`
- Template: `00 00 00 00 00 03 ?? ab ??`
- Related families: `family_20`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.446617` max=`1.879965` mean=`1.689925`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`0.925501` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.796875` confidence=`0.567328`
- Top discriminator candidates: offset `8` conf=`0.567328` salience=`0.623838`, offset `6` conf=`0.406161` salience=`0.420727`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `0`..`3` | type=`uint32` confidence=`0.99`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`8` | type=`uint8` confidence=`0.8966`
- bytes `6`..`6` | type=`uint8` confidence=`0.8621`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `6`..`6` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `6`..`6` discriminator, `7`..`7` constant
- header_end=`6` body_start=`6` confidence=`0.973` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `0`..`3` | label=`constant` confidence=`0.99`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `8`..`8` | label=`discriminator` confidence=`0.9466`

#### Notes

- Echoes request fields from family_20 with up to 10 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `29` (`1.0`)
- Repeated n-gram instances: `145`
- Top motifs: `0000`x116, `000000`x87, `000003`x29, `0003`x29, `ab01`x23

### family_30

- Role: `response`
- Messages: `23`
- Template: `00 00 00 00 00 03 ?? 91 ??`
- Related families: `family_18`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`1.879965` mean=`1.715714`
- Candidate discriminator offset: `8` cardinality=`4` entropy=`1.453851` salience=`0.623838` mutual_information=`0.481368` contrastive_separation=`0.8125` confidence=`0.586096`
- Top discriminator candidates: offset `8` conf=`0.586096` salience=`0.623838`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `0`..`3` | type=`uint32` confidence=`0.99`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.913`
- bytes `8`..`8` | type=`uint8` confidence=`0.8261`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` constant
- header_end=`6` body_start=`6` confidence=`0.9647` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `0`..`3` | label=`constant` confidence=`0.99`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `8`..`8` | label=`discriminator` confidence=`0.8761`

#### Notes

- Echoes request fields from family_18 with up to 10 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `23` (`1.0`)
- Repeated n-gram instances: `115`
- Top motifs: `0000`x92, `000000`x69, `000003`x23, `0003`x23, `000301`x21

### family_21

- Role: `unknown`
- Messages: `22`
- Template: `?? ?? 00 00 00 03 ?? 80 01`
- Semantic confidence: `0.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.657743` max=`2.281036` mean=`1.90854`
- Candidate discriminator offset: `1` cardinality=`6` entropy=`2.413088` salience=`0.204449` mutual_information=`0.180786` contrastive_separation=`0.84375` confidence=`0.355235`
- Top discriminator candidates: offset `1` conf=`0.355235` salience=`0.204449`, offset `0` conf=`0.33564` salience=`0.137523`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`8` | type=`uint8` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.9091`
- bytes `0`..`3` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` discriminator, `1`..`1` discriminator, `2`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` discriminator, `1`..`1` discriminator, `2`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` discriminator, `1`..`1` discriminator, `2`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`

#### Notes

- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `22` (`1.0`)
- Repeated n-gram instances: `48`
- Top motifs: `0000`x52, `000000`x30, `0300`x26, `0003`x24, `000003`x22

### family_12

- Role: `request`
- Messages: `18`
- Template: `00 00 00 00 00 06 ?? 08 00 ?? 00 00`
- Related families: `family_13`
- Role hint: `request`
- Semantic confidence: `0.75`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.207519` max=`1.584963` mean=`1.505988`
- Candidate discriminator offset: `9` cardinality=`4` entropy=`1.891061` salience=`0.327371` mutual_information=`0.38445` contrastive_separation=`0.8125` confidence=`0.465076`
- Top discriminator candidates: offset `9` conf=`0.465076` salience=`0.327371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `0`..`3` | type=`uint32` confidence=`0.99`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.8889`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`0.9533` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.8605` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `0`..`3` | label=`constant` confidence=`0.99`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.95`
- bytes `8`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Echoes request fields from family_13 with up to 7 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `18` (`1.0`)
- Repeated n-gram instances: `116`
- Top motifs: `0000`x94, `000000`x58, `000006`x18, `0006`x18, `0800`x18

### family_13

- Role: `response`
- Messages: `10`
- Template: `00 00 00 00 00 06 ?? 08 00 ?? 00 00`
- Related families: `family_12`
- Role hint: `response`
- Semantic confidence: `0.75`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.207519` max=`1.584963` mean=`1.442807`
- Candidate discriminator offset: `9` cardinality=`3` entropy=`1.521928` salience=`0.327371` mutual_information=`0.38445` contrastive_separation=`0.796875` confidence=`0.450764`
- Top discriminator candidates: offset `9` conf=`0.450764` salience=`0.327371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `0`..`3` | type=`uint32` confidence=`0.99`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.8`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`0.952` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.8533` fields=`0`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`3` | label=`echoed_request_field` confidence=`1.0`
- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `0`..`3` | label=`constant` confidence=`0.99`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`3` | label=`transaction_or_correlation_id` confidence=`0.95`
- bytes `6`..`6` | label=`discriminator` confidence=`0.9`
- bytes `8`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Echoes request fields from family_12 with up to 7 strong offset matches.
- Detected common protocol pattern: length field, discriminator

#### Feature Summary

- Messages with repetition: `10` (`1.0`)
- Repeated n-gram instances: `68`
- Top motifs: `0000`x54, `000000`x34, `000006`x10, `0006`x10, `0800`x10

### family_28

- Role: `unknown`
- Messages: `8`
- Template: `00 00 00 00 00 03 0a 88 0b`
- Semantic confidence: `0.0`
- Length stats: min=`9` max=`9` distinct=`1`
- Entropy summary: min=`1.879965` max=`1.879965` mean=`1.879965`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`8` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `0`..`3` | type=`uint32` confidence=`0.99`
- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `6`..`6` | type=`uint8` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `8`..`8` | type=`uint8` confidence=`0.99`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`6` body_start=`6` confidence=`0.8417` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`0.75` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `0`..`3` | label=`constant` confidence=`0.99`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`

#### Feature Summary

- Messages with repetition: `8` (`1.0`)
- Repeated n-gram instances: `40`
- Top motifs: `0000`x32, `000000`x24, `000003`x8, `00030a`x8, `030a88`x8

### family_9

- Role: `response`
- Messages: `6`
- Template: `00 ?? 00 00 00 06 ?? 05 00 ?? 00 00`
- Related families: `family_8`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.207519` max=`1.947339` mean=`1.645177`
- Candidate discriminator offset: `9` cardinality=`3` entropy=`1.584963` salience=`0.327371` mutual_information=`0.38445` contrastive_separation=`0.796875` confidence=`0.454764`
- Top discriminator candidates: offset `9` conf=`0.454764` salience=`0.327371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`3` | kind=`variable` confidence=`1.0`
- bytes `4`..`5` | kind=`variable` confidence=`1.0`
- bytes `6`..`6` | kind=`variable` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`1.0`
- bytes `8`..`10` | kind=`variable` confidence=`1.0`
- bytes `11`..`11` | kind=`variable` confidence=`1.0`

#### Field Hypotheses

- bytes `4`..`5` | type=`uint16` confidence=`0.99`
- bytes `7`..`7` | type=`uint8` confidence=`0.99`
- bytes `11`..`11` | type=`uint8` confidence=`0.99`
- bytes `6`..`6` | type=`flags_or_status` confidence=`0.7`
- bytes `0`..`3` | type=`blob` confidence=`0.5`
- bytes `8`..`10` | type=`bytes` confidence=`0.5`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`0` constant, `2`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`0` constant, `2`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`0` constant, `2`..`5` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `4`..`5` | label=`length` confidence=`1.0`
- bytes `7`..`7` | label=`length` confidence=`1.0`
- bytes `4`..`5` | label=`constant` confidence=`0.99`
- bytes `7`..`7` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `8`..`10` | label=`payload` confidence=`0.7`

#### Notes

- Echoes request fields from family_8 with up to 5 strong offset matches.

#### Feature Summary

- Messages with repetition: `6` (`1.0`)
- Repeated n-gram instances: `36`
- Top motifs: `0000`x26, `000000`x14, `000006`x6, `000100`x6, `010000`x6
