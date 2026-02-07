# Format Conversions

This directory specifies how to convert between plain text accounting formats.

## Conversion Pairs

| From | To | Specification |
|------|-----|---------------|
| [Beancount → Ledger](beancount-ledger/) | Ledger | Most features map directly |
| [Beancount → hledger](beancount-hledger/) | hledger | High compatibility |
| [Ledger → hledger](ledger-hledger/) | hledger | Near-identical syntax |

## Feature Matrices

- [Feature Support Matrix](matrix.md) - What features each format supports
- [Loss Matrix](loss-matrix.md) - What's lost in each conversion direction

## Interchange Format

For tool interoperability, we define a universal [interchange format](interchange/):

- [Specification](interchange/spec.md)
- [JSON Schema](interchange/journal.schema.json)
- [Protocol Buffers](interchange/journal.proto)

## Conversion Philosophy

### Lossless Where Possible

Conversions should preserve:
1. **Semantics** - Account balances must match
2. **Structure** - Transaction grouping preserved
3. **Metadata** - Tags, links, comments retained

### Graceful Degradation

When features don't map:
1. **Warn** - Emit conversion warnings
2. **Comment** - Preserve as comments when possible
3. **Document** - Reference edge cases documentation

## Bidirectional Considerations

```
Beancount ──────► Ledger ──────► Beancount
          convert        convert
```

Round-trip conversions may lose:
- Format-specific metadata syntax
- Ordering of certain elements
- Whitespace/formatting preferences

## See Also

- [Examples](../examples/) - Sample files in each format
- [Core Model](../core/model/) - Universal data model
