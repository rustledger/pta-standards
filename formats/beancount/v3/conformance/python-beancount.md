# Python Beancount 3.x Conformance

This document tracks how the Python beancount implementation (v3.x) conforms to the Beancount v3 specification.

## Version Information

| Property | Value |
|----------|-------|
| Specification | Beancount v3 |
| Implementation | Python beancount |
| Tested Version | 3.2.0 |
| Last Updated | 2026-02-07 |

## Conformance Legend

| Symbol | Meaning |
|--------|---------|
| :white_check_mark: | Fully conformant |
| :warning: | Partial - missing features or minor deviations |
| :x: | Non-conformant - significant deviation from spec |
| :hourglass: | Spec undefined - awaiting clarification |

## Summary

| Area | Status | Notes |
|------|--------|-------|
| Lexical Structure | :white_check_mark: | Fully conformant |
| Directives | :white_check_mark: | Fully conformant |
| Amounts & Numbers | :white_check_mark: | Fully conformant |
| Accounts | :white_check_mark: | Fully conformant |
| Transactions | :warning: | Elision rule deviation |
| Costs | :warning: | Merge cost not implemented |
| Booking | :warning: | AVERAGE method not implemented |
| Balance Assertions | :white_check_mark: | Fully conformant |
| Tolerances | :white_check_mark: | Fully conformant |
| Metadata | :white_check_mark: | Fully conformant |
| Plugins | :white_check_mark: | Fully conformant |

---

## Detailed Conformance

### Transactions

#### Amount Elision

| Spec Requirement | Implementation | Status |
|------------------|----------------|--------|
| One elided posting per currency | One elided posting **total** | :hourglass: |

**Deviation:** The specification states that one posting per currency may omit its amount. Python beancount only allows ONE elided posting total per transaction. The single posting expands to cover all currencies.

**Error Produced:** `CategorizationError: You may not have more than one auto-posting per currency`

> Note: The error message says "per currency" but the actual behavior is "one total".

**Tracking:** Awaiting spec clarification. See [Pending Issues](#pending-issues).

---

### Costs

#### Merge Cost Operator `{*}`

| Spec Requirement | Implementation | Status |
|------------------|----------------|--------|
| Merge all lots into average-cost lot | Not implemented | :warning: |

**Deviation:** The merge cost syntax `{*}` is parsed but not implemented.

**Error Produced:** `ParserError: Cost merging is not supported yet`

**Note:** This is a known unimplemented feature, not a bug.

---

### Booking Methods

#### AVERAGE Booking

| Spec Requirement | Implementation | Status |
|------------------|----------------|--------|
| Average cost basis booking | Not implemented | :warning: |

**Deviation:** The `AVERAGE` booking method is parsed but not implemented.

**Error Produced:** `AmbiguousMatchError: AVERAGE method is not supported`

**Note:** This is a known unimplemented feature, not a bug.

---

### Error Type Mapping

Python beancount maps spec error categories to the following types:

| Spec Category | Python Type | Module |
|---------------|-------------|--------|
| Lexical errors | `LexerError` | `beancount.parser.parser` |
| Syntax errors | `ParserError`, `ParserSyntaxError` | `beancount.parser.parser` |
| Semantic errors | `ValidationError` | `beancount.ops.validation` |
| Balance errors | `BalanceError` | `beancount.ops.balance` |
| Booking errors (lot) | `ReductionError` | `beancount.parser.booking_full` |
| Booking errors (elision) | `CategorizationError` | `beancount.parser.booking_full` |
| Pad errors | `PadError` | `beancount.ops.pad` |
| Document errors | `DocumentError` | `beancount.ops.documents` |

#### Additional Types

| Type | Purpose |
|------|---------|
| `DeprecatedError` | Warnings for deprecated features |
| `AmbiguousMatchError` | Booking ambiguity (also used for unimplemented AVERAGE) |

#### Error Inspection

```python
from beancount import loader

entries, errors, options = loader.load_file('ledger.beancount')

for error in errors:
    print(f"Type: {type(error).__name__}")
    print(f"File: {error.source.get('filename')}")
    print(f"Line: {error.source.get('lineno')}")
    print(f"Message: {error.message}")
```

#### JSON Output

```bash
bean-check --json ledger.beancount
```

---

## Pending Issues

Issues to be filed to clarify undefined spec items:

| Topic | Issue | Status | Spec Section |
|-------|-------|--------|--------------|
| Amount elision rule | TBD | To file | posting.md |
| Close date semantics | TBD | To file | validation/accounts.md |
| Close with non-zero balance | TBD | To file | validation/accounts.md |
| Empty transaction validity | TBD | To file | validation/balance.md |
| Duplicate metadata behavior | TBD | To file | metadata.md |
| Currency length limits | TBD | To file | validation/commodities.md |

---

## Python Beancount Behaviors (Pending Spec Clarification)

The following behaviors are observed in Python beancount. They are documented here for reference while spec clarification is pending.

### Amount Elision
- Python allows only ONE auto-posting total per transaction
- The single posting expands to cover all currencies
- Error message misleadingly says "per currency"

### Close Date Semantics
- Posting ON the close date is allowed
- Only postings AFTER the close date produce an error

### Close with Non-Zero Balance
- Closing an account with remaining balance is allowed
- No error or warning is produced

### Empty Transactions
- Transactions with zero postings are syntactically valid
- They pass validation (trivially balance)

### Duplicate Metadata
- Produces `ParserError`
- First value is retained

### Currency Length
- Minimum 2 characters required
- No maximum length is enforced
- The 24-character limit in older docs is not implemented

### String Escape Sequences
- Only `\"` (escaped quote) and `\\` (escaped backslash) are processed
- Other sequences like `\n`, `\t`, `\r` are kept literally (not converted to newline/tab/etc.)

### Booking Methods (case sensitivity)
- Booking method names MUST be uppercase (`"FIFO"`, not `"fifo"`)
- Lowercase booking methods produce an error

### Other Behaviors

1. **Unused pad produces error** - `PadError` when pad has no effect
2. **`operating_currency` is additive** - Values from included files accumulate
3. **Implicit prices require plugin** - No option; requires `beancount.plugins.implicit_prices`
4. **Leading decimals invalid** - `.50` is not valid; must use `0.50`

---

## Test Results

```
Last test run: 2026-02-07
Implementation: Python beancount 3.2.0
Tests passed: 155
Tests failed: 0
Tests skipped: 9

Skipped tests:
- account-closed-posting-same-day: Close date semantics UNDEFINED
- metadata-duplicate-key: Duplicate metadata behavior UNDEFINED
- include-cycle-detection: Requires external file setup
- booking-average-cost: AVERAGE method not implemented
- cost-asterisk-merge: Cost merging {*} not implemented
- document-directive: Requires fixture file
- bql-tag-filter: has_tag function not in beanquery
- bql-link-filter: matches_link function not in beanquery
- invalid-transaction-no-postings: Empty transactions UNDEFINED
```
