# Versioning Policy

This document describes how PTA Standards versions are numbered and managed.

## Version Format

We use [Semantic Versioning 2.0.0](https://semver.org/) with the format:

```
MAJOR.MINOR.PATCH
```

### Version Components

| Component | When Incremented | Example |
|-----------|-----------------|---------|
| **MAJOR** | Breaking changes to the specification | 1.0.0 → 2.0.0 |
| **MINOR** | New features, backwards-compatible additions | 1.0.0 → 1.1.0 |
| **PATCH** | Clarifications, typo fixes, non-normative changes | 1.0.0 → 1.0.1 |

## What Constitutes a Breaking Change?

A change is considered **breaking** if it:

1. **Changes required syntax** - Input that was valid becomes invalid
2. **Changes semantics** - Valid input produces different results
3. **Removes features** - Previously supported constructs are removed
4. **Changes error behavior** - Errors become success or vice versa

A change is **NOT breaking** if it:

1. **Adds new optional syntax** - New constructs that don't affect existing files
2. **Clarifies ambiguity** - Makes explicit what was previously undefined
3. **Fixes spec bugs** - Aligns spec with documented intent
4. **Adds examples** - Additional examples or test cases

## Pre-1.0 Versioning

During pre-1.0 development (0.x.y):

- MINOR version changes may include breaking changes
- PATCH version changes should remain backwards-compatible
- Each format specification may have its own version

## Version Pinning

Implementations SHOULD:

1. Declare which spec version they target
2. Document any deviations from the spec
3. Support version detection via file headers or options

Example version declaration:

```beancount
; Conforms to: PTA Beancount Spec v1.2.0
option "pta_spec_version" "1.2.0"
```

## Version Lifecycle

```
                   ┌─────────────────────────────────────┐
                   │                                     │
    ┌──────────┐   │   ┌──────────┐      ┌──────────┐   │   ┌──────────┐
    │  Draft   │───┼──▶│  Active  │─────▶│Deprecated│───┼──▶│ Retired  │
    └──────────┘   │   └──────────┘      └──────────┘   │   └──────────┘
                   │                                     │
                   └─────────────────────────────────────┘
                            Supported Versions
```

### Lifecycle Stages

| Stage | Description | Support Level |
|-------|-------------|---------------|
| **Draft** | Under development, may change | None |
| **Active** | Current recommended version | Full |
| **Deprecated** | Superseded, will be retired | Security only |
| **Retired** | No longer supported | None |

## Support Policy

- **Active versions**: Receive all updates and clarifications
- **Deprecated versions**: Receive only security-related fixes
- **Minimum support period**: 12 months after deprecation before retirement

## Version History

| Version | Status | Release Date | Notes |
|---------|--------|--------------|-------|
| 0.1.0 | Draft | TBD | Initial release |

## Related Documents

- [Releases](releases.md) - Release process
- [Breaking Changes](breaking-changes.md) - Breaking change policy
- [Deprecation](deprecation.md) - Deprecation process
