# Import Specifications

This directory defines specifications for importing external financial data formats into plain text accounting systems.

## Supported Formats

| Format | Description | Specification |
|--------|-------------|---------------|
| [CSV](csv/) | Comma-separated values (bank exports) | Flexible rule-based |
| [OFX](ofx/) | Open Financial Exchange | Structured mapping |
| [QIF](qif/) | Quicken Interchange Format | Legacy format |

## Import Process

```
External File → Parse → Transform → Generate → PTA Transactions
```

### Stages

1. **Parse**: Read external format into intermediate representation
2. **Transform**: Apply rules to extract transaction data
3. **Generate**: Create PTA-format transactions
4. **Validate**: Verify generated transactions

## Common Challenges

| Challenge | Solution |
|-----------|----------|
| Date formats | Configurable date parsing |
| Amount signs | Credit/debit column detection |
| Payee extraction | Pattern matching rules |
| Account mapping | Configurable account rules |
| Duplicate detection | Hash-based deduplication |

## Design Principles

1. **Declarative**: Rules describe what, not how
2. **Composable**: Small rules combine into complex mappings
3. **Reversible**: Can regenerate from same input
4. **Auditable**: Clear provenance tracking

## See Also

- [CSV Import](csv/spec.md) - Most common import format
- [OFX Import](ofx/spec.md) - Bank download format
- [QIF Import](qif/spec.md) - Legacy Quicken format
