# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: D:\tez\practical\protocol_re\data\05_families.json
- **source_feature_summary**: D:\tez\practical\protocol_re\data\03_family_features.json
- **source_keyword_summary**: D:\tez\practical\protocol_re\data\07_keywords.json
- **source_framing_summary**: D:\tez\practical\protocol_re\data\04_framing.json
- **source_relations_summary**: D:\tez\practical\protocol_re\data\08_relations.json
- **source_semantics_summary**: D:\tez\practical\protocol_re\data\09_semantics.json
- **framing_global_summary**: {'common_header_ends': [{'header_end': 8, 'family_count': 18, 'family_ratio': 0.6923}, {'header_end': 9, 'family_count': 4, 'family_ratio': 0.1538}, {'header_end': 6, 'family_count': 2, 'family_ratio': 0.0769}, {'header_end': 12, 'family_count': 1, 'family_ratio': 0.0385}, {'header_end': 7, 'family_count': 1, 'family_ratio': 0.0385}], 'field_type_counts': {'length': 91, 'constant': 16, 'discriminator': 16, 'transaction_or_counter': 5}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 26}
- **notes**: Initial auto-generated protocol model assembled from family summaries.

## Evaluation

- Messages: `200000` across `45340` sessions
- Corpus assignment coverage: `1` with `26` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `26` of `26`
- Pair hypotheses: `154658` direction_unknown_ratio=`0`
- Relation edges: `86` echo_edges=`86` length_relation_edges=`73`
- Semantic coverage: `26` of `26` families ratio=`1`
- Top semantic labels: `keyword`x107, `echoed_request_field`x50, `response_size_selector`x41, `constant`x34, `blob`x9, `transaction_or_correlation_id`x6, `length`x4
- Framing coverage: `26` of `26` families ratio=`1`
- Clustering diagnostics: warning_families=`25` split_candidates=`6` merge_candidates=`100`

### Clustering Diagnostic Warnings

