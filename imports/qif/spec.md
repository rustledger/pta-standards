# QIF Import Specification

This document specifies how to import QIF (Quicken Interchange Format) files into plain text accounting formats.

## Overview

QIF is a legacy format originally developed by Intuit for Quicken. While deprecated in favor of OFX, many institutions and tools still export QIF.

## QIF Structure

### Basic Format

```qif
!Type:Bank
D01/15/2024
T-45.67
PGROCERY STORE
MWeekly groceries
LExpenses:Food
^
D01/16/2024
T2500.00
PACME CORP
MSalary deposit
LIncome:Salary
^
```

### Record Markers

| Marker | Meaning |
|--------|---------|
| `!Type:` | Account type header |
| `^` | End of transaction |

### Field Codes

| Code | Field | Description |
|------|-------|-------------|
| `D` | Date | Transaction date |
| `T` | Amount | Transaction amount |
| `P` | Payee | Payee name |
| `M` | Memo | Description/memo |
| `L` | Category | Category (maps to account) |
| `N` | Number | Check number |
| `C` | Cleared | Cleared status |
| `A` | Address | Payee address (multi-line) |
| `S` | Split Category | Split transaction category |
| `E` | Split Memo | Split transaction memo |
| `$` | Split Amount | Split transaction amount |

## Account Types

| Type Header | Description |
|-------------|-------------|
| `!Type:Bank` | Bank account |
| `!Type:Cash` | Cash account |
| `!Type:CCard` | Credit card |
| `!Type:Invst` | Investment account |
| `!Type:Oth A` | Other asset |
| `!Type:Oth L` | Other liability |

## Field Mapping

### Basic Transaction

```qif
D01/15/2024
T-45.67
PGROCERY STORE
MWeekly groceries
^
```

Maps to:

```beancount
2024-01-15 * "GROCERY STORE" "Weekly groceries"
  Assets:Checking  -45.67 USD
  Expenses:Uncategorized
```

### With Category

```qif
D01/15/2024
T-45.67
PGROCERY STORE
LExpenses:Food:Groceries
^
```

Maps to:

```beancount
2024-01-15 * "GROCERY STORE"
  Assets:Checking  -45.67 USD
  Expenses:Food:Groceries
```

## Split Transactions

### QIF Split Format

```qif
D01/15/2024
T-100.00
PTarget
SExpenses:Groceries
EFood items
$-75.00
SExpenses:Household
ECleaning supplies
$-25.00
^
```

### Output

```beancount
2024-01-15 * "Target"
  Assets:Checking  -100.00 USD
  Expenses:Groceries  75.00 USD
    memo: "Food items"
  Expenses:Household  25.00 USD
    memo: "Cleaning supplies"
```

## Date Formats

QIF dates vary by locale:

| Format | Example | Pattern |
|--------|---------|---------|
| US | 01/15/2024 | `%m/%d/%Y` |
| US Short | 1/15'24 | `%-m/%-d'%y` |
| EU | 15/01/2024 | `%d/%m/%Y` |

### Configuration

```yaml
date_format: "%m/%d/%Y"
# or
date_formats:
  - "%m/%d/%Y"
  - "%m/%d'%y"
```

## Cleared Status

| Code | Status | PTA Flag |
|------|--------|----------|
| (empty) | Uncleared | `!` |
| `c` | Cleared | `*` |
| `*` | Cleared | `*` |
| `X` | Reconciled | `*` |

## Transfer Transactions

### QIF Transfer Notation

```qif
D01/15/2024
T-500.00
P[Savings]
MTransfer to savings
^
```

Brackets indicate transfer to another account.

### Output

```beancount
2024-01-15 * "Transfer to savings"
  Assets:Checking  -500.00 USD
  Assets:Savings    500.00 USD
```

## Investment Transactions

### QIF Investment Format

```qif
!Type:Invst
D01/15/2024
NBuy
YAAPL
I150.00
Q100
T15000.00
^
```

### Investment Codes

| Code | Field |
|------|-------|
| `N` | Action (Buy, Sell, Div, etc.) |
| `Y` | Security name |
| `I` | Price |
| `Q` | Quantity |
| `T` | Total amount |
| `O` | Commission |

### Output

```beancount
2024-01-15 * "Buy AAPL"
  Assets:Brokerage  100 AAPL {150.00 USD}
  Assets:Brokerage:Cash  -15000.00 USD
```

## Configuration

### Account Mapping

```yaml
# qif-config.yaml
default_account: Assets:Checking
currency: USD

account_types:
  Bank: Assets:Bank
  CCard: Liabilities:CreditCard
  Cash: Assets:Cash

category_mapping:
  "Groceries": "Expenses:Food:Groceries"
  "Auto:Gas": "Expenses:Transportation:Gas"
  "Salary": "Income:Salary"

transfer_accounts:
  "Savings": "Assets:Savings"
  "Credit Card": "Liabilities:CreditCard"
```

### Payee Rules

```yaml
rules:
  - match: "GROCERY STORE"
    payee: "Grocery Store"
    account: Expenses:Food:Groceries
```

## Multi-Account Files

QIF files may contain multiple accounts:

```qif
!Account
NChecking
TBank
^
!Type:Bank
D01/15/2024
...
^
!Account
NSavings
TBank
^
!Type:Bank
D01/15/2024
...
```

## Limitations

| Issue | Workaround |
|-------|------------|
| No currency field | Configure per-file |
| Ambiguous dates | Configure date format |
| Category vs Account | Map categories to accounts |
| No unique IDs | Hash-based deduplication |

## Error Handling

| Error | Action |
|-------|--------|
| Unknown type header | Warning, skip section |
| Invalid date | Reject transaction |
| Missing amount | Reject transaction |
| Unbalanced split | Warning |

## Output Example

```beancount
; Imported from QIF: quicken-export.qif
; Account: Assets:Checking

2024-01-15 * "GROCERY STORE" "Weekly groceries"
  qif-imported: TRUE
  Assets:Checking  -45.67 USD
  Expenses:Food:Groceries

2024-01-16 * "ACME CORP" "Salary deposit"
  qif-imported: TRUE
  Assets:Checking  2500.00 USD
  Income:Salary
```

## See Also

- [CSV Import](../csv/spec.md)
- [OFX Import](../ofx/spec.md)
