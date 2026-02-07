# Benchmark Methodology

This document describes the methodology for performance benchmarking of PTA implementations.

## Purpose

Performance benchmarks help users:
- Choose implementations based on speed requirements
- Understand performance characteristics
- Identify performance regressions
- Compare implementations fairly

## Benchmark Categories

### 1. Parse Performance

Measure time to parse input files.

| Metric | Description |
|--------|-------------|
| `parse_time_ms` | Time to parse file (cold) |
| `parse_throughput_mb_s` | MB/s parsing speed |
| `parse_lines_per_sec` | Lines parsed per second |

### 2. Validation Performance

Measure time to validate parsed data.

| Metric | Description |
|--------|-------------|
| `validate_time_ms` | Time to validate (after parse) |
| `total_time_ms` | Parse + validate combined |

### 3. Query Performance

Measure time to execute queries (Beancount BQL).

| Metric | Description |
|--------|-------------|
| `query_time_ms` | Time to execute query |
| `query_cold_ms` | First query (cold cache) |
| `query_warm_ms` | Subsequent queries (warm) |

### 4. Memory Usage

Measure memory consumption.

| Metric | Description |
|--------|-------------|
| `peak_memory_mb` | Peak memory during parse |
| `resident_memory_mb` | Steady-state memory |
| `memory_per_txn_kb` | Memory per transaction |

## Test Data

### Standard Benchmarks

Use the provided benchmark files:

| File | Size | Transactions | Description |
|------|------|--------------|-------------|
| `small.beancount` | 10 KB | 100 | Quick smoke test |
| `medium.beancount` | 1 MB | 10,000 | Typical personal ledger |
| `large.beancount` | 10 MB | 100,000 | Large/multi-year ledger |
| `huge.beancount` | 100 MB | 1,000,000 | Stress test |

### Synthetic Generation

Generate benchmark files:

```bash
# Generate a file with N transactions
./scripts/generate-benchmark.py --transactions 50000 --output bench50k.beancount
```

Generator options:
- `--transactions N` - Number of transactions
- `--accounts N` - Number of accounts
- `--commodities N` - Number of commodities
- `--start-date YYYY-MM-DD` - Starting date
- `--complexity [low|medium|high]` - Transaction complexity

### Real-World Data

For realistic benchmarks, use:
- Anonymized real ledgers (with permission)
- Generated ledgers mimicking real patterns
- Public example ledgers

## Measurement Protocol

### Warm-up

Before measuring:
1. Run 3 warm-up iterations (discarded)
2. Let system stabilize
3. Begin measurement

### Iterations

For each benchmark:
1. Run minimum 10 iterations
2. Run until 95% confidence interval < 5% of mean
3. Maximum 100 iterations

### Statistical Analysis

Report these statistics:
- **Mean** - Average time
- **Median** - 50th percentile
- **Std Dev** - Standard deviation
- **Min/Max** - Range
- **P95/P99** - High percentiles

### Outlier Handling

- Remove outliers > 3 standard deviations
- Report if more than 10% of runs are outliers
- Investigate cause of outliers

## Environment Requirements

### Isolation

- Disable CPU frequency scaling (use `performance` governor)
- Close unnecessary applications
- Disable network if not needed
- Run on dedicated hardware if possible

### System Reporting

Report these system details:
- OS name and version
- CPU model and core count
- RAM size and speed
- Disk type (SSD/HDD/NVMe)
- Compiler/runtime version

### Docker Environment

For reproducible benchmarks:

```dockerfile
FROM ubuntu:22.04

# Install implementations
RUN apt-get update && apt-get install -y \
    python3-pip \
    ledger \
    hledger

RUN pip install beancount

# Copy benchmark runner
COPY benchmark.py /benchmark/

WORKDIR /benchmark
CMD ["python3", "benchmark.py"]
```

## Reporting Format

### JSON Output

```json
{
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "system": {
      "os": "Ubuntu 22.04",
      "cpu": "AMD Ryzen 9 5900X",
      "cores": 12,
      "ram_gb": 64,
      "disk": "NVMe SSD"
    },
    "implementation": {
      "name": "rustledger",
      "version": "0.1.0"
    }
  },
  "results": [
    {
      "benchmark": "parse",
      "file": "medium.beancount",
      "file_size_mb": 1.0,
      "transactions": 10000,
      "iterations": 50,
      "metrics": {
        "time_ms": {
          "mean": 45.2,
          "median": 44.8,
          "std_dev": 2.1,
          "min": 42.1,
          "max": 52.3,
          "p95": 48.9,
          "p99": 51.2
        },
        "throughput_mb_s": 22.1,
        "peak_memory_mb": 85.3
      }
    }
  ]
}
```

### Comparison Table

For comparing implementations:

| Benchmark | beancount | rustledger | Speedup |
|-----------|-----------|------------|---------|
| Parse (medium) | 450 ms | 45 ms | 10x |
| Validate (medium) | 200 ms | 25 ms | 8x |
| Query (simple) | 50 ms | 8 ms | 6x |
| Memory (medium) | 500 MB | 85 MB | 5.9x |

## Fair Comparison Guidelines

### Apples to Apples

When comparing:
- Use same input file
- Same validation level (parse-only vs full validation)
- Same output requirements
- Same hardware and OS

### Feature Parity

Note feature differences:
- "rustledger does not run plugins, comparison is parse+validate only"
- "hledger includes balance calculation in parse time"

### Version Pinning

Record exact versions:
- Implementation version
- Test suite version
- Benchmark script version

## Running Benchmarks

### Quick Benchmark

```bash
# Single implementation, single file
./benchmark.py --impl beancount --file medium.beancount

# Compare two implementations
./benchmark.py --impl beancount,rustledger --file medium.beancount
```

### Full Suite

```bash
# Run all benchmarks
./benchmark.py --full-suite --output results.json

# With comparison chart
./benchmark.py --full-suite --output results.json --chart chart.png
```

### CI Integration

```yaml
# .github/workflows/benchmark.yml
name: Benchmark
on:
  push:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run benchmarks
        run: ./benchmark.py --full-suite --output results.json

      - name: Compare with baseline
        run: ./compare-baseline.py results.json

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: results.json
```

## Avoiding Common Pitfalls

1. **Cold vs Warm Cache** - First run is always slower
2. **Background Processes** - Can cause variance
3. **Thermal Throttling** - CPUs slow down when hot
4. **Memory Pressure** - Swapping destroys performance
5. **I/O Bottlenecks** - Use RAM disk for pure CPU benchmarks

## See Also

- [Benchmark Specification](spec.md)
- [Test Requirements](../process/test-requirements.md)
