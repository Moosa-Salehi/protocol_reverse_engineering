# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: D:\tez\practical\protocol_re\data\05_families.json
- **source_feature_summary**: D:\tez\practical\protocol_re\data\03_family_features.json
- **source_keyword_summary**: D:\tez\practical\protocol_re\data\07_keywords.json
- **source_framing_summary**: D:\tez\practical\protocol_re\data\04_framing.json
- **source_relations_summary**: D:\tez\practical\protocol_re\data\08_relations.json
- **source_semantics_summary**: D:\tez\practical\protocol_re\data\09_semantics.json
- **framing_global_summary**: {'common_header_ends': [{'header_end': 8, 'family_count': 18, 'family_ratio': 0.6429}, {'header_end': 9, 'family_count': 4, 'family_ratio': 0.1429}, {'header_end': 7, 'family_count': 3, 'family_ratio': 0.1071}, {'header_end': 6, 'family_count': 2, 'family_ratio': 0.0714}, {'header_end': 12, 'family_count': 1, 'family_ratio': 0.0357}], 'field_type_counts': {'length': 97, 'constant': 20, 'discriminator': 18, 'transaction_or_counter': 7}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 28}
- **notes**: Initial auto-generated protocol model assembled from family summaries.

## Evaluation

- Messages: `200000` across `45340` sessions
- Corpus assignment coverage: `1` with `28` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `28` of `28`
- Pair hypotheses: `154658` direction_unknown_ratio=`0`
- Relation edges: `95` echo_edges=`95` length_relation_edges=`81`
- Semantic coverage: `28` of `28` families ratio=`1`
- Top semantic labels: `keyword`x118, `echoed_request_field`x52, `response_size_selector`x45, `constant`x39, `blob`x9, `transaction_or_correlation_id`x5, `length`x4
- Framing coverage: `28` of `28` families ratio=`1`
- Clustering diagnostics: warning_families=`1` split_candidates=`0` merge_candidates=`0`

### Clustering Diagnostic Warnings

- `noise` | messages=`1353` split=`0.3` under_split=`0.3` over_split=`0` warnings=mixed directions, mixed length profile, noise family

### Evaluation Top Relation Edges

- `family_22` -> `family_4` | pairs=`11291` avg_score=`6.4362` support=`0.931` lift=`10.7523` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_21` -> `family_3` | pairs=`10939` avg_score=`6.4361` support=`0.8383` lift=`9.3732` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_23` -> `family_1` | pairs=`6591` avg_score=`6.4363` support=`0.9482` lift=`17.3077` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_3` -> `family_18` | pairs=`6387` avg_score=`4.9375` support=`0.477` lift=`4.5046` direction=`1` order=`1` echo_fields=`20` length_rules=`0`
- `family_18` -> `family_10` | pairs=`5745` avg_score=`6.4362` support=`0.3252` lift=`7.644` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_17` -> `family_9` | pairs=`5364` avg_score=`6.4361` support=`0.3277` lift=`7.0972` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_17` -> `family_5` | pairs=`5192` avg_score=`6.465` support=`0.3171` lift=`8.2449` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_18` -> `family_6` | pairs=`5012` avg_score=`6.4659` support=`0.2837` lift=`8.5304` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_18` -> `family_13` | pairs=`4814` avg_score=`6.4673` support=`0.2725` lift=`8.3081` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_17` -> `family_12` | pairs=`4794` avg_score=`6.4672` support=`0.2928` lift=`8.8959` direction=`1` order=`1` echo_fields=`20` length_rules=`14`

## Final Ground Truth Evaluation

- Overall score: `0.2266`
- Verdict: `fail`
- Matched message types: `11` of `11`
- Message type matching: accuracy=`0.3929` precision=`0.3929` recall=`1` f1=`0.5641`
- Field boundary: accuracy=`0.1141` precision=`0.1235` recall=`0.6` f1=`0.2049`
- Field semantics: accuracy=`0` precision=`0` recall=`0` f1=`0`
- Relations: accuracy=`0.0737` precision=`0.0737` recall=`1` f1=`0.1373`

## LLM Analysis

- Prompt size: `466774` bytes, `466774` characters, estimated tokens=`116694`

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `95`
- Strongest edges:
- `family_22` -> `family_4` | pairs=`11291` avg_score=`6.4362` support=`0.931` lift=`10.7523` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_21` -> `family_3` | pairs=`10939` avg_score=`6.4361` support=`0.8383` lift=`9.3732` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_23` -> `family_1` | pairs=`6591` avg_score=`6.4363` support=`0.9482` lift=`17.3077` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_3` -> `family_18` | pairs=`6387` avg_score=`4.9375` support=`0.477` lift=`4.5046` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_18` -> `family_10` | pairs=`5745` avg_score=`6.4362` support=`0.3252` lift=`7.644` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_17` -> `family_9` | pairs=`5364` avg_score=`6.4361` support=`0.3277` lift=`7.0972` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_17` -> `family_5` | pairs=`5192` avg_score=`6.465` support=`0.3171` lift=`8.2449` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_18` -> `family_6` | pairs=`5012` avg_score=`6.4659` support=`0.2837` lift=`8.5304` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_18` -> `family_13` | pairs=`4814` avg_score=`6.4673` support=`0.2725` lift=`8.3081` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_17` -> `family_12` | pairs=`4794` avg_score=`6.4672` support=`0.2928` lift=`8.8959` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_3` -> `family_22` | pairs=`4199` avg_score=`4.9375` support=`0.3136` lift=`4.3233` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_19` -> `family_11` | pairs=`3693` avg_score=`6.4362` support=`0.3116` lift=`11.6281` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_4` -> `family_19` | pairs=`3628` avg_score=`4.9375` support=`0.542` lift=`7.1489` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_9` -> `family_18` | pairs=`3236` avg_score=`4.9375` support=`0.4658` lift=`4.3987` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_5` -> `family_18` | pairs=`2972` avg_score=`4.9688` support=`0.5174` lift=`4.8859` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_19` -> `family_7` | pairs=`2898` avg_score=`6.4663` support=`0.2446` lift=`12.7178` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_19` -> `family_14` | pairs=`2640` avg_score=`6.4648` support=`0.2228` lift=`9.0009` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_18` | pairs=`2506` avg_score=`4.9688` support=`0.5087` lift=`4.8039` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_20` -> `family_2` | pairs=`2498` avg_score=`6.4669` support=`0.2713` lift=`15.4684` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_4` -> `family_23` | pairs=`2396` avg_score=`4.9375` support=`0.3579` lift=`8.0391` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_9` -> `family_22` | pairs=`2235` avg_score=`4.9375` support=`0.3217` lift=`4.435` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_5` -> `family_22` | pairs=`2156` avg_score=`4.9688` support=`0.3753` lift=`5.1743` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_20` -> `family_3` | pairs=`2000` avg_score=`6.4359` support=`0.2172` lift=`2.4291` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_25` -> `family_8` | pairs=`1945` avg_score=`6.4348` support=`0.4257` lift=`14.0408` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`20`
- `family_10` -> `family_19` | pairs=`1885` avg_score=`4.9375` support=`0.5779` lift=`7.6223` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`

