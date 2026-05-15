# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: D:\tez\practical\protocol_re\data\04_families.json
- **source_feature_summary**: D:\tez\practical\protocol_re\data\03_family_features.json
- **source_keyword_summary**: D:\tez\practical\protocol_re\data\06_keywords.json
- **source_relations_summary**: D:\tez\practical\protocol_re\data\08_relations.json
- **source_semantics_summary**: D:\tez\practical\protocol_re\data\09_semantics.json
- **notes**: Initial auto-generated protocol model assembled from family summaries.

## Evaluation

- Messages: `100000` across `20832` sessions
- Corpus assignment coverage: `1` with `16` families
- Clustering sample: `90619` messages ratio=`0.9062`
- Parseable families: `16` of `16`
- Pair hypotheses: `79168` direction_unknown_ratio=`0`
- Relation edges: `38` echo_edges=`38` length_relation_edges=`31`
- Semantic coverage: `16` of `16` families ratio=`1`
- Top semantic labels: `keyword`x46, `echoed_request_field`x42, `response_size_selector`x24, `constant`x18, `blob`x13, `length`x4, `transaction_or_correlation_id`x1

### Evaluation Top Relation Edges

- `family_14` -> `family_14` | pairs=`10360` avg_score=`6.4365` support=`0.3662` lift=`2.4364` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_7` | pairs=`6413` avg_score=`4.9455` support=`0.2574` lift=`1.1883` direction=`1` order=`1` echo_fields=`20` length_rules=`0`
- `family_7` -> `family_7` | pairs=`6406` avg_score=`6.4417` support=`0.7548` lift=`3.4839` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_12` | pairs=`2761` avg_score=`4.9688` support=`0.8569` lift=`2.1617` direction=`1` order=`1` echo_fields=`20` length_rules=`2`
- `family_14` -> `family_13` | pairs=`2391` avg_score=`6.4622` support=`0.0845` lift=`2.0093` direction=`1` order=`1` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_0` | pairs=`2146` avg_score=`6.4611` support=`0.0862` lift=`1.2827` direction=`0.9958` order=`1` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_0` | pairs=`2119` avg_score=`6.456` support=`0.0749` lift=`1.1152` direction=`0.9924` order=`1` echo_fields=`20` length_rules=`14`
- `family_12` -> `noise` | pairs=`1555` avg_score=`5.767` support=`0.0624` lift=`1.1286` direction=`0.5395` order=`1` echo_fields=`17` length_rules=`0`
- `family_0` -> `family_12` | pairs=`1545` avg_score=`4.9693` support=`0.515` lift=`1.2992` direction=`1` order=`1` echo_fields=`20` length_rules=`4`
- `noise` -> `family_7` | pairs=`1299` avg_score=`6.0546` support=`0.2659` lift=`1.2271` direction=`0.7321` order=`1` echo_fields=`17` length_rules=`0`

## Final Ground Truth Evaluation

- Overall score: `0.3849`
- Verdict: `fail`
- Matched message types: `11` of `11`
- Message type matching: accuracy=`0.6875` precision=`0.6875` recall=`1` f1=`0.8148`
- Field boundary: accuracy=`0.2609` precision=`0.2963` recall=`0.6857` f1=`0.4138`
- Field semantics: accuracy=`0` precision=`0` recall=`0` f1=`0`
- Relations: accuracy=`0.1842` precision=`0.1842` recall=`1` f1=`0.3111`

## LLM Analysis

