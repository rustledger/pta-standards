# Breaking Changes Policy

This document describes how breaking changes are handled in the PTA Standards.

## Definition

A **breaking change** is any modification that could cause:

1. Previously valid input to become invalid
2. Previously invalid input to become valid (in some contexts)
3. Valid input to produce different results
4. Changed error messages or codes that tools rely on

## Categories of Breaking Changes

### Syntax Breaking Changes

| Change Type | Example | Severity |
|-------------|---------|----------|
| Removed syntax | Removing `@` for tags | High |
| Changed syntax | `include` → `import` | High |
| New reserved words | `async` becomes keyword | Medium |
| Stricter validation | Requiring balanced transactions | Medium |

### Semantic Breaking Changes

| Change Type | Example | Severity |
|-------------|---------|----------|
| Changed computation | Different rounding rules | High |
| Changed defaults | Default booking method | High |
| New requirements | Mandatory metadata | Medium |
| Changed errors | Different error for same input | Low |

### Behavioral Breaking Changes

| Change Type | Example | Severity |
|-------------|---------|----------|
| Changed output format | Query result structure | Medium |
| Changed file handling | Include path resolution | Medium |
| Changed ordering | Transaction sort order | Low |

## Process for Breaking Changes

### 1. Proposal

All breaking changes require an RFC that includes:

- Clear description of the change
- Rationale and benefits
- Impact assessment
- Migration path
- Timeline

### 2. Review Period

- Minimum 4-week review period
- Community feedback solicited
- Implementation impact assessed

### 3. Deprecation (if applicable)

If replacing existing functionality:

- Follow [deprecation policy](deprecation.md)
- Minimum 12-month warning period
- Both old and new supported during transition

### 4. Implementation

Breaking changes are:

- Only included in major version releases
- Clearly documented in release notes
- Accompanied by migration tools when possible

## Impact Assessment Template

```markdown
## Breaking Change: [Name]

### Description
[What is changing]

### Affected Users
- [ ] All users
- [ ] Users of feature X
- [ ] Users with specific configuration
- [ ] Estimated percentage: X%

### Affected Implementations
- [ ] Parsers
- [ ] Validators
- [ ] Query engines
- [ ] Importers/Exporters
- [ ] Plugins

### Migration Effort
- [ ] Trivial (find-and-replace)
- [ ] Moderate (manual review required)
- [ ] Significant (logic changes required)
- [ ] Extensive (architectural changes)

### Automated Migration
- [ ] Fully automatable
- [ ] Partially automatable
- [ ] Manual only

### Rollback Risk
- [ ] Low (easily reversible)
- [ ] Medium (some data loss possible)
- [ ] High (difficult to reverse)
```

## Minimizing Breaking Changes

We aim to minimize breaking changes through:

### 1. Careful Initial Design

- Extensive review before features are released
- Consider future extensibility
- Learn from other formats' mistakes

### 2. Extensibility Mechanisms

- Optional features via pragmas/options
- Namespaced extensions
- Reserved syntax for future use

### 3. Compatibility Modes

When breaking changes are necessary:

- Provide compatibility flags
- Support version detection
- Allow gradual migration

## Breaking Change Examples

### Allowed Without Major Version

These are NOT breaking changes:

```markdown
- Adding new optional directive types
- Adding new optional metadata fields
- Relaxing validation (accepting more input)
- Adding new query functions
- Clarifying previously undefined behavior
- Fixing spec bugs to match implementation
```

### Require Major Version

These ARE breaking changes:

```markdown
- Removing directive types
- Changing directive syntax
- Making optional fields required
- Changing computation results
- Removing query functions
- Changing default behaviors
```

## Communication

Breaking changes are communicated through:

1. **RFC** - Initial proposal and discussion
2. **Changelog** - Listed in "Breaking Changes" section
3. **Release Notes** - Prominent placement
4. **Migration Guide** - Step-by-step instructions
5. **Blog Post** - For significant changes

## Exceptions

Breaking changes may bypass the normal process for:

1. **Security fixes** - Immediate action required
2. **Spec bugs** - Aligning with documented intent
3. **Legal requirements** - Compliance needs

These exceptions still require:

- Documentation
- Announcement
- Migration assistance

## Related Documents

- [Deprecation](deprecation.md) - Deprecation policy
- [Versioning](versioning.md) - Version numbering
- [RFC Process](../rfcs/README.md) - How to propose changes
