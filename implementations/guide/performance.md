# Performance Guide

This guide covers performance considerations for PTA implementations.

## Performance Targets

### Baseline Expectations

For a well-optimized implementation:

| Metric | Target |
|--------|--------|
| Parse + validate (10K txns) | < 500ms |
| Parse + validate (100K txns) | < 5 seconds |
| Memory usage (10K txns) | < 100 MB |
| Startup time | < 50ms |
| Query execution (typical) | < 100ms |

### By File Size

| Size | Transactions | Target Time |
|------|--------------|-------------|
| Small | < 1K | < 50ms |
| Medium | 1K - 10K | < 500ms |
| Large | 10K - 100K | < 5 seconds |
| Very Large | > 100K | < 30 seconds |

## Complexity Bounds

### Time Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Parse | O(n) | Linear in input size |
| Sort directives | O(n log n) | Stable sort |
| Interpolation | O(n × p) | n transactions, p postings each |
| Booking (FIFO/LIFO) | O(n × l) | n reductions, l lots average |
| Booking (STRICT) | O(n × l) | Usually l = 1 |
| Balance check | O(n) | Linear scan |
| Query (full scan) | O(n) | All transactions |
| Query (GROUP BY) | O(n log g) | g groups |

### Space Complexity

| Data Structure | Complexity | Notes |
|----------------|------------|-------|
| AST | O(n) | Linear in input |
| Inventories | O(a × l) | a accounts, l lots each |
| String interner | O(s) | s unique strings |
| Source map | O(f) | f files |

## Optimization Strategies

### 1. String Interning

Intern account names and currencies to reduce memory and enable fast comparison:

```
// Before: 24 bytes per account reference (String)
// After: 4 bytes per account reference (interned ID)
```

**Expected impact:** 50% memory reduction for string-heavy ledgers.

Benefits:
- Reduced memory usage
- O(1) equality comparison
- Cache-friendly access patterns

### 2. Arena Allocation

Allocate AST nodes in contiguous memory:

```
arena = Arena::new()
for directive in parse(source):
    arena.alloc(directive)
```

**Expected impact:** 2x parse speed improvement.

Benefits:
- Better cache locality
- Reduced allocator overhead
- Simplified memory management

### 3. Parallel Parsing

Parse included files in parallel:

```
files = collect_includes(main_file)
asts = parallel_map(files, parse_file)
```

**Expected impact:** Nx speedup for N files on N cores.

Considerations:
- Thread pool overhead
- File I/O may be the bottleneck
- Source map construction must be synchronized

### 4. Lazy Computation

Compute inventories on-demand rather than eagerly:

```
ledger.inventory(account, date):
    // Compute only up to requested date
    return compute_inventory_at(account, date)
```

**Expected impact:** Faster validation for partial checks.

Use cases:
- Quick syntax checking
- Balance assertions at specific dates
- Interactive exploration

### 5. Incremental Updates

For interactive use, reparse only changed sections:

```
on_file_change(file, changes):
    invalidate_directives_in_range(changes)
    reparse_affected_sections(changes)
    update_downstream_computations()
```

**Expected impact:** < 100ms response for edits.

## Profiling

### CPU Profiling

Identify hot spots:

```bash
# Linux perf
perf record --call-graph dwarf ./pta-tool check large.beancount
perf report

# Flamegraph
cargo flamegraph -- check large.beancount
```

### Memory Profiling

Track allocations:

```bash
# heaptrack
heaptrack ./pta-tool check large.beancount
heaptrack_gui heaptrack.*.gz

# valgrind massif
valgrind --tool=massif ./pta-tool check large.beancount
ms_print massif.out.*
```

### Benchmarking

Consistent measurement:

```bash
# Run benchmarks
cargo bench

# Compare against baseline
cargo bench -- --save-baseline main
git checkout feature-branch
cargo bench -- --baseline main
```

## Common Bottlenecks

### 1. String Allocations

**Symptom:** High allocation count in profiler.

**Solution:**
- Intern strings
- Use string slices instead of owned strings
- Pool temporary strings

### 2. Hash Map Overhead

**Symptom:** Significant time in hash operations.

**Solution:**
- Use faster hasher (FxHash, AHash)
- Pre-size hash maps
- Consider sorted vectors for small collections

### 3. Decimal Arithmetic

**Symptom:** Slow balance calculations.

**Solution:**
- Use fixed-point arithmetic where possible
- Batch operations
- Consider SIMD for aggregations

### 4. I/O Bound

**Symptom:** CPU utilization low during parsing.

**Solution:**
- Memory-map files
- Read files in parallel
- Use buffered I/O

### 5. Sorting Overhead

**Symptom:** Significant time in directive sorting.

**Solution:**
- Use radix sort for dates
- Maintain sorted order incrementally
- Parallel sort for large datasets

## Regression Prevention

### CI Benchmarks

Run benchmarks in CI:

```yaml
- name: Run benchmarks
  run: cargo bench -- --save-baseline ci

- name: Check for regression
  run: |
    cargo bench -- --baseline ci --threshold 10
    # Fail if >10% regression
```

### Benchmark Database

Track results over time:

```bash
# Save to JSON
cargo bench -- --format json > bench-results.json

# Upload to tracking
curl -X POST https://bench.example.com/upload -d @bench-results.json
```

## Memory Budget

### Per-Directive Overhead

Target: < 1 KB per directive average.

| Component | Typical Size |
|-----------|--------------|
| Date | 4 bytes |
| Type tag | 1 byte |
| Account refs | 4 bytes each |
| Amounts | 24 bytes each |
| Metadata | Variable |

### Per-Account Overhead

Target: < 10 KB per account average.

| Component | Typical Size |
|-----------|--------------|
| Name (interned) | 4 bytes |
| Inventory | 48 bytes base + lots |
| Each lot | 56 bytes |

## Testing Performance

### Synthetic Benchmarks

Generate test data:

```
generate_ledger(n_transactions):
    for i in 1..n:
        yield random_transaction()
```

### Real-World Benchmarks

Use representative files:
- Personal finance (5K-50K transactions)
- Small business (10K-100K transactions)
- Multi-year archives (100K+ transactions)

### Comparison Benchmarks

Compare against reference implementations:

```bash
echo "Reference implementation:"
time python -m beancount.scripts.check "$FILE"

echo "This implementation:"
time ./pta-tool check "$FILE"
```
