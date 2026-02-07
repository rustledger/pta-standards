# Register Report

The register shows a chronological list of transactions affecting specified accounts, with running balances.

## Structure

```
                    Account Register
              Assets:Bank:Checking

Date       Description              Amount       Balance
════════════════════════════════════════════════════════
2024-01-01 Opening Balance        5,000.00     5,000.00
2024-01-05 Grocery Store           -125.50     4,874.50
2024-01-10 Gas Station              -45.00     4,829.50
2024-01-15 Payroll               2,500.00     7,329.50
2024-01-18 Electric Company        -120.00     7,209.50
2024-01-20 Restaurant               -65.00     7,144.50
2024-01-25 Transfer to Savings  -1,000.00     6,144.50
2024-01-31 Interest                   2.15     6,146.65
```

## Data Model

```yaml
Register:
  account: AccountName
  period:
    begin: Date | null
    end: Date | null
  currency: Currency

  opening_balance: Amount

  entries:
    - date: Date
      description: String
      payee: String | null
      amount: Amount
      balance: Amount
      transaction_id: String | null

  closing_balance: Amount
```

## Entry Details

Each register entry corresponds to a posting to the account:

```yaml
RegisterEntry:
  date: Date                    # Transaction date
  description: String           # Narration/memo
  payee: String | null          # Payee if present
  amount: Amount                # Change to this account
  balance: Amount               # Running balance after

  # Optional details
  transaction_id: String        # Link to full transaction
  other_account: AccountName    # Contra account
  cleared: ClearedStatus        # *, !, or blank
  check_number: String | null   # Check # if applicable
```

## Running Balance

The running balance is computed as:

```
balance[i] = balance[i-1] + amount[i]
```

Where `balance[0]` is the opening balance.

## Multi-Account Register

Show transactions affecting multiple accounts:

```
                    Register
              Assets:Bank:*

Date       Account                    Amount       Balance
════════════════════════════════════════════════════════════
2024-01-01 Checking                 5,000.00     5,000.00
2024-01-01 Savings                 10,000.00    15,000.00
2024-01-05 Checking                  -125.50    14,874.50
2024-01-25 Checking                -1,000.00    13,874.50
2024-01-25 Savings                  1,000.00    14,874.50
```

## Detailed Register

Show full transaction details:

```
2024-01-05 * "Whole Foods" "Weekly groceries"
  Assets:Bank:Checking                           -125.50 USD
  Expenses:Food:Groceries                         125.50 USD

  Running balance: 4,874.50 USD
  ────────────────────────────────────────────────────────────
```

## Cleared Status

| Status | Symbol | Description |
|--------|--------|-------------|
| Uncleared | | Not yet processed |
| Pending | `!` | Pending/uncleared |
| Cleared | `*` | Cleared/reconciled |

```
Date       Clr  Description              Amount       Balance
═══════════════════════════════════════════════════════════════
2024-01-05  *  Grocery Store           -125.50     4,874.50
2024-01-10  !  Gas Station              -45.00     4,829.50
2024-01-12     Restaurant               -35.00     4,794.50
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--account PATTERN` | Account(s) to show | Required |
| `--begin DATE` | Start date | All |
| `--end DATE` | End date | All |
| `--cleared` | Only cleared entries | false |
| `--pending` | Only pending entries | false |
| `--uncleared` | Only uncleared entries | false |
| `--width N` | Output width | Terminal |
| `--related` | Show related accounts | false |

## Format-Specific Commands

### Beancount

```bash
bean-report ledger.beancount journal Assets:Bank:Checking
bean-report ledger.beancount journal --account "Assets:Bank:*"
```

### hledger

```bash
hledger register Assets:Bank:Checking
hledger reg checking --begin 2024-01-01
hledger reg --cleared checking
```

### Ledger

```bash
ledger register Assets:Bank:Checking
ledger reg checking --begin 2024-01-01
ledger reg --cleared checking
```

## JSON Output

```json
{
  "account": "Assets:Bank:Checking",
  "period": {
    "begin": "2024-01-01",
    "end": "2024-01-31"
  },
  "currency": "USD",
  "opening_balance": "5000.00",
  "entries": [
    {
      "date": "2024-01-05",
      "description": "Grocery Store",
      "amount": "-125.50",
      "balance": "4874.50",
      "cleared": true
    },
    {
      "date": "2024-01-15",
      "description": "Payroll",
      "amount": "2500.00",
      "balance": "7329.50",
      "cleared": true
    }
  ],
  "closing_balance": "6146.65"
}
```

## Reconciliation Use

The register is essential for bank reconciliation:

1. Get statement balance from bank
2. Filter register to reconciliation date
3. Mark cleared transactions as `*`
4. Verify register cleared balance = statement balance

## See Also

- [Balance Sheet](balance-sheet.md)
- [Trial Balance](trial-balance.md)
