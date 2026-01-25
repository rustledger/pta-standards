# Parser Implementation Guide

This guide covers best practices for implementing a PTA parser with error recovery and source location tracking.

## Error Recovery Philosophy

1. **Parse as much as possible** - Don't stop at first error
2. **Produce useful AST** - Partial results are valuable
3. **Accurate locations** - Errors point to exact source positions
4. **Cascading prevention** - Avoid spurious errors from earlier failures

## Source Locations

### Span Type

Track byte offsets for precise source mapping:

```
Span {
    start: usize,  // Byte offset of start
    end: usize,    // Byte offset of end (exclusive)
}
```

Operations:
- `len()` - Length in bytes
- `merge(other)` - Combine two spans
- `text(source)` - Extract text from source

### Source Location

Convert byte offsets to human-readable locations:

```
SourceLocation {
    file: Path,      // File path
    line: u32,       // 1-based line number
    column: u32,     // 1-based column number
    length: u32,     // Length in characters
    span: Span,      // Original byte span
}
```

### Spanned AST Nodes

Every AST node should carry its span:

```
Spanned<T> {
    value: T,
    span: Span,
}
```

This enables precise error reporting for any element.

## Recovery Strategies

### 1. Synchronization Points

Recover at well-defined syntax boundaries:

```
parse_directive():
    try:
        return parse_directive_inner()
    catch error:
        errors.push(error)
        synchronize_to_next_directive()
        return RECOVERED

synchronize_to_next_directive():
    while not at_end():
        skip_to_newline()
        advance_newline()
        if peek_is_date():
            return
```

### 2. Error Productions

Include error cases in the parser:

```
parse_posting():
    account = parse_account()

    try:
        units = parse_amount()
    catch recoverable_error:
        errors.push(warning("Invalid amount, treating as missing"))
        units = None  // Treat as interpolated posting

    // Continue parsing cost, price, etc.
    return Posting { account, units, ... }
```

### 3. Insertion Recovery

Insert missing tokens when safe:

```
parse_transaction():
    date = parse_date()

    if check(STAR) or check(BANG):
        flag = parse_flag()
    else:
        errors.push(warning("Missing transaction flag, assuming '*'"))
        flag = Spanned(Flag.Complete, current_span())

    // Continue...
```

### 4. Deletion Recovery

Skip unexpected tokens:

```
parse_postings():
    postings = []

    while check_indent():
        try:
            postings.push(parse_posting())
        catch error:
            errors.push(error)
            skip_to_newline()  // Skip bad posting

    return postings
```

## Error Message Quality

### Quality Criteria

1. **Specific** - "Expected ')' to close '(' at line 42" not "Syntax error"
2. **Actionable** - Suggest fixes when possible
3. **Located** - Point to exact character
4. **Contextual** - Show surrounding code

### Error Structure

```
ParseError {
    kind: ParseErrorKind,
    message: String,
    span: Span,
    notes: Vec<Note>,
    suggestions: Vec<Suggestion>,
}

Note {
    message: String,
    span: Option<Span>,
}

Suggestion {
    message: String,
    replacement: String,
    span: Span,
}
```

### Example Error Output

```
error[E0001]: Unexpected token
  --> ledger.beancount:42:15
   |
42 |   Assets:Cash  100 $USD
   |               ^^^^
   |               expected amount, found '$'
   |
   = note: currency names cannot start with '$'
   = suggestion: remove the '$' prefix
```

## Source Location Through Transformations

### The Challenge

Directives are transformed through multiple phases:

1. Parse → AST with spans
2. Include expansion → Multiple files merged
3. Interpolation → New amounts added
4. Pad expansion → Synthetic transactions
5. Plugin processing → Arbitrary transformations

Errors in later phases must point to original source.

### Approach 1: Carry Original Spans

```
Amount {
    number: Decimal,
    currency: Currency,
    span: Option<Span>,      // None if synthesized
    origin: Option<Origin>,  // For synthesized values
}

Origin =
    | Interpolated { from_transaction: Span }
    | Padded { from_pad: Span, from_balance: Span }
    | Plugin { plugin_name: String }
```

### Approach 2: Transformation Log

Track all transformations:

```
TransformEntry =
    | Interpolated {
        transaction_span: Span,
        posting_index: usize,
        computed_amount: Amount,
    }
    | PadExpanded {
        pad_span: Span,
        balance_span: Span,
        generated_transaction: Transaction,
    }
    | PluginModified {
        plugin: String,
        original_span: Span,
        description: String,
    }
```

### Include File Tracking

Maintain a source map for merged files:

```
SourceMap {
    files: Vec<SourceFile>,
    offset_map: Vec<(merged_offset, file_id, local_offset)>,
}

SourceFile {
    path: Path,
    content: String,
    start_offset: usize,  // Offset in merged source
}
```

Convert merged offsets to file locations via binary search.

## Error Aggregation

### Collecting Errors

```
ErrorCollector {
    errors: Vec<Error>,
    warnings: Vec<Error>,
    max_errors: usize,
}

methods:
    error(e) - Add error if under limit
    warning(w) - Add warning (no limit)
    should_abort() - True if max_errors reached
    finish() - Return all errors and warnings
```

### Error Deduplication

Avoid duplicates from cascading failures:

```
error_if_new(error):
    if not errors.any(e => e.span.overlaps(error.span)):
        errors.push(error)
```

### Cascading Prevention

Mark tokens as synthetic during recovery:

```
Token {
    kind: TokenKind,
    span: Span,
    is_synthetic: bool,  // True if inserted during recovery
}
```

Skip error reporting for synthetic tokens to prevent cascading.

## Testing Error Recovery

### Recovery Tests

```
test_recovery_missing_flag():
    source = """
2024-01-01 "Deposit"
  Assets:Cash  100 USD
  Income:Salary
"""
    (ledger, errors) = parse_with_recovery(source)

    assert ledger.transactions().count() == 1  // Recovered
    assert errors.any(e => e.message.contains("flag"))

test_recovery_continues_after_error():
    source = """
2024-01-01 * "First"
  Assets:Cash  100 USD
  Income:Salary

2024-01-02 * "Invalid"
  Assets:Cash  not_a_number USD
  Expenses:Food

2024-01-03 * "Third"
  Assets:Cash  50 USD
  Expenses:Food
"""
    (ledger, errors) = parse_with_recovery(source)

    assert ledger.transactions().count() == 2  // First and third
    assert errors.len() >= 1
```

### Location Accuracy Tests

```
test_error_location():
    source = "2024-01-01 * \"Test\"\n  Invalid:Account  100 USD\n"
    (_, errors) = parse_with_recovery(source)

    assert errors[0].location.line == 2
    assert errors[0].location.column == 3
```

## LSP Integration

For editor support, convert errors to LSP diagnostics:

```
Diagnostic {
    range: Range,          // 0-based line/column
    severity: Severity,
    code: String,
    message: String,
    related: Vec<RelatedInformation>,
}

Range {
    start: Position,
    end: Position,
}

Position {
    line: u32,      // 0-based for LSP
    character: u32, // UTF-16 code units
}
```

Note: LSP uses 0-based line numbers and UTF-16 character offsets.
