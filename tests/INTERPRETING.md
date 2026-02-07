# Interpreting Test Results

This document explains how to interpret PTA test suite results.

## Test Output Formats

### TAP Format

```
TAP version 14
1..164
ok 1 - syntax-valid-001: Basic transaction
ok 2 - syntax-valid-002: Multi-posting transaction
not ok 3 - syntax-invalid-001: Missing date
  ---
  message: Expected parse error, got success
  expected: parse error
  actual: parsed successfully
  ...
ok 4 - validation-001: Balanced transaction # SKIP Undefined behavior
```

### JSON Format

```json
{
  "summary": {
    "total": 164,
    "passed": 160,
    "failed": 3,
    "skipped": 1
  },
  "results": [
    {
      "id": "syntax-valid-001",
      "description": "Basic transaction",
      "status": "pass",
      "duration_ms": 12.5
    }
  ]
}
```

## Result Status

### Pass

Test executed and assertions matched.

```
ok 1 - syntax-valid-001: Basic transaction
```

### Fail

Test executed but assertions didn't match.

```
not ok 3 - syntax-invalid-001: Missing date
  ---
  message: Expected parse error, got success
  ...
```

### Skip

Test intentionally skipped.

```
ok 4 - validation-001 # SKIP Undefined behavior
```

### Error

Test couldn't be executed.

```
not ok 5 - syntax-001 # ERROR: Test file not found
```

## Understanding Failures

### Parse Expectation Mismatch

```
expected: parse error
actual: parsed successfully
```

The input should have failed to parse but didn't.

### Validation Expectation Mismatch

```
expected: validation error
actual: validated successfully
```

The input should have failed validation but passed.

### Error Message Mismatch

```
expected error containing: "account not opened"
actual error: "invalid date format"
```

An error occurred but not the expected one.

### Balance Mismatch

```
expected balance: 1000.00 USD
actual balance: 999.99 USD
```

Calculated balance differs from expected.

## Common Failure Patterns

### Implementation Difference

Different implementations may have valid variations:

```
Test: date-format-001
Expected: Parse success
Beancount: Pass
Ledger: Pass (with different date handling)
```

### Undefined Behavior

Some scenarios have no specified behavior:

```
# SKIP Undefined behavior: empty transaction
```

### Strict vs Permissive

Some tests only apply in strict mode:

```
# SKIP Requires strict mode
```

## Debugging Failures

### Step 1: Read the Test

```json
{
  "id": "validation-balance-001",
  "description": "Balance assertion failure",
  "input": "...",
  "expected": {
    "validate": false,
    "error_contains": "balance assertion"
  }
}
```

### Step 2: Run Manually

```bash
echo "$INPUT" | bean-check
```

### Step 3: Compare Output

```bash
# Expected: balance assertion error
# Actual: (examine output)
```

### Step 4: Check Implementation

Review implementation for:
- Parsing differences
- Validation logic
- Edge case handling

## Reporting Issues

### Bug Report Template

```markdown
## Test Failure Report

**Test ID:** validation-balance-001
**Implementation:** my-parser v1.0.0
**Platform:** Linux x86_64

### Expected
Parse error with message containing "balance"

### Actual
Parsed successfully

### Input
\`\`\`beancount
[test input]
\`\`\`

### Notes
Additional context...
```

## Compliance Levels

### Level 1: Core Syntax (80%+)

Basic parsing works.

### Level 2: Validation (90%+)

Validation rules implemented.

### Level 3: Full Compliance (95%+)

Near-complete specification coverage.

### Level 4: Reference (100%)

Matches reference implementation.

## See Also

- [Test Harness](harness/)
- [Test Suites](beancount/)
- [Contributing](../CONTRIBUTING.md)
