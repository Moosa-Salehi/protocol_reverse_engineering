# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: D:\tez\practical\protocol_re\data\05_families.json
- **source_feature_summary**: D:\tez\practical\protocol_re\data\03_family_features.json
- **source_keyword_summary**: D:\tez\practical\protocol_re\data\07_keywords.json
- **source_framing_summary**: D:\tez\practical\protocol_re\data\04_framing.json
- **source_relations_summary**: D:\tez\practical\protocol_re\data\08_relations.json
- **source_semantics_summary**: D:\tez\practical\protocol_re\data\09_semantics.json
- **framing_global_summary**: {'common_header_ends': [{'header_end': 6, 'family_count': 14, 'family_ratio': 0.875}, {'header_end': 12, 'family_count': 1, 'family_ratio': 0.0625}, {'header_end': 7, 'family_count': 1, 'family_ratio': 0.0625}], 'field_type_counts': {'length': 49, 'transaction_or_counter': 18, 'discriminator': 11, 'constant': 10}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 16}
- **notes**: Initial auto-generated protocol model assembled from family summaries.

## Evaluation

- Messages: `200000` across `45340` sessions
- Corpus assignment coverage: `1` with `16` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `16` of `16`
- Pair hypotheses: `154658` direction_unknown_ratio=`0`
- Relation edges: `40` echo_edges=`40` length_relation_edges=`26`
- Semantic coverage: `16` of `16` families ratio=`1`
- Top semantic labels: `keyword`x72, `echoed_request_field`x48, `response_size_selector`x35, `constant`x22, `blob`x9, `length`x7
- Framing coverage: `16` of `16` families ratio=`1`

### Evaluation Top Relation Edges

- `family_8` -> `family_8` | pairs=`18535` avg_score=`6.4423` support=`0.3692` lift=`2.145` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_14` | pairs=`17047` avg_score=`4.9454` support=`0.3396` lift=`1.1597` direction=`1` order=`1` echo_fields=`20` length_rules=`0`
- `family_11` -> `family_11` | pairs=`9256` avg_score=`6.4422` support=`0.7497` lift=`4.4732` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_11` | pairs=`8077` avg_score=`4.9465` support=`0.2359` lift=`1.4077` direction=`0.9986` order=`1` echo_fields=`20` length_rules=`0`
- `family_5` -> `family_5` | pairs=`4768` avg_score=`6.3616` support=`0.422` lift=`8.9512` direction=`0.9434` order=`1` echo_fields=`20` length_rules=`20`
- `family_2` -> `family_2` | pairs=`3984` avg_score=`6.4465` support=`0.6847` lift=`10.8647` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_7` -> `family_8` | pairs=`3632` avg_score=`6.4385` support=`0.9409` lift=`5.4667` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_0` | pairs=`3248` avg_score=`6.46` support=`0.0949` lift=`1.1738` direction=`0.9951` order=`1` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_14` | pairs=`2594` avg_score=`6.4364` support=`0.8477` lift=`2.8952` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_0` -> `family_14` | pairs=`2392` avg_score=`4.9692` support=`0.3243` lift=`1.1077` direction=`1` order=`1` echo_fields=`20` length_rules=`4`

## Final Ground Truth Evaluation

- Overall score: `0.3219`
- Verdict: `fail`
- Matched message types: `10` of `11`
- Message type matching: accuracy=`0.5882` precision=`0.625` recall=`0.9091` f1=`0.7407`
- Field boundary: accuracy=`0.1422` precision=`0.1465` recall=`0.8286` f1=`0.2489`
- Field semantics: accuracy=`0` precision=`0` recall=`0` f1=`0`
- Relations: accuracy=`0.175` precision=`0.175` recall=`1` f1=`0.2979`

## LLM Analysis