- `family_2` | messages=`13385` split=`0.5` under_split=`0.5` over_split=`0.8543` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_5` | messages=`6570` split=`0.5` under_split=`0.5` over_split=`0.8543` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_1` | messages=`13839` split=`0.5` under_split=`0.5` over_split=`0.854` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_4` | messages=`7143` split=`0.5` under_split=`0.5` over_split=`0.854` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_12` | messages=`17668` split=`0.5` under_split=`0.5` over_split=`0.7985` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_17` | messages=`12179` split=`0.5` under_split=`0.5` over_split=`0.7985` warnings=high latent dispersion, low latent silhouette, possible over-split merge candidate
- `family_0` | messages=`8476` split=`0.2` under_split=`0.2` over_split=`0.857` warnings=low latent silhouette, possible over-split merge candidate
- `family_6` | messages=`4145` split=`0.2` under_split=`0.2` over_split=`0.857` warnings=low latent silhouette, possible over-split merge candidate
- `family_11` | messages=`17584` split=`0.2` under_split=`0.2` over_split=`0.809` warnings=low latent silhouette, possible over-split merge candidate
- `family_16` | messages=`13326` split=`0.2` under_split=`0.2` over_split=`0.809` warnings=low latent silhouette, possible over-split merge candidate

### Clustering Merge Candidates

- `family_0` -> `family_6` distance=`0.0023` score=`0.857`
- `family_6` -> `family_0` distance=`0.0023` score=`0.857`
- `family_2` -> `family_5` distance=`0.0023` score=`0.8543`
- `family_5` -> `family_2` distance=`0.0023` score=`0.8543`
- `family_1` -> `family_4` distance=`0.0023` score=`0.854`
- `family_4` -> `family_1` distance=`0.0023` score=`0.854`
- `family_11` -> `family_16` distance=`0.003` score=`0.809`
- `family_16` -> `family_11` distance=`0.003` score=`0.809`
- `family_17` -> `family_12` distance=`0.0032` score=`0.7985`
- `family_12` -> `family_17` distance=`0.0032` score=`0.7985`

### Evaluation Top Relation Edges

- `family_17` -> `family_2` | pairs=`11297` avg_score=`6.4362` support=`0.9279` lift=`10.7213` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_16` -> `family_1` | pairs=`10941` avg_score=`6.4361` support=`0.8363` lift=`9.3465` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_18` -> `family_0` | pairs=`6585` avg_score=`6.4363` support=`0.9404` lift=`17.1599` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_1` -> `family_12` | pairs=`6382` avg_score=`4.9375` support=`0.4764` lift=`4.5026` direction=`1` order=`1` echo_fields=`20` length_rules=`0`
- `family_12` -> `family_5` | pairs=`5734` avg_score=`6.4362` support=`0.3249` lift=`7.6484` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_4` | pairs=`5354` avg_score=`6.4361` support=`0.3276` lift=`7.0927` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_22` | pairs=`5056` avg_score=`6.4647` support=`0.3093` lift=`8.0599` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_13` | pairs=`4769` avg_score=`6.4673` support=`0.2702` lift=`8.6762` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_14` | pairs=`4673` avg_score=`6.4672` support=`0.2859` lift=`8.973` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_1` -> `family_17` | pairs=`4220` avg_score=`4.9375` support=`0.315` lift=`4.3253` direction=`1` order=`1` echo_fields=`20` length_rules=`0`

## Final Ground Truth Evaluation

- Overall score: `0.2418`
- Verdict: `fail`
- Matched message types: `11` of `11`
- Message type matching: accuracy=`0.4231` precision=`0.4231` recall=`1` f1=`0.5946`
- Field boundary: accuracy=`0.125` precision=`0.1364` recall=`0.6` f1=`0.2222`
- Field semantics: accuracy=`0` precision=`0` recall=`0` f1=`0`
- Relations: accuracy=`0.0814` precision=`0.0814` recall=`1` f1=`0.1505`

## LLM Analysis

- Prompt size: `437807` bytes, `437807` characters, estimated tokens=`109452`

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `86`
- Strongest edges:
- `family_17` -> `family_2` | pairs=`11297` avg_score=`6.4362` support=`0.9279` lift=`10.7213` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_16` -> `family_1` | pairs=`10941` avg_score=`6.4361` support=`0.8363` lift=`9.3465` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_18` -> `family_0` | pairs=`6585` avg_score=`6.4363` support=`0.9404` lift=`17.1599` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_1` -> `family_12` | pairs=`6382` avg_score=`4.9375` support=`0.4764` lift=`4.5026` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_12` -> `family_5` | pairs=`5734` avg_score=`6.4362` support=`0.3249` lift=`7.6484` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_4` | pairs=`5354` avg_score=`6.4361` support=`0.3276` lift=`7.0927` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_22` | pairs=`5056` avg_score=`6.4647` support=`0.3093` lift=`8.0599` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_13` | pairs=`4769` avg_score=`6.4673` support=`0.2702` lift=`8.6762` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_14` | pairs=`4673` avg_score=`6.4672` support=`0.2859` lift=`8.973` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_1` -> `family_17` | pairs=`4220` avg_score=`4.9375` support=`0.315` lift=`4.3253` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_12` -> `family_24` | pairs=`3753` avg_score=`6.4658` support=`0.2127` lift=`4.8819` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_10` -> `family_6` | pairs=`3681` avg_score=`6.4362` support=`0.3109` lift=`11.6011` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_2` -> `family_10` | pairs=`3630` avg_score=`4.9375` support=`0.5424` lift=`7.16` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_4` -> `family_12` | pairs=`3234` avg_score=`4.9375` support=`0.4653` lift=`4.3978` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_22` -> `family_12` | pairs=`2886` avg_score=`4.9688` support=`0.5034` lift=`4.7577` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_10` -> `family_7` | pairs=`2828` avg_score=`6.4672` support=`0.2389` lift=`12.9763` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_10` -> `family_21` | pairs=`2759` avg_score=`6.4663` support=`0.233` lift=`12.2135` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_19` -> `family_3` | pairs=`2473` avg_score=`6.4352` support=`0.437` lift=`14.4322` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`20`
- `family_14` -> `family_12` | pairs=`2466` avg_score=`4.9688` support=`0.5168` lift=`4.884` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_2` -> `family_18` | pairs=`2412` avg_score=`4.9375` support=`0.3604` lift=`8.0379` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_4` -> `family_17` | pairs=`2239` avg_score=`4.9375` support=`0.3222` lift=`4.4233` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_22` -> `family_17` | pairs=`2146` avg_score=`4.9688` support=`0.3743` lift=`5.1396` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_15` -> `family_9` | pairs=`2135` avg_score=`6.4668` support=`0.2318` lift=`15.9519` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_15` -> `family_1` | pairs=`1997` avg_score=`6.4359` support=`0.2168` lift=`2.4227` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_20` -> `family_3` | pairs=`1993` avg_score=`6.4361` support=`0.379` lift=`12.518` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`

## Families

- Total families: `26`
- Families shown below: `26`

### family_12

- Role: `request`
- Messages: `17668`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_1`, `family_13`, `family_14`, `family_22`, `family_23`, `family_24`, `family_4`, `family_5`, `family_8`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5049`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.221252` max=`2.617492` mean=`2.449028`
- Candidate discriminator offset: `10` cardinality=`2` entropy=`0.01046` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`0.78125` confidence=`0.622134`
- Top discriminator candidates: offset `10` conf=`0.622134` salience=`1.0`, offset `9` conf=`0.552585` salience=`0.668347`, offset `7` conf=`0.384829` salience=`0.244371`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.696`
- bytes `1`..`1` | kind=`variable` confidence=`0.6467`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7902`
- bytes `10`..`11` | kind=`variable` confidence=`0.5437`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9996`
- bytes `10`..`11` | type=`keyword` confidence=`0.9993`
- bytes `0`..`0` | type=`keyword` confidence=`0.9972`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9857`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9997`
- bytes `9`..`9` | label=`keyword` confidence=`0.9996`
- bytes `10`..`11` | label=`keyword` confidence=`0.9993`
- bytes `0`..`0` | label=`keyword` confidence=`0.9972`

#### Notes

- Echoes request fields from family_1 with up to 20 strong offset matches.
- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.
- Echoes request fields from family_22 with up to 20 strong offset matches.
- Response size is tied to request fields from family_22.

#### Feature Summary

- Messages with repetition: `17668` (`1.0`)
- Repeated n-gram instances: `17668`
- Top motifs: `0000`x35336, `000000`x17668, `000006`x17668, `000601`x17668, `0006`x17668

### family_11

- Role: `request`
- Messages: `17584`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? ?? ??`
- Related families: `family_11`, `family_14`, `family_22`, `family_4`, `family_8`
- Role hint: `request`
- Semantic confidence: `0.9983`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.221252` max=`2.617492` mean=`2.439861`
- Candidate discriminator offset: `10` cardinality=`2` entropy=`0.373123` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`0.78125` confidence=`0.626397`
- Top discriminator candidates: offset `10` conf=`0.626397` salience=`1.0`, offset `9` conf=`0.547053` salience=`0.668347`, offset `7` conf=`0.382853` salience=`0.244371`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6974`
- bytes `1`..`1` | kind=`variable` confidence=`0.6473`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7861`
- bytes `10`..`11` | kind=`variable` confidence=`0.5365`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9995`
- bytes `10`..`11` | type=`keyword` confidence=`0.9993`
- bytes `0`..`0` | type=`keyword` confidence=`0.9972`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9856`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9997`
- bytes `9`..`9` | label=`keyword` confidence=`0.9995`
- bytes `10`..`11` | label=`keyword` confidence=`0.9993`
- bytes `0`..`0` | label=`keyword` confidence=`0.9972`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.

#### Feature Summary

- Messages with repetition: `17584` (`1.0`)
- Repeated n-gram instances: `18823`
- Top motifs: `0000`x36407, `000000`x17584, `000006`x17584, `000601`x17584, `0006`x17584

### family_1

- Role: `response`
- Messages: `13839`
- Template: `?? ?? 00 00 00 04 01 01 01 00`
- Related families: `family_12`, `family_15`, `family_16`, `family_17`, `family_19`, `family_20`, `noise`
- Role hint: `response`
- Semantic confidence: `0.5294`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.685475` max=`2.046439` mean=`2.03889`
- Candidate discriminator offset: `0` cardinality=`51` entropy=`5.628842` salience=`0.396297` mutual_information=`0.205723` contrastive_separation=`1.0` confidence=`0.326976`
- Top discriminator candidates: offset `0` conf=`0.326976` salience=`0.396297`, offset `1` conf=`0.222121` salience=`0.165443`
- Framing hypothesis: header=`0`..`8` body_start=`9` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6947`
- bytes `1`..`1` | kind=`variable` confidence=`0.6475`
- bytes `2`..`8` | kind=`constant` confidence=`0.85`
- bytes `9`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `9`..`9` | type=`length` confidence=`0.9968` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9963`
- bytes `2`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9817`

