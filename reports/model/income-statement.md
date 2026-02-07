# Income Statement Report

The income statement (profit & loss) shows revenue and expenses over a period of time.

## Structure

```
                   Income Statement
              January 1 - December 31, 2024

INCOME
  Income:Salary                   75,000.00 USD
  Income:Freelance                12,000.00 USD
  Income:Interest                    500.00 USD
  Income:Dividends                 1,200.00 USD
═══════════════════════════════════════════════
TOTAL INCOME                      88,700.00 USD


EXPENSES
  Housing
    Expenses:Rent                 18,000.00 USD
    Expenses:Utilities             2,400.00 USD
  ─────────────────────────────────────────────
    Total Housing                 20,400.00 USD

  Transportation
    Expenses:Gas                   2,400.00 USD
    Expenses:Insurance             1,200.00 USD
    Expenses:Maintenance             800.00 USD
  ─────────────────────────────────────────────
    Total Transportation           4,400.00 USD

  Food
    Expenses:Groceries             6,000.00 USD
    Expenses:Restaurants           2,400.00 USD
  ─────────────────────────────────────────────
    Total Food                     8,400.00 USD

  Other
    Expenses:Healthcare            3,600.00 USD
    Expenses:Entertainment         2,400.00 USD
    Expenses:Misc                  1,200.00 USD
  ─────────────────────────────────────────────
    Total Other                    7,200.00 USD

═══════════════════════════════════════════════
TOTAL EXPENSES                    40,400.00 USD


═══════════════════════════════════════════════
NET INCOME                        48,300.00 USD
```

## Data Model

```yaml
IncomeStatement:
  period:
    begin: Date
    end: Date
  currency: Currency

  income:
    categories:
      - name: String
        accounts: List[AccountBalance]
        total: Amount
    total: Amount

  expenses:
    categories:
      - name: String
        accounts: List[AccountBalance]
        total: Amount
    total: Amount

  net_income: Amount
```

## Net Income Calculation

```
Net Income = Total Income - Total Expenses
```

In double-entry terms (where income is negative, expenses positive):

```
Net Income = -(Sum of Income accounts + Sum of Expense accounts)
```

## Account Classification

### Income (negative/credit balance)

| Pattern | Category |
|---------|----------|
| `Income:Salary:*` | Earned Income |
| `Income:Freelance:*` | Earned Income |
| `Income:Interest:*` | Investment Income |
| `Income:Dividends:*` | Investment Income |
| `Income:Capital-Gains:*` | Investment Income |
| `Income:Gifts:*` | Other Income |

### Expenses (positive/debit balance)

| Pattern | Category |
|---------|----------|
| `Expenses:Rent:*` | Housing |
| `Expenses:Mortgage-Interest:*` | Housing |
| `Expenses:Utilities:*` | Housing |
| `Expenses:Groceries:*` | Food |
| `Expenses:Restaurants:*` | Food |
| `Expenses:Gas:*` | Transportation |
| `Expenses:Insurance:*` | Insurance |
| `Expenses:Healthcare:*` | Healthcare |
| `Expenses:Taxes:*` | Taxes |

## Periods

### Standard Periods

| Period | Description |
|--------|-------------|
| Monthly | Single calendar month |
| Quarterly | Q1, Q2, Q3, Q4 |
| Annual | Full calendar/fiscal year |
| YTD | Year to date |
| Custom | Any date range |

### Period Comparison

```
                   Income Statement
              Comparing 2023 vs 2024

                          2023         2024       Change
INCOME
  Salary              70,000.00    75,000.00    +7.14%
  Freelance            8,000.00    12,000.00   +50.00%
═════════════════════════════════════════════════════════
TOTAL INCOME          78,000.00    87,000.00   +11.54%
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--begin DATE` | Period start | Beginning |
| `--end DATE` | Period end | Today |
| `--period SPEC` | Period shorthand | None |
| `--monthly` | Show by month | false |
| `--quarterly` | Show by quarter | false |
| `--yearly` | Show by year | false |
| `--depth N` | Account depth | Unlimited |

## Format-Specific Commands

### Beancount

```bash
bean-report ledger.beancount income
bean-report ledger.beancount income --period "2024"
```

### hledger

```bash
hledger incomestatement
hledger is --period monthly
hledger is --begin 2024-01-01 --end 2024-12-31
```

### Ledger

```bash
ledger balance Income Expenses
ledger balance --begin 2024-01-01 --end 2024-12-31 Income Expenses
```

## JSON Output

```json
{
  "period": {
    "begin": "2024-01-01",
    "end": "2024-12-31"
  },
  "currency": "USD",
  "income": {
    "total": "88700.00",
    "accounts": [
      {"account": "Income:Salary", "amount": "75000.00"},
      {"account": "Income:Freelance", "amount": "12000.00"}
    ]
  },
  "expenses": {
    "total": "40400.00",
    "accounts": [
      {"account": "Expenses:Rent", "amount": "18000.00"},
      {"account": "Expenses:Groceries", "amount": "6000.00"}
    ]
  },
  "net_income": "48300.00"
}
```

## See Also

- [Balance Sheet](balance-sheet.md)
- [Budget Report](budget.md)