- Prompt size: `263979` bytes, `263979` characters, estimated tokens=`65995`

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `40`
- Strongest edges:
- `family_8` -> `family_8` | pairs=`18535` avg_score=`6.4423` support=`0.3692` lift=`2.145` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_14` | pairs=`17047` avg_score=`4.9454` support=`0.3396` lift=`1.1597` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_11` -> `family_11` | pairs=`9256` avg_score=`6.4422` support=`0.7497` lift=`4.4732` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_11` | pairs=`8077` avg_score=`4.9465` support=`0.2359` lift=`1.4077` direction=`0.9986` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_5` -> `family_5` | pairs=`4768` avg_score=`6.3616` support=`0.422` lift=`8.9512` direction=`0.9434` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`20`
- `family_2` -> `family_2` | pairs=`3984` avg_score=`6.4465` support=`0.6847` lift=`10.8647` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_7` -> `family_8` | pairs=`3632` avg_score=`6.4385` support=`0.9409` lift=`5.4667` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_0` | pairs=`3248` avg_score=`6.46` support=`0.0949` lift=`1.1738` direction=`0.9951` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_14` | pairs=`2594` avg_score=`6.4364` support=`0.8477` lift=`2.8952` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_0` -> `family_14` | pairs=`2392` avg_score=`4.9692` support=`0.3243` lift=`1.1077` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`4`
- `family_14` -> `noise` | pairs=`2287` avg_score=`5.9793` support=`0.0668` lift=`2.1997` direction=`0.6791` order=`1` flow=`client_to_server->server_to_client` echo_fields=`17`
- `family_5` -> `family_2` | pairs=`2250` avg_score=`4.9482` support=`0.1991` lift=`3.16` direction=`0.9996` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_5` -> `family_4` | pairs=`1858` avg_score=`4.9485` support=`0.1644` lift=`1.812` direction=`0.9995` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_8` -> `family_13` | pairs=`1777` avg_score=`4.9454` support=`0.0354` lift=`2.3545` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_11` -> `family_0` | pairs=`1726` avg_score=`6.4671` support=`0.1398` lift=`1.7296` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_10` -> `family_11` | pairs=`1664` avg_score=`6.4365` support=`0.9369` lift=`5.5902` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `noise` -> `family_11` | pairs=`1623` avg_score=`5.8674` support=`0.3438` lift=`2.0512` direction=`0.6057` order=`1` flow=`client_to_server->server_to_client` echo_fields=`17`
- `noise` -> `family_14` | pairs=`1559` avg_score=`5.9374` support=`0.3302` lift=`1.1278` direction=`0.6543` order=`1` flow=`client_to_server->server_to_client` echo_fields=`17`
- `family_4` -> `family_0` | pairs=`1559` avg_score=`6.4645` support=`0.1048` lift=`1.2968` direction=`0.9981` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_8` -> `noise` | pairs=`1536` avg_score=`5.5873` support=`0.0306` lift=`1.0074` direction=`0.5781` order=`1` flow=`server_to_client->client_to_server` echo_fields=`17`
- `family_0` -> `family_11` | pairs=`1388` avg_score=`4.9691` support=`0.1882` lift=`1.1229` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`4`
- `family_6` -> `family_8` | pairs=`1367` avg_score=`6.4662` support=`0.9942` lift=`5.776` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_14` | pairs=`1316` avg_score=`6.4683` support=`0.8934` lift=`3.0513` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_8` -> `family_3` | pairs=`1275` avg_score=`6.4662` support=`0.0254` lift=`2.8096` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_3` -> `family_14` | pairs=`1125` avg_score=`4.9688` support=`0.8402` lift=`2.8695` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`

## Families

- Total families: `16`
- Families shown below: `16`

### family_8

- Role: `request`
- Messages: `51024`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_13`, `family_14`, `family_3`, `family_6`, `family_7`, `family_8`, `noise`
- Role hint: `request`
- Semantic confidence: `0.62`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.521928` max=`2.732159` mean=`2.3074`
- Candidate keyword offset: `9` cardinality=`7` entropy=`1.9916`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6939`
- bytes `1`..`1` | kind=`variable` confidence=`0.6424`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7881`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.778`
- bytes `8`..`8` | kind=`variable` confidence=`0.7881`
- bytes `9`..`9` | kind=`variable` confidence=`0.7752`
- bytes `10`..`10` | kind=`variable` confidence=`0.7537`
- bytes `11`..`11` | kind=`variable` confidence=`0.773`

