# Design Principles

This document describes the core design principles guiding the PTA Standards project.

## Overview

These principles inform all specification decisions. When facing trade-offs, we prioritize principles higher in this list.

## Principle 1: Human Readability

**Plain text accounting files should be readable by humans without specialized tools.**

### Rationale

- Users should understand their financial data by reading the file
- Debugging should be possible with a text editor
- Data should outlive any specific software

### Implications

- Syntax is designed for human comprehension, not parsing efficiency
- Verbose formats preferred over compact binary
- Self-documenting structures where possible

### Examples

```beancount
; Clear and readable
2024-01-15 * "Whole Foods" "Weekly groceries"
  Expenses:Food:Groceries    85.50 USD
  Assets:Checking

; Not this (hypothetical compact format)
; 20240115*WF:WG;E:F:G:85.50USD;A:C
```

## Principle 2: Data Integrity

**Financial data must be accurate and verifiable.**

### Rationale

- Accounting errors can have real-world consequences
- Users must trust their data
- Auditing requires confidence in data integrity

### Implications

- Double-entry balance enforcement
- Explicit error on ambiguity
- No silent data loss or corruption
- Deterministic processing

### Examples

```beancount
; Transaction MUST balance
2024-01-15 * "Purchase"
  Expenses:Food    100 USD
  Assets:Cash     -100 USD  ; Required for balance

; Unbalanced transaction = ERROR, not warning
```

## Principle 3: Longevity

**Data formats should remain usable for decades.**

### Rationale

- Financial records may need to be kept 7+ years (tax)
- Personal records span lifetimes
- Software comes and goes; data persists

### Implications

- Simple, stable formats
- Minimal dependencies on external systems
- Human-readable over machine-optimized
- Version compatibility considerations

### Examples

```
; A file from 2010 should still parse in 2030
; Avoid features that depend on:
; - External services
; - Specific software versions
; - Proprietary formats
```

## Principle 4: Interoperability

**Users should not be locked into a single tool.**

### Rationale

- Competition benefits users
- Different tools have different strengths
- Migration should be possible

### Implications

- Document multiple formats
- Define conversion paths
- Identify common subset
- Accept format differences

### Examples

```
; Same financial data expressible in multiple formats

; Beancount
2024-01-15 * "Purchase"
  Expenses:Food  100 USD
  Assets:Cash

; Ledger
2024/01/15 * Purchase
    Expenses:Food  $100
    Assets:Cash
```

## Principle 5: Correctness Over Convenience

**Prefer explicit correctness over implicit convenience.**

### Rationale

- Implicit behavior causes surprises
- Debugging implicit behavior is hard
- Financial data requires precision

### Implications

- Require explicit account opening
- No automatic categorization in spec
- Clear error messages over silent fixes

### Examples

```beancount
; Require explicit open
2024-01-01 open Assets:Checking

; Not: automatically create account on first use
; Because: typos would create unwanted accounts
```

## Principle 6: Progressive Complexity

**Simple things should be simple; complex things should be possible.**

### Rationale

- New users shouldn't face unnecessary complexity
- Power users need advanced features
- Complexity should be opt-in

### Implications

- Core syntax is minimal
- Advanced features build on core
- Sensible defaults

### Examples

```beancount
; Simple case: no cost tracking needed
2024-01-15 * "Groceries"
  Expenses:Food  100 USD
  Assets:Cash

; Complex case: full lot tracking when needed
2024-01-15 * "Stock purchase"
  Assets:Brokerage  10 AAPL {150.00 USD, 2024-01-15, "lot-1"}
  Assets:Cash      -1500 USD
```

## Principle 7: Explicit Over Implicit

**Prefer explicit specification over implicit convention.**

### Rationale

- Implicit rules are hard to discover
- Different implementations may have different implicit behavior
- Explicit is debuggable

### Implications

- Document all behavior
- Minimize implementation-defined behavior
- When implicit behavior exists, document it clearly

### Examples

```beancount
; Explicit: clearly states the balance
2024-01-15 balance Assets:Checking 1000 USD

; Not relying on implicit: "just trust the sum"
```

## Principle 8: Fail Fast

**Errors should be detected and reported as early as possible.**

### Rationale

- Early detection prevents cascading problems
- Users can fix issues while context is fresh
- Silent failures lead to data corruption

### Implications

- Validate at parse time when possible
- Clear, actionable error messages
- No "best effort" silent recovery

### Examples

```
; Parse error reported immediately
ERROR: Invalid date format
  --> ledger.beancount:42:1
   |
42 | 2024-13-45 * "Invalid"
   | ^^^^^^^^^^

; Not: silently skip invalid entries
```

## Principle 9: Composability

**Features should work well together.**

### Rationale

- Users combine features in unexpected ways
- Orthogonal features are easier to understand
- Composability enables power use

### Implications

- Features don't have hidden interactions
- Metadata works everywhere
- Plugins can transform any directive

### Examples

```beancount
; Tags + metadata + cost tracking all work together
2024-01-15 * "Stock purchase" #investment ^order-123
  lot-id: "tax-lot-2024-001"
  Assets:Brokerage  10 AAPL {150.00 USD}
  Assets:Cash
```

## Principle 10: Minimal Magic

**Behavior should be predictable from the source.**

### Rationale

- Magic (hidden behavior) confuses users
- Debugging magic is difficult
- Different implementations may have different magic

### Implications

- What you see is what you get
- No hidden transformations
- Plugins are explicit

### Examples

```beancount
; Explicit plugin loading
plugin "beancount.plugins.auto_accounts"

; Not: plugins that silently modify behavior
; based on file location or environment
```

## Applying Principles

When principles conflict, use this priority order:

1. **Data Integrity** - Never compromise correctness
2. **Human Readability** - Maintain understandability
3. **Longevity** - Preserve long-term usability
4. **Correctness Over Convenience** - Be explicit
5. **Everything else** - Balance based on context

## Evolution

These principles may evolve. Changes require:

1. RFC proposing the change
2. Community discussion
3. Clear rationale for modification
4. Documentation of the change
