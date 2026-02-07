# QIF to PTA Mapping

This document specifies mapping from QIF (Quicken Interchange Format) to PTA formats.

## Overview

QIF is a legacy format from Quicken. This document specifies how to convert QIF records to PTA transactions.

## QIF Structure

### Record Types

| Code | Type |
|------|------|
| `!Type:Bank` | Bank account |
| `!Type:Cash` | Cash account |
| `!Type:CCard` | Credit card |
| `!Type:Invst` | Investment |
| `!Type:Cat` | Category list |

### Transaction Fields

| Code | Meaning |
|------|---------|
| `D` | Date |
| `T` | Amount |
| `P` | Payee |
| `M` | Memo |
| `C` | Cleared status |
| `N` | Check number |
| `L` | Category |
| `S` | Split category |
| `$` | Split amount |

## Basic Mapping

### QIF Transaction

```qif
!Type:Bank
D01/15/2024
T-50.00
PGrocery Store
MWeekly groceries
CX
LFood:Groceries
^
```

### Beancount Output

```beancount
2024-01-15 * "Grocery Store" "Weekly groceries"
  Expenses:Food:Groceries    50.00 USD
  Assets:Bank:Checking      -50.00 USD
```

### Ledger Output

```ledger
2024/01/15 * Grocery Store
    ; Weekly groceries
    Expenses:Food:Groceries    $50.00
    Assets:Bank:Checking
```

## Date Mapping

### QIF Date Formats

```
D1/15/24       → 2024-01-15
D01/15/2024    → 2024-01-15
D1/15'24       → 2024-01-15
```

### Conversion

```python
from datetime import datetime

def parse_qif_date(qif_date):
    formats = [
        "%m/%d/%Y",
        "%m/%d/%y",
        "%m/%d'%y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(qif_date, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unknown date format: {qif_date}")
```

## Amount Mapping

### QIF Amount

```
T-50.00     → Outflow (negative)
T50.00      → Inflow (positive)
T1,234.56   → With thousands separator
```

### Conversion

Remove commas, parse as decimal.

## Status Mapping

| QIF | PTA |
|-----|-----|
| (blank) | Unmarked |
| `*` | Pending (!) |
| `X` or `c` | Cleared (*) |

## Category Mapping

### QIF Categories

```
LFood:Groceries
```

### PTA Accounts

```
Expenses:Food:Groceries
```

### Mapping Rules

```yaml
category_mapping:
  "Food:Groceries": "Expenses:Food:Groceries"
  "Auto:Gas": "Expenses:Transportation:Gas"
  "Salary": "Income:Salary"

  # Default prefixes
  expense_prefix: "Expenses:"
  income_prefix: "Income:"
  asset_prefix: "Assets:"
```

## Split Transactions

### QIF Split

```qif
D01/15/2024
T-100.00
PCostco
SFood:Groceries
$-75.00
SHousehold
$-25.00
^
```

### PTA Output

```beancount
2024-01-15 * "Costco"
  Expenses:Food:Groceries    75.00 USD
  Expenses:Household         25.00 USD
  Assets:Bank:Checking     -100.00 USD
```

## Investment Transactions

### QIF Investment

```qif
!Type:Invst
D01/15/2024
NBuy
YAAPL
I150.00
Q10
T1500.00
^
```

### PTA Output

```beancount
2024-01-15 * "Buy AAPL"
  Assets:Brokerage    10 AAPL {150.00 USD}
  Assets:Cash       -1500.00 USD
```

### Investment Actions

| QIF | Meaning | PTA |
|-----|---------|-----|
| `Buy` | Purchase | Debit investment, credit cash |
| `Sell` | Sale | Credit investment, debit cash |
| `Div` | Dividend | Income posting |
| `IntInc` | Interest | Income posting |
| `ShrsIn` | Shares in | Transfer in |
| `ShrsOut` | Shares out | Transfer out |

## Transfer Mapping

### QIF Transfer

```qif
LChecking
```

or

```qif
L[Checking]
```

### Detection

Square brackets indicate transfer to named account.

## Example Conversion

### Complete QIF File

```qif
!Type:Bank
D01/15/2024
T-50.00
PGrocery Store
LFood
CX
^
D01/16/2024
T1000.00
PPayroll
LIncome:Salary
C*
^
D01/17/2024
T-75.00
PGas Station
SAuto:Gas
$-50.00
SAuto:Maintenance
$-25.00
^
```

### Converted Output

```beancount
2024-01-15 * "Grocery Store"
  Expenses:Food              50.00 USD
  Assets:Bank:Checking      -50.00 USD

2024-01-16 ! "Payroll"
  Assets:Bank:Checking     1000.00 USD
  Income:Salary           -1000.00 USD

2024-01-17 * "Gas Station"
  Expenses:Auto:Gas          50.00 USD
  Expenses:Auto:Maintenance  25.00 USD
  Assets:Bank:Checking      -75.00 USD
```

## Error Handling

### Missing Fields

- Date required
- Amount required
- Payee defaults to "Unknown"
- Category defaults to "Expenses:Unknown"

### Invalid Data

- Invalid dates: Skip or prompt
- Invalid amounts: Skip or prompt
- Unknown categories: Create or map to default

## See Also

- [OFX Mapping](../ofx/mapping.md)
- [CSV Rules](../csv/rules.md)
- [Import Specification](../README.md)
