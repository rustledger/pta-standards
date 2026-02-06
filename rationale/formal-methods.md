# Formal Methods

This document explains why we use formal specification languages and which ones we chose.

## Context

Formal methods use mathematical notation to specify system behavior precisely. They can catch ambiguities and errors that prose specifications miss.

## Decision

We use two formal specification languages:

1. **Alloy** - For structural properties and constraints
2. **TLA+** - For behavioral properties and state machines

## Rationale

### Why Formal Methods?

Plain text specifications can be:

- **Ambiguous** - "The balance should be correct"
- **Incomplete** - Missing edge cases
- **Inconsistent** - Contradictory requirements

Formal specifications are:

- **Precise** - Mathematical meaning
- **Analyzable** - Tools can check properties
- **Executable** - Can generate test cases

### Example: Balance Checking

**Prose specification**:
> "A transaction must balance."

**Questions prose doesn't answer**:
- Balance to exactly zero or within tolerance?
- Per-currency or total?
- Before or after rounding?

**Formal specification (Alloy)**:
```alloy
pred balanced[t: Transaction] {
  all c: Currency |
    let weights = { p: t.postings | p.weight.currency = c } |
    abs[sum[weights.amount]] <= tolerance[c]
}
```

This precisely defines: per-currency, within tolerance, on weights.

### Why These Two Languages?

#### Alloy

**Best for**:
- Structural properties
- Relational constraints
- Finding counterexamples
- Small scope exhaustive checking

**Use cases in PTA**:
- Account hierarchy constraints
- Posting structure validation
- Inventory invariants
- Booking method properties

**Example**:
```alloy
sig Account {
  parent: lone Account,
  children: set Account
}

fact NoSelfParent {
  no a: Account | a in a.^parent
}

fact ChildrenInverse {
  all a: Account | a.children = { c: Account | c.parent = a }
}
```

#### TLA+

**Best for**:
- State machine behavior
- Temporal properties
- Concurrent systems
- Sequences of operations

**Use cases in PTA**:
- Account lifecycle (open → active → closed)
- Transaction processing order
- Balance assertion timing
- Plugin execution order

**Example**:
```tla
VARIABLES accounts, balances

TypeInvariant ==
  /\ accounts \subseteq ACCOUNT
  /\ balances \in [accounts -> [CURRENCY -> Int]]

Open(a) ==
  /\ a \notin accounts
  /\ accounts' = accounts \cup {a}
  /\ balances' = balances @@ (a :> EmptyBalance)

Close(a) ==
  /\ a \in accounts
  /\ balances[a] = EmptyBalance
  /\ accounts' = accounts \ {a}
  /\ balances' = [acc \in accounts' |-> balances[acc]]
```

## Alternatives Considered

### Alternative 1: No Formal Methods

**Approach**: Rely on prose and tests only.

**Problems**:
- Ambiguity persists
- Missing edge cases
- No exhaustive checking

**Rejected because**: Formal methods catch issues prose misses.

### Alternative 2: Z Notation

**Approach**: Use Z specification language.

**Problems**:
- Steep learning curve
- Limited tool support
- Academic focus

**Rejected because**: Alloy is more accessible with better tooling.

### Alternative 3: B Method

**Approach**: Use B or Event-B.

**Problems**:
- Complex notation
- Primarily for verified systems
- Overkill for specifications

**Rejected because**: Too heavyweight for documentation purposes.

### Alternative 4: Coq/Lean

**Approach**: Use proof assistants.

**Problems**:
- Very steep learning curve
- Requires proof engineering
- Too time-intensive

**Rejected because**: Specification, not verification, is the goal.

### Alternative 5: Alloy Only

**Approach**: Use only Alloy.

**Problems**:
- Alloy struggles with temporal properties
- State machines are awkward

**Rejected because**: TLA+ handles behavioral specs better.

### Alternative 6: TLA+ Only

**Approach**: Use only TLA+.

**Problems**:
- TLA+ is verbose for structural constraints
- Relational reasoning is awkward

**Rejected because**: Alloy handles structural specs better.

## Implementation

### File Organization

```
core/formal/
├── inventory.als           # Alloy: inventory invariants
├── balance-equation.als    # Alloy: balance checking
├── booking/
│   ├── fifo.als           # Alloy: FIFO booking
│   ├── lifo.als           # Alloy: LIFO booking
│   └── average.als        # Alloy: average cost
└── tla/
    ├── AccountLifecycle.tla    # TLA+: account states
    ├── TransactionOrder.tla    # TLA+: processing order
    └── PluginExecution.tla     # TLA+: plugin chain
```

### Scope

Formal specifications cover:

| Area | Language | Why |
|------|----------|-----|
| Inventory model | Alloy | Structural constraints |
| Booking methods | Alloy | Algorithmic properties |
| Balance equation | Alloy | Mathematical invariant |
| Account lifecycle | TLA+ | State transitions |
| Directive ordering | TLA+ | Temporal sequence |
| Plugin execution | TLA+ | Execution model |

### Verification Level

We use formal methods for:

1. **Specification clarity** - Primary goal
2. **Counterexample finding** - Find edge cases
3. **Property checking** - Verify invariants

We do NOT use them for:

- Verified implementation (too costly)
- Complete proofs (diminishing returns)

## Consequences

### Benefits

1. **Precision** - Unambiguous specifications
2. **Edge case discovery** - Alloy finds counterexamples
3. **Behavioral clarity** - TLA+ models state machines
4. **Test generation** - Derive tests from specs
5. **Documentation** - Formal models explain behavior

### Costs

1. **Learning curve** - Contributors need to learn languages
2. **Maintenance** - Specs must track prose changes
3. **Tool dependencies** - Alloy Analyzer, TLC required
4. **Limited audience** - Not all readers know formal methods

### Mitigation

- Provide prose alongside formal specs
- Include comments explaining formal notation
- Link to learning resources
- Keep formal specs focused on complex areas

## Usage Guidance

### For Specification Authors

Use formal methods when:

- Prose is ambiguous
- Edge cases are subtle
- Algorithm correctness matters

```alloy
// Document the property being specified
// Balance checking: sum of weights per currency must be near zero
pred balanced[t: Transaction] {
  // For each currency...
  all c: Currency | ...
}
```

### For Implementers

Use formal specs to:

- Understand precise requirements
- Generate test cases
- Verify algorithm correctness

```python
# Implementing the Alloy spec for balanced
def is_balanced(transaction: Transaction) -> bool:
    for currency in get_currencies(transaction):
        total = sum(p.weight for p in transaction.postings
                    if p.weight.currency == currency)
        if abs(total) > get_tolerance(currency):
            return False
    return True
```

### For Readers

If unfamiliar with formal methods:

1. Read the prose specification first
2. Use formal specs as precise reference
3. Focus on comments explaining intent
4. Try the Alloy Analyzer to explore models

## References

- [Alloy](https://alloytools.org/) - Alloy language and analyzer
- [TLA+](https://lamport.azurewebsites.net/tla/tla.html) - Leslie Lamport's TLA+
- [Software Abstractions](https://mitpress.mit.edu/books/software-abstractions) - Alloy textbook
- [Specifying Systems](https://lamport.azurewebsites.net/tla/book.html) - TLA+ textbook
