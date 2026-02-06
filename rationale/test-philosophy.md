# Test Philosophy

This document explains our approach to testing and conformance verification.

## Context

Testing ensures specifications are implementable and implementations are correct. Different testing approaches serve different purposes.

## Core Principles

### 1. Specification-Driven Testing

Tests derive from specifications, not implementations:

```
Specification → Test Cases → Implementation Verification
```

Not:

```
Implementation → Extract Tests → Retrofit Specification
```

### 2. Format-Agnostic Test Harness

The test harness works with any format:

```yaml
# test-case.yaml
input: |
  2024-01-15 * "Test"
    Assets:Checking  100 USD
    Expenses:Food

expected:
  type: transaction
  date: 2024-01-15
  postings:
    - account: Assets:Checking
      amount: { number: "100", commodity: "USD" }
```

The harness invokes format-specific parsers and compares results.

### 3. Layered Testing

Tests are organized by conformance level:

| Level | Tests |
|-------|-------|
| Level 1: Parse | Syntax acceptance/rejection |
| Level 2: Validate | Semantic validation |
| Level 3: Query | Query language |
| Level 4: Full | Complete specification |

Implementations can claim partial conformance.

### 4. Positive and Negative Tests

Both valid and invalid inputs are tested:

**Positive test** (should succeed):
```yaml
input: |
  2024-01-01 open Assets:Checking
  2024-01-15 * "Valid"
    Assets:Checking  100 USD
    Income:Salary

expect: success
```

**Negative test** (should fail):
```yaml
input: |
  2024-01-15 * "Account not opened"
    Assets:Unknown  100 USD
    Income:Salary

expect:
  error: ACCOUNT_NOT_OPENED
  location: { line: 2, column: 3 }
```

## Test Categories

### Syntax Tests

Verify parser accepts/rejects input correctly:

```yaml
category: syntax
tests:
  - name: valid-transaction
    input: "2024-01-15 * \"Test\"\n  Account  100 USD\n  Other\n"
    expect: parse-success

  - name: invalid-date
    input: "2024-13-45 * \"Bad date\"\n"
    expect: parse-error
```

### Semantic Tests

Verify validation rules:

```yaml
category: validation
tests:
  - name: transaction-balances
    input: |
      2024-01-01 open Assets:A
      2024-01-01 open Assets:B
      2024-01-15 * "Balanced"
        Assets:A  100 USD
        Assets:B -100 USD
    expect: valid

  - name: transaction-unbalanced
    input: |
      2024-01-01 open Assets:A
      2024-01-01 open Assets:B
      2024-01-15 * "Unbalanced"
        Assets:A  100 USD
        Assets:B  -50 USD
    expect:
      error: TRANSACTION_NOT_BALANCED
```

### Behavioral Tests

Verify processing behavior:

```yaml
category: behavior
tests:
  - name: fifo-booking
    setup: |
      2024-01-01 open Assets:Stock AAPL "FIFO"
      2024-01-15 * "Buy lot 1"
        Assets:Stock  10 AAPL {100 USD}
        Assets:Cash
      2024-01-20 * "Buy lot 2"
        Assets:Stock  10 AAPL {110 USD}
        Assets:Cash
    action: |
      2024-02-01 * "Sell"
        Assets:Stock  -5 AAPL {}
        Assets:Cash
    expect:
      reduced_lot: { cost: "100 USD", date: "2024-01-15" }
```

### Query Tests

Verify query language:

```yaml
category: query
tests:
  - name: select-all-transactions
    setup: |
      ; ... ledger setup ...
    query: "SELECT date, narration FROM transactions"
    expect:
      columns: [date, narration]
      rows:
        - ["2024-01-15", "First"]
        - ["2024-01-20", "Second"]
```

## Test Organization

### Directory Structure

```
tests/
├── harness/              # Test runner implementation
├── fixtures/             # Shared test data
│   ├── minimal.beancount
│   └── comprehensive.beancount
├── syntax/               # Parser tests
│   ├── transactions/
│   ├── directives/
│   └── edge-cases/
├── validation/           # Semantic validation tests
│   ├── accounts/
│   ├── balance/
│   └── booking/
├── query/                # BQL tests
└── integration/          # End-to-end tests
```

