# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: D:\tez\practical\protocol_re\data\05_families.json
- **source_feature_summary**: D:\tez\practical\protocol_re\data\03_family_features.json
- **source_keyword_summary**: D:\tez\practical\protocol_re\data\07_keywords.json
- **source_framing_summary**: D:\tez\practical\protocol_re\data\04_framing.json
- **source_relations_summary**: D:\tez\practical\protocol_re\data\08_relations.json
- **source_semantics_summary**: D:\tez\practical\protocol_re\data\09_semantics.json
- **framing_global_summary**: {'common_header_ends': [{'header_end': 6, 'family_count': 14, 'family_ratio': 0.875}, {'header_end': 7, 'family_count': 1, 'family_ratio': 0.0625}, {'header_end': 12, 'family_count': 1, 'family_ratio': 0.0625}], 'field_type_counts': {'length': 49, 'transaction_or_counter': 18, 'discriminator': 11, 'constant': 10}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 16}
- **notes**: Initial auto-generated protocol model assembled from family summaries.

## Evaluation

- Messages: `200000` across `45340` sessions
- Corpus assignment coverage: `1` with `16` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `16` of `16`
- Pair hypotheses: `154658` direction_unknown_ratio=`0`
- Relation edges: `40` echo_edges=`40` length_relation_edges=`26`
- Semantic coverage: `16` of `16` families ratio=`1`
- Top semantic labels: `keyword`x76, `echoed_request_field`x54, `response_size_selector`x40, `constant`x24, `length`x12, `transaction_or_correlation_id`x7, `blob`x6
- Framing coverage: `16` of `16` families ratio=`1`
- Clustering diagnostics: warning_families=`7` split_candidates=`0` merge_candidates=`0`

### Clustering Diagnostic Warnings

- `family_11` | messages=`51186` split=`0.3` under_split=`0.3` over_split=`0` warnings=mixed directions, mixed length profile
- `family_14` | messages=`46616` split=`0.3` under_split=`0.3` over_split=`0` warnings=mixed directions, mixed length profile
- `family_8` | messages=`26044` split=`0.3` under_split=`0.3` over_split=`0` warnings=mixed directions, mixed length profile
- `family_3` | messages=`18375` split=`0.3` under_split=`0.3` over_split=`0` warnings=mixed directions, mixed length profile
- `family_4` | messages=`11678` split=`0.3` under_split=`0.3` over_split=`0` warnings=mixed directions, mixed length profile
- `family_2` | messages=`9898` split=`0.3` under_split=`0.3` over_split=`0` warnings=mixed directions, mixed length profile
- `noise` | messages=`5868` split=`0.3` under_split=`0.3` over_split=`0` warnings=mixed directions, mixed length profile, noise family

### Evaluation Top Relation Edges

- `family_11` -> `family_11` | pairs=`18602` avg_score=`6.4424` support=`0.3694` lift=`2.1443` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_14` | pairs=`16981` avg_score=`4.9454` support=`0.3372` lift=`1.1541` direction=`1` order=`1` echo_fields=`20` length_rules=`0`
- `family_8` -> `family_8` | pairs=`9281` avg_score=`6.4422` support=`0.7502` lift=`4.4714` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_8` | pairs=`8080` avg_score=`4.9469` support=`0.2363` lift=`1.4087` direction=`0.9984` order=`1` echo_fields=`20` length_rules=`0`
- `family_4` -> `family_4` | pairs=`4736` avg_score=`6.3632` support=`0.4217` lift=`8.9124` direction=`0.9445` order=`1` echo_fields=`20` length_rules=`20`
- `family_2` -> `family_2` | pairs=`3957` avg_score=`6.4463` support=`0.6824` lift=`10.8875` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_10` -> `family_11` | pairs=`3551` avg_score=`6.4376` support=`0.9626` lift=`5.5883` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_0` | pairs=`3228` avg_score=`6.4599` support=`0.0944` lift=`1.1679` direction=`0.995` order=`1` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_14` | pairs=`2634` avg_score=`6.4363` support=`0.832` lift=`2.8478` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_0` -> `family_14` | pairs=`2382` avg_score=`4.9692` support=`0.3229` lift=`1.1052` direction=`1` order=`1` echo_fields=`20` length_rules=`4`

## Final Ground Truth Evaluation

- Overall score: `0.3729`
- Verdict: `fail`
- Matched message types: `11` of `11`
- Message type matching: accuracy=`0.6875` precision=`0.6875` recall=`1` f1=`0.8148`
- Field boundary: accuracy=`0.2339` precision=`0.2458` recall=`0.8286` f1=`0.3791`
- Field semantics: accuracy=`0` precision=`0` recall=`0` f1=`0`
- Relations: accuracy=`0.175` precision=`0.175` recall=`1` f1=`0.2979`

