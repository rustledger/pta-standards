# Core Data Model

This document provides an overview of the core data model for plain text accounting systems.

## Overview

The core model defines the fundamental types and structures that underpin all plain text accounting formats. These abstractions are format-agnostic and capture the essential concepts of double-entry bookkeeping.

## Model Components

| Component | Document | Description |
|-----------|----------|-------------|
| Account | [account.md](account.md) | Named containers for tracking value |
| Amount | [amount.md](amount.md) | Quantity paired with commodity |
| Commodity | [commodity.md](commodity.md) | Unit of measure (currencies, stocks, etc.) |
| Posting | [posting.md](posting.md) | Single leg of a transaction |
| Transaction | [transaction.md](transaction.md) | Balanced collection of postings |
| Lot | [lot.md](lot.md) | Position with cost basis tracking |
| Price | [price.md](price.md) | Exchange rate between commodities |
| Metadata | [metadata.md](metadata.md) | Key-value annotations |
| Journal | [journal.md](journal.md) | Collection of directives |
| Ordering | [ordering.md](ordering.md) | Directive sequencing rules |

## Fundamental Relationships

```
Journal
  └── Directive[]
        ├── Transaction
        │     ├── Date
        │     ├── Payee?
        │     ├── Narration
        │     ├── Tags[]
        │     ├── Links[]
        │     ├── Metadata{}
        │     └── Posting[]
        │           ├── Account
        │           ├── Amount?
        │           │     ├── Number
        │           │     └── Commodity
        │           ├── Cost?
        │           │     ├── Number
        │           │     ├── Commodity
        │           │     ├── Date?
        │           │     └── Label?
        │           ├── Price?
        │           └── Metadata{}
        ├── Open
        ├── Close
        ├── Balance
        ├── Pad
        ├── Commodity
        ├── Price
        ├── Event
        ├── Note
        ├── Document
        ├── Query
        └── Custom
```

## Core Invariants

### Double-Entry Balance

Every transaction MUST balance: the sum of all posting amounts equals zero.

```
sum(posting.weight for posting in transaction.postings) == 0
```

### Account Lifecycle

Accounts MUST be opened before use and MAY be closed:

```
open_date <= first_posting_date <= last_posting_date <= close_date
```

### Chronological Ordering

Directives are processed in date order:

```
directive[n].date <= directive[n+1].date
```

### Single Currency Amounts

An amount always pairs exactly one number with one commodity:

```
Amount = (Number, Commodity)
```

### Cost Basis Tracking

Positions with cost maintain lot information:

```
Position = Amount | (Amount, CostBasis)
CostBasis = (Amount, Date?, Label?)
```

## Type Categories

### Primitive Types

| Type | Definition | Example |
|------|------------|---------|
| Date | Calendar date (YYYY-MM-DD) | `2024-01-15` |
| Number | Decimal number | `123.45` |
| String | Text value | `"Grocery Store"` |
| Flag | Transaction status | `*` (cleared) or `!` (pending) |

### Composite Types

| Type | Components |
|------|------------|
| Amount | Number + Commodity |
| Position | Amount + optional Cost |
| Posting | Account + Position + optional Price + Metadata |
| Transaction | Date + Flag + optional Payee + Narration + Postings + Metadata |

### Collection Types

| Type | Description |
|------|-------------|
| Inventory | Collection of positions in an account |
| Journal | Collection of directives |
| Price Database | Historical commodity prices |

## Cross-Format Compatibility

These core concepts map to specific syntax in each format:

| Concept | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Account separator | `:` | `:` | `:` |
| Amount format | `100 USD` | `$100` or `100 USD` | `$100` or `100 USD` |
| Cost syntax | `{100 USD}` | `{=$100}` or `{100 USD}` | `{100 USD}` |
| Price syntax | `@ 1.50 USD` | `@ $1.50` | `@ 1.50 USD` |
| Metadata | `key: "value"` | `; key: value` | `; key: value` |

## Design Principles

### 1. Immutability

Directive data is immutable once parsed. Modifications create new instances.

### 2. Precision

Decimal arithmetic preserves exact values. No floating-point approximations.

### 3. Completeness

All transaction information is explicit or deterministically derivable.

### 4. Locality

Errors reference specific source locations (file, line, column).

### 5. Determinism

Same input always produces same output. No hidden state or side effects.

## See Also

- [Types](../types/README.md) - Primitive type specifications
- [Numerics](../numerics/README.md) - Decimal arithmetic rules
- [Formal](../formal/) - Formal specifications in Alloy/TLA+
