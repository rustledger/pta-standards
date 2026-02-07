# Extension Specification Template

## Overview

Brief description of the extension.

## Motivation

Why this extension exists:
- Problem being solved
- Current limitations
- Benefits

## Syntax

### Grammar

```ebnf
extension_directive = ...
```

### Examples

```beancount
; Example usage
```

## Semantics

### Behavior

What the extension does when processed.

### Validation

What validation rules apply.

### Interaction

How it interacts with other features.

## Compatibility

### Beancount

How it works with Beancount:
- Native support
- Custom directive fallback
- Plugin implementation

### Ledger

How it works with Ledger:
- Native equivalent
- Comment fallback
- Ignored

### hledger

How it works with hledger:
- Native equivalent
- Comment fallback
- Ignored

## Implementation Notes

### Parsing

How to parse the extension.

### Processing

How to process the extension.

### Storage

How to store in AST.

## Test Cases

### Valid Examples

```beancount
; Test case 1: Basic usage
```

### Invalid Examples

```beancount
; Test case: Should fail
```

### Edge Cases

```beancount
; Test case: Edge condition
```

## Migration

### From Previous Version

How to migrate from older syntax.

### To Core

If this graduates, migration path.

## FAQ

### Common Questions

Q: Question?
A: Answer.

## Changelog

### 1.0.0

- Initial release

## References

- Related specifications
- Prior art
- Discussion links
