# Self-Certification Process

This document describes how implementations can self-certify their conformance level.

## Overview

PTA Standards uses a self-certification model. Implementations:
1. Run the conformance test suite
2. Submit their results
3. Receive a conformance badge

There is no central authority that validates results. Trust is established through:
- Transparent test results
- Reproducible testing process
- Community verification

## Prerequisites

Before self-certifying:

1. **Identify your target format and version**
   - Beancount v3
   - Ledger v1
   - hledger v1

2. **Set up the test environment**
   ```bash
   git clone https://github.com/pta-standards/pta-standards.git
   cd pta-standards
   ```

3. **Install or build your implementation**
   - Ensure it's accessible from command line
   - Note the version number

## Step 1: Run Conformance Tests

### Using the Standard Test Runner

```bash
cd tests/harness/runners/python

# Install dependencies
pip install -r requirements.txt

# Run tests
python runner.py \
  --manifest ../../../beancount/v3/manifest.json \
  --impl your-impl \
  --format json \
  --output results.json
```

### Using Your Own Test Runner

If you implement your own runner:
- Follow the [Test Harness Interface](../../tests/harness/interface.md)
- Output TAP format for verification
- Include all required metadata

## Step 2: Verify Results

Review your results:

```bash
# Summary
cat results.json | jq '.summary'

# Failed tests
cat results.json | jq '.results[] | select(.status == "fail")'
```

### Acceptable Failures

Some failures may be acceptable:
- Tests marked `skip: true`
- Tests with `undefined` tag
- Known precision limitations

Document any acceptable failures in your submission.

## Step 3: Determine Conformance Level

Based on your pass rate:

| Level | Name | Requirement |
|-------|------|-------------|
| 1 | Core Syntax | 100% syntax tests pass |
| 2 | Semantic Validation | Level 1 + 95% validation tests |
| 3 | Full Compatibility | Level 2 + 99% all tests |

Calculate your level:

```python
syntax_pass = syntax_passed / syntax_total >= 1.0
validation_pass = validation_passed / validation_total >= 0.95
full_pass = all_passed / all_total >= 0.99

if full_pass:
    level = 3
elif validation_pass and syntax_pass:
    level = 2
elif syntax_pass:
    level = 1
else:
    level = 0  # Not conformant
```

## Step 4: Submit Results

### Create Certification File

Create `certifications/your-impl.json`:

```json
{
  "implementation": {
    "name": "your-implementation",
    "version": "1.0.0",
    "repository": "https://github.com/user/impl",
    "maintainer": "your@email.com"
  },
  "certification": {
    "format": "beancount",
    "format_version": "v3",
    "level": 2,
    "date": "2024-01-15"
  },
  "results": {
    "total": 243,
    "passed": 240,
    "failed": 1,
    "skipped": 2,
    "pass_rate": "98.77%"
  },
  "test_environment": {
    "os": "Ubuntu 22.04",
    "runner_version": "1.0.0",
    "test_suite_commit": "abc123def"
  },
  "notes": "1 failure due to precision limitation documented in known issues",
  "full_results_url": "https://your-repo.com/conformance-results.json"
}
```

### Submit Pull Request

1. Fork the pta-standards repository
2. Add your certification file
3. Open a pull request with:
   - Title: `cert: Add [impl-name] certification for [format] v[version]`
   - Description: Summary of results and any notes

### Review Process

- Automated checks verify JSON schema
- Maintainers may request clarification
- Community can verify by running tests

## Step 5: Display Badge

Once merged, use the conformance badge:

### Markdown

```markdown
[![PTA Conformance](https://pta-standards.org/badges/beancount-v3-level2.svg)](https://pta-standards.org/conformance/your-impl)
```

### HTML

```html
<a href="https://pta-standards.org/conformance/your-impl">
  <img src="https://pta-standards.org/badges/beancount-v3-level2.svg"
       alt="PTA Conformance Level 2">
</a>
```

See [Badge Usage Guidelines](badge-usage.md) for styling options.

## Updating Certification

When your implementation changes:

1. Run tests against new version
2. Update certification file
3. Submit PR to update

Recommend re-certifying:
- Major version releases
- After significant changes to parser/validator
- When test suite is updated

## Verification by Others

Anyone can verify a certification:

```bash
# Clone the test suite
git clone https://github.com/pta-standards/pta-standards.git
cd pta-standards

# Check out the test suite version used
git checkout <test_suite_commit>

# Install the implementation
# (varies by implementation)

# Run tests
cd tests/harness/runners/python
python runner.py \
  --manifest ../../../beancount/v3/manifest.json \
  --impl the-implementation
```

If results differ significantly from claimed:
- Open an issue describing the discrepancy
- Include your test environment details
- Maintainers will investigate

## Revoking Certification

Certifications may be revoked if:
- Results were falsified
- Implementation regresses significantly
- Maintainer requests removal

Revoked certifications are moved to `certifications/revoked/`.

## Questions

For questions about the process:
- Open a discussion in the repository
- Email the maintainers
- Check existing certifications for examples

## See Also

- [Test Requirements](test-requirements.md)
- [Badge Usage Guidelines](badge-usage.md)
- [Registry of Certified Implementations](../registry.json)
