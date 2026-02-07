# Governance

This document describes the governance structure for the PTA Standards project.

## Mission

The PTA Standards project aims to create comprehensive, vendor-neutral specifications for plain text accounting formats, enabling interoperability and fostering a healthy ecosystem of implementations.

## Principles

1. **Vendor Neutral** - No single implementation has privileged status
2. **Community Driven** - Decisions reflect community consensus
3. **Backwards Compatible** - Minimize disruption to existing users
4. **Pragmatic** - Specifications should be implementable and useful
5. **Transparent** - All decisions are made in public

## Roles

### Contributors

Anyone who contributes to the project through:

- Pull requests
- Issue reports
- Documentation
- Testing
- Community support

Contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

### Maintainers

Maintainers are responsible for:

- Reviewing and merging pull requests
- Triaging issues
- Guiding project direction
- Representing the project

Current maintainers:

| Name | GitHub | Focus Area |
|------|--------|------------|
| TBD | @tbd | Core specification |

### Format Stewards

Each format specification has designated stewards who:

- Have deep expertise in that format
- Review format-specific changes
- Liaise with reference implementations
- Ensure consistency with format history

| Format | Stewards |
|--------|----------|
| Beancount | TBD |
| Ledger | TBD |
| hledger | TBD |

### Technical Steering Committee (TSC)

The TSC makes final decisions on:

- Major version releases
- Breaking changes
- New format additions
- Governance changes

TSC membership is by invitation based on sustained contributions.

## Decision Making

### Lazy Consensus

Most decisions use lazy consensus:

1. Proposal is made (PR, RFC, or issue)
2. Community has opportunity to comment
3. If no objections after review period, proposal is accepted

Review periods:

| Change Type | Minimum Review |
|-------------|----------------|
| Typo/clarification | 2 days |
| Minor feature | 1 week |
| Major feature | 2 weeks |
| Breaking change | 4 weeks |

### Voting

When consensus cannot be reached:

1. Discussion period to address concerns
2. If still unresolved, formal vote is called
3. Maintainers vote; simple majority wins
4. TSC can override with 2/3 majority

### Appeals

Decisions can be appealed to the TSC within 2 weeks.

## Meetings

- **Monthly**: Public community meeting (video call)
- **Quarterly**: TSC meeting for roadmap planning
- **As needed**: Working group meetings

Meeting notes are published in the project wiki.

## Adding New Formats

To add a new format to PTA Standards:

1. RFC proposing the addition
2. Demonstrated community interest
3. At least one reference implementation
4. Format steward identified
5. TSC approval

## Removing Formats

Formats may be removed if:

1. No active steward for 12+ months
2. Reference implementation abandoned
3. Community consensus

## Code of Conduct

All participants must follow the [Code of Conduct](CODE_OF_CONDUCT.md). Violations are handled by maintainers and escalated to TSC if needed.

## Changes to Governance

Changes to this governance document require:

1. RFC with 4-week review period
2. TSC approval
3. No objections from maintainers

## License

- Specification text: CC BY 4.0
- Code and schemas: Apache 2.0

See [LICENSE-DOCS](LICENSE-DOCS) and [LICENSE-CODE](LICENSE-CODE).

## Contact

- GitHub Issues: For bugs and feature requests
- Discussions: For general questions

## History

| Date | Change |
|------|--------|
| 2024-XX-XX | Initial governance document |
