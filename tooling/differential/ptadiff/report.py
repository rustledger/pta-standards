"""The per-category report: JSON for machines, a markdown table for people.

Both are deterministic for the same inputs (sorted, no timestamps), so a
nightly job can commit them and diff one night against the last.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from typing import Any

from .cluster import Cluster

SCHEMA = "ptadiff-report/1"


def build_report(
    clusters: list[Cluster],
    totals: Mapping[str, int],
    *,
    by_source: Mapping[str, Mapping[str, int]] | None = None,
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """The report as a JSON-ready dict.

    `totals` counts inputs by status (`match`, `mismatch`, `crash`);
    `by_source` the same per input source; `meta` is copied in as is (format,
    key, oracle and implementation versions, revisions...)."""
    mismatches = sum(c.size for c in clusters)
    return {
        "schema": SCHEMA,
        **dict(meta or {}),
        "totals": {"inputs": sum(totals.values()), **dict(sorted(totals.items()))},
        "by_source": {k: dict(sorted(v.items())) for k, v in sorted((by_source or {}).items())},
        "categories": [
            {
                "key": c.key,
                "size": c.size,
                "share": round(c.size / mismatches, 4) if mismatches else 0.0,
                "sources": dict(sorted(c.by("source").items())),
                "labels": dict(sorted(c.by("label").items())),
                "example": {
                    "id": c.shortest.id,
                    "source": c.shortest.source,
                    "text": c.shortest.text,
                },
                "minimized": c.minimized,
                "minimized_complete": c.minimized_complete,
                **({"features": c.features} if c.features is not None else {}),
            }
            for c in clusters
        ],
    }


def category_counts(report: Mapping[str, Any]) -> dict[str, int]:
    """`{key: size}` from a report: what a CI pin records."""
    return {c["key"]: c["size"] for c in report["categories"]}


def _cell(text: str) -> str:
    """`text` as an inline-code markdown table cell: JSON-escaped (so
    newlines and control characters show), pipes escaped."""
    body = json.dumps(text, ensure_ascii=True).replace("|", "\\|")
    fence = "``" if "`" in body else "`"
    pad = " " if fence == "``" else ""
    return f"{fence}{pad}{body}{pad}{fence}"


def _labels(labels: Mapping[str, int], top: int = 3) -> str:
    ranked = sorted(((k, n) for k, n in labels.items() if k), key=lambda kv: (-kv[1], kv[0]))
    shown = ", ".join(f"{k} {n}" for k, n in ranked[:top])
    return shown + (", ..." if len(ranked) > top else "")


def render_markdown(
    report: Mapping[str, Any],
    *,
    limit: int | None = 50,
    title: str | None = None,
    level: int = 1,
) -> str:
    """The report as markdown: totals, then one row per category (the first
    `limit`, all when `None`), each with its minimized example when there is
    one and its shortest example otherwise, and, when members carry labels,
    the most common ones. `title` heads it at heading `level`."""
    out = []
    title = title or report.get("title") or "Differential parse report"
    out += [f"{'#' * level} {title}", ""]
    for k in ("format", "key", "oracle", "implementation"):
        if k in report:
            v = report[k]
            out.append(f"- {k}: {v if isinstance(v, str) else json.dumps(v, sort_keys=True)}")
    t = report["totals"]
    out.append(
        f"- inputs: {t['inputs']}; match {t.get('match', 0)}, mismatch "
        f"{t.get('mismatch', 0)}, oracle crashed {t.get('crash', 0)}"
        + (f", deliberate deviation {t['deviation']}" if t.get("deviation") else "")
    )
    for name, n in sorted((report.get("deviations") or {}).items()):
        out.append(f"  - deviation `{name}`: {n}")
    cats = report["categories"]
    out.append(f"- categories: {len(cats)}")
    out.append("")
    if report.get("by_source"):
        out += ["| Source | Inputs | Match | Mismatch | Oracle crashed |", "|---|---|---|---|---|"]
        for src, c in report["by_source"].items():
            n = sum(c.values())
            out.append(
                f"| {src} | {n} | {c.get('match', 0)} | {c.get('mismatch', 0)} | {c.get('crash', 0)} |"
            )
        out.append("")
    shown = cats if limit is None else cats[:limit]
    labelled = any(k for c in cats for k in c.get("labels", {}))
    out += [
        "| # | Inputs | Share | Category |"
        + (" Labels |" if labelled else "")
        + " Example (minimized when marked *) |",
        "|---|---|---|---|" + ("---|" if labelled else "") + "---|",
    ]
    for rank, c in enumerate(shown, 1):
        if c.get("minimized") is not None:
            ex = _cell(c["minimized"]) + " *"
        else:
            ex = _cell(c["example"]["text"])
        if c.get("features"):
            ex += " (" + ", ".join(c["features"]) + ")"
        labels = f" {_labels(c['labels'])} |" if labelled else ""
        out.append(
            f"| {rank} | {c['size']} | {100 * c['share']:.1f}% | {_cell(c['key'])} |{labels} {ex} |"
        )
    if limit is not None and len(cats) > limit:
        rest = cats[limit:]
        out.append(
            f"| | {sum(c['size'] for c in rest)} | | {len(rest)} more categories |"
            + (" |" if labelled else "")
            + " |"
        )
    out.append("")
    covered = Counter()
    total = sum(c["size"] for c in cats)
    acc = 0
    for q, c in enumerate(cats, 1):
        acc += c["size"]
        if q in (5, 10, 20, 50):
            covered[q] = acc
    if total:
        out.append(
            "Coverage: "
            + ", ".join(f"top {q} = {100 * n / total:.1f}%" for q, n in sorted(covered.items()))
        )
        out.append("")
    return "\n".join(out)
