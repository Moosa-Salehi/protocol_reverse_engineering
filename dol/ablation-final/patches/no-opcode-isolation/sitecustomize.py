# ablation: no opcode isolation in stage 07 (loaded through PYTHONPATH before any pipeline module)
from protocol_re.config.thresholds import BoundaryDetection
BoundaryDetection.ISOLATE_BODY_OPCODE = False
