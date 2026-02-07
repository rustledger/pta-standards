# Error Message Guide

This guide covers creating clear, actionable error messages.

## Error Message Principles

### 1. Be Specific

**Bad:**
```
Error: Syntax error
```

**Good:**
```
Error: Expected amount after account name
```

**Best:**
```
Error: Expected amount like "100 USD" after "Assets:Cash"
```

### 2. Show Location

**Bad:**
```
Error: Invalid date
```

**Good:**
```
Error: Invalid date at line 42
```

**Best:**
```
error: Invalid date format
  --> finances.beancount:42:1
   |
42 | 2024-13-01 * "Transaction"
   | ^^^^^^^^^^ month must be 1-12, got 13
```

### 3. Suggest Fixes

**Bad:**
```
Error: Transaction does not balance
```

**Good:**
```
Error: Transaction does not balance (off by 1.00 USD)
```

**Best:**
```
error: Transaction does not balance
  --> finances.beancount:42:1
   |
42 | 2024-01-15 * "Groceries"
43 |   Expenses:Food  50.00 USD
44 |   Assets:Cash   -49.00 USD
   |
   = note: residual is -1.00 USD
   = help: either add the missing amount to a posting,
           or adjust an existing amount by 1.00 USD
```

## Error Structure

### Components

```
Error = {
    // Required
    level: Level,           // error, warning, info
    code: ErrorCode,        // E0042
    message: String,        // "Transaction does not balance"

    // Location (at least one)
    primary_span: Span,     // Main error location

    // Optional enhancements
    secondary_spans: Vec<LabeledSpan>,  // Related locations
    notes: Vec<String>,                  // Additional context
    suggestions: Vec<Suggestion>,        // Fix suggestions
}

LabeledSpan = {
    span: Span,
    label: String,
    style: SpanStyle,  // Primary, Secondary, Note
}

Suggestion = {
    message: String,      // "remove the dollar sign"
    replacement: String,  // "USD"
    span: Span,          // Where to apply
    applicability: Applicability,  // MachineApplicable, MaybeIncorrect
}
```

### Error Codes

Use structured codes for tooling:

```
Code Format: E[Category][Number]

Categories:
  E00xx - Lexical errors
  E01xx - Syntax errors
  E02xx - Semantic errors
  E03xx - Type errors
  E04xx - Balance errors
  E05xx - Account errors
  E06xx - Booking errors

Examples:
  E0001 - Unexpected character
  E0101 - Expected transaction flag
  E0401 - Transaction does not balance
  E0501 - Account not opened
```

## Error Rendering

### Terminal Output

For CLI tools, use colored output:

```
error[E0401]: transaction does not balance
  --> finances.beancount:142:1
   |
142 | 2024-01-15 * "Shopping"
    | ^^^^^^^^^^^^^^^^^^^^^^^^ transaction starts here
143 |   Expenses:Clothing  75.99 USD
144 |   Expenses:Tax        6.08 USD
145 |   Assets:Credit-Card
    |   ^^^^^^^^^^^^^^^^^^^^ missing amount needed
   |
   = note: sum of explicit amounts is 82.07 USD
   = help: add "-82.07 USD" to the credit card posting
```

Color scheme:
- **Red**: Error indicators (error, ^^^^^)
- **Blue**: Line numbers, file paths
- **Yellow**: Warnings
- **Green**: Suggestions, help text
- **Cyan**: Notes

### LSP Diagnostics

Convert to LSP format:

```
Diagnostic = {
    range: Range {
        start: { line: 141, character: 0 },
        end: { line: 141, character: 24 },
    },
    severity: DiagnosticSeverity.Error,
    code: "E0401",
    source: "pta-validator",
    message: "Transaction does not balance",
    relatedInformation: [
        {
            location: { uri: "...", range: {...} },
            message: "Missing amount here",
        }
    ],
}
```

### JSON Output

For tooling integration:

```json
{
  "errors": [
    {
      "level": "error",
      "code": "E0401",
      "message": "Transaction does not balance",
      "file": "finances.beancount",
      "span": {
        "start": { "line": 142, "column": 1, "offset": 3456 },
        "end": { "line": 142, "column": 25, "offset": 3480 }
      },
      "notes": [
        "sum of explicit amounts is 82.07 USD"
      ],
      "suggestion": {
        "message": "add \"-82.07 USD\" to the credit card posting",
        "replacement": "  Assets:Credit-Card  -82.07 USD",
        "span": { "start": {...}, "end": {...} }
      }
    }
  ]
}
```

## Common Error Patterns

### Parse Errors

#### Unexpected Token

```
error[E0101]: unexpected token
  --> ledger.beancount:42:15
   |
42 |   Assets:Cash  $ 100
   |                ^ expected amount, found '$'
   |
   = note: currency symbols like '$' are not used in Beancount
   = help: use currency code instead: "100 USD"
```