## Families

- Total families: `28`
- Families shown below: `28`

### family_18

- Role: `request`
- Messages: `17685`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_0`, `family_10`, `family_12`, `family_13`, `family_16`, `family_2`, `family_3`, `family_5`, `family_6`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5132`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.221252` max=`2.617492` mean=`2.449211`
- Candidate discriminator offset: `0` cardinality=`50` entropy=`5.555875` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.510815`
- Top discriminator candidates: offset `0` conf=`0.510815` salience=`1.0`, offset `10` conf=`0.453761` salience=`0.440942`, offset `9` conf=`0.386308` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.696`
- bytes `1`..`1` | kind=`variable` confidence=`0.6466`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7903`
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

- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_2 with up to 20 strong offset matches.
- Response size is tied to request fields from family_2.
- Echoes request fields from family_3 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `17685` (`1.0`)
- Repeated n-gram instances: `17685`
- Top motifs: `0000`x35370, `000000`x17685, `000006`x17685, `000601`x17685, `0006`x17685

### family_17

- Role: `request`
- Messages: `17605`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? ?? ??`
- Related families: `family_0`, `family_12`, `family_5`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.221252` max=`2.617492` mean=`2.439937`
- Candidate discriminator offset: `0` cardinality=`49` entropy=`5.495074` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.509967`
- Top discriminator candidates: offset `0` conf=`0.509967` salience=`1.0`, offset `10` conf=`0.457997` salience=`0.440942`, offset `9` conf=`0.380796` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6974`
- bytes `1`..`1` | kind=`variable` confidence=`0.6473`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7861`
- bytes `10`..`11` | kind=`variable` confidence=`0.5366`

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

#### Feature Summary

- Messages with repetition: `17605` (`1.0`)
- Repeated n-gram instances: `18838`
- Top motifs: `0000`x36443, `000000`x17605, `000006`x17605, `000601`x17605, `0006`x17605

### family_3

- Role: `response`
- Messages: `13832`
- Template: `?? ?? 00 00 00 04 01 01 01 00`
- Related families: `family_18`, `family_20`, `family_21`, `family_22`, `family_25`, `family_26`, `noise`
- Role hint: `response`
- Semantic confidence: `0.5324`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.685475` max=`2.046439` mean=`2.038887`
- Candidate discriminator offset: `0` cardinality=`50` entropy=`5.627624` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.510493`
- Top discriminator candidates: offset `0` conf=`0.510493` salience=`1.0`, offset `1` conf=`0.233392` salience=`0.202557`
- Framing hypothesis: header=`0`..`8` body_start=`9` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6947`
- bytes `1`..`1` | kind=`variable` confidence=`0.6475`
- bytes `2`..`8` | kind=`constant` confidence=`0.85`
- bytes `9`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `9`..`9` | type=`length` confidence=`0.9968` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9964`
- bytes `2`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9817`

#### Framing Hypotheses

- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `8`..`8` length, `9`..`9` length
- header_end=`8` body_start=`8` confidence=`0.8462` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `9`..`9` | label=`length` confidence=`0.9968`
- bytes `0`..`0` | label=`keyword` confidence=`0.9964`
- bytes `2`..`8` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9817`

#### Notes

- Echoes request fields from family_20 with up to 20 strong offset matches.
- Response size is tied to request fields from family_20.
- Echoes request fields from family_21 with up to 20 strong offset matches.
- Response size is tied to request fields from family_21.
- Echoes request fields from family_25 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `13832` (`1.0`)
- Repeated n-gram instances: `27752`
- Top motifs: `0101`x27708, `0000`x27664, `010101`x13876, `000000`x13832, `000004`x13832

### family_4

- Role: `response`
- Messages: `13391`
- Template: `?? ?? 00 00 00 04 01 01 01 00`
- Related families: `family_19`, `family_20`, `family_22`, `family_23`, `family_24`, `family_26`
- Role hint: `response`
- Semantic confidence: `0.6681`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`2.046439` max=`2.046439` mean=`2.046439`
- Candidate discriminator offset: `0` cardinality=`51` entropy=`5.600867` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.510445`
- Top discriminator candidates: offset `0` conf=`0.510445` salience=`1.0`, offset `1` conf=`0.233364` salience=`0.202557`
- Framing hypothesis: header=`0`..`8` body_start=`9` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6954`
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

- Echoes request fields from family_20 with up to 20 strong offset matches.
- Response size is tied to request fields from family_20.
- Echoes request fields from family_22 with up to 20 strong offset matches.
- Response size is tied to request fields from family_22.
- Echoes request fields from family_26 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `13391` (`1.0`)
- Repeated n-gram instances: `26852`
- Top motifs: `0101`x26817, `0000`x26782, `010101`x13426, `000000`x13391, `000004`x13391

### family_21

- Role: `request`
- Messages: `13287`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_3`, `family_5`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.896241` max=`2.450826` mean=`2.224778`
- Candidate discriminator offset: `0` cardinality=`52` entropy=`5.632617` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.510192`
- Top discriminator candidates: offset `0` conf=`0.510192` salience=`1.0`, offset `10` conf=`0.454781` salience=`0.440942`, offset `9` conf=`0.401027` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6947`
- bytes `1`..`1` | kind=`variable` confidence=`0.6493`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.764`
- bytes `10`..`11` | kind=`variable` confidence=`0.5421`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9997`
- bytes `7`..`7` | type=`keyword` confidence=`0.9995`
- bytes `9`..`9` | type=`keyword` confidence=`0.9994`
- bytes `0`..`0` | type=`keyword` confidence=`0.9961`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9807`

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

