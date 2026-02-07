# Level 1: Parse Conformance

Level 1 conformance requires correct parsing of valid Beancount syntax and proper rejection of invalid syntax.

## Requirements

### Lexical Analysis

The implementation MUST correctly tokenize:

| Token Type | Examples |
|------------|----------|
| Dates | `2024-01-15`, `2024/01/15` |
| Numbers | `100`, `100.00`, `-50.5`, `1,234.56` |
| Strings | `"Hello"`, `"Escaped \"quote\""` |
| Accounts | `Assets:Checking`, `Expenses:Food:Groceries` |
| Currencies | `USD`, `EUR`, `AAPL`, `BRK.B` |
| Tags | `#travel`, `#project-2024` |
| Links | `^invoice-001`, `^ref-123` |
| Keywords | `open`, `close`, `balance`, `txn`, etc. |
| Operators | `@`, `@@`, `{`, `}`, `{{`, `}}` |
| Comments | `; comment text` |

### Syntax Parsing

The implementation MUST parse all directive types:

| Directive | Minimum Support |
|-----------|-----------------|
| `open` | Account, optional currencies |
| `close` | Account |
| `balance` | Account, amount |
| `pad` | Two accounts |
| `commodity` | Currency |
| `price` | Currency, amount |
| `event` | Type, value |
| `note` | Account, string |
| `document` | Account, path |
| `query` | Name, query string |
| `custom` | Type, values |
| `option` | Name, value |
| `plugin` | Module, optional config |
| `include` | Path |
| Transaction | Flag, payee, narration, postings |

### Transaction Parsing

Transactions MUST be parsed with:

| Component | Requirement |
|-----------|-------------|
| Date | Required |
| Flag | `*`, `!`, `txn`, or omitted |
| Payee | Optional quoted string |
| Narration | Optional quoted string |
| Tags | Zero or more `#tag` |
| Links | Zero or more `^link` |
| Metadata | Key-value pairs |
| Postings | Two or more |

### Posting Parsing

Postings MUST be parsed with:

| Component | Requirement |
|-----------|-------------|
| Account | Required |
| Amount | Optional (one may be elided) |
| Cost spec | `{...}` or `{{...}}` |
| Price annotation | `@` or `@@` |
| Metadata | Indented key-value pairs |

### Error Handling

The implementation MUST:

1. **Detect syntax errors** in invalid input
2. **Report error location** (line and column)
3. **Provide error message** describing the issue
4. **Recover from errors** to continue parsing

### Error Reporting Format

Errors SHOULD include:

```
ERROR: <message>
  --> <file>:<line>:<column>
   |
<n> | <source line>
   |   ^^^^ <indicator>
   |
   = <hint or explanation>
```

## Test Suite

### Required Tests

| Suite | Purpose | Minimum Pass Rate |
|-------|---------|-------------------|
| `syntax/valid` | Valid syntax parses | 100% |
| `syntax/invalid` | Invalid syntax rejected | 100% |

### Test Categories

#### Valid Syntax Tests

- Empty file
- Comments only
- All directive types
- Complex transactions
- Unicode content
- Edge cases

#### Invalid Syntax Tests

- Malformed dates
- Unterminated strings
- Invalid account names
- Missing required components
- Structural errors

## Validation Behavior

Level 1 implementations:
- MUST accept all syntactically valid input
- MUST reject syntactically invalid input
- MAY skip semantic validation
- MAY produce warnings for suspicious constructs

## Non-Requirements

Level 1 does NOT require:
- Balance checking
- Account lifecycle validation
- Currency constraint enforcement
- Query execution
- Plugin support

## Example Implementation

```python
def parse(source: str) -> ParseResult:
    """
    Level 1 compliant parser.

    Returns:
        ParseResult with directives and syntax errors
    """
    tokens = tokenize(source)
    ast = build_ast(tokens)
    return ParseResult(
        directives=ast.directives,
        errors=ast.syntax_errors
    )
```

## Certification

To achieve Level 1:

1. Run syntax test suites
2. Achieve 100% pass rate
3. Document any implementation-specific behavior
4. Submit certification

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Rejecting valid Unicode | Support UTF-8 fully |
| Number parsing edge cases | Handle all formats |
| Escape sequence handling | Support `\"`, `\\`, `\n` |
| Comment preservation | Parse but may discard |
| Whitespace sensitivity | Follow indentation rules |

## See Also

- [Test Suite](/tests/beancount/v3/syntax/)
- [Lexical Specification](/formats/beancount/v3/spec/lexical.md)
- [Syntax Specification](/formats/beancount/v3/spec/syntax.md)
