# RFC-0000: Lot consumption ordering for interchangeable lots

- **RFC Number**: 0000 (assigned upon acceptance)
- **Author(s)**: rustledger maintainers
- **Status**: Draft
- **Created**: 2026-08-24
- **Updated**: 2026-08-24

## Summary

`core/model/lot.md` defines FIFO and LIFO as sorting matching positions by
acquisition **date**, and says positions "are merged only when ALL attributes
match exactly". Neither statement determines what happens when two positions
share a sort key. This RFC makes the merging rule biconditional and specifies
the ordering of equal-keyed positions, so that a reduction's outcome depends
only on facts the model records.

## Motivation

The specification is silent in two places, and implementations have filled the
silence differently. The result is that the same purchases produce different
cost bases.

### The gap is observable, and it moves tax figures

Three purchases, one date, two distinct costs. The lots labelled A and C are
identical in every attribute the model records: commodity, cost number, cost
currency, acquisition date and label.

```beancount
option "booking_method" "FIFO"
2020-01-01 open Assets:Stock  ACME
2020-01-01 open Assets:Cash   USD
2020-01-01 open Income:Gains  USD

2020-01-02 * "A"
  Assets:Stock  10 ACME {10.00 USD}
  Assets:Cash  -100.00 USD

2020-01-02 * "B"
  Assets:Stock  10 ACME {20.00 USD}
  Assets:Cash  -200.00 USD

2020-01-02 * "C"
  Assets:Stock  10 ACME {10.00 USD}
  Assets:Cash  -100.00 USD

2020-03-01 * "sell 15"
  Assets:Stock  -15 ACME {}
  Assets:Cash   300.00 USD
  Income:Gains
```

Writing the three acquisitions in each of the six possible orders, and
recording the remaining cost basis:

| order | rustledger 0.22 | Python Beancount 3.2.3 |
| --- | --- | --- |
| A B C | 200.00 | 250.00 |
| A C B | 250.00 | 250.00 |
| C A B | 250.00 | 250.00 |
| C B A | 200.00 | 250.00 |
| B A C | 150.00 | 150.00 |
| B C A | 150.00 | 150.00 |

Two conforming implementations, three outcomes against two, from identical
facts. Both implementations already order entries within a date by source
position, so this is not a disagreement about entry sequencing. It is a
disagreement about whether an interchangeable lot keeps its individual
identity when lots are consumed.

### Why the finer distinction is the wrong one

The distinction that separates `A B C` from `A C B` is where the unrelated lot
B was written relative to two lots that the model cannot tell apart. No
recorded attribute distinguishes those two ledgers.

That matters because it makes a reported figure depend on an editing accident.
Sorting a journal file, re-emitting it from an importer, or merging two
journals can change a cost basis and a realized gain without changing a single
fact about what was bought or sold.

External accounting practice does not supply the missing distinction either.
The default first-in-first-out rule in Treas. Reg. 1.1012-1(j)(3)(i) treats
units as sold "in order of time from the earliest **date** on which units
were acquired": the granularity is the date, and the rule says nothing about
sequence within one. IAS 2.23 and ASC 330 likewise treat FIFO as a cost-flow
assumption over _interchangeable_ items, reserving specific identification for
items that are "not ordinarily interchangeable". Under both, lots identical in
commodity, basis and acquisition date are interchangeable by definition, and
no authority assigns them an order.

So the specification cannot defer this to accounting standards. It has to
choose, and the choice should be the one that does not manufacture a
distinction from a difference the model does not record.

## Detailed Design

### Semantics

Add to `core/model/lot.md`.

**Definition.** Two positions are **interchangeable** when they agree on all
of: commodity, cost per unit, cost currency, acquisition date, and label.

**Rule 1 (merging is mandatory, not merely permitted).** Interchangeable
positions in the same inventory MUST be treated as a single position for every
purpose the specification defines, including reduction ordering, reported
holdings, and the identity of surviving lots. The existing sentence

> Positions are merged only when ALL attributes match exactly

states a necessary condition. It is replaced by a biconditional: positions are
merged **if and only if** all listed attributes match exactly.

**Rule 2 (ordering of equal sort keys).** Where an ordered booking method
(FIFO, LIFO, HIFO) compares positions whose sort key is equal, it MUST order
them by the acquisition that introduced each position, earliest first. The
sort key is the acquisition date for FIFO and LIFO, and the cost per unit for
HIFO. The merged position of Rule 1 is introduced by the earliest of the
acquisitions merged into it.

**Rule 3 (representation is unconstrained).** An implementation MAY retain
per-acquisition detail internally, provided no observable output depends on
it. Rules 1 and 2 constrain behaviour, not data structures.

Rule 2 is stated separately from Rule 1 because it is needed even when Rule 1
does not apply: two lots acquired on the same date at _different_ costs are
not interchangeable and do not merge, yet FIFO must still order them.