- Messages with repetition: `13287` (`1.0`)
- Repeated n-gram instances: `13731`
- Top motifs: `0000`x26869, `000000`x13344, `0006`x13291, `000006`x13287, `000601`x13287

### family_22

- Role: `request`
- Messages: `12132`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_0`, `family_12`, `family_2`, `family_3`, `family_4`, `family_5`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5033`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.450826` mean=`2.228993`
- Candidate discriminator offset: `0` cardinality=`51` entropy=`5.583389` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.510273`
- Top discriminator candidates: offset `0` conf=`0.510273` salience=`1.0`, offset `9` conf=`0.406593` salience=`0.11658`, offset `7` conf=`0.307258` salience=`0.088601`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6959`
- bytes `1`..`1` | kind=`variable` confidence=`0.6493`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7706`
- bytes `10`..`11` | kind=`variable` confidence=`0.5449`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9994`
- bytes `0`..`0` | type=`keyword` confidence=`0.9958`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9789`
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

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_2 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `12132` (`1.0`)
- Repeated n-gram instances: `12356`
- Top motifs: `0000`x24324, `000000`x12192, `0006`x12136, `000006`x12132, `000601`x12132

### family_19

- Role: `request`
- Messages: `11875`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_0`, `family_10`, `family_11`, `family_13`, `family_14`, `family_15`, `family_16`, `family_2`, `family_4`, `family_6`
- Role hint: `request`
- Semantic confidence: `0.5167`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.221252` max=`2.617492` mean=`2.439286`
- Candidate discriminator offset: `0` cardinality=`34` entropy=`4.987167` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.509578`
- Top discriminator candidates: offset `0` conf=`0.509578` salience=`1.0`, offset `10` conf=`0.453807` salience=`0.440942`, offset `9` conf=`0.389648` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7088`
- bytes `1`..`1` | kind=`variable` confidence=`0.6503`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.784`
- bytes `10`..`11` | kind=`variable` confidence=`0.5444`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9995`
- bytes `9`..`9` | type=`keyword` confidence=`0.9994`
- bytes `10`..`11` | type=`keyword` confidence=`0.9992`
- bytes `0`..`0` | type=`keyword` confidence=`0.9971`
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
- bytes `0`..`0` | label=`keyword` confidence=`0.9971`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_13 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `11875` (`1.0`)
- Repeated n-gram instances: `11877`
- Top motifs: `0000`x23750, `000000`x11875, `000006`x11875, `000601`x11875, `0006`x11875

### family_20

- Role: `request`
- Messages: `10067`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? ?? ??`
- Related families: `family_0`, `family_14`, `family_15`, `family_2`, `family_3`, `family_4`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `0.6765`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.896241` max=`2.617492` mean=`2.319959`
- Candidate discriminator offset: `0` cardinality=`91` entropy=`6.245223` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.510346`
- Top discriminator candidates: offset `0` conf=`0.510346` salience=`1.0`, offset `10` conf=`0.45888` salience=`0.440942`, offset `9` conf=`0.397225` salience=`0.11658`
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

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_15 with up to 20 strong offset matches.
- Response size is tied to request fields from family_15.
- Echoes request fields from family_2 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `10067` (`1.0`)
- Repeated n-gram instances: `10937`
- Top motifs: `0000`x20990, `0006`x10069, `000000`x10067, `000006`x10067, `000601`x10067

### family_1

- Role: `response`
- Messages: `8473`
- Template: `?? ?? 00 00 00 04 01 01 01 00`
- Related families: `family_23`, `family_24`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`2.046439` max=`2.046439` mean=`2.046439`
- Candidate discriminator offset: `0` cardinality=`35` entropy=`5.015614` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.509659`
- Top discriminator candidates: offset `0` conf=`0.509659` salience=`1.0`, offset `1` conf=`0.233396` salience=`0.202557`
- Framing hypothesis: header=`0`..`8` body_start=`9` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7086`
- bytes `1`..`1` | kind=`variable` confidence=`0.6519`
- bytes `2`..`8` | kind=`constant` confidence=`0.85`
- bytes `9`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `9`..`9` | type=`length` confidence=`0.9976` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9959`
- bytes `2`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9701`

#### Framing Hypotheses

- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `8`..`8` length, `9`..`9` length
- header_end=`8` body_start=`8` confidence=`0.8464` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `9`..`9` | label=`length` confidence=`0.9976`
- bytes `0`..`0` | label=`keyword` confidence=`0.9959`
- bytes `2`..`8` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9701`

#### Notes

- Echoes request fields from family_23 with up to 20 strong offset matches.
- Response size is tied to request fields from family_23.
- Echoes request fields from family_24 with up to 20 strong offset matches.
- Response size is tied to request fields from family_24.

#### Feature Summary

- Messages with repetition: `8473` (`1.0`)
- Repeated n-gram instances: `16986`
- Top motifs: `0101`x16966, `0000`x16946, `010101`x8493, `000000`x8473, `000004`x8473

### family_9

