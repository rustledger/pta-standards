# Open Directive

## Overview

The `open` directive declares an account's existence and optionally constrains its allowed currencies and booking method.

## Syntax

```ebnf
open = date WHITESPACE "open" WHITESPACE account
       [WHITESPACE currency_list]
       [WHITESPACE booking_method]
       (NEWLINE metadata)*

currency_list  = currency ("," currency)*
booking_method = string
```

## Components

### Date

The date the account becomes available for use. Postings to this account before this date will produce validation errors.

### Account

The full account name including root type:

```beancount
2024-01-01 open Assets:US:BofA:Checking
2024-01-01 open Liabilities:CreditCard:Chase
2024-01-01 open Expenses:Food:Groceries
```

### Currency Constraint

Optional list of allowed currencies:

```beancount
; Allow only USD
2024-01-01 open Assets:Checking USD

; Allow multiple currencies
2024-01-01 open Assets:Brokerage USD,EUR,AAPL,MSFT

; Allow any currency (default)
2024-01-01 open Expenses:Food
```

When specified, postings using other currencies will produce validation errors.

### Booking Method

Optional string specifying how lot matching works for reductions:

```beancount
2024-01-01 open Assets:Brokerage USD,AAPL "FIFO"
2024-01-01 open Assets:Retirement USD,VTSAX "LIFO"
2024-01-01 open Assets:Trading USD,BTC "STRICT"
```

## Booking Methods

| Method | Description |
|--------|-------------|
| `STRICT` | Require exact lot specification (default) |
| `FIFO` | First-in, first-out |
| `LIFO` | Last-in, first-out |
| `HIFO` | Highest cost first |
| `NONE` | Allow any reduction (no lot tracking) |
| `AVERAGE` | Use average cost basis |
| `AVERAGE_ONLY` | Average cost, merge on acquisition |

See [booking.md](../booking.md) for detailed booking method documentation.

## Examples

### Basic Account

```beancount
2024-01-01 open Assets:Checking
```

### With Currency Constraint

```beancount
2024-01-01 open Assets:US:Schwab:Cash USD
2024-01-01 open Assets:EU:Bank:Cash EUR
```

### With Booking Method

```beancount
; Retirement account with FIFO booking
2024-01-01 open Assets:Retirement:401k USD,VTSAX "FIFO"

; Trading account requiring explicit lot selection
2024-01-01 open Assets:Trading:Coinbase USD,BTC,ETH "STRICT"
```

### With Metadata

```beancount
2024-01-01 open Assets:Checking USD
  institution: "Bank of America"
  account-number: "****1234"
  opened-by: "online"
```

## Account Naming

### Root Types

Every account MUST start with one of five root types:

| Root | Purpose | Normal Balance |
|------|---------|----------------|
| `Assets` | Things you own | Debit |
| `Liabilities` | Things you owe | Credit |
| `Equity` | Net worth, opening balances | Credit |
| `Income` | Money received | Credit |
| `Expenses` | Money spent | Debit |

### Component Rules

- Components are separated by colons (`:`)
- Each component MUST begin with a capital letter
- Subsequent characters may be letters, numbers, or hyphens
- Components MUST NOT contain spaces

### Valid Examples

```
Assets:US:BofA:Checking
Liabilities:CreditCard:Chase-Sapphire
Expenses:Food:Groceries
Income:Salary:2024
Equity:Opening-Balances
```

### Invalid Examples

```
assets:Checking           ; lowercase root
Assets:checking           ; lowercase component
Assets:My Checking        ; space in component
Assets::Checking          ; empty component
Savings:Account           ; invalid root type
```

## Validation

| Error | Condition |
|-------|-----------|
| E1002 | Account already opened (duplicate open) |
| E1005 | Invalid account name |
| E5002 | Posting uses currency not in constraint list |

## Implicit Opens

Some implementations support implicit account opening (creating accounts on first use). This is controlled by the option:

```beancount
option "allow_implicit_open" "TRUE"
```

When enabled, accounts are automatically opened on their first use. This is NOT recommended for production ledgers.

## Relationship to Close

Accounts opened with `open` can be closed with `close`:

```beancount
2020-01-01 open Assets:OldAccount USD
; ... transactions ...
2024-12-31 close Assets:OldAccount
```

After closing, the account cannot be used in new postings.

## Implementation Notes

1. Store the open date for lifecycle validation
2. Store currency constraints for posting validation
3. Store booking method for inventory operations
4. Track all opened accounts for reference validation
