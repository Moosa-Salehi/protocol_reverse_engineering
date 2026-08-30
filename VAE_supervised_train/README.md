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
  --dataset VAE_supervised_train/cache/messages.jsonl
```

`--train-protocols` and `--validation-protocols` accept comma-separated names. Validation
defaults to the full training selection. A distinct validation protocol set is useful
for measuring transfer, but records are never randomly split. Families below
`--min-family-support` are excluded from training; singleton families remain available
to evaluation. Sampling with replacement safely handles small families.

The revised defaults write `best_v2.pth`, `latest.pth`, and `metrics_v2.jsonl`, preserving
the original experimental run. Validation is performed every five epochs on a
deterministic family-stratified subset. All eligible records are still used for
training. Each protocol tunes HDBSCAN independently over larger cluster-size values.

With the default zero reconstruction weight, the decoder is bypassed completely during
training. Metrics are JSONL by default; pass `--metrics-format json` for a single JSON
array. To run expensive full-corpus validation only when the subset produces a new best
candidate, add `--full-validation-on-best`.

Interrupted revised runs can resume with complete optimizer and early-stopping state:

```bash
python VAE_supervised_train/train.py \
  --dataset VAE_supervised_train/cache/messages.jsonl \
  --resume VAE_supervised_train/checkpoints/latest.pth
```

`--epochs` is the final epoch number when resuming, not the number of additional epochs.
Legacy `best.pth` checkpoints cannot resume because they do not contain optimizer state,
but they remain valid for evaluation.

Evaluate a checkpoint with independent HDBSCAN runs per protocol:

```bash
python VAE_supervised_train/evaluate.py \
  --dataset VAE_supervised_train/cache/messages.jsonl \
  --checkpoint VAE_supervised_train/checkpoints/best_v2.pth \
  --output VAE_supervised_train/checkpoints/evaluation.json
```

Evaluation automatically uses the saved per-protocol HDBSCAN settings. Pass
`--no-use-checkpoint-hdbscan` to override them with the global CLI settings.

The checkpoint is intentionally a new format and is not silently compatible with the
legacy `assets/pre_trained/industrial_VAE.pth`. Its deterministic `mu` vector is the
embedding intended for HDBSCAN.