## LLM Analysis

- Prompt size: `292019` bytes, `292019` characters, estimated tokens=`73005`

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `40`
- Strongest edges:
- `family_11` -> `family_11` | pairs=`18602` avg_score=`6.4424` support=`0.3694` lift=`2.1443` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_14` | pairs=`16981` avg_score=`4.9454` support=`0.3372` lift=`1.1541` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_8` -> `family_8` | pairs=`9281` avg_score=`6.4422` support=`0.7502` lift=`4.4714` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_8` | pairs=`8080` avg_score=`4.9469` support=`0.2363` lift=`1.4087` direction=`0.9984` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_4` -> `family_4` | pairs=`4736` avg_score=`6.3632` support=`0.4217` lift=`8.9124` direction=`0.9445` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`20`
- `family_2` -> `family_2` | pairs=`3957` avg_score=`6.4463` support=`0.6824` lift=`10.8875` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_10` -> `family_11` | pairs=`3551` avg_score=`6.4376` support=`0.9626` lift=`5.5883` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_0` | pairs=`3228` avg_score=`6.4599` support=`0.0944` lift=`1.1679` direction=`0.995` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_14` | pairs=`2634` avg_score=`6.4363` support=`0.832` lift=`2.8478` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_0` -> `family_14` | pairs=`2382` avg_score=`4.9692` support=`0.3229` lift=`1.1052` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`4`
- `family_14` -> `noise` | pairs=`2244` avg_score=`5.9693` support=`0.0656` lift=`2.1686` direction=`0.6725` order=`1` flow=`client_to_server->server_to_client` echo_fields=`17`
- `family_4` -> `family_2` | pairs=`2240` avg_score=`4.9482` support=`0.1994` lift=`3.182` direction=`0.9996` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_11` -> `family_13` | pairs=`1859` avg_score=`4.9455` support=`0.0369` lift=`2.3483` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_4` -> `family_3` | pairs=`1854` avg_score=`4.9485` support=`0.1651` lift=`1.8148` direction=`0.9995` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_8` -> `family_0` | pairs=`1728` avg_score=`6.4671` support=`0.1397` lift=`1.7277` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_7` -> `family_8` | pairs=`1632` avg_score=`6.4365` support=`0.9342` lift=`5.5682` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `noise` -> `family_8` | pairs=`1592` avg_score=`5.8849` support=`0.3374` lift=`2.0113` direction=`0.6175` order=`1` flow=`client_to_server->server_to_client` echo_fields=`17`
- `noise` -> `family_14` | pairs=`1588` avg_score=`5.949` support=`0.3366` lift=`1.1521` direction=`0.6618` order=`1` flow=`client_to_server->server_to_client` echo_fields=`17`
- `family_3` -> `family_0` | pairs=`1564` avg_score=`6.4645` support=`0.1048` lift=`1.2967` direction=`0.9981` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_11` -> `noise` | pairs=`1557` avg_score=`5.5767` support=`0.0309` lift=`1.0214` direction=`0.5851` order=`1` flow=`server_to_client->client_to_server` echo_fields=`17`
- `family_0` -> `family_8` | pairs=`1388` avg_score=`4.9691` support=`0.1882` lift=`1.1215` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`4`
- `family_9` -> `family_11` | pairs=`1365` avg_score=`6.4668` support=`0.9935` lift=`5.7675` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_5` | pairs=`1301` avg_score=`6.4663` support=`0.0258` lift=`2.8557` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_14` | pairs=`1284` avg_score=`6.4683` support=`0.888` lift=`3.0394` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_5` -> `family_14` | pairs=`1119` avg_score=`4.9688` support=`0.8277` lift=`2.833` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`

## Families

- Total families: `16`
- Families shown below: `16`

### family_11

- Role: `request`
- Messages: `51186`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_10`, `family_11`, `family_13`, `family_14`, `family_5`, `family_9`, `noise`
- Role hint: `request`
- Semantic confidence: `0.621`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.521928` max=`2.732159` mean=`2.30799`
- Candidate discriminator offset: `0` cardinality=`52` entropy=`5.618933` salience=`1.0` mutual_information=`0.207388` contrastive_separation=`1.0` confidence=`0.508623`
- Top discriminator candidates: offset `0` conf=`0.508623` salience=`1.0`, offset `10` conf=`0.424521` salience=`0.4055`, offset `8` conf=`0.398398` salience=`0.084807`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6939`
- bytes `1`..`1` | kind=`variable` confidence=`0.6424`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7779`
- bytes `8`..`8` | kind=`variable` confidence=`0.7881`
- bytes `9`..`9` | kind=`variable` confidence=`0.7753`
- bytes `10`..`10` | kind=`variable` confidence=`0.7539`
- bytes `11`..`11` | kind=`variable` confidence=`0.7731`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`0.9999`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `9`..`9` | type=`keyword` confidence=`0.9999`
- bytes `11`..`11` | type=`keyword` confidence=`0.9999`
- bytes `10`..`10` | type=`keyword` confidence=`0.9997`
- bytes `0`..`0` | type=`keyword` confidence=`0.999`
- bytes `1`..`1` | type=`keyword` confidence=`0.995`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant

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
- bytes `7`..`7` | label=`keyword` confidence=`0.9999`

#### Notes

- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.
- Echoes request fields from family_9 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `51186` (`1.0`)
- Repeated n-gram instances: `65712`
- Top motifs: `0000`x102784, `000000`x51340, `0101`x35294, `0100`x28072, `0006`x24798

### family_14

- Role: `response`
- Messages: `46616`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_11`, `family_12`, `family_13`, `family_5`, `family_6`, `family_7`, `family_8`, `noise`
- Role hint: `response`
- Semantic confidence: `0.6354`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.317694`
- Candidate discriminator offset: `0` cardinality=`50` entropy=`5.500669` salience=`1.0` mutual_information=`0.207388` contrastive_separation=`1.0` confidence=`0.508404`
- Top discriminator candidates: offset `0` conf=`0.508404` salience=`1.0`, offset `10` conf=`0.434284` salience=`0.4055`, offset `8` conf=`0.398601` salience=`0.084807`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6966`
- bytes `1`..`1` | kind=`variable` confidence=`0.6425`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7781`
- bytes `8`..`8` | kind=`variable` confidence=`0.7884`
- bytes `9`..`9` | kind=`variable` confidence=`0.7749`
- bytes `10`..`10` | kind=`variable` confidence=`0.7555`
- bytes `11`..`11` | kind=`variable` confidence=`0.7735`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`0.9999`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `9`..`9` | type=`keyword` confidence=`0.9998`
- bytes `11`..`11` | type=`keyword` confidence=`0.9998`
- bytes `10`..`10` | type=`keyword` confidence=`0.9997`
- bytes `0`..`0` | type=`keyword` confidence=`0.9989`
- bytes `1`..`1` | type=`keyword` confidence=`0.9945`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9999`
- bytes `8`..`8` | label=`keyword` confidence=`0.9999`
- bytes `9`..`9` | label=`keyword` confidence=`0.9998`
- bytes `11`..`11` | label=`keyword` confidence=`0.9998`
- bytes `10`..`10` | label=`keyword` confidence=`0.9997`
- bytes `0`..`0` | label=`keyword` confidence=`0.9989`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_11 with up to 20 strong offset matches.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.