#### Field Hypotheses

- bytes `2`..`4` | type=`framing_constant` confidence=`1.0`
- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`0.9999`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `9`..`9` | type=`keyword` confidence=`0.9999`
- bytes `11`..`11` | type=`keyword` confidence=`0.9999`
- bytes `10`..`10` | type=`keyword` confidence=`0.9997`

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

- Echoes request fields from family_6 with up to 20 strong offset matches.
- Response size is tied to request fields from family_6.
- Echoes request fields from family_7 with up to 20 strong offset matches.
- Response size is tied to request fields from family_7.
- Echoes request fields from family_8 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `51024` (`1.0`)
- Repeated n-gram instances: `65546`
- Top motifs: `0000`x102459, `000000`x51178, `0101`x35363, `0100`x28140, `0006`x24654

### family_14

- Role: `response`
- Messages: `46674`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_10`, `family_11`, `family_12`, `family_13`, `family_3`, `family_8`, `family_9`, `noise`
- Role hint: `response`
- Semantic confidence: `0.6349`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.318024`
- Candidate keyword offset: `9` cardinality=`7` entropy=`2.0048`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6966`
- bytes `1`..`1` | kind=`variable` confidence=`0.6425`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7883`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7781`
- bytes `8`..`8` | kind=`variable` confidence=`0.7883`
- bytes `9`..`9` | kind=`variable` confidence=`0.7749`
- bytes `10`..`10` | kind=`variable` confidence=`0.7555`
- bytes `11`..`11` | kind=`variable` confidence=`0.7736`

#### Field Hypotheses

- bytes `2`..`4` | type=`framing_constant` confidence=`1.0`
- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`0.9999`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `9`..`9` | type=`keyword` confidence=`0.9999`
- bytes `11`..`11` | type=`keyword` confidence=`0.9998`
- bytes `10`..`10` | type=`keyword` confidence=`0.9997`

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
- bytes `9`..`9` | label=`keyword` confidence=`0.9999`
- bytes `11`..`11` | label=`keyword` confidence=`0.9998`
- bytes `10`..`10` | label=`keyword` confidence=`0.9997`
- bytes `0`..`0` | label=`keyword` confidence=`0.9989`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_13 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `46674` (`1.0`)
- Repeated n-gram instances: `59917`
- Top motifs: `0000`x93669, `000000`x46817, `0101`x32515, `0100`x25931, `0006`x23060

### family_11

- Role: `response`
- Messages: `26018`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_14`, `family_9`, `noise`
- Role hint: `response`
- Semantic confidence: `0.6596`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.320438`
- Candidate keyword offset: `9` cardinality=`7` entropy=`1.9965`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7114`
- bytes `1`..`1` | kind=`variable` confidence=`0.6454`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7881`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7779`
- bytes `8`..`8` | kind=`variable` confidence=`0.7881`
- bytes `9`..`9` | kind=`variable` confidence=`0.7752`
- bytes `10`..`10` | kind=`variable` confidence=`0.7557`
- bytes `11`..`11` | kind=`variable` confidence=`0.7724`

#### Field Hypotheses

- bytes `2`..`4` | type=`framing_constant` confidence=`1.0`
- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `7`..`7` | type=`keyword` confidence=`0.9998`
- bytes `9`..`9` | type=`keyword` confidence=`0.9997`
- bytes `11`..`11` | type=`keyword` confidence=`0.9997`
- bytes `10`..`10` | type=`keyword` confidence=`0.9996`

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
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_11 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `26018` (`1.0`)
- Repeated n-gram instances: `33345`
- Top motifs: `0000`x52211, `000000`x26091, `0101`x18027, `0100`x14342, `0006`x12475

