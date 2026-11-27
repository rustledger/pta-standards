"""`python -m ptadiff`: generate inputs, run a differential, minimize one input.

    python -m ptadiff generate --format beancount --generator g1 --seed 1 --n 1000 -o g1.jsonl
    python -m ptadiff run --format beancount --impl "IMPL --jsonl" \\
        --input corpus/ --input g1.jsonl --gen g2:1:1000 \\
        [--hooks hooks.py] [--key shape] [--minimize 10] \\
        [--results out.jsonl] [--json report.json] [--markdown report.md]
    python -m ptadiff minimize --format beancount --impl "IMPL --jsonl" FILE
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

from . import __version__
from .cluster import Member, cluster, minimize_clusters
from .formats import FORMATS, get_format
from .minimize import minimize
from .model import content_id
from .pipeline import Differ, load_hooks
from .protocol import JsonlImplementation
from .report import build_report, render_markdown


def read_inputs(path: Path, extensions: tuple[str, ...]):
    """`(source, label, text)` for every input under `path`: a directory's
    files with one of `extensions` (recursively, in path order), a `.jsonl`
    file's `{"text": ...}` lines, or any other file whole. Files that are not
    UTF-8 are skipped."""
    if path.is_dir():
        for p in sorted(q for q in path.rglob("*") if q.is_file()):
            if extensions and p.suffix not in extensions:
                continue
            try:
                yield str(path), str(p.relative_to(path)), p.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                continue
    elif path.suffix == ".jsonl":
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f):
                obj = json.loads(line)
                yield str(path), obj.get("id") or f"{path.name}:{n}", obj["text"]
    else:
        yield str(path), path.name, path.read_bytes().decode("utf-8")


def _setup(args):
    fmt = get_format(args.format)
    for name in args.no_normalize or ():
        fmt.normalizer(name).enabled = False
    if args.hooks:
        load_hooks(fmt, args.hooks)
    oracle = fmt.oracle()
    impl = JsonlImplementation(args.impl)
    return fmt, Differ(fmt, oracle, impl, key=args.key, jobs=args.jobs)


def cmd_generate(args) -> int:
    fmt = get_format(args.format)
    gen = fmt.generators[args.generator]
    lines = "".join(
        json.dumps({"id": content_id(text), "text": text}) + "\n" for text in gen(args.seed, args.n)
    )
    if args.output:
        Path(args.output).write_text(lines, encoding="utf-8")
    else:
        sys.stdout.write(lines)
    return 0


def cmd_run(args) -> int:
    fmt, differ = _setup(args)
    items: dict[str, tuple[str, str, str]] = {}
    for p in args.input or ():
        for source, label, text in read_inputs(Path(p), fmt.extensions):
            items.setdefault(content_id(text), (source, label, text))
    for spec in args.gen or ():
        name, seed, n = spec.split(":")
        for text in fmt.generators[name](int(seed), int(n)):
            items.setdefault(content_id(text), (f"{name}:{seed}", "", text))
    if not items:
        print("error: no inputs", file=sys.stderr)
        return 2
    order = sorted(items)
    verdicts = differ.evaluate([(i, items[i][2]) for i in order])
    totals: Counter[str] = Counter()
    by_source: dict[str, Counter[str]] = defaultdict(Counter)
    members = []
    for i in order:
        source, label, text = items[i]
        v = verdicts[i]
        totals[v.status] += 1
        by_source[source][v.status] += 1
        if v.status == "mismatch":
            members.append(Member(i, v.key or "", text, source, ""))
    clusters = cluster(members)

    def one(text, key):
        r = minimize(text, key, differ.keys_of, fmt.shrink_units)
        return r.text, r.complete

    if args.minimize:
        minimize_clusters(clusters, one, top=args.minimize)
    oracle = differ.oracle
    report = build_report(
        clusters,
        totals,
        by_source=by_source,
        meta={
            "format": fmt.name,
            "key": differ.key_name,
            "oracle": {"name": oracle.name, "version": oracle.version()},
            "implementation": differ.impl.name,
            "ptadiff": __version__,
        },
    )
    if args.results:
        with open(args.results, "w", encoding="utf-8") as f:
            for i in order:
                v = verdicts[i]
                source, label, text = items[i]
                f.write(
                    json.dumps(
                        {
                            "id": i,
                            "source": source,
                            "label": label,
                            "status": v.status,
                            "key": v.key,
                            "crash": v.crash,
                            "text": text,
                            "oracle": [e.to_json() for e in v.oracle],
                            "impl": [e.to_json() for e in v.impl],
                        }
                    )
                    + "\n"
                )
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    md = render_markdown(report, limit=args.limit)
    if args.markdown:
        Path(args.markdown).write_text(md, encoding="utf-8")
    print(md)
    return 0


def cmd_minimize(args) -> int:
    fmt, differ = _setup(args)
    text = Path(args.file).read_bytes().decode("utf-8")
    key = differ.keys_of([text])[0]
    if key is None:
        print("the input does not mismatch", file=sys.stderr)
        return 1
    r = minimize(text, key, differ.keys_of, fmt.shrink_units, max_evaluations=args.budget)
    print(
        json.dumps(
            {"key": key, "text": r.text, "evaluations": r.evaluations, "complete": r.complete}
        )
    )
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="ptadiff", description=__doc__.splitlines()[0])
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="write a generator's inputs as JSON lines")
    g.add_argument("--format", choices=FORMATS, required=True)
    g.add_argument("--generator", required=True)
    g.add_argument("--seed", type=int, required=True)
    g.add_argument("--n", type=int, required=True)
    g.add_argument("-o", "--output")
    g.set_defaults(fn=cmd_generate)

    def common(p):
        p.add_argument("--format", choices=FORMATS, required=True)
        p.add_argument("--impl", required=True, help="the implementation's command line")
        p.add_argument("--hooks", help="a module of extra normalizers (see load_hooks)")
        p.add_argument("--key", help="category key name (default: the format's first)")
        p.add_argument("--no-normalize", action="append", metavar="NAME")
        p.add_argument("--jobs", type=int, default=os.cpu_count() or 1)

    r = sub.add_parser("run", help="compare, categorize, cluster and report")
    common(r)
    r.add_argument("--input", action="append", help="a directory, .jsonl, or file")
    r.add_argument("--gen", action="append", metavar="NAME:SEED:N")
    r.add_argument("--minimize", type=int, default=0, metavar="TOP")
    r.add_argument("--results", help="per-input JSON lines")
    r.add_argument("--json", help="the report as JSON")
    r.add_argument("--markdown", help="the report as markdown")
    r.add_argument("--limit", type=int, default=50, help="markdown rows")
    r.set_defaults(fn=cmd_run)

    m = sub.add_parser("minimize", help="minimize one input, keeping its category")
    common(m)
    m.add_argument("file")
    m.add_argument("--budget", type=int, default=5000)
    m.set_defaults(fn=cmd_minimize)

    args = ap.parse_args(argv)
    return args.fn(args)
