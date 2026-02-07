# Conformance Levels Overview

This document provides an overview of the conformance levels for plain text accounting implementations.

## Level Summary

| Level | Name | Core Capability | Use Case |
|-------|------|-----------------|----------|
| 1 | Parse | Syntax recognition | Syntax highlighting, linting |
| 2 | Validate | Semantic checks | Full editors, importers |
| 3 | Query | BQL execution | Reporting tools |
| 4 | Full | All features | Complete implementations |

## Level Requirements

### Level 1: Parse

**Capability**: Correctly parse valid Beancount syntax and reject invalid syntax.

| Requirement | Description |
|-------------|-------------|
| Lexical analysis | Tokenize all valid inputs |
| Syntax parsing | Build correct AST |
| Error detection | Identify syntax errors with location |
| Error recovery | Continue parsing after errors |

**Test suites**: `syntax/valid`, `syntax/invalid`

### Level 2: Validate

**Capability**: Level 1 + semantic validation.

| Requirement | Description |
|-------------|-------------|
| Account lifecycle | Verify open/close |
| Balance checking | Validate transaction balance |
| Currency constraints | Check account currencies |
| Duplicate detection | Find duplicate entries |

**Test suites**: Level 1 + `validation`

### Level 3: Query

**Capability**: Level 2 + query language execution.

| Requirement | Description |
|-------------|-------------|
| BQL parsing | Parse query syntax |
| Query execution | Execute SELECT queries |
| Aggregations | GROUP BY, SUM, COUNT, etc. |
| Filtering | WHERE clause support |

**Test suites**: Level 2 + `bql`

### Level 4: Full

**Capability**: Level 3 + all Beancount features.

| Requirement | Description |
|-------------|-------------|
| All booking methods | FIFO, LIFO, AVERAGE, etc. |
| Plugins | Plugin loading and execution |
| All directives | Complete directive support |
| Price database | Full price tracking |

**Test suites**: Level 3 + `booking` + all remaining suites

## Feature Matrix

| Feature | L1 | L2 | L3 | L4 |
|---------|----|----|----|----|
| Parse transactions | ✓ | ✓ | ✓ | ✓ |
| Parse all directives | ✓ | ✓ | ✓ | ✓ |
| Syntax error reporting | ✓ | ✓ | ✓ | ✓ |
| Account validation | | ✓ | ✓ | ✓ |
| Balance validation | | ✓ | ✓ | ✓ |
| Currency constraints | | ✓ | ✓ | ✓ |
| Basic queries | | | ✓ | ✓ |
| Aggregate queries | | | ✓ | ✓ |
| FIFO booking | | | | ✓ |
| LIFO booking | | | | ✓ |
| AVERAGE booking | | | | ✓ |
| Plugin support | | | | ✓ |
| Pad expansion | | | | ✓ |

## Choosing a Level

### Level 1: Parse

Best for:
- Syntax highlighters
- Code formatters
- Linters
- Editor integrations (basic)

Examples: tree-sitter grammars, VSCode extensions

### Level 2: Validate

Best for:
- Import tools
- Editor integrations (advanced)
- Conversion utilities
- Pre-commit hooks

Examples: beancount-import, format converters

### Level 3: Query

Best for:
- Reporting tools
- Data exporters
- Analysis tools
- Dashboards

Examples: fava, custom report generators

### Level 4: Full

Best for:
- Complete Beancount implementations
- Alternative runtimes
- Full-featured applications

Examples: beancount, rustledger

## Certification Requirements

### Minimum Test Pass Rate

| Level | Required Pass Rate |
|-------|-------------------|
| 1 | 100% of syntax tests |
| 2 | 100% of Level 1 + 95% of validation |
| 3 | 100% of Level 2 + 95% of BQL |
| 4 | 95% of all tests |

### Documentation Requirements

All levels must document:
1. Known limitations
2. Implementation-specific behavior
3. Extension features (if any)

## Partial Conformance

Implementations MAY claim partial conformance:

```
"Level 2 conformant, partial Level 3 (basic queries only)"
```

Partial conformance MUST specify:
- Passing test suites
- Known failing tests
- Unsupported features

## Version Compatibility

Conformance is version-specific:
- Implementations certify against specific format versions
- New format versions may require re-certification
- Implementations may support multiple versions

## Upgrading Levels

To upgrade from Level N to Level N+1:

1. Run additional test suites
2. Fix any failures
3. Update documentation
4. Submit updated certification

## See Also

- [Level 1 Details](level-1-parse.md)
- [Level 2 Details](level-2-validate.md)
- [Level 3 Details](level-3-query.md)
- [Level 4 Details](level-4-full.md)
