# Beancount Specification Changelog

All notable changes to the Beancount format specification.

## [Unreleased]

### Added
- Complete v3 specification
- Plugin specification
- BQL query documentation

## [3.0.0] - 2024-01-15

### Added
- Beancount v3 specification
- Updated directive syntax
- New booking methods documentation
- Plugin hook specification
- Tree-sitter grammar

### Changed
- Date format strictly YYYY-MM-DD
- Updated amount parsing
- Refined balance assertion rules

### Removed
- Legacy v2 compatibility notes

## [2.0.0] - Historical

### Notes
- Based on Beancount 2.x
- Original specification baseline

---

## Version Mapping

| Spec Version | Beancount Version | Status |
|--------------|-------------------|--------|
| 3.0.0 | 3.x | Current |
| 2.0.0 | 2.x | Legacy |

## Migration Notes

### v2 to v3

Key changes when migrating from v2:

1. **No breaking syntax changes** in core format
2. **API changes** in Python library
3. **Plugin API updates**
4. **Performance improvements**

### From Ledger

1. **Add account directives** - All accounts must be opened
2. **Date format** - Use YYYY-MM-DD only
3. **Explicit amounts** - No elision
4. **Booking** - Choose booking method

### From hledger

1. **Open accounts** - Required open directives
2. **Commodity position** - After amount
3. **No virtual postings** - Use separate transactions
4. **Different metadata** - Use Beancount syntax

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines on proposing specification changes.
