# hledger Format Specification

This directory contains the formal specification for the hledger journal format.

## Overview

hledger is a robust, cross-platform plain text accounting tool written in Haskell. It is largely compatible with Ledger's journal format while adding its own features and stricter parsing.

## History

hledger was created by Simon Michael in 2007 as a Haskell implementation of Ledger. It aims for:
- Cross-platform compatibility
- Robust error handling
- Clear documentation
- Active development and maintenance

## Key Features

- **Ledger compatibility**: Most Ledger files work with hledger
- **Strict parsing**: Catches more errors at parse time
- **Multiple interfaces**: CLI, web, TUI, API
- **Good error messages**: Clear, actionable diagnostics
- **Multi-currency**: First-class currency handling
- **CSV import**: Built-in CSV conversion rules

## Versions

| Version | Status | Description |
|---------|--------|-------------|
| [v1](v1/) | Current | Current hledger format |

## Directory Structure

```
hledger/
├── README.md           # This file
├── compliance.md       # Compliance testing guide
├── CHANGELOG.md        # Version history
└── v1/
    ├── README.md       # Version overview
    ├── spec/           # Detailed specifications
    └── tree-sitter/    # Grammar definitions
```

## Quick Start

### Basic Transaction

```hledger
2024-01-15 Grocery Store
    expenses:food    $50.00
    assets:checking
```

### Account Declaration

```hledger
account assets:checking
    ; type: Asset
```

### Commodity Declaration

```hledger
commodity $1,000.00
```

## Differences from Ledger

### Stricter Parsing

- Requires consistent date formats
- More rigorous balance checking
- Clearer virtual posting rules

### Added Features

- `decimal-mark` directive
- Account type declarations
- Built-in CSV rules

### Different Defaults

- Default to strict account checking
- Different report output formatting

## Related Resources

- [hledger Official Site](https://hledger.org/)
- [hledger Manual](https://hledger.org/hledger.html)
- [hledger-web](https://hledger.org/hledger-web.html)

## See Also

- [Ledger Format](../ledger/)
- [Beancount Format](../beancount/)
- [Format Comparison](../README.md)
