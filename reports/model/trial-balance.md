# Trial Balance Report

The trial balance lists all accounts with their debit and credit balances, verifying that total debits equal total credits.

## Structure

```
                      Trial Balance
                    As of 2024-12-31

Account                           Debit         Credit
════════════════════════════════════════════════════════
Assets:Bank:Checking           5,000.00
Assets:Bank:Savings           10,000.00
Assets:Receivables             2,500.00
Assets:Property              200,000.00
Assets:Vehicle                25,000.00
Liabilities:CreditCard                         1,200.00
Liabilities:Payables                           3,000.00
Liabilities:Mortgage                         150,000.00
Equity:OpeningBalances                        50,000.00
Income:Salary                                 75,000.00
Income:Freelance                              12,000.00
Expenses:Rent                 18,000.00
Expenses:Groceries             6,000.00
Expenses:Utilities             2,400.00
Expenses:Gas                   2,400.00
Expenses:Insurance             1,200.00
Expenses:Healthcare            3,600.00
Expenses:Entertainment         2,400.00
Expenses:Restaurants           2,400.00
Expenses:Maintenance             800.00
Expenses:Misc                  1,200.00
────────────────────────────────────────────────────────
TOTALS                       291,200.00      291,200.00
```

## Fundamental Property

```
Sum of Debits = Sum of Credits
```

This is the core verification of double-entry bookkeeping. If debits don't equal credits, there's an error in the ledger.

## Data Model

```yaml
TrialBalance:
  as_of: Date
  currency: Currency

  accounts:
    - account: AccountName
      debit: Amount | null
      credit: Amount | null

  totals:
    debit: Amount
    credit: Amount

  balanced: Boolean
```

## Debit vs Credit

| Account Type | Normal Balance | Increase | Decrease |
|--------------|---------------|----------|----------|
| Assets | Debit | Debit | Credit |
| Liabilities | Credit | Credit | Debit |
| Equity | Credit | Credit | Debit |
| Income | Credit | Credit | Debit |
| Expenses | Debit | Debit | Credit |

## Account Balance Presentation

### Signed Balance (PTA internal)

```
Assets:Checking     5000.00 USD    (positive = debit)
Income:Salary     -75000.00 USD    (negative = credit)
```

### Debit/Credit Columns (traditional)

```
Account              Debit         Credit
Assets:Checking    5,000.00
Income:Salary                     75,000.00
```

## Verification Uses

1. **Balance Check**: Total debits must equal credits
2. **Account Review**: Identify unexpected balances
3. **Period Close**: Verify before closing books
4. **Audit Trail**: Starting point for financial statements

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--date DATE` | As of date | Today |
| `--currency CUR` | Convert to currency | None |
| `--empty` | Show zero-balance accounts | false |
| `--depth N` | Account hierarchy depth | Unlimited |
| `--sort FIELD` | Sort by account/debit/credit | account |

## Format-Specific Commands

### Beancount

```bash
bean-report ledger.beancount trial
bean-report ledger.beancount trial --currency USD
```

### hledger

```bash
hledger balance --tree
hledger balance --flat --no-total
```

### Ledger

```bash
ledger balance
ledger balance --flat
```

## Extended Trial Balance

Some systems support an extended trial balance with adjustments:

```
                     Extended Trial Balance
                       As of 2024-12-31

                    Unadjusted         Adjustments          Adjusted
Account             Dr      Cr         Dr      Cr          Dr      Cr
═══════════════════════════════════════════════════════════════════════
Assets:Checking   5,000            -            -        5,000
Assets:Prepaid    1,200               -      200        1,000
Expenses:Ins          -               200     -           200
```

## JSON Output

```json
{
  "as_of": "2024-12-31",
  "currency": "USD",
  "accounts": [
    {"account": "Assets:Bank:Checking", "debit": "5000.00", "credit": null},
    {"account": "Assets:Bank:Savings", "debit": "10000.00", "credit": null},
    {"account": "Income:Salary", "debit": null, "credit": "75000.00"},
    {"account": "Expenses:Rent", "debit": "18000.00", "credit": null}
  ],
  "totals": {
    "debit": "291200.00",
    "credit": "291200.00"
  },
  "balanced": true
}
```

## Formal Verification

The trial balance property is specified formally in [trial-balance.als](../formal/trial-balance.als):

```alloy
fact DebitEqualsCredit {
  sum[Account.debit_balance] = sum[Account.credit_balance]
}
```

## See Also

- [Balance Sheet](balance-sheet.md)
- [Formal Models](../formal/)
