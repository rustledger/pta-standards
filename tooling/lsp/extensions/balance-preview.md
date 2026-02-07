# Balance Preview Extension

This extension specifies real-time balance preview and validation features.

## Features

### Live Balance Display

Servers SHOULD display current balances via:
- Hover on account names
- Code lens above transactions
- Inlay hints after postings

### Balance Impact Preview

Show how a transaction affects account balances:

```beancount
2024-01-15 * "Salary deposit"
  Assets:Checking  1000.00 USD  ; Balance: 1,234.56 → 2,234.56 USD
  Income:Salary   -1000.00 USD  ; Balance: -5,000.00 → -6,000.00 USD
```

### Balance Assertion Preview

Before saving, show if balance assertions will pass:

```beancount
2024-01-16 balance Assets:Checking  2234.56 USD  ; ✓ Will pass
2024-01-16 balance Assets:Checking  2000.00 USD  ; ✗ Actual: 2,234.56 USD
```

### Running Balance

Display running balance after each transaction:

```beancount
2024-01-01 open Assets:Checking USD

2024-01-15 * "Deposit"
  Assets:Checking  1000.00 USD  ; Running: 1,000.00 USD
  Income:Salary

2024-01-20 * "Withdrawal"
  Assets:Checking  -50.00 USD   ; Running: 950.00 USD
  Expenses:Cash
```

## Code Lens

### Transaction Balance Impact

Display above transactions:

```
[Assets:Checking +1000.00 USD] [Income:Salary -1000.00 USD]
2024-01-15 * "Salary deposit"
  Assets:Checking  1000.00 USD
  Income:Salary
```

### Account Summary

Display above account sections:

```
[Balance: 1,234.56 USD | 45 transactions | Last: 2024-01-15]
; === Assets:Checking ===
```

## Diagnostics

### Pre-emptive Balance Warnings

Warn about balance issues before they occur:

| Warning | Description |
|---------|-------------|
| Balance will fail | Upcoming balance assertion won't match |
| Negative balance | Account will go negative |
| Large deviation | Transaction causes unusual balance change |

### Example Diagnostic

```json
{
  "range": {"start": {"line": 50, "character": 0}, "end": {"line": 50, "character": 40}},
  "severity": 2,
  "code": "beancount/balance/assertion-will-fail",
  "source": "beancount",
  "message": "Balance assertion will fail: expected 1000.00 USD, actual will be 950.00 USD",
  "relatedInformation": [
    {
      "location": {"uri": "file:///ledger.beancount", "range": {"start": {"line": 45}, "end": {"line": 45}}},
      "message": "This transaction causes the discrepancy"
    }
  ]
}
```

## Configuration

```json
{
  "beancount.balance.showRunningBalance": true,
  "beancount.balance.showBalanceImpact": true,
  "beancount.balance.codeLens.enabled": true,
  "beancount.balance.codeLens.showAccountSummary": true,
  "beancount.balance.warnNegativeBalance": true,
  "beancount.balance.warnLargeDeviation": 10000,
  "beancount.balance.previewAssertions": true
}
```

## Custom Requests

### `beancount/getRunningBalance`

Get running balance at a specific line.

**Request:**
```json
{
  "textDocument": {"uri": "file:///ledger.beancount"},
  "position": {"line": 50, "character": 0},
  "account": "Assets:Checking"
}
```

**Response:**
```json
{
  "account": "Assets:Checking",
  "balances": [
    {"currency": "USD", "amount": "1234.56"}
  ],
  "asOfDate": "2024-01-15",
  "transactionCount": 45
}
```

### `beancount/getBalanceAtDate`

Get balance for an account at a specific date.

**Request:**
```json
{
  "account": "Assets:Checking",
  "date": "2024-01-15"
}
```

**Response:**
```json
{
  "account": "Assets:Checking",
  "date": "2024-01-15",
  "balances": [
    {"currency": "USD", "amount": "1234.56"}
  ]
}
```
