# Security Specifications

This directory contains security requirements and guidelines for Beancount implementations.

## Overview

Plain text accounting tools process user-controlled input files. While ledger files are typically local and trusted, implementations MUST handle malformed or malicious input gracefully to prevent:

- Denial of Service (resource exhaustion)
- Information disclosure (path traversal)
- Code execution (plugin sandboxing)

## Threat Model

See [threat-model.md](threat-model.md) for the complete threat analysis.

### Trust Boundaries

```
┌─────────────────────────────────────────────────────────┐
│                    User Environment                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ Ledger File │    │  Includes   │    │  Plugins    │ │
│  │  (trusted)  │───▶│ (semi-trust)│───▶│ (untrusted) │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Beancount Implementation            │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────┐  │   │
│  │  │ Parser  │  │ Loader  │  │ Plugin Runtime  │  │   │
│  │  └─────────┘  └─────────┘  └─────────────────┘  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Security Topics

### Input Handling

| Topic | Description | Spec |
|-------|-------------|------|
| [Input Limits](limits/input.md) | Size, line length, file count | MUST |
| [Memory Limits](limits/memory.md) | Memory usage bounds | SHOULD |
| [Nesting Limits](limits/nesting.md) | Recursion depth limits | MUST |

### Parsing

| Topic | Description | Spec |
|-------|-------------|------|
| [ReDoS](parsing/redos.md) | Regular expression denial of service | MUST |
| [Stack Overflow](parsing/stack-overflow.md) | Parser stack exhaustion | MUST |

### File Includes

| Topic | Description | Spec |
|-------|-------------|------|
| [Path Traversal](includes/path-traversal.md) | Directory escape prevention | MUST |
| [Cycles](includes/cycles.md) | Include cycle detection | MUST |
| [Symlinks](includes/symlinks.md) | Symbolic link handling | SHOULD |

### Plugins

| Topic | Description | Spec |
|-------|-------------|------|
| [Sandboxing](plugins/sandboxing.md) | Plugin isolation requirements | SHOULD |
| [Capabilities](plugins/capabilities.md) | Plugin permission model | SHOULD |

## Conformance Levels

Implementations MUST document their security posture:

| Level | Requirements |
|-------|--------------|
| **Basic** | Input limits, path traversal protection |
| **Standard** | Basic + ReDoS protection, cycle detection |
| **Hardened** | Standard + plugin sandboxing, memory limits |

## Reporting Vulnerabilities

See [SECURITY.md](../SECURITY.md) in the repository root.
