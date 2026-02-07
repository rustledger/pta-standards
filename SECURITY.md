# Security Policy

This document describes security considerations for PTA Standards and how to report security issues.

## Scope

Security considerations for PTA Standards include:

1. **Specification Security** - Security implications of specified behaviors
2. **Reference Implementation** - Build tools and test harness
3. **Documentation** - Preventing misleading security guidance

## Security Considerations in Specifications

### Parser Security

Implementations should be aware of:

| Risk | Description | Mitigation |
|------|-------------|------------|
| DoS via complex input | Deeply nested structures, long lines | Impose limits |
| Path traversal | `include` directives with `../` | Validate paths |
| Unicode issues | Homoglyph attacks, RTL override | Normalize input |
| Memory exhaustion | Very large files | Stream processing |

### Data Security

| Risk | Description | Mitigation |
|------|-------------|------------|
| Sensitive data exposure | Account numbers, balances | Encryption at rest |
| Injection attacks | Metadata in external systems | Sanitize output |
| Information leakage | Error messages reveal paths | Generic errors |

### Include File Security

The `include` directive poses risks:

```beancount
; Potentially dangerous
include "/etc/passwd"           ; Absolute paths outside project
include "../../../secret.bean"  ; Path traversal
include "https://evil.com/x"    ; Remote includes (if supported)
```

Recommendations for implementations:

1. Restrict includes to project directory
2. Disallow absolute paths by default
3. Require explicit opt-in for remote includes
4. Validate paths before opening

## Reporting Security Issues

### For Specification Issues

If you find a security issue in the specification itself:

1. **Do NOT open a public issue**
2. Open a GitHub Security Advisory (private)
3. Include:
   - Description of the issue
   - Potential impact
   - Suggested fix (if any)

### For Implementation Issues

Security issues in specific implementations should be reported to those projects directly. This specification project is not responsible for implementation security.

### For Build Tool Issues

Security issues in our build tools and test harness:

1. Open a GitHub Security Advisory
2. Or contact maintainers directly

## Response Timeline

| Stage | Timeline |
|-------|----------|
| Acknowledgment | 48 hours |
| Initial assessment | 1 week |
| Fix development | 2-4 weeks |
| Disclosure | After fix, or 90 days |

## Disclosure Policy

We follow coordinated disclosure:

1. Reporter notifies us privately
2. We assess and develop fix
3. We coordinate disclosure timing with reporter
4. Public disclosure after fix is available

Credit is given to reporters unless they prefer anonymity.

## Security Updates

Security-related specification changes are:

1. Marked clearly in changelog
2. Announced via security mailing list
3. Given expedited review when needed

## Best Practices for Implementations

We recommend implementations:

### Input Validation

```
- Limit maximum file size
- Limit maximum line length
- Limit include depth
- Limit directive count
- Timeout on parsing
```

### Path Handling

```
- Canonicalize paths
- Check for traversal attempts
- Restrict to allowed directories
- Use allowlists over denylists
```

### Error Handling

```
- Avoid exposing full file paths
- Sanitize user input in errors
- Log security events
- Fail securely
```

### Dependency Security

```
- Keep dependencies updated
- Audit dependency trees
- Use lockfiles
- Monitor for CVEs
```

## Security-Related Specification Sections

| Section | Security Relevance |
|---------|-------------------|
| `include` directive | Path traversal, remote includes |
| `plugin` directive | Code execution |
| Metadata fields | Injection if exported |
| Account names | Unicode normalization |
| Decimal handling | Precision attacks |

## Threat Model

### In Scope

- Malicious input files
- Malicious include targets
- Resource exhaustion
- Information disclosure

### Out of Scope

- Compromised development environment
- Physical access attacks
- Social engineering
- Network attacks (unless remote includes)

## Resources

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [Path Traversal Prevention](https://owasp.org/www-community/attacks/Path_Traversal)
- [Unicode Security Guide](https://unicode.org/reports/tr36/)

## Changelog

| Date | Change |
|------|--------|
| 2024-XX-XX | Initial security policy |
