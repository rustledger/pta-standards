# Extension Proposal Process

This document describes how to propose new PTA extensions.

## Overview

Extensions go through a structured process:
1. Proposal
2. Discussion
3. Implementation
4. Adoption
5. Graduation

## Proposal Template

### Title

Clear, descriptive name for the extension.

### Summary

One paragraph describing what the extension does.

### Motivation

Why is this extension needed?
- Use cases
- Current limitations
- Benefits

### Specification

Detailed technical specification:
- Syntax
- Semantics
- Validation rules
- Examples

### Compatibility

Impact on existing formats:
- Beancount compatibility
- Ledger compatibility
- hledger compatibility
- Breaking changes

### Implementation

Reference implementation details:
- Repository
- Dependencies
- Installation

### Test Cases

Representative test cases:
- Valid examples
- Invalid examples
- Edge cases

### Alternatives Considered

Other approaches and why they weren't chosen.

### References

Related work, prior art, discussions.

## Submission Process

### Step 1: Draft

Create proposal document following template.

### Step 2: Discussion

Open discussion issue in repository.

### Step 3: Revision

Incorporate feedback into proposal.

### Step 4: Implementation

Create reference implementation.

### Step 5: Testing

Add tests to extension.

### Step 6: Documentation

Complete documentation.

### Step 7: Review

Final review and acceptance.

## Example Proposal

```markdown
# Extension: Budget Tracking

## Summary

Add native budget directive for envelope budgeting.

## Motivation

Currently budgets require workarounds with virtual postings
or external tools. Native support would improve usability.

## Specification

### Syntax

\`\`\`beancount
2024-01-01 budget Food 500.00 USD
\`\`\`

### Semantics

Creates budget envelope for specified account prefix.

### Validation

Warns when spending exceeds budget.

## Compatibility

- Beancount: Custom directive fallback
- Ledger: Periodic transaction equivalent
- hledger: Forecast equivalent

## Implementation

https://github.com/example/pta-budget-extension

## Test Cases

See tests/budget/*.beancount
```

## Review Criteria

Proposals evaluated on:
- Clarity of specification
- Quality of implementation
- Test coverage
- Documentation completeness
- Community interest
- Compatibility impact

## Timeline

| Phase | Duration |
|-------|----------|
| Draft | 2 weeks |
| Discussion | 4 weeks |
| Implementation | 4 weeks |
| Review | 2 weeks |

## See Also

- [Graduation Criteria](graduation.md)
- [Extension Template](../catalog/template/)
