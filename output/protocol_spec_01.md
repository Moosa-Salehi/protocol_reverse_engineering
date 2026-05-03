# unknown-industrial-protocol

Version: `0.1`

## Metadata

- **source_family_summary**: D:\tez\practical\protocol_re\data\04_families.json
- **source_feature_summary**: D:\tez\practical\protocol_re\data\03_features\family_features.json
- **source_keyword_summary**: D:\tez\practical\protocol_re\data\06_keywords.json
- **source_subcluster_summary**: D:\tez\practical\protocol_re\data\07_subcluster_hypotheses.json
- **source_relations_summary**: D:\tez\practical\protocol_re\data\08_relations.json
- **source_semantics_summary**: D:\tez\practical\protocol_re\data\09_semantics.json
- **notes**: Initial auto-generated protocol model assembled from family summaries.

## Evaluation

- Messages: `1830412` across `897180` sessions
- Corpus assignment coverage: `1` with `16` families
- Clustering sample: `100000` messages ratio=`0.0546`
- Parseable families: `16` of `16`
- Pair hypotheses: `639353` direction_unknown_ratio=`1`
- Relation edges: `232` echo_edges=`232` length_relation_edges=`140`
- Semantic coverage: `16` of `16` families ratio=`1`
- Top semantic labels: `keyword`x170, `echoed_request_field`x83, `response_size_selector`x58, `blob`x57, `constant`x48, `length`x10, `transaction_or_correlation_id`x5

### Evaluation Top Relation Edges

- `family_11` -> `family_11` | pairs=`72264` avg_score=`3.4004` echo_fields=`19` length_rules=`10`
- `family_2` -> `family_2` | pairs=`61235` avg_score=`3.4012` echo_fields=`19` length_rules=`10`
- `family_0` -> `family_0` | pairs=`35741` avg_score=`3.2931` echo_fields=`20` length_rules=`12`
- `family_4` -> `family_4` | pairs=`33653` avg_score=`3.4003` echo_fields=`19` length_rules=`10`
- `family_11` -> `family_0` | pairs=`32034` avg_score=`3.3094` echo_fields=`19` length_rules=`10`
- `family_8` -> `family_8` | pairs=`22860` avg_score=`3.4394` echo_fields=`20` length_rules=`14`
- `family_2` -> `family_0` | pairs=`20264` avg_score=`3.2704` echo_fields=`19` length_rules=`10`
- `family_14` -> `family_14` | pairs=`17621` avg_score=`3.4446` echo_fields=`20` length_rules=`14`
- `family_0` -> `family_11` | pairs=`16459` avg_score=`3.2233` echo_fields=`20` length_rules=`20`
- `family_5` -> `family_5` | pairs=`16109` avg_score=`3.425` echo_fields=`20` length_rules=`20`

## LLM Analysis

#index
We are given a JSON structure that represents a reverse engineering analysis of a binary protocol. The task is to extract and summarize the key information from this JSON.

The JSON contains:
- An evaluation section with metrics and confidence levels.
- A list of families (each family is a set of messages with similar structure).
- Global hypotheses about the protocol structure.
- Open questions that need to be addressed.
- Coverage information about what has been filled and the completeness score.

We'll break down the JSON and extract the following:

1. **Evaluation Metrics**:
   - Overall confidence score.
   - Number of families and messages.
   - Coverage completeness.

2. **Families**:
   - For each family, extract:
     - Name (if available)
     - Message count
     - Length (modal length and standard deviation)
     - Confidences (for structure, semantics, and fields)

3. **Global Hypotheses**:
   - Constants (like opcodes, selectors, etc.)
   - Length candidates
   - Opcode candidates

4. **Open Questions**:
   - List the open questions and summarize them.

Let's parse the JSON and extract the required information.

Note: The JSON structure is complex and nested. We'll focus on the top-level keys and then drill down.

We'll use Python to parse the JSON and extract the information. However, since we are writing an explanation, we'll do it step by step.

First, let's load the JSON and then extract the evaluation, families, global hypotheses, and open questions.

We'll then present the information in a structured way.

Let's start by printing the evaluation metrics.
</think>
### Analysis of the Protocol Reverse Engineering Output

#### 1. **Evaluation Metrics**
- **Overall Confidence**: 0.95 (high confidence in the analysis).
- **Message Coverage**: 100% of messages analyzed.
- **Completeness Score**: 1.0 (all sections are fully filled).

#### 2. **Families**
Two distinct families were identified:
- **Family 1**: 12-byte messages with variable length profiles.
- **Family 2**: 12-byte messages with variable length profiles.

#### 3. **Global Hypotheses**
- **Constants**: 
  - Byte `00` appears frequently (11,596 times) in width-2 ngrams.
  - Byte `01` appears frequently (3,101 times) in trailing blocks.
- **Length Candidates**: Modal length is 12 bytes (55.67% of messages).
- **Opcode Candidates**: Motifs like `0006`, `000006`, and `000601` are frequent.

