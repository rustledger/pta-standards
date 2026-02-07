# Error Codes Specification

This document defines error codes and messages for Ledger parsers and validators.

## Error Categories

### Parse Errors (P-xxx)

Errors during lexical analysis or parsing.

### Validation Errors (V-xxx)

Errors during semantic validation.

### Expression Errors (X-xxx)

Errors in value expression evaluation.

### Warning Codes (W-xxx)

Non-fatal issues that may indicate problems.

## Parse Errors

### P-001: Invalid Date

```
P-001: Invalid date format
  Line 5: 2024/13/45 Transaction
  Expected: YYYY/MM/DD, YYYY-MM-DD, or YYYY.MM.DD
```

### P-002: Invalid Amount

```
P-002: Invalid amount format
  Line 8:     Expenses:Food    $abc
  Expected: Numeric value with optional commodity
```

### P-003: Missing Account

```
P-003: Missing account name
  Line 12:     $50.00
  Postings require an account name
```

### P-004: Unexpected Token

```
P-004: Unexpected token
  Line 15: 2024/01/15 @ Invalid
  Unexpected '@' in transaction header
```

### P-005: Unclosed Parenthesis

```
P-005: Unclosed parenthesis
  Line 20:     (Budget:Food    $50
  Expected: Closing ')' for virtual account
```

### P-006: Unclosed Bracket

```
P-006: Unclosed bracket
  Line 25:     [Savings:Goal    $50
  Expected: Closing ']' for balanced virtual account
```

### P-007: Invalid Account Name

```
P-007: Invalid account name
  Line 30:     :Empty:Segment    $50
  Account segments cannot be empty
```

### P-008: Indentation Error

```
P-008: Invalid indentation
  Line 35: Expenses:Food    $50
  Postings must be indented
```

### P-009: Invalid Commodity

```
P-009: Invalid commodity symbol
  Line 40:     Assets:Bank    100 123ABC
  Commodity cannot start with digit
```

### P-010: Unterminated String

```
P-010: Unterminated string
  Line 45:     ; Note: "This never ends
  Expected: Closing quote
```

### P-011: Invalid Escape Sequence

```
P-011: Invalid escape sequence
  Line 50:     ; Note: "Bad \x escape"
  Unknown escape sequence: \x
```

### P-012: Invalid Period Expression

```
P-012: Invalid period expression
  Line 55: ~ invalid period
  Could not parse period specification
```

### P-013: Invalid Automated Query

```
P-013: Invalid automated transaction query
  Line 60: = [unclosed
  Expected: Valid regex or expression
```

## Validation Errors

### V-001: Unbalanced Transaction

```
V-001: Transaction does not balance
  Line 50-52: 2024/01/15 Unbalanced
    Difference: $10.00
    All commodity totals must equal zero
```

### V-002: Multiple Amount Elisions

```
V-002: Multiple elided amounts for same commodity
  Line 65-67: 2024/01/15 Bad
    Only one posting per commodity can omit amount
```

### V-003: Balance Assertion Failed

```
V-003: Balance assertion failed
  Line 70:     Assets:Checking    $100 = $1500
  Expected: $1500.00
  Actual:   $1400.00
```

### V-004: Account Not Declared

```
V-004: Account not declared
  Line 75:     Expenses:Foood    $50
  Account 'Expenses:Foood' not found
  Did you mean: Expenses:Food ?
```

### V-005: Commodity Not Declared

```
V-005: Commodity not declared
  Line 80:     Assets:Bank    100 XYZ
  Commodity 'XYZ' not found
```

### V-006: Price Mismatch

```
V-006: Price annotation error
  Line 85:     Assets:Stock    10 AAPL @ $150 @@ $1600
  Cannot use both @ and @@ on same posting
```

### V-007: Duplicate Account

```
V-007: Duplicate account declaration
  Line 90: account Assets:Checking
  Previously declared at line 10
```

### V-008: Include Not Found

```
V-008: Included file not found
  Line 95: include missing.ledger
  File 'missing.ledger' does not exist
```

### V-009: Include Cycle

```
V-009: Circular include detected
  Line 100: include main.ledger
  Include cycle: main.ledger -> other.ledger -> main.ledger
```

### V-010: Assertion Failed

