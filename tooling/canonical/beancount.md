# Beancount Canonical Output

This document specifies canonical output format for Beancount journals.

## Format

### Transaction

```beancount
2024-01-15 * "Payee" "Narration"
  Account:One    100.00 USD
  Account:Two   -100.00 USD
```

## Formatting Rules

### Date

```beancount
2024-01-15    ; YYYY-MM-DD only
```

### Flag

```beancount
2024-01-15 * "Cleared"
2024-01-15 ! "Pending"
```

### Payee and Narration

```beancount
2024-01-15 * "Payee" "Narration"
2024-01-15 * "Just narration"
```

Both must be quoted.

### Account Alignment

```beancount
  Assets:Bank:Checking     100.00 USD
  Expenses:Food:Groceries  -50.00 USD
```

2-space indent, right-align amounts.

### Amount Format

```beancount
  Account    1234.56 USD
  Account    10 AAPL {150.00 USD}
  Account    10 AAPL {150.00 USD, 2024-01-10}
```

Number before commodity, no grouping separators in canonical form.

### Metadata

```beancount
2024-01-15 * "Payee" "Narration"
  key: "value"
  Account    100.00 USD
    posting-key: "posting-value"
```

### Tags and Links

```beancount
2024-01-15 * "Payee" "Narration" #tag1 #tag2 ^link1
  Account    100.00 USD
```

## Directive Order

1. `option` directives
2. `plugin` directives
3. `open` directives (chronological)
4. `commodity` directives
5. Transactions (chronological)
6. `close` directives
7. `balance` directives (with related transactions)

## Example

```beancount
; Canonical Beancount output

option "title" "My Ledger"
option "operating_currency" "USD"

plugin "beancount.plugins.leafonly"

2024-01-01 open Assets:Bank:Checking USD
2024-01-01 open Expenses:Food:Groceries
2024-01-01 open Equity:Opening-Balances

2024-01-01 commodity USD
  name: "US Dollar"

2024-01-01 * "Opening Balance"
  Assets:Bank:Checking     5000.00 USD
  Equity:Opening-Balances

2024-01-15 * "Whole Foods" "Weekly groceries" #groceries
  receipt: "scan-2024-01-15.pdf"
  Expenses:Food:Groceries    125.50 USD
  Assets:Bank:Checking      -125.50 USD

2024-01-31 balance Assets:Bank:Checking  4874.50 USD
```

## Normalization

### Input

```beancount
2024-01-15 * "Payee" "Description"
    Assets:Bank         100 USD
    Expenses:Food
```

### Canonical Output

```beancount
2024-01-15 * "Payee" "Description"
  Assets:Bank      100.00 USD
  Expenses:Food   -100.00 USD
```

## Differences from Other Formats

| Feature | Beancount | Ledger/hledger |
|---------|-----------|----------------|
| Quotes | Required | Optional |
| Amount position | Before commodity | Either |
| Indent | 2 spaces | 4 spaces |
| Elision | Explicit | Allowed |

## See Also

- [Canonical Specification](spec.md)
- [Beancount Specification](../../formats/beancount/)