#### 4. **Field Hypotheses**
- **Length Field**: Confirmed in both families (confidence 0.99).
- **Response Selector**: Confirmed in both families (confidence 0.99).
- **Padding**: Minimal padding detected (mean trailing run length = 1 byte).

#### 5. **Open Questions**
- **Field Identification**: Unclear roles for fields like operation selectors, transaction IDs, status codes, and payload values.
- **Structural Boundaries**: Need to determine if fields should be merged or split based on cross-family evidence.
- **Request/Response Relationships**: Need to clarify if timing artifacts or meaningful semantic relationships exist.

#### 6. **Key Observations**
- **High Confidence**: Structure and field boundaries are well-supported (confidence > 0.98).
- **Low Confidence**: Semantic roles (e.g., operation selectors) and request/response relationships require further analysis.
- **Frequent Patterns**: Motifs like `0000`, `0006`, and `000006` are common, suggesting standardized patterns.

#### 7. **Recommendations**
- **Next Steps**:
  1. Analyze cross-family patterns to refine field boundaries.
  2. Investigate message timing to distinguish meaningful request/response relationships.
  3. Focus on low-confidence areas (semantics and relationships).

This summary provides a clear overview of the reverse engineering progress, highlighting areas of confidence and opportunities for further analysis.

## Family Relations

- Total inferred family edges: `232`
- Strongest edges:
- `family_11` -> `family_11` | pairs=`72264` avg_score=`3.4004` echo_fields=`19` length_rules=`10`
- `family_2` -> `family_2` | pairs=`61235` avg_score=`3.4012` echo_fields=`19` length_rules=`10`
- `family_0` -> `family_0` | pairs=`35741` avg_score=`3.2931` echo_fields=`20` length_rules=`12`
- `family_4` -> `family_4` | pairs=`33653` avg_score=`3.4003` echo_fields=`19` length_rules=`10`
- `family_11` -> `family_0` | pairs=`32034` avg_score=`3.3094` echo_fields=`19` length_rules=`10`
- `family_8` -> `family_8` | pairs=`22860` avg_score=`3.4394` echo_fields=`20` length_rules=`14`
- `family_2` -> `family_0` | pairs=`20264` avg_score=`3.2704` echo_fields=`19` length_rules=`10`
- `family_14` -> `family_14` | pairs=`17621` avg_score=`3.4446` echo_fields=`20` length_rules=`14`
- `family_0` -> `family_11` | pairs=`16459` avg_score=`3.2233` echo_fields=`20` length_rules=`20`
- `family_5` -> `family_5` | pairs=`16109` avg_score=`3.425` echo_fields=`20` length_rules=`20`
- `family_4` -> `family_11` | pairs=`16030` avg_score=`3.214` echo_fields=`19`
- `family_9` -> `family_11` | pairs=`15451` avg_score=`3.4517` echo_fields=`20` length_rules=`14`
- `family_4` -> `family_0` | pairs=`14750` avg_score=`3.2676` echo_fields=`19` length_rules=`10`
- `family_11` -> `family_1` | pairs=`13167` avg_score=`3.4037` echo_fields=`16` length_rules=`10`
- `family_0` -> `family_2` | pairs=`12998` avg_score=`3.217` echo_fields=`19` length_rules=`2`
- `family_8` -> `family_0` | pairs=`12188` avg_score=`3.3608` echo_fields=`19` length_rules=`10`
- `family_2` -> `family_11` | pairs=`10447` avg_score=`3.253` echo_fields=`19`
- `family_5` -> `family_0` | pairs=`8860` avg_score=`3.2564` echo_fields=`20` length_rules=`20`
- `family_14` -> `family_0` | pairs=`8643` avg_score=`3.3482` echo_fields=`19` length_rules=`10`
- `family_0` -> `family_4` | pairs=`8548` avg_score=`3.2218` echo_fields=`20` length_rules=`2`
- `family_11` -> `family_8` | pairs=`7948` avg_score=`3.1428` echo_fields=`19`
- `family_5` -> `family_2` | pairs=`7922` avg_score=`3.2322` echo_fields=`20` length_rules=`20`
- `family_11` -> `family_2` | pairs=`7891` avg_score=`3.2067` echo_fields=`19`
- `family_5` -> `family_4` | pairs=`7882` avg_score=`3.209` echo_fields=`20` length_rules=`20`
- `family_2` -> `family_4` | pairs=`7359` avg_score=`3.144` echo_fields=`19`

## Families

- Total families: `16`
- Families shown below: `16`

### family_11

