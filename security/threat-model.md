# Threat Model

## Overview

This document analyzes security threats to Beancount implementations and defines mitigations.

## Assumptions

### Trusted

- The user invoking the tool
- The main ledger file (user-created)
- The local filesystem (user's machine)

### Semi-Trusted

- Included files (may be from shared locations)
- Downloaded price data
- Imported bank statements

### Untrusted

- Third-party plugins
- Network-fetched content
- Files from untrusted sources

## Threat Categories

### T1: Denial of Service

#### T1.1: Resource Exhaustion

**Description:** Malicious input causes excessive CPU, memory, or disk usage.

**Attack Vectors:**
- Extremely large files
- Deeply nested includes
- Pathological regex patterns
- Infinite loops in expressions

**Mitigations:**
- Input size limits (see [limits/input.md](limits/input.md))
- Memory limits (see [limits/memory.md](limits/memory.md))
- Nesting depth limits (see [limits/nesting.md](limits/nesting.md))
- Timeout mechanisms

#### T1.2: Algorithmic Complexity

**Description:** Input triggers worst-case algorithmic behavior.

**Attack Vectors:**
- Hash collision attacks on dictionaries
- ReDoS (Regular Expression DoS)
- Quadratic parsing behavior

**Mitigations:**
- Use DOS-resistant hash functions for user-controlled keys
- Avoid backtracking regex (see [parsing/redos.md](parsing/redos.md))
- Linear-time parsing algorithms

### T2: Information Disclosure

#### T2.1: Path Traversal

**Description:** Attacker reads files outside intended directory.

**Attack Vectors:**
- `include "../../../etc/passwd"`
- `include "/etc/shadow"`
- Symbolic link following

**Mitigations:**
- Restrict includes to subdirectories (see [includes/path-traversal.md](includes/path-traversal.md))
- Resolve and validate paths before access
- Optional: reject symlinks (see [includes/symlinks.md](includes/symlinks.md))

#### T2.2: Error Message Leakage

**Description:** Error messages reveal sensitive information.

**Attack Vectors:**
- Full file paths in errors
- Stack traces with internal state
- Timing side channels

**Mitigations:**
- Sanitize error messages for untrusted contexts
- Use constant-time comparisons where appropriate

### T3: Code Execution

#### T3.1: Plugin Attacks

**Description:** Malicious plugin executes arbitrary code.

**Attack Vectors:**
- File system access
- Network access
- Process spawning
- Environment variable access

**Mitigations:**
- Plugin sandboxing (see [plugins/sandboxing.md](plugins/sandboxing.md))
- Capability-based permissions (see [plugins/capabilities.md](plugins/capabilities.md))
- Code signing / allowlists

#### T3.2: Expression Injection

**Description:** User input interpreted as code.

**Attack Vectors:**
- Arithmetic expression evaluation
- Query string interpolation
- Format string attacks

**Mitigations:**
- Parse expressions to AST, don't eval()
- Parameterized queries
- Input validation

### T4: Data Integrity

#### T4.1: Include Cycles

**Description:** Circular includes cause infinite loops or corruption.

**Attack Vectors:**
- `a.beancount` includes `b.beancount` includes `a.beancount`
- Self-inclusion

**Mitigations:**
- Cycle detection (see [includes/cycles.md](includes/cycles.md))
- Track included files in a set

#### T4.2: Race Conditions

**Description:** TOCTOU (time-of-check-time-of-use) vulnerabilities.

**Attack Vectors:**
- File modified between check and read
- Symlink swapping

**Mitigations:**
- Use file handles, not paths, after opening
- Atomic operations where possible

## Risk Matrix

| Threat | Likelihood | Impact | Risk | Priority |
|--------|------------|--------|------|----------|
| T1.1 Resource Exhaustion | Medium | Medium | Medium | High |
| T1.2 Algorithmic Complexity | Low | High | Medium | Medium |
| T2.1 Path Traversal | Medium | High | High | High |
| T2.2 Error Leakage | Low | Low | Low | Low |
| T3.1 Plugin Attacks | Medium | Critical | High | High |
| T3.2 Expression Injection | Low | High | Medium | Medium |
| T4.1 Include Cycles | Medium | Low | Low | Medium |
| T4.2 Race Conditions | Low | Medium | Low | Low |

## Security Requirements Summary

### MUST (Required)

1. Limit input file size
2. Detect and reject include cycles
3. Prevent path traversal in includes
4. Avoid ReDoS-vulnerable patterns
5. Limit parser recursion depth

### SHOULD (Recommended)

1. Limit memory usage
2. Sandbox third-party plugins
3. Validate symlinks before following
4. Use DOS-resistant hashing

### MAY (Optional)

1. Implement plugin capability system
2. Support file integrity verification
3. Provide audit logging