- Role: `response`
- Messages: `7140`
- Template: `?? ?? 00 00 00 04 01 02 01 00`
- Related families: `family_17`, `family_18`, `family_20`, `family_21`, `family_22`, `family_25`, `family_26`
- Role hint: `response`
- Semantic confidence: `0.5274`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.685475` max=`2.370951` mean=`2.287897`
- Candidate discriminator offset: `0` cardinality=`51` entropy=`5.635219` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.508946`
- Top discriminator candidates: offset `0` conf=`0.508946` salience=`1.0`, offset `1` conf=`0.233367` salience=`0.202557`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6958`
- bytes `1`..`1` | kind=`variable` confidence=`0.6541`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.9997`
- bytes `0`..`0` | type=`keyword` confidence=`0.9929`
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
- bytes `0`..`0` | label=`keyword` confidence=`0.9929`
- bytes `2`..`7` | label=`response_size_selector` confidence=`0.9794`
- bytes `1`..`1` | label=`keyword` confidence=`0.9647`
- bytes `8`..`9` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_17 with up to 20 strong offset matches.
- Response size is tied to request fields from family_17.
- Echoes request fields from family_20 with up to 20 strong offset matches.
- Response size is tied to request fields from family_20.
- Echoes request fields from family_21 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `7140` (`1.0`)
- Repeated n-gram instances: `7365`
- Top motifs: `0000`x14280, `000000`x7140, `000004`x7140, `000401`x7140, `0004`x7140

### family_23

- Role: `request`
- Messages: `6955`
- Template: `?? ?? 00 00 00 06 01 01 00 ?? 00 01`
- Related families: `family_1`, `family_10`, `family_13`, `family_14`, `family_2`, `family_4`, `family_6`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5376`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.450826` mean=`2.225414`
- Candidate discriminator offset: `9` cardinality=`7` entropy=`2.185747` salience=`0.11658` mutual_information=`0.32483` contrastive_separation=`0.859375` confidence=`0.408002`
- Top discriminator candidates: offset `9` conf=`0.408002` salience=`0.11658`, offset `7` conf=`0.306124` salience=`0.088601`, offset `11` conf=`0.298096` salience=`0.051626`
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
- bytes `1`..`1` | type=`keyword` confidence=`0.9632`
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
- bytes `1`..`1` | label=`keyword` confidence=`0.9632`
- bytes `2`..`8` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_13 with up to 20 strong offset matches.
- Response size is tied to request fields from family_13.
- Echoes request fields from family_14 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `6955` (`1.0`)
- Repeated n-gram instances: `7055`
- Top motifs: `0000`x13931, `000000`x6976, `0006`x6957, `000006`x6955, `000601`x6955

### family_10

- Role: `response`
- Messages: `6580`
- Template: `?? ?? 00 00 00 04 01 02 01 00`
- Related families: `family_18`, `family_19`, `family_23`, `family_24`
- Role hint: `response`
- Semantic confidence: `0.6427`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.846439` max=`2.370951` mean=`2.322923`
- Candidate discriminator offset: `0` cardinality=`50` entropy=`5.599157` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.510425`
- Top discriminator candidates: offset `0` conf=`0.510425` salience=`1.0`, offset `1` conf=`0.233286` salience=`0.202557`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6968`
- bytes `1`..`1` | kind=`variable` confidence=`0.6553`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.9997`
- bytes `0`..`0` | type=`keyword` confidence=`0.9924`
- bytes `1`..`1` | type=`keyword` confidence=`0.9617`
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
- bytes `1`..`1` | label=`keyword` confidence=`0.9617`
- bytes `8`..`9` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_18 with up to 20 strong offset matches.
- Response size is tied to request fields from family_18.

#### Feature Summary

- Messages with repetition: `6580` (`1.0`)
- Repeated n-gram instances: `6586`
- Top motifs: `0000`x13160, `000000`x6580, `000004`x6580, `000401`x6580, `0004`x6580

### family_5

- Role: `response`
- Messages: `5950`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_17`, `family_18`, `family_21`, `family_22`, `family_25`, `family_26`
- Role hint: `response`
- Semantic confidence: `0.5223`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.40401` max=`3.027169` mean=`2.728754`
- Candidate discriminator offset: `0` cardinality=`51` entropy=`5.570684` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.509906`
- Top discriminator candidates: offset `0` conf=`0.509906` salience=`1.0`, offset `10` conf=`0.39966` salience=`0.440942`, offset `9` conf=`0.37938` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6977`
- bytes `1`..`1` | kind=`variable` confidence=`0.6575`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7383`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.999`
- bytes `10`..`10` | type=`keyword` confidence=`0.9926`
- bytes `0`..`0` | type=`keyword` confidence=`0.9914`
- bytes `1`..`1` | type=`keyword` confidence=`0.957`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`9` | label=`keyword` confidence=`0.999`
- bytes `10`..`10` | label=`keyword` confidence=`0.9926`
- bytes `0`..`0` | label=`keyword` confidence=`0.9914`
- bytes `1`..`1` | label=`keyword` confidence=`0.957`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_17 with up to 20 strong offset matches.
- Response size is tied to request fields from family_17.
- Echoes request fields from family_21 with up to 20 strong offset matches.
- Response size is tied to request fields from family_21.

#### Feature Summary

- Messages with repetition: `5950` (`1.0`)
- Repeated n-gram instances: `6110`
- Top motifs: `0000`x11947, `0005`x6048, `000000`x5965, `000005`x5950, `000501`x5950

### family_25