#### Feature Summary

- Messages with repetition: `46616` (`1.0`)
- Repeated n-gram instances: `59858`
- Top motifs: `0000`x93553, `000000`x46759, `0101`x32529, `0100`x25945, `0006`x23019

### family_8

- Role: `response`
- Messages: `26044`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_14`, `family_6`, `family_7`, `family_8`, `noise`
- Role hint: `response`
- Semantic confidence: `0.6588`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.32039`
- Candidate discriminator offset: `0` cardinality=`34` entropy=`4.847875` salience=`1.0` mutual_information=`0.207388` contrastive_separation=`1.0` confidence=`0.507039`
- Top discriminator candidates: offset `0` conf=`0.507039` salience=`1.0`, offset `10` conf=`0.45365` salience=`0.4055`, offset `8` conf=`0.39812` salience=`0.084807`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7114`
- bytes `1`..`1` | kind=`variable` confidence=`0.6454`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7779`
- bytes `8`..`8` | kind=`variable` confidence=`0.7881`
- bytes `9`..`9` | kind=`variable` confidence=`0.7751`
- bytes `10`..`10` | kind=`variable` confidence=`0.7557`
- bytes `11`..`11` | kind=`variable` confidence=`0.7724`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `7`..`7` | type=`keyword` confidence=`0.9998`
- bytes `9`..`9` | type=`keyword` confidence=`0.9997`
- bytes `11`..`11` | type=`keyword` confidence=`0.9997`
- bytes `10`..`10` | type=`keyword` confidence=`0.9996`
- bytes `0`..`0` | type=`keyword` confidence=`0.9987`
- bytes `1`..`1` | type=`keyword` confidence=`0.9902`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`0.9999`
- bytes `7`..`7` | label=`keyword` confidence=`0.9998`
- bytes `9`..`9` | label=`keyword` confidence=`0.9997`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_14 with up to 20 strong offset matches.
- Echoes request fields from family_6 with up to 20 strong offset matches.
- Response size is tied to request fields from family_6.

