# Release Process

This document describes how PTA Standards releases are created and published.

## Release Types

### Regular Releases

Regular releases follow a predictable schedule:

| Release Type | Frequency | Contents |
|--------------|-----------|----------|
| **Major** (X.0.0) | As needed | Breaking changes, major features |
| **Minor** (x.Y.0) | Quarterly | New features, enhancements |
| **Patch** (x.y.Z) | As needed | Bug fixes, clarifications |

### Hotfix Releases

Hotfix releases are created for:

- Critical specification errors
- Security-related clarifications
- Urgent compatibility issues

Hotfixes may be released at any time outside the regular schedule.

## Release Checklist

### Pre-Release

1. [ ] All RFCs for this release are merged
2. [ ] Changelog is updated
3. [ ] Version numbers are updated in all locations
4. [ ] All tests pass
5. [ ] Documentation is complete
6. [ ] Breaking changes are documented

### Release

1. [ ] Create release branch: `release/vX.Y.Z`
2. [ ] Final review of changes
3. [ ] Tag the release: `vX.Y.Z`
4. [ ] Generate release artifacts
5. [ ] Publish release notes

### Post-Release

1. [ ] Announce on mailing list
2. [ ] Update implementation registry
3. [ ] Merge release branch to main
4. [ ] Begin next development cycle

## Release Artifacts

Each release produces:

| Artifact | Description | Format |
|----------|-------------|--------|
| Specification documents | Canonical spec text | Markdown, HTML, PDF |
| JSON Schemas | Machine-readable schemas | JSON |
| Grammar files | Formal grammars | EBNF, ABNF |
| Test suites | Conformance tests | JSON |
| Changelog | List of changes | Markdown |

## Release Branches

```
main ─────●─────●─────●─────●─────●─────●─────▶
          │     │           │
          │     │           └─── release/v1.2.0
          │     │
          │     └─── release/v1.1.0
          │
          └─── release/v1.0.0
```

### Branch Naming

- Release branches: `release/vX.Y.Z`
- Feature branches: `feature/description`
- Hotfix branches: `hotfix/vX.Y.Z`

## Version Locations

Version numbers must be updated in:

1. `README.md` - Badge and documentation
2. `*/version.md` - Each specification's version file
3. `package.json` - If applicable
4. `CHANGELOG.md` - Release notes
5. JSON schemas - `$id` and version fields

## Changelog Format

We follow [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [1.2.0] - 2024-06-15

### Added
- New feature description

### Changed
- Modified behavior description

### Deprecated
- Feature being phased out

### Removed
- Feature that was removed

### Fixed
- Bug that was fixed

### Security
- Security-related changes
```

## Announcement Template

```
Subject: PTA Standards vX.Y.Z Released

We are pleased to announce the release of PTA Standards vX.Y.Z.

## Highlights

- Feature 1
- Feature 2
- Feature 3

## Breaking Changes

[List any breaking changes]

## Full Changelog

[Link to changelog]

## Downloads

[Links to release artifacts]

## Thank You

Thanks to all contributors: [names]
```

## Related Documents

- [Versioning](versioning.md) - Version numbering
- [Breaking Changes](breaking-changes.md) - Breaking change policy
- [CHANGELOG.md](../../CHANGELOG.md) - Release history
