# CSV Import Rules Specification

This document specifies rule-based CSV import for PTA formats.

## Overview

CSV rules define how to transform bank CSV exports into PTA transactions:
- Field mapping
- Amount parsing
- Account categorization
- Payee normalization

## Rule File Format

### hledger-style

```
; rules for bank.csv

skip 1
fields date, description, amount

date-format %m/%d/%Y
currency $

account1 Assets:Bank:Checking
account2 Expenses:Unknown

if Grocery|WHOLEFDS
  account2 Expenses:Food:Groceries

if AMAZON
  account2 Expenses:Shopping
```

### YAML Format

```yaml
csv_rules:
  source: bank.csv
  skip_lines: 1
  fields:
    date: 0
    description: 1
    amount: 2

  date_format: "%m/%d/%Y"
  default_currency: USD

  account1: Assets:Bank:Checking
  account2: Expenses:Unknown

  rules:
    - match: "Grocery|WHOLEFDS"
      account2: Expenses:Food:Groceries
    - match: "AMAZON"
      account2: Expenses:Shopping
```

## Field Mapping

### Basic Fields

```yaml
fields:
  date: 0          # Column index
  description: 1
  amount: 2
  # or by header name
  date: "Date"
  description: "Description"
  amount: "Amount"
```

### Multiple Amount Columns

```yaml
fields:
  date: 0
  description: 1
  debit: 2
  credit: 3

amount:
  debit: negative
  credit: positive
```

### Combined Amount

```yaml
amount:
  column: 2
  sign: infer  # from value sign
```

## Date Parsing

### Format Specification

```yaml
date_format: "%Y-%m-%d"    # ISO
date_format: "%m/%d/%Y"    # US
date_format: "%d/%m/%Y"    # EU
date_format: "%d.%m.%Y"    # German
```

### Multiple Formats

```yaml
date_formats:
  - "%Y-%m-%d"
  - "%m/%d/%Y"
```

## Amount Parsing

### Decimal Handling

```yaml
decimal_mark: "."
thousands_sep: ","
```

### Currency

```yaml
default_currency: USD
currency_column: 4
```

### Sign Convention

```yaml
amount_sign:
  positive: credit
  negative: debit
```

## Account Rules

### Pattern Matching

```yaml
rules:
  - match: "GROCERY|TRADER JOE"
    account2: Expenses:Food:Groceries

  - match: "UBER|LYFT"
    account2: Expenses:Transportation

  - match: "^PAYROLL"
    account2: Income:Salary
```

### Regex Support

```yaml
rules:
  - match: "^(?:VENMO|ZELLE).*"
    regex: true
    account2: Assets:Transfers
```

### Amount-Based Rules

```yaml
rules:
  - amount_greater: 1000
    account2: Expenses:Large
    tags: [large-expense, review]
```

### Combined Conditions

```yaml
rules:
  - match: "AMAZON"
    amount_less: 50
    account2: Expenses:Shopping:Small

  - match: "AMAZON"
    amount_greater: 50
    account2: Expenses:Shopping:Large
```

## Payee Normalization

### Simple Replacement

```yaml
payee_rules:
  - match: "WHOLEFDS.*"
    payee: "Whole Foods"

  - match: "AMZN.*|AMAZON.*"
    payee: "Amazon"
```

### Extraction

```yaml
payee_rules:
  - match: "^(.+?)\s+\d{4}$"
    extract: 1
```

## Output Format

### Transaction Template

```yaml
output:
  format: beancount
  template: |
    {date} * "{payee}" "{description}"
      {account1}  {amount} {currency}
      {account2}
```

### Metadata

```yaml
output:
  include_original: true
  metadata:
    source: "bank-import"
    csv_line: "{line_number}"
```

## Example Rules File

```yaml
# bank-checking.rules.yaml

source_type: csv
encoding: utf-8
skip_lines: 1
delimiter: ","

fields:
  date: 0
  description: 1
  amount: 2
  balance: 3

date_format: "%m/%d/%Y"
decimal_mark: "."
default_currency: USD

account1: Assets:Bank:Checking

# Default category
account2: Expenses:Unknown

# Categorization rules
rules:
  # Income
  - match: "PAYROLL|DIRECT DEP"
    account2: Income:Salary

  # Transfers
  - match: "TRANSFER|VENMO|ZELLE"
    account2: Assets:Transfers

  # Groceries
  - match: "WHOLE ?FOODS|TRADER JOE|SAFEWAY|GROCERY"
    account2: Expenses:Food:Groceries

  # Restaurants
  - match: "DOORDASH|GRUBHUB|UBER EATS"
    account2: Expenses:Food:Delivery

  # Transportation
  - match: "UBER|LYFT"
    account2: Expenses:Transportation:Rideshare

  - match: "SHELL|CHEVRON|76"
    account2: Expenses:Transportation:Gas

  # Shopping
  - match: "AMAZON|AMZN"
    account2: Expenses:Shopping:Online

  # Bills
  - match: "ELECTRIC|PG&E|UTILITY"
    account2: Expenses:Utilities:Electric

  - match: "COMCAST|XFINITY|AT&T"
    account2: Expenses:Utilities:Internet

# Payee cleanup
payee_rules:
  - match: "WHOLEFDS MKT.*"
    payee: "Whole Foods"
  - match: "AMZN MKTP.*"
    payee: "Amazon"
```

## See Also

- [CSV Import Specification](spec.md)
- [OFX Mapping](../ofx/mapping.md)
- [QIF Mapping](../qif/mapping.md)
