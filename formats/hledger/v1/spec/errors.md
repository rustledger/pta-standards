# Error Codes Specification

This document defines error codes and messages for hledger parsers and validators.

## Error Categories

### Parse Errors (P-xxx)

Errors during lexical analysis or parsing.

### Validation Errors (V-xxx)

Errors during semantic validation.

### Warning Codes (W-xxx)

Non-fatal issues that may indicate problems.

## Parse Errors

### P-001: Invalid Date

```
P-001: Invalid date format
  Line 5: 2024-13-45 Transaction
  Expected: YYYY-MM-DD, YYYY/MM/DD, or YYYY.MM.DD
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
  Line 15: 2024-01-15 @ Invalid
  Unexpected '@' in transaction header
```

### P-005: Unclosed Quote

```
P-005: Unclosed quoted string
  Line 20:     Assets:Bank    10 "gold
  Expected: Closing quote for commodity name
```

### P-006: Invalid Account Name

```
P-006: Invalid account name
  Line 25:     :Empty:Segment    $50
  Account segments cannot be empty
```

### P-007: Indentation Error

```
P-007: Invalid indentation
  Line 30: Expenses:Food    $50
  Postings must be indented
```

### P-008: Invalid Status

```
P-008: Invalid status marker
  Line 35: 2024-01-15 ? Transaction
  Status must be '*' (cleared) or '!' (pending)
```

### P-009: Duplicate Date

```
P-009: Multiple dates in transaction
  Line 40: 2024-01-15=2024-01-20=2024-01-25 Bad
  Only one secondary date allowed
```

### P-010: Invalid Tag

```
P-010: Invalid tag format
  Line 45:     ; :badtag
  Tags must have format name:value or name:
```

## Validation Errors

### V-001: Unbalanced Transaction

```
V-001: Transaction does not balance
  Line 50-52: 2024-01-15 Unbalanced
    Difference: $10.00
    All commodity totals must equal zero
```

### V-002: Account Not Declared

```
V-002: Account not declared
  Line 55:     Expenses:Foood    $50
  Account 'Expenses:Foood' not found
  Did you mean: Expenses:Food ?
```

### V-003: Balance Assertion Failed

```
V-003: Balance assertion failed
  Line 60:     Assets:Checking    $100 = $1500
  Expected: $1500.00
  Actual:   $1400.00
```

### V-004: Multiple Amount Elisions

```
V-004: Multiple elided amounts for same commodity
  Line 65-67: 2024-01-15 Bad
    Only one posting per commodity can omit amount
```

### V-005: Commodity Not Declared

```
V-005: Commodity not declared
  Line 70:     Assets:Bank    100 XYZ
  Commodity 'XYZ' not found
```

### V-006: Price Mismatch

```
V-006: Price annotation mismatch
  Line 75:     Assets:Stock    10 AAPL @ $150 @@ $1600
  Cannot use both @ and @@ on same amount
```

### V-007: Virtual Posting Imbalance

```
V-007: Balanced virtual postings don't balance
  Line 80-82:
    [Budget:A]    $50
    [Budget:B]    $30
  Difference: $20.00
```

### V-008: Duplicate Account

```
V-008: Duplicate account declaration
  Line 85: account Assets:Checking
  Previously declared at line 10
```

### V-009: Include Not Found

```
V-009: Included file not found
  Line 90: include missing.journal
  File 'missing.journal' does not exist
```

### V-010: Include Cycle

```
V-010: Circular include detected
  Line 95: include main.journal
  Include cycle: main.journal -> other.journal -> main.journal
```

### V-011: Future Date

```
V-011: Transaction date in future
  Line 100: 2030-01-15 Future transaction
  Date is after current date
  (Disable with --future)
```

### V-012: Negative Balance

```
V-012: Account balance went negative
  Line 105:     Assets:Checking    $-100 = $-50
  Assets:Checking has negative balance
  (Disable with --permissive)
```

### V-013: Invalid Account Type

```
V-013: Invalid account type inference
  Line 110: account Stuff:Things
  Cannot infer type for account 'Stuff:Things'
  Use account type declaration or standard prefix
```

### V-014: Orphaned Posting

```
V-014: Posting outside transaction
  Line 115:     Expenses:Food    $50
  Posting found without transaction header
```

### V-015: Empty Transaction

```
V-015: Transaction has no postings
  Line 120: 2024-01-15 Empty transaction
  Transactions must have at least one posting
```

## Warning Codes

### W-001: Unusual Account

```
W-001: Unusual account name
  Line 125:     assets:checking    $50
  Account name should start with capital letter
```

### W-002: Large Amount

```
W-002: Unusually large amount
  Line 130:     Expenses:Food    $999999.00
  Amount exceeds typical threshold
```

### W-003: Old Date

```
W-003: Very old transaction date
  Line 135: 1900-01-01 Ancient
  Transaction date is unusually old
```

### W-004: Unused Account

```
W-004: Declared account never used
  Line 140: account Assets:Unused
  Account declared but has no transactions
```

### W-005: Implicit Commodity

```
W-005: Implicit commodity format
  Line 145:     Assets:Bank    $1234
  Commodity format inferred from first use
  Consider explicit 'commodity' directive
```

### W-006: Precision Loss

```
W-006: Precision loss in calculation
  Line 150:     Expenses:A    $33.333333333333
  Amount truncated to commodity precision
```

### W-007: Balance Check

```
W-007: Balance check failed (non-fatal)
  Line 155: 2024/01/15 balance Assets:Checking = $1500
  Account balance differs from expected
  (Error promoted to V-003 in strict mode)
```

## Error Output Formats

### Default (Human-Readable)

```
hledger: Error at example.journal:50
  V-001: Transaction does not balance

  50 | 2024-01-15 Unbalanced
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
      "file": "example.journal",
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

### TAP Format

```
not ok 1 - example.journal:50 V-001 Transaction does not balance
  ---
  file: example.journal
  line: 50
  code: V-001
  ...
```

## Error Handling Modes

### Strict Mode (Default)

All errors abort processing.

### Permissive Mode

Some errors become warnings:
- V-011 (future dates)
- V-012 (negative balances)
- W-007 (balance checks)

### Pedantic Mode

All warnings become errors.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Parse error |
| 2 | Validation error |
| 3 | File not found |
| 4 | Permission denied |
| 5 | Include cycle |

## See Also

- [Syntax Specification](syntax.md)
- [hledger Manual: Error Messages](https://hledger.org/errors.html)
