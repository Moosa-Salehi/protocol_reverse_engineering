# Cluster-free dataset workflow

This workflow builds fine-tuning records without HDBSCAN, VAE, family IDs, or a
protocol model. It uses small local batches grouped by direction and payload
length, while targets come from reviewed annotations.

Expected layout:

```text
messages\<protocol>\01_messages.jsonl
annotations\<protocol>.jsonl   # or .json
```

Run on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\finetuning\cluster-free-dataset\build_all_windows.ps1 `
  -MessagesRoot .\finetuning\windows_data\runs `
  -AnnotationsRoot .\finetuning\cluster-free-dataset\annotations `
  -OutputRoot .\finetuning\cluster-free-dataset\data
```

Each annotation must contain `msg_id` and at least one of `boundaries` or
`semantic_labels`. Set `reviewed=true` and `approved=true` only after review.
Run the normal promotion, leakage audit, rendered-length check, and dataset
split commands before training. This workflow does not create gold labels from
raw payloads automatically.

The builder emits one prompt per target message, omits empty semantic targets
unless `--include-empty-semantic` is explicitly supplied, and rejects prompts
over its default 12,000-character limit. Protocol identity is kept in record
metadata rather than copied into the user prompt so the leakage audit can check
for protocol-name leakage.

Validate a regenerated file before splitting:

```bash
python finetuning/cluster-free-dataset/validate_dataset.py \
  finetuning/cluster-free-dataset/data/combined/raw.jsonl
```
