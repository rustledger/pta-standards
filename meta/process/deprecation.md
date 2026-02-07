# Deprecation Policy

This document describes how features are deprecated and eventually removed from the PTA Standards.

## Deprecation Principles

1. **No surprise removals** - Features are always deprecated before removal
2. **Clear timelines** - Deprecation includes expected removal date
3. **Migration paths** - Alternatives are documented
4. **Implementation time** - Sufficient time for implementations to adapt

## Deprecation Process

### Stage 1: Proposal

1. Create an RFC proposing deprecation
2. Document the reason for deprecation
3. Provide migration guidance
4. Specify proposed timeline

### Stage 2: Announcement

Once approved:

1. Mark feature as deprecated in specification
2. Add deprecation notice with version number
3. Update conformance tests to warn on deprecated features
4. Announce deprecation in release notes

### Stage 3: Deprecation Period

During the deprecation period:

1. Feature remains fully functional
2. Implementations SHOULD warn users
3. Documentation emphasizes alternatives
4. New tutorials avoid deprecated features

### Stage 4: Removal

After deprecation period:

1. Create RFC for removal (if major change)
2. Remove feature in next major version
3. Update tests to reject deprecated syntax
4. Archive documentation

## Timeline Guidelines

| Feature Type | Minimum Deprecation Period |
|--------------|---------------------------|
| Syntax elements | 2 major versions or 24 months |
| Options/settings | 1 major version or 12 months |
| Query functions | 1 major version or 12 months |
| Plugin APIs | 2 major versions or 24 months |
| Error codes | 1 major version or 12 months |

## Documentation Format

Deprecated features are marked in the specification as:

```markdown
### Feature Name

> **Deprecated since v1.2.0**: This feature is deprecated and will be
> removed in v2.0.0. Use [alternative] instead. See [migration guide].
```

## Deprecation Notices

### In Specifications

```markdown
::: warning Deprecated
This feature is deprecated as of v1.2.0. Use `new_feature` instead.
Removal planned for v2.0.0.
:::
```

### In JSON Schemas

```json
{
  "old_field": {
    "type": "string",
    "deprecated": true,
    "description": "Deprecated: Use new_field instead"
  }
}
```

### In Grammar Files

```ebnf
(* DEPRECATED: Use new_directive instead *)
old_directive = "old" , identifier ;
```

## Migration Guides

Each deprecation requires a migration guide covering:

1. **What is deprecated** - Clear identification
2. **Why it's deprecated** - Rationale
3. **What to use instead** - Alternative
4. **How to migrate** - Step-by-step instructions
5. **Automated tools** - If available

Example migration guide structure:

```markdown
# Migrating from X to Y

## Overview
Feature X is deprecated in v1.2.0 and will be removed in v2.0.0.

## Why This Change?
[Explanation of rationale]

## Migration Steps

### Step 1: Identify Usage
[How to find uses of deprecated feature]

### Step 2: Update Syntax
[Before/after examples]

### Step 3: Verify
[How to verify migration succeeded]

## Automated Migration
[Script or tool to automate migration]
```

## Exceptions

The following may be removed without deprecation:

1. **Security vulnerabilities** - Immediate removal if required
2. **Spec bugs** - Corrections to match documented intent
3. **Pre-1.0 features** - During initial development
4. **Experimental features** - Clearly marked as experimental

## Tracking Deprecations

Active deprecations are tracked in:

1. `CHANGELOG.md` - Listed under "Deprecated"
2. `docs/deprecations.md` - Comprehensive list
3. GitHub issues - Labeled `deprecation`

## Related Documents

- [Breaking Changes](breaking-changes.md) - Breaking change policy
- [Versioning](versioning.md) - Version numbering
- [RFC Process](../rfcs/README.md) - How to propose deprecations