#### Framing Hypotheses

- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `8`..`8` length, `9`..`9` length
- header_end=`8` body_start=`8` confidence=`0.8462` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `9`..`9` | label=`length` confidence=`0.9968`
- bytes `0`..`0` | label=`keyword` confidence=`0.9963`
- bytes `2`..`8` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9817`

#### Notes

- Echoes request fields from family_15 with up to 20 strong offset matches.
- Response size is tied to request fields from family_15.
- Echoes request fields from family_16 with up to 20 strong offset matches.
- Response size is tied to request fields from family_16.
- Echoes request fields from family_19 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `13839` (`1.0`)
- Repeated n-gram instances: `27766`
- Top motifs: `0101`x27722, `0000`x27678, `010101`x13883, `000000`x13839, `000004`x13839

### family_2

- Role: `response`
- Messages: `13385`
- Template: `?? ?? 00 00 00 04 01 01 01 00`
- Related families: `family_10`, `family_15`, `family_17`, `family_18`, `family_20`
- Role hint: `response`
- Semantic confidence: `0.6668`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`2.046439` max=`2.046439` mean=`2.046439`
- Candidate discriminator offset: `0` cardinality=`51` entropy=`5.604407` salience=`0.396297` mutual_information=`0.205723` contrastive_separation=`1.0` confidence=`0.326927`
- Top discriminator candidates: offset `0` conf=`0.326927` salience=`0.396297`, offset `1` conf=`0.222093` salience=`0.165443`
- Framing hypothesis: header=`0`..`8` body_start=`9` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6953`
- bytes `1`..`1` | kind=`variable` confidence=`0.6477`
- bytes `2`..`8` | kind=`constant` confidence=`0.85`
- bytes `9`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `9`..`9` | type=`length` confidence=`0.9974` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9962`
- bytes `2`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9811`

#### Framing Hypotheses

- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `8`..`8` length, `9`..`9` length
- header_end=`8` body_start=`8` confidence=`0.8462` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `9`..`9` | label=`length` confidence=`0.9974`
- bytes `0`..`0` | label=`keyword` confidence=`0.9962`
- bytes `2`..`8` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9811`

#### Notes

- Echoes request fields from family_15 with up to 20 strong offset matches.
- Response size is tied to request fields from family_15.
- Echoes request fields from family_17 with up to 20 strong offset matches.
- Response size is tied to request fields from family_17.
- Echoes request fields from family_20 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `13385` (`1.0`)
- Repeated n-gram instances: `26840`
- Top motifs: `0101`x26805, `0000`x26770, `010101`x13420, `000000`x13385, `000004`x13385

### family_16

- Role: `request`
- Messages: `13326`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_1`, `family_22`, `family_4`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.896241` max=`2.450826` mean=`2.225284`
- Candidate discriminator offset: `10` cardinality=`2` entropy=`0.131844` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`0.78125` confidence=`0.623179`
- Top discriminator candidates: offset `10` conf=`0.623179` salience=`1.0`, offset `9` conf=`0.567312` salience=`0.668347`, offset `11` conf=`0.362795` salience=`0.419519`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6946`
- bytes `1`..`1` | kind=`variable` confidence=`0.6493`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7639`
- bytes `10`..`11` | kind=`variable` confidence=`0.542`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9997`
- bytes `7`..`7` | type=`keyword` confidence=`0.9995`
- bytes `9`..`9` | type=`keyword` confidence=`0.9994`
- bytes `0`..`0` | type=`keyword` confidence=`0.9961`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9808`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`keyword` confidence=`0.9997`
- bytes `7`..`7` | label=`keyword` confidence=`0.9995`
- bytes `9`..`9` | label=`keyword` confidence=`0.9994`
- bytes `0`..`0` | label=`keyword` confidence=`0.9961`

#### Feature Summary

- Messages with repetition: `13326` (`1.0`)
- Repeated n-gram instances: `13776`
- Top motifs: `0000`x26953, `000000`x13383, `0006`x13330, `000006`x13326, `000601`x13326

### family_17

- Role: `request`
- Messages: `12179`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_1`, `family_14`, `family_2`, `family_22`, `family_4`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5044`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.450826` mean=`2.229676`
- Candidate discriminator offset: `9` cardinality=`7` entropy=`2.211354` salience=`0.668347` mutual_information=`0.327788` contrastive_separation=`0.859375` confidence=`0.572881`
- Top discriminator candidates: offset `9` conf=`0.572881` salience=`0.668347`, offset `11` conf=`0.41621` salience=`0.419519`, offset `7` conf=`0.354229` salience=`0.244371`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6958`
- bytes `1`..`1` | kind=`variable` confidence=`0.6493`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7705`
- bytes `10`..`11` | kind=`variable` confidence=`0.5449`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9994`
- bytes `0`..`0` | type=`keyword` confidence=`0.9958`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.979`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`keyword` confidence=`0.9997`
- bytes `9`..`9` | label=`keyword` confidence=`0.9994`
- bytes `0`..`0` | label=`keyword` confidence=`0.9958`
- bytes `8`..`8` | label=`constant` confidence=`0.99`

#### Notes

- Echoes request fields from family_1 with up to 20 strong offset matches.
- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.
- Echoes request fields from family_22 with up to 20 strong offset matches.
- Response size is tied to request fields from family_22.

#### Feature Summary

- Messages with repetition: `12179` (`1.0`)
- Repeated n-gram instances: `12403`
- Top motifs: `0000`x24418, `000000`x12239, `0006`x12183, `000006`x12179, `000601`x12179

### family_10

