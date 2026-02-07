# Conformance Test Requirements

This document defines the requirements that implementations must meet to claim conformance to PTA format specifications.

## Conformance Levels

### Level 1: Core Syntax

The implementation correctly parses and processes core syntax elements.

**Required Test Suites:**
- `syntax/valid/*` - All valid syntax tests must parse successfully
- `syntax/invalid/*` - All invalid syntax tests must produce parse errors

**Pass Criteria:**
- 100% of valid syntax tests must parse without error
- 100% of invalid syntax tests must produce errors
- No crashes on any test input

### Level 2: Semantic Validation

The implementation correctly validates semantic rules.

**Required Test Suites:**
- All Level 1 tests
- `validation/*` - Semantic validation tests

**Pass Criteria:**
- 95% of validation tests must match expected behavior
- Skipped tests (marked `skip: true`) do not count against pass rate
- Validation error types must match (not exact messages)

### Level 3: Full Compatibility

The implementation matches reference behavior on all tests.

**Required Test Suites:**
- All Level 2 tests
- All query/BQL tests (where applicable)
- All directive-specific tests

**Pass Criteria:**
- 99% of all tests must pass
- Balance calculations must match within tolerance (1e-8)
- Query results must match exactly

## Test Categories

### Syntax Tests

Verify parsing of the input format.

| Result | Meaning |
|--------|---------|
| `parse: success` | Input must parse without errors |
| `parse: error` | Input must produce a parse error |
| `directive_count: N` | Exactly N directives must be parsed |

### Validation Tests

Verify semantic validation after successful parsing.

| Result | Meaning |
|--------|---------|
| `validate: success` | No validation errors |
| `validate: error` | At least one validation error |
| `error_count: N` | Exactly N validation errors |
| `error_contains: [...]` | Error message contains substring |

### Balance Tests

Verify balance calculations.

| Result | Meaning |
|--------|---------|
| `balance: {...}` | Account balances must match |
| `tolerance: 1e-8` | Allowed difference in amounts |

### Query Tests

Verify query language execution (Beancount BQL).

| Result | Meaning |
|--------|---------|
| `query: success` | Query executes without error |
| `row_count: N` | Query returns exactly N rows |
| `columns: [...]` | Result has specified columns |

## Running Tests

### Test Execution

```bash
# Run all tests for an implementation
test-runner --manifest path/to/manifest.json --impl your-impl

# Run specific level
test-runner --manifest path/to/manifest.json --level 1

# Run specific suite
test-runner --manifest path/to/manifest.json --suite validation
```

### Output Format

Test runners must output TAP (Test Anything Protocol) format:

```tap
TAP version 14
1..100
ok 1 - syntax-valid-001
ok 2 - syntax-valid-002
not ok 3 - validation-001
  ---
  message: Expected validation error, got success
  expected: error
  actual: success
  ...
ok 4 - validation-002 # SKIP Undefined behavior
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | One or more tests failed |
| 2 | Test runner error (not a test failure) |

## Required Metadata

When submitting conformance results, include:

```json
{
  "implementation": {
    "name": "your-implementation",
    "version": "1.0.0",
    "language": "rust",
    "repository": "https://github.com/user/repo"
  },
  "format": {
    "name": "beancount",
    "version": "v3"
  },
  "results": {
    "level": 2,
    "total": 243,
    "passed": 240,
    "failed": 1,
    "skipped": 2,
    "pass_rate": "98.8%"
  },
  "test_run": {
    "date": "2024-01-15",
    "runner_version": "1.0.0",
    "commit": "abc123"
  }
}
```

## Test Environment

### Isolation

Each test must be independent. Implementations must:
- Not rely on state from previous tests
- Not modify global state
- Process each test input in isolation

### Timeouts

Tests must complete within reasonable time:
- Syntax tests: 5 seconds
- Validation tests: 10 seconds
- Query tests: 30 seconds

### Resource Limits

Tests should not require excessive resources:
- Memory: < 1 GB
- Disk: No persistent storage required

## Handling Undefined Behavior

Some behaviors are explicitly undefined in specs:

1. **Marked as `skip: true`** - Test is informational only
2. **Tagged with `undefined`** - Implementation-specific behavior
3. **Documented in spec** - Check the relevant specification

Implementations may:
- Choose any reasonable behavior for undefined cases
- Document their chosen behavior
- Skip tests marked as undefined

## Reporting Issues

If you believe a test is incorrect:

1. Open an issue with the `test-issue` label
2. Include the test ID and your analysis
3. Provide evidence from the format specification

Tests may be corrected or marked as skipped pending resolution.

## See Also

- [Self-Certification Process](self-certification.md)
- [Badge Usage Guidelines](badge-usage.md)
- [Test Harness Interface](../../tests/harness/interface.md)