#### Feature Summary

- Messages with repetition: `26044` (`1.0`)
- Repeated n-gram instances: `33370`
- Top motifs: `0000`x52263, `000000`x26117, `0101`x18050, `0100`x14365, `0006`x12501

### family_3

- Role: `response`
- Messages: `18375`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_4`, `family_7`
- Role hint: `response`
- Semantic confidence: `0.6228`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`3.027169` mean=`2.361599`
- Candidate discriminator offset: `0` cardinality=`94` entropy=`6.199223` salience=`1.0` mutual_information=`0.207388` contrastive_separation=`1.0` confidence=`0.5092`
- Top discriminator candidates: offset `0` conf=`0.5092` salience=`1.0`, offset `8` conf=`0.392874` salience=`0.084807`, offset `10` conf=`0.361518` salience=`0.4055`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6824`
- bytes `1`..`1` | kind=`variable` confidence=`0.683`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7771`
- bytes `8`..`8` | kind=`variable` confidence=`0.789`
- bytes `9`..`9` | kind=`variable` confidence=`0.7607`
- bytes `10`..`10` | kind=`variable` confidence=`0.7616`
- bytes `11`..`11` | kind=`variable` confidence=`0.7824`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9998`
- bytes `11`..`11` | type=`keyword` confidence=`0.9998`
- bytes `7`..`7` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9991`
- bytes `10`..`10` | type=`keyword` confidence=`0.9978`
- bytes `0`..`0` | type=`keyword` confidence=`0.9949`
- bytes `1`..`1` | type=`keyword` confidence=`0.9942`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `9`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`0.9998`
- bytes `11`..`11` | label=`keyword` confidence=`0.9998`
- bytes `7`..`7` | label=`keyword` confidence=`0.9997`
- bytes `9`..`9` | label=`keyword` confidence=`0.9991`
- bytes `10`..`10` | label=`response_size_selector` confidence=`0.9987`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_4 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `18375` (`1.0`)
- Repeated n-gram instances: `21567`
- Top motifs: `0000`x36789, `000000`x18375, `0006`x10926, `000006`x10716, `000601`x10716

### family_0

- Role: `response`
- Messages: `15626`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 00`
- Related families: `family_13`, `family_14`, `family_2`, `family_3`, `family_4`, `family_8`
- Role hint: `response`
- Semantic confidence: `0.5743`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.947339` max=`3.027169` mean=`2.864584`
- Candidate discriminator offset: `8` cardinality=`2` entropy=`0.743136` salience=`0.084807` mutual_information=`0.076129` contrastive_separation=`0.78125` confidence=`0.404287`
- Top discriminator candidates: offset `8` conf=`0.404287` salience=`0.084807`, offset `10` conf=`0.373964` salience=`0.4055`, offset `9` conf=`0.3145` salience=`0.077977`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6721`
- bytes `1`..`1` | kind=`variable` confidence=`0.646`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7158`
- bytes `11`..`11` | kind=`constant` confidence=`0.8935`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `6`..`9` | type=`keyword` confidence=`0.9986`
- bytes `10`..`10` | type=`keyword` confidence=`0.9951`
- bytes `0`..`0` | type=`keyword` confidence=`0.9917`
- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9836`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `11`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `6`..`9` | label=`keyword` confidence=`0.9986`
- bytes `10`..`10` | label=`keyword` confidence=`0.9951`
- bytes `6`..`9` | label=`response_size_selector` confidence=`0.9929`
- bytes `0`..`0` | label=`keyword` confidence=`0.9917`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9836`
- bytes `2`..`5` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.
- Echoes request fields from family_2 with up to 20 strong offset matches.
- Response size is tied to request fields from family_2.
- Echoes request fields from family_3 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `15626` (`1.0`)
- Repeated n-gram instances: `18863`
- Top motifs: `0000`x34387, `000000`x15690, `000005`x12331, `000501`x12331, `010402`x12331

### family_4

- Role: `request`
- Messages: `11678`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01 00 04 00 00 00 06 01 01 00 0e 00 01`
- Related families: `family_0`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.6765`
- Length stats: min=`10` max=`24` distinct=`4`
- Entropy summary: min=`1.360964` max=`3.027169` mean=`2.346428`
- Candidate discriminator offset: `0` cardinality=`76` entropy=`5.557105` salience=`1.0` mutual_information=`0.207388` contrastive_separation=`1.0` confidence=`0.509291`
- Top discriminator candidates: offset `0` conf=`0.509291` salience=`1.0`, offset `8` conf=`0.392224` salience=`0.084807`, offset `10` conf=`0.361606` salience=`0.4055`
- Framing hypothesis: header=`0`..`11` body_start=`12` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6973`
- bytes `1`..`1` | kind=`variable` confidence=`0.6816`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7885`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7769`
- bytes `8`..`8` | kind=`variable` confidence=`0.7885`
- bytes `9`..`9` | kind=`variable` confidence=`0.7611`
- bytes `10`..`10` | kind=`variable` confidence=`0.7608`
- bytes `11`..`11` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`0.9999` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9997`
- bytes `11`..`11` | type=`keyword` confidence=`0.9997`
- bytes `7`..`7` | type=`keyword` confidence=`0.9996`
- bytes `9`..`9` | type=`keyword` confidence=`0.9987`
- bytes `10`..`10` | type=`keyword` confidence=`0.9965`
- bytes `0`..`0` | type=`keyword` confidence=`0.9935`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `12`..`23` | type=`constant` confidence=`0.99`

#### Framing Hypotheses

- header_end=`12` body_start=`12` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`13` body_start=`13` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`18` body_start=`18` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `12`..`23` | label=`echoed_request_field` confidence=`1.0`
- bytes `12`..`23` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`0.9999`
- bytes `8`..`8` | label=`keyword` confidence=`0.9997`
- bytes `11`..`11` | label=`keyword` confidence=`0.9997`
- bytes `7`..`7` | label=`keyword` confidence=`0.9996`
- bytes `9`..`9` | label=`keyword` confidence=`0.9987`

#### Notes

- Echoes request fields from family_4 with up to 20 strong offset matches.
- Response size is tied to request fields from family_4.

#### Feature Summary

- Messages with repetition: `11678` (`1.0`)
- Repeated n-gram instances: `14360`
- Top motifs: `0000`x23558, `000000`x11846, `0006`x6910, `0601`x6690, `000006`x6686

### family_2

- Role: `response`
- Messages: `9898`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_2`, `family_4`
- Role hint: `response`
- Semantic confidence: `0.6046`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`3.027169` mean=`2.350698`
- Candidate discriminator offset: `0` cardinality=`38` entropy=`4.90285` salience=`1.0` mutual_information=`0.207388` contrastive_separation=`1.0` confidence=`0.507973`
- Top discriminator candidates: offset `0` conf=`0.507973` salience=`1.0`, offset `10` conf=`0.402817` salience=`0.4055`, offset `8` conf=`0.39364` salience=`0.084807`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7111`
- bytes `1`..`1` | kind=`variable` confidence=`0.6788`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7773`
- bytes `8`..`8` | kind=`variable` confidence=`0.7894`
- bytes `9`..`9` | kind=`variable` confidence=`0.7607`
- bytes `10`..`10` | kind=`variable` confidence=`0.7665`
- bytes `11`..`11` | kind=`variable` confidence=`0.7827`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9997`
- bytes `11`..`11` | type=`keyword` confidence=`0.9996`
- bytes `7`..`7` | type=`keyword` confidence=`0.9995`
- bytes `9`..`9` | type=`keyword` confidence=`0.9989`
- bytes `10`..`10` | type=`keyword` confidence=`0.9984`
- bytes `0`..`0` | type=`keyword` confidence=`0.9962`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9891`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`7` body_start=`7` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`8` body_start=`8` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`0.9997`
- bytes `11`..`11` | label=`keyword` confidence=`0.9996`
- bytes `7`..`7` | label=`keyword` confidence=`0.9995`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_2 with up to 20 strong offset matches.
- Response size is tied to request fields from family_2.
- Echoes request fields from family_4 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `9898` (`1.0`)
- Repeated n-gram instances: `12089`
- Top motifs: `0000`x19963, `000000`x10017, `0101`x5857, `000006`x5803, `000601`x5803