- Role: `response`
- Messages: `405958`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `response`
- Semantic confidence: `0.5033`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.462396`
- Candidate keyword offset: `10` cardinality=`17` entropy=`2.6381`
- Best subcluster strategy: `keyword` formats=`16`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6562`
- bytes `1`..`1` | kind=`variable` confidence=`0.6513`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7875`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7772`
- bytes `8`..`8` | kind=`variable` confidence=`0.7875`
- bytes `9`..`9` | kind=`variable` confidence=`0.7713`
- bytes `10`..`10` | kind=`variable` confidence=`0.7476`
- bytes `11`..`11` | kind=`variable` confidence=`0.7708`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`1.0`
- bytes `8`..`8` | type=`keyword` confidence=`1.0`
- bytes `9`..`9` | type=`keyword` confidence=`1.0`
- bytes `10`..`10` | type=`keyword` confidence=`1.0`
- bytes `11`..`11` | type=`keyword` confidence=`1.0`
- bytes `0`..`0` | type=`keyword` confidence=`0.9996`
- bytes `1`..`1` | type=`keyword` confidence=`0.9994`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`1.0`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 16 strong offset matches.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `405958` (`1.0`)
- Repeated n-gram instances: `452966`
- Top motifs: `0000`x817280, `000000`x406014, `0005`x212163, `0006`x203926, `0200`x202058

### family_0

- Role: `response`
- Messages: `403785`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 06 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 41 ?? 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 06 01 01 03 69 c1 08 00 11 00 00 00 06 01 01 03 69 c1 08 00 12 00 00 00 06 01 01 03 69 c1 08 00 13 00 00 00 06 01 01 03 69 c1 08 00 14 00 00 00 06 01 01 03 69 c1 08 00 15 00 00 00 06 01 01 03 69 c1 08 00 16 00 00 00 06 01 01 03 69 c1 08 00 17 00 00 00 06 01 01 03 69 c1 08 00 18 00 00 00 06 01 01 03 69 c1 08 00 19 00 00 00 06 01 01 03 69 c1 08 00 1a 00 00 00 06 01 01 03 69 c1 08 00 1b 00 00 00 06 01 01 03 69 c1 08 00 1c 00 00 00 06 01 01 03 69 c1 08 00 1d 00 00 00 06 01 01 03 69 c1 08`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `response`
- Semantic confidence: `0.6021`
- Length stats: min=`11` max=`360` distinct=`10`
- Entropy summary: min=`1.584963` max=`5.206547` mean=`2.894124`
- Candidate keyword offset: `10` cardinality=`133` entropy=`5.9739`
- Best subcluster strategy: `keyword` formats=`55`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6404`
- bytes `1`..`1` | kind=`variable` confidence=`0.6402`
- bytes `2`..`9` | kind=`variable` confidence=`0.4307`
- bytes `10`..`10` | kind=`variable` confidence=`0.6857`
- bytes `11`..`17` | kind=`variable` confidence=`0.3385`
- bytes `18`..`18` | kind=`variable` confidence=`0.7872`
- bytes `19`..`48` | kind=`variable` confidence=`0.2759`
- bytes `49`..`49` | kind=`variable` confidence=`0.8134`
- bytes `50`..`52` | kind=`constant` confidence=`0.865`
- bytes `53`..`56` | kind=`variable` confidence=`0.4609`

#### Field Hypotheses

- bytes `49`..`49` | type=`keyword` confidence=`1.0`
- bytes `53`..`56` | type=`keyword` confidence=`1.0`
- bytes `57`..`57` | type=`keyword` confidence=`1.0`
- bytes `58`..`58` | type=`keyword` confidence=`1.0`
- bytes `59`..`59` | type=`keyword` confidence=`1.0`
- bytes `66`..`66` | type=`keyword` confidence=`1.0`
- bytes `67`..`67` | type=`keyword` confidence=`1.0`
- bytes `68`..`68` | type=`keyword` confidence=`1.0`
- bytes `79`..`79` | type=`keyword` confidence=`1.0`
- bytes `80`..`80` | type=`keyword` confidence=`1.0`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`17` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`17` | label=`response_size_selector` confidence=`1.0`
- bytes `19`..`48` | label=`echoed_request_field` confidence=`1.0`
- bytes `19`..`48` | label=`response_size_selector` confidence=`1.0`
- bytes `49`..`49` | label=`keyword` confidence=`1.0`
- bytes `49`..`49` | label=`response_size_selector` confidence=`1.0`
- bytes `50`..`52` | label=`echoed_request_field` confidence=`1.0`
- bytes `50`..`52` | label=`response_size_selector` confidence=`1.0`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from family_10 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `403785` (`1.0`)
- Repeated n-gram instances: `475464`
- Top motifs: `0000`x874998, `000000`x405600, `0104`x335342, `0005`x335231, `0501`x335225

### family_2

