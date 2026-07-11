from __future__ import annotations

from protocol_re.export.html import _byte_ruler


def test_byte_ruler_caps_template_to_family_modal_length() -> None:
    family = {
        "family_id": "family_0",
        "template": " ".join(["00"] * 20),
        "segments": [{"start": 0, "end": 20}],
        "feature_summary": {
            "structure_stats": {
                "length_profile": {
                    "kind": "mostly_fixed",
                    "modal_length": 12,
                    "modal_ratio": 0.96,
                }
            }
        },
    }
    labels = [
        {"start": 0, "length": 6, "label": "header", "field_type": "bytes"},
        {"start": 10, "length": 8, "label": "payload", "field_type": "bytes"},
        {"start": 18, "length": 2, "label": "noise", "field_type": "bytes"},
    ]

    html = _byte_ruler(family, labels=labels)

    assert "--cols:12" in html
    assert "+8" in html
    assert "grid-column:11 / span 2" in html
    assert "grid-column:19" not in html
    assert "clipped at modal length 12" in html
