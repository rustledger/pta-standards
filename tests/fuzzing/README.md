# Fuzzing Test Infrastructure

This directory contains resources for fuzz testing PTA format parsers.

## Overview

Fuzz testing helps discover edge cases, crashes, and security vulnerabilities by generating random or semi-random inputs. The resources here support multiple fuzzing tools.

## Directory Structure

```
fuzzing/
├── README.md           # This file
├── dictionaries/       # Token dictionaries for guided fuzzing
│   ├── beancount.dict  # Beancount tokens
│   ├── ledger.dict     # Ledger tokens
│   └── hledger.dict    # hledger tokens
├── seeds/              # Seed corpus of valid files
│   ├── beancount/      # Beancount seed files
│   ├── ledger/         # Ledger seed files
│   └── hledger/        # hledger seed files
└── targets/            # Fuzzing harness templates
    ├── parse_fuzz.py   # Python fuzzing harness
    └── parse_fuzz.rs   # Rust fuzzing harness
```

## Dictionaries

Dictionary files contain tokens that are meaningful to the parser. Fuzzers use these to generate more effective test cases.

Format: One token per line. Lines starting with `#` are comments.

```
# Example
"open"
"2024-01-15"
"USD"
```

## Using with AFL

```bash
# Install AFL
apt install afl

# Build with AFL instrumentation
CC=afl-gcc cargo build --release

# Run fuzzer
afl-fuzz -i seeds/beancount -o findings -x dictionaries/beancount.dict -- ./target/release/parser @@
```

## Using with libFuzzer

```bash
# Build with libFuzzer (Rust)
cargo +nightly fuzz run parse_fuzz -- -dict=dictionaries/beancount.dict

# With corpus
cargo +nightly fuzz run parse_fuzz seeds/beancount -- -dict=dictionaries/beancount.dict
```

## Using with Honggfuzz

```bash
# Install honggfuzz
cargo install honggfuzz

# Run
HFUZZ_RUN_ARGS="-w dictionaries/beancount.dict" cargo hfuzz run parse_fuzz
```

## Seed Corpus

The `seeds/` directory contains minimal valid files that serve as starting points:

| File | Purpose |
|------|---------|
| minimal.* | Smallest valid file |
| directives.* | One of each directive type |
| complex.* | Complex but valid file |
| edge-cases.* | Known edge cases |

## Findings

When a fuzzer finds a crash or hang:

1. Minimize the test case
2. Verify it's reproducible
3. Check if it's a duplicate
4. File an issue with the test case

## Coverage-Guided Fuzzing

For best results, compile with coverage instrumentation:

```bash
# Rust
RUSTFLAGS="-C instrument-coverage" cargo build

# C/C++
clang -fprofile-instr-generate -fcoverage-mapping ...
```

## Recommended Fuzzing Duration

| Phase | Duration | Purpose |
|-------|----------|---------|
| Quick | 1 hour | Smoke test |
| Standard | 24 hours | Regular testing |
| Deep | 1 week | Release preparation |

## Security Considerations

When fuzzing, the parser should:

- Never crash (panic/segfault)
- Never hang indefinitely
- Use bounded memory
- Handle malformed input gracefully

Report security issues via the security policy.
