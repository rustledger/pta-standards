# Stability Markers

This document defines stability markers used throughout the PTA Standards to indicate the maturity and commitment level of features.

## Purpose

Stability markers help:

- **Implementers** know which features are safe to rely on
- **Users** understand what might change
- **Maintainers** communicate intent clearly

## Feature Stability Levels

### STABLE

```
**[STABLE]** Feature description
```

**Meaning:**
- Feature is mature and well-tested
- Backwards-compatible changes only
- Breaking changes require major version bump
- Safe to use in production

**Commitment:**
- Will not be removed without deprecation period
- Behavior will remain consistent
- Any changes will be documented

**Example:**
```
**[STABLE]** Transaction syntax

2024-01-15 * "Payee" "Narration"
  Account  Amount
```

### EXPERIMENTAL

```
**[EXPERIMENTAL]** Feature description
```

**Meaning:**
- Feature is new or under active development
- May change in incompatible ways
- May be removed entirely
- Feedback welcomed

**Commitment:**
- No backwards compatibility guarantee
- May change between minor versions
- Will be promoted to STABLE or removed

**Example:**
```
**[EXPERIMENTAL]** Inline arithmetic expressions

2024-01-15 * "Split"
  Expenses:Food  (100 / 3) USD
  Assets:Cash
```

### DEPRECATED

```
**[DEPRECATED]** Feature description
```

**Meaning:**
- Feature is scheduled for removal
- Should not be used in new code
- Existing usage should be migrated
- Replacement is available

**Commitment:**
- Will be removed in future major version
- Will produce warnings during deprecation period
- Documentation will include migration path

**Example:**
```
**[DEPRECATED]** Old option name

; Old (deprecated)
option "name_assets" "Assets"

; New (use instead)
option "account_root_assets" "Assets"
```

### REMOVED

```
**[REMOVED]** Feature description
```

**Meaning:**
- Feature no longer exists
- Attempting to use will produce errors
- Documented for historical reference

**Documentation:**
- Version when removed
- What to use instead
- Migration guide reference

**Example:**
```
**[REMOVED in v3]** experiment_explicit_tolerances option

; Was:
option "experiment_explicit_tolerances" "TRUE"

; Now:
; Explicit tolerances are the default behavior.
; Remove this option from your file.
```

## Implementation Status Markers

### REQUIRED

```
**[REQUIRED]** Feature description
```

**Meaning:**
- Must be implemented for conformance
- Core functionality
- Part of minimum viable implementation

**Example:**
```
**[REQUIRED]** Transaction parsing

Implementations MUST parse transaction directives.
```

### OPTIONAL

```
**[OPTIONAL]** Feature description
```

**Meaning:**
- May be implemented
- Not required for conformance
- Enhances functionality

**Example:**
```
**[OPTIONAL]** Query language support

Implementations MAY support the BQL query language.
```

### EXTENSION

```
**[EXTENSION]** Feature description
```

**Meaning:**
- Not part of core specification
- Implementation-specific feature
- May not be portable

**Example:**
```
**[EXTENSION]** Custom directive types

Beancount supports 'custom' directives for implementation-specific needs.
```

## Conformance Level Markers

### LEVEL-1 (Parse)

```
**[LEVEL-1]** Feature
```

Basic parsing capability required.

### LEVEL-2 (Validate)

```
**[LEVEL-2]** Feature
```

Validation and balance checking required.

### LEVEL-3 (Query)

```
**[LEVEL-3]** Feature
```

Query language support required.

### LEVEL-4 (Full)

```
**[LEVEL-4]** Feature
```

Full specification compliance required.

See [Conformance Levels](../../conformance/levels/overview.md) for details.

## Format-Specific Markers

### Beancount-Only

```
**[BEANCOUNT]** Feature
```

Feature specific to Beancount format.

### Ledger-Only

```
**[LEDGER]** Feature
```

Feature specific to Ledger format.

### hledger-Only

```
**[HLEDGER]** Feature
```

Feature specific to hledger format.

### Universal

```
**[UNIVERSAL]** Feature
```

Feature supported across all major formats.

## Usage Guidelines

### In Specification Documents

Place markers at the beginning of feature descriptions:

```markdown
## Transaction Directive

**[STABLE]** **[REQUIRED]** **[UNIVERSAL]**

A transaction records a financial event...
```

### In API Documentation

Mark stability of functions and types:

```python
class Transaction:
    """
    [STABLE] A financial transaction.

    Attributes:
        date: [STABLE] Transaction date
        flag: [STABLE] Status flag
        postings: [STABLE] List of postings
        metadata: [EXPERIMENTAL] Key-value metadata
    """
```

### In Changelogs

Reference stability when announcing changes:

```markdown
## v2.0.0

### Breaking Changes

- **[REMOVED]** `experiment_explicit_tolerances` option

### Deprecations

- **[DEPRECATED]** `name_assets` option, use `account_root_assets`

### New Features

- **[EXPERIMENTAL]** Inline arithmetic expressions
```

## Stability Transitions

### Promotion Path

```
EXPERIMENTAL → STABLE
```

Criteria for promotion:
- Feature has been tested in production
- No significant issues reported
- API/syntax is finalized
- Documentation is complete

### Deprecation Path

```
STABLE → DEPRECATED → REMOVED
```

Timeline:
- Deprecation announced in minor version
- Warning messages in deprecated version
- Removal in next major version
- Minimum deprecation period: 1 major version cycle

### Experimental to Removed

```
EXPERIMENTAL → REMOVED
```

Experimental features may be removed without deprecation period.

## Version Compatibility

### Stable Features

| From Version | To Version | Compatibility |
|--------------|------------|---------------|
| 1.x | 1.y (y > x) | Full |
| 1.x | 2.0 | Check deprecations |
| 1.x | 3.0 | Migration required |

### Experimental Features

| From Version | To Version | Compatibility |
|--------------|------------|---------------|
| 1.x | 1.y | Not guaranteed |
| 1.x | 2.0 | Not guaranteed |

## Documentation Requirements

### For STABLE Features

- Complete specification
- Multiple examples
- Edge case documentation
- Error messages defined

### For EXPERIMENTAL Features

- Basic specification
- Usage examples
- Known limitations
- Feedback channels

### For DEPRECATED Features

- Deprecation notice
- Replacement documentation
- Migration guide
- Removal timeline

### For REMOVED Features

- Historical reference
- Replacement pointer
- Migration guide link
- Removal version

## Examples in Practice

### Mixed Stability Document

```markdown
# Balance Directive

## Syntax

**[STABLE]** **[REQUIRED]**

```beancount
DATE balance ACCOUNT AMOUNT
```

## Tolerance Specification

**[STABLE]** **[OPTIONAL]**

```beancount
DATE balance ACCOUNT AMOUNT ~ TOLERANCE
```

## Partial Balance Assertion

**[EXPERIMENTAL]**

```beancount
DATE balance ACCOUNT ~AMOUNT
```

Asserts that balance is approximately AMOUNT.
```
