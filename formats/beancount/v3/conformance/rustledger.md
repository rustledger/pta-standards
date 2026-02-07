# Rustledger Conformance

This document tracks how Rustledger conforms to the Beancount v3 specification.

## Version Information

| Property | Value |
|----------|-------|
| Specification | Beancount v3 |
| Implementation | Rustledger |
| Tested Version | 0.5.x |
| Last Updated | 2026-02-07 |

## Conformance Legend

| Symbol | Meaning |
|--------|---------|
| :white_check_mark: | Fully conformant |
| :warning: | Partial - missing features or minor deviations |
| :x: | Non-conformant - significant deviation from spec |
| :hourglass: | Spec undefined - awaiting clarification |

## Summary

| Area | Status | Notes |
|------|--------|-------|
| Lexical Structure | :white_check_mark: | Fully conformant |
| Directives | :white_check_mark: | Fully conformant |
| Amounts & Numbers | :warning: | 28-digit precision limit |
| Accounts | :white_check_mark: | Fully conformant |
| Transactions | :white_check_mark: | Matches Python behavior |
| Costs | :warning: | Merge cost not implemented |
| Booking | :warning: | AVERAGE method not implemented |
| Balance Assertions | :white_check_mark: | Fully conformant |
| Tolerances | :white_check_mark: | Fully conformant |
| Metadata | :white_check_mark: | Fully conformant |
| Plugins | :warning: | Native plugins only, no Python |
| BQL | :white_check_mark: | Full query support |

---

## Detailed Conformance

### Amounts & Numbers

#### Decimal Precision

| Spec Requirement | Implementation | Status |
|------------------|----------------|--------|
| Arbitrary precision | 28 decimal digits max | :warning: |

**Deviation:** Rustledger uses `rust_decimal` which has a maximum precision of 28 significant digits. Python beancount uses Python's `decimal.Decimal` with arbitrary precision.

**Practical Impact:** None for real-world usage. Only affects synthetic test cases with extreme precision (e.g., 28+ decimal places).

**Known Failure:** 1 compatibility test fails due to this limitation:
- `beancount-lazy-plugins/tests_data_output_some_fund_output.beancount` - Contains `0.7142857142857142857142857143` amounts

**Future:** Consider migration to `bigdecimal` crate for arbitrary precision.

---

### Costs

#### Merge Cost Operator `{*}`

| Spec Requirement | Implementation | Status |
|------------------|----------------|--------|
| Merge all lots into average-cost lot | Not implemented | :warning: |

**Deviation:** The merge cost syntax `{*}` is parsed but not implemented.

**Error Produced:** `Cost merging is not yet implemented`

**Note:** Matches Python beancount behavior - also unimplemented.

---

### Booking Methods

#### AVERAGE Booking

| Spec Requirement | Implementation | Status |
|------------------|----------------|--------|
| Average cost basis booking | Not implemented | :warning: |

**Deviation:** The `AVERAGE` booking method is parsed but not implemented.

**Error Produced:** `AVERAGE booking method is not yet implemented`

**Note:** Matches Python beancount behavior - also unimplemented.

#### Implemented Booking Methods

| Method | Status | Notes |
|--------|--------|-------|
| STRICT | :white_check_mark: | Exact lot matching required |
| FIFO | :white_check_mark: | First-in, first-out |
| LIFO | :white_check_mark: | Last-in, first-out |
| HIFO | :white_check_mark: | Highest-in, first-out |
| NONE | :white_check_mark: | No automatic booking |
| AVERAGE | :x: | Not implemented |

---

### Plugins

#### Native vs Python Plugins

| Spec Requirement | Implementation | Status |
|------------------|----------------|--------|
| Python plugin loading | Native plugins only | :warning: |

**Deviation:** Rustledger cannot execute Python plugins. It provides:
1. Native Rust plugins (20 built-in, matching common beancount plugins)
2. WASM plugin support for sandboxed execution

**Native Plugin Equivalents:**

| Python Plugin | Rustledger Equivalent |
|--------------|----------------------|
| `beancount.plugins.auto_accounts` | `auto_accounts` |
| `beancount.plugins.check_commodity` | `check_commodity` |
| `beancount.plugins.coherent_cost` | `coherent_cost` |
| `beancount.plugins.commodity_attr` | `commodity_attr` |
| `beancount.plugins.currency_accounts` | `currency_accounts` |
| `beancount.plugins.implicit_prices` | `implicit_prices` |
| `beancount.plugins.leafonly` | `leaf_only` |
| `beancount.plugins.noduplicates` | `no_duplicates` |
| `beancount.plugins.nounused` | `no_unused` |
| `beancount.plugins.onecommodity` | `one_commodity` |
| `beancount.plugins.pedantic` | `pedantic` |
| `beancount.plugins.sellgains` | `sell_gains` |
| `beancount.plugins.unique_prices` | `unique_prices` |

