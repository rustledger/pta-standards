"""A semantic-mode implementation under test: beancount's own snapshot,
perturbed on request, so the pipeline can be tested end to end.

* a ledger holding `; PERTURB-ERROR` gets an extra error on that line;
* `; PERTURB-UNITS` doubles the first posting's units of every transaction;
* `; PERTURB-CRASH` answers a crash.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ptadiff.formats.beancount.semantic import _load_one

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

for raw in sys.stdin:
    obj = json.loads(raw)
    text = obj["text"]
    if "; PERTURB-CRASH" in text:
        print(json.dumps({"id": obj["id"], "crash": "panicked: on request"}))
        continue
    snap = _load_one(obj)
    for n, line in enumerate(text.split("\n"), 1):
        if "; PERTURB-ERROR" in line:
            snap["errors"].append({"file": "main.beancount", "line": n, "code": "X1", "msg": "x"})
    if "; PERTURB-UNITS" in text:
        for e in snap["entries"]:
            if e["type"] == "transaction" and e["postings"]:
                u = e["postings"][0]["units"]
                u["number"] = str(2 * float(u["number"]))
    print(json.dumps({"id": obj["id"], "snapshot": snap}, ensure_ascii=False))
