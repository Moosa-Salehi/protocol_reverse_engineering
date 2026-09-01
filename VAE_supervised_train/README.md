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

The current defaults write `best_v3.pth`, `latest_v3.pth`, and `metrics_v3.jsonl`,
preserving earlier runs. Validation is performed every five epochs on a deterministic
family-stratified subset. All eligible records are still used for training. Each
protocol tunes HDBSCAN independently.

With the default zero reconstruction weight, the decoder is bypassed completely during
training. Metrics are JSONL by default; pass `--metrics-format json` for a single JSON
array. When the subset produces a new best candidate, full-corpus validation is enabled
by default. It re-embeds all messages and retunes HDBSCAN per protocol using absolute
cluster sizes plus fractions of that protocol's population. Only the full-corpus score
can update `best_v3.pth`; subset metrics are only a fast candidate gate. Disable this
behavior with `--no-full-validation-on-best`.

Candidate full embeddings are stored under `checkpoints/full_embedding_cache/`. Each
cache entry includes a model signature and is reused only when the weights and dataset
shape match. Full HDBSCAN tuning uses a two-stage search: all population-scaled cluster
sizes are scanned first, then `min_samples` and epsilon are refined around the winning
size.

Training displays epoch, batch, loss, and HDBSCAN-tuning progress with `tqdm`. Deprecation
and future warnings are hidden by default. Use `--show-warnings` to restore them or
`--no-progress` for non-interactive logs.

At startup the trainer prints whether it is using CPU or CUDA. For CUDA it also reports
the GPU model, CUDA version, compute capability, memory, and mixed-precision status.
`CUBLAS_WORKSPACE_CONFIG=:4096:8` is set before PyTorch operations so deterministic CUDA
training does not emit repeated CuBLAS warnings.

Interrupted revised runs can resume with complete optimizer and early-stopping state:

```bash
python VAE_supervised_train/train.py \
  --dataset VAE_supervised_train/cache/messages.jsonl \
  --resume VAE_supervised_train/checkpoints/latest_v3.pth
```

`--epochs` is the final epoch number when resuming, not the number of additional epochs.
Legacy `best.pth` checkpoints cannot resume because they do not contain optimizer state,
but they remain valid for evaluation.

Evaluate a checkpoint with independent HDBSCAN runs per protocol:

```bash
python VAE_supervised_train/evaluate.py \
  --dataset VAE_supervised_train/cache/messages.jsonl \
  --checkpoint VAE_supervised_train/checkpoints/best_v3.pth \
  --output VAE_supervised_train/checkpoints/evaluation.json
```

Evaluation automatically uses the saved per-protocol HDBSCAN settings. Pass
`--no-use-checkpoint-hdbscan` to override them with the global CLI settings.

The checkpoint is intentionally a new format and is not silently compatible with the
legacy `assets/pre_trained/industrial_VAE.pth`. Its deterministic `mu` vector is the
embedding intended for HDBSCAN.

To use the supervised encoder in the existing family-discovery stage, pass the
checkpoint as the neural model and provide the existing filter argument. 
The filter is metadata and it is never supplied to the model:

```bash
python scripts/04_discover_families.py input_messages.jsonl families.json \
  --method hdbscan \
  --feature-mode neural \
  --neural-model-path VAE_supervised_train/checkpoints/best_v3.pth \
  --supervised-hdbscan-checkpoint VAE_supervised_train/checkpoints/best_v3.pth \
  --tshark-filter modbus \
  --sample-size 0 \
  --pca-components 0
```
