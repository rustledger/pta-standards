# Extension Graduation Criteria

This document defines criteria for extensions to graduate into the core specification.

## Overview

Graduation moves an extension from:
- Experimental → Stable
- Optional → Recommended
- Extension → Core

## Graduation Levels

### Level 1: Experimental

- Working implementation exists
- Basic documentation
- Some test coverage
- Limited adoption

### Level 2: Stable

- Multiple implementations
- Complete documentation
- Comprehensive tests
- Growing adoption

### Level 3: Recommended

- Wide adoption
- Proven stability
- Community consensus
- Integration ready

### Level 4: Core

- Format integration
- Universal support
- Backward compatible
- Specification complete

## Criteria

### Implementation Quality

- [ ] Reference implementation complete
- [ ] At least one additional implementation
- [ ] No known critical bugs
- [ ] Performance acceptable

### Documentation

- [ ] Specification complete
- [ ] User guide available
- [ ] Examples provided
- [ ] Migration guide (if applicable)

### Testing

- [ ] Unit tests complete
- [ ] Integration tests
- [ ] Edge case coverage
- [ ] Cross-implementation tests

### Adoption

- [ ] Multiple projects using
- [ ] Positive user feedback
- [ ] No blocking concerns
- [ ] Maintenance commitment

### Compatibility

- [ ] No breaking changes to core
- [ ] Graceful degradation
- [ ] Interoperability verified
- [ ] Upgrade path defined

## Graduation Process

### Step 1: Self-Assessment

Extension maintainer evaluates against criteria.

### Step 2: Application

Submit graduation application with:
- Evidence for each criterion
- Implementation status
- Adoption metrics
- Known issues

### Step 3: Review

Community review period (30 days):
- Technical review
- Compatibility review
- User feedback

### Step 4: Decision

Steering committee decision:
- Approve graduation
- Request changes
- Decline with feedback

### Step 5: Integration

If approved:
- Merge into specification
- Update implementations
- Announce graduation

## Maintenance Requirements

Graduated extensions require:
- Active maintenance
- Bug fix commitment
- Version compatibility
- Documentation updates

## Deprecation

Extensions may be deprecated if:
- No active maintainer
- Superseded by better solution
- Critical unfixable issues
- Declining adoption

## Examples

### Successful Graduation

```
Extension: Balance Assertions
Path: Experimental → Stable → Recommended → Core
Timeline: 18 months
Implementations: 5
Adoption: Universal
```

### Pending Graduation

```
Extension: Auto-Categorization
Status: Stable
Blockers: Second implementation needed
Target: Recommended
```

## See Also

- [Proposal Process](proposal.md)
- [Extension Template](../catalog/template/)
