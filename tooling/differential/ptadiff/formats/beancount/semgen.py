"""Seeded generators of WELL-FORMED beancount ledgers, for the semantic
differential.

Each generator is a pure function of `(seed, n)` returning `n` distinct
`ptadiff.snapshot.Ledger`s, sorted by id. It draws only from its own
`random.Random(seed)` with `random`, `randint`, `randrange` and `choice`
(stable across CPython versions), so a count measured over a sample can be
pinned in CI; `tests/test_semgen.py` pins a digest of each.

The ledgers parse cleanly. A small model of the ledger (what each account
holds, lot by lot, and each cash balance) keeps most of them valid: a
reduction names lots that exist, a balance assertion asserts what the model
computes. About one ledger in five carries one deliberate FAULT (an oversold
lot, an off balance, an unbalanced transaction, a closed or unopened account,
an ambiguous match...), so booking and validation errors are compared too.

The weight is on where implementations have disagreed: lots with cost, date
and label; every booking method, AVERAGE and NONE included; partial and total
reductions; `{}`, `{{}}` and `{#}` cost specs; `@` and `@@` prices; elided
amounts; tolerances, precision and rounding; pads and balance assertions
(with `~` tolerances); several currencies; `operating_currency`; includes
whose files set options and plugins; beancount's built-in plugins.

* `s1`: lots and booking: buys and sells under every method;
* `s2`: pads, balances, tolerances, precision and rounding;
* `s3`: multi-file ledgers: includes, options and plugins across files;
* `s4`: beancount's built-in plugins;
* `smix`: a mix of all of the above.

The vocabulary and the model are ours, written for this differential work;
nothing is taken from beancount's sources.
"""

from __future__ import annotations

import datetime as _dt
import random
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal

from ...snapshot import Ledger, ledger_id
from ..base import Generator

METHODS = ("STRICT", "FIFO", "LIFO", "HIFO", "AVERAGE", "NONE", "STRICT_WITH_SIZE")
#: The methods a lot account is opened with, in proportion. AVERAGE is the
#: rarest: beancount 3.2.3 does not implement it, so most AVERAGE ledgers
#: are a declared deviation of every implementation that does.
METHOD_DRAW = (
    *("STRICT", "FIFO") * 3,
    *("LIFO", "HIFO", "NONE", "STRICT_WITH_SIZE") * 2,
    "AVERAGE",
)
COMMODITIES = ("HOOL", "ACME", "VTI", "BTC")
PLUGINS = (
    "implicit_prices",
    "auto_accounts",
    "check_commodity",
    "leafonly",
    "noduplicates",
    "onecommodity",
    "unique_prices",
    "check_closing",
    "close_tree",
    "coherent_cost",
    "sellgains",
    "nounused",
    "check_drained",
    "commodity_attr",
    "currency_accounts",
    "pedantic",
    "auto",
)
FAULTS = (
    "oversell",
    "unbalanced",
    "unbalanced-small",
    "balance-off",
    "unopened",
    "after-close",
    "currency-constraint",
    "ambiguous",
    "two-elided",
    "no-lot",
    "pad-unused",
    "pad-cost",
    "duplicate-open",
)


def _q(x: Decimal, places: int) -> Decimal:
    return x.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_EVEN)


def _fmt(x: Decimal) -> str:
    return format(x, "f")


@dataclass
class Lot:
    units: Decimal
    commodity: str
    cost: Decimal
    currency: str
    date: str
    label: str | None = None