- Role: `request`
- Messages: `5313`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? ?? ?? 00 04 00 00 00 06 01 01 00 0e 00 01`
- Related families: `family_0`, `family_15`, `family_3`, `family_5`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `0.9749`
- Length stats: min=`12` max=`24` distinct=`2`
- Entropy summary: min=`1.650022` max=`2.617492` mean=`2.287154`
- Candidate discriminator offset: `0` cardinality=`56` entropy=`5.373594` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.509605`
- Top discriminator candidates: offset `0` conf=`0.509605` salience=`1.0`, offset `10` conf=`0.462199` salience=`0.440942`, offset `9` conf=`0.398891` salience=`0.11658`
- Framing hypothesis: header=`0`..`11` body_start=`12` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7029`
- bytes `1`..`1` | kind=`variable` confidence=`0.6889`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.7706`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7587`
- bytes `10`..`11` | kind=`variable` confidence=`0.85`
- bytes `12`..`23` | kind=`constant` confidence=`0.85`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9991`
- bytes `7`..`7` | type=`keyword` confidence=`0.9989`
- bytes `9`..`9` | type=`keyword` confidence=`0.9985`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `12`..`23` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9895`
- bytes `1`..`1` | type=`keyword` confidence=`0.9868`

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
- bytes `10`..`11` | label=`keyword` confidence=`0.9991`

#### Notes

- Echoes request fields from family_3 with up to 20 strong offset matches.
- Echoes request fields from family_5 with up to 20 strong offset matches.
- Response size is tied to request fields from family_5.
- Echoes request fields from family_9 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `5313` (`1.0`)
- Repeated n-gram instances: `6495`
- Top motifs: `0000`x11468, `000000`x5410, `0006`x5317, `0601`x5317, `000006`x5314

### family_6

- Role: `response`
- Messages: `5144`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_18`, `family_19`, `family_23`
- Role hint: `response`
- Semantic confidence: `0.644`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.40401` max=`2.845351` mean=`2.738703`
- Candidate discriminator offset: `0` cardinality=`49` entropy=`5.477338` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.509642`
- Top discriminator candidates: offset `0` conf=`0.509642` salience=`1.0`, offset `10` conf=`0.398023` salience=`0.440942`, offset `9` conf=`0.383997` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7002`
- bytes `1`..`1` | kind=`variable` confidence=`0.6598`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7553`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.999`
- bytes `10`..`10` | type=`keyword` confidence=`0.9928`
- bytes `0`..`0` | type=`keyword` confidence=`0.9905`
- bytes `1`..`1` | type=`keyword` confidence=`0.9502`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`9` | label=`keyword` confidence=`0.999`
- bytes `10`..`10` | label=`keyword` confidence=`0.9928`
- bytes `0`..`0` | label=`keyword` confidence=`0.9905`
- bytes `1`..`1` | label=`keyword` confidence=`0.9502`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_18 with up to 20 strong offset matches.
- Response size is tied to request fields from family_18.

#### Feature Summary

- Messages with repetition: `5144` (`1.0`)
- Repeated n-gram instances: `5198`
- Top motifs: `0000`x10322, `000000`x5164, `000005`x5144, `000501`x5144, `0005`x5144

### family_12

- Role: `response`
- Messages: `5091`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ??`
- Related families: `family_17`, `family_18`, `family_22`, `family_26`
- Role hint: `response`
- Semantic confidence: `0.5151`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`3.027169` max=`3.027169` mean=`3.027169`
- Candidate discriminator offset: `0` cardinality=`47` entropy=`5.452085` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.510044`
- Top discriminator candidates: offset `0` conf=`0.510044` salience=`1.0`, offset `10` conf=`0.409192` salience=`0.440942`, offset `9` conf=`0.335157` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7007`
- bytes `1`..`1` | kind=`variable` confidence=`0.6597`
- bytes `2`..`7` | kind=`constant` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7992`
- bytes `10`..`10` | kind=`variable` confidence=`0.7167`

#### Field Hypotheses

- bytes `9`..`9` | type=`keyword` confidence=`0.9973`
- bytes `0`..`0` | type=`keyword` confidence=`0.9908`
- bytes `2`..`7` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9882`
- bytes `1`..`1` | type=`keyword` confidence=`0.9507`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9973`
- bytes `0`..`0` | label=`keyword` confidence=`0.9908`
- bytes `2`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9882`
- bytes `1`..`1` | label=`keyword` confidence=`0.9507`

#### Notes

- Echoes request fields from family_17 with up to 20 strong offset matches.
- Response size is tied to request fields from family_17.

#### Feature Summary

- Messages with repetition: `5091` (`1.0`)
- Repeated n-gram instances: `5091`
- Top motifs: `0000`x10182, `000000`x5091, `000005`x5091, `000501`x5091, `010402`x5091

### family_13

- Role: `response`
- Messages: `5073`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ??`
- Related families: `family_18`, `family_19`, `family_23`, `family_24`
- Role hint: `response`
- Semantic confidence: `0.6797`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`3.027169` max=`3.027169` mean=`3.027169`
- Candidate discriminator offset: `0` cardinality=`56` entropy=`5.603396` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.510026`
- Top discriminator candidates: offset `0` conf=`0.510026` salience=`1.0`, offset `10` conf=`0.407369` salience=`0.440942`, offset `9` conf=`0.338658` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6979`
- bytes `1`..`1` | kind=`variable` confidence=`0.6608`
- bytes `2`..`7` | kind=`constant` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7957`
- bytes `10`..`10` | kind=`variable` confidence=`0.7129`

#### Field Hypotheses

