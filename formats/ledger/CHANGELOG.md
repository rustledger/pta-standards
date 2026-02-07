# Ledger Specification Changelog

All notable changes to the Ledger format specification.

## [Unreleased]

### Added
- Complete v1 specification
- Tree-sitter grammar
- Expression specification

## [1.0.0] - 2024-01-15

### Added
- Core syntax specification
- Transaction format
- Posting format
- Amount and commodity handling
- Virtual postings
- Automated transactions
- Periodic transactions
- Value expressions
- Balance assertions
- Directive specifications
- Error codes
- Tree-sitter grammar
- JSON Schema for AST

### Notes
- Based on Ledger 3.x behavior
- Documents common patterns

---

## Version Mapping

| Spec Version | Ledger Version | Status |
|--------------|----------------|--------|
| 1.0.0 | 3.x | Current |

## Migration Notes

### From hledger

- More flexible date formats
- Expression language differences
- Different defaults

### From Beancount

- No required account opening
- Amount elision allowed
- Virtual posting support
- Expression language

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.
