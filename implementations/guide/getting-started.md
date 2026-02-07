# Getting Started

This guide helps you start implementing a PTA specification.

## Choosing a Scope

Before starting, decide what you're building:

| Goal | Scope | Effort |
|------|-------|--------|
| Syntax highlighting | Lexer only | Days |
| Editor support | Parser + basic validation | Weeks |
| CLI tool | Full implementation | Months |
| Alternative to reference | Full + optimizations | Months-Years |

## Recommended Approach

### Phase 1: Lexer

Start with lexical analysis:

1. Tokenize the input into tokens
2. Handle all valid lexemes
3. Report lexical errors with positions
4. Build a test suite from spec examples

Key tokens to handle:

| Token | Example | Notes |
|-------|---------|-------|
| DATE | `2024-01-15` | ISO format |
| ACCOUNT | `Assets:Bank:Checking` | Colon-separated |
| CURRENCY | `USD`, `AAPL` | All caps |
| NUMBER | `123.45`, `-100` | Signed decimals |
| STRING | `"Description"` | Double-quoted |
| FLAG | `*`, `!`, `txn` | Transaction flags |

### Phase 2: Parser

Build the syntax tree:

1. Parse all directive types
2. Implement error recovery
3. Track source locations
4. Produce a clean AST

Start with these directives:

```
1. open / close - Account lifecycle
2. commodity - Currency definitions
3. transaction - The core directive
4. balance - Balance assertions
5. pad - Balance padding
6. note / document - Documentation
7. option / plugin - Configuration
8. include - File inclusion
```

### Phase 3: Validation

Add semantic analysis:

1. Balance checking per transaction
2. Account open/close validation
3. Booking and lot tracking
4. Interpolation (missing amounts)

See [Validator Guide](validator.md) for details.

### Phase 4: Query/Reports

Add query capabilities:

1. Transaction filtering
2. Balance computation
3. Report generation
4. BQL support (for Beancount)

## Architecture Overview

Typical implementation structure:

```
                    ┌──────────┐
                    │  Source  │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │  Lexer   │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │  Parser  │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │   AST    │
                    └────┬─────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐    ┌─────▼────┐    ┌──────▼─────┐
   │Validator │    │ Booking  │    │ Includes   │
   └────┬─────┘    └─────┬────┘    └──────┬─────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                    ┌────▼─────┐
                    │  Ledger  │
                    └────┬─────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐    ┌─────▼────┐    ┌──────▼─────┐
   │  Query   │    │ Reports  │    │  Export    │
   └──────────┘    └──────────┘    └────────────┘
```

## Data Types

### Core Types

Define these fundamental types:

```
Date = { year: u16, month: u8, day: u8 }

Decimal = arbitrary-precision decimal number

Currency = interned string, uppercase

Account = {
    type: AccountType,   // Assets, Liabilities, Equity, Income, Expenses
    components: [String], // ["Bank", "Checking"]
}

Amount = {
    number: Decimal,
    currency: Currency,
}
```

### Position and Inventory

For tracking holdings:

```
Cost = {
    number: Decimal,
    currency: Currency,
    date: Option<Date>,
    label: Option<String>,
}

Position = {
    units: Amount,
    cost: Option<Cost>,
}

Inventory = Map<(Currency, Option<Cost>), Position>
```

### Directives

Core directive types:

```
Directive =
    | Open { date, account, currencies, booking }
    | Close { date, account }
    | Commodity { date, currency, metadata }
    | Transaction { date, flag, payee, narration, postings, tags, links }
    | Balance { date, account, amount }
    | Pad { date, account, source_account }
    | Note { date, account, comment }
    | Document { date, account, path }
    | Event { date, type, description }
    | Price { date, currency, amount }
    | Option { key, value }
    | Plugin { name, config }
    | Include { path }
    | Custom { date, type, values }

Posting = {
    account: Account,
    units: Option<Amount>,
    cost: Option<CostSpec>,
    price: Option<Amount>,
    flag: Option<Flag>,
    metadata: Metadata,
}
```

## Testing Strategy

### Unit Tests

Test each component independently:

```
test_lexer_date():
    tokens = lex("2024-01-15")
    assert tokens[0].kind == DATE
    assert tokens[0].value == "2024-01-15"

test_parser_transaction():
    ast = parse("""
2024-01-15 * "Test"
  Assets:Cash  100 USD
  Equity:Opening-Balances
""")
    assert ast.transactions.len() == 1
```

### Conformance Tests

Use the specification test suite:

```bash
# Run conformance tests
python tests/harness/runners/python/runner.py \
    --manifest tests/beancount/v3/manifest.json \
    --format tap
```

### Fuzz Testing

Test with random input:

```
for input in generate_random_inputs():
    try:
        parse(input)
    catch:
        # Crashes are bugs, errors are expected
        verify_no_crash()
```

## Common Pitfalls

### 1. Decimal Precision

**Wrong:** Using float64 for numbers.

**Right:** Use arbitrary-precision decimals.

```
# Float loses precision
0.1 + 0.2 == 0.30000000000000004  # Wrong!

# Decimal preserves precision
Decimal("0.1") + Decimal("0.2") == Decimal("0.3")  # Correct
```

### 2. Date-Time Handling

**Wrong:** Using timestamps for dates.

**Right:** Use date-only types without time zones.

```
# Dates in ledgers are calendar dates, not instants
2024-01-15  # This is a date, not a datetime
```

### 3. Account Name Encoding

**Wrong:** Treating account names as ASCII.

**Right:** Support UTF-8 account names.

```
; Valid account names
Assets:銀行:普通預金
Expenses:カフェ
```

### 4. Balance Assertion Timing

**Wrong:** Checking balance at end of day.

**Right (Beancount):** Check balance at START of day.

```
2024-01-15 txn "Deposit"
  Assets:Cash  100 USD
  Income:Salary

; This checks balance BEFORE the transaction above
2024-01-15 balance Assets:Cash  0 USD  ; Fails!

; Check on next day instead
2024-01-16 balance Assets:Cash  100 USD  ; Passes
```

### 5. Interpolation Edge Cases

**Wrong:** Simple subtraction for missing amount.

**Right:** Handle multiple currencies and costs.

```
2024-01-15 * "Multi-currency"
  Assets:Cash        100 USD
  Assets:Bank       -100 EUR
  Expenses:Fees          ; Must interpolate correctly
```

## Next Steps

1. Read the [Parser Guide](parser.md) for error recovery
2. Read the [Validator Guide](validator.md) for semantic checks
3. Review [Performance Guide](performance.md) for optimization
4. Run the conformance test suite
5. Join the community for help

## Resources

- [Specification documents](../../formats/) - Formal grammar and semantics
- [Test suite](../../tests/) - Conformance tests
- [Reference implementations](../registry.json) - Existing implementations
- [Rationale](../../rationale/) - Design decisions explained