### noise

- Role: `request`
- Messages: `5868`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? ??`
- Related families: `family_11`, `family_14`, `family_6`, `family_7`, `family_8`
- Role hint: `request`
- Semantic confidence: `0.5377`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.729574` max=`3.027169` mean=`2.603329`
- Candidate discriminator offset: `8` cardinality=`2` entropy=`0.985309` salience=`0.084807` mutual_information=`0.076129` contrastive_separation=`0.78125` confidence=`0.410605`
- Top discriminator candidates: offset `8` conf=`0.410605` salience=`0.084807`, offset `7` conf=`0.391316` salience=`0.083791`, offset `10` conf=`0.357404` salience=`0.4055`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6873`
- bytes `1`..`1` | kind=`variable` confidence=`0.6569`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7815`
- bytes `8`..`8` | kind=`variable` confidence=`0.798`
- bytes `9`..`9` | kind=`variable` confidence=`0.7783`
- bytes `10`..`10` | kind=`variable` confidence=`0.7653`
- bytes `11`..`11` | kind=`variable` confidence=`0.7731`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9997`
- bytes `7`..`7` | type=`keyword` confidence=`0.9993`
- bytes `11`..`11` | type=`keyword` confidence=`0.9981`
- bytes `9`..`9` | type=`keyword` confidence=`0.9971`
- bytes `10`..`10` | type=`keyword` confidence=`0.9918`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9824`
- bytes `1`..`1` | type=`keyword` confidence=`0.9564`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

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