- bytes `9`..`9` | type=`keyword` confidence=`0.9972`
- bytes `2`..`7` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.989`
- bytes `10`..`10` | type=`keyword` confidence=`0.986`
- bytes `1`..`1` | type=`keyword` confidence=`0.9505`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`8` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `2`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`7` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9972`
- bytes `2`..`7` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.989`
- bytes `10`..`10` | label=`keyword` confidence=`0.986`
- bytes `1`..`1` | label=`keyword` confidence=`0.9505`

#### Notes

- Echoes request fields from family_18 with up to 20 strong offset matches.
- Response size is tied to request fields from family_18.

#### Feature Summary

- Messages with repetition: `5073` (`1.0`)
- Repeated n-gram instances: `5073`
- Top motifs: `0000`x10146, `000000`x5073, `000005`x5073, `000501`x5073, `010402`x5073

### family_8

- Role: `response`
- Messages: `4689`
- Template: `?? ?? 00 00 00 04 01 ?? 01 00 00 0e`
- Related families: `family_19`, `family_20`, `family_24`, `family_25`, `family_26`
- Role hint: `response`
- Semantic confidence: `0.6178`
- Length stats: min=`10` max=`12` distinct=`2`
- Entropy summary: min=`1.360964` max=`2.370951` mean=`2.113155`
- Candidate discriminator offset: `0` cardinality=`118` entropy=`6.109445` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.51034`
- Top discriminator candidates: offset `0` conf=`0.51034` salience=`1.0`, offset `7` conf=`0.322849` salience=`0.088601`, offset `1` conf=`0.232023` salience=`0.202557`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6916`
- bytes `1`..`1` | kind=`variable` confidence=`0.6919`
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

- Echoes request fields from family_24 with up to 20 strong offset matches.
- Response size is tied to request fields from family_24.
- Echoes request fields from family_25 with up to 20 strong offset matches.
- Response size is tied to request fields from family_25.
- Echoes request fields from family_26 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `4689` (`1.0`)
- Repeated n-gram instances: `7850`
- Top motifs: `0000`x9491, `0101`x5679, `000000`x4802, `0100`x4712, `0004`x4690

### family_11

- Role: `response`
- Messages: `4145`
- Template: `?? ?? 00 00 00 04 01 02 01 00`
- Related families: `family_19`, `family_24`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`10` max=`10` distinct=`1`
- Entropy summary: min=`1.846439` max=`2.370951` mean=`2.32105`
- Candidate discriminator offset: `0` cardinality=`34` entropy=`4.989457` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.509611`
- Top discriminator candidates: offset `0` conf=`0.509611` salience=`1.0`, offset `1` conf=`0.233368` salience=`0.202557`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7107`
- bytes `1`..`1` | kind=`variable` confidence=`0.6635`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.9995`
- bytes `0`..`0` | type=`keyword` confidence=`0.9918`
- bytes `1`..`1` | type=`keyword` confidence=`0.9392`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`9` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `8`..`8` length

#### Semantic Labels

- bytes `8`..`9` | label=`keyword` confidence=`0.9995`
- bytes `0`..`0` | label=`keyword` confidence=`0.9918`
- bytes `1`..`1` | label=`keyword` confidence=`0.9392`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_19 with up to 20 strong offset matches.
- Response size is tied to request fields from family_19.
- Echoes request fields from family_24 with up to 20 strong offset matches.
- Response size is tied to request fields from family_24.

#### Feature Summary

- Messages with repetition: `4145` (`1.0`)
- Repeated n-gram instances: `4160`
- Top motifs: `0000`x8290, `000000`x4145, `000004`x4145, `000401`x4145, `0004`x4145

### family_0

- Role: `response`
- Messages: `4084`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_17`, `family_18`, `family_19`, `family_20`, `family_22`, `family_24`, `family_25`, `family_26`
- Role hint: `response`
- Semantic confidence: `0.5559`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.040373` max=`3.027169` mean=`2.698669`
- Candidate discriminator offset: `10` cardinality=`46` entropy=`4.537976` salience=`0.440942` mutual_information=`0.290278` contrastive_separation=`1.0` confidence=`0.4065`
- Top discriminator candidates: offset `10` conf=`0.4065` salience=`0.440942`, offset `9` conf=`0.388206` salience=`0.11658`, offset `7` conf=`0.309357` salience=`0.088601`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6899`
- bytes `1`..`1` | kind=`variable` confidence=`0.6826`
- bytes `2`..`5` | kind=`constant` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7991`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7976`
- bytes `10`..`10` | kind=`variable` confidence=`0.722`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9995`
- bytes `9`..`9` | type=`keyword` confidence=`0.9985`
- bytes `2`..`5` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9887`
- bytes `0`..`0` | type=`keyword` confidence=`0.9706`
- bytes `1`..`1` | type=`keyword` confidence=`0.9373`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9995`
- bytes `9`..`9` | label=`keyword` confidence=`0.9985`
- bytes `2`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9887`
- bytes `0`..`0` | label=`keyword` confidence=`0.9706`

#### Notes

- Echoes request fields from family_17 with up to 20 strong offset matches.
- Response size is tied to request fields from family_17.
- Echoes request fields from family_18 with up to 20 strong offset matches.
- Response size is tied to request fields from family_18.
- Echoes request fields from family_25 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `4084` (`1.0`)
- Repeated n-gram instances: `5117`
- Top motifs: `0000`x8620, `0005`x4533, `000000`x4161, `0501`x4085, `000005`x4084

### family_14

- Role: `response`
- Messages: `3828`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_19`, `family_20`, `family_23`
- Role hint: `response`
- Semantic confidence: `0.9631`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.40401` max=`3.027169` mean=`2.924391`
- Candidate discriminator offset: `0` cardinality=`59` entropy=`5.534548` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.509962`
- Top discriminator candidates: offset `0` conf=`0.509962` salience=`1.0`, offset `10` conf=`0.407` salience=`0.440942`, offset `9` conf=`0.365402` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.701`
- bytes `1`..`1` | kind=`variable` confidence=`0.6778`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7849`
- bytes `10`..`10` | kind=`variable` confidence=`0.7164`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9995`
- bytes `9`..`9` | type=`keyword` confidence=`0.9969`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9851`
- bytes `0`..`0` | type=`keyword` confidence=`0.9846`
- bytes `1`..`1` | type=`keyword` confidence=`0.9637`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `7`..`7` length
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `7`..`7` length
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator, `7`..`7` length

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9995`
- bytes `9`..`9` | label=`keyword` confidence=`0.9969`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9851`
- bytes `0`..`0` | label=`keyword` confidence=`0.9846`
- bytes `1`..`1` | label=`keyword` confidence=`0.9637`

#### Notes

- Echoes request fields from family_19 with up to 20 strong offset matches.
- Response size is tied to request fields from family_19.
- Echoes request fields from family_20 with up to 20 strong offset matches.
- Response size is tied to request fields from family_20.

#### Feature Summary

- Messages with repetition: `3828` (`1.0`)
- Repeated n-gram instances: `3846`
- Top motifs: `0000`x7674, `000000`x3828, `000005`x3828, `000501`x3828, `0005`x3828

