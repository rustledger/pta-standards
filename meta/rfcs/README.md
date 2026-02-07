# Requests for Comments (RFCs)

This directory contains RFCs for significant changes to the PTA Standards.

## What is an RFC?

An RFC (Request for Comments) is a design document that describes a proposed change to the specification. RFCs are used for:

- New features or syntax additions
- Breaking changes to existing behavior
- Significant process or governance changes
- Deprecation of existing features

## When to Write an RFC

You need an RFC for:

| Change Type | RFC Required? |
|-------------|--------------|
| New directive type | Yes |
| New syntax element | Yes |
| Breaking change | Yes |
| New option or pragma | Maybe (if complex) |
| Bug fix / clarification | No |
| Documentation improvement | No |
| New examples | No |

## RFC Process

### 1. Pre-RFC Discussion

Before writing an RFC:

- Open a GitHub issue to discuss the idea
- Gather initial feedback
- Refine the proposal

### 2. Write the RFC

- Copy `0000-template.md` to `0000-your-feature.md`
- Fill in all sections
- Submit as a pull request

### 3. Review Period

- Minimum 2-week review period (4 weeks for breaking changes)
- Address feedback and update RFC
- Build consensus

### 4. Decision

RFCs can be:

- **Accepted** - Merged and assigned a number
- **Rejected** - Closed with rationale
- **Deferred** - Postponed for later consideration
- **Withdrawn** - Author withdraws proposal

### 5. Implementation

Once accepted:

- RFC is merged with an assigned number
- Implementation work can begin
- RFC is referenced in spec changes

## RFC Numbering

- RFCs are numbered sequentially: 0001, 0002, etc.
- Numbers are assigned when RFC is accepted
- Use 0000 in filename until acceptance

## RFC Index

### Accepted RFCs

| Number | Title | Status |
|--------|-------|--------|
| - | - | - |

### Pending RFCs

| Title | PR | Status |
|-------|-------|--------|
| - | - | - |

### Rejected/Withdrawn RFCs

Rejected and withdrawn RFCs are kept for historical reference.

| Title | PR | Reason |
|-------|-------|--------|
| - | - | - |

## RFC Template

See [0000-template.md](0000-template.md) for the RFC template.

## Related Documents

- [CONTRIBUTING.md](../../CONTRIBUTING.md) - How to contribute
- [Breaking Changes](../process/breaking-changes.md) - Breaking change policy
- [Deprecation](../process/deprecation.md) - Deprecation policy
