# Conformance Program

This directory defines the conformance certification program for plain text accounting implementations.

## Overview

The conformance program provides a standardized way to assess and communicate implementation compatibility. Implementations can achieve different conformance levels based on their feature support.

## Conformance Levels

| Level | Name | Description |
|-------|------|-------------|
| 1 | Parse | Correctly parse valid syntax |
| 2 | Validate | Parse + semantic validation |
| 3 | Query | Parse + validate + query execution |
| 4 | Full | Complete feature support |

See [levels/overview.md](levels/overview.md) for detailed requirements.

## Directory Structure

```
conformance/
├── README.md           # This file
├── registry.json       # Certified implementations
├── levels/
│   ├── overview.md     # Level comparison
│   ├── level-1-parse.md
│   ├── level-2-validate.md
│   ├── level-3-query.md
│   └── level-4-full.md
├── process/
│   ├── self-certification.md
│   ├── test-requirements.md
│   └── badge-usage.md
└── benchmarks/
    ├── spec.md
    └── methodology.md
```

## Certification Process

1. **Self-Assessment**: Run conformance test suite
2. **Documentation**: Record test results and any known limitations
3. **Registration**: Submit to registry via pull request
4. **Maintenance**: Re-certify with new spec versions

## Test Suite

The conformance test suite is located in `/tests/`. Each level has specific test requirements:

| Level | Test Suites Required |
|-------|---------------------|
| 1 | syntax/valid, syntax/invalid |
| 2 | Level 1 + validation |
| 3 | Level 2 + bql |
| 4 | Level 3 + booking + all features |

## Badges

Implementations may display conformance badges:

```markdown
![Beancount v3 Level 2](https://pta-spec.org/badges/beancount-v3-level2.svg)
```

## Registry

The `registry.json` file tracks certified implementations:

```json
{
  "implementations": [
    {
      "name": "beancount",
      "version": "3.0.0",
      "format": "beancount",
      "format_version": "v3",
      "level": 4,
      "certified_date": "2024-01-15",
      "test_results_url": "https://..."
    }
  ]
}
```

## Benefits

- **Users**: Know what features to expect
- **Implementers**: Clear specification targets
- **Ecosystem**: Interoperability confidence
- **Quality**: Standardized testing

## See Also

- [Test Suite](/tests/) - Conformance tests
- [Test Harness](/tests/harness/) - Test runner
