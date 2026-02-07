# Test Harness

The test harness provides a standardized way to run conformance tests against any PTA implementation.

## Quick Start

```bash
# Run all Beancount tests
python runners/python/runner.py --manifest ../beancount/v3/manifest.json

# Run specific suite
python runners/python/runner.py --manifest ../beancount/v3/manifest.json --suite syntax/valid

# Output JSON results
python runners/python/runner.py --manifest ../beancount/v3/manifest.json --format json > results.json

# Filter by tags
python runners/python/runner.py --manifest ../beancount/v3/manifest.json --tags booking,fifo
```

## Directory Structure

```
harness/
├── README.md              # This file
├── spec.md                # Test format specification
├── interface.md           # Runner interface specification
├── manifest.schema.json   # JSON Schema for manifest files
├── test-case.schema.json  # JSON Schema for test cases
└── runners/
    ├── python/            # Reference Python runner
    │   ├── runner.py      # Main entry point
    │   └── loader.py      # Test case loading
    └── rust/              # Rust runner (template)
        ├── Cargo.toml
        └── src/main.rs
```

## Test Organization

Tests are organized by format and version:

```
tests/
├── beancount/v3/
│   ├── manifest.json      # Test suite manifest
│   ├── syntax/valid/      # Valid syntax tests
│   ├── syntax/invalid/    # Invalid syntax tests
│   ├── validation/        # Semantic validation
│   ├── booking/           # Booking algorithm tests
│   ├── bql/               # Query language tests
│   └── regression/        # Bug fix tests
├── ledger/v1/
│   └── ...
└── hledger/v1/
    └── ...
```

## Writing Tests

### Test Case Format

```json
{
  "id": "unique-test-id",
  "description": "What this test verifies",
  "input": {
    "inline": "2024-01-01 open Assets:Bank"
  },
  "expected": {
    "parse": "success",
    "directives": 1
  },
  "tags": ["open", "directive"]
}
```

### Input Types

**Inline content:**
```json
"input": {
  "inline": "2024-01-01 * \"Test\"\n  Assets:A  100 USD\n  Assets:B"
}
```

**External file:**
```json
"input": {
  "file": "fixtures/complex-example.beancount"
}
```

### Expected Outcomes

```json
"expected": {
  "parse": "success|error",
  "validate": "success|error|skip",
  "directives": 5,
  "error_count": 2,
  "error_contains": ["balance", "failed"],
  "balance": {
    "Assets:Bank": {"USD": "1000.00"}
  }
}
```

## Running Tests

### Command Line Options

| Option | Description |
|--------|-------------|
| `--manifest PATH` | Path to manifest.json (required) |
| `--suite NAME` | Run only specific test suite |
| `--test ID` | Run single test by ID |
| `--tags TAG,...` | Filter by tags |
| `--format tap\|json` | Output format (default: tap) |
| `--verbose` | Show detailed output |
| `--fail-fast` | Stop on first failure |

### Output Formats

**TAP (Test Anything Protocol):**
```
TAP version 14
1..164
ok 1 - empty-file: Empty file is valid
ok 2 - comment-only: File with only comments
not ok 3 - invalid-date: Invalid date format
  ---
  expected: parse error
  actual: parse success
  ...
```

**JSON:**
```json
{
  "summary": {
    "total": 164,
    "passed": 160,
    "failed": 3,
    "skipped": 1
  },
  "results": [...]
}
```

## Implementing a Runner

See [interface.md](interface.md) for the runner interface specification.

Requirements:
1. Parse manifest.json to find test suites
2. Load tests.json from each suite directory
3. Execute tests against target implementation
4. Compare actual vs expected results
5. Output results in TAP or JSON format

## Conformance Levels

Tests are tagged by conformance level:

| Level | Required Tests |
|-------|----------------|
| 1 - Parse | syntax/valid, syntax/invalid |
| 2 - Validate | Level 1 + validation |
| 3 - Query | Level 2 + bql |
| 4 - Full | All tests |

## See Also

- [spec.md](spec.md) - Test format specification
- [interface.md](interface.md) - Runner interface
- [../README.md](../README.md) - Test suite overview
