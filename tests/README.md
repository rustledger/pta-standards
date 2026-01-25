# Conformance Test Suite

Test cases for verifying implementation conformance.

## Structure

```
tests/
├── harness/            # Test runner specification
│   ├── spec.md         # Test format specification
│   └── runners/        # Reference implementations
├── beancount/v3/       # Beancount test cases
├── ledger/v1/          # Ledger test cases
├── hledger/v1/         # hledger test cases
├── cross-format/       # Conversion tests
├── differential/       # Compare implementations
└── fuzzing/            # Fuzz testing corpus
```

## Test Categories

| Category | Description |
|----------|-------------|
| syntax/valid/ | Files that must parse successfully |
| syntax/invalid/ | Files that must fail parsing |
| validation/pass/ | Files that must validate |
| validation/fail/ | Files with validation errors |
| booking/ | Cost basis algorithm tests |
| regression/ | Bug fix verification |

## Running Tests

See [harness/README.md](harness/README.md) for instructions.
