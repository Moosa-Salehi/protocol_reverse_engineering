#!/usr/bin/env python3
"""Mock llama-server for smoke-testing the local-finetuned backend.

Returns plausible fine-tuned-model JSON for boundary_refinement and
semantic_labeling prompts without running any model. Usage:
    python tests/mock_llama_server.py [port]
"""
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quiet
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        prompt = body["messages"][-1]["content"]
        payload_hex = re.search(r'"payload_hex":"([0-9a-f]+)"', prompt)
        plen = len(payload_hex.group(1)) // 2 if payload_hex else 8

        if "### TASK: boundary_refinement" in prompt:
            # Model merges fields 2+3 (edges 0,1,6,end) - differs from a
            # hypothetical stage-07 hypothesis of 1+2+5 by dropping edge 3.
            boundaries = sorted({0, 1, plen})
            content = json.dumps({"boundaries": boundaries})
        elif "### TASK: semantic_labeling" in prompt:
            content = json.dumps(
                {
                    "semantic_labels": [
                        {"offset": 0, "width": 1, "semantic_role": "function_code", "field_type": "uint8"},
                        {"offset": 1, "width": 2, "semantic_role": "length", "field_type": "uint16"},
                    ]
                }
            )
        else:
            content = "{}"

        response = {
            "choices": [{"message": {"role": "assistant", "content": content}}],
            "model": "mock",
        }
        data = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"mock llama-server on :{port}")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