### Test Naming

```
<category>-<feature>-<case>.yaml

syntax-transaction-basic.yaml
syntax-transaction-with-metadata.yaml
validation-balance-within-tolerance.yaml
validation-balance-exceeds-tolerance.yaml
```

## Error Testing

### Error Identification

Tests specify expected error codes:

```yaml
expect:
  error: E1001  # Or symbolic name: ACCOUNT_NOT_OPENED
```

### Error Location

Tests verify error locations:

```yaml
expect:
  error: SYNTAX_ERROR
  location:
    line: 5
    column: 10
    # Optionally:
    file: "included.beancount"
```

### Error Messages

Error message text is NOT tested (implementation freedom), but error codes ARE tested (specification compliance).

## Differential Testing

### Cross-Implementation Testing

Compare implementations against each other:

```
Input File → Implementation A → Output A
           → Implementation B → Output B
           → Reference Impl   → Expected

Compare: Output A ≈ Output B ≈ Expected
```

### Cross-Format Testing

Test conversions preserve semantics:

```
Beancount File → Convert to Ledger → Convert back → Compare
```

## Fuzz Testing

### Grammar-Based Fuzzing

Generate random valid inputs from grammar:

```python
def generate_transaction():
    date = random_date()
    flag = random.choice(['*', '!'])
    narration = random_string()
    postings = [generate_posting() for _ in range(random.randint(2, 5))]
    # Ensure balance
    balance_postings(postings)
    return Transaction(date, flag, narration, postings)
```

### Mutation Fuzzing

Mutate valid inputs to find edge cases:

```python
def mutate(input_bytes):
    # Flip bits, insert/delete bytes, etc.
    return mutated_bytes
```

### Property Testing

Verify properties hold for generated inputs:

```python
@given(transactions())
def test_parse_unparse_roundtrip(txn):
    text = unparse(txn)
    parsed = parse(text)
    assert parsed == txn
```

## Coverage

### Specification Coverage

Track which specification sections have tests:

```
spec/directives/transaction.md
  ✓ Basic syntax (15 tests)
  ✓ Metadata (8 tests)
  ✓ Tags and links (12 tests)
  ✗ Edge case: empty narration (0 tests)  # Gap!
```

### Code Coverage

Implementation code coverage is the implementer's responsibility, not the specification's.

### Grammar Coverage

Track which grammar productions are tested:

```
transaction: 100% (all alternatives)
posting: 95% (missing: posting with only account)
amount: 100%
```

## Conformance Testing

### Self-Certification

Implementations run the test suite and report results:

```yaml
implementation: my-parser
version: 1.0.0
format: beancount-v3
results:
  level-1-parse: 100% (500/500)
  level-2-validate: 98% (490/500)
  level-3-query: 0% (not implemented)
```

### Test Versioning

Test suite versions align with specification versions:

```
tests/v3.0/  # Tests for specification v3.0
tests/v3.1/  # Tests for specification v3.1
```

## Implementation Guidance

### For Test Authors

1. Derive tests from specification
2. Include edge cases
3. Test both success and failure
4. Document test purpose

### For Implementers

1. Run full test suite
2. Report conformance level
3. Contribute tests for gaps found
4. Don't special-case tests

## Consequences

### Benefits

1. **Specification validation** - Tests verify spec is implementable
2. **Implementation verification** - Tests verify correctness
3. **Regression prevention** - Tests catch breakage
4. **Documentation** - Tests show expected behavior
5. **Interoperability** - Shared tests enable compatibility

### Costs

1. **Maintenance** - Tests must track spec changes
2. **Coverage gaps** - Some cases may be missed
3. **Test complexity** - Harness development effort

## References

- [Test Harness](../tests/harness/README.md) - Test runner documentation
- [Conformance Levels](../conformance/levels/overview.md) - Level definitions
- [Fuzzing](../tests/fuzzing/README.md) - Fuzz testing approach
