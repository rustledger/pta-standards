# PTA Extensions Registry

This directory contains specifications for PTA format extensions.

## Overview

Extensions allow expanding PTA formats with:
- Custom directives
- Additional metadata
- New validation rules
- Specialized features

## Extension Process

### Proposal

1. Create proposal document
2. Discuss in community
3. Iterate on design
4. Reach consensus

### Implementation

1. Reference implementation
2. Documentation
3. Test suite
4. Compatibility analysis

### Graduation

1. Community adoption
2. Multiple implementations
3. Stable specification
4. Format integration

## Directory Structure

```
extensions/
├── README.md           # This file
├── process/
│   ├── proposal.md     # Proposal template
│   └── graduation.md   # Graduation criteria
└── catalog/
    └── template/       # Extension template
        ├── README.md
        └── spec.md
```

## Extension Categories

### Directive Extensions

New directive types:

```beancount
2024-01-15 custom "budget" "food" 500.00 USD
```

### Metadata Extensions

Standardized metadata keys:

```beancount
    receipt: "file.pdf"
    project: "alpha"
```

### Validation Extensions

Additional validation rules:

```beancount
; Require approval for amounts > $1000
```

### Query Extensions

Extended query capabilities:

```sql
SELECT account, SUM(amount) WHERE tag = 'project'
```

## Compatibility

Extensions SHOULD:
- Not break core syntax
- Degrade gracefully
- Document compatibility
- Provide fallbacks

## Catalog

### Active Extensions

None yet - contribute the first!

### Proposed Extensions

Submit proposals via the process outlined in `process/proposal.md`.

## Contributing

1. Read the proposal process
2. Create extension proposal
3. Implement reference version
4. Submit for review

## See Also

- [Proposal Process](process/proposal.md)
- [Graduation Criteria](process/graduation.md)
- [Extension Template](catalog/template/)
