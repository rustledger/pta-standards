# PTA Standards

[![Conformance Tests](https://github.com/pta-standards/pta-standards/actions/workflows/run-tests.yml/badge.svg)](https://github.com/pta-standards/pta-standards/actions/workflows/run-tests.yml)

**Plain Text Accounting Standards**: Specifications for Beancount, Ledger, and hledger formats.

> [!NOTE]
> This project is in early development. Contributions welcome!

## Overview

This repository contains formal specifications for plain text accounting formats:

| Format | Version | Status |
|--------|---------|--------|
| [Beancount](formats/beancount/) | v3 | Draft |
| [Ledger](formats/ledger/) | v1 | Planned |
| [hledger](formats/hledger/) | v1 | Planned |

## Structure

```
pta-standards/
├── core/           # Shared foundations (data model, types, numerics)
├── formats/        # Individual format specifications
│   ├── beancount/  # Beancount v2, v3
│   ├── ledger/     # Ledger v1
│   └── hledger/    # hledger v1
├── tests/          # Conformance test suites
├── tooling/        # CLI, LSP, error code specifications
└── meta/           # RFCs, ADRs, governance
```

## Goals

1. **Precise**: Unambiguous specifications that can be implemented correctly
2. **Testable**: Comprehensive test suites for conformance verification
3. **Interoperable**: Enable format conversion and tool compatibility
4. **Community-driven**: Open process for evolution and extension

## Specifications Include

- **Grammars**: EBNF and ABNF formal grammars
- **Schemas**: JSON Schema and Protocol Buffers for AST
- **Tree-sitter**: Editor integration grammars
- **Formal models**: Alloy specifications for invariants
- **Test vectors**: Conformance test suites

## License

- **Documentation** (*.md, specs): [CC-BY-4.0](LICENSE-DOCS)
- **Code** (grammars, schemas, tests): [MIT](LICENSE-CODE)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

<!-- CONFORMANCE-RESULTS-START -->
## Conformance Test Results

*Results updated nightly. See [conformance documentation](formats/beancount/v3/conformance/) for details.*
<!-- CONFORMANCE-RESULTS-END -->

## Related Projects

- [rustledger](https://github.com/rustledger/rustledger) - Rust implementation of Beancount
- [beancount](https://github.com/beancount/beancount) - Original Python implementation
- [ledger](https://github.com/ledger/ledger) - C++ implementation
- [hledger](https://github.com/simonmichael/hledger) - Haskell implementation