@dataclass
class Model:
    r: random.Random
    day: int = 0
    lines: list[str] = field(default_factory=list)
    opened: dict[str, str | None] = field(default_factory=dict)
    closed: set[str] = field(default_factory=set)
    lots: dict[str, list[Lot]] = field(default_factory=dict)
    cash: dict[tuple[str, str], Decimal] = field(default_factory=dict)
    labels: int = 0
    #: Whether a fault was injected.
    faulted: bool = False
    #: Accounts the model's figures can no longer be trusted for.
    unsure: set[str] = field(default_factory=set)

    # -- helpers ------------------------------------------------------------

    def date(self) -> str:
        return (_dt.date(2024, 1, 1) + _dt.timedelta(days=self.day)).isoformat()

    def tick(self) -> None:
        self.day += self.r.choice((0, 0, 1, 1, 1, 2, 3, 7))

    def emit(self, *lines: str) -> None:
        self.lines.extend(lines)

    def gap(self) -> None:
        if self.r.random() < 0.7:
            self.lines.append("")

    def open(self, account: str, currencies: str = "", booking: str | None = None) -> None:
        if account in self.opened:
            return
        self.opened[account] = booking
        tail = (" " + currencies if currencies else "") + (f' "{booking}"' if booking else "")
        self.emit(f"{self.date()} open {account}{tail}")

    def add_cash(self, account: str, currency: str, number: Decimal) -> None:
        key = (account, currency)
        self.cash[key] = self.cash.get(key, Decimal(0)) + number

    def amount(self, lo: int, hi: int, places: int = 2) -> Decimal:
        return Decimal(self.r.randint(lo * 10**places, hi * 10**places)).scaleb(-places)

    def held(self, account: str, commodity: str) -> list[Lot]:
        return [x for x in self.lots.get(account, []) if x.commodity == commodity and x.units]

    # -- transactions -------------------------------------------------------

    def txn(self, narration: str, postings: list[str], flag: str = "*", extra: str = "") -> None:
        self.emit(f'{self.date()} {flag} "{narration}"{extra}', *postings)
        self.gap()

    def salary(self) -> None:
        n = self.amount(500, 3000, self.r.choice((0, 2, 2, 2)))
        explicit = self.r.random() < 0.5
        self.txn(
            "salary",
            [
                f"  Assets:Cash  {_fmt(n)} USD" if explicit else "  Assets:Cash",
                f"  Income:Salary  -{_fmt(n)} USD",
            ],
        )
        self.add_cash("Assets:Cash", "USD", n)

    def expense(self) -> None:
        r = self.r
        places = r.choice((2, 2, 2, 3, 0, 1))
        parts = [self.amount(1, 80, places) for _ in range(r.randint(1, 3))]
        source = r.choice(("Assets:Cash", "Assets:Cash", "Liabilities:Card"))
        posts = [
            f"  {r.choice(('Expenses:Food', 'Expenses:Fees', 'Expenses:Rent'))}  {_fmt(p)} USD"
            for p in parts
        ]
        total = sum(parts, Decimal(0))
        style = r.random()
        if style < 0.5:
            posts.append(f"  {source}")
        elif style < 0.8:
            posts.append(f"  {source}  -{_fmt(total)} USD")
        else:
            # Explicit, but off by less than the inferred tolerance.
            off = Decimal(r.choice((1, 2, 4))).scaleb(-(places + 1)) if places else Decimal(0)
            posts.append(f"  {source}  -{_fmt(total + off)} USD")
            total += off
        if r.random() < 0.3:
            posts = [posts[-1], *posts[:-1]]
        self.txn("spend", posts)
        self.add_cash(source, "USD", -total)

    def fx(self) -> None:
        r = self.r
        eur = self.amount(10, 500, 2)
        rate = self.amount(1, 1, 4) + Decimal(r.randint(0, 3000)).scaleb(-4)
        usd = _q(eur * rate, 2)
        kind = r.random()
        if kind < 0.4:
            posts = [f"  Assets:Bank:EUR  {_fmt(eur)} EUR @ {_fmt(rate)} USD", "  Assets:Cash"]
            usd = eur * rate
        elif kind < 0.7:
            posts = [
                f"  Assets:Bank:EUR  {_fmt(eur)} EUR @@ {_fmt(usd)} USD",
                f"  Assets:Cash  -{_fmt(usd)} USD",
            ]
        elif kind < 0.85:
            posts = [f"  Assets:Bank:EUR  {_fmt(eur)} EUR @", f"  Assets:Cash  -{_fmt(usd)} USD"]
        else:
            posts = [
                f"  Assets:Cash  -{_fmt(usd)} USD",
                f"  Assets:Bank:EUR  {_fmt(eur)} EUR @@ {_fmt(usd)} USD",
            ]
        self.txn("fx", posts)
        self.add_cash("Assets:Bank:EUR", "EUR", eur)
        self.add_cash("Assets:Cash", "USD", -usd)
        self.unsure.add("Assets:Cash")

    def broker(self, method: str | None = None) -> str:
        method = method or self.r.choice(METHOD_DRAW)
        account = f"Assets:Broker:{method.title().replace('_', '')}"
        if account not in self.opened:
            self.open(account, booking=method if self.r.random() < 0.9 else None)
        return account

    def buy(self, account: str | None = None) -> None:
        r = self.r
        account = account or self.broker()
        comm = r.choice(COMMODITIES)
        units = (
            Decimal(r.randint(1, 20)) if comm != "BTC" else self.amount(0, 2, 4) + Decimal("0.01")
        )
        if r.random() < 0.15 and comm != "BTC":
            units = units + Decimal(r.choice(("0.5", "0.25", "0.125")))
        cost = self.amount(5, 300, r.choice((2, 2, 2, 4, 0)))
        cur = "USD"
        lot_date = self.date()
        label = None
        style = r.random()
        if style < 0.35:
            spec = f"{{{_fmt(cost)} {cur}}}"
        elif style < 0.5:
            total = _q(units * cost, 2)
            spec = f"{{{{{_fmt(total)} {cur}}}}}"
            cost = total / units
        elif style < 0.6:
            fee = self.amount(1, 10, 2)
            spec = f"{{{_fmt(cost)} # {_fmt(fee)} {cur}}}"
            cost = cost + fee / units
        elif style < 0.72:
            lot_date = (_dt.date(2023, 6, 1) + _dt.timedelta(days=r.randint(0, 200))).isoformat()
            spec = f"{{{_fmt(cost)} {cur}, {lot_date}}}"
        elif style < 0.85:
            self.labels += 1
            label = f"lot{self.labels}"
            spec = f'{{{_fmt(cost)} {cur}, "{label}"}}'
        elif style < 0.93:
            # An empty cost on a purchase takes the price's number, so the
            # cash posting must state its amount: two unknowns otherwise.
            spec = f"{{}} @ {_fmt(cost)} {cur}"
        else:
            self.labels += 1
            label = f"lot{self.labels}"
            spec = f'{{{_fmt(cost)} {cur}, {lot_date}, "{label}"}}'
        if r.random() < 0.2 and "@" not in spec:
            spec += f" @ {_fmt(self.amount(5, 300, 2))} {cur}"
        cash = units * cost
        if r.random() < 0.6 and not spec.startswith("{}"):
            posts = [f"  {account}  {_fmt(units)} {comm} {spec}", "  Assets:Cash"]
        else:
            shown = _q(cash, 2)
            posts = [
                f"  {account}  {_fmt(units)} {comm} {spec}",
                f"  Assets:Cash  -{_fmt(shown)} USD",
            ]
            cash = shown
        if r.random() < 0.2:
            posts.insert(1, "  Expenses:Fees  1.00 USD")
            if posts[-1] != "  Assets:Cash":
                posts[-1] = f"  Assets:Cash  -{_fmt(cash + 1)} USD"
            cash += 1
        self.txn(f"buy {comm}", posts)
        self.lots.setdefault(account, []).append(Lot(units, comm, cost, cur, lot_date, label))
        self.add_cash("Assets:Cash", "USD", -cash)
        self.unsure.add("Assets:Cash")

    def _pick(self, method: str, lots: list[Lot]) -> list[Lot]:
        if method in ("LIFO",):
            return list(reversed(lots))
        if method == "HIFO":
            return sorted(lots, key=lambda x: -x.cost)
        return list(lots)

    def sell(self, account: str | None = None, *, fault: str | None = None) -> bool:
        r = self.r
        candidates = [a for a, ls in self.lots.items() if any(x.units > 0 for x in ls)]
        if account is None:
            if not candidates:
                return False
            account = r.choice(sorted(candidates))
        method = self.opened.get(account) or "STRICT"
        comms = sorted({x.commodity for x in self.lots.get(account, []) if x.units > 0})
        if not comms:
            return False
        comm = r.choice(comms)
        lots = self.held(account, comm)
        price = self.amount(5, 320, 2)
        total = sum((x.units for x in lots), Decimal(0))
        whole = r.random() < 0.35
        if fault == "oversell":
            units = total + Decimal(r.randint(1, 5))
        elif whole:
            units = total
        else:
            units = min(total, Decimal(r.randint(1, max(1, int(total)))))
            if units <= 0:
                units = total
        # The cost spec of the reduction.
        style = r.random()
        if fault == "no-lot":
            spec = "{999.99 USD}"
        elif fault == "ambiguous":
            spec = "{}"
        elif method in ("STRICT", "STRICT_WITH_SIZE") and len(lots) > 1 and not whole:
            lot = r.choice(lots)
            units = min(units, lot.units)
            if lot.label and style < 0.4:
                spec = f'{{"{lot.label}"}}'
            elif style < 0.7:
                spec = (
                    f"{{{_fmt(lot.cost)} USD, {lot.date}}}"
                    if lot.cost == _q(lot.cost, 4)
                    else f"{{{lot.date}}}"
                )
            else:
                spec = f"{{{lot.date}}}" if sum(x.date == lot.date for x in lots) == 1 else "{}"
                if spec == "{}":
                    units = total
        elif method == "NONE":
            # NONE matches no lot, so `{}` names no cost: state one (a lot's).
            spec = f"{{{_fmt(_q(lots[0].cost, 4))} USD}}"
        elif style < 0.55:
            spec = "{}"
        elif (
            style < 0.7 and len({x.cost for x in lots}) == 1 and lots[0].cost == _q(lots[0].cost, 4)
        ):
            spec = f"{{{_fmt(lots[0].cost)} USD}}"
        elif style < 0.8:
            spec = "{USD}"
        else:
            spec = "{}"
        price_s = (
            f"@ {_fmt(price)} USD" if r.random() < 0.85 else f"@@ {_fmt(_q(price * units, 2))} USD"
        )
        proceeds = _q(price * units, 2)
        gains = r.random()
        posts = [f"  {account}  -{_fmt(units)} {comm} {spec} {price_s}"]
        if gains < 0.6:
            posts += [f"  Assets:Cash  {_fmt(proceeds)} USD", "  Income:Gains"]
        elif gains < 0.8:
            posts += (
                ["  Assets:Cash", "  Income:Gains  0 USD"]
                if r.random() < 0.2
                else [
                    f"  Assets:Cash  {_fmt(proceeds)} USD",
                    "  Income:Gains  ",
                ]
            )
        else:
            posts += [
                f"  Assets:Cash  {_fmt(proceeds)} USD",
                "  Income:Gains",
                "  Expenses:Fees  0.00 USD",
            ]
        self.txn(f"sell {comm}", [p.rstrip() for p in posts])
        # Update the model.
        left = units
        for lot in self._pick(method, lots):
            take = min(left, lot.units)
            lot.units -= take
            left -= take
            if not left:
                break
        self.add_cash("Assets:Cash", "USD", proceeds)
        self.unsure.add("Assets:Cash")
        self.unsure.add(account)
        return True

    def price(self) -> None:
        comm = self.r.choice((*COMMODITIES, "EUR"))
        self.emit(
            f"{self.date()} price {comm}  {_fmt(self.amount(1, 300, self.r.choice((2, 4))))} USD"
        )

    def balance(self, account: str = "Assets:Cash", *, off: Decimal = Decimal(0)) -> None:
        cur = "EUR" if account.endswith("EUR") else "USD"
        # Checked at the start of its day: after every transaction so far.
        self.day += 1
        n = self.cash.get((account, cur), Decimal(0)) + off
        if account in self.unsure and not off:
            # The model's figure may be off by interpolation rounding: assert
            # with a tolerance, or not at all.
            if self.r.random() < 0.5:
                return
            self.emit(f"{self.date()} balance {account}  {_fmt(_q(n, 2))} ~ 0.05 {cur}")
            return
        places = (
            max(2, -n.as_tuple().exponent) if n == n.to_integral_value() else -n.as_tuple().exponent
        )
        shown = _q(n, places) if places >= 0 else n
        if self.r.random() < 0.25:
            self.emit(f"{self.date()} balance {account}  {_fmt(shown)} ~ 0.01 {cur}")
        else:
            self.emit(f"{self.date()} balance {account}  {_fmt(shown)} {cur}")

    def pad(self, account: str = "Assets:Bank:Savings", *, cost: bool = False) -> None:
        r = self.r
        self.open(account, "USD" if r.random() < 0.3 else "")
        self.open("Equity:Opening")
        target = self.amount(10, 5000, r.choice((0, 2, 2)))
        self.emit(f"{self.date()} pad {account} Equity:Opening")
        # A balance is checked at the start of its day, so it must come at
        # least a day after the pad it consumes.
        self.tick()
        self.day += 1
        self.emit(f"{self.date()} balance {account}  {_fmt(target)} USD")
        self.cash[(account, "USD")] = target
        if r.random() < 0.3:
            self.tick()
            self.day += 1
            target2 = target + self.amount(1, 100, 2)
            self.emit(f"{self.date()} pad {account} Equity:Opening")
            self.day += r.choice((1, 3))
            self.emit(f"{self.date()} balance {account}  {_fmt(target2)} USD")
            self.cash[(account, "USD")] = target2

    # -- faults ---------------------------------------------------------------

    def fault(self, kind: str) -> None:
        r = self.r
        self.faulted = True
        if kind == "oversell":
            if not self.sell(fault="oversell"):
                self.buy()
                self.tick()
                self.sell(fault="oversell")
        elif kind == "unbalanced":
            self.txn("unbalanced", ["  Expenses:Food  10.00 USD", "  Assets:Cash  -9.00 USD"])
            self.unsure.add("Assets:Cash")
        elif kind == "unbalanced-small":
            self.txn("unbalanced", ["  Expenses:Food  10.00 USD", "  Assets:Cash  -9.99 USD"])
            self.unsure.add("Assets:Cash")
        elif kind == "balance-off":
            self.balance("Assets:Cash", off=Decimal(r.choice(("0.01", "1", "0.004", "100"))))
        elif kind == "unopened":
            self.txn("unopened", ["  Expenses:Nowhere  5.00 USD", "  Assets:Cash  -5.00 USD"])
            self.add_cash("Assets:Cash", "USD", Decimal(-5))
        elif kind == "after-close":
            self.open("Assets:Old")
            self.tick()
            self.emit(f"{self.date()} close Assets:Old")
            self.day += 1
            self.txn("after close", ["  Assets:Old  5.00 USD", "  Assets:Cash  -5.00 USD"])
            self.add_cash("Assets:Cash", "USD", Decimal(-5))
        elif kind == "currency-constraint":
            self.open("Assets:UsdOnly", "USD")
            self.txn(
                "wrong currency", ["  Assets:UsdOnly  5.00 EUR", "  Assets:Bank:EUR  -5.00 EUR"]
            )
            self.add_cash("Assets:Bank:EUR", "EUR", Decimal(-5))
        elif kind == "ambiguous":
            acct = self.broker("STRICT")
            self.buy(acct)
            self.tick()
            self.buy(acct)
            self.tick()
            self.sell(acct, fault="ambiguous")
        elif kind == "two-elided":
            self.txn(
                "two elided", ["  Expenses:Food  5.00 USD", "  Assets:Cash", "  Liabilities:Card"]
            )
            self.unsure |= {"Assets:Cash", "Liabilities:Card"}
        elif kind == "no-lot":
            if not self.sell(fault="no-lot"):
                self.buy()
                self.tick()
                self.sell(fault="no-lot")
        elif kind == "pad-unused":
            self.open("Assets:Bank:Idle")
            self.open("Equity:Opening")
            self.emit(f"{self.date()} pad Assets:Bank:Idle Equity:Opening")
            self.day += 1
            self.emit(f"{self.date()} balance Assets:Bank:Idle  0 USD")
        elif kind == "pad-cost":
            acct = self.broker(r.choice(("FIFO", "STRICT")))
            self.open("Equity:Opening")
            self.emit(f"{self.date()} pad {acct} Equity:Opening")
            self.day += 1
            self.emit(f"{self.date()} balance {acct}  5 HOOL")
        elif kind == "duplicate-open":
            self.emit(f"{self.date()} open Assets:Cash")