### family_4

- Role: `response`
- Messages: `18323`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_10`, `family_5`
- Role hint: `response`
- Semantic confidence: `0.6207`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`3.027169` mean=`2.361278`
- Candidate keyword offset: `9` cardinality=`16` entropy=`2.649`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6824`
- bytes `1`..`1` | kind=`variable` confidence=`0.683`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.789`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7771`
- bytes `8`..`8` | kind=`variable` confidence=`0.789`
- bytes `9`..`9` | kind=`variable` confidence=`0.7607`
- bytes `10`..`10` | kind=`variable` confidence=`0.7616`
- bytes `11`..`11` | kind=`variable` confidence=`0.7824`

#### Field Hypotheses

- bytes `2`..`4` | type=`framing_constant` confidence=`1.0`
- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9998`
- bytes `11`..`11` | type=`keyword` confidence=`0.9998`
- bytes `7`..`7` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9991`
- bytes `10`..`10` | type=`keyword` confidence=`0.9978`

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
- Echoes request fields from family_5 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `18323` (`1.0`)
- Repeated n-gram instances: `21509`
- Top motifs: `0000`x36685, `000000`x18323, `0006`x10895, `000006`x10686, `000601`x10686

### family_0

- Role: `response`
- Messages: `15624`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 00`
- Related families: `family_11`, `family_13`, `family_14`, `family_2`, `family_4`, `family_5`
- Role hint: `response`
- Semantic confidence: `0.5752`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.947339` max=`3.027169` mean=`2.86454`
- Candidate keyword offset: `10` cardinality=`75` entropy=`4.7098`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6721`
- bytes `1`..`1` | kind=`variable` confidence=`0.646`
- bytes `2`..`9` | kind=`variable` confidence=`0.4314`
- bytes `10`..`10` | kind=`variable` confidence=`0.7158`
- bytes `11`..`11` | kind=`constant` confidence=`0.8935`

#### Field Hypotheses

- bytes `2`..`4` | type=`framing_constant` confidence=`1.0`
- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `10`..`10` | type=`keyword` confidence=`0.9952`
- bytes `0`..`0` | type=`keyword` confidence=`0.9917`
- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9836`
- bytes `5`..`5` | type=`framing_discriminator` confidence=`0.825`
- bytes `0`..`1` | type=`framing_transaction_or_counter` confidence=`0.6258` endian=`big`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`keyword` confidence=`0.9952`
- bytes `2`..`9` | label=`response_size_selector` confidence=`0.9929`
- bytes `0`..`0` | label=`keyword` confidence=`0.9917`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9836`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.
- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.
- Echoes request fields from family_2 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `15624` (`1.0`)
- Repeated n-gram instances: `18861`
- Top motifs: `0000`x34383, `000000`x15688, `000005`x12329, `000501`x12329, `010402`x12329

### family_5

- Role: `request`
- Messages: `11696`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01 00 04 00 00 00 06 01 01 00 0e 00 01`
- Related families: `family_0`, `family_2`, `family_4`, `family_5`
- Role hint: `request`
- Semantic confidence: `0.6762`
- Length stats: min=`10` max=`24` distinct=`4`
- Entropy summary: min=`1.360964` max=`3.027169` mean=`2.342643`
- Candidate keyword offset: `9` cardinality=`15` entropy=`2.6319`
- Framing hypothesis: header=`0`..`11` body_start=`12` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6978`
- bytes `1`..`1` | kind=`variable` confidence=`0.6817`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7887`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.777`
- bytes `8`..`8` | kind=`variable` confidence=`0.7887`
- bytes `9`..`9` | kind=`variable` confidence=`0.7612`
- bytes `10`..`10` | kind=`variable` confidence=`0.762`
- bytes `11`..`23` | kind=`constant` confidence=`0.505`

#### Field Hypotheses

- bytes `2`..`4` | type=`framing_constant` confidence=`1.0`
- bytes `6`..`6` | type=`framing_constant` confidence=`1.0`
- bytes `2`..`5` | type=`framing_length` confidence=`0.9999` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`0.9999` endian=`big`
- bytes `5`..`5` | type=`length` confidence=`0.9999` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`0.9999` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9997`
- bytes `7`..`7` | type=`keyword` confidence=`0.9996`
- bytes `11`..`11` | type=`framing_length` confidence=`0.9988` endian=`big`
- bytes `9`..`9` | type=`keyword` confidence=`0.9987`

