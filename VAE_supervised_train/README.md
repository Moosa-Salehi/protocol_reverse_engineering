# Supervised VAE clustering experiment

This directory contains an isolated experimental pipeline. Trusted protocol and family
metadata is used by annotation, balanced sampling, loss construction, and evaluation;
the model input contains only payload byte IDs and a padding mask.

Build the cached dataset from the existing sampled captures:

```bash
python VAE_supervised_train/build_dataset.py \
  --pcap-root finetuning/windows_data/sampled_pcaps \
  --output VAE_supervised_train/cache/messages.jsonl
```

Each PCAP result is cached under `cache/pcap_records/`. Re-running the command reuses a
cache entry when the source path, size, modification time, extraction rules, and
confidence threshold are unchanged. Use `--force` only to deliberately rerun TShark.

Train on all eligible records (there is no database row split):

```bash
python VAE_supervised_train/train.py \
  --dataset VAE_supervised_train/cache/messages.jsonl \
  --output VAE_supervised_train/checkpoints/best.pth
```

`--train-protocols` and `--validation-protocols` accept comma-separated names. Validation
defaults to the full training selection. A distinct validation protocol set is useful
for measuring transfer, but records are never randomly split. Families below
`--min-family-support` are excluded from training; singleton families remain available
to evaluation. Sampling with replacement safely handles small families.

Training always initializes a new model from scratch. Metrics are JSONL by default;
pass `--metrics-format json` for a single JSON array.

Evaluate a checkpoint with independent HDBSCAN runs per protocol:

```bash
python VAE_supervised_train/evaluate.py \
  --dataset VAE_supervised_train/cache/messages.jsonl \
  --checkpoint VAE_supervised_train/checkpoints/best.pth \
  --output VAE_supervised_train/checkpoints/evaluation.json
```

The checkpoint is intentionally a new format and is not silently compatible with the
legacy `assets/pre_trained/industrial_VAE.pth`. Its deterministic `mu` vector is the
embedding intended for HDBSCAN.