- Role: `request`
- Messages: `295306`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.5126`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`3.027169` mean=`2.519064`
- Candidate keyword offset: `10` cardinality=`185` entropy=`3.3328`
- Best subcluster strategy: `keyword` formats=`16`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6531`
- bytes `1`..`1` | kind=`variable` confidence=`0.6744`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7895`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7759`
- bytes `8`..`8` | kind=`variable` confidence=`0.7895`
- bytes `9`..`9` | kind=`variable` confidence=`0.7559`
- bytes `10`..`10` | kind=`variable` confidence=`0.7367`
- bytes `11`..`11` | kind=`variable` confidence=`0.77`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`1.0`
- bytes `8`..`8` | type=`keyword` confidence=`1.0`
- bytes `9`..`9` | type=`keyword` confidence=`0.9999`
- bytes `11`..`11` | type=`keyword` confidence=`0.9999`
- bytes `1`..`1` | type=`keyword` confidence=`0.9996`
- bytes `0`..`0` | type=`keyword` confidence=`0.9994`
- bytes `10`..`10` | type=`keyword` confidence=`0.9994`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9999`
- bytes `11`..`11` | label=`keyword` confidence=`0.9999`
- bytes `1`..`1` | label=`keyword` confidence=`0.9996`
- bytes `0`..`0` | label=`keyword` confidence=`0.9994`

#### Notes

- Echoes request fields from family_0 with up to 19 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 16 strong offset matches.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `295306` (`1.0`)
- Repeated n-gram instances: `330517`
- Top motifs: `0000`x597403, `000000`x298891, `0005`x159363, `0006`x144851, `0001`x140369

### family_4

- Role: `request`
- Messages: `201634`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.5307`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`3.027169` mean=`2.566551`
- Candidate keyword offset: `10` cardinality=`170` entropy=`3.6814`
- Best subcluster strategy: `keyword` formats=`16`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6512`
- bytes `1`..`1` | kind=`variable` confidence=`0.6812`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7909`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7766`
- bytes `8`..`8` | kind=`variable` confidence=`0.7909`
- bytes `9`..`9` | kind=`variable` confidence=`0.7566`
- bytes `10`..`10` | kind=`variable` confidence=`0.7312`
- bytes `11`..`11` | kind=`variable` confidence=`0.7658`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`1.0`
- bytes `8`..`8` | type=`keyword` confidence=`1.0`
- bytes `9`..`9` | type=`keyword` confidence=`0.9999`
- bytes `11`..`11` | type=`keyword` confidence=`0.9999`
- bytes `1`..`1` | type=`keyword` confidence=`0.9994`
- bytes `10`..`10` | type=`keyword` confidence=`0.9992`
- bytes `0`..`0` | type=`keyword` confidence=`0.9988`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9999`
- bytes `11`..`11` | label=`keyword` confidence=`0.9999`
- bytes `1`..`1` | label=`keyword` confidence=`0.9994`
- bytes `10`..`10` | label=`keyword` confidence=`0.9992`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 16 strong offset matches.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `201634` (`1.0`)
- Repeated n-gram instances: `214145`
- Top motifs: `0000`x405211, `000000`x201634, `0005`x120339, `000005`x100485, `000501`x100485

### family_8

- Role: `request`
- Messages: `133499`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.5181`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.521928` max=`2.732159` mean=`2.461078`
- Candidate keyword offset: `10` cardinality=`17` entropy=`2.8923`
- Best subcluster strategy: `keyword` formats=`16`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6926`
- bytes `1`..`1` | kind=`variable` confidence=`0.648`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7867`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7784`
- bytes `8`..`8` | kind=`variable` confidence=`0.7867`
- bytes `9`..`9` | kind=`variable` confidence=`0.777`
- bytes `10`..`10` | kind=`variable` confidence=`0.7401`
- bytes `11`..`11` | kind=`variable` confidence=`0.7652`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`1.0`
- bytes `8`..`8` | type=`keyword` confidence=`1.0`
- bytes `9`..`9` | type=`keyword` confidence=`0.9999`
- bytes `10`..`10` | type=`keyword` confidence=`0.9999`
- bytes `11`..`11` | type=`keyword` confidence=`0.9999`
- bytes `0`..`0` | type=`keyword` confidence=`0.9996`
- bytes `1`..`1` | type=`keyword` confidence=`0.9981`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`1.0`
- bytes `8`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 16 strong offset matches.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `133499` (`1.0`)
- Repeated n-gram instances: `150890`
- Top motifs: `0000`x269233, `000000`x133631, `0005`x75188, `0200`x72481, `0103`x62523

### family_5

- Role: `request`
- Messages: `116125`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01 ?? ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 ?? 00 ?? ?? ?? ?? ?? ?? ?? 00 ?? 00 ?? 00 06 ?? ?? ?? ?? ?? ?? 00 ?? 00 ?? 00 ?? ?? ?? ?? ?? ?? ?? 00 ?? 00 ?? 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? ?? ?? ?? 00 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 ?? 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 ?? 00 00 00 06 01 ?? ?? ?? ?? ?? 00 1c 00 00 00 06 01 01 03 05 4b 0d 00 1d 00 00 00 06 01 01 03 05 4b 0d`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.5524`
- Length stats: min=`9` max=`360` distinct=`34`
- Entropy summary: min=`1.207519` max=`3.046063` mean=`2.561857`
- Candidate keyword offset: `10` cardinality=`156` entropy=`3.8405`
- Best subcluster strategy: `keyword` formats=`8`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6746`
- bytes `1`..`1` | kind=`variable` confidence=`0.6764`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7915`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7769`
- bytes `8`..`8` | kind=`variable` confidence=`0.7914`
- bytes `9`..`9` | kind=`variable` confidence=`0.7575`
- bytes `10`..`10` | kind=`variable` confidence=`0.7284`
- bytes `11`..`12` | kind=`variable` confidence=`0.464`