#### Framing Hypotheses

- header_end=`12` body_start=`12` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`13` body_start=`13` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`18` body_start=`18` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`23` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`23` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`0.9999`
- bytes `8`..`8` | label=`keyword` confidence=`0.9997`
- bytes `7`..`7` | label=`keyword` confidence=`0.9996`
- bytes `9`..`9` | label=`keyword` confidence=`0.9987`
- bytes `10`..`10` | label=`echoed_request_field` confidence=`0.9972`
- bytes `10`..`10` | label=`response_size_selector` confidence=`0.9972`

#### Notes

- Echoes request fields from family_5 with up to 20 strong offset matches.
- Response size is tied to request fields from family_5.

#### Feature Summary

- Messages with repetition: `11696` (`1.0`)
- Repeated n-gram instances: `14384`
- Top motifs: `0000`x23595, `000000`x11864, `0006`x6977, `0601`x6755, `000006`x6751

### family_2

- Role: `response`
- Messages: `9951`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_2`, `family_5`
- Role hint: `response`
- Semantic confidence: `0.6045`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`3.027169` mean=`2.352236`
- Candidate keyword offset: `9` cardinality=`11` entropy=`2.6579`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.711`
- bytes `1`..`1` | kind=`variable` confidence=`0.6787`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7893`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7773`
- bytes `8`..`8` | kind=`variable` confidence=`0.7893`
- bytes `9`..`9` | kind=`variable` confidence=`0.7606`
- bytes `10`..`10` | kind=`variable` confidence=`0.7661`
- bytes `11`..`11` | kind=`variable` confidence=`0.7826`

#### Field Hypotheses

- bytes `2`..`4` | type=`framing_constant` confidence=`1.0`
- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9997`
- bytes `11`..`11` | type=`keyword` confidence=`0.9996`
- bytes `7`..`7` | type=`keyword` confidence=`0.9995`
- bytes `9`..`9` | type=`keyword` confidence=`0.9989`
- bytes `10`..`10` | type=`keyword` confidence=`0.9984`

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
- Echoes request fields from family_5 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `9951` (`1.0`)
- Repeated n-gram instances: `12144`
- Top motifs: `0000`x20069, `000000`x10070, `0101`x5869, `000006`x5823, `000601`x5823

### noise

- Role: `request`
- Messages: `5882`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? ??`
- Related families: `family_10`, `family_11`, `family_14`, `family_8`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5364`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.729574` max=`3.027169` mean=`2.607803`
- Candidate keyword offset: `10` cardinality=`50` entropy=`2.594`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6871`
- bytes `1`..`1` | kind=`variable` confidence=`0.6568`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7979`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7817`
- bytes `8`..`8` | kind=`variable` confidence=`0.7979`
- bytes `9`..`9` | kind=`variable` confidence=`0.7786`
- bytes `10`..`10` | kind=`variable` confidence=`0.7647`
- bytes `11`..`11` | kind=`variable` confidence=`0.7725`

#### Field Hypotheses

- bytes `2`..`4` | type=`framing_constant` confidence=`1.0`
- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9997`
- bytes `7`..`7` | type=`keyword` confidence=`0.9993`
- bytes `11`..`11` | type=`keyword` confidence=`0.9981`
- bytes `9`..`9` | type=`keyword` confidence=`0.9971`
- bytes `10`..`10` | type=`keyword` confidence=`0.9915`

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

