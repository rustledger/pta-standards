# PTA Diff Specification

This document specifies differencing algorithms for PTA journals.

## Overview

Journal diffing compares two versions:
- Structural changes
- Data changes
- Semantic equivalence

## Diff Types

### Textual Diff

Line-by-line comparison:

```diff
- 2024-01-15 * "Old Payee"
+ 2024-01-15 * "New Payee"
    Expenses:Food  50.00 USD
    Assets:Cash
```

### Structural Diff

AST-level comparison:

```json
{
  "changes": [
    {
      "type": "modified",
      "path": "/transactions/0/payee",
      "old": "Old Payee",
      "new": "New Payee"
    }
  ]
}
```

### Semantic Diff

Business-level comparison:

```json
{
  "balance_changes": [
    {
      "account": "Assets:Bank",
      "old": "1000.00 USD",
      "new": "1500.00 USD",
      "delta": "500.00 USD"
    }
  ]
}
```

## Algorithm

### Transaction Matching

1. Match by date and payee
2. Match by posting similarity
3. Match by amount totals

### Change Detection

For each matched pair:
1. Compare date
2. Compare payee/narration
3. Compare postings
4. Compare metadata

## Output Formats

### Unified Diff

```diff
--- old.journal
+++ new.journal
@@ -10,5 +10,5 @@
 2024-01-15 * "Payee"
-  Expenses:Food  50.00 USD
+  Expenses:Food  75.00 USD
   Assets:Cash
```

### JSON Diff

```json
{
  "added": [],
  "removed": [],
  "modified": [
    {
      "id": "txn-2024-01-15-001",
      "changes": [
        {"field": "postings.0.amount", "from": "50.00", "to": "75.00"}
      ]
    }
  ]
}
```

### HTML Diff

Side-by-side visual comparison.

## Commands

### Basic Diff

```bash
pta diff old.journal new.journal
```

### Semantic Diff

```bash
pta diff --semantic old.journal new.journal
```

### Balance Delta

```bash
pta diff --balance-delta old.journal new.journal
```

## Use Cases

### Version Control

Track changes in journal files:

```bash
git diff --ext-diff=pta-diff *.journal
```

### Audit Trail

Compare before/after imports:

```bash
pta diff before-import.journal after-import.journal
```

### Reconciliation

Find discrepancies:

```bash
pta diff bank-statement.journal my-records.journal
```

## See Also

- [Semantic Diff](semantic.md)
- [Tooling Overview](../README.md)
