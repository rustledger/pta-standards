# Balance Sheet Report

The balance sheet shows the financial position at a specific point in time: assets, liabilities, and equity.

## Structure

```
                    Balance Sheet
                  As of 2024-12-31

ASSETS
  Current Assets
    Assets:Bank:Checking           5,000.00 USD
    Assets:Bank:Savings           10,000.00 USD
    Assets:Receivables             2,500.00 USD
  ─────────────────────────────────────────────
    Total Current Assets          17,500.00 USD

  Fixed Assets
    Assets:Property              200,000.00 USD
    Assets:Vehicle                25,000.00 USD
  ─────────────────────────────────────────────
    Total Fixed Assets           225,000.00 USD
═══════════════════════════════════════════════
TOTAL ASSETS                     242,500.00 USD


LIABILITIES
  Current Liabilities
    Liabilities:CreditCard         1,200.00 USD
    Liabilities:Payables           3,000.00 USD
  ─────────────────────────────────────────────
    Total Current Liabilities      4,200.00 USD

  Long-term Liabilities
    Liabilities:Mortgage         150,000.00 USD
  ─────────────────────────────────────────────
    Total Long-term Liabilities  150,000.00 USD
═══════════════════════════════════════════════
TOTAL LIABILITIES                154,200.00 USD


EQUITY
  Equity:OpeningBalances          50,000.00 USD
  Retained Earnings               38,300.00 USD
═══════════════════════════════════════════════
TOTAL EQUITY                      88,300.00 USD

═══════════════════════════════════════════════
TOTAL LIABILITIES + EQUITY       242,500.00 USD
```

## Accounting Equation

The balance sheet must satisfy:

```
Assets = Liabilities + Equity
```

This is verified formally in [balance-sheet.als](../formal/balance-sheet.als).

## Signs and Presentation

The sign of a category total is not constrained. "Normally positive" and
"normally negative" below describe the usual case, not a rule (see
[Normal Balance Direction](../../core/model/account.md#normal-balance-direction)):
an overdrawn bank account makes an Assets balance negative, an over-paid
credit card makes a Liabilities balance positive, and contra accounts (such
as accumulated depreciation) carry the opposite sign to their category. A
balance sheet containing them is still valid and still satisfies the
accounting equation.

The report above shows liabilities and equity as positive numbers. That is
a display choice: in the stored, signed form they are negative and
`Assets + Liabilities + Equity = 0`. Implementations MAY flip the sign of
credit-normal categories for display (hledger's `bs`, Fava's
`invert-income-liabilities-equity`, BQL's `POSSIGN`); an opposite-sign
account then shows with a minus sign under its category.

## Data Model

```yaml
BalanceSheet:
  as_of: Date
  currency: Currency

  assets:
    current:
      accounts: List[AccountBalance]
      total: Amount
    fixed:
      accounts: List[AccountBalance]
      total: Amount
    total: Amount

  liabilities:
    current:
      accounts: List[AccountBalance]
      total: Amount
    long_term:
      accounts: List[AccountBalance]
      total: Amount
    total: Amount

  equity:
    accounts: List[AccountBalance]
    retained_earnings: Amount
    total: Amount

AccountBalance:
  account: AccountName
  balance: Amount
```

## Account Classification

### Assets (normally positive)

| Prefix | Classification |
|--------|---------------|
| `Assets:Bank:*` | Current |
| `Assets:Cash:*` | Current |
| `Assets:Receivables:*` | Current |
| `Assets:Investments:*` | Current or Fixed |
| `Assets:Property:*` | Fixed |
| `Assets:Vehicle:*` | Fixed |

### Liabilities (normally negative)

| Prefix | Classification |
|--------|---------------|
| `Liabilities:CreditCard:*` | Current |
| `Liabilities:Payables:*` | Current |
| `Liabilities:Loans:*` | Long-term |
| `Liabilities:Mortgage:*` | Long-term |

### Equity (normally negative)

| Prefix | Description |
|--------|-------------|
| `Equity:OpeningBalances` | Initial equity |
| `Equity:Retained` | Accumulated earnings |
| `Equity:Contributions` | Owner contributions |

## Retained Earnings Calculation

Retained earnings are computed as:

```
Retained Earnings = -(Income + Expenses)
```

Where:
- Income accounts have negative balances (credits)
- Expense accounts have positive balances (debits)

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--date DATE` | Report as of date | Today |
| `--currency CUR` | Convert to currency | None |
| `--depth N` | Account hierarchy depth | Unlimited |
| `--flat` | Don't show hierarchy | false |
| `--empty` | Show zero-balance accounts | false |

## Format-Specific Commands

### Beancount

```bash
bean-report ledger.beancount balsheet
bean-report ledger.beancount balsheet --currency USD
```

### hledger

```bash
hledger balancesheet
hledger bs --date 2024-12-31
hledger bs --depth 2
```

### Ledger

```bash
ledger balance Assets Liabilities Equity
ledger balance --date 2024-12-31 Assets Liabilities Equity
```

## JSON Output

```json
{
  "as_of": "2024-12-31",
  "currency": "USD",
  "assets": {
    "total": "242500.00",
    "accounts": [
      {"account": "Assets:Bank:Checking", "balance": "5000.00"},
      {"account": "Assets:Bank:Savings", "balance": "10000.00"}
    ]
  },
  "liabilities": {
    "total": "154200.00",
    "accounts": [
      {"account": "Liabilities:CreditCard", "balance": "1200.00"},
      {"account": "Liabilities:Mortgage", "balance": "150000.00"}
    ]
  },
  "equity": {
    "total": "88300.00"
  }
}
```

## See Also

- [Income Statement](income-statement.md)
- [Trial Balance](trial-balance.md)
