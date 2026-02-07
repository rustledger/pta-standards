# Lexical Specification

This document defines the lexical structure of Ledger files: characters, tokens, whitespace, and comments.

## Character Set

### Encoding

Ledger files MUST be encoded in UTF-8.

```
file = UTF-8 encoded text
BOM  = optional (U+FEFF at start)
```

### Line Endings

Ledger accepts:
- LF (Unix): `\n`
- CRLF (Windows): `\r\n`
- CR (legacy Mac): `\r`

Implementations SHOULD normalize to LF internally.

## Whitespace

### Horizontal Whitespace

```
SPACE = U+0020
TAB   = U+0009
```

### Significant Whitespace

| Context | Whitespace Role |
|---------|----------------|
| Line start | Indicates posting (must be indented) |
| Account/amount separator | Two spaces minimum |
| Token separator | Single space sufficient |

### Indentation

Postings MUST be indented:

```ledger
2024/01/15 Transaction
    Expenses:Food    $50    ; Indented with spaces
	Assets:Checking        ; Indented with tab
```

Minimum: 1 space or 1 tab.

## Comments

### Line Comments

Three comment styles:

```ledger
; Semicolon comment (most common)
# Hash comment
* Asterisk comment (org-mode compatible)
```

### End-of-Line Comments

```ledger
2024/01/15 Transaction  ; Header comment
    Expenses:Food    $50  ; Posting comment
    Assets:Checking
```

### Block Comments

```ledger
comment
This is a block comment.
Multiple lines are allowed.
Anything until 'end comment'.
end comment
```

### Metadata Comments

Special comment syntax for metadata:

```ledger
    Expenses:Food    $50
        ; Key: Value
        ; :tag1:tag2:
```

## Dates

### Primary Format

```
date = year "/" month "/" day
     | year "-" month "-" day
     | year "." month "." day

year  = digit digit digit digit
month = digit digit
day   = digit digit
```

### Examples

```ledger
2024/01/15    ; Slash (most common)
2024-01-15    ; Dash
2024.01.15    ; Dot
```

### Effective Dates

```ledger
2024/01/15=2024/01/20    ; Primary=Effective
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

### Thousands Separator

```ledger
$1,234,567.89    ; Comma separator
1.234.567,89 EUR ; European style
```

## Commodities

### Symbol Commodities

```
symbol = "$" | "€" | "£" | "¥" | ...
```

### Alphabetic Commodities

```
commodity = letter (letter | digit | "_" | "-" | "'")*
```

### Quoted Commodities

```
quoted_commodity = '"' (non-quote-char | '\"')* '"'
```

### Examples

```ledger
$100            ; Symbol
100 USD         ; Alphabetic
100 "ACME Inc"  ; Quoted
```

## Accounts

### Account Name

```
account = segment (":" segment)*
segment = (letter | digit | " " | "-" | "_")+
```

### Virtual Accounts

```
virtual_account          = "(" account ")"
balanced_virtual_account = "[" account "]"
```

### Examples

```ledger
Assets:Bank:Checking
Expenses:Food & Dining
(Budget:Food)
[Savings:Goal]
```

## Strings

### Payee/Narration

Unquoted text from after status/code to end of line or comment:

```ledger
2024/01/15 This is the payee text  ; Comment
```

### Quoted Strings

```
string = '"' (char | escape)* '"'
escape = "\\" | '\"' | "\n" | "\t"
```

## Status Markers

```
status = "*" | "!"
```

| Marker | Meaning |
|--------|---------|
| (none) | Unmarked |
| `!` | Pending |
| `*` | Cleared |

## Transaction Codes

```
code = "(" text ")"
```

```ledger
2024/01/15 * (#1234) Check payment
```

## Tags

### Inline Tags

```
tag_list = ":" tag (":" tag)* ":"
tag      = (letter | digit | "-" | "_")+
```

```ledger
; :personal:reimbursable:
```

### Metadata Tags

```
metadata = key ":" value
key      = (letter | digit | "-" | "_")+
value    = text
```

```ledger
; Receipt: photo.jpg
; Project: Alpha
```

## Operators

### Arithmetic

```
+ - * / ( )
```

### Comparison

```
== != < > <= >= =~ !~
```

### Logical

```
and or not
```

## Reserved Words

### Directive Keywords

```
account commodity tag payee alias include
bucket assert check define apply end
year Y D P A
```

### Expression Keywords

```
and or not expr true false
```

### Function Names

```
abs round floor ceiling truncate
total amount commodity quantity
date today year month day
any all count sum min max average
has_tag tag format join
```

## Token Examples

### Complete Transaction

```ledger
2024/01/15 * (#1234) Whole Foods  ; Weekly groceries
    ; :groceries:food:
    Expenses:Food:Groceries    $125.50
        ; Receipt: IMG_001.jpg
    Assets:Bank:Checking      $-125.50 = $1000.00
```

Tokens:
1. Date: `2024/01/15`
2. Status: `*`
3. Code: `(#1234)`
4. Payee: `Whole Foods`
5. Comment: `; Weekly groceries`
6. Tags: `:groceries:food:`
7. Account: `Expenses:Food:Groceries`
8. Amount: `$125.50`
9. Metadata: `Receipt: IMG_001.jpg`
10. Account: `Assets:Bank:Checking`
11. Amount: `$-125.50`
12. Balance assertion: `= $1000.00`

## Error Recovery

### Unterminated String

```
Error: Unterminated string at line 42
  "This string never ends
  ^
```

### Invalid Character

```
Error: Invalid character at line 42
  2024/01/15 Purchase™
                     ^
  Unexpected character: ™
```

### Invalid Date

```
Error: Invalid date at line 42
  2024/13/45 Transaction
  ^
  Month 13 and day 45 are invalid
```

## See Also

- [Syntax Specification](syntax.md)
- [Amounts Specification](amounts.md)
- [Posting Specification](posting.md)
