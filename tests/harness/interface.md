# Runner Interface Specification

This document specifies the interface that test runners must implement.

## Overview

A conformance test runner:
1. Reads test manifests and test cases
2. Executes tests against an implementation
3. Compares results against expected outcomes
4. Reports results in a standard format

## Command Line Interface

### Required Arguments

```
runner --manifest PATH
```

The `--manifest` argument specifies the manifest.json file to use.

### Optional Arguments

| Argument | Description |
|----------|-------------|
| `--suite NAME` | Run only the named test suite |
| `--test ID` | Run only the test with given ID |
| `--tags TAG,...` | Run only tests matching tags |
| `--format FORMAT` | Output format: `tap` or `json` |
| `--verbose` | Show detailed output |
| `--fail-fast` | Stop on first failure |
| `--timeout MS` | Per-test timeout in milliseconds |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | One or more tests failed |
| 2 | Runner error (config, I/O, etc.) |

## Execution Flow

```
1. Load manifest.json
2. For each test_directory in manifest:
   a. Load tests.json
   b. For each test:
      - If skip=true, record as skipped
      - Execute test
      - Compare actual vs expected
      - Record result
3. Output results
4. Exit with appropriate code
```

## Test Execution

### Parse Test

1. Feed input to parser
2. Check for parse errors
3. If `expected.parse == "success"`:
   - Assert no parse errors
   - Optionally check `expected.directives`
4. If `expected.parse == "error"`:
   - Assert at least one parse error
   - Check `expected.error_contains` if present

### Validation Test

1. Parse input
2. If parse succeeds and `expected.validate` is set:
   - Run validation
   - Compare against expected validation result
3. Check `expected.balance` if present

### Query Test

1. Parse and validate input
2. Execute query (from test input or separate field)
3. Compare results against expected

## Result Structure

Each test produces a result:

```
TestResult {
  test_id: string,
  status: "pass" | "fail" | "skip" | "error",
  duration_ms: number,
  expected: {...},
  actual: {...},
  message: string | null
}
```

## Output Formats

### TAP (Test Anything Protocol)

```
TAP version 14
1..{total_tests}
ok 1 - {test_id}: {description}
not ok 2 - {test_id}: {description}
  ---
  message: {failure_message}
  expected: {expected_value}
  actual: {actual_value}
  ...
ok 3 - {test_id}: {description} # SKIP {skip_reason}
```

TAP version 14 features:
- YAML diagnostic blocks for failures
- `# SKIP` directive for skipped tests
- `# TODO` for expected failures

### JSON

```json
{
  "version": "1.0.0",
  "timestamp": "2024-02-07T10:30:00Z",
  "manifest": "../beancount/v3/manifest.json",
  "summary": {
    "total": 164,
    "passed": 160,
    "failed": 3,
    "skipped": 1,
    "duration_ms": 1234
  },
  "results": [
    {
      "test_id": "empty-file",
      "suite": "syntax/valid",
      "status": "pass",
      "duration_ms": 5
    },
    {
      "test_id": "invalid-date",
      "suite": "syntax/invalid",
      "status": "fail",
      "duration_ms": 3,
      "expected": {"parse": "error"},
      "actual": {"parse": "success"},
      "message": "Expected parse error but parsing succeeded"
    }
  ]
}
```

## Implementation Requirements

### Parsing

The runner must be able to:
- Load JSON manifest and test files
- Handle inline and file-based inputs
- Parse the target format (Beancount, Ledger, hledger)

### Comparison

When comparing results:
- Use appropriate tolerance for decimal comparisons
- Normalize whitespace in error message matching
- Handle case-insensitive matching where specified

### Error Handling

The runner should:
- Catch implementation crashes and report as test errors
- Handle timeouts gracefully
- Provide clear error messages for configuration issues

### Performance

Recommendations:
- Parse test files once and cache
- Support parallel test execution
- Report individual test timing

## Reference Implementation

The Python reference implementation is in `runners/python/`:

```python
# runner.py - Main entry point
# loader.py - Test case loading

# Usage:
python runner.py --manifest ../beancount/v3/manifest.json
```

## Extending the Runner

To add support for a new implementation:

1. Create executor class implementing test execution
2. Register executor for the target format
3. Implement parse/validate/query methods

Example executor interface:

```python
class Executor(ABC):
    @abstractmethod
    def parse(self, source: str) -> ParseResult:
        pass

    @abstractmethod
    def validate(self, source: str) -> ValidationResult:
        pass

    @abstractmethod
    def query(self, source: str, query: str) -> QueryResult:
        pass
```

## Conformance Requirements

A runner is conformant if it:

1. Correctly interprets test case format
2. Produces valid TAP or JSON output
3. Accurately reports pass/fail/skip status
4. Handles all expected outcome types
5. Returns correct exit codes
