# Account Completion Extension

This extension specifies enhanced account completion features beyond basic LSP completion.

## Smart Account Completion

### Contextual Suggestions

Servers SHOULD provide contextually relevant account suggestions:

| Context | Suggestion Priority |
|---------|---------------------|
| After `open` directive | Suggest new account names |
| In posting (debit) | Suggest expense/asset accounts |
| In posting (credit) | Suggest income/liability accounts |
| In balance assertion | Suggest accounts with balances |
| After colon in account | Suggest next component |

### Hierarchical Completion

When user types `Assets:`, suggest:
1. Existing sub-accounts (`Assets:Checking`, `Assets:Savings`)
2. Common patterns (`Assets:Bank`, `Assets:Cash`)
3. Recently created accounts

### Frequency-Based Ranking

Account suggestions SHOULD be ranked by:
1. Frequency of use in similar transactions
2. Recency of use
3. Alphabetical order

### Similar Transaction Matching

When completing a posting, analyze previous transactions with same:
- Payee
- Narration keywords
- Tags

Suggest accounts used in those transactions first.

## Configuration

```json
{
  "beancount.completion.accounts.maxSuggestions": 20,
  "beancount.completion.accounts.includeClosedAccounts": false,
  "beancount.completion.accounts.fuzzyMatch": true,
  "beancount.completion.accounts.showBalance": true,
  "beancount.completion.accounts.sortBy": "frequency"
}
```

## Example Responses

### Basic Account Completion

Request at position after `  ` in posting:

```json
{
  "items": [
    {
      "label": "Expenses:Food:Groceries",
      "kind": 7,
      "detail": "Used 45 times",
      "sortText": "0001",
      "insertText": "Expenses:Food:Groceries"
    },
    {
      "label": "Expenses:Food:Restaurant",
      "kind": 7,
      "detail": "Used 32 times",
      "sortText": "0002",
      "insertText": "Expenses:Food:Restaurant"
    }
  ]
}
```

### Partial Account Completion

Request at position after `Exp`:

```json
{
  "items": [
    {
      "label": "Expenses:Food",
      "kind": 7,
      "insertText": "Expenses:Food",
      "textEdit": {
        "range": {"start": {"line": 5, "character": 2}, "end": {"line": 5, "character": 5}},
        "newText": "Expenses:Food"
      }
    }
  ]
}
```
