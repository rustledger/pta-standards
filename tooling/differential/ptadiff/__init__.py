"""ptadiff: format-generic differential testing of plain-text-accounting
parsers against a reference implementation.

Stages: oracle adapters and the implementation protocol produce errors;
`compare` finds where two sides disagree; a format's key names each
mismatch; `minimize` shrinks an input while keeping its key; `cluster`
groups by key; `report` writes JSON and markdown. See README.md.
"""

from .cluster import Cluster, Member, cluster, minimize_clusters
from .compare import Divergence, agree, divergences, first_divergence, line_counts
from .formats import FormatPlugin, Mismatch, get_format
from .minimize import Minimized, minimize
from .model import Error, Outcome, Token, content_id
from .pipeline import Differ, Verdict, categorize, load_hooks
from .pool import Crash, run_forked
from .protocol import JsonlImplementation, ProtocolError
from .report import build_report, category_counts, render_markdown

__version__ = "0.1.0"

__all__ = [
    "Cluster",
    "Crash",
    "Differ",
    "Divergence",
    "Error",
    "FormatPlugin",
    "JsonlImplementation",
    "Member",
    "Minimized",
    "Mismatch",
    "Outcome",
    "ProtocolError",
    "Token",
    "Verdict",
    "__version__",
    "agree",
    "build_report",
    "categorize",
    "category_counts",
    "cluster",
    "content_id",
    "divergences",
    "first_divergence",
    "get_format",
    "line_counts",
    "load_hooks",
    "minimize",
    "minimize_clusters",
    "render_markdown",
    "run_forked",
]
