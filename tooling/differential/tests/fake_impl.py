"""A tiny implementation under test that speaks the ptadiff protocol."""

import json
import sys

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

for raw in sys.stdin:
    obj = json.loads(raw)
    errors = []
    for n, line in enumerate(obj["text"].split("\n"), 1):
        if "BAD2" in line:
            errors += [{"line": n, "code": "X2", "msg": "bad2"}] * 2
        elif "BAD" in line:
            # The line itself, unescaped below: messages quote input.
            errors.append({"line": n, "code": "X1", "msg": "bad: " + line})
    if "EOF!" in obj["text"]:
        errors.append({"line": 0, "code": "X0", "msg": "eof"})
    sys.stdout.write(json.dumps({"id": obj["id"], "errors": errors}, ensure_ascii=False) + "\n")