**Workaround:** For unsupported Python plugins, pre-process with Python beancount.

---

### Error Type Mapping

Rustledger maps spec error categories to the following types:

| Spec Category | Rustledger Type | Module |
|---------------|-----------------|--------|
| Lexical errors | `LexerError` | `rustledger-parser` |
| Syntax errors | `ParseError` | `rustledger-parser` |
| Semantic errors | `ValidationError` | `rustledger-validate` |
| Balance errors | `BalanceError` | `rustledger-validate` |
| Booking errors | `BookingError` | `rustledger-booking` |
| Include errors | `IncludeError` | `rustledger-loader` |

#### Error Codes

Rustledger uses structured error codes:

```
E0001 - E0099: Lexer/Parser errors
E0100 - E0199: Validation errors
E0200 - E0299: Balance errors
E0300 - E0399: Booking errors
E0400 - E0499: Include/loader errors
```

#### JSON Output

```bash
rledger check --json ledger.beancount
```

Output format:
```json
{
  "errors": [
    {
      "code": "E0101",
      "message": "Account not opened",
      "file": "ledger.beancount",
      "line": 15,
      "column": 3
    }
  ],
  "warnings": [],
  "stats": {
    "entries": 150,
    "accounts": 25,
    "commodities": 3
  }
}
```

---

## CLI Compatibility

| Python Command | Rustledger Command | Status |
|----------------|-------------------|--------|
| `bean-check` | `rledger check` | :white_check_mark: |
| `bean-query` | `rledger query` | :white_check_mark: |
| `bean-format` | `rledger format` | :white_check_mark: |
| `bean-doctor` | `rledger doctor` | :white_check_mark: |
| `bean-report` | `rledger report` | :white_check_mark: |
| `bean-example` | - | Not implemented |
| `bean-extract` | - | Not implemented |
| `bean-identify` | - | Not implemented |
| `bean-file` | - | Not implemented |
| `bean-price` | - | Not implemented |

---

## Performance Comparison

Rustledger provides significant performance improvements:

| Operation | Python beancount | Rustledger | Speedup |
|-----------|-----------------|------------|---------|
| Parse 10K transactions | ~2.5s | ~0.08s | 30x |
| Validate large ledger | ~4.0s | ~0.15s | 25x |
| BQL query | ~1.5s | ~0.05s | 30x |

---

## Compatibility Testing

Rustledger maintains compatibility through:

1. **Conformance Tests:** Same test suite as Python beancount
2. **Differential Testing:** Compares output against Python for 600+ real ledgers
3. **Fuzz Testing:** Property-based testing for parser robustness

### Compatibility Rate

```
Total compatibility tests: 694
Passing: 693
Failing: 1 (decimal precision)
Rate: 99.86%
```

---

## Test Results

```
Last test run: 2026-02-07
Implementation: Rustledger 0.5.x
Tests passed: TBD (awaiting CI run)
Tests failed: TBD
Tests skipped: 9

Skipped tests (same as Python):
- account-closed-posting-same-day: Close date semantics UNDEFINED
- metadata-duplicate-key: Duplicate metadata behavior UNDEFINED
- include-cycle-detection: Requires external file setup
- booking-average-cost: AVERAGE method not implemented
- cost-asterisk-merge: Cost merging {*} not implemented
- document-directive: Requires fixture file
- bql-tag-filter: has_tag function not in BQL
- bql-link-filter: matches_link function not in BQL
- invalid-transaction-no-postings: Empty transactions UNDEFINED
```

---

## Rustledger-Specific Features

Features in Rustledger not in Python beancount:

| Feature | Description |
|---------|-------------|
| WASM support | Run in browser via WebAssembly |
| LSP server | Language Server Protocol support |
| Structured errors | Error codes with machine-readable format |
| Parallel parsing | Multi-threaded include processing |
| Incremental parsing | Fast re-parse on file changes |

---

## Building Rustledger

```bash
# From source
git clone https://github.com/rustledger/rustledger
cd rustledger
cargo build --release

# Install
cargo install rustledger
```

## Running Conformance Tests

```bash
# Set binary path
export RLEDGER_BIN=/path/to/rledger

# Run tests
cd tests/harness/runners/python
python runner.py --manifest ../../../beancount/v3/manifest.json --impl rustledger
```