#: The configuration a plugin needs (beancount 3.2.3's `currency_accounts`
#: and `commodity_attr` fail without one).
PLUGIN_CONFIG = {
    "currency_accounts": "Equity:CurrencyAccounts",
    "commodity_attr": "{'name': None}",
}


def _plugin_line(name: str) -> str:
    config = PLUGIN_CONFIG.get(name)
    tail = f' "{config}"' if config else ""
    return f'plugin "beancount.plugins.{name}"{tail}'


def _header(
    m: Model, *, options: list[str] | None = None, plugins: list[str] | None = None
) -> None:
    r = m.r
    for o in options or ():
        m.emit(o)
    for p in plugins or ():
        m.emit(_plugin_line(p))
    if options or plugins:
        m.emit("")
    m.open("Assets:Cash", "USD" if r.random() < 0.4 else "")
    m.open("Assets:Bank:EUR", "EUR" if r.random() < 0.4 else "")
    m.open("Liabilities:Card")
    m.open("Income:Salary")
    m.open("Income:Gains")
    for e in ("Expenses:Food", "Expenses:Fees", "Expenses:Rent"):
        m.open(e)
    m.emit("")


def _options(r: random.Random, *, included: bool = False) -> list[str]:
    """Options for a file; `included` leaves out `display_precision`, which
    beancount 3.2.3 cannot merge from an included file (it raises)."""
    out = []
    if r.random() < 0.4:
        out.append(f'option "operating_currency" "{r.choice(("USD", "EUR"))}"')
        if r.random() < 0.3:
            out.append('option "operating_currency" "EUR"')
    if r.random() < 0.2:
        out.append(f'option "booking_method" "{r.choice(METHOD_DRAW)}"')
    if r.random() < 0.15:
        out.append(
            f'option "inferred_tolerance_default" "{r.choice(("USD", "*"))}:{r.choice(("0.01", "0.005", "0.1"))}"'
        )
    if r.random() < 0.1:
        out.append(f'option "tolerance_multiplier" "{r.choice(("0.6", "1.1", "0.5"))}"')
    if r.random() < 0.1:
        out.append('option "infer_tolerance_from_cost" "TRUE"')
    if r.random() < 0.05 and not included:
        out.append('option "display_precision" "USD:0.01"')
    return out


