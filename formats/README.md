# Format Specifications

Individual specifications for each PTA format.

## Formats

| Format | Versions | Description |
|--------|----------|-------------|
| [beancount/](beancount/) | v2, v3 | Double-entry with cost tracking |
| [ledger/](ledger/) | v1 | Original PTA format |
| [hledger/](hledger/) | v1 | Haskell implementation |

## Structure

Each format follows a consistent structure:

```
format/
├── README.md           # Overview and history
├── CHANGELOG.md        # Version history
├── vN/
│   ├── spec/           # Normative specification
│   │   ├── directives/ # One file per directive
│   │   └── ...
│   ├── grammar/        # EBNF and ABNF grammars
│   ├── schema/         # JSON Schema and Protobuf
│   ├── tree-sitter/    # Editor grammar
│   ├── formal/         # Alloy models
│   └── migration/      # Upgrade guides
└── compliance.md       # Conformance requirements
```
