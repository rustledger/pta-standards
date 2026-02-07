# Differential Testing

Differential testing (also known as differential fuzzing) compares the behavior of multiple implementations against the same input to find discrepancies.

## Purpose

While conformance tests verify behavior against a specification, differential testing:
- Finds edge cases where implementations diverge
- Catches bugs that conformance tests miss
- Validates that alternative implementations match reference behavior
- Discovers undocumented behavior differences

## Architecture

```
                    ┌─────────────┐
                    │   Input     │
                    │  Generator  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │  Impl A  │ │  Impl B  │ │  Impl C  │
       │(Reference)│ │  (Test)  │ │  (Test)  │
       └────┬─────┘ └────┬─────┘ └────┬─────┘
            │            │            │
            ▼            ▼            ▼
       ┌─────────────────────────────────────┐
       │           Comparator                │
       │  - Parse results                    │
       │  - Error messages                   │
       │  - Validation errors                │
       │  - Query results                    │
       │  - Balance calculations             │
       └─────────────────────────────────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Divergence  │
                  │   Report    │
                  └─────────────┘
```

## Comparison Groups

### Beancount Implementations

| Implementation | Type | Notes |
|---------------|------|-------|
| beancount (Python) | Reference | v3 is the canonical implementation |
| fava | Web UI | Uses beancount as backend |
| rustledger | Alternative | Rust implementation |
| beancount-parser-lima | Parser only | TypeScript implementation |

### Ledger Implementations

| Implementation | Type | Notes |
|---------------|------|-------|
| ledger | Reference | C++ original |
| hledger | Compatible | Haskell, mostly compatible |
| ledger-cli | Go port | Subset of features |

### hledger Implementations

| Implementation | Type | Notes |
|---------------|------|-------|
| hledger | Reference | Haskell original |
| hledger-web | Web UI | Uses hledger as backend |

## Comparison Dimensions

### 1. Parse Results

Compare the parsed AST/directive structure:

```json
{
  "dimension": "parse",
  "compare": {
    "directive_count": true,
    "directive_types": true,
    "directive_dates": true,
    "account_names": true,
    "amounts": true,
    "metadata": true
  },
  "tolerance": {
    "amount_precision": 10
  }
}
```

### 2. Error Detection

Compare which errors are detected:

```json
{
  "dimension": "errors",
  "compare": {
    "error_count": true,
    "error_types": true,
    "error_locations": true,
    "error_severity": true
  },
  "normalize": {
    "line_numbers": "relative",
    "messages": "ignore"
  }
}
```

### 3. Balance Calculation

Compare final balances after processing:

```json
{
  "dimension": "balance",
  "compare": {
    "account_balances": true,
    "inventory_positions": true,
    "unrealized_gains": false
  },
  "tolerance": {
    "amount": "1e-8"
  }
}
```

### 4. Query Results

Compare query output (for BQL/query-capable implementations):

```json
{
  "dimension": "query",
  "queries": [
    "SELECT account, sum(position) GROUP BY account",
    "SELECT date, narration WHERE account ~ 'Expenses'",
    "BALANCES"
  ],
  "compare": {
    "row_count": true,
    "column_names": true,
    "cell_values": true
  }
}
```

## Input Sources

### 1. Conformance Test Inputs

Use existing test cases from `tests/beancount/`, `tests/ledger/`, `tests/hledger/`:

```bash
# Run differential test on all conformance inputs
differential-test --config config.json --inputs conformance
```

### 2. Fuzzer-Generated Inputs

Use AFL/libFuzzer corpus:

```bash
# Run on fuzzer corpus
differential-test --config config.json --inputs fuzzing/corpus/
```

### 3. Real-World Ledgers

Use sanitized real-world ledger files:

```bash
# Run on real-world examples
differential-test --config config.json --inputs real-world/
```

### 4. Grammar-Based Generation

Generate inputs from grammar:

```bash
# Generate and test random valid inputs
differential-test --config config.json --generate 1000
```

## Running Differential Tests

### Prerequisites

Install all implementations to compare:

```bash
# Beancount (Python)
pip install beancount

# rustledger
cargo install rustledger

# hledger
stack install hledger
# or: apt install hledger

# Ledger
apt install ledger
```

### Basic Usage

