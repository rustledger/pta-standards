# Benchmark Specification

This document specifies the standard benchmarks for PTA implementations.

## Benchmark Suite

### Core Benchmarks

Every conforming implementation should report these:

| ID | Name | Description |
|----|------|-------------|
| `B001` | parse-small | Parse 100 transactions |
| `B002` | parse-medium | Parse 10,000 transactions |
| `B003` | parse-large | Parse 100,000 transactions |
| `B004` | validate-medium | Validate 10,000 transactions |
| `B005` | memory-medium | Memory usage for 10,000 transactions |

### Extended Benchmarks

Optional benchmarks for specific features:

| ID | Name | Description |
|----|------|-------------|
| `B101` | query-simple | Simple balance query |
| `B102` | query-filter | Query with date filter |
| `B103` | query-aggregate | Aggregation query |
| `B201` | incremental-add | Add single transaction |
| `B202` | incremental-reparse | Reparse after edit |

## Benchmark Definitions

### B001: parse-small

**Purpose:** Baseline parse performance

**Input:**
```
File: benchmarks/small.beancount
Size: ~10 KB
Transactions: 100
Accounts: 20
Commodities: 3
```

**Measurement:**
- Parse file from disk
- Return number of directives
- Measure wall-clock time

**Expected Results:**
- Most implementations: < 10 ms
- Baseline (Python beancount): ~50 ms

### B002: parse-medium

**Purpose:** Typical personal ledger performance

**Input:**
```
File: benchmarks/medium.beancount
Size: ~1 MB
Transactions: 10,000
Accounts: 100
Commodities: 10
Date range: 3 years
```

**Measurement:**
- Parse file from disk
- Include lexing and AST construction
- Exclude validation

### B003: parse-large

**Purpose:** Large ledger stress test

**Input:**
```
File: benchmarks/large.beancount
Size: ~10 MB
Transactions: 100,000
Accounts: 500
Commodities: 50
Date range: 10 years
```

**Measurement:**
- Same as B002
- Tests scalability

### B004: validate-medium

**Purpose:** Validation performance

**Input:** Same as B002

**Measurement:**
- Parse + full validation
- Include all semantic checks
- Include balance verification

### B005: memory-medium

**Purpose:** Memory efficiency

**Input:** Same as B002

**Measurement:**
- Peak heap allocation
- Resident set size
- Memory per transaction

## Benchmark Input Format

### File Structure

Benchmark files follow consistent structure:

```beancount
; Benchmark file: medium.beancount
; Generated: 2024-01-15
; Transactions: 10000
; Accounts: 100
; Commodities: 10

option "title" "Benchmark Ledger"
option "operating_currency" "USD"

; Account declarations
2020-01-01 open Assets:Bank:Checking USD
2020-01-01 open Assets:Bank:Savings USD
2020-01-01 open Assets:Investment:Brokerage USD,AAPL,GOOG
; ... more accounts

; Transactions
2020-01-15 * "Grocery Store" "Weekly shopping"
  Expenses:Food:Groceries  50.00 USD
  Assets:Bank:Checking

; ... 9999 more transactions
```

### Complexity Levels

**Low Complexity:**
- Simple transactions (2 postings)
- Single commodity
- No metadata

**Medium Complexity:**
- 2-4 postings per transaction
- Multiple commodities
- Some metadata/tags

**High Complexity:**
- Complex transactions (cost basis, lots)
- Many commodities
- Full metadata
- Balance assertions

## Result Schema

### Single Benchmark

```json
{
  "benchmark_id": "B002",
  "name": "parse-medium",
  "input": {
    "file": "medium.beancount",
    "size_bytes": 1048576,
    "transactions": 10000
  },
  "configuration": {
    "warm_up_iterations": 3,
    "measured_iterations": 50,
    "timeout_seconds": 60
  },
  "results": {
    "time": {
      "unit": "milliseconds",
      "mean": 45.2,
      "median": 44.8,
      "std_dev": 2.1,
      "min": 42.1,
      "max": 52.3,
      "p95": 48.9,
      "p99": 51.2
    },
    "throughput": {
      "mb_per_second": 22.1,
      "transactions_per_second": 221239
    },
    "memory": {
      "peak_mb": 85.3,
      "resident_mb": 72.1
    }
  },
  "environment": {
    "os": "Ubuntu 22.04",
    "cpu": "AMD Ryzen 9 5900X",
    "ram_gb": 64
  }
}
```

### Full Suite

```json
{
  "suite": "pta-benchmarks-v1",
  "timestamp": "2024-01-15T10:30:00Z",
  "implementation": {
    "name": "rustledger",
    "version": "0.1.0",
    "commit": "abc123"
  },
  "benchmarks": [
    { "benchmark_id": "B001", ... },
    { "benchmark_id": "B002", ... },
    { "benchmark_id": "B003", ... }
  ],
  "summary": {
    "total_benchmarks": 5,
    "passed": 5,
    "failed": 0
  }
}
```

## Baseline Comparisons

### Reference Implementation Times

| Benchmark | beancount 3.0 | Notes |
|-----------|---------------|-------|
| B001 | 50 ms | Python baseline |
| B002 | 450 ms | Python baseline |
| B003 | 5000 ms | Python baseline |
| B004 | 650 ms | Parse + validate |
| B005 | 500 MB | Python objects |

### Speedup Calculation

```
speedup = baseline_time / measured_time

Example:
  beancount B002: 450 ms
  rustledger B002: 45 ms
  speedup = 450 / 45 = 10x
```

## Benchmark Runner Interface

### Command Line

```bash
# Run single benchmark
pta-bench --benchmark B002 --impl rustledger --output results.json

# Run all benchmarks
pta-bench --all --impl rustledger --output results.json

# Compare implementations
pta-bench --all --impl beancount,rustledger --compare
```

### Programmatic

```python
from pta_bench import BenchmarkRunner, Benchmark

runner = BenchmarkRunner(implementation="rustledger")

# Run single benchmark
result = runner.run(Benchmark.PARSE_MEDIUM)
print(f"Time: {result.time.mean} ms")

# Run all benchmarks
results = runner.run_all()
results.save("results.json")
```

## CI Integration

### GitHub Actions

```yaml
name: Benchmarks

on:
  push:
    branches: [main]
  pull_request:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup
        run: pip install pta-bench

      - name: Run benchmarks
        run: pta-bench --all --impl my-impl --output results.json

      - name: Compare with main
        run: pta-bench compare results.json baseline.json

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            // Post benchmark comparison as PR comment
```

## Validation

### Required Checks

1. **Correctness** - Benchmark produces correct output
2. **Stability** - Low variance between runs
3. **Reproducibility** - Same results on same hardware

### Anomaly Detection

Flag results if:
- Variance > 20% of mean
- Result differs > 50% from previous run
- Memory usage grows unexpectedly

## See Also

- [Benchmark Methodology](methodology.md)
- [Test Requirements](../process/test-requirements.md)