- Echoes request fields from family_14 with up to 17 strong offset matches.
- Echoes request fields from family_8 with up to 17 strong offset matches.

#### Feature Summary

- Messages with repetition: `5882` (`1.0`)
- Repeated n-gram instances: `6046`
- Top motifs: `0000`x11821, `000000`x5939, `0006`x3326, `000006`x3324, `000601`x3324

### family_7

- Role: `request`
- Messages: `3860`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_3`, `family_8`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.825011` max=`2.450826` mean=`2.201685`
- Candidate keyword offset: `9` cardinality=`7` entropy=`2.246`
- Framing hypothesis: header=`0`..`6` body_start=`7` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7166`
- bytes `1`..`1` | kind=`variable` confidence=`0.6717`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.797`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7701`
- bytes `10`..`11` | kind=`variable` confidence=`0.5451`

#### Field Hypotheses

- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `2`..`6` | type=`framing_constant` confidence=`1.0`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `10`..`11` | type=`keyword` confidence=`0.9995`
- bytes `7`..`7` | type=`keyword` confidence=`0.9987`
- bytes `9`..`9` | type=`keyword` confidence=`0.9982`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9891`

#### Framing Hypotheses

- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator
- header_end=`9` body_start=`9` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length, `7`..`7` discriminator

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`keyword` confidence=`0.9995`
- bytes `7`..`7` | label=`keyword` confidence=`0.9987`
- bytes `9`..`9` | label=`keyword` confidence=`0.9982`
- bytes `2`..`6` | label=`constant` confidence=`0.99`

#### Feature Summary

- Messages with repetition: `3860` (`1.0`)
- Repeated n-gram instances: `3863`
- Top motifs: `0000`x7720, `000000`x3860, `000006`x3860, `000601`x3860, `0006`x3860

### family_13

- Role: `request`
- Messages: `3060`
- Template: `?? ?? 00 00 00 06 01 01 00 ?? 00 01`
- Related families: `family_0`, `family_14`, `family_3`, `family_8`
- Role hint: `request`
- Semantic confidence: `0.5364`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.450826` mean=`2.231006`
- Candidate keyword offset: `9` cardinality=`5` entropy=`1.9247`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7091`
- bytes `1`..`1` | kind=`variable` confidence=`0.682`
- bytes `2`..`8` | kind=`variable` confidence=`0.4991`
- bytes `9`..`9` | kind=`variable` confidence=`0.7773`
- bytes `10`..`11` | kind=`constant` confidence=`0.725`

#### Field Hypotheses

- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `9`..`9` | type=`keyword` confidence=`0.9984`
- bytes `10`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9843`
- bytes `1`..`1` | type=`keyword` confidence=`0.9193`
- bytes `0`..`1` | type=`framing_transaction_or_counter` confidence=`0.7023` endian=`big`
- bytes `0`..`3` | type=`framing_transaction_or_counter` confidence=`0.6478` endian=`big`
- bytes `2`..`8` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9984`
- bytes `10`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9843`
- bytes `1`..`1` | label=`keyword` confidence=`0.9193`
- bytes `2`..`8` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_3 with up to 20 strong offset matches.
- Response size is tied to request fields from family_3.
- Echoes request fields from family_8 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `3060` (`1.0`)
- Repeated n-gram instances: `3064`
- Top motifs: `0000`x6120, `000000`x3060, `000006`x3060, `000601`x3060, `0001`x3060

### family_10

- Role: `request`
- Messages: `1776`
- Template: `?? ?? 00 00 00 06 01 01 00 ?? 00 01`
- Related families: `family_11`, `family_14`, `family_4`, `noise`
- Role hint: `request`
- Semantic confidence: `0.6036`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.221252` mean=`2.21975`
- Candidate keyword offset: `9` cardinality=`4` entropy=`1.6385`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7177`
- bytes `1`..`1` | kind=`variable` confidence=`0.7007`
- bytes `2`..`8` | kind=`constant` confidence=`0.6812`
- bytes `9`..`9` | kind=`variable` confidence=`0.7839`
- bytes `10`..`11` | kind=`constant` confidence=`0.725`

#### Field Hypotheses

- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `9`..`9` | type=`keyword` confidence=`0.9977`
- bytes `2`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9814`
- bytes `1`..`1` | type=`keyword` confidence=`0.8615`
- bytes `0`..`1` | type=`framing_transaction_or_counter` confidence=`0.7025` endian=`big`
- bytes `0`..`3` | type=`framing_transaction_or_counter` confidence=`0.6552` endian=`big`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9977`
- bytes `2`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9814`
- bytes `1`..`1` | label=`keyword` confidence=`0.8615`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Echoes request fields from family_4 with up to 20 strong offset matches.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `1776` (`1.0`)
- Repeated n-gram instances: `1779`
- Top motifs: `0000`x3552, `000000`x1776, `000006`x1776, `000601`x1776, `010100`x1776

