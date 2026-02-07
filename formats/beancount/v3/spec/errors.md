# Error Conditions

This document specifies the conditions that MUST produce errors during beancount processing.

## Error Structure

All errors MUST include:

| Field | Description |
|-------|-------------|
| Location | File path and line number where the error occurred |
| Message | Human-readable description of the error |
| Context | The directive that caused the error (when applicable) |

## Error Categories

### Lexical Errors

Errors during tokenization:

| Condition | Description |
|-----------|-------------|
| Invalid token | Unrecognized character sequence |
| Unterminated string | String literal without closing quote |
| Invalid date format | Date not matching `YYYY-MM-DD` or `YYYY/MM/DD` |

### Syntax Errors

Errors during parsing:

| Condition | Description |
|-----------|-------------|
| Malformed directive | Directive structure doesn't match grammar |
| Unknown directive | Unrecognized directive keyword |
| Missing required field | Required component missing from directive |
| Invalid option | Unknown option name |
| Invalid option value | Option value doesn't match expected format |

### Semantic Errors

Errors during validation:

| Condition | Description |
|-----------|-------------|
| Account not opened | Posting references account without prior `open` |
| Duplicate open | Same account opened twice without intervening `close` |
| Posting after close | Posting references account after its `close` date |
| Currency constraint | Posting uses currency not allowed by account's `open` |
| Transaction imbalance | Sum of posting weights doesn't equal zero (within tolerance) |
| Duplicate metadata | Same metadata key appears twice on one directive |

### Balance Errors

Errors during balance assertion processing:

| Condition | Description |
|-----------|-------------|
| Assertion failed | Actual balance doesn't match expected (outside tolerance) |

### Booking Errors

Errors during lot matching and booking:

| Condition | Description |
|-----------|-------------|
| No matching lot | Reduction cost specification doesn't match any existing lot |
| Insufficient units | Not enough units in matched lots to fulfill reduction |
| Ambiguous match | Multiple lots match in STRICT mode without disambiguation |
| Elision ambiguity | Multiple postings with missing amounts (see elision rules) |

### Pad Errors

Errors during pad directive processing:

| Condition | Description |
|-----------|-------------|
| Unused pad | Pad directive without subsequent balance directive |
| Zero adjustment | Pad produces no change (balance already matches) |

### Document Errors

Errors during document directive processing:

| Condition | Description |
|-----------|-------------|
| File not found | Document path references non-existent file |

## Error Severity

All conditions listed above are errors that MUST be reported. Implementations MAY also provide:

- **Warnings** - Non-fatal issues that don't prevent processing
- **Info** - Informational messages about processing

## Error Recovery

Implementations SHOULD continue processing after encountering errors when possible, to report multiple errors in a single pass. However, some errors (like severe syntax errors) may prevent further processing.

## Error Reporting

### Required Information

Error output MUST include:
- File path where error occurred
- Line number where error occurred
- Clear description of the problem

### Recommended Information

Error output SHOULD include:
- Column number (for syntax errors)
- The offending text/token
- Suggestion for how to fix the issue

### Machine-Readable Output

Implementations SHOULD support machine-readable error output (e.g., JSON) for tooling integration.

## Processing Order

Errors are detected in the following order:

1. **Lexical** - During tokenization
2. **Syntax** - During parsing
3. **Semantic** - During validation (account references, currencies)
4. **Booking** - During lot matching and interpolation
5. **Balance** - During balance assertion checking
6. **Document** - During document file verification
