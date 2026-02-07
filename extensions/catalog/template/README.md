# Extension Template

This directory provides a template for new PTA extensions.

## Quick Start

1. Copy this directory
2. Rename to your extension name
3. Fill in the template files
4. Implement your extension

## Directory Structure

```
your-extension/
├── README.md      # Extension overview (this template)
├── spec.md        # Detailed specification
├── examples/      # Usage examples
│   ├── basic.beancount
│   └── advanced.beancount
├── tests/         # Test cases
│   ├── valid/
│   └── invalid/
└── impl/          # Reference implementation
    └── ...
```

## README Template

Fill in the sections below:

---

# Extension Name

Brief description of what this extension does.

## Status

- [ ] Experimental
- [ ] Stable
- [ ] Recommended

## Installation

How to install/enable the extension.

## Usage

Basic usage examples.

## Documentation

Link to full specification.

## Compatibility

| Format | Support |
|--------|---------|
| Beancount | ✓ |
| Ledger | ✓ |
| hledger | ✓ |

## Contributing

How to contribute to this extension.

## License

License information.

## See Also

- [Specification](spec.md)
- [Examples](examples/)
