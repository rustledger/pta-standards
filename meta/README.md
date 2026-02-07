# Meta Documentation

This directory contains governance, process, and decision documentation for the PTA Standards project.

## Contents

### Architecture Decision Records (ADRs)

The `adrs/` directory contains documented decisions about the project's architecture and approach:

- [ADR-0001: Three Separate Specs](adrs/0001-three-separate-specs.md) - Why we maintain separate specifications for Beancount, Ledger, and hledger
- [ADR-0002: Alloy Over TLA+](adrs/0002-alloy-over-tlaplus.md) - Why we chose Alloy for formal modeling

### Requests for Comments (RFCs)

The `rfcs/` directory contains proposals for significant changes:

- [RFC Template](rfcs/0000-template.md) - Template for new RFC proposals
- [RFC Index](rfcs/README.md) - List of all RFCs

### Process Documentation

The `process/` directory documents how we manage the specification:

- [Versioning](process/versioning.md) - How spec versions are numbered
- [Releases](process/releases.md) - Release process and schedule
- [Deprecation](process/deprecation.md) - How features are deprecated
- [Breaking Changes](process/breaking-changes.md) - Policy for breaking changes

## Contributing

To propose a change to the specification:

1. **Minor clarifications**: Open a pull request directly
2. **New features or behaviors**: Write an RFC first
3. **Architectural decisions**: Document as an ADR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## Governance

See [GOVERNANCE.md](../GOVERNANCE.md) for project governance structure.