- Role: `request`
- Messages: `11864`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_13`, `family_2`, `family_21`, `family_23`, `family_24`, `family_3`, `family_5`, `family_6`, `family_7`, `family_8`
- Role hint: `request`
- Semantic confidence: `0.5132`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.221252` max=`2.617492` mean=`2.438849`
- Candidate discriminator offset: `10` cardinality=`2` entropy=`0.01796` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`0.78125` confidence=`0.622181`
- Top discriminator candidates: offset `10` conf=`0.622181` salience=`1.0`, offset `9` conf=`0.556001` salience=`0.668347`, offset `7` conf=`0.383037` salience=`0.244371`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7087`
- bytes `1`..`1` | kind=`variable` confidence=`0.6504`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7838`
- bytes `10`..`11` | kind=`variable` confidence=`0.5444`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9995`
- bytes `9`..`9` | type=`keyword` confidence=`0.9994`
- bytes `10`..`11` | type=`keyword` confidence=`0.9992`
- bytes `0`..`0` | type=`keyword` confidence=`0.997`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9787`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9995`
- bytes `9`..`9` | label=`keyword` confidence=`0.9994`
- bytes `10`..`11` | label=`keyword` confidence=`0.9992`
- bytes `0`..`0` | label=`keyword` confidence=`0.997`

#### Notes

- Echoes request fields from family_13 with up to 20 strong offset matches.
- Response size is tied to request fields from family_13.
- Echoes request fields from family_2 with up to 20 strong offset matches.
- Echoes request fields from family_23 with up to 20 strong offset matches.
- Response size is tied to request fields from family_23.

#### Feature Summary

- Messages with repetition: `11864` (`1.0`)
- Repeated n-gram instances: `11866`
- Top motifs: `0000`x23728, `000000`x11864, `000006`x11864, `000601`x11864, `0006`x11864

### family_15

- Role: `request`
- Messages: `10073`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? ?? ??`
- Related families: `family_1`, `family_2`, `family_23`, `family_24`, `family_3`, `family_4`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.6804`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.896241` max=`2.617492` mean=`2.320139`
- Candidate discriminator offset: `10` cardinality=`2` entropy=`0.423558` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`0.78125` confidence=`0.62725`
- Top discriminator candidates: offset `10` conf=`0.62725` salience=`1.0`, offset `9` conf=`0.563442` salience=`0.668347`, offset `7` conf=`0.376728` salience=`0.244371`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6827`
- bytes `1`..`1` | kind=`variable` confidence=`0.6825`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7598`
- bytes `10`..`11` | kind=`variable` confidence=`0.5355`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9995`
- bytes `7`..`7` | type=`keyword` confidence=`0.9994`
- bytes `9`..`9` | type=`keyword` confidence=`0.9992`
- bytes `1`..`1` | type=`keyword` confidence=`0.9912`
- bytes `0`..`0` | type=`keyword` confidence=`0.991`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`keyword` confidence=`0.9995`
- bytes `7`..`7` | label=`keyword` confidence=`0.9994`
- bytes `9`..`9` | label=`keyword` confidence=`0.9992`
- bytes `1`..`1` | label=`keyword` confidence=`0.9912`

#### Notes

- Echoes request fields from family_1 with up to 20 strong offset matches.
- Echoes request fields from family_23 with up to 20 strong offset matches.
- Response size is tied to request fields from family_23.
- Echoes request fields from family_3 with up to 20 strong offset matches.
- Response size is tied to request fields from family_3.

#### Feature Summary

- Messages with repetition: `10073` (`1.0`)
- Repeated n-gram instances: `10943`
- Top motifs: `0000`x21002, `0006`x10075, `000000`x10073, `000006`x10073, `000601`x10073

### family_0

- Role: `response`
- Messages: `8476`
- Template: `?? ?? 00 00 00 04 01 01 01 00`
- Related families: `family_18`, `family_20`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`2.046439` max=`2.046439` mean=`2.046439`
- Candidate discriminator offset: `0` cardinality=`35` entropy=`5.020203` salience=`0.396297` mutual_information=`0.205723` contrastive_separation=`1.0` confidence=`0.326142`
- Top discriminator candidates: offset `0` conf=`0.326142` salience=`0.396297`, offset `1` conf=`0.222126` salience=`0.165443`
- Framing hypothesis: header=`0`..`8` body_start=`9` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7085`
- bytes `1`..`1` | kind=`variable` confidence=`0.6519`
- bytes `2`..`8` | kind=`constant` confidence=`0.85`
- bytes `9`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `9`..`9` | type=`length` confidence=`0.9976` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9959`
- bytes `2`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9702`

#### Framing Hypotheses

- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `8`..`8` length, `9`..`9` length
- header_end=`8` body_start=`8` confidence=`0.8464` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `9`..`9` | label=`length` confidence=`0.9976`
- bytes `0`..`0` | label=`keyword` confidence=`0.9959`
- bytes `2`..`8` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9702`

#### Notes

- Echoes request fields from family_18 with up to 20 strong offset matches.
- Response size is tied to request fields from family_18.
- Echoes request fields from family_20 with up to 20 strong offset matches.
- Response size is tied to request fields from family_20.

#### Feature Summary

- Messages with repetition: `8476` (`1.0`)
- Repeated n-gram instances: `16992`
- Top motifs: `0101`x16972, `0000`x16952, `010101`x8496, `000000`x8476, `000004`x8476

### family_4

- Role: `response`
- Messages: `7143`
- Template: `?? ?? 00 00 00 04 01 02 01 00`
- Related families: `family_11`, `family_12`, `family_15`, `family_16`, `family_17`, `family_19`, `family_20`
- Role hint: `response`
- Semantic confidence: `0.5246`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.685475` max=`2.370951` mean=`2.287873`
- Candidate discriminator offset: `0` cardinality=`52` entropy=`5.636488` salience=`0.396297` mutual_information=`0.205723` contrastive_separation=`1.0` confidence=`0.32543`
- Top discriminator candidates: offset `0` conf=`0.32543` salience=`0.396297`, offset `1` conf=`0.222097` salience=`0.165443`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6958`
- bytes `1`..`1` | kind=`variable` confidence=`0.6541`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.9997`
- bytes `0`..`0` | type=`keyword` confidence=`0.9927`
- bytes `1`..`1` | type=`keyword` confidence=`0.9647`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`9` | label=`keyword` confidence=`0.9997`
- bytes `0`..`0` | label=`keyword` confidence=`0.9927`
- bytes `2`..`7` | label=`response_size_selector` confidence=`0.9903`
- bytes `1`..`1` | label=`keyword` confidence=`0.9647`
- bytes `8`..`9` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.
- Echoes request fields from family_15 with up to 20 strong offset matches.
- Response size is tied to request fields from family_15.
- Echoes request fields from family_16 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `7143` (`1.0`)
- Repeated n-gram instances: `7368`
- Top motifs: `0000`x14286, `000000`x7143, `000004`x7143, `000401`x7143, `0004`x7143

### family_18

