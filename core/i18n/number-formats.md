# Number Formats

This document specifies number formatting for internationalization in plain text accounting.

## Input vs. Output

### Input (Canonical)

Source files MUST use period as decimal separator:

```
1234.56       ; Canonical format
```

This format is:
- Unambiguous (no locale dependency)
- Consistent (same parsing rules everywhere)
- Programming-friendly (standard decimal notation)

### Output (Localized)

Reports and displays MAY use locale-specific formats:

```
1,234.56      ; en-US
1.234,56      ; de-DE
1 234,56      ; fr-FR
1'234.56      ; de-CH
```

## Decimal Separator

### Canonical (Period)

The period (`.`) is the ONLY valid decimal separator in source files:

```
100.00        ; Valid
100,00        ; Invalid in source
```

### Locale Variants

| Locale | Separator | Example |
|--------|-----------|---------|
| en-US | . (period) | 1234.56 |
| en-GB | . (period) | 1234.56 |
| de-DE | , (comma) | 1234,56 |
| fr-FR | , (comma) | 1234,56 |
| es-ES | , (comma) | 1234,56 |
| de-CH | . (period) | 1234.56 |

## Grouping Separator

### Input Handling

Grouping separators in input MAY be accepted and are stripped:

```
1,234,567.89  ; Accepted, parsed as 1234567.89
1.234.567,89  ; NOT accepted (comma decimal + dot group)
```

### Locale Variants

| Locale | Separator | Example |
|--------|-----------|---------|
| en-US | , (comma) | 1,234,567 |
| de-DE | . (period) | 1.234.567 |
| fr-FR | (space) | 1 234 567 |
| de-CH | ' (apostrophe) | 1'234'567 |
| ja-JP | , (comma) | 1,234,567 |
| hi-IN | , (lakh system) | 12,34,567 |

### Grouping Size

| System | Pattern | Example |
|--------|---------|---------|
| Western | 3,3,3... | 1,234,567,890 |
| Indian (lakh) | 3,2,2... | 1,23,45,67,890 |
| Chinese (wan) | 4,4,4... | 12,3456,7890 |

## Negative Numbers

### Input Formats

```
-100.00       ; Prefix minus (canonical)
(100.00)      ; Parentheses (accepted)
100.00-       ; Suffix minus (rare)
```

### Output Formats

| Locale/Style | Example |
|--------------|---------|
| Standard | -1,234.56 |
| Accounting | (1,234.56) |
| Suffix | 1,234.56- |

### Accounting Format

Negative numbers in parentheses for financial reports:

```
Revenue         1,234.56
Expenses       (1,234.56)
─────────────────────────
Net                 0.00
```

## Zero Handling

### Positive/Negative Zero

```
0             ; Zero
-0            ; Negative zero (equals 0)
0.00          ; Zero with precision
```

### Zero Display Options

| Style | Display |
|-------|---------|
| Standard | 0.00 |
| Dash | - |
| Blank | (empty) |

## Precision Display

### Trailing Zeros

| Input | Display (2 places) |
|-------|-------------------|
| 100 | 100.00 |
| 100.5 | 100.50 |
| 100.123 | 100.12 (rounded) |

### Maximum Precision

```
0.123456789   ; Preserve all digits
1000000000    ; Large numbers preserved
```

## Currency-Specific Formatting

### Minor Units

| Currency | Decimals | Example |
|----------|----------|---------|
| USD | 2 | 100.00 |
| EUR | 2 | 100.00 |
| JPY | 0 | 100 |
| KWD | 3 | 100.000 |
| BTC | 8 | 0.00000001 |

### Display Rules

```
100 USD       ; $100.00 (2 decimals)
100 JPY       ; ¥100 (0 decimals)
100 KWD       ; KD100.000 (3 decimals)
```

## Percentage Display

### As Decimal

```
0.15          ; 15% stored as decimal
```

### As Percentage

```
15%           ; Display format
15.5%         ; With decimals
```

## Scientific Notation

### Not Used in PTA

Scientific notation is NOT used in plain text accounting:

```
1000000       ; Valid (one million)
1e6           ; Invalid in most PTA formats
```

### Implementation Note

Parsers SHOULD reject scientific notation to prevent precision loss.

## Configuration

### Option Syntax

```
option "number_format" "1,234.56"    ; Pattern
option "locale" "de-DE"               ; Locale-based
```

### Format Patterns

| Pattern | Meaning |
|---------|---------|
| `#,##0.00` | Comma grouping, period decimal, 2 places |
| `#.##0,00` | Period grouping, comma decimal, 2 places |
| `# ##0,00` | Space grouping, comma decimal, 2 places |

## Implementation

### Formatting

```python
import babel.numbers

def format_number(value: Decimal, locale: str = 'en_US') -> str:
    return babel.numbers.format_decimal(value, locale=locale)

# Examples:
# format_number(Decimal('1234.56'), 'en_US') → "1,234.56"
# format_number(Decimal('1234.56'), 'de_DE') → "1.234,56"
```

### Parsing (Canonical)

```python
import re
from decimal import Decimal

def parse_number(s: str) -> Decimal:
    """Parse canonical number format only."""
    # Strip grouping separators
    s = s.replace(',', '')

    # Validate format
    if not re.match(r'^-?\d+(\.\d+)?$', s):
        raise ParseError(f"Invalid number: {s}")

    return Decimal(s)
```

### Locale-Aware Parsing

For user input (not source files):

```python
import babel.numbers

def parse_locale_number(s: str, locale: str) -> Decimal:
    return babel.numbers.parse_decimal(s, locale=locale)
```

## Alignment

### Right Alignment

Numbers are typically right-aligned in reports:

```
Account              Debit    Credit
───────────────────────────────────────
Assets:Checking   1,000.00
Income:Salary                1,000.00
```

### Decimal Alignment

Align decimal points for readability:

```
    1.00
   10.00
  100.00
1,000.00
```

## Error Messages

### Invalid Format

```
ERROR: Invalid number format
  --> ledger.beancount:42:18
   |
42 |   Assets:Cash  1.234,56 EUR
   |                ^^^^^^^^
   |
   = use period (.) as decimal separator
```

### Overflow

```
ERROR: Number overflow
  --> ledger.beancount:42:15
   |
42 |   Assets:Cash  99999999999999999999999999999 USD
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
   = number exceeds maximum precision
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Decimal separator | Period only | Period only | Period only |
| Grouping input | Comma | Comma | Comma |
| Locale output | Limited | Yes | Yes |
| Negative format | Prefix `-` | Prefix `-` | Prefix `-` |
| Accounting format | No | Yes | Yes |
