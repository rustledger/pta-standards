# Posting Structure

## Overview

A posting is a single line within a transaction that specifies a transfer of value to or from an account. Every transaction consists of two or more postings.

## Syntax

```ebnf
posting = INDENT [flag] account [WHITESPACE amount [cost] [price]]

flag   = "*" | "!"
cost   = "{" cost_spec "}" | "{{" cost_spec "}}"
price  = "@" amount | "@@" amount
```

## Components

### Indentation

Postings MUST be indented (at least one space or tab):

```beancount
2024-01-15 * "Transaction"
  Assets:Checking   100 USD    ; Correct: indented
  Income:Salary                 ; Correct: indented

2024-01-15 * "Invalid"
Assets:Checking   100 USD      ; ERROR: not indented
```

### Flag (Optional)

A posting may have its own flag independent of the transaction:

| Flag | Meaning |
|------|---------|
| `*` | Complete/verified |
| `!` | Incomplete/needs attention |

```beancount
2024-01-15 * "Mixed status"
  Assets:Checking   -100 USD   ; Inherits transaction flag (*)
  * Expenses:Food     50 USD   ; Explicitly complete
  ! Expenses:Other    50 USD   ; Explicitly incomplete
```

### Account

The account receiving or giving value. Must be a valid account name:

```beancount
2024-01-15 * "Transfer"
  Assets:Checking        -500 USD
  Assets:Savings          500 USD
```

### Amount (Optional)

A number followed by a currency:

```beancount
2024-01-15 * "Purchase"
  Assets:Checking   -85.50 USD
  Expenses:Food      85.50 USD
```

When omitted, the amount is computed to balance the transaction:

```beancount
2024-01-15 * "Purchase"
  Assets:Checking   -85.50 USD
  Expenses:Food                   ; Computed as 85.50 USD
```

### Cost Specification (Optional)

Records the acquisition cost of commodities:

```beancount
2024-01-15 * "Buy stock"
  Assets:Brokerage   10 AAPL {150 USD}      ; Per-unit cost
  Assets:Brokerage   10 AAPL {{1500 USD}}   ; Total cost
  Assets:Cash       -1500 USD
```

See [costs.md](costs.md) for full cost specification documentation.

### Price Annotation (Optional)

Records the exchange rate for currency conversion:

```beancount
2024-01-15 * "Exchange"
  Assets:EUR   100 EUR @ 1.10 USD    ; Per-unit price
  Assets:EUR   100 EUR @@ 110 USD    ; Total price
  Assets:USD  -110 USD
```

See [prices.md](prices.md) for full price annotation documentation.

## Amount Elision

### Rules

1. At most one posting per currency MAY omit its amount
2. The omitted amount is computed to make the transaction balance

### Valid Examples

```beancount
; One elided posting
2024-01-15 * "Simple"
  Assets:Checking   100 USD
  Income:Salary               ; = -100 USD

; Multiple currencies, one elision per currency
2024-01-15 * "Multi-currency"
  Assets:EUR        100 EUR
  Assets:USD        110 USD
  Income:Gift:EUR             ; = -100 EUR
  Income:Gift:USD             ; = -110 USD
```

### Invalid Examples

```beancount
; ERROR: Two elided postings for same currency
2024-01-15 * "Ambiguous"
  Assets:Checking   100 USD
  Expenses:Food
  Expenses:Coffee             ; Which gets how much?

; ERROR: Cannot compute without other amounts
2024-01-15 * "Empty"
  Assets:Checking
  Income:Salary               ; No amounts to compute from
```

## Weight Calculation

The posting weight determines how it contributes to transaction balancing:

| Posting Type | Weight Formula |
|--------------|----------------|
| Simple amount | amount |
| With cost `{cost}` | units × cost |
| With total cost `{{cost}}` | cost |
| With price `@ price` | units × price |
| With total price `@@ price` | price |
| Cost + Price | units × cost (price is informational) |

### Examples

```beancount
; Simple: weight = 100 USD
Assets:Checking  100 USD

; Cost: weight = 10 × 150 = 1500 USD
Assets:Stock  10 AAPL {150 USD}

; Total cost: weight = 1500 USD
Assets:Stock  10 AAPL {{1500 USD}}

; Price: weight = 100 × 1.10 = 110 USD
Assets:EUR  100 EUR @ 1.10 USD

; Total price: weight = 110 USD
Assets:EUR  100 EUR @@ 110 USD

; Cost + Price: weight = 10 × 150 = 1500 USD (price ignored for balance)
Assets:Stock  10 AAPL {150 USD} @ 180 USD
```

## Posting Metadata

Metadata can be attached to individual postings with double indentation:

```beancount
2024-01-15 * "Purchase"
  transaction-meta: "value"           ; Transaction metadata (single indent)
  Assets:Checking   -85.50 USD
    bank-ref: "TXN123"                ; Posting metadata (double indent)
    category: "groceries"
  Expenses:Food      85.50 USD
    receipt: "scan.pdf"
```

## Arithmetic Expressions

Amounts support arithmetic expressions:

```beancount
2024-01-15 * "Split dinner"
  Assets:Checking        -75.00 USD
  Expenses:Food:Mine     (75.00 / 3) USD
  Expenses:Food:Alice    (75.00 / 3) USD
  Expenses:Food:Bob      (75.00 / 3) USD
```

Supported operators:
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Parentheses: `(` `)`

## Balance Verification

After parsing all postings:

1. Compute weight of each posting
2. Sum weights by currency
3. Each currency's sum must equal zero (within tolerance)

```beancount
2024-01-15 * "Balanced"
  Assets:Checking   -100.00 USD    ; -100 USD
  Expenses:Food       50.00 USD    ; +50 USD
  Expenses:Coffee     50.00 USD    ; +50 USD
  ; Sum: -100 + 50 + 50 = 0 ✓
```

## Posting Order

Posting order within a transaction:
- Is preserved for display purposes
- Does NOT affect validation
- Does NOT affect booking (unless explicitly configured)

## Examples

### Basic Transfer

```beancount
2024-01-15 * "ATM Withdrawal"
  Assets:Cash         200.00 USD
  Assets:Checking    -200.00 USD
```

### Purchase with Elision

```beancount
2024-01-15 * "Grocery shopping"
  Expenses:Food        85.50 USD
  Assets:Checking                    ; -85.50 USD computed
```

### Stock Purchase with Cost

```beancount
2024-01-15 * "Buy Apple stock"
  Assets:Brokerage    10 AAPL {185.50 USD}
  Expenses:Commission   9.99 USD
  Assets:Cash                        ; -1864.99 USD computed
```

### Currency Exchange with Price

```beancount
2024-01-15 * "EUR to USD"
  Assets:EUR  -100 EUR @ 1.10 USD    ; Gives 100 EUR
  Assets:USD   110 USD               ; Gets 110 USD
```

### Complex Transaction

```beancount
2024-01-15 * "Stock sale with commission"
  Assets:Brokerage    -10 AAPL {150 USD} @ 185 USD
    lot-id: "2023-buy"
  Assets:Cash         1840.01 USD
    bank-ref: "DEP123"
  Expenses:Commission    9.99 USD
  Income:CapitalGains               ; -350 USD gain computed
```

## Validation Errors

| Error | Condition |
|-------|-----------|
| E3001 | Transaction does not balance |
| E3002 | Multiple postings missing amounts for same currency |
| E1001 | Account not opened |
| E1003 | Account closed before posting date |
| E5002 | Currency not allowed in account |