### family_12

- Role: `request`
- Messages: `1506`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_14`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.284159` max=`3.027169` mean=`2.472511`
- Candidate keyword offset: `10` cardinality=`4` entropy=`0.306`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7109`
- bytes `1`..`1` | kind=`variable` confidence=`0.7038`
- bytes `2`..`11` | kind=`variable` confidence=`0.4529`

#### Field Hypotheses

- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9688`
- bytes `1`..`1` | type=`keyword` confidence=`0.8353`
- bytes `0`..`1` | type=`framing_transaction_or_counter` confidence=`0.8013` endian=`big`
- bytes `0`..`3` | type=`framing_transaction_or_counter` confidence=`0.79` endian=`big`
- bytes `2`..`11` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `0`..`0` | label=`keyword` confidence=`0.9688`
- bytes `1`..`1` | label=`keyword` confidence=`0.8353`
- bytes `2`..`11` | label=`blob` confidence=`0.5`

#### Feature Summary

- Messages with repetition: `1506` (`1.0`)
- Repeated n-gram instances: `1512`
- Top motifs: `0000`x3012, `000000`x1506, `2300`x1451, `000006`x1445, `000601`x1445

### family_3

- Role: `response`
- Messages: `1409`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ?? 01`
- Related families: `family_13`, `family_14`, `family_7`, `family_8`
- Role hint: `response`
- Semantic confidence: `0.5303`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.450826` max=`3.027169` mean=`2.987634`
- Candidate keyword offset: `10` cardinality=`12` entropy=`2.8312`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7276`
- bytes `1`..`1` | kind=`variable` confidence=`0.7078`
- bytes `2`..`9` | kind=`variable` confidence=`0.4313`
- bytes `10`..`10` | kind=`variable` confidence=`0.7594`
- bytes `11`..`11` | kind=`constant` confidence=`0.8661`

#### Field Hypotheses

- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `10`..`10` | type=`keyword` confidence=`0.9915`
- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9723`
- bytes `1`..`1` | type=`keyword` confidence=`0.8183`
- bytes `0`..`1` | type=`framing_transaction_or_counter` confidence=`0.6563` endian=`big`
- bytes `0`..`3` | type=`framing_transaction_or_counter` confidence=`0.6563` endian=`big`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`keyword` confidence=`0.9915`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9723`
- bytes `1`..`1` | label=`keyword` confidence=`0.8183`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_7 with up to 20 strong offset matches.
- Response size is tied to request fields from family_7.
- Echoes request fields from family_8 with up to 20 strong offset matches.
- Response size is tied to request fields from family_8.

#### Feature Summary

- Messages with repetition: `1409` (`1.0`)
- Repeated n-gram instances: `1411`
- Top motifs: `0000`x2819, `000000`x1410, `000005`x1398, `000501`x1398, `010402`x1398

### family_6

- Role: `request`
- Messages: `1375`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_8`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.896241` max=`2.845351` mean=`2.418458`
- Candidate keyword offset: `9` cardinality=`3` entropy=`0.3997`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.715`
- bytes `1`..`1` | kind=`variable` confidence=`0.7088`
- bytes `2`..`11` | kind=`variable` confidence=`0.4552`

