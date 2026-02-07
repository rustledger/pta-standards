# PTA Tooling Specifications

This directory contains specifications for tooling that works with Plain Text Accounting formats.

## Overview

Tooling specifications define:
- Standard tool interfaces
- Output formats
- Interoperability requirements
- Editor integrations

## Categories

### Canonical Output

Standardized output formats for consistent cross-tool behavior.

```
canonical/
├── spec.md        # Canonical format specification
├── ledger.md      # Ledger canonical output
├── hledger.md     # hledger canonical output
└── beancount.md   # Beancount canonical output
```

### Linting

Code quality and style checking rules.

```
linting/
├── spec.md              # Linting framework
└── rules/
    ├── style.md         # Style rules
    ├── correctness.md   # Correctness rules
    └── consistency.md   # Consistency rules
```

### Diff Tools

Semantic differencing for journals.

```
diff/
├── spec.md       # Diff algorithm specification
└── semantic.md   # Semantic diff rules
```

### MCP Integration

Model Context Protocol integration for AI assistants.

```
mcp/
└── spec.md       # MCP server specification
```

### WASM

WebAssembly compilation targets.

```
wasm/
└── spec.md       # WASM interface specification
```

## Tool Categories

### Parsers

- Syntax parsing
- AST generation
- Error recovery

### Validators

- Balance checking
- Account validation
- Constraint verification

### Formatters

- Code formatting
- Canonical output
- Pretty printing

### Converters

- Format conversion
- Import/export
- Migration tools

### Analyzers

- Balance reports
- Register views
- Budget analysis

### Editors

- Syntax highlighting
- Code completion
- Error diagnostics

## Cross-Format Considerations

### Common Interface

All tools SHOULD support:

```bash
tool check FILE          # Validate
tool format FILE         # Format
tool convert FILE -o FMT # Convert
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Parse error |
| 2 | Validation error |
| 3 | File not found |

### Output Formats

- Human-readable (default)
- JSON (`--format json`)
- TAP (`--format tap`)

## Integration Points

### Editor Integration

- Language Server Protocol (LSP)
- Tree-sitter grammars
- Syntax highlighting queries

### CI/CD Integration

- Pre-commit hooks
- GitHub Actions
- Validation pipelines

### AI Integration

- MCP servers
- Structured output
- Natural language queries

## See Also

- [Core Specifications](../core/)
- [Format Specifications](../formats/)
- [Test Harness](../tests/harness/)
