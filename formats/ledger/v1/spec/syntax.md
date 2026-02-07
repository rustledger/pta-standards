# Ledger Syntax Specification

This document specifies the lexical structure and syntax rules for Ledger format files.

## File Structure

A Ledger file consists of:
- Zero or more directives
- Separated by blank lines
- With optional comments

### Character Encoding

- Files MUST be valid UTF-8
- BOM (Byte Order Mark) SHOULD NOT be present
- Line endings: LF (Unix) or CRLF (Windows)

### Whitespace

| Character | Name | Usage |
|-----------|------|-------|
| Space (0x20) | Space | General separator |
| Tab (0x09) | Tab | Posting indentation |
| LF (0x0A) | Newline | Line terminator |
| CR (0x0D) | Carriage return | Part of CRLF |

### Comments

```ledger
; This is a line comment
# This is also a comment (hash style)
* This line is ignored (star at column 0)

2024/01/15 Transaction
    ; This is a posting comment
    Expenses:Food  $50  ; Inline comment
    Assets:Checking
```

Comment rules:
- `;` or `#` at start of line: entire line is a comment
- `;` after posting: inline comment
- `*` at column 0: line is ignored (org-mode compatibility)

## Date Format

Ledger accepts multiple date formats:

```
YYYY/MM/DD    ; Canonical format
YYYY-MM-DD    ; ISO format
YYYY.MM.DD    ; Dot separator
MM/DD         ; Uses default year (Y directive)
MM/DD/YYYY    ; US format
DD/MM/YYYY    ; European format (with --european flag)
```

### Date Components

| Component | Range | Leading Zero |
|-----------|-------|--------------|
| Year | 0001-9999 | Required (4 digits) |
| Month | 01-12 | Optional |
| Day | 01-31 | Optional |

### Effective Dates

```ledger
2024/01/15=2024/01/20 Future Payment
    ; Transaction date is 01/15, effective date is 01/20
    Expenses:Bills  $100
    Assets:Checking
```

## Account Names

Account names are hierarchical paths separated by colons:

```
Assets:Bank:Checking
Expenses:Food:Groceries
Liabilities:Credit Card:Visa
Income:Salary
Equity:Opening Balances
```

### Rules

1. Components separated by `:` (colon)
2. No leading or trailing colons
3. Components can contain:
   - Letters (Unicode letters allowed)
   - Digits (not as first character)
   - Spaces (embedded, not leading/trailing)
   - Hyphens, underscores
4. Case-insensitive comparison (but case is preserved)

### Special Characters

These characters are NOT allowed in account names:
- `:` (except as separator)
- `[`, `]`, `(`, `)` (virtual posting markers)
- `@`, `{`, `}` (price/cost markers)
- `;` (comment marker)

## Amount Format

### Basic Amounts

```ledger
$100.00          ; Symbol prefix
100.00 USD       ; Code suffix
-$50.00          ; Negative with prefix symbol
-50.00 EUR       ; Negative with suffix code
$1,234.56        ; With thousand separators
1.234,56 EUR     ; European format
```

### Commodity Symbols

| Type | Example | Position |
|------|---------|----------|
| Symbol | `$`, `€`, `£` | Prefix |
| Code | `USD`, `EUR` | Suffix |
| Quoted | `"AAPL"` | Either |

### Precision

- Amounts preserve display precision
- Internal calculations use higher precision
- Display precision derived from commodity format directive

## Posting Format

```
    ACCOUNT  AMOUNT [@ PRICE] [= BALANCE] [; COMMENT]
```

### Indentation

- Postings MUST be indented
- At least one space or tab
- Convention: 4 spaces or 1 tab

### Components

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 AAPL @ $150.00  ; price annotation
    Assets:Brokerage    10 AAPL {$150.00}  ; lot cost
    Assets:Checking    $-1500.00 = $500.00 ; balance assertion
```

## Value Expressions

Ledger supports arithmetic expressions in amounts:

```ledger
2024/01/15 Split Bill
    Expenses:Food      ($100 / 3)
    Assets:Checking

2024/01/15 Tax Calculation
    Expenses:Tax       ($1000 * 0.25)
    Assets:Checking
```

### Operators

| Operator | Description |
|----------|-------------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `()` | Grouping |

### Functions

See [expressions/functions.md](../expressions/functions.md) for built-in functions.

## Metadata

Metadata is key-value pairs attached to transactions or postings:

```ledger
2024/01/15 * Grocery Store
    ; Payee: Whole Foods
    ; Category: groceries
    Expenses:Food      $50.00
        ; Receipt: receipt-001.pdf
    Assets:Checking
```

### Tag Syntax

```ledger
2024/01/15 * Transaction
    ; :tag1:tag2:tag3:
    Expenses:Food  $50
    Assets:Checking
```

## Virtual Postings

### Unbalanced Virtual Postings

```ledger
2024/01/15 * Budget Entry
    Expenses:Food        $50.00
    (Budget:Food)       $-50.00    ; Virtual, unbalanced
    Assets:Checking
```

### Balanced Virtual Postings

```ledger
2024/01/15 * Savings Goal
    Assets:Checking      $100.00
    [Savings:Goal]      $-100.00   ; Virtual, balanced
    Income:Salary
```

## Line Continuation

Long lines can be continued with a backslash:

```ledger
2024/01/15 * Very Long Transaction Description \
             That Continues On Next Line
    Expenses:Food  $50.00
    Assets:Checking
```

## Include Directive

```ledger
include accounts.ledger
include ~/finances/2024/*.ledger
```

Paths can be:
- Relative to current file
- Absolute paths
- Glob patterns

## Grammar Summary (EBNF)

```ebnf
journal = { directive | comment | blank_line } ;

directive = transaction
          | account_directive
          | commodity_directive
          | price_directive
          | include_directive
          | alias_directive
          | bucket_directive
          | year_directive
          | automated_transaction
          | periodic_transaction ;

transaction = date [ effective_date ] [ flag ] description newline
              { posting } ;

posting = indent account [ amount ] [ price ] [ balance ] [ comment ] newline ;

amount = [ "-" ] ( commodity_symbol value | value commodity_code ) ;

value = digit { digit | "," | "." } ;
```

## See Also

- [Amounts Specification](amounts.md)
- [Posting Specification](posting.md)
- [Transaction Directive](directives/transaction.md)
- [Value Expressions](../expressions/spec.md)
