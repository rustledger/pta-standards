# Implementations

This directory contains resources for implementing the PTA specifications.

## Implementation Guide

The `guide/` directory contains detailed guidance for implementers:

| Document | Description |
|----------|-------------|
| [Getting Started](guide/getting-started.md) | Overview and first steps |
| [Parser](guide/parser.md) | Parsing with error recovery |
| [Validator](guide/validator.md) | Validation implementation |
| [Performance](guide/performance.md) | Optimization strategies |
| [Error Messages](guide/error-messages.md) | User-friendly error formatting |
| [Incremental](guide/incremental.md) | Incremental parsing for editors |

## Implementation Registry

The [registry.json](registry.json) file tracks known implementations of PTA formats.

### Registry Fields

| Field | Description |
|-------|-------------|
| `name` | Implementation name |
| `format` | Supported format(s): beancount, ledger, hledger |
| `language` | Implementation language |
| `repository` | Source code URL |
| `website` | Project website (if different) |
| `license` | SPDX license identifier |
| `status` | development, beta, stable, maintained, unmaintained |
| `features` | List of supported features |
| `conformance` | Spec conformance level |

### Adding Your Implementation

To add your implementation to the registry:

1. Fork this repository
2. Add an entry to `registry.json`
3. Submit a pull request

Entry template:

```json
{
  "name": "my-implementation",
  "format": ["beancount"],
  "language": "Rust",
  "repository": "https://github.com/user/my-implementation",
  "license": "MIT",
  "status": "development",
  "features": ["parse", "validate"],
  "conformance": {
    "spec_version": "0.1.0",
    "test_results": {
      "passed": 150,
      "failed": 14,
      "skipped": 0
    }
  }
}
```

## Conformance Testing

Use the conformance test suite to verify your implementation:

```bash
# Run the test harness against your implementation
python tests/harness/runners/python/runner.py \
  --manifest tests/beancount/v3/manifest.json \
  --format json \
  > results.json
```

See the [conformance documentation](../conformance/README.md) for details.

## Feature Matrix

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Parse | Required | Required | Required |
| Validate | Required | Optional | Optional |
| Query (BQL) | Optional | N/A | N/A |
| Query (hledger) | N/A | N/A | Optional |
| Reports | Optional | Optional | Optional |
| Plugins | Optional | N/A | N/A |

## Implementation Levels

### Level 1: Parser

Minimum viable implementation:

- Parse all valid syntax
- Report syntax errors with locations
- Produce usable AST

### Level 2: Validator

Add validation:

- Balance checking
- Account open/close validation
- Booking and lot tracking
- Interpolation

### Level 3: Query Engine

Add query capabilities:

- BQL support (Beancount)
- Filter and aggregate transactions
- Report generation

### Level 4: Full Implementation

Complete implementation:

- All Level 1-3 features
- Plugin system
- Import/export
- Editor integration (LSP)

## Language Recommendations

Recommendations by implementation language:

### Rust

- Use `logos` or `winnow` for lexing
- Use `chumsky` or `pest` for parsing
- Use `rust_decimal` for decimal arithmetic
- Use `miette` for error reporting

### Python

- Use Python's built-in decimal module
- Consider `lark` for parsing
- Use `rich` for error formatting

### TypeScript/JavaScript

- Use `decimal.js` for decimal arithmetic
- Consider tree-sitter for parsing
- Use `ohm-js` for PEG grammars

### Go

- Use `shopspring/decimal` for arithmetic
- Consider `participle` for parsing

## Getting Help

- Open a GitHub issue for questions
- Join the discussion forums
- Review existing implementations for examples
