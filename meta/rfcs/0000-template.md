# RFC-0000: [Title]

- **RFC Number**: 0000 (assigned upon acceptance)
- **Author(s)**: [Your Name]
- **Status**: Draft
- **Created**: YYYY-MM-DD
- **Updated**: YYYY-MM-DD

## Summary

One paragraph explanation of the feature or change.

## Motivation

Why are we doing this? What problem does it solve? What use cases does it support?

Include:
- Current limitations
- User needs
- Why existing solutions are insufficient

## Detailed Design

### Syntax

If proposing new syntax, provide the grammar:

```ebnf
new_directive = "keyword" , identifier , value ;
```

Example usage:

```beancount
; Example of the new feature
keyword example value
```

### Semantics

Describe the behavior:

- What happens when this feature is used?
- How does it interact with existing features?
- Edge cases and corner cases

### Error Handling

What errors can occur and how are they reported?

| Condition | Error Message |
|-----------|---------------|
| Invalid usage | "Error: description" |

### Examples

Provide multiple examples showing:

1. Basic usage
2. Common patterns
3. Edge cases
4. Error cases

```beancount
; Example 1: Basic usage
...

; Example 2: With options
...
```

## Alternatives Considered

What other designs were considered? Why weren't they chosen?

### Alternative 1: [Name]

Description and why it was rejected.

### Alternative 2: [Name]

Description and why it was rejected.

## Compatibility

### Backwards Compatibility

- Is this a breaking change?
- If yes, what is the migration path?

### Forward Compatibility

- Can older implementations ignore this feature?
- What happens if this feature is used with older tools?

### Cross-Format Compatibility

- Does this feature exist in other PTA formats?
- If so, how does this proposal align?

## Implementation Notes

Guidance for implementers:

- Recommended implementation approach
- Performance considerations
- Security considerations

## Open Questions

Unresolved questions to be addressed during review:

1. Question 1?
2. Question 2?

## References

- Related RFCs
- External specifications
- Prior art

## Changelog

- YYYY-MM-DD: Initial draft
- YYYY-MM-DD: Updated based on feedback

---

## Appendix A: Grammar

Complete grammar additions if applicable.

## Appendix B: Test Cases

Conformance test cases for this feature.

```json
{
  "id": "feature-basic-001",
  "description": "Basic usage of feature",
  "input": "...",
  "expected": {
    "parse": true,
    "validate": true
  }
}
```
