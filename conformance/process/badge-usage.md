# Conformance Badge Usage Guidelines

This document describes how to use PTA conformance badges after certification.

## Badge Types

### Format-Specific Badges

Each format has its own badge design:

| Format | Badge |
|--------|-------|
| Beancount | ![Beancount](https://img.shields.io/badge/PTA-Beancount-green) |
| Ledger | ![Ledger](https://img.shields.io/badge/PTA-Ledger-blue) |
| hledger | ![hledger](https://img.shields.io/badge/PTA-hledger-purple) |

### Level Indicators

Badges indicate conformance level:

| Level | Badge Style |
|-------|-------------|
| Level 1: Core Syntax | `beancount-v3-L1` |
| Level 2: Validation | `beancount-v3-L2` |
| Level 3: Full | `beancount-v3-L3` |

## Badge URLs

### Static Badges (Recommended)

Use shields.io for consistent styling:

```
https://img.shields.io/badge/PTA-Beancount_v3_L2-green
```

### Dynamic Badges

For auto-updating badges (coming soon):

```
https://pta-standards.org/badge/{implementation}.svg
```

## Usage Examples

### README Badge

Add to your project README:

```markdown
# My Beancount Implementation

[![PTA Conformance](https://img.shields.io/badge/PTA-Beancount_v3_L2-green)](https://github.com/pta-standards/pta-standards)

A fast Beancount parser written in Rust.
```

### With Test Results Link

Link to your detailed results:

```markdown
[![PTA Beancount v3 Level 2](https://img.shields.io/badge/PTA-Beancount_v3_L2-green)](https://github.com/your/repo/blob/main/CONFORMANCE.md)
```

### Multiple Formats

If your implementation supports multiple formats:

```markdown
[![Beancount](https://img.shields.io/badge/PTA-Beancount_v3_L3-green)](...)
[![hledger](https://img.shields.io/badge/PTA-hledger_v1_L2-purple)](...)
```

### In Documentation

Reference conformance in your docs:

```markdown
## Compatibility

This implementation is certified **PTA Beancount v3 Level 2** conformant,
meaning it correctly parses all standard Beancount syntax and validates
semantic rules with 98%+ accuracy.

See our [conformance results](./conformance/results.json) for details.
```

## Badge Styling

### Color Coding

| Level | Color | Hex |
|-------|-------|-----|
| Level 1 | Yellow | `#dfb317` |
| Level 2 | Green | `#97ca00` |
| Level 3 | Bright Green | `#4c1` |
| Not Conformant | Red | `#e05d44` |

### Custom Styles

Shields.io supports various styles:

```markdown
<!-- Flat -->
![](https://img.shields.io/badge/PTA-Beancount_L2-green?style=flat)

<!-- Flat Square -->
![](https://img.shields.io/badge/PTA-Beancount_L2-green?style=flat-square)

<!-- For The Badge -->
![](https://img.shields.io/badge/PTA-Beancount_L2-green?style=for-the-badge)

<!-- Plastic -->
![](https://img.shields.io/badge/PTA-Beancount_L2-green?style=plastic)
```

### With Logo

Include the PTA logo:

```markdown
![](https://img.shields.io/badge/PTA-Beancount_L2-green?logo=data:...)
```

## Requirements

### Accuracy

- Only display badges for levels you've actually achieved
- Update badges when re-certifying at a new level
- Remove badges if certification is revoked

### Version Specificity

- Include the format version in your badge
- Update when certifying for a new version
- Don't claim certification for versions you haven't tested

### Linking

- Link to your certification or results when possible
- Include certification date somewhere in your docs
- Reference the test suite version used

## Do's and Don'ts

### Do

- Display your earned badge prominently
- Link to detailed conformance results
- Update badge when you improve conformance level
- Include certification date
- Mention any known limitations

### Don't

- Claim a higher level than achieved
- Display badge for untested versions
- Use badge after certification expires/revokes
- Modify badge to misrepresent status
- Claim "100% compatible" without Level 3

## Expiration

Certifications don't formally expire, but:

- Re-certify when the test suite is significantly updated
- Re-certify for major releases of your implementation
- Stale certifications (>1 year) may be questioned

## Badge Generator

Generate your badge URL:

```bash
# Level 1
echo "https://img.shields.io/badge/PTA-${FORMAT}_v${VERSION}_L1-yellow"

# Level 2
echo "https://img.shields.io/badge/PTA-${FORMAT}_v${VERSION}_L2-green"

# Level 3
echo "https://img.shields.io/badge/PTA-${FORMAT}_v${VERSION}_L3-brightgreen"
```

## Full Example

```markdown
# rustledger

[![CI](https://github.com/user/rustledger/actions/workflows/ci.yml/badge.svg)](...)
[![Crates.io](https://img.shields.io/crates/v/rustledger)](...)
[![PTA Conformance](https://img.shields.io/badge/PTA-Beancount_v3_L2-green)](https://github.com/pta-standards/pta-standards/blob/main/certifications/rustledger.json)

A fast Beancount implementation in Rust.

## Conformance

This implementation is certified **PTA Beancount v3 Level 2** (January 2024).

| Metric | Value |
|--------|-------|
| Tests Passed | 240/243 |
| Pass Rate | 98.77% |
| Failures | 1 (precision limitation) |
| Skipped | 2 (undefined behavior) |

See [conformance results](./conformance/) for details.
```

## Questions

For badge-related questions:
- Open an issue with the `badge` label
- Check existing implementations for examples
- Review the shields.io documentation

## See Also

- [Self-Certification Process](self-certification.md)
- [Test Requirements](test-requirements.md)
- [Shields.io Documentation](https://shields.io)
