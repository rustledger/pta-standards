# Lexical Structure

## Overview

This document specifies the lexical elements of Beancount: character encoding, whitespace, comments, and tokens.

## Character Encoding

### UTF-8

Beancount files MUST be encoded in UTF-8:

```
Content-Type: text/plain; charset=utf-8
```

### BOM Handling

The UTF-8 BOM (Byte Order Mark, `EF BB BF`) at the start of a file:
- SHOULD be accepted without error
- MUST be ignored (not treated as content)
- SHOULD NOT be written by formatters

### Unicode Normalization

Implementations SHOULD normalize Unicode to NFC (Canonical Composition) for:
- Account name comparison
- Currency symbol comparison
- Metadata key comparison

## Line Structure

### Line Endings

All standard line endings are accepted:

| Sequence | Name | Platform |
|----------|------|----------|
| `\n` | LF | Unix/Linux/macOS |
| `\r\n` | CRLF | Windows |
| `\r` | CR | Classic Mac (rare) |

Implementations SHOULD normalize to `\n` internally.

### Line Length

There is no specified maximum line length. However:
- Implementations SHOULD support lines up to 10,000 characters
- Implementations MAY warn about excessively long lines
- Formatters SHOULD wrap at reasonable widths (80-120 chars)

## Whitespace

### Significant Whitespace

Indentation is significant for:
- Postings (must be indented)
- Metadata (must be indented)
- Posting metadata (must be double-indented)

```beancount
2024-01-15 * "Transaction"        ; No indent
  metadata: "value"               ; Single indent (transaction metadata)
  Account:Name  100 USD           ; Single indent (posting)
    posting-meta: "value"         ; Double indent (posting metadata)
```

### Whitespace Characters

| Character | Code Point | Name |
|-----------|------------|------|
| Space | U+0020 | SPACE |
| Tab | U+0009 | HORIZONTAL TAB |

Other whitespace characters (non-breaking space, etc.) are NOT treated as whitespace.

### Indentation

Indentation MUST be:
- At least one space or tab
- Consistent within a file (recommended)

Tabs and spaces MAY be mixed, but this is NOT recommended.

### Trailing Whitespace

Trailing whitespace on lines:
- MUST be ignored by parsers
- SHOULD be removed by formatters

## Comments

### Line Comments

Comments begin with semicolon (`;`) and extend to end of line:

```beancount
; This is a full-line comment
2024-01-15 * "Transaction"  ; This is an inline comment
  Account:Name  100 USD     ; Another inline comment
```

### Comment Position

Comments are valid:
- On their own line
- After any directive or posting
- After metadata values

```beancount
; Standalone comment
2024-01-15 * "Transaction"  ; After directive
  key: "value"              ; After metadata
  Account:Name  100 USD     ; After posting
```

### Non-Directive Lines

Lines that don't start with a recognized pattern are silently ignored:

```beancount
* This line is ignored (not a valid directive)
Random text is also ignored

2024-01-15 * "Valid transaction"
  Assets:Cash  100 USD
  Income:Gift
```

This enables org-mode style formatting:

```beancount
* 2024 Finances

** January

2024-01-15 * "Salary"
  Assets:Checking  3000 USD
  Income:Salary
```

## Tokens

### Date

ISO 8601 date format:

```ebnf
date = YYYY "-" MM "-" DD
     | YYYY "/" MM "/" DD

YYYY = digit{4}
MM   = digit{2}
DD   = digit{2}
```

Examples:
```
2024-01-15
2024/01/15
```

Both separators are equivalent. Dash (`-`) is preferred.

### Account

Colon-separated components starting with root type:

```ebnf
account = root_type (":" component)+

root_type = "Assets" | "Liabilities" | "Equity" | "Income" | "Expenses"
component = capital_start alphanumeric_dash*

capital_start    = [A-Z] | [0-9]
alphanumeric_dash = [A-Za-z0-9-]
```

Examples:
```
Assets:Checking
Assets:US:BofA:Checking
Liabilities:CreditCard:Chase-Sapphire
Expenses:Food:Groceries
Income:Salary:2024
```