- Role: `request`
- Messages: `7006`
- Template: `?? ?? 00 00 00 06 01 01 00 ?? 00 01`
- Related families: `family_0`, `family_13`, `family_2`, `family_23`, `family_24`, `family_5`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5279`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.450826` mean=`2.227317`
- Candidate discriminator offset: `9` cardinality=`7` entropy=`2.210718` salience=`0.668347` mutual_information=`0.327788` contrastive_separation=`0.859375` confidence=`0.574361`
- Top discriminator candidates: offset `9` conf=`0.574361` salience=`0.668347`, offset `11` conf=`0.408381` salience=`0.419519`, offset `7` conf=`0.353125` salience=`0.244371`
- Framing hypothesis: header=`0`..`8` body_start=`9` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7108`
- bytes `1`..`1` | kind=`variable` confidence=`0.6556`
- bytes `2`..`8` | kind=`variable` confidence=`0.85`
- bytes `9`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`11` | kind=`variable` confidence=`0.5449`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9996`
- bytes `9`..`9` | type=`keyword` confidence=`0.999`
- bytes `0`..`0` | type=`keyword` confidence=`0.9951`
- bytes `1`..`1` | type=`keyword` confidence=`0.9635`
- bytes `2`..`8` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`9` body_start=`9` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `9`..`9` discriminator
- header_end=`11` body_start=`11` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `9`..`9` discriminator

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`keyword` confidence=`0.9996`
- bytes `9`..`9` | label=`keyword` confidence=`0.999`
- bytes `0`..`0` | label=`keyword` confidence=`0.9951`
- bytes `1`..`1` | label=`keyword` confidence=`0.9635`
- bytes `2`..`8` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_13 with up to 20 strong offset matches.
- Response size is tied to request fields from family_13.
- Echoes request fields from family_2 with up to 20 strong offset matches.
- Echoes request fields from family_23 with up to 20 strong offset matches.
- Response size is tied to request fields from family_23.

#### Feature Summary

- Messages with repetition: `7006` (`1.0`)
- Repeated n-gram instances: `7106`
- Top motifs: `0000`x14033, `000000`x7027, `0006`x7008, `000006`x7006, `000601`x7006

### family_24

- Role: `response`
- Messages: `6737`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_10`, `family_12`, `family_15`, `family_18`
- Role hint: `response`
- Semantic confidence: `0.7044`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.40401` max=`3.027169` mean=`2.813989`
- Candidate discriminator offset: `10` cardinality=`56` entropy=`4.292113` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`1.0` confidence=`0.56953`
- Top discriminator candidates: offset `10` conf=`0.56953` salience=`1.0`, offset `9` conf=`0.528701` salience=`0.668347`, offset `0` conf=`0.327074` salience=`0.396297`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6844`
- bytes `1`..`1` | kind=`variable` confidence=`0.6664`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7939`
- bytes `10`..`10` | kind=`variable` confidence=`0.7264`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9985`
- bytes `10`..`10` | type=`keyword` confidence=`0.9917`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9874`
- bytes `1`..`1` | type=`keyword` confidence=`0.9722`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `7`..`7` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `7`..`7` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9997`
- bytes `9`..`9` | label=`keyword` confidence=`0.9985`
- bytes `10`..`10` | label=`keyword` confidence=`0.9917`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9874`
- bytes `1`..`1` | label=`keyword` confidence=`0.9722`

#### Notes

- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_15 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `6737` (`1.0`)
- Repeated n-gram instances: `6793`
- Top motifs: `0000`x13507, `0005`x6760, `000000`x6737, `000005`x6737, `000501`x6737

### family_5

- Role: `response`
- Messages: `6570`
- Template: `?? ?? 00 00 00 04 01 02 01 00`
- Related families: `family_10`, `family_12`, `family_18`, `family_20`
- Role hint: `response`
- Semantic confidence: `0.6428`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.846439` max=`2.370951` mean=`2.322925`
- Candidate discriminator offset: `0` cardinality=`50` entropy=`5.599821` salience=`0.396297` mutual_information=`0.205723` contrastive_separation=`1.0` confidence=`0.326906`
- Top discriminator candidates: offset `0` conf=`0.326906` salience=`0.396297`, offset `1` conf=`0.222014` salience=`0.165443`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6967`
- bytes `1`..`1` | kind=`variable` confidence=`0.6554`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.9997`
- bytes `0`..`0` | type=`keyword` confidence=`0.9924`
- bytes `1`..`1` | type=`keyword` confidence=`0.9616`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`9` | label=`keyword` confidence=`0.9997`
- bytes `0`..`0` | label=`keyword` confidence=`0.9924`
- bytes `1`..`1` | label=`keyword` confidence=`0.9616`
- bytes `8`..`9` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.

#### Feature Summary

- Messages with repetition: `6570` (`1.0`)
- Repeated n-gram instances: `6576`
- Top motifs: `0000`x13140, `000000`x6570, `000004`x6570, `000401`x6570, `0004`x6570

### family_19

- Role: `request`
- Messages: `6391`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? ?? ?? 00 04 00 00 00 06 01 01 00 0e 00 01`
- Related families: `family_1`, `family_14`, `family_22`, `family_23`, `family_3`, `family_4`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `0.8545`
- Length stats: min=`12` max=`24` distinct=`2`
- Entropy summary: min=`1.650022` max=`2.617492` mean=`2.295655`
- Candidate discriminator offset: `10` cardinality=`2` entropy=`0.518964` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`0.78125` confidence=`0.629065`
- Top discriminator candidates: offset `10` conf=`0.629065` salience=`1.0`, offset `9` conf=`0.563694` salience=`0.668347`, offset `7` conf=`0.378576` salience=`0.244371`
- Framing hypothesis: header=`0`..`11` body_start=`12` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6983`
- bytes `1`..`1` | kind=`variable` confidence=`0.6884`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.7709`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7596`
- bytes `10`..`11` | kind=`variable` confidence=`0.85`
- bytes `12`..`23` | kind=`constant` confidence=`0.85`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9992`
- bytes `7`..`7` | type=`keyword` confidence=`0.9991`
- bytes `9`..`9` | type=`keyword` confidence=`0.9987`
- bytes `0`..`0` | type=`keyword` confidence=`0.9905`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `12`..`23` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.989`

#### Framing Hypotheses

- header_end=`12` body_start=`12` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`13` body_start=`13` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`18` body_start=`18` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `12`..`23` | label=`echoed_request_field` confidence=`1.0`
- bytes `12`..`23` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`keyword` confidence=`0.9992`

#### Notes

- Echoes request fields from family_1 with up to 20 strong offset matches.
- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.
- Echoes request fields from family_22 with up to 20 strong offset matches.
- Response size is tied to request fields from family_22.

#### Feature Summary

- Messages with repetition: `6391` (`1.0`)
- Repeated n-gram instances: `7640`
- Top motifs: `0000`x13636, `000000`x6512, `0006`x6395, `0601`x6395, `000006`x6392

### family_22

- Role: `response`
- Messages: `5937`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_11`, `family_12`, `family_16`, `family_17`, `family_19`
- Role hint: `response`
- Semantic confidence: `0.5248`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.40401` max=`2.845351` mean=`2.727383`
- Candidate discriminator offset: `10` cardinality=`42` entropy=`3.694903` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`1.0` confidence=`0.56761`
- Top discriminator candidates: offset `10` conf=`0.56761` salience=`1.0`, offset `9` conf=`0.545129` salience=`0.668347`, offset `0` conf=`0.326627` salience=`0.396297`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6965`
- bytes `1`..`1` | kind=`variable` confidence=`0.6579`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7394`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.999`
- bytes `10`..`10` | type=`keyword` confidence=`0.9929`
- bytes `0`..`0` | type=`keyword` confidence=`0.9897`
- bytes `1`..`1` | type=`keyword` confidence=`0.9569`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`9` | label=`keyword` confidence=`0.999`
- bytes `10`..`10` | label=`keyword` confidence=`0.9929`
- bytes `0`..`0` | label=`keyword` confidence=`0.9897`
- bytes `1`..`1` | label=`keyword` confidence=`0.9569`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.
- Echoes request fields from family_16 with up to 20 strong offset matches.
- Response size is tied to request fields from family_16.

