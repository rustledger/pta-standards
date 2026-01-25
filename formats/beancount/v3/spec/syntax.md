# Beancount Syntax Overview

This document provides an overview of Beancount syntax.
Individual directives are documented in the [directives/](directives/) directory.

## Core Concepts

Beancount is a declarative text-based double-entry bookkeeping system.
Input files contain directives (entries) with dates and types, plus optional global options.

## File Structure

A Beancount file consists of:

1. **Options** - Global configuration (undated)
2. **Directives** - Dated accounting entries
3. **Comments** - Documentation (ignored by parser)

```beancount
; Options at top
option "title" "My Ledger"
option "operating_currency" "USD"

; Directives follow
2024-01-01 open Assets:Checking USD

2024-01-15 * "Payee" "Description"
  Assets:Checking   100.00 USD
  Income:Salary
```

## Date Format

All directives begin with dates in ISO 8601 format:

```
YYYY-MM-DD
```

Both dash and slash variants are accepted:
- `2024-02-03` (preferred)
- `2024/02/03`

## Comments

Lines starting with semicolon are comments:

```beancount
; This is a comment
2024-01-01 * "Transaction"
  Assets:Cash  -20 USD  ; inline comment
  Expenses:Food
```

Non-directive lines are silently ignored, enabling org-mode formatting.

## Accounts

Account names consist of colon-separated components:

```
RootType:Component:Component:...
```

### Root Types

Every account MUST start with one of five root types:

| Root Type | Purpose |
|-----------|---------|
| `Assets` | Things you own |
| `Liabilities` | Things you owe |
| `Equity` | Net worth / opening balances |
| `Income` | Money received |
| `Expenses` | Money spent |

### Component Rules

- MUST start with a capital letter or number
- MAY contain letters, numbers, and dashes
- MUST NOT contain spaces or special characters

**Examples:**
```
Assets:US:BofA:Checking
Assets:US:BofA:Savings
Expenses:Food:Groceries
Liabilities:CreditCard:Chase
```

## Commodities/Currencies

Currency names are recognized by syntax:

- All capital letters
- 1-24 characters long
- MUST start and end with capital letters or numbers
- Middle characters: letters, numbers, apostrophes, periods, underscores, dashes

**Examples:**
```
USD     ; US Dollar
EUR     ; Euro
MSFT    ; Stock
VACHR   ; Custom (vacation hours)
BTC     ; Cryptocurrency
```

No pre-declaration required (though `commodity` directive is available).

## Amounts

An amount is a number followed by a currency:

```
100.00 USD
-50 EUR
1,234.56 CAD
```

### Number Format

- Decimal point: `.`
- Grouping separator: `,` (optional)
- Negative: `-` prefix

### Arithmetic Expressions

Amounts support expressions:

```beancount
2024-01-01 * "Split"
  Expenses:Food  (100 / 3) USD
  Assets:Cash
```

Operators: `+`, `-`, `*`, `/`, `(`, `)`

## Strings

Text enclosed in double quotes:

```beancount
"Simple string"
"Multi-line
string allowed"
```

Strings MAY span multiple lines.

## Tags

Hash-prefixed identifiers for categorizing:

```beancount
2024-01-15 * "Flight" #berlin-trip #travel
  Expenses:Flights  -1230.27 USD
  Liabilities:CreditCard
```

### Tag Stack

Apply tags to multiple directives:

```beancount
pushtag #berlin-trip
2024-04-23 * "Hotel"
  ...
2024-04-24 * "Restaurant"
  ...
poptag #berlin-trip
```

## Links

Caret-prefixed identifiers connecting related transactions:

```beancount
2024-02-05 * "Invoice" ^invoice-001
  Income:Clients  -8450.00 USD
  Assets:Receivable

2024-02-20 * "Payment" ^invoice-001
  Assets:Checking  8450.00 USD
  Assets:Receivable
```

## Metadata

Key-value pairs attached to directives or postings:

```beancount
2024-01-15 * "Purchase"
  receipt: "photo.jpg"
  Assets:Cash  -50 USD
    category: "groceries"
  Expenses:Food
```

### Key Format

- MUST start with lowercase letter
- MAY contain letters, numbers, dashes, underscores

### Value Types

- Strings: `"text"`
- Numbers: `123.45`
- Dates: `2024-01-15`
- Accounts: `Assets:Cash`
- Currencies: `USD`
- Tags: `#tag`
- Amounts: `100 USD`
- Booleans: `TRUE`, `FALSE`

## Directive Types

| Directive | Purpose |
|-----------|---------|
| `open` | Declare account existence |
| `close` | Mark account as inactive |
| `commodity` | Declare currency with metadata |
| `transaction` | Financial exchange |
| `balance` | Assert account balance |
| `pad` | Auto-generate balancing entry |
| `note` | Attach comment to account |
| `document` | Link external file |
| `price` | Record exchange rate |
| `event` | Track variable over time |
| `query` | Embed SQL query |
| `custom` | User-defined directive |

See [directives/](directives/) for detailed documentation of each.

## Entry Ordering

Directives are automatically sorted chronologically after parsing.
Within the same date:

1. Balance assertions and other non-transaction directives first
2. Transactions after

File order is preserved for directives with identical date and type.

## Includes

Split files across documents:

```beancount
include "accounts.beancount"
include "2024/january.beancount"
```

Relative paths resolve to including file's directory.

## Plugins

Load transformation modules:

```beancount
plugin "beancount.plugins.implicit_prices"
plugin "my_plugin" "config_string"
```
