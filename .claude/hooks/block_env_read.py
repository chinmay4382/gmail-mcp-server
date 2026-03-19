#!/usr/bin/env python3
import json, sys, re

data = json.load(sys.stdin)
path = data.get("tool_input", {}).get("file_path", "")

if re.search(r"(^|\/)\.env$", path):
    print(json.dumps({
        "decision": "block",
        "reason": "Reading .env is blocked — use .env.example instead"
    }))
    sys.exit(2)