#### Feature Summary

- Messages with repetition: `5937` (`1.0`)
- Repeated n-gram instances: `6084`
- Top motifs: `0000`x11922, `0005`x6023, `000000`x5950, `000005`x5937, `000501`x5937

### family_23

- Role: `response`
- Messages: `5613`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_10`, `family_12`, `family_15`, `family_18`, `family_19`, `family_20`
- Role hint: `response`
- Semantic confidence: `0.6331`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.040373` max=`3.027169` mean=`2.827391`
- Candidate discriminator offset: `10` cardinality=`67` entropy=`4.959942` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`1.0` confidence=`0.573908`
- Top discriminator candidates: offset `10` conf=`0.573908` salience=`1.0`, offset `9` conf=`0.543575` salience=`0.668347`, offset `7` conf=`0.362102` salience=`0.244371`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6798`
- bytes `1`..`1` | kind=`variable` confidence=`0.6838`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7902`
- bytes `10`..`10` | kind=`variable` confidence=`0.7127`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9996`
- bytes `9`..`9` | type=`keyword` confidence=`0.9984`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9881`
- bytes `1`..`1` | type=`keyword` confidence=`0.9852`
- bytes `0`..`0` | type=`keyword` confidence=`0.9824`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9996`
- bytes `9`..`9` | label=`keyword` confidence=`0.9984`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9881`
- bytes `1`..`1` | label=`keyword` confidence=`0.9852`
- bytes `0`..`0` | label=`keyword` confidence=`0.9824`

#### Notes

- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_19 with up to 20 strong offset matches.
- Response size is tied to request fields from family_19.
- Echoes request fields from family_20 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `5613` (`1.0`)
- Repeated n-gram instances: `5918`
- Top motifs: `0000`x11361, `000000`x5687, `0005`x5675, `0501`x5614, `000005`x5613

### family_20

- Role: `request`
- Messages: `5266`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_0`, `family_1`, `family_13`, `family_2`, `family_23`, `family_3`, `family_4`, `family_5`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5144`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.896241` max=`2.617492` mean=`2.32746`
- Candidate discriminator offset: `10` cardinality=`2` entropy=`0.019905` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`0.78125` confidence=`0.634217`
- Top discriminator candidates: offset `10` conf=`0.634217` salience=`1.0`, offset `9` conf=`0.567371` salience=`0.668347`, offset `11` conf=`0.415411` salience=`0.419519`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7031`
- bytes `1`..`1` | kind=`variable` confidence=`0.69`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7658`
- bytes `10`..`11` | kind=`variable` confidence=`0.5446`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9992`
- bytes `7`..`7` | type=`keyword` confidence=`0.9989`
- bytes `9`..`9` | type=`keyword` confidence=`0.9987`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9875`
- bytes `0`..`0` | type=`keyword` confidence=`0.9865`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`keyword` confidence=`0.9992`
- bytes `7`..`7` | label=`keyword` confidence=`0.9989`
- bytes `9`..`9` | label=`keyword` confidence=`0.9987`
- bytes `2`..`6` | label=`constant` confidence=`0.99`

#### Notes

- Echoes request fields from family_1 with up to 20 strong offset matches.
- Echoes request fields from family_13 with up to 20 strong offset matches.
- Response size is tied to request fields from family_13.
- Echoes request fields from family_2 with up to 20 strong offset matches.
- Echoes request fields from family_23 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `5266` (`1.0`)
- Repeated n-gram instances: `5770`
- Top motifs: `0000`x10663, `000000`x5397, `000006`x5266, `000601`x5266, `0006`x5266

### family_14

- Role: `response`
- Messages: `4928`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ??`
- Related families: `family_11`, `family_12`, `family_17`, `family_19`
- Role hint: `response`
- Semantic confidence: `0.5182`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`3.027169` max=`3.027169` mean=`3.027169`
- Candidate discriminator offset: `10` cardinality=`60` entropy=`4.766203` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`1.0` confidence=`0.577437`
- Top discriminator candidates: offset `10` conf=`0.577437` salience=`1.0`, offset `9` conf=`0.502035` salience=`0.668347`, offset `0` conf=`0.326468` salience=`0.396297`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7013`
- bytes `1`..`1` | kind=`variable` confidence=`0.6602`
- bytes `2`..`7` | kind=`constant` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.799`
- bytes `10`..`10` | kind=`variable` confidence=`0.7171`

#### Field Hypotheses