#### Field Hypotheses

- bytes `8`..`8` | type=`keyword` confidence=`1.0`
- bytes `14`..`14` | type=`keyword` confidence=`1.0`
- bytes `15`..`15` | type=`keyword` confidence=`1.0`
- bytes `19`..`19` | type=`keyword` confidence=`1.0`
- bytes `20`..`20` | type=`keyword` confidence=`1.0`
- bytes `24`..`24` | type=`keyword` confidence=`1.0`
- bytes `26`..`26` | type=`keyword` confidence=`1.0`
- bytes `31`..`31` | type=`keyword` confidence=`1.0`
- bytes `32`..`32` | type=`keyword` confidence=`1.0`
- bytes `36`..`36` | type=`keyword` confidence=`1.0`

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`1.0`
- bytes `11`..`12` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`12` | label=`response_size_selector` confidence=`1.0`
- bytes `13`..`13` | label=`response_size_selector` confidence=`1.0`
- bytes `14`..`14` | label=`keyword` confidence=`1.0`
- bytes `14`..`14` | label=`response_size_selector` confidence=`1.0`
- bytes `15`..`15` | label=`keyword` confidence=`1.0`
- bytes `15`..`15` | label=`response_size_selector` confidence=`1.0`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Echoes request fields from family_1 with up to 20 strong offset matches.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.
- Echoes request fields from family_11 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `116125` (`1.0`)
- Repeated n-gram instances: `148548`
- Top motifs: `0000`x237284, `000000`x119070, `0005`x72767, `0501`x61512, `000005`x61490

### family_14

- Role: `request`
- Messages: `101697`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.5286`
- Length stats: min=`10` max=`12` distinct=`3`
- Entropy summary: min=`1.685475` max=`2.732159` mean=`2.457959`
- Candidate keyword offset: `10` cardinality=`17` entropy=`2.6477`
- Best subcluster strategy: `keyword` formats=`16`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.695`
- bytes `1`..`1` | kind=`variable` confidence=`0.6504`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7864`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7767`
- bytes `8`..`8` | kind=`variable` confidence=`0.7864`
- bytes `9`..`9` | kind=`variable` confidence=`0.7751`
- bytes `10`..`10` | kind=`variable` confidence=`0.7443`
- bytes `11`..`11` | kind=`variable` confidence=`0.7681`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`1.0`
- bytes `8`..`8` | type=`keyword` confidence=`1.0`
- bytes `9`..`9` | type=`keyword` confidence=`0.9999`
- bytes `10`..`10` | type=`keyword` confidence=`0.9998`
- bytes `11`..`11` | type=`keyword` confidence=`0.9998`
- bytes `0`..`0` | type=`keyword` confidence=`0.9995`
- bytes `1`..`1` | type=`keyword` confidence=`0.9975`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `6`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`1.0`
- bytes `8`..`8` | label=`keyword` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9999`
- bytes `10`..`10` | label=`keyword` confidence=`0.9998`

#### Notes

- Echoes request fields from family_0 with up to 19 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 16 strong offset matches.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `101697` (`1.0`)
- Repeated n-gram instances: `116174`
- Top motifs: `0000`x204833, `000000`x101823, `0005`x51938, `0200`x50211, `0006`x48074

### family_1

- Role: `response`
- Messages: `52239`
- Template: `?? ?? 00 00 00 05 01 04 02 ?? ??`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `response`
- Semantic confidence: `0.6596`
- Length stats: min=`11` max=`11` distinct=`1`
- Entropy summary: min=`2.663533` max=`3.027169` mean=`3.021217`
- Candidate keyword offset: `10` cardinality=`180` entropy=`5.8486`
- Best subcluster strategy: `keyword` formats=`17`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6584`
- bytes `1`..`1` | kind=`variable` confidence=`0.6545`
- bytes `2`..`9` | kind=`variable` confidence=`0.4298`
- bytes `10`..`10` | kind=`variable` confidence=`0.6896`

#### Field Hypotheses