#### Missing Required Element

```
error[E0102]: missing transaction flag
  --> ledger.beancount:42:1
   |
42 | 2024-01-15 "Description"
   |            ^ expected '*' or '!' before description
   |
   = help: add '*' for completed or '!' for pending:
           2024-01-15 * "Description"
```

### Validation Errors

#### Balance Error

```
error[E0401]: transaction does not balance
  --> ledger.beancount:42:1
   |
42 | 2024-01-15 * "Multi-currency confusion"
43 |   Assets:USD   100 USD
44 |   Assets:EUR   -100 EUR
   |
   = note: amounts in different currencies cannot balance automatically
   = help: add a price annotation to convert:
             Assets:EUR   -100 EUR @ 1.10 USD
```

#### Account Not Opened

```
error[E0501]: account "Assets:Savings" was not opened
  --> ledger.beancount:42:3
   |
42 |   Assets:Savings  1000 USD
   |   ^^^^^^^^^^^^^^ account used here
   |
   = help: add an open directive before first use:
           2024-01-01 open Assets:Savings USD
```

#### Balance Assertion Failed

```
error[E0402]: balance assertion failed
  --> ledger.beancount:100:1
   |
100| 2024-06-01 balance Assets:Checking  5000.00 USD
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: expected: 5000.00 USD
           actual:   4872.50 USD
           difference: -127.50 USD
   |
   = help: check transactions between 2024-05-15 and 2024-06-01
   |
note: last known balance was here
  --> ledger.beancount:85:1
   |
85 | 2024-05-15 balance Assets:Checking  5000.00 USD
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

### Booking Errors

#### Insufficient Lots

```
error[E0601]: insufficient lots for reduction
  --> ledger.beancount:200:3
   |
200|   Assets:Stocks  -50 AAPL {150.00 USD}
   |                  ^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: trying to reduce 50 AAPL at 150.00 USD
           but only 30 AAPL at 150.00 USD available
   |
note: lot was acquired here
  --> ledger.beancount:150:3
   |
150|   Assets:Stocks   30 AAPL {150.00 USD}
   |                   ^^^^^^^^^^^^^^^^^^^^^
```

#### Ambiguous Lot

```
error[E0602]: ambiguous lot specification
  --> ledger.beancount:200:3
   |
200|   Assets:Stocks  -50 AAPL {}
   |                        ^^ matches multiple lots
   |
   = note: found 3 matching lots:
           - 30 AAPL @ 150.00 USD (2024-01-15)
           - 40 AAPL @ 155.00 USD (2024-02-20)
           - 25 AAPL @ 160.00 USD (2024-03-10)
   |
   = help: specify which lot using cost, date, or label:
           -50 AAPL {150.00 USD, 2024-01-15}
```

## Suggestion Quality

### Machine-Applicable

Can be applied automatically:

```
Suggestion {
    message: "remove duplicate semicolon",
    replacement: "",
    span: Span { start: 45, end: 46 },
    applicability: MachineApplicable,
}
```

### Maybe Incorrect

Might need human review:

```
Suggestion {
    message: "did you mean 'Assets:Bank:Checking'?",
    replacement: "Assets:Bank:Checking",
    span: Span { ... },
    applicability: MaybeIncorrect,
}
```

### Has Placeholders

Requires user input:

```
Suggestion {
    message: "add missing amount",
    replacement: "  <ACCOUNT>  <AMOUNT> <CURRENCY>",
    span: Span { ... },
    applicability: HasPlaceholders,
}
```

## Localization

Support translated error messages:

```
ErrorCatalog = {
    E0401: {
        en: "Transaction does not balance",
        de: "Transaktion ist nicht ausgeglichen",
        ja: "取引が均衡していません",
    },
    ...
}

format_error(error, locale):
    template = catalog[error.code][locale]
    return interpolate(template, error.params)
```

## Testing Error Messages

### Snapshot Tests

Capture error output for review:

```
test_balance_error_message():
    source = """
2024-01-15 * "Test"
  Assets:Cash  100 USD
  Expenses:Food  99 USD
"""
    errors = validate(parse(source))

    assert_snapshot(format_errors(errors))
```

### Regression Tests

Ensure errors don't regress:

```
test_error_location_accuracy():
    source = "2024-13-01 * \"Test\"\n"
    errors = parse(source).errors

    assert errors[0].span.start.line == 1
    assert errors[0].span.start.column == 6  // Points to "13"
```

### Fuzz Testing

Verify no crashes on random input:

```
fuzz_error_formatting():
    for input in random_inputs():
        result = parse(input)
        for error in result.errors:
            // Should never crash
            formatted = format_error(error)
            assert formatted is String
```
