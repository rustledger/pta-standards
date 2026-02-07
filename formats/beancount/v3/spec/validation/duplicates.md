# Duplicate Detection

> **IMPORTANT**: Python beancount 3.x does NOT have built-in duplicate detection. The options described below (`check_duplicates`, `duplicate_check`, etc.) do NOT exist in the reference implementation. This document describes potential approaches for implementations that wish to add this feature.

## Overview

Duplicate detection identifies potentially redundant entries in the ledger, helping prevent double-entry of transactions from imports or manual entry.

## Types of Duplicates

### Exact Duplicates

Transactions with identical:
- Date
- Flag
- Payee and narration
- All postings (accounts, amounts)
- Tags and links

### Probable Duplicates

Transactions with matching:
- Date (or within N days)
- Amount (primary posting)
- Account

But differing in:
- Narration text
- Metadata
- Secondary postings

### Import Duplicates

Transactions that match previously imported entries based on:
- External ID (bank reference)
- Date + amount + account

## Detection Methods

### Hash-Based Detection

Compute hash of transaction contents:

```python
def transaction_hash(txn):
    components = [
        txn.date.isoformat(),
        txn.flag,
        txn.payee or "",
        txn.narration or "",
    ]
    for posting in txn.postings:
        components.extend([
            posting.account,
            str(posting.units),
        ])
    return hashlib.sha256("".join(components).encode()).hexdigest()
```

### Fuzzy Matching

For probable duplicates, use similarity scoring:

```python
def similarity_score(txn1, txn2):
    score = 0
    if txn1.date == txn2.date:
        score += 40
    elif abs((txn1.date - txn2.date).days) <= 3:
        score += 20

    if amounts_match(txn1, txn2):
        score += 40

    if accounts_overlap(txn1, txn2):
        score += 20

    return score  # Threshold: 80+
```

### Metadata-Based Detection

Use unique identifiers from imports:

```beancount
2024-01-15 * "Coffee Shop"
  bank-ref: "TXN123456789"
  Assets:Checking  -5.50 USD
  Expenses:Food

; Later import with same bank-ref → duplicate
2024-01-15 * "COFFEE SHOP NYC"
  bank-ref: "TXN123456789"    ; Same reference = duplicate
  Assets:Checking  -5.50 USD
  Expenses:Food
```

## Configuration

### Enable Detection

```beancount
option "check_duplicates" "TRUE"
```

### Sensitivity

```beancount
; Strict: exact matches only
option "duplicate_check" "strict"

; Fuzzy: probable duplicates
option "duplicate_check" "fuzzy"

; Metadata: use bank references
option "duplicate_check" "metadata"
```

### Date Window

```beancount
; Check within N days
option "duplicate_window_days" "3"
```

### Ignore Fields

```beancount
; Don't consider narration in comparison
option "duplicate_ignore" "narration"
```

## Warning Format

Duplicate detection produces warnings, not errors:

```
warning: Possible duplicate transaction
  --> ledger.beancount:150:1
   |
150| 2024-01-15 * "Coffee Shop"
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
   = similar to: ledger.beancount:42
   = matching: date, amount (-5.50 USD), account (Assets:Checking)
   = hint: add 'duplicate: FALSE' metadata to suppress
```

## Suppressing Warnings

### Metadata Flag

Mark intentional duplicates:

```beancount
2024-01-15 * "Monthly subscription"
  duplicate: FALSE    ; Intentionally similar to other entries
  Assets:Checking  -9.99 USD
  Expenses:Subscriptions
```

### Different Links

Transactions with different links are not duplicates:

```beancount
2024-01-15 * "Payment" ^invoice-001
  Assets:Checking  -100 USD
  Expenses:Services

2024-01-15 * "Payment" ^invoice-002
  Assets:Checking  -100 USD    ; Same amount but different link
  Expenses:Services
```

### Different Tags

Context-differentiating tags:

```beancount
2024-01-15 * "Lunch" #work
  Assets:Checking  -15 USD
  Expenses:Meals

2024-01-15 * "Lunch" #personal
  Assets:Checking  -15 USD    ; Same amount but different context
  Expenses:Meals
```

## Import Workflow

### First Import

```beancount
2024-01-15 * "AMAZON.COM"
  import-id: "amzn-2024-01-15-001"
  Assets:Checking  -50.00 USD
  Expenses:Shopping
```

### Duplicate Import (Detected)

```beancount
; This would be flagged as duplicate:
2024-01-15 * "Amazon Purchase"
  import-id: "amzn-2024-01-15-001"    ; Same ID
  Assets:Checking  -50.00 USD
  Expenses:Shopping
```

### Handling Duplicates

1. **Skip**: Don't import duplicates
2. **Mark**: Import but add `duplicate: TRUE`
3. **Merge**: Combine metadata from both
4. **Prompt**: Ask user to resolve

## Common Duplicate Scenarios

### Credit Card Statement

```beancount
; Pending transaction
2024-01-15 ! "UBER TRIP"
  Liabilities:CreditCard  -25.00 USD
  Expenses:Transport

; Posted transaction (probable duplicate)
2024-01-17 * "UBER* TRIP"
  Liabilities:CreditCard  -25.00 USD
  Expenses:Transport
```

### Transfer Between Accounts

```beancount
; From checking statement
2024-01-15 * "Transfer to Savings"
  Assets:Checking  -1000 USD
  Assets:Savings

; From savings statement (same transfer)
2024-01-15 * "Transfer from Checking"
  Assets:Savings   1000 USD
  Assets:Checking
```

This is a **valid duplicate** of the same real-world event.

### Recurring Payments

```beancount
; These are NOT duplicates - different months
2024-01-01 * "Netflix"
  Assets:Checking  -15.99 USD
  Expenses:Entertainment

2024-02-01 * "Netflix"
  Assets:Checking  -15.99 USD
  Expenses:Entertainment
```

## Duplicate Report

Generate a duplicate report:

```bash
bean-check --duplicates ledger.beancount
```

Output:
```
Duplicate Analysis
==================

Exact duplicates: 0

Probable duplicates: 3

1. ledger.beancount:42 ↔ ledger.beancount:150
   Date: 2024-01-15
   Amount: -5.50 USD
   Account: Assets:Checking
   Similarity: 95%

2. ledger.beancount:89 ↔ ledger.beancount:205
   Date: 2024-01-20 / 2024-01-22
   Amount: -25.00 USD
   Account: Liabilities:CreditCard
   Similarity: 85%
   Note: Possibly pending → posted transition

3. ...
```

## Implementation Notes

1. Build index of transactions by (date, amount, account)
2. For each transaction, check for matches in index
3. Apply similarity scoring for fuzzy matching
4. Check metadata for unique identifiers
5. Respect suppression flags and link/tag differences
6. Report as warnings with location information