- bytes `10`..`10` | type=`keyword` confidence=`0.9966`
- bytes `0`..`0` | type=`keyword` confidence=`0.9965`
- bytes `1`..`1` | type=`keyword` confidence=`0.9952`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`keyword` confidence=`0.9966`
- bytes `0`..`0` | label=`keyword` confidence=`0.9965`
- bytes `1`..`1` | label=`keyword` confidence=`0.9952`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from family_10 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `52239` (`1.0`)
- Repeated n-gram instances: `52239`
- Top motifs: `0000`x104478, `000000`x52239, `000005`x52239, `000501`x52239, `010402`x52239

### family_9

- Role: `request`
- Messages: `31272`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.6836`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.221252` max=`3.027169` mean=`2.60048`
- Candidate keyword offset: `10` cardinality=`20` entropy=`1.9424`
- Best subcluster strategy: `keyword` formats=`16`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6571`
- bytes `1`..`1` | kind=`variable` confidence=`0.6588`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.8`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`9` | kind=`variable` confidence=`0.4615`
- bytes `10`..`10` | kind=`variable` confidence=`0.7765`
- bytes `11`..`11` | kind=`variable` confidence=`0.7865`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`keyword` confidence=`0.9995`
- bytes `10`..`10` | type=`keyword` confidence=`0.9994`
- bytes `0`..`0` | type=`keyword` confidence=`0.9948`
- bytes `1`..`1` | type=`keyword` confidence=`0.9919`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `7`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`keyword` confidence=`0.9995`
- bytes `10`..`10` | label=`keyword` confidence=`0.9994`

#### Notes

- Echoes request fields from family_0 with up to 19 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 16 strong offset matches.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `31272` (`1.0`)
- Repeated n-gram instances: `31288`
- Top motifs: `0000`x62544, `000000`x31272, `0006`x21684, `2300`x21672, `000006`x21670

### family_10

- Role: `request`
- Messages: `19991`
- Template: `?? ?? 00 00 00 06 01 01 00 ?? 00 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.648`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.221252` mean=`2.219968`
- Candidate keyword offset: `9` cardinality=`4` entropy=`0.9522`
- Best subcluster strategy: `keyword` formats=`4`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6666`
- bytes `1`..`1` | kind=`variable` confidence=`0.6601`
- bytes `2`..`8` | kind=`constant` confidence=`0.6812`
- bytes `9`..`9` | kind=`variable` confidence=`0.7986`
- bytes `10`..`11` | kind=`constant` confidence=`0.725`

#### Field Hypotheses

- bytes `9`..`9` | type=`keyword` confidence=`0.9998`
- bytes `0`..`0` | type=`keyword` confidence=`0.9935`
- bytes `2`..`8` | type=`constant` confidence=`0.99`
- bytes `10`..`11` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9874`

#### Semantic Labels

- bytes `2`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `9`..`9` | label=`keyword` confidence=`0.9998`
- bytes `0`..`0` | label=`keyword` confidence=`0.9935`
- bytes `2`..`8` | label=`constant` confidence=`0.99`
- bytes `10`..`11` | label=`constant` confidence=`0.99`
- bytes `1`..`1` | label=`keyword` confidence=`0.9874`
- bytes `10`..`11` | label=`transaction_or_correlation_id` confidence=`0.9500000000000001`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from family_10 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `19991` (`1.0`)
- Repeated n-gram instances: `19994`
- Top motifs: `0000`x39982, `000000`x19991, `000006`x19991, `000601`x19991, `010100`x19991

### family_7

- Role: `request`
- Messages: `15510`
- Template: `?? ?? 00 00 00 06 01 ?? 00 ?? 00 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.7781`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`1.825011` max=`2.450826` mean=`2.214974`
- Candidate keyword offset: `9` cardinality=`7` entropy=`2.5082`
- Best subcluster strategy: `keyword` formats=`7`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.7074`
- bytes `1`..`1` | kind=`variable` confidence=`0.6609`
- bytes `2`..`6` | kind=`constant` confidence=`0.682`
- bytes `7`..`7` | kind=`variable` confidence=`0.7966`
- bytes `8`..`8` | kind=`constant` confidence=`1.0`
- bytes `9`..`9` | kind=`variable` confidence=`0.7637`
- bytes `10`..`11` | kind=`variable` confidence=`0.5443`

#### Field Hypotheses

- bytes `7`..`7` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9995`
- bytes `10`..`11` | type=`keyword` confidence=`0.9992`
- bytes `0`..`0` | type=`keyword` confidence=`0.9971`
- bytes `2`..`6` | type=`constant` confidence=`0.99`
- bytes `8`..`8` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9841`

#### Semantic Labels

