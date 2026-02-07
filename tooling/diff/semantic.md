# Semantic Diff Specification

This document specifies semantic differencing for PTA journals.

## Overview

Semantic diff compares financial meaning rather than text:
- Equivalent transactions in different formats
- Reordered entries
- Split/merged transactions

## Equivalence Rules

### Amount Equivalence

```
50.00 USD ≡ 50 USD ≡ $50.00
```

### Account Equivalence

With aliases:
```
Assets:Bank ≡ bank (if alias bank = Assets:Bank)
```

### Transaction Equivalence

Same date, postings balance equivalently:

```beancount
; These are semantically equivalent:

2024-01-15 * "Store"
  Expenses:Food  50.00 USD
  Assets:Cash   -50.00 USD

2024-01-15 * "Store"
  Assets:Cash   -50.00 USD
  Expenses:Food  50.00 USD
```

## Comparison Levels

### Exact Match

All fields identical.

### Semantic Match

Same financial effect:
- Date matches
- Postings balance equivalently
- May differ in formatting, ordering

### Fuzzy Match

Approximate match:
- Date within tolerance
- Amount within tolerance
- Payee similarity

## Ignoring Differences

### Whitespace

```diff
-    Account    50.00 USD
+    Account   50.00 USD
```

Ignored (whitespace only).

### Formatting

```diff
- $1,000.00
+ 1000.00 USD
```

Ignored (same amount).

### Ordering

```diff
- Expenses:A  50.00 USD
- Expenses:B  30.00 USD
+ Expenses:B  30.00 USD
+ Expenses:A  50.00 USD
```

Ignored (same postings, different order).

## Significant Differences

### Amount Change

```diff
- Expenses:Food  50.00 USD
+ Expenses:Food  75.00 USD
```

Significant: amount changed.

### Account Change

```diff
- Expenses:Food  50.00 USD
+ Expenses:Dining  50.00 USD
```

Significant: different account.

### Missing/Added

```diff
+ 2024-01-20 * "New Transaction"
+   Expenses:Food  25.00 USD
+   Assets:Cash
```

Significant: new transaction.

## Balance Impact

### Delta Report

```json
{
  "balance_deltas": [
    {
      "account": "Assets:Bank",
      "before": "5000.00 USD",
      "after": "4500.00 USD",
      "delta": "-500.00 USD"
    },
    {
      "account": "Expenses:Food",
      "before": "200.00 USD",
      "after": "700.00 USD",
      "delta": "500.00 USD"
    }
  ]
}
```

### Net Effect

```json
{
  "net_change": {
    "USD": "0.00"
  },
  "balanced": true
}
```

## Matching Algorithm

### Phase 1: Exact Match

Match transactions with identical:
- Date
- Payee
- Amount total

### Phase 2: Fuzzy Match

For unmatched, try:
- Date within 3 days
- Amount within 1%
- Payee Levenshtein distance < 3

### Phase 3: Residual

Remaining are additions/deletions.

## Commands

### Semantic Compare

```bash
pta diff --semantic old.journal new.journal
```

### Balance Delta

```bash
pta diff --balance-delta old.journal new.journal
```

### Ignore Options

```bash
pta diff --ignore-whitespace --ignore-order old.journal new.journal
```

## Output

### Semantic Summary

```
Semantic Diff: old.journal → new.journal

Identical: 150 transactions
Modified: 3 transactions
Added: 2 transactions
Removed: 1 transaction

Net balance change:
  Assets:Bank: -500.00 USD
  Expenses:Food: +500.00 USD
```

## See Also

- [Diff Specification](spec.md)
- [Canonical Output](../canonical/spec.md)
