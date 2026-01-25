# ADR 0002: Alloy over TLA+

## Status

Accepted

## Context

Formal verification can catch specification bugs before implementation. Two popular tools:

- **TLA+**: Temporal logic, state machines, model checking
- **Alloy**: Relational logic, bounded model finding, visualization

Both can verify invariants like "debits equal credits" and "FIFO selects oldest lot."

## Decision

We will use **Alloy** for formal specifications.

## Consequences

**Positive:**
- Alloy's relational model maps well to accounting concepts
- Better visualization of counterexamples
- Simpler syntax for non-temporal properties
- Smaller learning curve

**Negative:**
- Less suitable for concurrent/temporal properties
- Smaller community than TLA+
- Bounded model finding (not exhaustive proof)

**Neutral:**
- `.als` files in `*/formal/` directories
- Can add TLA+ later if needed for temporal properties
