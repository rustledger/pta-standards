# Notation Conventions

This document defines the notation conventions used throughout the PTA Standards specifications.

## Grammar Notation

### EBNF (Extended Backus-Naur Form)

Syntax rules use EBNF notation:

| Symbol | Meaning | Example |
|--------|---------|---------|
| `=` | Definition | `digit = "0" \| "1" \| ... \| "9"` |
| `\|` | Alternative | `sign = "+" \| "-"` |
| `[ ]` | Optional | `[sign] number` |
| `{ }` | Repetition (0+) | `digits = digit {digit}` |
| `( )` | Grouping | `(a \| b) c` |
| `" "` | Terminal string | `"option"` |
| `' '` | Terminal string | `'open'` |
| `;` | Comment | `; this is a comment` |

### PEG (Parsing Expression Grammar)

Alternative notation for parsing:

| Symbol | Meaning |
|--------|---------|
| `←` | Definition |
| `/` | Ordered choice |
| `?` | Optional |
| `*` | Zero or more |
| `+` | One or more |
| `!` | Not predicate |
| `&` | And predicate |

### Examples

```ebnf
; EBNF
transaction = date flag [payee] narration newline {posting} ;
posting = indent account [amount] [cost] [price] newline ;

; PEG
transaction ← date flag payee? narration newline posting+
posting ← indent account amount? cost? price? newline
```

## Code Examples

### Syntax Highlighting

Code examples use language identifiers:

````
```beancount
2024-01-15 * "Example transaction"
  Assets:Checking  100 USD
  Income:Salary
```
````

### Supported Languages

| Language | Identifier |
|----------|------------|
| Beancount | `beancount` |
| Ledger | `ledger` |
| hledger | `hledger` |
| Python | `python` |
| Rust | `rust` |
| JSON | `json` |
| SQL/BQL | `sql` |

### Placeholder Text

Placeholders in examples:

| Notation | Meaning |
|----------|---------|
| `...` | Content omitted |
| `<name>` | Replace with actual value |
| `[optional]` | May be omitted |
| `{repeated}` | Zero or more times |

```beancount
2024-01-15 * "<payee>" "<narration>"
  <account>  <amount>
  ...
```

## Mathematical Notation

### Arithmetic

| Symbol | Meaning |
|--------|---------|
| `+` | Addition |
| `-` | Subtraction |
| `×` or `*` | Multiplication |
| `÷` or `/` | Division |
| `=` | Equality |
| `≠` | Not equal |
| `≈` | Approximately equal |
| `≤` | Less or equal |
| `≥` | Greater or equal |

### Set Notation

| Symbol | Meaning |
|--------|---------|
| `∈` | Element of |
| `∉` | Not element of |
| `⊂` | Subset |
| `∪` | Union |
| `∩` | Intersection |
| `∅` | Empty set |
| `{ }` | Set definition |

### Logic

| Symbol | Meaning |
|--------|---------|
| `∧` | Logical AND |
| `∨` | Logical OR |
| `¬` | Logical NOT |
| `→` | Implies |
| `↔` | If and only if |
| `∀` | For all |
| `∃` | There exists |

## Type Notation

### Type Signatures

```
function_name(param: Type) -> ReturnType
```

### Common Types

| Notation | Meaning |
|----------|---------|
| `String` | Text value |
| `Number` | Numeric value |
| `Decimal` | Exact decimal |
| `Date` | Calendar date |
| `Boolean` | TRUE/FALSE |
| `List[T]` | List of T |
| `Set[T]` | Set of T |
| `Dict[K,V]` | Map from K to V |
| `Optional[T]` | T or null |
| `T?` | Optional T |

### Type Examples

```
parse_date(s: String) -> Date
format_amount(a: Amount, locale: String) -> String
validate(entries: List[Directive]) -> List[Error]
```

## Diagram Notation

### Flow Diagrams

```
[Start] → [Process] → [End]
            ↓
         [Branch]
```

### Tree Structures

```
Parent
├── Child 1
│   ├── Grandchild A
│   └── Grandchild B
└── Child 2
```

### Tables

```
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

## Error Messages

### Error Format

```
<level>: <message>
  --> <file>:<line>:<column>
   |
<n> | <source line>
   | <highlight>
   |
   = <note>
   = hint: <suggestion>
```

### Error Levels

| Level | Meaning |
|-------|---------|
| `error` | Must be fixed |
| `warning` | Should be reviewed |
| `note` | Informational |
| `hint` | Suggested fix |

### Example

```
error: Account not opened
  --> ledger.beancount:42:3
   |
42 |   Assets:Unknown  100 USD
   |   ^^^^^^^^^^^^^^
   |
   = hint: add 'open' directive before this transaction
```

## Reference Notation

### Document References

```
See [document-name.md](path/to/document.md)
```

### Section References

```
See [Section Name](#section-name)
```

### External References

```
See [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119)
```

### Cross-References

```
As defined in [Types: Decimal](../types/decimal.md)
```

## Version Notation

### Semantic Versioning

```
MAJOR.MINOR.PATCH

1.0.0  ; First stable release
1.1.0  ; New features, backwards compatible
1.1.1  ; Bug fixes only
2.0.0  ; Breaking changes
```

### Pre-release

```
1.0.0-alpha.1
1.0.0-beta.2
1.0.0-rc.1
```

### Specification Version

```
PTA Standards v1.0
Beancount v3
Ledger v3
```

## Status Markers

### Feature Status

| Marker | Meaning |
|--------|---------|
| **[STABLE]** | Unlikely to change |
| **[EXPERIMENTAL]** | May change |
| **[DEPRECATED]** | Will be removed |
| **[REMOVED]** | No longer supported |

### Implementation Status

| Marker | Meaning |
|--------|---------|
| **[REQUIRED]** | Must implement |
| **[OPTIONAL]** | May implement |
| **[EXTENSION]** | Non-standard |

See [stability-markers.md](stability-markers.md) for details.

## Abbreviations

### Common Abbreviations

| Abbreviation | Meaning |
|--------------|---------|
| PTA | Plain Text Accounting |
| AST | Abstract Syntax Tree |
| BQL | Beancount Query Language |
| EBNF | Extended Backus-Naur Form |
| PEG | Parsing Expression Grammar |
| ISO | International Organization for Standardization |
| UTC | Coordinated Universal Time |

### Currency Codes

ISO 4217 three-letter codes:

```
USD, EUR, GBP, JPY, CHF, ...
```

## Conventions in Examples

### Valid Examples

Prefixed with semicolon comment or shown without marker:

```beancount
; Valid example
2024-01-15 * "Purchase"
  Assets:Checking  -100 USD
  Expenses:Food
```

### Invalid Examples

Marked with `; Invalid` or `; ERROR`:

```beancount
; Invalid: missing narration
2024-01-15 *
  Assets:Checking  100 USD
  Income:Salary
```

### Output Examples

Shown with `; Output:` prefix:

```
; Output:
Assets:Checking     1000.00 USD
Expenses:Food        500.00 USD
```