- Echoes request fields from family_11 with up to 17 strong offset matches.
- Echoes request fields from family_14 with up to 17 strong offset matches.

#### Feature Summary

- Messages with repetition: `5868` (`1.0`)
- Repeated n-gram instances: `6032`
- Top motifs: `0000`x11793, `000000`x5925, `0006`x3354, `000006`x3352, `000601`x3352

### family_10

- Role: `request`
- Messages: `3689`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_11`, `family_5`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.825011` max=`2.450826` mean=`2.185903`
- Candidate discriminator offset: `9` cardinality=`6` entropy=`2.136217` salience=`0.077977` mutual_information=`0.234079` contrastive_separation=`0.84375` confidence=`0.378372`
- Top discriminator candidates: offset `9` conf=`0.378372` salience=`0.077977`, offset `7` conf=`0.282689` salience=`0.083791`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7169`
- bytes `1`..`1` | kind=`variable` confidence=`0.6717`
- bytes `2`..`6` | kind=`constant` confidence=`0.85`
- bytes `7`..`8` | kind=`variable` confidence=`0.85`
- bytes `9`..`9` | kind=`variable` confidence=`0.7725`
- bytes `10`..`11` | kind=`constant` confidence=`0.725`

#### Field Hypotheses

- bytes `7`..`8` | type=`keyword` confidence=`0.9989`
- bytes `9`..`9` | type=`keyword` confidence=`0.9984`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `10`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9886`
- bytes `1`..`1` | type=`keyword` confidence=`0.933`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`8` | label=`keyword` confidence=`0.9989`
- bytes `9`..`9` | label=`keyword` confidence=`0.9984`
- bytes `2`..`6` | label=`constant` confidence=`0.99`
- bytes `10`..`11` | label=`constant` confidence=`0.99`

#### Feature Summary

- Messages with repetition: `3689` (`1.0`)
- Repeated n-gram instances: `3692`
- Top motifs: `0000`x7378, `000000`x3689, `000006`x3689, `000601`x3689, `0001`x3689

### family_13

