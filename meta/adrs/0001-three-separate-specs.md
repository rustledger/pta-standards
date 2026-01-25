# ADR 0001: Three Separate Specs

## Status

Accepted

## Context

Plain text accounting has three major formats: Beancount, Ledger, and hledger. These formats share concepts but differ in syntax, features, and semantics.

Options considered:
1. **Single unified spec** with format-specific extensions
2. **Three separate specs** with shared core
3. **One spec per format** with no shared components

## Decision

We will maintain **three separate format specifications** that share a common core:

- `core/` - Shared data model, types, numerics
- `formats/beancount/` - Beancount-specific spec
- `formats/ledger/` - Ledger-specific spec
- `formats/hledger/` - hledger-specific spec

## Consequences

**Positive:**
- Each format can evolve independently
- Clear ownership and scope
- Implementations can target one format
- Shared core reduces duplication

**Negative:**
- More files to maintain
- Must keep core in sync with all formats
- Cross-format features harder to specify

**Neutral:**
- Conversion specs live in `conversions/`
- Test suites are format-specific
