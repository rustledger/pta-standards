"""One oracle, one implementation, one format: a verdict and a category for
every input."""

from __future__ import annotations

import importlib.util
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .compare import Divergence, first_divergence
from .formats.base import FormatPlugin, Mismatch, Normalizer
from .model import Error
from .pool import Crash


@dataclass(frozen=True)
class Verdict:
    """The comparison of one input. `status` is `match`, `mismatch` or
    `crash` (the oracle gave no verdict; the implementation is not judged).
    Errors are the normalized ones; `key` is set for a mismatch."""

    status: str
    oracle: tuple[Error, ...] = ()
    impl: tuple[Error, ...] = ()
    divergence: Divergence | None = None
    key: str | None = None
    crash: str | None = None


def categorize(
    fmt: FormatPlugin,
    key_name: str | None,
    text: str,
    oracle: Sequence[Error],
    impl: Sequence[Error],
    tokens=None,
) -> tuple[Divergence | None, str | None]:
    """The first divergence of two NORMALIZED error lists and its category
    key, or `(None, None)` when they agree. `text` is the oracle's input;
    `tokens` the oracle's tokens for it (needed by token-shape keys; `None`
    when the lexer crashed, which such keys mark with `?`)."""
    d = first_divergence(oracle, impl)
    if d is None:
        return None, None
    m = Mismatch(text, tuple(oracle), tuple(impl), d, None if tokens is None else tuple(tokens))
    return d, fmt.key(key_name)(m)


class Differ:
    """Runs both sides over batches of inputs and judges each one."""

    def __init__(self, fmt: FormatPlugin, oracle, impl, *, key: str | None = None, jobs: int = 1):
        self.fmt, self.oracle, self.impl = fmt, oracle, impl
        self.key_name = key or fmt.default_key
        fmt.key(self.key_name)  # fail early on an unknown key
        self.jobs = jobs

    def evaluate(self, items: Sequence[tuple[str, str]]) -> dict[str, Verdict]:
        """`{id: Verdict}` for every `(id, text)`."""
        fmt = self.fmt
        oracle_text = {i: fmt.oracle_input(t) for i, t in items}
        oracle_out = self.oracle.parse(list(oracle_text.items()), jobs=self.jobs)
        impl_out = self.impl.run(items)
        verdicts: dict[str, Verdict] = {}
        pending = {}
        for i, _ in items:
            o = oracle_out[i]
            if not o.ok:
                verdicts[i] = Verdict("crash", crash=o.crash)
                continue
            text = oracle_text[i]
            oe = tuple(fmt.normalize("oracle", text, list(o.errors)))
            ie = tuple(fmt.normalize("impl", text, list(impl_out[i])))
            d = first_divergence(oe, ie)
            if d is None:
                verdicts[i] = Verdict("match", oe, ie)
            else:
                pending[i] = (oe, ie, d)
        tokens = {}
        if pending and fmt.needs_tokens:
            tokens = self.oracle.lex([(i, oracle_text[i]) for i in pending], jobs=self.jobs)
        keyfn = fmt.key(self.key_name)
        for i, (oe, ie, d) in pending.items():
            toks = tokens.get(i)
            toks = None if toks is None or isinstance(toks, Crash) else tuple(toks)
            key = keyfn(Mismatch(oracle_text[i], oe, ie, d, toks))
            verdicts[i] = Verdict("mismatch", oe, ie, d, key)
        return verdicts

    def keys_of(self, texts: Sequence[str]) -> list[str | None]:
        """Each text's category key, `None` where it matches or crashes: the
        minimizer's test."""
        items = [(f"m{n}", t) for n, t in enumerate(texts)]
        v = self.evaluate(items)
        return [v[i].key for i, _ in items]


def load_hooks(fmt: FormatPlugin, path: str | Path) -> None:
    """Append the normalizers a hooks module defines to `fmt`.

    The module may define any of `oracle_input(text) -> text`,
    `normalize_oracle(text, errors) -> errors` and
    `normalize_impl(text, errors) -> errors` (errors are `ptadiff.Error`
    lists). They run after the format's own normalizers. This is where an
    implementation states its DELIBERATE differences from the oracle, so
    they are not counted as mismatches.
    """
    spec = importlib.util.spec_from_file_location("ptadiff_hooks", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load hooks from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for attr, side in (
        ("oracle_input", "oracle-input"),
        ("normalize_oracle", "oracle"),
        ("normalize_impl", "impl"),
    ):
        fn = getattr(module, attr, None)
        if fn is not None:
            fmt.normalizers.append(Normalizer(f"hooks:{attr}", side, fn, f"from {path}"))