- Model: `deepseek-r1:8b`
- Prompt size: `148707` bytes, `148707` characters, estimated tokens=`37177`

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `38`
- Strongest edges:
- `family_14` -> `family_14` | pairs=`10360` avg_score=`6.4365` support=`0.3662` lift=`2.4364` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_7` | pairs=`6413` avg_score=`4.9455` support=`0.2574` lift=`1.1883` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_7` -> `family_7` | pairs=`6406` avg_score=`6.4417` support=`0.7548` lift=`3.4839` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_13` -> `family_12` | pairs=`2761` avg_score=`4.9688` support=`0.8569` lift=`2.1617` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_14` -> `family_13` | pairs=`2391` avg_score=`6.4622` support=`0.0845` lift=`2.0093` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_0` | pairs=`2146` avg_score=`6.4611` support=`0.0862` lift=`1.2827` direction=`0.9958` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_14` -> `family_0` | pairs=`2119` avg_score=`6.456` support=`0.0749` lift=`1.1152` direction=`0.9924` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_12` -> `noise` | pairs=`1555` avg_score=`5.767` support=`0.0624` lift=`1.1286` direction=`0.5395` order=`1` flow=`client_to_server->server_to_client` echo_fields=`17`
- `family_0` -> `family_12` | pairs=`1545` avg_score=`4.9693` support=`0.515` lift=`1.2992` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`4`
- `noise` -> `family_7` | pairs=`1299` avg_score=`6.0546` support=`0.2659` lift=`1.2271` direction=`0.7321` order=`1` flow=`client_to_server->server_to_client` echo_fields=`17`
- `family_14` -> `family_4` | pairs=`1198` avg_score=`6.4662` support=`0.0423` lift=`2.7983` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_4` -> `family_12` | pairs=`1119` avg_score=`4.9688` support=`0.9833` lift=`2.4805` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_7` -> `family_0` | pairs=`979` avg_score=`6.4678` support=`0.1154` lift=`1.7176` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_12` -> `family_1` | pairs=`888` avg_score=`6.4663` support=`0.0356` lift=`3.1782` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_10` -> `family_12` | pairs=`858` avg_score=`6.4683` support=`1` lift=`2.5226` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_9` -> `family_14` | pairs=`809` avg_score=`6.437` support=`1` lift=`6.6533` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_11` -> `family_12` | pairs=`761` avg_score=`6.437` support=`1` lift=`2.5226` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_0` -> `family_7` | pairs=`750` avg_score=`4.9693` support=`0.25` lift=`1.1539` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`4`
- `family_8` -> `family_13` | pairs=`720` avg_score=`6.4683` support=`0.8431` lift=`20.0438` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_5` -> `family_7` | pairs=`692` avg_score=`6.4683` support=`1` lift=`4.6157` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_7` -> `family_2` | pairs=`645` avg_score=`6.4671` support=`0.076` lift=`9.3281` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_6` -> `family_7` | pairs=`644` avg_score=`6.437` support=`1` lift=`4.6157` direction=`1` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`14`
- `family_1` -> `family_7` | pairs=`549` avg_score=`4.9688` support=`0.8912` lift=`4.1136` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20` length_rules=`2`
- `family_12` -> `family_5` | pairs=`495` avg_score=`4.9464` support=`0.0199` lift=`2.28` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`
- `family_14` -> `family_10` | pairs=`457` avg_score=`4.9388` support=`0.0162` lift=`1.5749` direction=`1` order=`1` flow=`server_to_client->client_to_server` echo_fields=`20`

## Families

- Total families: `16`
- Families shown below: `16`

### family_12

- Role: `request`
- Messages: `32401`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_13`, `family_4`, `family_5`, `family_7`, `noise`
- Role hint: `request`
- Semantic confidence: `0.6201`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.31869`
- Candidate keyword offset: `9` cardinality=`7` entropy=`2.0917`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7075`
- bytes `1`..`1` | kind=`variable` confidence=`0.6429`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7888`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7782`
- bytes `8`..`8` | kind=`variable` confidence=`0.7888`
- bytes `9`..`9` | kind=`variable` confidence=`0.773`
- bytes `10`..`10` | kind=`variable` confidence=`0.761`
- bytes `11`..`11` | kind=`variable` confidence=`0.7763`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `7`..`7` | type=`keyword` confidence=`0.9998`
- bytes `9`..`9` | type=`keyword` confidence=`0.9998`
- bytes `11`..`11` | type=`keyword` confidence=`0.9998`
- bytes `10`..`10` | type=`keyword` confidence=`0.9997`
- bytes `0`..`0` | type=`keyword` confidence=`0.9989`
- bytes `1`..`1` | type=`keyword` confidence=`0.9921`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

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
- bytes `8`..`8` | label=`keyword` confidence=`0.9999`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_11 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `32401` (`1.0`)
- Repeated n-gram instances: `41062`
- Top motifs: `0000`x65061, `000000`x32524, `0101`x22118, `0100`x18033, `0006`x16938

