# Account Directive

The `account` directive declares an account and its properties.

## Syntax

```hledger
account ACCOUNTNAME
    [SUBDIRECTIVE]...
```

## Basic Declaration

```hledger
account Assets:Checking
account Expenses:Food
account Liabilities:Credit Card
```

## Purpose

Account directives serve several purposes:

1. **Validation** - Only declared accounts can be used
2. **Documentation** - Describe account purpose
3. **Type inference** - Specify account type
4. **Completion** - Enable editor autocomplete

## Subdirectives

### Type Subdirective

Explicitly set the account type:

```hledger
account Assets:Crypto
    type: Asset

account Revenue:Sales
    type: Revenue
```

Valid types: `Asset`, `Liability`, `Equity`, `Revenue`, `Expense`, `Cash`

### Alias Subdirective

Define shorthand names:

```hledger
account Assets:Bank:First National Checking
    alias: checking
    alias: fnc
```

Usage:

```hledger
2024-01-15 Deposit
    checking    $100    ; Expands to Assets:Bank:First National Checking
    Income:Salary
```

### Note Subdirective

Add description:

```hledger
account Assets:Emergency Fund
    note: 6 months of expenses for emergencies

account Expenses:Medical
    note: Healthcare costs including insurance and copays
```

### Default Subdirective

Mark as default account:

```hledger
account Assets:Checking
    default
```

## Account Types

### Automatic Type Inference

hledger infers type from account name prefix:

| Prefix | Type |
|--------|------|
| `assets:` | Asset |
| `liabilities:` | Liability |
| `equity:` | Equity |
| `revenues:` | Revenue |
| `income:` | Revenue |
| `expenses:` | Expense |

### Explicit Type

Override inference with type subdirective:

```hledger
account Investments:Retirement
    type: Asset

account Opening Balances
    type: Equity
```

## Hierarchical Declaration

Declare parent and children separately:

```hledger
account Assets
account Assets:Bank
account Assets:Bank:Checking
account Assets:Bank:Savings
```

Or use indentation (visual grouping only):

```hledger
account Assets
  account Assets:Bank
    account Assets:Bank:Checking
    account Assets:Bank:Savings
```

## Account Names

### Valid Characters

- Letters (Unicode supported)
- Numbers
- Spaces
- Colons (as separator)
- Most punctuation except `;`, `[`, `]`, `(`, `)`

### Examples

```hledger
account Assets:Bank:Checking
account Liabilities:Credit Cards:Visa
account Expenses:Food & Dining
account Assets:Währung:EUR
account Assets:日本円
```

## Validation Mode

With `--strict` or `--pedantic`:

```hledger
; Undeclared account causes error
2024-01-15 Transaction
    Expenses:Foood    $50    ; Error: undeclared
    Assets:Checking
```

## Multiple Declarations

Account can be declared multiple times:

```hledger
account Assets:Checking

; Later in file or included file
account Assets:Checking
    note: Primary checking account
    alias: checking
```

Properties are merged.

## Complete Example

```hledger
; ===== Account Declarations =====

; Asset accounts
account Assets
    type: Asset
    note: All owned resources

account Assets:Bank:Checking
    alias: checking
    note: Primary transaction account

account Assets:Bank:Savings
    alias: savings
    note: Emergency fund

account Assets:Investments:Brokerage
    alias: brokerage
    note: Stock investments

; Liability accounts
account Liabilities:Credit Card:Visa
    alias: visa
    type: Liability

account Liabilities:Mortgage
    type: Liability
    note: Home loan 30-year fixed

; Equity
account Equity:Opening Balances
    type: Equity

; Income
account Income:Salary
    type: Revenue
    alias: salary

account Income:Interest
    type: Revenue

; Expenses
account Expenses:Food:Groceries
    type: Expense
    alias: groceries

account Expenses:Food:Restaurants
    type: Expense
    alias: dining

account Expenses:Housing:Rent
    type: Expense

account Expenses:Utilities
    type: Expense
```

## Command Line

```bash
# List all accounts
hledger accounts

# Check for undeclared accounts
hledger check accounts

# Use strict mode
hledger bal --strict
```

## See Also

- [Commodity Directive](commodity.md)
- [Syntax Specification](../syntax.md)
