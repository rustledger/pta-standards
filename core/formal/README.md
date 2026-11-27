# Formal Verification

This directory contains formal specifications for verifying correctness of PTA implementations.

## Contents

### TLA+ Specifications (`tla/`)

TLA+ (Temporal Logic of Actions) specifications model and verify critical algorithms:

| File | Purpose |
|------|---------|
| `AccountStateMachine.tla` | Account lifecycle (open/close) state machine |
| `AVERAGECorrect.tla` | AVERAGE booking method correctness |
| `BuggyInventory.tla` | Counter-example for incorrect implementations |
| `ConcurrentAccess.tla` | Concurrent ledger access safety |
| `Conservation.tla` | Conservation of value (no money created/destroyed) |
| `DoubleEntry.tla` | Double-entry bookkeeping invariants |
| `FIFOCheck.tla` | FIFO booking verification |
| `FIFOCorrect.tla` | FIFO selects oldest lots correctly |
| `HIFOCorrect.tla` | HIFO (Highest-In-First-Out) correctness |
| `Interpolation.tla` | Missing amount interpolation |
| `LIFOCorrect.tla` | LIFO selects newest lots correctly |
| `MultiCurrency.tla` | Multi-currency transaction handling |
| `NONECorrect.tla` | NONE booking allows mixed inventories |
| `PluginCorrect.tla` | Plugin execution order and safety |
| `PriceDB.tla` | Price database consistency |
| `QueryExecution.tla` | BQL query execution semantics |
| `SimpleInventory.tla` | Basic inventory operations |
| `STRICTCorrect.tla` | STRICT booking requires unambiguous match |
| `ValidationCorrect.tla` | Validation phase ordering and completeness |

### Running TLA+ Specs

Install [TLA+ Toolbox](https://lamport.azurewebsites.net/tla/toolbox.html) or use command-line tools:

```bash
# Check a specification
tlc FIFOCorrect.tla

# With model constants
tlc -config FIFOCorrect.cfg FIFOCorrect.tla
```

### Key Properties Verified

1. **Booking Correctness**
   - FIFO always selects oldest matching lot
   - LIFO always selects newest matching lot
   - STRICT rejects ambiguous matches
   - AVERAGE maintains correct weighted average

2. **Conservation Laws**
   - Transaction balance: sum of weights = 0
   - No value created or destroyed

3. **Account Lifecycle**
   - Postings only to open accounts
   - No double-open or double-close
   - Close only when balance allows

4. **Concurrency Safety**
   - Multiple readers safe
   - Write operations serialize correctly

## Alloy Specifications

Alloy models (`*.als`) live beside the specs they formalize: this directory
(`inventory.als`, `balance_equation.als`, `booking/`, `reports/`),
`core/types/decimal.als`, and `formats/*/formal/`. Alloy provides relational
modeling suitable for structural properties.

The `Run Alloy` workflow runs every command of every model with Alloy 6.2:

```bash
python3 scripts/run_alloy.py --jar alloy.jar            # all models
python3 scripts/run_alloy.py --jar alloy.jar core/formal/inventory.als
```

A `check` passes when it finds no counterexample and a `run` when it finds an
instance (unless the command says `expect`). Commands known to fail are listed,
with the reason, in `scripts/alloy-known-failures.txt`. Module names cannot
contain `-`, so a model that another model `open`s must use `_` in its file name.

Alloy integers are small fixed-width two's complement numbers that wrap
around, and the analyzer's overflow guard does not reliably reject wrapped
sums. Models therefore scale example amounts down and bound magnitudes in the
premises of their checks; keep scopes small so CI stays fast.

See [ADR-0002](../../meta/adrs/0002-alloy-over-tlaplus.md) for rationale.

## Using Formal Specs

### For Implementers

Use these specs to:
- Understand precise semantics
- Generate test cases via model checking
- Verify your implementation matches the model

### For Spec Authors

When modifying specifications:
1. Run TLC model checker
2. Verify all invariants pass
3. Check for deadlock/livelock
4. Document any new assumptions

## References

- [TLA+ Home](https://lamport.azurewebsites.net/tla/tla.html)
- [Learn TLA+](https://learntla.com/)
- [TLC Model Checker](https://lamport.azurewebsites.net/tla/tools.html)
- [Alloy Analyzer](https://alloytools.org/)