### family_26

- Role: `request`
- Messages: `3438`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_0`, `family_12`, `family_15`, `family_3`, `family_4`, `family_5`, `family_8`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5138`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.896241` max=`2.617492` mean=`2.32522`
- Candidate discriminator offset: `0` cardinality=`50` entropy=`4.942762` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.508699`
- Top discriminator candidates: offset `0` conf=`0.508699` salience=`1.0`, offset `10` conf=`0.464059` salience=`0.440942`, offset `9` conf=`0.402933` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.714`
- bytes `1`..`1` | kind=`variable` confidence=`0.6928`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7641`
- bytes `10`..`11` | kind=`variable` confidence=`0.5446`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9988`
- bytes `7`..`7` | type=`keyword` confidence=`0.9983`
- bytes `9`..`9` | type=`keyword` confidence=`0.998`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9855`
- bytes `1`..`1` | type=`keyword` confidence=`0.9811`

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
- bytes `10`..`11` | label=`keyword` confidence=`0.9988`
- bytes `7`..`7` | label=`keyword` confidence=`0.9983`
- bytes `9`..`9` | label=`keyword` confidence=`0.998`
- bytes `2`..`6` | label=`constant` confidence=`0.99`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_15 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `3438` (`1.0`)
- Repeated n-gram instances: `3786`
- Top motifs: `0000`x6966, `000000`x3528, `000006`x3438, `000601`x3438, `0006`x3438

### family_24

- Role: `request`
- Messages: `3015`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_13`, `family_15`, `family_16`, `family_4`, `family_8`
- Role hint: `request`
- Semantic confidence: `0.5272`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.896241` max=`2.617492` mean=`2.332266`
- Candidate discriminator offset: `0` cardinality=`29` entropy=`4.329339` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.508115`
- Top discriminator candidates: offset `0` conf=`0.508115` salience=`1.0`, offset `10` conf=`0.475017` salience=`0.440942`, offset `9` conf=`0.397804` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7261`
- bytes `1`..`1` | kind=`variable` confidence=`0.6928`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7705`
- bytes `10`..`11` | kind=`variable` confidence=`0.5448`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9993`
- bytes `7`..`7` | type=`keyword` confidence=`0.9983`
- bytes `9`..`9` | type=`keyword` confidence=`0.9977`
- bytes `0`..`0` | type=`keyword` confidence=`0.9904`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9784`

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
- bytes `10`..`11` | label=`keyword` confidence=`0.9993`
- bytes `7`..`7` | label=`keyword` confidence=`0.9983`
- bytes `9`..`9` | label=`keyword` confidence=`0.9977`
- bytes `0`..`0` | label=`keyword` confidence=`0.9904`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_13 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `3015` (`1.0`)
- Repeated n-gram instances: `3264`
- Top motifs: `0000`x6098, `000000`x3083, `000006`x3015, `000601`x3015, `0006`x3015

### family_7

- Role: `response`
- Messages: `2974`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_19`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.368523` max=`3.027169` mean=`2.744914`
- Candidate discriminator offset: `0` cardinality=`33` entropy=`4.815726` salience=`1.0` mutual_information=`0.215749` contrastive_separation=`1.0` confidence=`0.508624`
- Top discriminator candidates: offset `0` conf=`0.508624` salience=`1.0`, offset `10` conf=`0.396235` salience=`0.440942`, offset `9` conf=`0.3818` salience=`0.11658`
- Framing hypothesis: header=`0`..`7` body_start=`8` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7156`
- bytes `1`..`1` | kind=`variable` confidence=`0.6748`
- bytes `2`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7535`

#### Field Hypotheses

- bytes `8`..`9` | type=`keyword` confidence=`0.999`
- bytes `10`..`10` | type=`keyword` confidence=`0.9902`
- bytes `0`..`0` | type=`keyword` confidence=`0.9889`
- bytes `1`..`1` | type=`keyword` confidence=`0.9143`
- bytes `2`..`7` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator
- header_end=`10` body_start=`10` confidence=`1.0` fields=`2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `8`..`9` | label=`keyword` confidence=`0.999`
- bytes `10`..`10` | label=`keyword` confidence=`0.9902`
- bytes `0`..`0` | label=`keyword` confidence=`0.9889`
- bytes `1`..`1` | label=`keyword` confidence=`0.9143`
- bytes `2`..`7` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_19 with up to 20 strong offset matches.
- Response size is tied to request fields from family_19.

#### Feature Summary

- Messages with repetition: `2974` (`1.0`)
- Repeated n-gram instances: `3011`
- Top motifs: `0000`x5978, `000000`x2981, `000005`x2974, `000501`x2974, `0005`x2974

### family_2

- Role: `request`
- Messages: `2713`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_18`, `family_19`, `family_20`, `family_22`, `family_23`
- Role hint: `request`
- Semantic confidence: `0.5071`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.40401` max=`3.027169` mean=`2.799863`
- Candidate discriminator offset: `10` cardinality=`35` entropy=`4.562741` salience=`0.440942` mutual_information=`0.290278` contrastive_separation=`1.0` confidence=`0.405938`
- Top discriminator candidates: offset `10` conf=`0.405938` salience=`0.440942`, offset `9` conf=`0.405033` salience=`0.11658`, offset `7` conf=`0.314991` salience=`0.088601`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7036`
- bytes `1`..`1` | kind=`variable` confidence=`0.6902`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7921`
- bytes `10`..`10` | kind=`variable` confidence=`0.722`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9993`
- bytes `9`..`9` | type=`keyword` confidence=`0.9982`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9871`
- bytes `0`..`0` | type=`keyword` confidence=`0.9808`
- bytes `1`..`1` | type=`keyword` confidence=`0.9683`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9993`
- bytes `9`..`9` | label=`keyword` confidence=`0.9982`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9871`
- bytes `0`..`0` | label=`keyword` confidence=`0.9808`
- bytes `1`..`1` | label=`keyword` confidence=`0.9683`