### family_14

- Role: `request`
- Messages: `28629`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? 00 01`
- Related families: `family_0`, `family_10`, `family_13`, `family_14`, `family_4`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5967`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.521928` max=`2.450826` mean=`2.264221`
- Candidate keyword offset: `9` cardinality=`7` entropy=`2.2076`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7075`
- bytes `1`..`1` | kind=`variable` confidence=`0.6433`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7971`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7811`
- bytes `8`..`8` | kind=`variable` confidence=`0.7971`
- bytes `9`..`9` | kind=`variable` confidence=`0.7704`
- bytes `10`..`11` | kind=`variable` confidence=`0.5079`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9999`
- bytes `10`..`11` | type=`keyword` confidence=`0.9999`
- bytes `7`..`7` | type=`keyword` confidence=`0.9998`
- bytes `9`..`9` | type=`keyword` confidence=`0.9998`
- bytes `0`..`0` | type=`keyword` confidence=`0.9987`
- bytes `1`..`1` | type=`keyword` confidence=`0.9911`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.
- Echoes request fields from family_9 with up to 20 strong offset matches.
- Response size is tied to request fields from family_9.

#### Feature Summary

- Messages with repetition: `28629` (`1.0`)
- Repeated n-gram instances: `37047`
- Top motifs: `0000`x57527, `000000`x28742, `0101`x22129, `0100`x17955, `0601`x16733

### family_7

- Role: `response`
- Messages: `17180`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_12`, `family_2`, `family_3`, `family_5`, `family_6`, `family_7`, `noise`
- Role hint: `response`
- Semantic confidence: `0.673`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.321538`
- Candidate keyword offset: `9` cardinality=`7` entropy=`2.1007`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7261`
- bytes `1`..`1` | kind=`variable` confidence=`0.6454`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7882`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7782`
- bytes `8`..`8` | kind=`variable` confidence=`0.7882`
- bytes `9`..`9` | kind=`variable` confidence=`0.7729`
- bytes `10`..`10` | kind=`variable` confidence=`0.7599`
- bytes `11`..`11` | kind=`variable` confidence=`0.7743`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9998`
- bytes `11`..`11` | type=`keyword` confidence=`0.9998`
- bytes `7`..`7` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9996`
- bytes `10`..`10` | type=`keyword` confidence=`0.9995`
- bytes `0`..`0` | type=`keyword` confidence=`0.9987`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9851`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`0.9998`
- bytes `11`..`11` | label=`keyword` confidence=`0.9998`
- bytes `7`..`7` | label=`keyword` confidence=`0.9997`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from family_12 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `17180` (`1.0`)
- Repeated n-gram instances: `21828`
- Top motifs: `0000`x34499, `000000`x17247, `0101`x11817, `0100`x9564, `0006`x8609

### noise

- Role: `response`
- Messages: `5658`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? ??`
- Related families: `family_0`, `family_10`, `family_12`, `family_13`, `family_5`, `family_6`, `family_7`, `family_8`
- Role hint: `response`
- Semantic confidence: `0.5348`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.729574` max=`3.027169` mean=`2.538388`
- Candidate keyword offset: `10` cardinality=`45` entropy=`2.3311`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6913`
- bytes `1`..`1` | kind=`variable` confidence=`0.6576`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7983`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7809`
- bytes `8`..`8` | kind=`variable` confidence=`0.7983`
- bytes `9`..`9` | kind=`variable` confidence=`0.7704`
- bytes `10`..`10` | kind=`variable` confidence=`0.7704`
- bytes `11`..`11` | kind=`variable` confidence=`0.7765`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9996`
- bytes `7`..`7` | type=`keyword` confidence=`0.9991`
- bytes `11`..`11` | type=`keyword` confidence=`0.9984`
- bytes `9`..`9` | type=`keyword` confidence=`0.9968`
- bytes `10`..`10` | type=`keyword` confidence=`0.992`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9834`
- bytes `1`..`1` | type=`keyword` confidence=`0.9548`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`0.9996`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_12 with up to 17 strong offset matches.
- Echoes request fields from family_8 with up to 20 strong offset matches.
- Response size is tied to request fields from family_8.

