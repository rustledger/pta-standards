# History of Plain Text Accounting

This document provides historical context for plain text accounting and the tools that shaped it.

## Origins

### Double-Entry Bookkeeping (1494)

Plain text accounting builds on double-entry bookkeeping, codified by Luca Pacioli in 1494. The fundamental principle—every transaction affects at least two accounts, with debits equaling credits—remains unchanged.

### Early Computer Accounting

Early computerized accounting systems (1960s-1980s) used proprietary formats and required specialized hardware. Data portability was minimal.

### The Unix Philosophy

The Unix philosophy of small, composable tools working with text streams influenced PTA design:

- Text as universal interface
- Simple formats over complex ones
- Tools that do one thing well

## Ledger (2003)

### Creation

John Wiegley created Ledger in 2003, establishing the plain text accounting paradigm:

- Plain text files editable with any editor
- Command-line interface
- Double-entry enforcement
- Multiple currencies

### Key Innovations

- **Text-based format**: Human-readable, version-controllable
- **Flexible syntax**: Accommodates various accounting styles
- **Expression language**: Calculations within the ledger
- **Virtual postings**: Envelope budgeting
- **Automated transactions**: Rule-based posting generation

### Influence

Ledger established patterns that all subsequent tools follow:

```ledger
2024/01/15 * Grocery Store
    Expenses:Food:Groceries         $85.50
    Assets:Checking
```

## hledger (2007)

### Creation

Simon Michael created hledger in 2007 as a Haskell implementation:

- Stricter parsing than Ledger
- Better error messages
- Cross-platform support
- Web interface

### Divergence

hledger intentionally diverged from Ledger in some areas:

- Stricter syntax requirements
- Different default behaviors
- Additional features (timedot format, CSV rules)

### Philosophy

hledger emphasized:

- Reliability over flexibility
- Clear documentation
- Beginner-friendly error messages

## Beancount (2007-2008)

### Creation

Martin Blais created Beancount around 2007-2008:

- Python implementation
- Even stricter syntax
- Plugin architecture
- Query language (BQL)

### Key Differences

Beancount took a more opinionated approach:

- **Required account opening**: Accounts must be declared before use
- **Uppercase commodities**: Enforced naming convention
- **No expressions**: Simplicity over flexibility
- **Explicit everything**: Minimal implicit behavior

### Innovations

- **Plugin system**: Extensible validation and transformation
- **Query language**: SQL-like queries on ledger data
- **Importers framework**: Structured bank import system
- **Fava**: Web interface with rich visualizations

## Comparison Timeline

```
1494  Pacioli publishes double-entry bookkeeping
 ...
2003  Ledger created (C++)
2007  hledger created (Haskell)
2008  Beancount created (Python)
 ...
2014  Fava web interface for Beancount
2016  Ledger 3.0 released
2020  Beancount v2 stable
2023  Beancount v3 development
2024  PTA Standards project initiated
```

## Format Evolution

### Ledger Format

```ledger
; Original Ledger syntax (2003)
2024/01/15 * Grocery Store
    Expenses:Food         $85.50
    Assets:Checking

; With metadata (later addition)
2024/01/15 * Grocery Store
    ; :tag:
    Expenses:Food         $85.50
    Assets:Checking
```

### hledger Format

```hledger
; hledger syntax (mostly compatible)
2024-01-15 * Grocery Store
    Expenses:Food         $85.50
    Assets:Checking

; hledger-specific: timedot format
2024-01-15
client1  .... ....  ; 2 hours
client2  ..         ; 0.5 hours
```

### Beancount Format

```beancount
; Beancount syntax (stricter)
2024-01-01 open Assets:Checking USD
2024-01-01 open Expenses:Food

2024-01-15 * "Grocery Store" "Weekly shopping"
  Expenses:Food         85.50 USD
  Assets:Checking
```

## Community Development

### Mailing Lists and Forums

- Ledger: ledger-cli Google Group
- hledger: hledger mail list, Matrix chat
- Beancount: beancount Google Group

### Ecosystem Growth

Each tool developed an ecosystem:

| Tool | Importers | Integrations | Web UI |
|------|-----------|--------------|--------|
| Ledger | Community | Emacs, Vim | ledger-web |
| hledger | Built-in CSV | Emacs, Vim | hledger-web |
| Beancount | Framework | Emacs, Vim | Fava |

### Cross-Pollination

Ideas flow between communities:

- Beancount's plugin concept influenced hledger
- Ledger's expressions inspired extensions
- hledger's CSV rules adopted by others

## The Need for Standards

### Fragmentation Challenges

By 2020, fragmentation became apparent:

- Subtle syntax differences caused conversion issues
- Users confused by similar-but-different formats
- Tool authors reimplementing similar logic
- No authoritative specification for any format

### Standardization Efforts

Various efforts emerged:

- Community documentation projects
- Conversion tool development
- Discussion of common interchange format

### PTA Standards Project

The PTA Standards project aims to:

1. Document existing formats precisely
2. Enable reliable conversion between formats
3. Define conformance levels for implementations
4. Preserve the history and rationale of decisions

## Lessons from History

### What Worked

- **Plain text**: Survived 20+ years, still relevant
- **Double-entry**: Fundamental principle unchanged
- **Command-line**: Composable with other tools
- **Community**: Passionate, helpful users

### What Challenged

- **Format fragmentation**: Similar but incompatible
- **Documentation gaps**: Behavior defined by implementation
- **Feature creep**: Complexity growth over time

### Future Considerations

- Maintain backwards compatibility
- Document before implementing
- Preserve the "plain text" philosophy
- Support interoperability

## References

- [Ledger CLI](https://www.ledger-cli.org/)
- [hledger](https://hledger.org/)
- [Beancount](https://beancount.github.io/)
- [Plain Text Accounting](https://plaintextaccounting.org/)
- [Pacioli's Summa de Arithmetica](https://en.wikipedia.org/wiki/Summa_de_arithmetica)