```
V-010: Assertion failed
  Line 105: assert total(Assets) > 0
  Assertion evaluated to false
  Actual: total(Assets) = $-500
```

### V-011: Check Failed

```
V-011: Check failed (warning)
  Line 110: check Assets:Checking >= $0
  Check evaluated to false
  Actual: Assets:Checking = $-100
```

### V-012: Virtual Imbalance

```
V-012: Balanced virtual postings don't balance
  Line 115-117:
    [Budget:A]    $50
    [Budget:B]    $30
  Difference: $20.00
```

### V-013: Invalid Alias Target

```
V-013: Alias target not found
  Line 120: alias foo = NonExistent:Account
  Account 'NonExistent:Account' not declared
```

### V-014: Orphaned Posting

```
V-014: Posting outside transaction
  Line 125:     Expenses:Food    $50
  Posting found without transaction header
```

### V-015: Empty Transaction

```
V-015: Transaction has no postings
  Line 130: 2024/01/15 Empty transaction
  Transactions must have at least one posting
```

## Expression Errors

### X-001: Division by Zero

```
X-001: Division by zero
  Line 135:     Expenses:A    ($100 / 0)
  Cannot divide by zero
```

### X-002: Type Mismatch

```
X-002: Type mismatch in expression
  Line 140: assert $100 + "text"
  Cannot add amount and string
```

### X-003: Undefined Variable

```
X-003: Undefined variable
  Line 145: = expr unknown_var > 0
  Variable 'unknown_var' is not defined
```

### X-004: Unknown Function

```
X-004: Unknown function
  Line 150: = expr bad_func(amount)
  Function 'bad_func' is not defined
```

### X-005: Invalid Regex

```
X-005: Invalid regular expression
  Line 155: = expr account =~ /[unclosed
  Regex syntax error: unclosed bracket
```

### X-006: Argument Count

```
X-006: Wrong number of arguments
  Line 160: = expr round($50, 2, 3)
  round() expects 1 argument, got 3
```

## Warning Codes

### W-001: Unusual Account Name

```
W-001: Unusual account name
  Line 165:     assets:checking    $50
  Account name should start with capital letter
```

### W-002: Large Amount

```
W-002: Unusually large amount
  Line 170:     Expenses:Food    $999999.00
  Amount exceeds typical threshold
```

### W-003: Future Date

```
W-003: Future transaction date
  Line 175: 2099/01/15 Future
  Transaction date is in the future
```

### W-004: Old Date

```
W-004: Very old transaction date
  Line 180: 1900/01/01 Ancient
  Transaction date is unusually old
```

### W-005: Unused Account

```
W-005: Declared account never used
  Line 185: account Assets:Unused
  Account declared but has no transactions
```

### W-006: Precision Loss

```
W-006: Precision loss in calculation
  Line 190:     Expenses:A    ($100 / 3)
  Result truncated: 33.333333...
```

### W-007: Deprecated Syntax

```
W-007: Deprecated syntax
  Line 195: D $1,000.00
  Consider using 'commodity' directive instead
```

## Error Output Formats

### Default (Human-Readable)

```
ledger: Error at journal.ledger:50
  V-001: Transaction does not balance

  50 | 2024/01/15 Unbalanced
  51 |     Expenses:Food    $50.00
  52 |     Assets:Checking  $-40.00
     |                          ^^^^

  Difference: $10.00
```

### JSON Format

```json
{
  "errors": [
    {
      "code": "V-001",
      "severity": "error",
      "file": "journal.ledger",
      "line": 50,
      "column": 1,
      "end_line": 52,
      "end_column": 30,
      "message": "Transaction does not balance",
      "details": {
        "difference": "$10.00"
      }
    }
  ]
}
```

## Error Handling Modes

### Strict Mode

All errors and warnings abort processing.

### Normal Mode (Default)

Errors abort; warnings are reported but continue.

### Permissive Mode

Some errors become warnings:
- W-003 (future dates)
- W-006 (precision loss)

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Parse error |
| 2 | Validation error |
| 3 | File not found |
| 4 | Include cycle |
| 5 | Expression error |

## See Also

- [Syntax Specification](syntax.md)
- [Validation Rules](validation/balance.md)
- [Value Expressions](expressions/spec.md)