#### Feature Summary

- Messages with repetition: `5658` (`1.0`)
- Repeated n-gram instances: `5835`
- Top motifs: `0000`x11378, `000000`x5720, `000006`x3418, `000601`x3418, `0006`x3418

### family_0

- Role: `response`
- Messages: `5343`
- Template: `?? ?? 00 00 00 05 01 04 02 2c ?? 00`
- Related families: `family_10`, `family_11`, `family_12`, `family_14`, `family_7`, `noise`
- Role hint: `response`
- Semantic confidence: `0.6464`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.450826` max=`3.027169` mean=`3.007968`
- Candidate keyword offset: `10` cardinality=`56` entropy=`4.382`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6858`
- bytes `1`..`1` | kind=`variable` confidence=`0.6574`
- bytes `2`..`9` | kind=`variable` confidence=`0.4297`
- bytes `10`..`10` | kind=`variable` confidence=`0.7252`
- bytes `11`..`11` | kind=`constant` confidence=`0.8681`

#### Field Hypotheses

- bytes `11`..`11` | type=`constant` confidence=`0.99`
- bytes `10`..`10` | type=`keyword` confidence=`0.9895`
- bytes `0`..`0` | type=`keyword` confidence=`0.9833`
- bytes `1`..`1` | type=`keyword` confidence=`0.9521`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`0.9968`
- bytes `11`..`11` | label=`constant` confidence=`0.99`
- bytes `10`..`10` | label=`keyword` confidence=`0.9895`
- bytes `0`..`0` | label=`keyword` confidence=`0.9833`
- bytes `1`..`1` | label=`keyword` confidence=`0.9521`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.
- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.
- Echoes request fields from family_7 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `5343` (`1.0`)
- Repeated n-gram instances: `5389`
- Top motifs: `0000`x10708, `000000`x5365, `000005`x5221, `000501`x5221, `010402`x5221

### family_13

- Role: `response`
- Messages: `3331`
- Template: `?? ?? 00 00 00 05 01 03 02 00 ??`
- Related families: `family_10`, `family_11`, `family_12`, `family_14`, `family_8`, `noise`
- Role hint: `response`
- Semantic confidence: `0.5229`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.40401` max=`2.732159` mean=`2.724919`
- Candidate keyword offset: `10` cardinality=`8` entropy=`2.8615`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7163`
- bytes `1`..`1` | kind=`variable` confidence=`0.6688`
- bytes `2`..`9` | kind=`constant` confidence=`0.6333`
- bytes `10`..`10` | kind=`variable` confidence=`0.7565`

#### Field Hypotheses

- bytes `10`..`10` | type=`keyword` confidence=`0.9976`
- bytes `0`..`0` | type=`keyword` confidence=`0.991`
- bytes `2`..`9` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9231`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`keyword` confidence=`0.9976`
- bytes `0`..`0` | label=`keyword` confidence=`0.991`
- bytes `2`..`9` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9231`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.
- Echoes request fields from family_8 with up to 20 strong offset matches.
- Response size is tied to request fields from family_8.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `3331` (`1.0`)
- Repeated n-gram instances: `3356`
- Top motifs: `0000`x6669, `0200`x3342, `000000`x3338, `000005`x3331, `000501`x3331

### family_4

