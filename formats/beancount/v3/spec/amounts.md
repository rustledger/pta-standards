# Amounts

## Overview

An amount is a decimal number paired with a currency. Amounts represent quantities of commodities in postings, balance assertions, and price directives.

## Syntax

```ebnf
amount = number WHITESPACE currency

number = sign? integer ("." fraction)?

sign     = "-" | "+"
integer  = digit+ ("," digit+)*
fraction = digit+
digit    = [0-9]

currency = uppercase+ (currency_char)* uppercase?
```

## Components

### Number

The numeric value, which may be:
- Positive: `100`, `100.00`, `+100`
- Negative: `-50`, `-50.00`
- With grouping: `1,234.56`, `1,234,567.89`

Note: Leading decimals without integer part (`.50`) are NOT valid. Use `0.50` instead.

### Currency

The commodity identifier:
- MUST start with uppercase letter (A-Z)
- MUST end with uppercase letter or digit (A-Z, 0-9)
- Middle characters MAY include: A-Z, 0-9, apostrophe, period, underscore, dash

> **UNDEFINED**: Maximum length is not enforced. See [commodities.md](validation/commodities.md).

## Number Format

### Decimal Point

The decimal separator is always a period (`.`):

```
100.00    ; Valid
100,00    ; Invalid (comma is grouping separator)
```

### Grouping Separator

Commas group digits for readability and are ignored:

```
1,234.56       ; = 1234.56
1,234,567.89   ; = 1234567.89
1234.56        ; Also valid (no grouping)
```

Grouping is purely cosmetic; `1,234.56` and `1234.56` are identical.

### Sign

Both positive (`+`) and negative (`-`) signs are supported:

```
100      ; Positive (implicit)
+50      ; Positive (explicit)
-50      ; Negative
```

### Leading/Trailing Zeros

Leading and trailing zeros are allowed:

```
0100.00    ; = 100.00
100.500    ; = 100.5
0.50       ; Valid (integer part required)
```

### Precision

Implementations MUST support at least 28 significant digits:

```
0.0000000000000000000000000001   ; Valid (28 decimal places)
123456789012345678901234567890   ; May exceed precision
```

## Arithmetic Expressions

Amounts may include arithmetic expressions:

```ebnf
amount_expr = term (('+' | '-') term)*
term        = factor (('*' | '/') factor)*
factor      = number | '(' amount_expr ')' | '-' factor
```

### Operators

| Operator | Precedence | Associativity |
|----------|------------|---------------|
| `+` `-` | Low | Left |
| `*` `/` | High | Left |
| `()` | Highest | - |
| unary `-` | Highest | Right |

### Examples

```beancount
2024-01-15 * "Split expense"
  Expenses:Food  (100 / 3) USD           ; = 33.333... USD
  Expenses:Food  (100 / 3) USD
  Expenses:Food  (100 / 3) USD
  Assets:Cash   -100 USD

2024-01-15 * "Tax calculation"
  Expenses:Purchase  (99.99 * 1.08) USD  ; = 107.9892 USD
  Assets:Checking

2024-01-15 * "Complex split"
  Expenses:Dinner  ((75 + 25) / 4) USD   ; = 25 USD
  Assets:Cash
```

### Division Behavior

Division produces exact decimal results when possible:

```
100 / 4 = 25.00
100 / 3 = 33.333333...  ; Repeating decimal
```

Implementations SHOULD maintain sufficient precision for financial calculations.

## Currency Format

### Valid Currencies

```
USD       ; US Dollar
EUR       ; Euro
GBP       ; British Pound
AAPL      ; Stock symbol
VTSAX     ; Mutual fund
BTC       ; Cryptocurrency
AU        ; Gold
KRW       ; Korean Won
```

### Currency Rules

1. MUST start with uppercase letter (A-Z)
2. MUST end with uppercase letter or digit (A-Z, 0-9)
3. MAY contain in middle: A-Z, 0-9, ', ., _, -
4. Single-character currencies are valid (e.g., `V`)
5. Maximum length is UNDEFINED (not enforced)

### Invalid Currencies

```
usd       ; Lowercase not allowed
$USD      ; Special characters at start
123       ; Must start with letter
USD-      ; Cannot end with special character
```

## Amount Examples

### Simple Amounts

```beancount
100 USD
-50.25 EUR
1,234.56 CAD
0.00000001 BTC
```

### In Postings

```beancount
2024-01-15 * "Various amounts"
  Assets:Checking      1,000.00 USD
  Assets:Savings       2,500.00 USD
  Assets:Brokerage        10 AAPL
  Assets:Crypto            0.5 BTC
  Income:Various
```

### In Balance Assertions

```beancount
2024-01-15 balance Assets:Checking  5,432.10 USD
2024-01-15 balance Assets:Stock       100 AAPL
```

### In Price Directives

```beancount
2024-01-15 price AAPL  185.50 USD
2024-01-15 price EUR     1.0875 USD
2024-01-15 price BTC 42,500.00 USD
```

## Rounding

### Display Rounding

For display, amounts are typically rounded to the commodity's precision:

| Currency | Typical Precision | Example |
|----------|-------------------|---------|
| USD | 2 | 100.00 USD |
| EUR | 2 | 50.25 EUR |
| BTC | 8 | 0.00123456 BTC |
| AAPL | 0 | 10 AAPL |

### Calculation Precision

Internally, full precision is maintained:

```beancount
; 100 / 3 = 33.333333... (full precision)
; Displayed as 33.33 USD but stored precisely
2024-01-15 * "Split"
  Expenses:Food  (100 / 3) USD
  Expenses:Food  (100 / 3) USD
  Expenses:Food  (100 / 3) USD
  Assets:Cash   -100 USD
```

### Balance Tolerance

Balance checks use tolerance to handle precision:

```beancount
; These may not sum exactly to 100 when displayed
; but balance within tolerance
2024-01-15 * "Three-way split"
  Expenses:A  33.33 USD
  Expenses:B  33.33 USD
  Expenses:C  33.34 USD    ; Adjusted for rounding
  Assets:Cash -100.00 USD
```

See [tolerances.md](tolerances.md) for tolerance calculation rules.

## Negative Amounts

Negative amounts typically represent:
- Outflows from asset accounts
- Credits to liability accounts
- Reductions in positions

```beancount
2024-01-15 * "Withdrawal"
  Assets:Cash         200 USD      ; Positive: receiving cash
  Assets:Checking    -200 USD      ; Negative: giving from checking
```

The sign is part of the double-entry system; debits and credits are represented by positive and negative amounts.

## Zero Amounts

Zero amounts are valid:

```beancount
2024-01-15 * "No-op transaction"
  Assets:Checking    0 USD
  Expenses:Fees      0 USD

2024-01-15 balance Assets:Closed  0 USD
```

Zero is often used in:
- Placeholder postings
- Balance assertions for closed accounts
- Debugging

## Implementation Notes

1. Parse numbers with arbitrary precision
2. Preserve original formatting for display
3. Use decimal arithmetic (not floating point)
4. Apply tolerance rules for balance checking
5. Support at least 28 significant digits
6. Handle grouping separators (ignore commas)
