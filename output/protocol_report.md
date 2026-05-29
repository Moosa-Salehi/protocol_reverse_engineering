# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: D:\tez\practical\protocol_re\data\05_families.json
- **source_feature_summary**: D:\tez\practical\protocol_re\data\03_family_features.json
- **source_keyword_summary**: D:\tez\practical\protocol_re\data\07_keywords.json
- **source_framing_summary**: D:\tez\practical\protocol_re\data\04_framing.json
- **source_relations_summary**: D:\tez\practical\protocol_re\data\08_relations.json
- **source_semantics_summary**: D:\tez\practical\protocol_re\data\09_semantics.json
- **framing_global_summary**: {'common_header_ends': [{'header_end': 12, 'family_count': 1, 'family_ratio': 0.5}, {'header_end': 6, 'family_count': 1, 'family_ratio': 0.5}], 'field_type_counts': {'length': 7, 'discriminator': 4, 'constant': 3, 'transaction_or_counter': 2}, 'mean_best_confidence': 1.0, 'families_with_header_candidate': 2}
- **notes**: Initial auto-generated protocol model assembled from family summaries.

## Evaluation

- Messages: `200000` across `45340` sessions
- Corpus assignment coverage: `1` with `2` families
- Clustering sample: `100000` messages ratio=`0.5`
- Parseable families: `2` of `2`
- Pair hypotheses: `154658` direction_unknown_ratio=`0`
- Relation edges: `1` echo_edges=`1` length_relation_edges=`1`
- Semantic coverage: `2` of `2` families ratio=`1`
- Top semantic labels: `keyword`x12, `constant`x4, `echoed_request_field`x3, `length`x2, `blob`x2, `response_size_selector`x2, `transaction_or_correlation_id`x1
- Framing coverage: `2` of `2` families ratio=`1`
- Clustering diagnostics: warning_families=`2` split_candidates=`0` merge_candidates=`0`

### Clustering Diagnostic Warnings

- `family_0` | messages=`199715` split=`0.3` under_split=`0.3` over_split=`0` warnings=mixed directions, mixed length profile
- `noise` | messages=`285` split=`0` under_split=`0` over_split=`0` warnings=noise family

### Evaluation Top Relation Edges

- `noise` -> `noise` | pairs=`24` avg_score=`6.3675` support=`0.15` lift=`84.6668` direction=`0.9167` order=`1` echo_fields=`20` length_rules=`12`

## Final Ground Truth Evaluation

- Overall score: `0.1587`
- Verdict: `fail`
- Matched message types: `2` of `11`
- Message type matching: accuracy=`0.1818` precision=`1` recall=`0.1818` f1=`0.3077`
- Field boundary: accuracy=`0.1957` precision=`0.45` recall=`0.2571` f1=`0.3273`
- Field semantics: accuracy=`0` precision=`0` recall=`0` f1=`0`
- Relations: accuracy=`0` precision=`0` recall=`0` f1=`0`

## LLM Analysis

- Prompt size: `54253` bytes, `54253` characters, estimated tokens=`13564`

_LLM analysis was skipped because stage 15 ran in render-only mode._

## Family Relations

- Total inferred family edges: `1`
- Strongest edges:
- `noise` -> `noise` | pairs=`24` avg_score=`6.3675` support=`0.15` lift=`84.6668` direction=`0.9167` order=`1` flow=`client_to_server->server_to_client` echo_fields=`20` length_rules=`12`

## Families

- Total families: `2`
- Families shown below: `2`

### family_0

- Role: `unknown`
- Messages: `199715`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01 00 04 00 00 00 06 01 01 00 0e 00 01`
- Semantic confidence: `0.0`
- Length stats: min=`10` max=`24` distinct=`4`
- Entropy summary: min=`1.360964` max=`3.027169` mean=`2.379326`
- Candidate discriminator offset: `8` cardinality=`3` entropy=`1.475727` salience=`0.990509` mutual_information=`0.001176` contrastive_separation=`0.796875` confidence=`0.644812`
- Top discriminator candidates: offset `8` conf=`0.644812` salience=`0.990509`, offset `7` conf=`0.54244` salience=`0.992903`, offset `9` conf=`0.487483` salience=`0.995831`
- Framing hypothesis: header=`0`..`11` body_start=`12` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6626`
- bytes `1`..`1` | kind=`variable` confidence=`0.6405`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7868`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7745`
- bytes `8`..`8` | kind=`variable` confidence=`0.7868`
- bytes `9`..`9` | kind=`variable` confidence=`0.7593`
- bytes `10`..`10` | kind=`variable` confidence=`0.7383`
- bytes `11`..`11` | kind=`variable` confidence=`0.85`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`1.0`
- bytes `8`..`8` | type=`keyword` confidence=`1.0`
- bytes `9`..`9` | type=`keyword` confidence=`0.9999`
- bytes `11`..`11` | type=`keyword` confidence=`0.9999`
- bytes `0`..`0` | type=`keyword` confidence=`0.9993`
- bytes `10`..`10` | type=`keyword` confidence=`0.9993`
- bytes `1`..`1` | type=`keyword` confidence=`0.9987`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Framing Hypotheses

