# Grammar Format Choices

This document explains why we provide grammars in multiple notation formats.

## Context

Formal grammars precisely define valid syntax. Multiple grammar notation formats exist, each with different strengths and tool support.

## Decision

We provide grammars in three formats:

1. **PEG** (Parsing Expression Grammar)
2. **EBNF** (Extended Backus-Naur Form)
3. **ABNF** (Augmented BNF, RFC 5234)

## Rationale

### Why Multiple Formats?

Different audiences need different formats:

| Audience | Preferred Format | Reason |
|----------|------------------|--------|
| Parser implementers | PEG | Direct translation to parser combinators |
| Language designers | EBNF | ISO standard, widely taught |
| Protocol implementers | ABNF | RFC standard, precise |
| Academics | EBNF/BNF | Theoretical foundation |

### Why These Three?

#### PEG (Parsing Expression Grammar)

**Strengths**:
- Unambiguous by design (ordered choice)
- Direct mapping to recursive descent parsers
- Supported by many parser generators
- Handles greedy matching naturally

**Tools supporting PEG**:
- pest (Rust)
- PEG.js (JavaScript)
- parsiux, pyparsing (Python)
- tree-sitter (multi-language)

**Example**:
```peg
transaction <- date SP flag SP payee? narration NL posting+
posting <- INDENT account SP amount? cost? price? NL
```

#### EBNF (Extended Backus-Naur Form)

**Strengths**:
- ISO/IEC 14977 standard
- Widely understood
- Taught in computer science curricula
- Good for documentation

**Characteristics**:
- Declarative, not operational
- May be ambiguous (requires disambiguation)
- Human-readable

**Example**:
```ebnf
transaction = date, flag, [payee], narration, {posting} ;
posting = indent, account, [amount], [cost], [price] ;
```

#### ABNF (Augmented BNF)

**Strengths**:
- RFC 5234 standard
- Used in IETF specifications
- Precise character-level definitions
- Good for protocol specifications

**Characteristics**:
- Terminal symbols are numeric or quoted
- Explicit repetition syntax
- Common in networking specs

**Example**:
```abnf
transaction = date SP flag [SP payee] SP narration CRLF 1*posting
posting     = indent account [SP amount] [SP cost] [SP price] CRLF
```

## Alternatives Considered

### Alternative 1: PEG Only

**Approach**: Provide only PEG grammar.

**Problems**:
- Unfamiliar to some audiences
- Less readable for documentation
- Not an ISO standard

**Rejected because**: Limits accessibility.

### Alternative 2: EBNF Only

**Approach**: Provide only EBNF grammar.

**Problems**:
- Ambiguous (need disambiguation rules)
- Less direct for parser implementation
- No tool ecosystem for PEG generators

**Rejected because**: Parser implementers need unambiguous spec.

### Alternative 3: BNF (Original)

**Approach**: Use original BNF notation.

**Problems**:
- More verbose than EBNF
- No standard repetition syntax
- Dated notation

**Rejected because**: EBNF is strictly superior.

### Alternative 4: ANTLR Format

**Approach**: Use ANTLR grammar format.

**Problems**:
- Tool-specific
- Mixes grammar with actions
- Not a standard

**Rejected because**: Too implementation-specific.

## Implementation

### File Organization

```
formats/beancount/v3/grammar/
├── beancount.peg      # PEG grammar
├── beancount.ebnf     # EBNF grammar
└── beancount.abnf     # ABNF grammar
```

### Consistency Requirements

All three grammars MUST:

1. Define the same language
2. Use consistent naming for productions
3. Be tested against the same test suite
4. Be updated together

### Canonical Format

PEG is the **canonical** format because:

- Unambiguous by construction
- Directly implementable
- Most precise operational semantics

EBNF and ABNF are derived from PEG and kept synchronized.

## Consequences

### Benefits

1. **Wide accessibility** - Readers can use familiar notation
2. **Tool flexibility** - Implementers can use preferred parser generator
3. **Standards compliance** - ISO and RFC formats available
4. **Documentation value** - EBNF is readable in specifications

### Costs

1. **Maintenance burden** - Three files to keep synchronized
2. **Potential drift** - Formats could become inconsistent
3. **Complexity** - More artifacts to manage

### Mitigation

- Automated tests verify grammars define same language
- Single source (PEG) with derivation tools
- Clear update procedures

## Usage Guidance

### For Documentation

Use EBNF in prose:

```markdown
A transaction consists of a date, flag, optional payee,
narration, and one or more postings:

​```ebnf
transaction = date, flag, [payee], narration, {posting} ;
​```
```

### For Implementation

Use PEG for parser generators:

```rust
// pest grammar
transaction = { date ~ flag ~ payee? ~ narration ~ posting+ }
```

### For Protocol Specs

Use ABNF for formal specifications:

```abnf
; RFC-style specification
transaction = date SP flag [SP payee] SP narration CRLF 1*posting
```

## References

- [ISO/IEC 14977](https://www.iso.org/standard/26153.html) - EBNF standard
- [RFC 5234](https://tools.ietf.org/html/rfc5234) - ABNF specification
- [PEG Paper](https://bford.info/pub/lang/peg.pdf) - Bryan Ford's original paper
- [Notation Conventions](../core/conventions/notation.md) - How we write grammars