```bash
# Compare beancount implementations
./differential.py --config config.json --group beancount

# Compare ledger implementations
./differential.py --config config.json --group ledger

# Compare specific implementations
./differential.py --config config.json --impls "beancount,rustledger"

# Test single file
./differential.py --config config.json --file test.beancount

# Generate divergence report
./differential.py --config config.json --report divergences.json
```

### CI Integration

```yaml
# .github/workflows/differential.yml
name: Differential Testing
on:
  schedule:
    - cron: '0 2 * * *'  # Nightly
  workflow_dispatch:

jobs:
  differential:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install implementations
        run: |
          pip install beancount
          cargo install rustledger

      - name: Run differential tests
        run: |
          cd tests/differential
          ./differential.py --config config.json --report report.json

      - name: Upload divergences
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: divergences
          path: tests/differential/divergences/
```

## Divergence Handling

### Classification

Divergences are classified as:

| Type | Description | Action |
|------|-------------|--------|
| `bug` | Clear implementation bug | File issue |
| `undocumented` | Undocumented behavior difference | Document or fix |
| `intentional` | Known intentional difference | Add to known-divergences |
| `precision` | Floating-point precision difference | Adjust tolerance |
| `undefined` | Spec says "undefined" | Document as implementation-specific |

### Known Divergences

Some divergences are expected and documented in `known-divergences.json`:

```json
{
  "divergences": [
    {
      "id": "precision-28-digits",
      "implementations": ["beancount", "rustledger"],
      "description": "rustledger uses rust_decimal (28 digit precision) vs Python arbitrary precision",
      "type": "precision",
      "inputs": ["extreme-precision.beancount"]
    },
    {
      "id": "error-message-format",
      "implementations": ["beancount", "rustledger"],
      "description": "Error message wording differs",
      "type": "intentional",
      "dimension": "errors.messages"
    }
  ]
}
```

### Minimizing Divergences

When a divergence is found, use delta debugging to minimize:

```bash
# Find minimal diverging input
./minimize.py --input divergence-001.beancount --output minimal.beancount
```

## Output Format

### Divergence Report

```json
{
  "run": {
    "timestamp": "2024-01-15T10:30:00Z",
    "implementations": ["beancount-3.0.0", "rustledger-0.1.0"],
    "input_count": 500
  },
  "summary": {
    "total_inputs": 500,
    "matching": 495,
    "diverging": 5,
    "errors": 0
  },
  "divergences": [
    {
      "id": "div-001",
      "input": "tests/edge-case-001.beancount",
      "dimension": "balance",
      "implementations": {
        "beancount-3.0.0": {
          "Expenses:Food": {"USD": "50.00"}
        },
        "rustledger-0.1.0": {
          "Expenses:Food": {"USD": "50.000000001"}
        }
      },
      "classification": "precision",
      "notes": "Rounding difference in interpolation"
    }
  ]
}
```

## Best Practices

1. **Start with conformance tests** - Use known-good inputs first
2. **Normalize output** - Remove timestamps, paths, implementation-specific formatting
3. **Set appropriate tolerances** - Decimal precision, line numbers, etc.
4. **Document known divergences** - Don't repeatedly flag the same issues
5. **Minimize diverging inputs** - Find the smallest reproducing case
6. **Test incrementally** - Don't compare everything at once
7. **Automate in CI** - Run nightly to catch regressions

## Directory Structure

```
tests/differential/
├── README.md              # This file
├── config.json            # Implementation and comparison config
├── known-divergences.json # Expected divergences
├── differential.py        # Main runner script
├── minimize.py            # Delta debugging minimizer
├── comparators/           # Comparison logic
│   ├── parse.py
│   ├── balance.py
│   ├── errors.py
│   └── query.py
├── normalizers/           # Output normalization
│   ├── beancount.py
│   ├── ledger.py
│   └── hledger.py
├── corpus/                # Test inputs
│   ├── conformance/       # Symlinks to conformance tests
│   ├── fuzzing/           # Fuzzer-generated
│   └── real-world/        # Sanitized real ledgers
└── divergences/           # Captured divergences
    ├── div-001.beancount
    └── div-001.json
```

## See Also

- [Fuzzing Documentation](../fuzzing/README.md)
- [Test Harness Specification](../harness/spec.md)
- [Cross-Format Tests](../cross-format/README.md)
