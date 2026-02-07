# Amount Completion Extension

This extension specifies smart amount completion and calculation features.

## Features

### Currency Completion

After typing an amount, suggest appropriate currencies:

| Context | Suggested Currencies |
|---------|---------------------|
| Account with currency constraint | Constrained currencies only |
| Any account | Operating currencies first, then all |
| After price `@` | All currencies except posting currency |

### Amount Inference

Servers MAY suggest amounts based on:
1. Transaction balance requirement
2. Historical transaction patterns
3. Recurring transaction amounts

### Expression Support

Support arithmetic expressions in amounts:

```beancount
2024-01-15 * "Split dinner"
  Expenses:Food  (89.50 / 3) USD  ; Server can show computed: 29.83 USD
  Assets:Cash
```

### Balancing Amount

When only one posting needs an amount, suggest the balancing amount:

```beancount
2024-01-15 * "Purchase"
  Expenses:Food  50.00 USD
  Assets:Cash    |  ; Suggest: -50.00 USD
```

## Inlay Hints

Servers SHOULD provide inlay hints for:

| Hint Type | Display |
|-----------|---------|
| Computed expression | `(100 / 3)` → `33.33` |
| Elided amount | Show computed amount |
| Total cost | `10 AAPL {{1500 USD}}` → `150.00 USD each` |
| Currency conversion | `100 EUR @ 1.10 USD` → `= 110.00 USD` |

## Configuration

```json
{
  "beancount.completion.amounts.suggestBalancing": true,
  "beancount.completion.amounts.showComputedExpressions": true,
  "beancount.completion.amounts.decimalPlaces": 2,
  "beancount.inlayHints.amounts.enabled": true,
  "beancount.inlayHints.amounts.showConversions": true
}
```

## Example: Balancing Amount Suggestion

Transaction with one posting:

```beancount
2024-01-15 * "Grocery shopping"
  Expenses:Food  50.00 USD
  Assets:Checking  |
```

Completion at `|` position:

```json
{
  "items": [
    {
      "label": "-50.00 USD",
      "kind": 12,
      "detail": "Balancing amount",
      "insertText": "-50.00 USD",
      "preselect": true
    }
  ]
}
```

## Example: Currency Completion

After amount `100 `:

```json
{
  "items": [
    {
      "label": "USD",
      "kind": 11,
      "detail": "Operating currency",
      "sortText": "0001"
    },
    {
      "label": "EUR",
      "kind": 11,
      "detail": "Operating currency",
      "sortText": "0002"
    },
    {
      "label": "AAPL",
      "kind": 11,
      "detail": "Commodity",
      "sortText": "1001"
    }
  ]
}
```