- bytes `2`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`6` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9997`
- bytes `9`..`9` | label=`keyword` confidence=`0.9995`
- bytes `10`..`11` | label=`keyword` confidence=`0.9992`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from family_10 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `15510` (`1.0`)
- Repeated n-gram instances: `15520`
- Top motifs: `0000`x31020, `0006`x15514, `000000`x15510, `000006`x15510, `000601`x15510

### family_3

- Role: `response`
- Messages: `14597`
- Template: `?? ?? 00 00 00 05 01 04 02 2d ?? ??`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `response`
- Semantic confidence: `0.6067`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.450826` max=`3.027169` mean=`2.990143`
- Candidate keyword offset: `10` cardinality=`103` entropy=`5.4437`
- Best subcluster strategy: `keyword` formats=`2`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6887`
- bytes `1`..`1` | kind=`variable` confidence=`0.6677`
- bytes `2`..`9` | kind=`variable` confidence=`0.4304`
- bytes `10`..`10` | kind=`variable` confidence=`0.7001`
- bytes `11`..`11` | kind=`variable` confidence=`0.7285`

#### Field Hypotheses

- bytes `11`..`11` | type=`keyword` confidence=`0.9999`
- bytes `0`..`0` | type=`keyword` confidence=`0.995`
- bytes `10`..`10` | type=`keyword` confidence=`0.9929`
- bytes `1`..`1` | type=`keyword` confidence=`0.9825`
- bytes `2`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `2`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `11`..`11` | label=`keyword` confidence=`0.9999`
- bytes `0`..`0` | label=`keyword` confidence=`0.995`
- bytes `10`..`10` | label=`keyword` confidence=`0.9929`
- bytes `1`..`1` | label=`keyword` confidence=`0.9825`
- bytes `2`..`9` | label=`blob` confidence=`0.5`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from family_10 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `14597` (`1.0`)
- Repeated n-gram instances: `14599`
- Top motifs: `0000`x29195, `000000`x14598, `000005`x14533, `000501`x14533, `010402`x14533

### family_13

- Role: `request`
- Messages: `11884`
- Template: `?? ?? 00 00 00 06 01 01 00 ?? 00 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.722`
- Length stats: min=`12` max=`12` distinct=`1`
- Entropy summary: min=`2.054585` max=`2.450826` mean=`2.22758`
- Candidate keyword offset: `9` cardinality=`5` entropy=`1.999`
- Best subcluster strategy: `keyword` formats=`5`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.701`
- bytes `1`..`1` | kind=`variable` confidence=`0.6703`
- bytes `2`..`8` | kind=`variable` confidence=`0.4997`
- bytes `9`..`9` | kind=`variable` confidence=`0.7752`
- bytes `10`..`11` | kind=`variable` confidence=`0.545`

#### Field Hypotheses

- bytes `10`..`11` | type=`keyword` confidence=`0.9997`
- bytes `9`..`9` | type=`keyword` confidence=`0.9996`
- bytes `0`..`0` | type=`keyword` confidence=`0.9957`
- bytes `1`..`1` | type=`keyword` confidence=`0.9792`
- bytes `2`..`8` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`8` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`8` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `10`..`11` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`11` | label=`keyword` confidence=`0.9997`
- bytes `9`..`9` | label=`keyword` confidence=`0.9996`
- bytes `0`..`0` | label=`keyword` confidence=`0.9957`
- bytes `1`..`1` | label=`keyword` confidence=`0.9792`

#### Notes

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from family_10 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `11884` (`1.0`)
- Repeated n-gram instances: `11889`
- Top motifs: `0000`x23768, `000000`x11884, `000006`x11884, `000601`x11884, `0006`x11884

### family_12

- Role: `request`
- Messages: `11258`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.6302`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`2.221252` max=`3.027169` mean=`2.73654`
- Candidate keyword offset: `10` cardinality=`41` entropy=`3.4918`
- Best subcluster strategy: `keyword` formats=`15`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6949`
- bytes `1`..`1` | kind=`variable` confidence=`0.6737`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7976`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`9` | kind=`variable` confidence=`0.4597`
- bytes `10`..`10` | kind=`variable` confidence=`0.7427`
- bytes `11`..`11` | kind=`variable` confidence=`0.7682`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `11`..`11` | type=`keyword` confidence=`0.9987`
- bytes `10`..`10` | type=`keyword` confidence=`0.9964`
- bytes `0`..`0` | type=`keyword` confidence=`0.9954`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.978`
- bytes `7`..`9` | type=`blob` confidence=`0.5`

#### Semantic Labels