- Role: `request`
- Messages: `3166`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_0`, `family_11`, `family_14`, `family_5`
- Role hint: `request`
- Semantic confidence: `0.5286`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.450826` mean=`2.237786`
- Candidate discriminator offset: `9` cardinality=`5` entropy=`1.994045` salience=`0.077977` mutual_information=`0.234079` contrastive_separation=`0.828125` confidence=`0.381065`
- Top discriminator candidates: offset `9` conf=`0.381065` salience=`0.077977`, offset `7` conf=`0.279143` salience=`0.083791`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7095`
- bytes `1`..`1` | kind=`variable` confidence=`0.6813`
- bytes `2`..`5` | kind=`constant` confidence=`0.85`
- bytes `6`..`8` | kind=`variable` confidence=`0.85`
- bytes `9`..`9` | kind=`variable` confidence=`0.7757`
- bytes `10`..`11` | kind=`constant` confidence=`0.725`

#### Field Hypotheses

- bytes `9`..`9` | type=`keyword` confidence=`0.9984`
- bytes `2`..`5` | type=`constant` confidence=`0.99`
- bytes `10`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9845`
- bytes `1`..`1` | type=`keyword` confidence=`0.922`
- bytes `6`..`8` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`response_size_selector` confidence=`1.0`
- bytes `6`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9984`
- bytes `2`..`5` | label=`constant` confidence=`0.99`
- bytes `10`..`11` | label=`constant` confidence=`0.99`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_11 with up to 20 strong offset matches.
- Echoes request fields from family_5 with up to 20 strong offset matches.
- Response size is tied to request fields from family_5.

#### Feature Summary

- Messages with repetition: `3166` (`1.0`)
- Repeated n-gram instances: `3170`
- Top motifs: `0000`x6332, `000000`x3166, `000006`x3166, `000601`x3166, `0001`x3166

### family_7

- Role: `request`
- Messages: `1747`
- Template: `?? ?? 00 00 00 06 01 01 00 ?? 00 01`
- Related families: `family_14`, `family_3`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `0.6042`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.221252` mean=`2.21963`
- Candidate discriminator offset: `9` cardinality=`4` entropy=`1.622696` salience=`0.077977` mutual_information=`0.234079` contrastive_separation=`0.8125` confidence=`0.382874`
- Top discriminator candidates: offset `9` conf=`0.382874` salience=`0.077977`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.718`
- bytes `1`..`1` | kind=`variable` confidence=`0.7014`
- bytes `2`..`5` | kind=`constant` confidence=`0.85`
- bytes `6`..`8` | kind=`constant` confidence=`0.85`
- bytes `9`..`9` | kind=`variable` confidence=`0.7843`
- bytes `10`..`11` | kind=`constant` confidence=`0.725`

#### Field Hypotheses

- bytes `9`..`9` | type=`keyword` confidence=`0.9977`
- bytes `2`..`5` | type=`constant` confidence=`0.99`
- bytes `6`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9805`
- bytes `1`..`1` | type=`keyword` confidence=`0.8592`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`response_size_selector` confidence=`1.0`
- bytes `6`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9977`
- bytes `2`..`5` | label=`constant` confidence=`0.99`
- bytes `6`..`8` | label=`constant` confidence=`0.99`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Echoes request fields from family_3 with up to 20 strong offset matches.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `1747` (`1.0`)
- Repeated n-gram instances: `1750`
- Top motifs: `0000`x3494, `000000`x1747, `000006`x1747, `000601`x1747, `010100`x1747

### family_12

- Role: `request`
- Messages: `1479`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_14`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.284159` max=`3.027169` mean=`2.473296`
- Candidate discriminator offset: `10` cardinality=`4` entropy=`0.315002` salience=`0.4055` mutual_information=`0.23178` contrastive_separation=`0.8125` confidence=`0.526004`
- Top discriminator candidates: offset `10` conf=`0.526004` salience=`0.4055`, offset `9` conf=`0.437641` salience=`0.077977`, offset `7` conf=`0.418082` salience=`0.083791`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7118`
- bytes `1`..`1` | kind=`variable` confidence=`0.7049`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`11` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9675`
- bytes `1`..`1` | type=`keyword` confidence=`0.8323`
- bytes `6`..`11` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `2`..`5` | label=`response_size_selector` confidence=`1.0`
- bytes `6`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `0`..`0` | label=`keyword` confidence=`0.9675`
- bytes `2`..`5` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `1`..`1` | label=`keyword` confidence=`0.8323`

#### Feature Summary

- Messages with repetition: `1479` (`1.0`)
- Repeated n-gram instances: `1485`
- Top motifs: `0000`x2958, `000000`x1479, `2300`x1423, `000006`x1417, `000601`x1417

### family_5

- Role: `response`
- Messages: `1422`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ?? ??`
- Related families: `family_10`, `family_11`, `family_13`, `family_14`
- Role hint: `response`
- Semantic confidence: `0.5297`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.284159` max=`3.027169` mean=`2.98261`
- Candidate discriminator offset: `10` cardinality=`13` entropy=`2.868056` salience=`0.4055` mutual_information=`0.23178` contrastive_separation=`0.953125` confidence=`0.431005`
- Top discriminator candidates: offset `10` conf=`0.431005` salience=`0.4055`, offset `9` conf=`0.427135` salience=`0.077977`, offset `8` conf=`0.394519` salience=`0.084807`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7271`
- bytes `1`..`1` | kind=`variable` confidence=`0.7073`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7588`
- bytes `11`..`11` | kind=`variable` confidence=`0.7522`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`keyword` confidence=`0.9986`
- bytes `6`..`9` | type=`keyword` confidence=`0.9965`
- bytes `10`..`10` | type=`keyword` confidence=`0.9909`
- bytes `0`..`0` | type=`keyword` confidence=`0.9712`
- bytes `1`..`1` | type=`keyword` confidence=`0.82`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`keyword` confidence=`0.9986`
- bytes `6`..`9` | label=`keyword` confidence=`0.9965`
- bytes `10`..`10` | label=`keyword` confidence=`0.9909`
- bytes `0`..`0` | label=`keyword` confidence=`0.9712`
- bytes `2`..`5` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `1`..`1` | label=`keyword` confidence=`0.82`

#### Notes

- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.

#### Feature Summary

- Messages with repetition: `1422` (`1.0`)
- Repeated n-gram instances: `1424`
- Top motifs: `0000`x2845, `000000`x1423, `000005`x1398, `000501`x1398, `010402`x1398

### family_9

- Role: `request`
- Messages: `1374`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_11`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.896241` max=`2.845351` mean=`2.423096`
- Candidate discriminator offset: `10` cardinality=`3` entropy=`0.060232` salience=`0.4055` mutual_information=`0.23178` contrastive_separation=`0.796875` confidence=`0.539851`
- Top discriminator candidates: offset `10` conf=`0.539851` salience=`0.4055`, offset `8` conf=`0.404731` salience=`0.084807`, offset `9` conf=`0.346435` salience=`0.077977`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7149`
- bytes `1`..`1` | kind=`variable` confidence=`0.7085`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`11` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9723`
- bytes `1`..`1` | type=`keyword` confidence=`0.8195`
- bytes `6`..`11` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `2`..`5` | label=`response_size_selector` confidence=`1.0`
- bytes `6`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `0`..`0` | label=`keyword` confidence=`0.9723`
- bytes `2`..`5` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `1`..`1` | label=`keyword` confidence=`0.8195`

#### Feature Summary

- Messages with repetition: `1374` (`1.0`)
- Repeated n-gram instances: `1379`
- Top motifs: `0000`x2748, `000000`x1374, `000006`x1365, `000601`x1365, `0001`x1365

### family_6

- Role: `request`
- Messages: `946`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_14`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5709`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.221252` max=`3.027169` mean=`2.466964`
- Candidate discriminator offset: `10` cardinality=`3` entropy=`0.214834` salience=`0.4055` mutual_information=`0.23178` contrastive_separation=`0.796875` confidence=`0.540109`
- Top discriminator candidates: offset `10` conf=`0.540109` salience=`0.4055`, offset `9` conf=`0.429825` salience=`0.077977`, offset `7` conf=`0.401561` salience=`0.083791`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7259`
- bytes `1`..`1` | kind=`variable` confidence=`0.739`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`11` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9662`
- bytes `1`..`1` | type=`blob` confidence=`0.5`
- bytes `6`..`11` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `2`..`5` | label=`response_size_selector` confidence=`1.0`
- bytes `6`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `0`..`0` | label=`keyword` confidence=`0.9662`
- bytes `2`..`5` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `946` (`1.0`)
- Repeated n-gram instances: `948`
- Top motifs: `0000`x1892, `000000`x946, `000006`x915, `000601`x915, `0006`x915