#### Notes

- Echoes request fields from family_20 with up to 20 strong offset matches.
- Response size is tied to request fields from family_20.

#### Feature Summary

- Messages with repetition: `2713` (`1.0`)
- Repeated n-gram instances: `2893`
- Top motifs: `0000`x5494, `0005`x2825, `000000`x2713, `000005`x2713, `000501`x2713

### family_15

- Role: `response`
- Messages: `2308`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_19`, `family_20`, `family_24`, `family_25`, `family_26`
- Role hint: `response`
- Semantic confidence: `0.8112`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.222192` max=`3.027169` mean=`2.884847`
- Candidate discriminator offset: `10` cardinality=`52` entropy=`5.065455` salience=`0.440942` mutual_information=`0.290278` contrastive_separation=`1.0` confidence=`0.40705`
- Top discriminator candidates: offset `10` conf=`0.40705` salience=`0.440942`, offset `9` conf=`0.392236` salience=`0.11658`, offset `7` conf=`0.310476` salience=`0.088601`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6983`
- bytes `1`..`1` | kind=`variable` confidence=`0.7003`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7869`
- bytes `10`..`10` | kind=`variable` confidence=`0.7141`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9991`
- bytes `9`..`9` | type=`keyword` confidence=`0.9965`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9775`
- bytes `1`..`1` | type=`keyword` confidence=`0.977`
- bytes `0`..`0` | type=`keyword` confidence=`0.9662`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9991`
- bytes `9`..`9` | label=`keyword` confidence=`0.9965`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9775`
- bytes `1`..`1` | label=`keyword` confidence=`0.977`
- bytes `0`..`0` | label=`keyword` confidence=`0.9662`

#### Notes

- Echoes request fields from family_19 with up to 20 strong offset matches.
- Response size is tied to request fields from family_19.
- Echoes request fields from family_24 with up to 20 strong offset matches.
- Response size is tied to request fields from family_24.
- Echoes request fields from family_25 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `2308` (`1.0`)
- Repeated n-gram instances: `2452`
- Top motifs: `0000`x4694, `000000`x2355, `000005`x2308, `000501`x2308, `0005`x2308

### family_16

- Role: `response`
- Messages: `1860`
- Template: `?? ?? 00 00 00 05 01 ?? 02 ?? ??`
- Related families: `family_18`, `family_19`, `family_24`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.550341` max=`3.027169` mean=`2.93788`
- Candidate discriminator offset: `10` cardinality=`41` entropy=`4.630582` salience=`0.440942` mutual_information=`0.290278` contrastive_separation=`1.0` confidence=`0.407146`
- Top discriminator candidates: offset `10` conf=`0.407146` salience=`0.440942`, offset `9` conf=`0.3784` salience=`0.11658`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7099`
- bytes `1`..`1` | kind=`variable` confidence=`0.6988`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`7` | kind=`variable` confidence=`0.85`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.786`
- bytes `10`..`10` | kind=`variable` confidence=`0.7237`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9989`
- bytes `9`..`9` | type=`keyword` confidence=`0.9946`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.978`
- bytes `0`..`0` | type=`keyword` confidence=`0.9763`
- bytes `1`..`1` | type=`keyword` confidence=`0.9554`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `7`..`7` | label=`keyword` confidence=`0.9989`
- bytes `9`..`9` | label=`keyword` confidence=`0.9946`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `8`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.978`
- bytes `0`..`0` | label=`keyword` confidence=`0.9763`
- bytes `1`..`1` | label=`keyword` confidence=`0.9554`

#### Notes

- Echoes request fields from family_18 with up to 20 strong offset matches.
- Response size is tied to request fields from family_18.
- Echoes request fields from family_19 with up to 20 strong offset matches.
- Response size is tied to request fields from family_19.
- Echoes request fields from family_24 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `1860` (`1.0`)
- Repeated n-gram instances: `1860`
- Top motifs: `0000`x3720, `000000`x1860, `000005`x1860, `000501`x1860, `0005`x1860

### noise

- Role: `request`
- Messages: `1353`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? ??`
- Related families: `family_17`, `family_18`, `family_20`, `family_21`, `family_22`, `family_23`, `family_25`, `family_26`, `family_3`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5331`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.521928` max=`3.027169` mean=`2.103638`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.491892` salience=`0.08998` mutual_information=`0.324464` contrastive_separation=`0.796875` confidence=`0.453581`
- Top discriminator candidates: offset `8` conf=`0.453581` salience=`0.08998`, offset `10` conf=`0.420577` salience=`0.440942`, offset `9` conf=`0.379566` salience=`0.11658`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7173`
- bytes `1`..`1` | kind=`variable` confidence=`0.7279`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7827`
- bytes `8`..`8` | kind=`variable` confidence=`0.7872`
- bytes `9`..`9` | kind=`variable` confidence=`0.783`
- bytes `10`..`10` | kind=`variable` confidence=`0.7383`
- bytes `11`..`11` | kind=`variable` confidence=`0.7408`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`keyword` confidence=`0.9985`
- bytes `8`..`8` | type=`keyword` confidence=`0.9978`
- bytes `7`..`7` | type=`keyword` confidence=`0.9963`
- bytes `9`..`9` | type=`keyword` confidence=`0.9933`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9889`
- bytes `0`..`0` | type=`keyword` confidence=`0.9239`
- bytes `1`..`1` | type=`keyword` confidence=`0.8167`

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
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`keyword` confidence=`0.9985`
- bytes `8`..`8` | label=`keyword` confidence=`0.9978`

#### Notes

- Echoes request fields from family_17 with up to 20 strong offset matches.
- Response size is tied to request fields from family_17.
- Echoes request fields from family_21 with up to 20 strong offset matches.
- Response size is tied to request fields from family_21.
- Echoes request fields from family_23 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `1353` (`1.0`)
- Repeated n-gram instances: `2359`
- Top motifs: `0000`x2910, `000000`x1460, `0101`x1381, `0100`x1061, `010100`x839