- bytes `9`..`9` | type=`keyword` confidence=`0.9972`
- bytes `0`..`0` | type=`keyword` confidence=`0.9905`
- bytes `2`..`7` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9878`
- bytes `1`..`1` | type=`keyword` confidence=`0.9491`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9972`
- bytes `0`..`0` | label=`keyword` confidence=`0.9905`
- bytes `2`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9878`
- bytes `1`..`1` | label=`keyword` confidence=`0.9491`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.

#### Feature Summary

- Messages with repetition: `4928` (`1.0`)
- Repeated n-gram instances: `4928`
- Top motifs: `0000`x9856, `000000`x4928, `000005`x4928, `000501`x4928, `010402`x4928

### family_13

- Role: `response`
- Messages: `4817`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ??`
- Related families: `family_10`, `family_12`, `family_18`, `family_20`
- Role hint: `response`
- Semantic confidence: `0.692`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.732159` max=`3.027169` mean=`3.018962`
- Candidate discriminator offset: `10` cardinality=`65` entropy=`4.8982` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`1.0` confidence=`0.575688`
- Top discriminator candidates: offset `10` conf=`0.575688` salience=`1.0`, offset `9` conf=`0.499608` salience=`0.668347`, offset `0` conf=`0.326414` salience=`0.396297`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7011`
- bytes `1`..`1` | kind=`variable` confidence=`0.6617`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7921`
- bytes `10`..`10` | kind=`variable` confidence=`0.7146`

#### Field Hypotheses

- bytes `9`..`9` | type=`keyword` confidence=`0.9969`
- bytes `0`..`0` | type=`keyword` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9865`
- bytes `1`..`1` | type=`keyword` confidence=`0.9479`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9969`
- bytes `0`..`0` | label=`keyword` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9865`
- bytes `1`..`1` | label=`keyword` confidence=`0.9479`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.

#### Feature Summary

- Messages with repetition: `4817` (`1.0`)
- Repeated n-gram instances: `4817`
- Top motifs: `0000`x9634, `000000`x4817, `000005`x4817, `000501`x4817, `0005`x4817

### family_3

- Role: `response`
- Messages: `4683`
- Template: `?? ?? 00 00 00 04 01 ?? 01 00 00 0e`
- Related families: `family_10`, `family_15`, `family_19`, `family_20`
- Role hint: `response`
- Semantic confidence: `0.6176`
- Length stats: min=`10` max=`12` distinct=`2`
- Entropy summary: min=`1.360964` max=`2.370951` mean=`2.113224`
- Candidate discriminator offset: `7` cardinality=`3` entropy=`0.976122` salience=`0.244371` mutual_information=`0.251001` contrastive_separation=`0.796875` confidence=`0.369765`
- Top discriminator candidates: offset `7` conf=`0.369765` salience=`0.244371`, offset `0` conf=`0.326821` salience=`0.396297`, offset `1` conf=`0.22075` salience=`0.165443`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6916`
- bytes `1`..`1` | kind=`variable` confidence=`0.692`
- bytes `2`..`6` | kind=`variable` confidence=`0.5021`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`11` | kind=`constant` confidence=`0.85`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9994`
- bytes `8`..`11` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9855`
- bytes `0`..`0` | type=`keyword` confidence=`0.9748`
- bytes `2`..`6` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `8`..`8` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9994`
- bytes `8`..`11` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9855`
- bytes `0`..`0` | label=`keyword` confidence=`0.9748`
- bytes `8`..`11` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `2`..`6` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_19 with up to 20 strong offset matches.
- Response size is tied to request fields from family_19.
- Echoes request fields from family_20 with up to 20 strong offset matches.
- Response size is tied to request fields from family_20.

#### Feature Summary

- Messages with repetition: `4683` (`1.0`)
- Repeated n-gram instances: `7840`
- Top motifs: `0000`x9479, `0101`x5671, `000000`x4796, `0100`x4706, `0004`x4684

### family_6

- Role: `response`
- Messages: `4145`
- Template: `?? ?? 00 00 00 04 01 02 01 00`
- Related families: `family_10`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.846439` max=`2.370951` mean=`2.32105`
- Candidate discriminator offset: `0` cardinality=`35` entropy=`4.996736` salience=`0.396297` mutual_information=`0.205723` contrastive_separation=`1.0` confidence=`0.326094`
- Top discriminator candidates: offset `0` conf=`0.326094` salience=`0.396297`, offset `1` conf=`0.222083` salience=`0.165443`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7106`
- bytes `1`..`1` | kind=`variable` confidence=`0.6635`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.9995`
- bytes `0`..`0` | type=`keyword` confidence=`0.9916`
- bytes `1`..`1` | type=`keyword` confidence=`0.9392`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `8`..`9` | label=`keyword` confidence=`0.9995`
- bytes `0`..`0` | label=`keyword` confidence=`0.9916`
- bytes `1`..`1` | label=`keyword` confidence=`0.9392`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `4145` (`1.0`)
- Repeated n-gram instances: `4160`
- Top motifs: `0000`x8290, `000000`x4145, `000004`x4145, `000401`x4145, `0004`x4145

### family_21

- Role: `response`
- Messages: `2951`
- Template: `?? ?? 00 00 00 05 01 03 02 00 ??`
- Related families: `family_10`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.368523` max=`2.845351` mean=`2.726774`
- Candidate discriminator offset: `10` cardinality=`29` entropy=`2.782775` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`1.0` confidence=`0.564457`
- Top discriminator candidates: offset `10` conf=`0.564457` salience=`1.0`, offset `9` conf=`0.544013` salience=`0.668347`, offset `0` conf=`0.325082` salience=`0.396297`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7137`
- bytes `1`..`1` | kind=`variable` confidence=`0.6746`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7609`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.999`
- bytes `10`..`10` | type=`keyword` confidence=`0.9902`
- bytes `0`..`0` | type=`keyword` confidence=`0.9868`
- bytes `1`..`1` | type=`keyword` confidence=`0.9136`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `8`..`9` | label=`keyword` confidence=`0.999`
- bytes `10`..`10` | label=`keyword` confidence=`0.9902`
- bytes `0`..`0` | label=`keyword` confidence=`0.9868`
- bytes `1`..`1` | label=`keyword` confidence=`0.9136`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `2951` (`1.0`)
- Repeated n-gram instances: `2980`
- Top motifs: `0000`x5927, `000000`x2955, `000005`x2951, `000501`x2951, `0005`x2951

### family_7