def _body(m: Model, steps: int, weights: dict[str, float]) -> None:
    r = m.r
    names = sorted(weights)
    total = sum(weights.values())
    for _ in range(steps):
        x = r.random() * total
        for name in names:
            x -= weights[name]
            if x <= 0:
                break
        m.tick()
        if name == "salary":
            m.salary()
        elif name == "expense":
            m.expense()
        elif name == "fx":
            m.fx()
        elif name == "buy":
            m.buy()
        elif name == "sell":
            if not m.sell():
                m.buy()
        elif name == "price":
            m.price()
        elif name == "balance":
            m.balance(
                r.choice(("Assets:Cash", "Assets:Cash", "Assets:Bank:EUR", "Liabilities:Card"))
            )
        elif name == "pad":
            m.pad(r.choice(("Assets:Bank:Savings", "Assets:Bank:Other")))


def _maybe_fault(m: Model, share: float = 0.2) -> None:
    if m.r.random() < share:
        m.tick()
        m.fault(m.r.choice(FAULTS))


def _text(m: Model) -> str:
    text = "\n".join(m.lines).rstrip("\n") + "\n"
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text


W_LOTS = {
    "salary": 1.0,
    "expense": 0.6,
    "fx": 0.4,
    "buy": 3.0,
    "sell": 3.0,
    "price": 0.4,
    "balance": 0.4,
    "pad": 0.1,
}
W_PADS = {
    "salary": 1.0,
    "expense": 2.0,
    "fx": 1.0,
    "buy": 0.5,
    "sell": 0.4,
    "price": 0.2,
    "balance": 2.0,
    "pad": 1.5,
}
W_PLUG = {
    "salary": 1.0,
    "expense": 1.0,
    "fx": 0.6,
    "buy": 1.5,
    "sell": 1.5,
    "price": 0.8,
    "balance": 0.6,
    "pad": 0.4,
}


