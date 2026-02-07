# Beancount Sources of Truth

This document lists all authoritative sources for validating the Beancount specification.

## Primary Sources (Highest Authority)

### 1. Source Code
The ultimate source of truth for behavior is the actual Python implementation.

| Repository | URL | Description |
|------------|-----|-------------|
| **beancount** | https://github.com/beancount/beancount | Main Beancount source code (v3 branch is current) |
| **beanquery** | https://github.com/beancount/beanquery | BQL query engine (separate package since v3) |

**Key files to check:**
- `beancount/parser/grammar.py` - Parser grammar
- `beancount/parser/lexer.py` - Lexer rules
- `beancount/core/data.py` - Data types (directives, postings, etc.)
- `beancount/ops/validation.py` - Validation logic
- `beancount/parser/options.py` - Valid options list
- `beanquery/query_parser.py` - BQL grammar

### 2. Official Documentation
Documentation authored by Martin Blais.

| Source | URL | Description |
|--------|-----|-------------|
| **Google Docs (Canonical)** | http://furius.ca/beancount/doc/index | Original source documents |
| **GitHub Docs** | https://github.com/beancount/docs | Auto-generated markdown from Google Docs |
| **Published Docs** | https://beancount.github.io/docs/ | Rendered documentation site |

**Key documents:**
- [Beancount Language Syntax](https://beancount.github.io/docs/beancount_language_syntax.html)
- [Beancount Query Language](https://beancount.github.io/docs/beancount_query_language.html)
- [Beancount Design Doc](https://beancount.github.io/docs/beancount_design_doc.html)
- [Beancount V3: Goals & Design](https://beancount.github.io/docs/beancount_v3.html)
- [Installing Beancount](https://beancount.github.io/docs/installing_beancount.html)

## Secondary Sources

### 3. GitHub Issues & Pull Requests
Discussions about bugs, features, and clarifications.

| Repository | Issues URL |
|------------|------------|
| beancount/beancount | https://github.com/beancount/beancount/issues |
| beancount/beanquery | https://github.com/beancount/beanquery/issues |
| beancount/docs | https://github.com/beancount/docs/issues |

**How to use:**
- Search for specific features or behaviors
- Check closed issues for historical decisions
- Look at PRs for implementation details

### 4. Mailing List
Community discussions and official responses from Martin Blais.

| Source | URL |
|--------|-----|
| **Beancount Google Group** | https://groups.google.com/g/beancount |
| **Mail Archive** | https://www.mail-archive.com/beancount@googlegroups.com/ |

**How to use:**
- Search for specific topics or edge cases
- Martin Blais often provides authoritative clarifications
- Historical discussions explain design decisions

### 5. Test Files
Test cases in the repository serve as executable specifications.

| Location | Description |
|----------|-------------|
| `beancount/parser/*_test.py` | Parser tests |
| `beancount/ops/*_test.py` | Validation tests |
| `beanquery/*_test.py` | Query engine tests |
| `examples/` | Example ledger files |

## Tertiary Sources (Reference Only)

### 6. Community Resources
Not authoritative, but useful for understanding usage patterns.

| Source | URL | Description |
|--------|-----|-------------|
| **Awesome Beancount** | https://awesome-beancount.com/ | Curated list of resources |
| **Beancount.io** | https://beancount.io/ | Community guide and tutorials |
| **Reddit r/plaintextaccounting** | https://reddit.com/r/plaintextaccounting | Community discussions |

## Validation Priority

When validating spec claims, check sources in this order:

1. **Test the actual Python implementation** - Run code against beancount 3.x
2. **Check source code** - Read the parser/validator implementation
3. **Read official docs** - beancount.github.io or Google Docs
4. **Search GitHub issues** - For edge cases and discussions
5. **Search mailing list** - For historical context and clarifications

## Version Information

| Component | Current Version | Notes |
|-----------|-----------------|-------|
| beancount | 3.x | v3 branch is current stable |
| beanquery | 0.2.x | Separate package since v3 |
| Python | 3.12+ | Required for v3 |

## Known Discrepancies

When the spec and implementation differ, **the implementation is authoritative** unless there's an open bug report indicating the implementation is wrong.

Document any discrepancies found during validation in the spec files themselves.

## Validation Methodology

For each spec file:

1. **Identify claims** - List specific behaviors/syntax described
2. **Write test cases** - Create Python scripts to verify claims
3. **Check source code** - Read relevant implementation files
4. **Search issues/docs** - Look for discussions about edge cases
5. **Update spec** - Fix any incorrect claims, add notes for ambiguities

## Related Files

- [CHANGELOG.md](CHANGELOG.md) - Record of spec changes
- [compliance.md](compliance.md) - Implementation compliance notes
