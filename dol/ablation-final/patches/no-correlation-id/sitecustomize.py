# ablation: no correlation-id detection (pairing falls back to the adjacency score; the discriminator search no longer
# masks the correlation-id bytes)
from protocol_re.config.thresholds import RequestResponsePairing
RequestResponsePairing.CORRELATION_MIN_COVERAGE = 1.01