### Error Handling

None. This RFC changes no journal from accepted to rejected on its own account,
though see Compatibility: a non-conforming implementation will change which
ledgers it accepts when it adopts the rules.

### Examples

```beancount
; Rule 1: A and C are interchangeable, so the sell takes 10 from the merged
; 20-unit position at 10.00 and 5 from the 20.00 position, whichever order the
; three acquisitions are written in. Remaining basis is 250.00.
2020-01-02 * "A"
  Assets:Stock  10 ACME {10.00 USD}
  Assets:Cash  -100.00 USD
2020-01-02 * "B"
  Assets:Stock  10 ACME {20.00 USD}
  Assets:Cash  -200.00 USD
2020-01-02 * "C"
  Assets:Stock  10 ACME {10.00 USD}
  Assets:Cash  -100.00 USD
```

```beancount
; Rule 2 without Rule 1: same date, different costs, so no merging. FIFO
; cannot separate them by date and takes the earlier acquisition first.
2020-01-02 * "first"
  Assets:Stock  10 ACME {10.00 USD}
  Assets:Cash  -100.00 USD
2020-01-02 * "second"
  Assets:Stock  10 ACME {12.00 USD}
  Assets:Cash  -120.00 USD
```

```beancount
; Rule 1 does not reach across labels: these are NOT interchangeable and are
; consumed in acquisition order.
2020-01-02 * "morning"
  Assets:Stock  10 ACME {10.00 USD, "morning"}
  Assets:Cash  -100.00 USD
2020-01-02 * "afternoon"
  Assets:Stock  10 ACME {10.00 USD, "afternoon"}
  Assets:Cash  -100.00 USD
```

## Alternatives Considered

### Alternative 1: Order by full acquisition sequence

Consume lots strictly in the order acquired, never merging. This is
rustledger's current behaviour.

It has a real argument in its favour: it preserves information, and it is
consistent with treating source order within a date as meaningful, which both
implementations already do for entry sequencing.

Rejected because the information it preserves is not recorded anywhere the
model can appeal to. Dates are held at day resolution, so "B was acquired
between A and C" is not a fact the format captures; it is an artifact of
where the author typed a line. Making a cost basis depend on it means a
semantically null edit changes a tax figure, as the table above shows.

### Alternative 2: Leave it unspecified

Document that implementations may differ, as rustledger currently does in its
migration guide.

Rejected because the divergence is not confined to presentation. It changes
reported basis and realized gains, and it changes which ledgers load at all:
because merging changes which lots _survive_ a reduction, a later reduction
naming an explicit cost can find its lot drained under one rule and present
under the other. Implementations diverge in both directions on this, so
"unspecified" means a journal that loads under one conforming tool and fails
under another.

### Alternative 3: Specify merging but leave equal sort keys unspecified

Adopt Rule 1 alone. Rejected: Rule 1 does not reach lots that share a date but
differ in cost, which is a distinct and equally observable case. Leaving it
open would resolve the reported divergence while leaving its neighbour to be
settled by whichever way each implementation's sort happens to be stable.

## Compatibility

### Backwards Compatibility

This is a breaking change for implementations that do not already merge.

Ledgers whose acquisitions never repeat a lot identity within a date are
unaffected, which is the large majority.

For affected ledgers, reported cost basis, realized gains, and the acquisition
dates of surviving lots may change, and a reduction naming an explicit cost
may begin or cease to resolve. There is no syntax migration: the same journal
text books differently. Implementations adopting the rules should say so in
release notes and should consider naming the cause in the error raised when a
reduction can no longer be satisfied, since the arithmetic message alone gives
the reader nothing to search for.

### Forward Compatibility

An implementation that has not adopted these rules produces different numbers
rather than failing to parse. There is no syntax to ignore.

### Cross-Format Compatibility

Python Beancount 3.2.3 already conforms: its inventory is keyed on
`(currency, cost)` where cost carries number, currency, date and label, so
interchangeable lots are necessarily merged. Its equal-key ordering follows
from `sorted()` being stable, which satisfies Rule 2 in practice.

rustledger 0.22 does not conform to Rule 1; it keeps one position per
acquisition. It satisfies Rule 2.

Ledger and hledger track lots differently and are out of scope; this RFC
constrains formats that carry per-lot cost basis.

## Implementation Notes

An implementation that stores one slot per acquisition conforms by ordering
slots on `(sort key, earliest slot holding an interchangeable lot)` rather
than on `(sort key, own index)`, keeping per-acquisition provenance available
for diagnostics.

**That is not a one-line change, and an earlier draft of this RFC was wrong to
say so.** The ordering needs a map from lot identity to its earliest slot, and
where that map lives dominates the cost. Measured on rustledger 0.22 against a
20,000-transaction FIFO journal, where the unmodified build takes 21.9s:

| approach | 20,000 txns | versus baseline |
| --- | --- | --- |
| scan for the earliest match inside the sort comparator | 213s | 9.7x |
| build the map once per sort, and per incremental insert | 124s | 5.7x |
| carry the map in the ordered index and update it in place | 26.4s | 1.21x |

The first two are the quadratic shape this codebase twice removed. Only the
third is viable, and it does change the storage model: the index gains a
`identity -> earliest slot` map that must be populated on build, updated on
insert, and rebuilt when slot renumbering invalidates it.

Even then the remaining cost is real: 1.10x at 2,000 transactions and 1.21x at
20,000 on a booking-heavy shape. Implementers should budget for that rather
than expect it free. An implementation that merges eagerly at acquisition time
satisfies Rule 1 by construction and pays none of this.

Rule 3 still holds: conformance constrains behaviour, not representation. What
it does not promise is that conforming is cheap for every representation.

## Open Questions

1. Should Rule 1 extend to positions that are interchangeable except for
   acquisition date, where one carries no date at all? Both known
   implementations treat a date-less lot as distinct, but neither documents it.
2. Does Rule 2's "earliest acquisition" need a tie-break when two acquisitions
   occur in the same transaction? Both known implementations order by posting
   index within the transaction; this RFC does not currently say so.
3. Should the specification require implementations to make the merging
   observable in reports, or only in consumption ordering? Rule 1 as written
   requires the former.

## References

- `core/model/lot.md`, Inventory and Booking Methods sections
- Treas. Reg. 1.1012-1(j)(3)(i), default first-in-first-out rule for units
  held by a broker
- IAS 2.23 to 2.27, cost formulas and specific identification
- ASC 330, inventory cost-flow assumptions
- rustledger issue #2118, the divergence that prompted this RFC
- rustledger issue #2115, an equal-sort-key ordering defect fixed under
  Rule 2's reading before this RFC was written

## Changelog

- 2026-08-24: Initial draft
- 2026-08-24: Corrected Implementation Notes. The first draft claimed
  conforming was "a change to one comparison, not to the storage model". A
  prototype disproved it: the naive form is 9.7x slower on a 20,000
  transaction journal, and the viable form requires a maintained map in the
  index. Measurements added.

---

## Appendix A: Grammar

No grammar changes.

## Appendix B: Test Cases

```json
{
  "id": "lot-interchangeable-ordering-001",
  "description": "Interchangeable lots are consumed as one position regardless of the order the acquisitions are written",
  "rule": "RFC-0000 Rule 1",
  "variants": [
    {"order": ["A", "B", "C"]},
    {"order": ["A", "C", "B"]},
    {"order": ["C", "A", "B"]},
    {"order": ["C", "B", "A"]}
  ],
  "lots": {
    "A": {"units": 10, "cost": "10.00 USD", "date": "2020-01-02"},
    "B": {"units": 10, "cost": "20.00 USD", "date": "2020-01-02"},
    "C": {"units": 10, "cost": "10.00 USD", "date": "2020-01-02"}
  },
  "reduction": {"units": -15, "cost_spec": "{}", "date": "2020-03-01"},
  "expect": {
    "remaining": [
      {"units": 5, "cost": "10.00 USD"},
      {"units": 10, "cost": "20.00 USD"}
    ],
    "remaining_cost_basis": "250.00 USD"
  },
  "note": "All four variants MUST produce this result. An implementation ordering by full acquisition sequence returns 200.00 for A B C and C B A."
}
```

```json
{
  "id": "lot-equal-sort-key-ordering-002",
  "description": "Lots sharing an acquisition date but differing in cost are consumed earliest-acquisition-first under FIFO",
  "rule": "RFC-0000 Rule 2",
  "lots": [
    {"units": 10, "cost": "10.00 USD", "date": "2020-01-02", "acquired_position": 0},
    {"units": 10, "cost": "12.00 USD", "date": "2020-01-02", "acquired_position": 1}
  ],
  "reduction": {"units": -10, "cost_spec": "{}", "method": "FIFO"},
  "expect": {"consumed": [{"units": 10, "cost": "10.00 USD"}]}
}
```

```json
{
  "id": "lot-label-not-interchangeable-003",
  "description": "Labels make otherwise identical lots distinct, so Rule 1 does not merge them",
  "rule": "RFC-0000 Rule 1",
  "lots": [
    {"units": 10, "cost": "10.00 USD", "date": "2020-01-02", "label": "morning"},
    {"units": 10, "cost": "20.00 USD", "date": "2020-01-02"},
    {"units": 10, "cost": "10.00 USD", "date": "2020-01-02", "label": "afternoon"}
  ],
  "reduction": {"units": -15, "cost_spec": "{}", "method": "FIFO"},
  "expect": {
    "consumed": [
      {"units": 10, "cost": "10.00 USD", "label": "morning"},
      {"units": 5, "cost": "20.00 USD"}
    ]
  }
}
```
