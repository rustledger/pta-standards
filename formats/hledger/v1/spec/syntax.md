# hledger Syntax Specification

This document defines the syntax for hledger journal files.

## File Structure

An hledger journal file consists of:
- Directives (account, commodity, include, etc.)
- Transactions
- Comments
- Whitespace

## Comments

### Line Comments

```hledger
; Semicolon comment
# Hash comment
* Asterisk comment (org-mode style)
```

### End-of-Line Comments

```hledger
2024-01-15 Groceries  ; Comment on transaction
    Expenses:Food    $50  ; Comment on posting
    Assets:Checking
```

### Block Comments

```hledger
comment
This is a block comment.
Multiple lines are allowed.
end comment
```

## Dates

### Date Formats

```hledger
2024-01-15    ; ISO format (preferred)
2024/01/15    ; Slash format
2024.01.15    ; Dot format
```

### Secondary Dates

```hledger
2024-01-15=2024-01-20 Payment  ; Posting date on right
```

## Transactions

### Basic Structure

```hledger
DATE [STATUS] [CODE] DESCRIPTION
    ACCOUNT  AMOUNT
    ACCOUNT  [AMOUNT]
```

### Examples

```hledger
2024-01-15 Groceries
    Expenses:Food    $50.00
    Assets:Checking

2024-01-15 * (#123) Cleared purchase
    Expenses:Shopping    $100.00
    Liabilities:CreditCard

2024-01-15 ! Pending transfer
    Assets:Savings    $500.00
    Assets:Checking
```

## Status Markers

| Marker | Meaning | Aliases |
|--------|---------|---------|
| (none) | Unmarked | |
| `!` | Pending | |
| `*` | Cleared | |

## Transaction Codes

Optional code in parentheses:

```hledger
2024-01-15 (#12345) Check payment
    Expenses:Rent    $1500
    Assets:Checking
```

## Accounts

### Account Names

- Colon-separated segments
- Case-sensitive
- Unicode allowed

```hledger
Assets:Bank:Checking
Liabilities:Credit Cards:Visa
Expenses:Food & Dining:Restaurants
```

### Reserved Top-Level Accounts

By convention:
- `Assets`
- `Liabilities`
- `Equity`
- `Income` (or `Revenue`)
- `Expenses`

## Amounts

### Basic Amounts

```hledger
$100.00
100.00 USD
EUR 100,00
1,234.56 USD
```

### Commodity Placement

```hledger
$100       ; Symbol before
100 USD    ; Code after
EUR 100    ; Symbol before (European)
```

### Negative Amounts

```hledger
-$100.00
$-100.00
-100.00 USD
```

### Thousand Separators

```hledger
$1,234,567.89    ; US style
1.234.567,89 EUR ; European style
1 234 567.89 USD ; Space separator
```

## Amount Inference

One posting per commodity can omit its amount:

```hledger
2024-01-15 Grocery
    Expenses:Food    $50
    Assets:Checking       ; Inferred as -$50
```

## Prices

### Per-Unit Price (@)

```hledger
    Assets:Investments    10 AAPL @ $150.00
```

### Total Price (@@)

```hledger
    Assets:EUR    100 EUR @@ $110.00
```

## Balance Assertions

### Single-Commodity Assertion (=)

```hledger
    Assets:Checking    $100 = $1500
    ; Assert Checking has exactly $1500
```

### Subaccount-Inclusive Assertion (=*)

```hledger
    Assets:Bank    $0 =* $5000
    ; Assert Assets:Bank and all subaccounts total $5000
```

### Zero Balance Check

```hledger
    Assets:Checking    $0 = $0
    ; Verify account is empty
```

## Balance Assignments

### Auto-Calculate Posting

```hledger
    Assets:Checking    = $1000
    ; Set balance TO $1000, calculate required amount
    Income:Adjustment
```

## Virtual Postings

### Unbalanced Virtual (Parentheses)

```hledger
    (Budget:Food)    $-50
    ; Not included in transaction balance
```

### Balanced Virtual (Brackets)

```hledger
    [Budget:Food]    $-50
    [Budget:Groceries]    $50
    ; Must balance with other [] postings
```

## Posting Dates

### Inline Date

```hledger
2024-01-15 Payment
    Expenses:Bill    $100  ; date:2024-01-20
    Assets:Checking
```

### Secondary Date Syntax

```hledger
    Expenses:Bill    $100  ; [2024-01-20]
```

## Tags

### Inline Tags

```hledger
2024-01-15 Groceries  ; project:home, category:food
    Expenses:Food    $50
    Assets:Checking
```

### Tag Syntax

```
name:value    ; Tag with value
name:         ; Tag without value (empty)
```

### Transaction Tags

Apply to entire transaction:

```hledger
2024-01-15 Purchase
    ; project:renovation
    Expenses:Materials    $100
    Assets:Checking
```

### Posting Tags

Apply to specific posting:

```hledger
2024-01-15 Purchase
    Expenses:Materials    $100  ; location:store-a
    Assets:Checking
```

## Whitespace Rules

### Indentation

- Postings MUST be indented
- Minimum: 1 space
- Convention: 2 or 4 spaces

### Amount Alignment

```hledger
2024-01-15 Groceries
    Expenses:Food:Groceries     $50.00
    Expenses:Food:Snacks        $10.00
    Assets:Checking            $-60.00
```

### Two-Space Separator

At least two spaces between account and amount:

```hledger
    Expenses:Food  $50.00    ; Correct: 2 spaces
    Expenses:Food $50.00     ; WRONG: 1 space
```

## Multi-Line Descriptions

Not directly supported. Use comments for continuation:

```hledger
2024-01-15 Purchase at store
    ; Additional details here
    Expenses:Shopping    $100
    Assets:Checking
```

## Character Encoding

- UTF-8 is the default encoding
- BOM is optional but supported
- Line endings: LF or CRLF

## Special Characters

### In Account Names

Allowed: letters, numbers, spaces, symbols except:
- `;` (starts comment)
- `[` `]` (virtual postings)
- `(` `)` (virtual postings)

### Escaping

No escape sequences. Use Unicode directly.

## Grammar Summary

```ebnf
journal = { entry } ;

entry = transaction
      | directive
      | comment
      | blank_line ;

transaction = date [ secondary_date ] [ status ] [ code ] description newline
              { posting } ;

posting = indent [ status ] account [ amount ] [ assertion ] [ comment ] newline ;

date = year "-" month "-" day
     | year "/" month "/" day
     | year "." month "." day ;

status = "*" | "!" ;

code = "(" text ")" ;

amount = [ "-" ] [ commodity ] number [ commodity ] ;

assertion = "=" amount
          | "=*" amount ;
```

## See Also

- [Amounts Specification](amounts.md)
- [Posting Specification](posting.md)
- [Transaction Directive](directives/transaction.md)