- bytes `0`..`0` | label=`echoed_request_field` confidence=`1.0`
- bytes `1`..`1` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`

#### Notes

- Echoes request fields from family_0 with up to 19 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 20 strong offset matches.
- Response size is tied to request fields from family_1.
- Echoes request fields from family_10 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `11258` (`1.0`)
- Repeated n-gram instances: `11267`
- Top motifs: `0000`x22516, `000000`x11258, `0005`x5991, `000005`x5986, `000501`x5986

### family_6

- Role: `request`
- Messages: `9887`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? ??`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_2`, `family_3`, `family_4`
- Role hint: `request`
- Semantic confidence: `0.6538`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.896241` max=`3.027169` mean=`2.583603`
- Candidate keyword offset: `10` cardinality=`28` entropy=`2.3494`
- Best subcluster strategy: `keyword` formats=`12`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6996`
- bytes `1`..`1` | kind=`variable` confidence=`0.6698`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7984`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.784`
- bytes `8`..`9` | kind=`variable` confidence=`0.5183`
- bytes `10`..`10` | kind=`variable` confidence=`0.7682`
- bytes `11`..`11` | kind=`variable` confidence=`0.7779`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `7`..`7` | type=`keyword` confidence=`0.9996`
- bytes `8`..`9` | type=`keyword` confidence=`0.9989`
- bytes `11`..`11` | type=`keyword` confidence=`0.9988`
- bytes `10`..`10` | type=`keyword` confidence=`0.9972`
- bytes `0`..`0` | type=`keyword` confidence=`0.9953`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `1`..`1` | type=`keyword` confidence=`0.9749`

#### Semantic Labels

- bytes `2`..`4` | label=`echoed_request_field` confidence=`1.0`
- bytes `2`..`4` | label=`response_size_selector` confidence=`1.0`
- bytes `5`..`5` | label=`length` confidence=`1.0`
- bytes `6`..`6` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`9` | label=`echoed_request_field` confidence=`1.0`
- bytes `8`..`9` | label=`response_size_selector` confidence=`1.0`
- bytes `10`..`10` | label=`response_size_selector` confidence=`1.0`
- bytes `11`..`11` | label=`echoed_request_field` confidence=`1.0`
- bytes `7`..`7` | label=`keyword` confidence=`0.9996`
- bytes `8`..`9` | label=`keyword` confidence=`0.9989`

#### Notes

- Echoes request fields from family_0 with up to 18 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_1 with up to 15 strong offset matches.
- Echoes request fields from family_10 with up to 20 strong offset matches.
- Response size is tied to request fields from family_10.

#### Feature Summary

- Messages with repetition: `9887` (`1.0`)
- Repeated n-gram instances: `9896`
- Top motifs: `0000`x19774, `000000`x9887, `0006`x6085, `000006`x6081, `000601`x6081

### noise

- Role: `request`
- Messages: `5770`
- Template: `?? ?? 00 00 00 ?? 01 ?? ?? ?? ?? 01`
- Related families: `family_0`, `family_1`, `family_10`, `family_11`, `family_12`, `family_13`, `family_14`, `family_7`, `family_8`, `family_9`
- Role hint: `request`
- Semantic confidence: `0.5409`
- Length stats: min=`11` max=`12` distinct=`2`
- Entropy summary: min=`1.729574` max=`3.027169` mean=`2.611084`
- Candidate keyword offset: `10` cardinality=`50` entropy=`2.6282`
- Best subcluster strategy: `keyword` formats=`11`

#### Segments

- bytes `0`..`0` | kind=`variable` confidence=`0.6873`
- bytes `1`..`1` | kind=`variable` confidence=`0.6571`
- bytes `2`..`4` | kind=`constant` confidence=`1.0`
- bytes `5`..`5` | kind=`variable` confidence=`0.7978`
- bytes `6`..`6` | kind=`constant` confidence=`1.0`
- bytes `7`..`7` | kind=`variable` confidence=`0.7832`
- bytes `8`..`8` | kind=`variable` confidence=`0.7978`
- bytes `9`..`9` | kind=`variable` confidence=`0.7789`
- bytes `10`..`10` | kind=`variable` confidence=`0.764`
- bytes `11`..`11` | kind=`variable` confidence=`0.7756`

#### Field Hypotheses

- bytes `5`..`5` | type=`length` confidence=`1.0` endian=`big`
- bytes `8`..`8` | type=`keyword` confidence=`0.9997`
- bytes `7`..`7` | type=`keyword` confidence=`0.9993`
- bytes `11`..`11` | type=`keyword` confidence=`0.9981`
- bytes `9`..`9` | type=`keyword` confidence=`0.9971`
- bytes `10`..`10` | type=`keyword` confidence=`0.9913`
- bytes `2`..`4` | type=`constant` confidence=`0.99`
- bytes `6`..`6` | type=`constant` confidence=`0.99`
- bytes `0`..`0` | type=`keyword` confidence=`0.9821`
- bytes `1`..`1` | type=`keyword` confidence=`0.9556`

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

- Echoes request fields from family_0 with up to 20 strong offset matches.
- Response size is tied to request fields from family_0.
- Echoes request fields from family_11 with up to 20 strong offset matches.
- Response size is tied to request fields from family_11.
- Echoes request fields from family_13 with up to 20 strong offset matches.

#### Feature Summary

- Messages with repetition: `5770` (`1.0`)
- Repeated n-gram instances: `5929`
- Top motifs: `0000`x11596, `000000`x5826, `0006`x3213, `000006`x3212, `000601`x3212