def _ledger_s1(r: random.Random) -> Ledger:
    m = Model(r)
    _header(m, options=_options(r) if r.random() < 0.3 else [])
    m.salary()
    _body(m, r.randint(3, 10), W_LOTS)
    _maybe_fault(m)
    return Ledger(_text(m))


def _ledger_s2(r: random.Random) -> Ledger:
    m = Model(r)
    _header(m, options=_options(r) if r.random() < 0.6 else [])
    m.salary()
    _body(m, r.randint(3, 10), W_PADS)
    if r.random() < 0.7:
        m.tick()
        m.balance("Assets:Cash")
    _maybe_fault(m)
    return Ledger(_text(m))


def _plugins(r: random.Random, k: int) -> list[str]:
    out: list[str] = []
    for _ in range(k):
        p = r.choice(PLUGINS)
        if p not in out:
            out.append(p)
    return out


def _ledger_s4(r: random.Random) -> Ledger:
    m = Model(r)
    plugins = _plugins(r, r.randint(1, 3))
    opts = _options(r) if r.random() < 0.3 else []
    if "currency_accounts" in plugins and r.random() < 0.5:
        opts.append('option "operating_currency" "USD"')
    _header(m, options=opts, plugins=plugins)
    if "auto_accounts" in plugins or "auto" in plugins:
        # Let the plugin open what the body uses: drop some opens.
        m.lines = [ln for ln in m.lines if not (" open " in ln and r.random() < 0.5)]
    strict = {"commodity_attr", "check_commodity", "pedantic"} & set(plugins)
    if strict and r.random() < 0.85:
        # Declare the commodities (with the attribute `commodity_attr` is
        # configured to require), so most such ledgers are valid.
        for c in ("USD", "EUR", *COMMODITIES):
            m.emit(f"2024-01-01 commodity {c}", f'  name: "{c.lower()}"')
    m.salary()
    _body(m, r.randint(3, 9), W_PLUG)
    if "check_closing" in plugins:
        # A position moved in, then out with `closing: TRUE`: the plugin's
        # zero assertion the next day holds.
        m.open("Assets:Temp")
        m.tick()
        m.txn("park", ["  Assets:Temp  5.00 USD", "  Assets:Cash  -5.00 USD"])
        m.tick()
        m.txn(
            "unpark", ["  Assets:Temp  -5.00 USD", "    closing: TRUE", "  Assets:Cash  5.00 USD"]
        )
    if {"nounused", "pedantic"} & set(plugins) and r.random() < 0.85:
        # Use every account the header opened.
        m.tick()
        m.txn(
            "touch",
            [
                "  Expenses:Food  0.01 USD",
                "  Expenses:Fees  0.01 USD",
                "  Expenses:Rent  0.01 USD",
                "  Income:Gains  0.01 USD",
                "  Liabilities:Card  -0.04 USD",
            ],
        )
    if "close_tree" in plugins or "check_drained" in plugins:
        m.tick()
        m.emit(f"{m.date()} close Expenses:Rent")
    _maybe_fault(m)
    return Ledger(_text(m))


