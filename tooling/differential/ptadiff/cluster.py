"""Group mismatches by category key."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field


@dataclass
class Member:
    """One mismatching input: its id, category key, text, where it came
    from, and any consumer-defined label (a symptom bucket, say)."""

    id: str
    key: str
    text: str
    source: str = ""
    label: str = ""
    #: The input itself when it is more than `text` (a multi-file
    #: `ptadiff.snapshot.Ledger`, whose `text` is its rendering).
    payload: object = None


@dataclass
class Cluster:
    key: str
    members: list[Member] = field(default_factory=list)
    #: The minimized form of `shortest`, once a minimizer has run.
    minimized: str | None = None
    minimized_complete: bool | None = None
    #: What the minimized example is made of (the format's
    #: `ledger_features`), for a semantic cluster.
    features: list[str] | None = None

    @property
    def size(self) -> int:
        return len(self.members)

    @property
    def shortest(self) -> Member:
        """The shortest member (ties broken by text, then id)."""
        return min(self.members, key=lambda m: (len(m.text), m.text, m.id))

    def by(self, attr: str) -> Counter[str]:
        return Counter(getattr(m, attr) for m in self.members)


def cluster(members: Iterable[Member]) -> list[Cluster]:
    """One cluster per key, largest first, ties by key."""
    groups: dict[str, Cluster] = {}
    for m in members:
        groups.setdefault(m.key, Cluster(m.key)).members.append(m)
    return sorted(groups.values(), key=lambda c: (-c.size, c.key))


def minimize_clusters(
    clusters: list[Cluster],
    minimize_one: Callable[[str, str], tuple[str, bool]],
    *,
    top: int | None = None,
) -> None:
    """Set `minimized` on the first `top` clusters (all when `None`):
    `minimize_one(text, key)` returns the minimized text and whether the
    minimizer reached a fixed point."""
    for c in clusters[: top if top is not None else len(clusters)]:
        c.minimized, c.minimized_complete = minimize_one(c.shortest.text, c.key)
