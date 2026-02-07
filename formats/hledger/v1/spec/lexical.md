# hledger Lexical Specification

This document defines the lexical structure of hledger journal files.

## Character Set

### Encoding

hledger files MUST be UTF-8 encoded.

```
file = UTF-8 encoded text
BOM  = optional (U+FEFF at start)
```

### Line Endings

Supported line endings:
- LF (Unix): `\n`
- CRLF (Windows): `\r\n`

## Whitespace

### Horizontal Whitespace

```
SPACE = U+0020
TAB   = U+0009
```

### Significance

| Context | Rule |
|---------|------|
| Line start | Indicates posting (must be indented) |
| Account/amount | Two or more spaces separate |
| Token separation | Single space sufficient |

### Indentation

Postings require indentation:

```hledger
2024-01-15 Transaction
    expenses:food    $50   ; Spaces
	assets:cash            ; Tab also OK
```

## Comments

### Line Comments

```hledger
; Semicolon comment (primary)
# Hash comment
* Star comment
```

### Inline Comments

```hledger
2024-01-15 Payee  ; Comment after payee
    account    $50  ; Comment after amount
```

### Comment Block

```hledger
comment
This is a multi-line comment.
Everything until 'end comment'.
end comment
```

## Dates

### Formats

```hledger
2024-01-15    ; Dash separator (preferred)
2024/01/15    ; Slash separator
2024.01.15    ; Dot separator
```

### Secondary Date

```hledger
2024-01-15=2024-01-20    ; Primary=Secondary
```

## Numbers

### Integer

```
integer = ["-"] digit+
```

### Decimal

```
decimal = ["-"] digit* "." digit+
        | ["-"] digit+ ["." digit*]
```

### With Grouping

```hledger
1,000.00        ; Comma grouping
1.000,00        ; European style
1 000.00        ; Space grouping
```

## Commodities

### Symbol Commodities

```hledger
$100            ; Dollar
€100            ; Euro
£100            ; Pound
¥100            ; Yen
```

### Alphabetic Commodities

```hledger
100 USD
100 EUR
10 AAPL
1.5 BTC
```

### Quoted Commodities

```hledger
100 "MUTUAL FUND"
10 "Company Stock"
```

## Accounts

### Structure

```
account = segment (":" segment)*
segment = non-whitespace+
```

### Examples

```hledger
assets:bank:checking
expenses:food:groceries
liabilities:credit card
```

### Virtual Accounts

```hledger
(budget:food)           ; Unbalanced virtual
[savings:goal]          ; Balanced virtual
```

## Strings

### Payee/Description

Unquoted text after date/status:

```hledger
2024-01-15 This is the description text
```

### Quoted Values

```hledger
commodity "US DOLLARS"
```

## Status Markers

| Marker | Meaning |
|--------|---------|
| (none) | Unmarked |
| `!` | Pending |
| `*` | Cleared |

```hledger
2024-01-15 Unmarked
2024-01-15 ! Pending
2024-01-15 * Cleared
```

## Transaction Codes

```hledger
2024-01-15 (#1234) With code
2024-01-15 (check 567) Another code
```

## Tags

### Inline Format

```hledger
; tag1:, tag2:value, tag3:another value
```

### Colon Format

```hledger
; :tag1:tag2:tag3:
```

## Reserved Words

### Directives

```
account commodity include payee tag
decimal-mark alias apply year
comment end
```

### Special

```
assert check
```

## Token Examples

### Full Transaction

```hledger
2024-01-15 * (123) Grocery Store  ; weekly shopping
    ; :food:groceries:
    expenses:food:groceries    $50.00
        ; receipt: scan.pdf
    assets:bank:checking       $-50.00 = $1000.00
```

Tokens:
1. Date: `2024-01-15`
2. Status: `*`
3. Code: `(123)`
4. Description: `Grocery Store`
5. Comment: `; weekly shopping`
6. Tags: `:food:groceries:`
7. Account: `expenses:food:groceries`
8. Amount: `$50.00`
9. Metadata: `receipt: scan.pdf`
10. Account: `assets:bank:checking`
11. Amount: `$-50.00`
12. Balance assertion: `= $1000.00`

## See Also

- [Syntax Specification](syntax.md)
- [Amounts Specification](amounts.md)