### family_1

- Role: `response`
- Messages: `886`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_8`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.024296`
- Candidate discriminator offset: `10` cardinality=`11` entropy=`2.094176` salience=`0.4055` mutual_information=`0.23178` contrastive_separation=`0.921875` confidence=`0.429143`
- Top discriminator candidates: offset `10` conf=`0.429143` salience=`0.4055`, offset `9` conf=`0.34673` salience=`0.077977`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7336`
- bytes `1`..`1` | kind=`variable` confidence=`0.7455`
- bytes `2`..`5` | kind=`constant` confidence=`0.85`
- bytes `6`..`9` | kind=`variable` confidence=`0.85`
- bytes `10`..`10` | kind=`variable` confidence=`0.7774`

#### Field Hypotheses

- bytes `6`..`9` | type=`keyword` confidence=`0.9944`
- bytes `2`..`5` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9876`
- bytes `0`..`0` | type=`keyword` confidence=`0.9707`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `6`..`9` | label=`keyword` confidence=`0.9944`
- bytes `2`..`5` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9876`
- bytes `0`..`0` | label=`keyword` confidence=`0.9707`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_8 with up to 20 strong offset matches.
- Response size is tied to request fields from family_8.

#### Feature Summary

- Messages with repetition: `886` (`1.0`)
- Repeated n-gram instances: `886`
- Top motifs: `0000`x1772, `000000`x886, `000005`x886, `000501`x886, `010402`x886
