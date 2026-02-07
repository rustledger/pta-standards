# Budget Report

The budget report compares actual spending against budgeted amounts.

## Structure

```
                    Budget Report
              January 2024

Category                    Budget      Actual    Variance    %
════════════════════════════════════════════════════════════════
INCOME
  Salary                  6,250.00    6,250.00        0.00  100%
  Freelance               1,000.00    1,500.00     +500.00  150%
─────────────────────────────────────────────────────────────────
  Total Income            7,250.00    7,750.00     +500.00  107%

EXPENSES
  Housing
    Rent                  1,500.00    1,500.00        0.00  100%
    Utilities               200.00      185.00      +15.00   93%
  ───────────────────────────────────────────────────────────────
    Total Housing         1,700.00    1,685.00      +15.00   99%

  Food
    Groceries               500.00      525.00      -25.00  105%
    Restaurants             200.00      275.00      -75.00  138%
  ───────────────────────────────────────────────────────────────
    Total Food              700.00      800.00     -100.00  114%

  Transportation
    Gas                     200.00      180.00      +20.00   90%
    Insurance               100.00      100.00        0.00  100%
  ───────────────────────────────────────────────────────────────
    Total Transportation    300.00      280.00      +20.00   93%

═════════════════════════════════════════════════════════════════
TOTAL EXPENSES            2,700.00    2,765.00      -65.00  102%

═════════════════════════════════════════════════════════════════
NET (Income - Expenses)   4,550.00    4,985.00     +435.00  110%
```

## Data Model

```yaml
BudgetReport:
  period:
    begin: Date
    end: Date
  currency: Currency

  categories:
    - name: String
      type: income | expense
      budgeted: Amount
      actual: Amount
      variance: Amount
      percentage: Decimal
      subcategories:
        - name: String
          budgeted: Amount
          actual: Amount
          variance: Amount
          percentage: Decimal

  totals:
    income:
      budgeted: Amount
      actual: Amount
    expenses:
      budgeted: Amount
      actual: Amount
    net:
      budgeted: Amount
      actual: Amount
```

## Variance Calculation

```
Variance = Budgeted - Actual    (for expenses)
Variance = Actual - Budgeted    (for income)
Percentage = (Actual / Budgeted) * 100
```

### Variance Interpretation

| Type | Positive Variance | Negative Variance |
|------|-------------------|-------------------|
| Income | Over target (good) | Under target (bad) |
| Expenses | Under budget (good) | Over budget (bad) |

## Budget Definition

### Beancount Custom Directive

```beancount
2024-01-01 custom "budget" Expenses:Food:Groceries 500.00 USD
2024-01-01 custom "budget" Expenses:Food:Restaurants 200.00 USD
2024-01-01 custom "budget" Expenses:Rent 1500.00 USD
```

### hledger Periodic Transaction

```hledger
~ monthly
    Expenses:Food:Groceries    $500
    Expenses:Food:Restaurants  $200
    Expenses:Rent             $1500
    Assets:Budget
```

### Separate Budget File

```yaml
# budget-2024.yaml
period: monthly
currency: USD

income:
  Salary: 6250.00
  Freelance: 1000.00

expenses:
  Housing:
    Rent: 1500.00
    Utilities: 200.00
  Food:
    Groceries: 500.00
    Restaurants: 200.00
  Transportation:
    Gas: 200.00
    Insurance: 100.00
```

## Period Handling

### Monthly Budget

```
Budget for January 2024
- Groceries: $500/month budget vs $525 actual
```

### Annual Budget (pro-rated)

```
Annual budget: $6000
Monthly pro-rata: $500
January actual: $525 (105% of monthly)
YTD actual: $525 (9% of annual)
```

### Rolling Budget

Show last N months:

```
           Oct      Nov      Dec      Total
Budget   500.00   500.00   500.00   1,500.00
Actual   480.00   525.00   490.00   1,495.00
Var      +20.00   -25.00   +10.00      +5.00
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--begin DATE` | Period start | Month start |
| `--end DATE` | Period end | Month end |
| `--period SPEC` | Period (monthly, yearly) | monthly |
| `--budget-file PATH` | Budget definition file | None |
| `--no-rollup` | Don't roll up categories | false |
| `--show-empty` | Show categories with no activity | false |

## Format-Specific Commands

### Beancount

```bash
bean-report ledger.beancount budget
```

### hledger

```bash
hledger balance --budget
hledger bal -M --budget
hledger bal --budget --period monthly
```

### Ledger

```bash
ledger budget
ledger --budget balance
```

## Alerts and Thresholds

Define warning thresholds:

```yaml
alerts:
  warning: 90    # Warn at 90% of budget
  critical: 100  # Critical at 100%

categories:
  Expenses:Food:
    budget: 700.00
    warning: 80   # Override: warn earlier for food
```

Report output:

```
Category           Budget    Actual    Status
Groceries          500.00    475.00    ⚠️ 95% (warning)
Restaurants        200.00    275.00    🔴 138% (over)
Gas                200.00    150.00    ✓ 75%
```

## JSON Output

```json
{
  "period": {
    "begin": "2024-01-01",
    "end": "2024-01-31"
  },
  "currency": "USD",
  "categories": [
    {
      "name": "Expenses:Food:Groceries",
      "budgeted": "500.00",
      "actual": "525.00",
      "variance": "-25.00",
      "percentage": 105.0
    }
  ],
  "totals": {
    "expenses": {
      "budgeted": "2700.00",
      "actual": "2765.00",
      "variance": "-65.00"
    },
    "net": {
      "budgeted": "4550.00",
      "actual": "4985.00",
      "variance": "+435.00"
    }
  }
}
```

## See Also

- [Income Statement](income-statement.md)
- [Register](register.md)
