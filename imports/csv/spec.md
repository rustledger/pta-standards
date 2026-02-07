# CSV Import Specification

This document specifies how to import CSV (Comma-Separated Values) files into plain text accounting formats.

## Overview

CSV is the most common format for bank and financial institution exports. This specification defines a rule-based system for transforming CSV data into PTA transactions.

## CSV Parsing

### Basic Format

```csv
Date,Description,Amount,Balance
2024-01-15,"GROCERY STORE",-45.67,1234.56
2024-01-16,"DIRECT DEPOSIT",2500.00,3734.56
```

### Parsing Options

| Option | Description | Default |
|--------|-------------|---------|
| `separator` | Field delimiter | `,` |
| `quote` | Quote character | `"` |
| `encoding` | Character encoding | `utf-8` |
| `skip_lines` | Header lines to skip | `1` |
| `date_format` | Date parsing format | `%Y-%m-%d` |

## Rule-Based Mapping

### Rule File Structure

```yaml
# bank-checking.rules
account: Assets:Checking
currency: USD

fields:
  date: 1
  amount: 3
  description: 2
  balance: 4

date_format: "%m/%d/%Y"

rules:
  - match: "GROCERY|WHOLE FOODS"
    account: Expenses:Food:Groceries

  - match: "AMAZON"
    account: Expenses:Shopping
    payee: "Amazon"

  - match: "DIRECT DEPOSIT"
    account: Income:Salary

  - default:
    account: Expenses:Uncategorized
```

### Field Mapping

| Field | Required | Description |
|-------|----------|-------------|
| `date` | Yes | Transaction date column |
| `amount` | Yes | Transaction amount |
| `description` | Yes | Raw description text |
| `payee` | No | Payee name |
| `balance` | No | Running balance |

### Amount Handling

#### Single Column
```yaml
fields:
  amount: 3
# Positive = credit, Negative = debit
```

#### Separate Debit/Credit
```yaml
fields:
  debit: 3
  credit: 4
```

## Matching Rules

### Pattern Matching

```yaml
rules:
  - match: "WHOLE FOODS|TRADER JOE"
    account: Expenses:Food:Groceries
    payee: "Grocery Store"
```

Patterns use regular expressions (case-insensitive).

### Match Priority

Rules are evaluated in order; first match wins.

### Match Output

```yaml
rules:
  - match: "AMAZON"
    account: Expenses:Shopping
    payee: "Amazon"
    narration: "Online purchase"
    tags: ["online"]
```

## Date Parsing

| Format | Example | Pattern |
|--------|---------|---------|
| ISO | 2024-01-15 | `%Y-%m-%d` |
| US | 01/15/2024 | `%m/%d/%Y` |
| EU | 15/01/2024 | `%d/%m/%Y` |

## Duplicate Detection

```yaml
duplicate_detection:
  method: hash
  fields: [date, amount, description]
```

## Balance Assertions

```yaml
balance_assertions:
  enabled: true
  frequency: daily
```

## Example Output

```beancount
2024-01-15 * "Whole Foods" "Groceries"
  imported: TRUE
  Assets:Checking  -45.67 USD
  Expenses:Food:Groceries
```

## See Also

- [OFX Import](../ofx/spec.md)
- [QIF Import](../qif/spec.md)
