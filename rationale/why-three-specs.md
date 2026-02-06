# Why Three Specifications

This document explains why PTA Standards documents three separate format specifications (Beancount, Ledger, hledger) rather than defining a single unified format.

## Context

Plain text accounting has three major formats:

1. **Ledger** - The original (2003), C++ implementation
2. **hledger** - Haskell implementation (2007), Ledger-compatible with extensions
3. **Beancount** - Python implementation (2008), intentionally different syntax

Each has a significant user base, ecosystem, and design philosophy.

## Decision

We document all three formats as separate specifications rather than:

- Defining a single "standard" format
- Choosing one format as canonical
- Creating a new unified format

## Rationale

### 1. Respect Existing Communities

Each format has:

- Thousands of active users
- Years of accumulated ledger files
- Tooling ecosystems (editors, importers, reports)
- Design decisions made for good reasons

Declaring one format "the standard" would:

- Alienate other communities
- Invalidate existing files
- Discard valuable design work

### 2. Different Design Trade-offs

The formats made different trade-offs:

| Aspect | Ledger | hledger | Beancount |
|--------|--------|---------|-----------|
| Flexibility | High | Medium | Low |
| Strictness | Low | Medium | High |
| Error messages | Minimal | Good | Good |
| Learning curve | Medium | Medium | Steeper |
| Features | Most | Many | Focused |

No single trade-off is universally correct.

### 3. Innovation Preservation

Different formats enable experimentation:

- Ledger pioneered expression evaluation
- hledger developed timedot format
- Beancount created the plugin architecture

A single standard might stifle innovation.

### 4. Practical Compatibility

Despite differences, the formats share:

- Double-entry semantics
- Similar account hierarchies
- Comparable posting structures
- Related metadata concepts

Documenting the differences enables:

- Accurate format conversion
- Tool interoperability
- User migration between formats

### 5. Historical Precedent

Computing has successful multi-format ecosystems:

- Programming languages (no single "standard" language)
- Image formats (PNG, JPEG, WebP coexist)
- Document formats (with interchange standards)

## Alternatives Considered

### Alternative 1: Single Standard Format

**Approach**: Define one format as "the" standard.

**Problems**:
- Which format? Each has advocates.
- Existing files become non-standard
- Implementation differences become "bugs"
- Community fragmentation

**Rejected because**: No consensus possible, would harm adoption.

### Alternative 2: New Unified Format

**Approach**: Create a new format combining best features.

**Problems**:
- Fourth format, not replacement
- Migration burden for all users
- Years of development needed
- Uncertain adoption

**Rejected because**: Adds complexity without solving core problems.

### Alternative 3: Lowest Common Denominator

**Approach**: Standardize only features common to all formats.

**Problems**:
- Loses valuable features
- Doesn't help with format-specific issues
- Still need format documentation

**Rejected because**: Insufficient utility.

### Alternative 4: Document Nothing

**Approach**: Let implementations define formats.

**Problems**:
- Current situation continues
- No authoritative reference
- Conversion remains unreliable

**Rejected because**: Doesn't address the actual problems.

## Our Approach

### Separate Format Specifications

Each format gets a complete specification:

```
formats/
├── beancount/v3/    # Beancount v3 specification
├── ledger/v1/       # Ledger format specification
└── hledger/v1/      # hledger format specification
```

### Shared Core Model

Common concepts documented once:

```
core/
├── model/           # Accounts, transactions, postings
├── types/           # Decimal, date, string
└── numerics/        # Tolerance, rounding
```

### Explicit Conversion Documentation

How to convert between formats:

```
conversions/
├── beancount-ledger/
├── beancount-hledger/
└── ledger-hledger/
```

### Conformance Levels

Common compliance tiers applicable to any format:

```
conformance/
├── levels/          # Parse, validate, query, full
└── process/         # Certification process
```

## Consequences

### Benefits

1. **Accurate documentation** for each format
2. **Reliable conversion** between formats
3. **Community inclusion** - no format is "wrong"
4. **Innovation continues** in each ecosystem
5. **Practical interoperability** where possible

### Costs

1. **More documentation** to maintain
2. **Complexity** in understanding differences
3. **No single answer** to "which format?"

### Trade-offs Accepted

We accept that:

- Users must still choose a format
- Some features won't convert perfectly
- Documentation is larger than single-format spec

## Implementation Guidance

### For Users

- Choose the format that fits your needs
- Understand conversion limitations
- Use format-specific features knowing portability impact

### For Tool Authors

- Pick a primary format to support
- Use specifications for accuracy
- Document which format(s) you implement
- Consider conversion support

### For the Project

- Maintain all three specifications
- Keep conversion documentation current
- Document format-specific features clearly
- Avoid favoring one format

## Future Considerations

### Possible Evolution

- Formats may converge on some features
- New formats may emerge
- Interchange format might develop organically

### Commitment

We commit to:

- Documenting formats as they exist
- Not forcing artificial convergence
- Supporting format diversity
- Enabling interoperability where practical

## References

- [Design Principles](design-principles.md) - Principle 4: Interoperability
- [History](history.md) - How the formats developed
- [Conversions](../conversions/README.md) - Format conversion specifications
