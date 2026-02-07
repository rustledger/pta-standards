# hledger Format Introduction

## Overview

hledger is a plain text accounting tool that uses a human-readable file format for recording financial transactions. This specification documents hledger's journal format version 1.

## Design Philosophy

hledger prioritizes:
- **Simplicity**: Easy to read and write by hand
- **Compatibility**: High compatibility with Ledger format
- **Strictness**: Clear rules with helpful error messages
- **Power**: Rich querying and reporting capabilities

## File Extensions

| Extension | Format |
|-----------|--------|
| `.journal` | Primary hledger format |
| `.hledger` | Alternative extension |
| `.j` | Short form |
| `.ledger` | Ledger-compatible files |
| `.timeclock` | Timeclock format |
| `.timedot` | Timedot format |
| `.csv` | CSV with rules file |

## Basic Structure

An hledger journal consists of:

1. **Directives** - Configuration and declarations
2. **Transactions** - Financial movements
3. **Comments** - Documentation and notes

### Minimal Example

```hledger
; My first hledger journal

2024-01-15 Opening balance
    Assets:Checking    $1000
    Equity:Opening

2024-01-16 Groceries
    Expenses:Food    $50
    Assets:Checking
```

## Core Concepts

### Double-Entry Bookkeeping

Every transaction has at least two postings that sum to zero:

```hledger
2024-01-15 Buy coffee
    Expenses:Food:Coffee    $5.00
    Assets:Cash            $-5.00
```

### Account Hierarchy

Accounts form a tree structure using colons:

```
Assets
├── Cash
├── Bank
│   ├── Checking
│   └── Savings
└── Investments
    ├── Stocks
    └── Bonds
```

### Commodities

Amounts have associated commodities (currencies, units):

```hledger
    Assets:Bank    $1000.00        ; US dollars
    Assets:EUR     500.00 EUR      ; Euros
    Assets:Stock   10 AAPL         ; Apple shares
```

## Comparison with Other Formats

### vs Ledger

hledger is highly compatible with Ledger but differs in:
- Stricter parsing (fewer ambiguities)
- Some syntax not supported (value expressions, etc.)
- Additional features (balance assertions, CSV rules)

### vs Beancount

hledger differs from Beancount in:
- Date format (YYYY-MM-DD vs YYYY-MM-DD)
- Account hierarchy (colons vs colons with required types)
- Syntax differences (postings, directives)

## File Organization

### Single File

```hledger
; journal.hledger - All in one file
account Assets:Checking
account Expenses:Food

2024-01-15 Transaction
    Expenses:Food    $50
    Assets:Checking
```

### Multiple Files

```hledger
; main.journal
include accounts.journal
include 2024/*.journal
include prices.journal
```

## Transaction Lifecycle

1. **Recording**: Enter transaction
2. **Parsing**: Validate syntax
3. **Validation**: Check balances
4. **Reporting**: Query and analyze

## Key Features

### Balance Assertions

Verify account balances at specific points:

```hledger
2024-01-31 Month end
    Assets:Checking    $0 = $1500
    ; Assert balance is $1500
    Expenses:Misc
```

### Virtual Postings

Track budgets and allocations without affecting real balances:

```hledger
2024-01-15 Expense
    Expenses:Food    $50
    (Budget:Food)   $-50    ; Virtual
    Assets:Checking
```

### Tags and Metadata

Attach structured data to transactions:

```hledger
2024-01-15 Office supplies  ; project:office, vendor:staples
    Expenses:Office    $25
    Assets:Checking
```

### Status Markers

Track transaction verification status:

```hledger
2024-01-15 Pending check        ; Unmarked
2024-01-15 ! Pending deposit    ; Pending
2024-01-15 * Verified payment   ; Cleared
```

## Report Types

hledger supports various reports:

| Report | Command | Description |
|--------|---------|-------------|
| Balance | `hledger bal` | Account balances |
| Register | `hledger reg` | Transaction list |
| Income Statement | `hledger is` | Revenues and expenses |
| Balance Sheet | `hledger bs` | Assets, liabilities, equity |
| Cash Flow | `hledger cf` | Cash movements |

## Querying

Filter transactions with query expressions:

```bash
hledger bal date:2024
hledger reg tag:project=office
hledger bal expenses amt:'>100'
```

## Best Practices

1. **Use account declarations** for validation
2. **Include balance assertions** regularly
3. **Organize files by year** for large journals
4. **Use consistent commodities** throughout
5. **Add descriptions** to all transactions
6. **Use tags** for categorization

## Next Steps

- [Syntax Specification](syntax.md) - Detailed syntax rules
- [Transaction Directive](directives/transaction.md) - Transaction format
- [Account Directive](directives/account.md) - Account declarations
- [Examples](../examples/) - Sample journals
