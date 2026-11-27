import json

from ptadiff.cluster import Member, cluster, minimize_clusters
from ptadiff.report import build_report, category_counts, render_markdown


def members():
    return [
        Member("1", "k|b", "long text", "fuzz"),
        Member("2", "k|a", "xx", "gen"),
        Member("3", "k|b", "bb", "fuzz", "lbl"),
        Member("4", "k|b", "aa", "gen"),
    ]


def test_cluster_orders_by_size_then_key():
    cs = cluster(members())
    assert [(c.key, c.size) for c in cs] == [("k|b", 3), ("k|a", 1)]
    assert cs[0].shortest.id == "4"  # ties on length broken by text
    assert cs[0].by("source") == {"fuzz": 2, "gen": 1}


def test_report_json_and_markdown():
    cs = cluster(members())
    minimize_clusters(cs, lambda text, key: (text[:1], True), top=1)
    rep = build_report(cs, {"match": 6, "mismatch": 4}, meta={"format": "f", "key": "shape"})
    assert rep["totals"] == {"inputs": 10, "match": 6, "mismatch": 4}
    assert category_counts(rep) == {"k|b": 3, "k|a": 1}
    assert rep["categories"][0]["minimized"] == "a"
    assert rep["categories"][1]["minimized"] is None
    json.dumps(rep)  # serializable
    md = render_markdown(rep)
    # Keys hold pipes, which must not break the table.
    assert '`"k\\|b"`' in md
    assert '`"a"` *' in md
    # One member carries a label, so the table shows a labels column.
    assert "| Labels |" in md and "lbl 1" in md
    assert render_markdown(rep, title="T", level=2).startswith("## T\n")


def test_report_markdown_escapes_backticks_and_newlines():
    cs = cluster([Member("1", "k", "a`b\nc", "s")])
    md = render_markdown(build_report(cs, {"mismatch": 1}))
    assert '`` "a`b\\nc" ``' in md


def test_report_is_deterministic():
    a = build_report(cluster(members()), {"mismatch": 4})
    b = build_report(cluster(list(reversed(members()))), {"mismatch": 4})
    assert a == b