def _ledger_s3(r: random.Random) -> Ledger:
    """A main file that includes two or three others, each with its share of
    the options, plugins, opens and transactions."""
    m = Model(r)
    n_files = r.randint(1, 3)
    names = [r.choice(("accounts", "2024/q1", "trades", "bank"))]
    for _ in range(n_files - 1):
        nm = r.choice(("2024/q2", "prices", "extra", "sub/more"))
        if nm not in names:
            names.append(nm)
    paths = [f"{nm}.beancount" for nm in names]
    main_opts = _options(r) if r.random() < 0.6 else []
    main_plugins = _plugins(r, 1) if r.random() < 0.25 else []
    _header(m, options=main_opts, plugins=main_plugins)
    body_main = list(m.lines)
    files: dict[str, str] = {}
    for path in paths:
        m.lines = []
        if r.random() < 0.4:
            for o in _options(r, included=True) or [
                f'option "operating_currency" "{r.choice(("USD", "EUR", "CAD"))}"'
            ]:
                m.emit(o)
        if r.random() < 0.1:
            # beancount ignores a plugin an included file declares; a share of
            # ledgers exercises that all the same.
            for p in _plugins(r, 1):
                m.emit(_plugin_line(p))
        if r.random() < 0.3:
            # The same lot account opened and traded in its own file.
            m.broker()
        _body(m, r.randint(2, 6), W_LOTS if "trades" in path else W_PADS)
        files[path] = _text(m) if m.lines else "\n"
    m.lines = body_main
    includes = [f'include "{p}"' for p in paths]
    where = r.random()
    if where < 0.5:
        m.lines = [*includes, "", *m.lines]
    else:
        m.lines = [*m.lines, "", *includes]
    m.tick()
    m.day += 30
    m.salary()
    if r.random() < 0.5:
        m.balance("Assets:Cash")
    _maybe_fault(m)
    return Ledger(_text(m), files)