- Role: `response`
- Messages: `1198`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_12`, `family_14`
- Role hint: `response`
- Semantic confidence: `0.517`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.594907` max=`3.027169` mean=`3.014724`
- Candidate keyword offset: `10` cardinality=`8` entropy=`2.4662`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7379`
- bytes `1`..`1` | kind=`variable` confidence=`0.7189`
- bytes `2`..`9` | kind=`variable` confidence=`0.4318`
- bytes `10`..`10` | kind=`variable` confidence=`0.7669`

#### Field Hypotheses

- bytes `10`..`10` | type=`keyword` confidence=`0.9933`
- bytes `0`..`0` | type=`keyword` confidence=`0.9866`
- bytes `1`..`1` | type=`blob` confidence=`0.5`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`keyword` confidence=`0.9933`
- bytes `0`..`0` | label=`keyword` confidence=`0.9866`
- bytes `1`..`1` | label=`blob` confidence=`0.5`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_14 with up to 20 strong offset matches.
- Response size is tied to request fields from family_14.

#### Feature Summary

- Messages with repetition: `1198` (`1.0`)
- Repeated n-gram instances: `1200`
- Top motifs: `0000`x2397, `000000`x1199, `000005`x1198, `000501`x1198, `010402`x1198

### family_1

- Role: `response`
- Messages: `888`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_12`, `family_5`, `family_6`, `family_7`
- Role hint: `response`
- Semantic confidence: `0.5916`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.732159` max=`3.027169` mean=`3.023151`
- Candidate keyword offset: `10` cardinality=`10` entropy=`2.0379`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7402`
- bytes `1`..`1` | kind=`variable` confidence=`0.7454`
- bytes `2`..`9` | kind=`variable` confidence=`0.4319`
- bytes `10`..`10` | kind=`variable` confidence=`0.7782`

#### Field Hypotheses

- bytes `10`..`10` | type=`keyword` confidence=`0.9887`
- bytes `0`..`0` | type=`keyword` confidence=`0.9809`
- bytes `1`..`1` | type=`blob` confidence=`0.5`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`keyword` confidence=`0.9887`
- bytes `0`..`0` | label=`keyword` confidence=`0.9809`
- bytes `1`..`1` | label=`blob` confidence=`0.5`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_12 with up to 20 strong offset matches.
- Response size is tied to request fields from family_12.

#### Feature Summary

- Messages with repetition: `888` (`1.0`)
- Repeated n-gram instances: `890`
- Top motifs: `0000`x1777, `000000`x889, `000005`x888, `000501`x888, `010402`x888

### family_10

- Role: `request`
- Messages: `858`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_0`, `family_12`, `family_13`, `family_14`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5138`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.284159` max=`2.450826` mean=`2.448301`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7333`
- bytes `1`..`1` | kind=`variable` confidence=`0.7476`
- bytes `2`..`11` | kind=`constant` confidence=`0.6358`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9767`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9767`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_13 with up to 20 strong offset matches.
- Response size is tied to request fields from family_13.
- Echoes request fields from family_14 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `858` (`1.0`)
- Repeated n-gram instances: `864`
- Top motifs: `0000`x1716, `2300`x864, `000000`x858, `000006`x858, `000601`x858

### family_8