- header_end=`12` body_start=`12` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`13` body_start=`13` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant
- header_end=`18` body_start=`18` confidence=`1.0` fields=`2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length, `5`..`5` discriminator, `6`..`6` constant

#### Semantic Labels

- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9999`
- bytes `11`..`11` | label=`keyword` confidence=`0.9999`
- bytes `0`..`0` | label=`keyword` confidence=`0.9993`
- bytes `10`..`10` | label=`keyword` confidence=`0.9993`
- bytes `1`..`1` | label=`keyword` confidence=`0.9987`
- bytes `2`..`4` | label=`constant` confidence=`0.99`
- bytes `6`..`6` | label=`constant` confidence=`0.99`

#### Feature Summary

- Messages with repetition: `199715` (`1.0`)
- Repeated n-gram instances: `246225`
- Top motifs: `0000`x403905, `000000`x200460, `0101`x118566, `0006`x102860, `0601`x101745

### noise

- Role: `unknown`
- Messages: `285`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? ??`
- Related families: `noise`
- Role hint: `unknown`
- Semantic confidence: `0.5`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.896241` max=`3.027169` mean=`2.783042`
- Candidate discriminator offset: `8` cardinality=`2` entropy=`0.798524` salience=`0.990509` mutual_information=`0.001176` contrastive_separation=`0.78125` confidence=`0.619456`
- Top discriminator candidates: offset `8` conf=`0.619456` salience=`0.990509`, offset `9` conf=`0.527122` salience=`0.995831`, offset `10` conf=`0.268782` salience=`0.23055`
- Framing hypothesis: header=`0`..`5` body_start=`6` confidence=`1.0`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7846`
- bytes `1`..`1` | kind=`variable` confidence=`0.8033`
- bytes `2`..`5` | kind=`variable` confidence=`0.85`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7939`
- bytes `8`..`8` | kind=`variable` confidence=`0.8046`
- bytes `9`..`9` | kind=`variable` confidence=`0.7852`
- bytes `10`..`10` | kind=`variable` confidence=`0.7815`
- bytes `11`..`11` | kind=`variable` confidence=`0.7362`

#### Field Hypotheses

- bytes `2`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.993`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `11`..`11` | type=`keyword` confidence=`0.986`
- bytes `7`..`7` | type=`keyword` confidence=`0.9825`
- bytes `9`..`9` | type=`keyword` confidence=`0.9474`
- bytes `10`..`10` | type=`keyword` confidence=`0.8526`
- bytes `0`..`0` | type=`blob` confidence=`0.5`
- bytes `1`..`1` | type=`blob` confidence=`0.5`

#### Framing Hypotheses

- header_end=`6` body_start=`6` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`7` body_start=`7` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length
- header_end=`8` body_start=`8` confidence=`1.0` fields=`0`..`1` transaction_or_counter, `0`..`3` transaction_or_counter, `2`..`4` constant, `2`..`5` length, `4`..`5` length, `5`..`5` length

#### Semantic Labels

- bytes `2`..`5` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`0.993`
- bytes `6`..`6` | label=`constant` confidence=`0.99`
- bytes `11`..`11` | label=`keyword` confidence=`0.986`
- bytes `7`..`7` | label=`keyword` confidence=`0.9825`
- bytes `2`..`5` | label=`response_size_selector` confidence=`0.9583`
- bytes `8`..`8` | label=`echoed_request_field` confidence=`0.9583`
- bytes `8`..`8` | label=`response_size_selector` confidence=`0.9583`

#### Notes

- Echoes request fields from noise with up to 20 strong offset matches.
- Response size is tied to request fields from noise.

#### Feature Summary

- Messages with repetition: `285` (`1.0`)
- Repeated n-gram instances: `360`
- Top motifs: `0000`x604, `000000`x319, `000005`x216, `000501`x216, `0005`x216
