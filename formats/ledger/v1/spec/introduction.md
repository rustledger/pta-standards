# Ledger Format Introduction

## Overview

Ledger is a powerful, double-entry accounting system accessed from the command line. This specification documents Ledger's journal format version 1.

## History

Ledger was created by John Wiegley in 2003 as a command-line accounting tool. It pioneered the plain text accounting approach that inspired hledger, Beancount, and many other tools.

## Design Philosophy

Ledger prioritizes:
- **Power**: Rich expression language and automation features
- **Flexibility**: Minimal required structure, maximum expressiveness
- **Speed**: Efficient processing of large journals
- **Unix Philosophy**: Composable with other command-line tools

## File Extensions

| Extension | Description |
|-----------|-------------|
| `.ledger` | Primary Ledger format |
| `.ldg` | Short form |
| `.dat` | Data file (common alternative) |
| `.journal` | Generic journal (shared with hledger) |

## Basic Structure

A Ledger journal consists of:

1. **Directives** - Configuration and declarations
2. **Transactions** - Financial movements
3. **Automated Transactions** - Rule-based auto-posting
4. **Periodic Transactions** - Budgets and forecasts
5. **Comments** - Documentation

### Minimal Example

```ledger
; My first Ledger journal

2024/01/15 Opening Balance
    Assets:Checking    $1000
    Equity:Opening

2024/01/16 Groceries
    Expenses:Food    $50
    Assets:Checking
```

## Core Concepts

### Double-Entry Bookkeeping

Every transaction has at least two postings that sum to zero:

```ledger
2024/01/15 Buy coffee
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
```

### Commodities

Amounts have associated commodities (currencies, units):

```ledger
    Assets:Bank        $1000.00
    Assets:EUR         500.00 EUR
    Assets:Stock       10 AAPL
```

## Unique Features

### Value Expressions

Ledger supports a powerful expression language:

```ledger
= expr account =~ /Expenses:Food/
    (Budget:Food)  (amount * -1)
```

### Virtual Postings

Track budgets without affecting real balances:

```ledger
2024/01/15 Expense
    Expenses:Food        $50
    (Budget:Food)       $-50    ; Virtual unbalanced
    Assets:Checking     $-50
```

### Automated Transactions

Generate postings based on rules:

```ledger
= /Grocery/
    (Budget:Food)  -1

2024/01/15 Whole Foods Grocery
    Expenses:Food    $75
    Assets:Checking
; Auto-adds: (Budget:Food) $-75
```

### Periodic Transactions

Define recurring transactions for budgeting:

```ledger
~ Monthly
    Expenses:Rent    $1500
    Assets:Checking
```

## Transaction Lifecycle

1. **Recording**: Enter transaction in journal
2. **Parsing**: Validate syntax and structure
3. **Balancing**: Verify transaction sums to zero
4. **Reporting**: Query and analyze

## Status Markers

Track transaction verification status:

```ledger
2024/01/15 Unmarked transaction
    ...

2024/01/15 ! Pending transaction
    ...

2024/01/15 * Cleared transaction
    ...
```

## Metadata and Tags

Attach structured data to transactions:

```ledger
2024/01/15 * Purchase
    ; :business:reimbursable:
    ; Receipt: photo.jpg
    Expenses:Office    $100
    Assets:Checking
```

## Report Types

Ledger supports various reports:

| Report | Command | Description |
|--------|---------|-------------|
| Balance | `ledger bal` | Account balances |
| Register | `ledger reg` | Transaction list |
| Print | `ledger print` | Formatted journal |
| Stats | `ledger stats` | Journal statistics |

## Querying

Filter transactions with expressions:

```bash
ledger bal Expenses
ledger reg @Grocery
ledger bal -p "this month"
ledger reg expr 'amount > 100'
```

## Comparison with Other Formats

### vs Beancount

Ledger differs from Beancount in:
- More flexible syntax (fewer requirements)
- Value expression language
- Virtual postings
- Automated and periodic transactions

### vs hledger

Ledger differs from hledger in:
- Full expression language
- Some syntax variations
- Different default behaviors

## Best Practices

1. **Use consistent date format** (YYYY/MM/DD recommended)
2. **Declare accounts** for validation
3. **Use meaningful payees** and notes
4. **Add tags** for categorization
5. **Regular balance assertions**
6. **Organize with includes** for large journals

## Next Steps

- [Lexical Specification](lexical.md) - Tokens and whitespace
- [Syntax Specification](syntax.md) - Grammar rules
- [Transaction Directive](directives/transaction.md) - Transaction format
- [Value Expressions](expressions/spec.md) - Expression language
