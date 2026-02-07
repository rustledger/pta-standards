# hledger Specification Changelog

All notable changes to the hledger format specification.

## [Unreleased]

### Added
- Initial specification draft
- Tree-sitter grammar
- Test suite framework

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

## [1.0.0] - 2024-01-15

### Added
- Core syntax specification
- Transaction format
- Posting format
- Amount specification
- Commodity handling
- Account directives
- Include mechanism
- Balance assertions
- Price annotations
- Metadata and tags
- Comment syntax
- Tree-sitter grammar
- JSON Schema for AST
- Comprehensive test suite

### Notes
- Based on hledger 1.32 behavior
- Compatible with hledger 1.x series
- Documents common patterns and best practices

---

## Version History Reference

This specification tracks the following hledger versions:

| Spec Version | hledger Version | Status |
|--------------|-----------------|--------|
| 1.0.0 | 1.32.x | Current |

## Migration Notes

### From Ledger

Key differences when migrating from Ledger:

1. **Date format**: Prefer YYYY-MM-DD
2. **Decimal mark**: May need `decimal-mark` directive
3. **Account types**: Use hledger account type syntax
4. **Virtual postings**: Check balanced vs unbalanced syntax

### From Beancount

Key differences when migrating from Beancount:

1. **Date separator**: Use `-` or `/`, not just `-`
2. **Directive syntax**: Different keyword format
3. **Booking**: hledger doesn't use booking methods
4. **Plugins**: No plugin system (yet)

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on:
- Proposing specification changes
- Documenting breaking changes
- Version numbering conventions