def _ledger_mix(r: random.Random) -> Ledger:
    return r.choice((_ledger_s1, _ledger_s2, _ledger_s3, _ledger_s4))(r)


def _collect(fn, seed: int, n: int) -> list[Ledger]:
    r = random.Random(seed)
    out: dict[str, Ledger] = {}
    attempts = 0
    while len(out) < n:
        attempts += 1
        if attempts > 20 * n + 1000:
            raise RuntimeError("generator cannot produce enough distinct ledgers")
        led = fn(r)
        out.setdefault(ledger_id(led), led)
    return [out[k] for k in sorted(out)]


def s1(seed: int, n: int) -> list[Ledger]:
    return _collect(_ledger_s1, seed, n)


def s2(seed: int, n: int) -> list[Ledger]:
    return _collect(_ledger_s2, seed, n)


def s3(seed: int, n: int) -> list[Ledger]:
    return _collect(_ledger_s3, seed, n)


def s4(seed: int, n: int) -> list[Ledger]:
    return _collect(_ledger_s4, seed, n)


def smix(seed: int, n: int) -> list[Ledger]:
    return _collect(_ledger_mix, seed, n)


SEMANTIC_GENERATORS = {
    g.name: g
    for g in (
        Generator("s1", s1, "lots and booking: buys and sells under every method"),
        Generator("s2", s2, "pads, balances, tolerances, precision and rounding"),
        Generator("s3", s3, "multi-file: includes, options and plugins across files"),
        Generator("s4", s4, "beancount's built-in plugins"),
        Generator("smix", smix, "a mix of s1-s4"),
    )
}