### Currency

Uppercase identifier:

```ebnf
currency = uppercase_letter (currency_char)* uppercase_letter?

uppercase_letter = [A-Z]
currency_char    = [A-Z0-9'._-]
```

Length: 1-24 characters

Examples:
```
USD
EUR
AAPL
VTSAX
BTC
AU
VACHR
```

### Number

Decimal number with optional sign and grouping:

```ebnf
number = sign? digits ("." digits)?
       | sign? "." digits

sign   = "-"
digits = digit+ ("," digit+)*
digit  = [0-9]
```

Examples:
```
100
100.00
-50.25
1,234.56
1,234,567.89
.50
```

Grouping separator (`,`) is optional and ignored.

### String

Double-quoted text:

```ebnf
string = '"' string_char* '"'

string_char = [^"\\]
            | '\\' escape_char

escape_char = '"' | '\\' | 'n' | 't' | 'r'
```

Strings MAY span multiple lines:

```beancount
2024-01-15 * "Multi-line
narration is
allowed"
  Assets:Cash  100 USD
  Income:Gift
```

Escape sequences:
| Sequence | Character |
|----------|-----------|
| `\"` | Double quote |
| `\\` | Backslash |
| `\n` | Newline |
| `\t` | Tab |
| `\r` | Carriage return |

### Tag

Hash-prefixed identifier:

```ebnf
tag = "#" tag_char+

tag_char = [A-Za-z0-9-_/]
```

Examples:
```
#travel
#berlin-trip
#2024/q1
#tax_deductible
```

### Link

Caret-prefixed identifier:

```ebnf
link = "^" link_char+

link_char = [A-Za-z0-9-_/]
```

Examples:
```
^invoice-001
^project/2024
^ref_12345
```

### Metadata Key

Lowercase identifier:

```ebnf
metadata_key = lowercase_letter (alphanumeric_dash_underscore)*

lowercase_letter = [a-z]
alphanumeric_dash_underscore = [A-Za-z0-9-_]
```

Examples:
```
filename
invoice-number
receipt_url
check123
```

### Boolean

```ebnf
boolean = "TRUE" | "FALSE"
```

Case-sensitive (must be uppercase).

### Keywords

Reserved keywords:

| Keyword | Usage |
|---------|-------|
| `txn` | Transaction flag |
| `open` | Open directive |
| `close` | Close directive |
| `commodity` | Commodity directive |
| `pad` | Pad directive |
| `balance` | Balance directive |
| `price` | Price directive |
| `event` | Event directive |
| `query` | Query directive |
| `note` | Note directive |
| `document` | Document directive |
| `custom` | Custom directive |
| `option` | Option directive |
| `plugin` | Plugin directive |
| `include` | Include directive |
| `pushtag` | Push tag |
| `poptag` | Pop tag |
| `pushmeta` | Push metadata |
| `popmeta` | Pop metadata |
| `TRUE` | Boolean true |
| `FALSE` | Boolean false |

## Operators and Punctuation

| Symbol | Usage |
|--------|-------|
| `*` | Complete flag, merge cost |
| `!` | Incomplete flag |
| `#` | Tag prefix |
| `^` | Link prefix |
| `:` | Account separator, metadata delimiter |
| `,` | Number grouping, list separator |
| `.` | Decimal point |
| `-` | Negative sign, date separator |
| `/` | Date separator, tag/link separator |
| `@` | Price annotation |
| `@@` | Total price annotation |
| `{` `}` | Cost specification |
| `{{` `}}` | Total cost specification |
| `~` | Tolerance operator |
| `(` `)` | Expression grouping |
| `+` | Addition |
| `*` | Multiplication |
| `/` | Division |
| `"` | String delimiter |
| `;` | Comment start |

## Implementation Notes

1. Tokenize greedily (longest match wins)
2. Distinguish date from number by context
3. Currency ends at whitespace or punctuation
4. Account contains no whitespace
5. Comments extend to end of line only