#### Field Hypotheses

- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9724`
- bytes `0`..`1` | type=`framing_transaction_or_counter` confidence=`0.8246` endian=`big`
- bytes `1`..`1` | type=`keyword` confidence=`0.8196`
- bytes `0`..`3` | type=`framing_transaction_or_counter` confidence=`0.7992` endian=`big`
- bytes `2`..`11` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `2`..`6` constant, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `0`..`0` | label=`keyword` confidence=`0.9724`
- bytes `1`..`1` | label=`keyword` confidence=`0.8196`
- bytes `2`..`11` | label=`blob` confidence=`0.5`

#### Feature Summary

- Messages with repetition: `1375` (`1.0`)
- Repeated n-gram instances: `1380`
- Top motifs: `0000`x2750, `000000`x1375, `000006`x1367, `000601`x1367, `0001`x1367

### family_9

- Role: `request`
- Messages: `936`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_11`, `family_14`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5701`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.284159` max=`3.027169` mean=`2.468117`
- Candidate keyword offset: `7` cardinality=`3` entropy=`0.2317`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7265`
- bytes `1`..`1` | kind=`variable` confidence=`0.74`
- bytes `2`..`11` | kind=`variable` confidence=`0.4537`

#### Field Hypotheses

- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `0`..`0` | type=`keyword` confidence=`0.9658`
- bytes `0`..`1` | type=`framing_transaction_or_counter` confidence=`0.812` endian=`big`
- bytes `0`..`3` | type=`framing_transaction_or_counter` confidence=`0.799` endian=`big`
- bytes `1`..`1` | type=`blob` confidence=`0.5`
- bytes `2`..`11` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `0`..`0` | label=`keyword` confidence=`0.9658`
- bytes `1`..`1` | label=`blob` confidence=`0.5`
- bytes `2`..`11` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `936` (`1.0`)
- Repeated n-gram instances: `938`
- Top motifs: `0000`x1872, `000000`x936, `2300`x907, `000006`x905, `000601`x905

### family_1

- Role: `response`
- Messages: `886`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_11`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.024296`
- Candidate keyword offset: `10` cardinality=`11` entropy=`2.0942`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7336`
- bytes `1`..`1` | kind=`variable` confidence=`0.7455`
- bytes `2`..`9` | kind=`variable` confidence=`0.432`
- bytes `10`..`10` | kind=`variable` confidence=`0.7774`

#### Field Hypotheses

- bytes `2`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `4`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `5`..`5` | type=`framing_length` confidence=`1.0` endian=`big`
- bytes `10`..`10` | type=`keyword` confidence=`0.9876`
- bytes `0`..`0` | type=`keyword` confidence=`0.9707`
- bytes `0`..`1` | type=`framing_transaction_or_counter` confidence=`0.7267` endian=`big`
- bytes `0`..`3` | type=`framing_transaction_or_counter` confidence=`0.7143` endian=`big`
- bytes `1`..`1` | type=`blob` confidence=`0.5`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`5` length, `4`..`5` length, `5`..`5` length, `7`..`7` length

#### Semantic Labels

- bytes `10`..`10` | label=`keyword` confidence=`0.9876`
- bytes `0`..`0` | label=`keyword` confidence=`0.9707`
- bytes `1`..`1` | label=`blob` confidence=`0.5`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.

#### Feature Summary

- Messages with repetition: `886` (`1.0`)
- Repeated n-gram instances: `886`
- Top motifs: `0000`x1772, `000000`x886, `000005`x886, `000501`x886, `010402`x886
