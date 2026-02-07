# Report Specifications

This directory defines standard report models for plain text accounting systems.

## Report Types

| Report | Description | Specification |
|--------|-------------|---------------|
| [Balance Sheet](model/balance-sheet.md) | Assets, liabilities, equity at a point in time |
| [Income Statement](model/income-statement.md) | Revenue and expenses over a period |
| [Trial Balance](model/trial-balance.md) | All account balances for verification |
| [Register](model/register.md) | Transaction history for accounts |
| [Budget](model/budget.md) | Budget vs actual comparison |

## Common Concepts

### Date Ranges

Reports operate on date ranges:

```
# As of date (balance sheet)
--date 2024-01-31

# Period (income statement)
--begin 2024-01-01 --end 2024-01-31
```

### Account Selection

Reports can filter by account patterns:

```
# Specific account
--account Assets:Bank:Checking

# Pattern matching
--account "Assets:Bank:*"

# Account type
--type Assets,Liabilities
```

### Currency Handling

| Option | Description |
|--------|-------------|
| Native | Show all currencies as-is |
| Convert | Convert to operating currency |
| Cost | Show at cost basis |
| Market | Show at market value |

### Output Formats

| Format | Description |
|--------|-------------|
| Text | Human-readable tabular format |
| CSV | Comma-separated values |
| JSON | Structured data format |
| HTML | Web-friendly format |

## Formal Models

Alloy formal specifications verify report correctness:

- [Balance Sheet Constraints](formal/balance-sheet.als)
- [Trial Balance Constraints](formal/trial-balance.als)

## See Also

- [Core Data Model](../core/model/)
- [Query Language](../bql/)