- Role: `request`
- Messages: `854`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_13`, `noise`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.284159` max=`2.450826` mean=`2.448094`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.734`
- bytes `1`..`1` | kind=`variable` confidence=`0.7479`
- bytes `2`..`11` | kind=`constant` confidence=`0.6358`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9789`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9789`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Feature Summary

- Messages with repetition: `854` (`1.0`)
- Repeated n-gram instances: `859`
- Top motifs: `0000`x1708, `2300`x859, `000000`x854, `000006`x854, `000601`x854

### family_9

- Role: `request`
- Messages: `809`
- Template: `?? ?? 00 00 00 06 01 01 00 19 00 01`
- Related families: `family_14`
- Role hint: `request`
- Semantic confidence: `1.0`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.825011` max=`2.221252` mean=`2.217672`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7352`
- bytes `1`..`1` | kind=`variable` confidence=`0.7543`
- bytes `2`..`11` | kind=`constant` confidence=`0.6548`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9778`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9778`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Feature Summary

- Messages with repetition: `809` (`1.0`)
- Repeated n-gram instances: `811`
- Top motifs: `0000`x1618, `1900`x811, `000000`x809, `000006`x809, `000601`x809

### family_11

- Role: `request`
- Messages: `761`
- Template: `?? ?? 00 00 00 06 01 01 00 19 00 01`
- Related families: `family_0`, `family_12`, `family_13`
- Role hint: `request`
- Semantic confidence: `0.7625`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.221252` mean=`2.219719`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7372`
- bytes `1`..`1` | kind=`variable` confidence=`0.7605`
- bytes `2`..`11` | kind=`constant` confidence=`0.6548`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9763`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9763`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_13 with up to 20 strong offset matches.
- Response size is tied to request fields from family_13.

#### Feature Summary

- Messages with repetition: `761` (`1.0`)
- Repeated n-gram instances: `764`
- Top motifs: `0000`x1522, `1900`x764, `000000`x761, `000006`x761, `000601`x761

### family_5

- Role: `request`
- Messages: `692`
- Template: `?? ?? 00 00 00 06 01 03 00 23 00 01`
- Related families: `family_1`, `family_12`, `family_7`, `noise`
- Role hint: `request`
- Semantic confidence: `0.5282`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.284159` max=`2.450826` mean=`2.44914`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.74`
- bytes `1`..`1` | kind=`variable` confidence=`0.7723`
- bytes `2`..`11` | kind=`constant` confidence=`0.6358`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9769`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9769`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from family_12 with up to 20 strong offset matches.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `692` (`1.0`)
- Repeated n-gram instances: `694`
- Top motifs: `0000`x1384, `2300`x694, `000000`x692, `000006`x692, `000601`x692

### family_2

- Role: `response`
- Messages: `645`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ??`
- Related families: `family_7`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.023786`
- Candidate keyword offset: `10` cardinality=`3` entropy=`1.3759`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7506`
- bytes `1`..`1` | kind=`variable` confidence=`0.7813`
- bytes `2`..`9` | kind=`constant` confidence=`0.6115`
- bytes `10`..`10` | kind=`variable` confidence=`0.7907`

#### Field Hypotheses

- bytes `10`..`10` | type=`keyword` confidence=`0.9953`
- bytes `2`..`9` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9829`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `10`..`10` | label=`keyword` confidence=`0.9953`
- bytes `2`..`9` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9829`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_7 with up to 20 strong offset matches.
- Response size is tied to request fields from family_7.

#### Feature Summary

- Messages with repetition: `645` (`1.0`)
- Repeated n-gram instances: `645`
- Top motifs: `0000`x1290, `000000`x645, `000005`x645, `000501`x645, `010402`x645

### family_6

- Role: `request`
- Messages: `644`
- Template: `?? ?? 00 00 00 06 01 01 00 19 00 01`
- Related families: `family_1`, `family_7`, `noise`
- Role hint: `request`
- Semantic confidence: `0.8552`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.221252` mean=`2.21944`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7435`
- bytes `1`..`1` | kind=`variable` confidence=`0.7799`
- bytes `2`..`11` | kind=`constant` confidence=`0.6548`

#### Field Hypotheses

- bytes `2`..`11` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9767`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `2`..`11` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.9767`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from noise with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `644` (`1.0`)
- Repeated n-gram instances: `647`
- Top motifs: `0000`x1288, `1900`x647, `000000`x644, `000006`x644, `000601`x644

### family_3

- Role: `response`
- Messages: `109`
- Template: `?? ?? 00 00 00 05 01 04 02 2d 11`
- Related families: `family_7`
- Role hint: `response`
- Semantic confidence: `1.0`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.845351` max=`3.027169` mean=`3.023833`
- Candidate keyword offset: `4` cardinality=`1` entropy=`-0.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7818`
- bytes `1`..`1` | kind=`variable` confidence=`0.8543`
- bytes `2`..`10` | kind=`constant` confidence=`0.601`

#### Field Hypotheses

- bytes `2`..`10` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.945`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`10` | label=`constant` confidence=`0.99`
- bytes `0`..`0` | label=`keyword` confidence=`0.945`
- bytes `1`..`1` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_7 with up to 20 strong offset matches.
- Response size is tied to request fields from family_7.

#### Feature Summary

- Messages with repetition: `109` (`1.0`)
- Repeated n-gram instances: `109`
- Top motifs: `0000`x218, `000000`x109, `000005`x109, `000501`x109, `010402`x109