- Role: `response`
- Messages: `2847`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ??`
- Related families: `family_10`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`3.027169` max=`3.027169` mean=`3.027169`
- Candidate discriminator offset: `10` cardinality=`42` entropy=`4.097688` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`1.0` confidence=`0.573257`
- Top discriminator candidates: offset `10` conf=`0.573257` salience=`1.0`, offset `9` conf=`0.523061` salience=`0.668347`, offset `0` conf=`0.325133` salience=`0.396297`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7161`
- bytes `1`..`1` | kind=`variable` confidence=`0.6747`
- bytes `2`..`7` | kind=`constant` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7977`
- bytes `10`..`10` | kind=`variable` confidence=`0.7331`

#### Field Hypotheses

- bytes `9`..`9` | type=`keyword` confidence=`0.9958`
- bytes `2`..`7` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9891`
- bytes `10`..`10` | type=`keyword` confidence=`0.9852`
- bytes `1`..`1` | type=`keyword` confidence=`0.9118`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `9`..`9` | label=`keyword` confidence=`0.9958`
- bytes `2`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9891`
- bytes `10`..`10` | label=`keyword` confidence=`0.9852`
- bytes `1`..`1` | label=`keyword` confidence=`0.9118`

#### Notes

- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `2847` (`1.0`)
- Repeated n-gram instances: `2847`
- Top motifs: `0000`x5694, `000000`x2847, `000005`x2847, `000501`x2847, `010402`x2847

### family_9

- Role: `response`
- Messages: `2247`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_10`, `family_12`, `family_15`, `family_17`
- Role hint: `response`
- Semantic confidence: `0.5151`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.40401` max=`3.027169` mean=`2.790491`
- Candidate discriminator offset: `9` cardinality=`4` entropy=`1.286635` salience=`0.668347` mutual_information=`0.327788` contrastive_separation=`0.8125` confidence=`0.578482`
- Top discriminator candidates: offset `9` conf=`0.578482` salience=`0.668347`, offset `10` conf=`0.573311` salience=`1.0`, offset `7` conf=`0.362155` salience=`0.244371`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7057`
- bytes `1`..`1` | kind=`variable` confidence=`0.6947`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7917`
- bytes `10`..`10` | kind=`variable` confidence=`0.7231`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9991`
- bytes `9`..`9` | type=`keyword` confidence=`0.9982`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9844`
- bytes `0`..`0` | type=`keyword` confidence=`0.972`
- bytes `1`..`1` | type=`keyword` confidence=`0.9617`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9991`
- bytes `9`..`9` | label=`keyword` confidence=`0.9982`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9844`
- bytes `0`..`0` | label=`keyword` confidence=`0.972`
- bytes `1`..`1` | label=`keyword` confidence=`0.9617`

#### Notes

- Echoes request fields from family_15 with up to 20 strong offset matches.
- Response size is tied to request fields from family_15.

#### Feature Summary

- Messages with repetition: `2247` (`1.0`)
- Repeated n-gram instances: `2417`
- Top motifs: `0000`x4559, `0005`x2352, `000000`x2247, `000005`x2247, `000501`x2247

### family_8

- Role: `response`
- Messages: `2171`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_10`, `family_11`, `family_12`, `family_16`, `family_17`, `family_18`, `family_19`, `family_20`
- Role hint: `response`
- Semantic confidence: `0.6209`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.222192` max=`3.027169` mean=`2.601045`
- Candidate discriminator offset: `10` cardinality=`36` entropy=`3.80796` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`1.0` confidence=`0.571561`
- Top discriminator candidates: offset `10` conf=`0.571561` salience=`1.0`, offset `9` conf=`0.546031` salience=`0.668347`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.694`
- bytes `1`..`1` | kind=`variable` confidence=`0.7024`
- bytes `2`..`5` | kind=`constant` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7403`

#### Field Hypotheses

- bytes `6`..`9` | type=`keyword` confidence=`0.9982`
- bytes `2`..`5` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9834`
- bytes `0`..`0` | type=`keyword` confidence=`0.9401`
- bytes `1`..`1` | type=`keyword` confidence=`0.8839`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `6`..`9` | label=`keyword` confidence=`0.9982`
- bytes `2`..`5` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9834`
- bytes `2`..`5` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `6`..`9` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `0`..`0` | label=`keyword` confidence=`0.9401`
- bytes `1`..`1` | label=`keyword` confidence=`0.8839`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_16 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `2171` (`1.0`)
- Repeated n-gram instances: `3005`
- Top motifs: `0000`x4728, `0005`x2529, `000000`x2221, `000005`x2171, `000501`x2171

### noise

- Role: `request`
- Messages: `2154`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? ??`
- Related families: `family_1`, `family_10`, `family_12`, `family_16`, `family_17`, `family_18`, `family_19`, `family_20`
- Role hint: `request`
- Semantic confidence: `0.7152`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.521928` max=`3.027169` mean=`2.332471`
- Candidate discriminator offset: `10` cardinality=`44` entropy=`3.514743` salience=`1.0` mutual_information=`0.293013` contrastive_separation=`1.0` confidence=`0.564209`
- Top discriminator candidates: offset `10` conf=`0.564209` salience=`1.0`, offset `9` conf=`0.529733` salience=`0.668347`, offset `8` conf=`0.501269` salience=`0.246095`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7042`
- bytes `1`..`1` | kind=`variable` confidence=`0.6975`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7765`
- bytes `8`..`8` | kind=`variable` confidence=`0.7867`
- bytes `9`..`9` | kind=`variable` confidence=`0.7818`
- bytes `10`..`10` | kind=`variable` confidence=`0.7238`
- bytes `11`..`11` | kind=`variable` confidence=`0.731`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`keyword` confidence=`0.9991`
- bytes `8`..`8` | type=`keyword` confidence=`0.9986`
- bytes `7`..`7` | type=`keyword` confidence=`0.9977`
- bytes `9`..`9` | type=`keyword` confidence=`0.9954`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9796`
- bytes `0`..`0` | type=`keyword` confidence=`0.9522`
- bytes `1`..`1` | type=`keyword` confidence=`0.8812`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`response_size_selector` confidence=`1.0`

#### Notes

- Echoes request fields from family_16 with up to 20 strong offset matches.
- Response size is tied to request fields from family_16.
- Echoes request fields from family_19 with up to 20 strong offset matches.
- Response size is tied to request fields from family_19.
- Echoes request fields from family_20 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `2154` (`1.0`)
- Repeated n-gram instances: `3259`
- Top motifs: `0000`x4550, `000000`x2289, `0101`x1396, `0100`x1117, `0005`x1089
