# Level 2: Validate Conformance

Level 2 conformance requires Level 1 parsing plus semantic validation of the parsed directives.

## Requirements

### Level 1 Prerequisites

All Level 1 requirements MUST be met.

### Account Lifecycle Validation

The implementation MUST verify:

| Rule | Validation |
|------|------------|
| Open before use | Accounts must be opened before postings |
| Single open | Account cannot be opened twice |
| Close after open | Close date must be after open date |
| No post-close postings | No postings after close date |
| Close only opened | Cannot close unopened account |

### Transaction Balance Validation

The implementation MUST verify:

| Rule | Validation |
|------|------------|
| Balance to zero | Sum of posting weights = 0 |
| Tolerance handling | Within commodity-specific tolerance |
| Multi-currency | Each currency balances independently |
| Cost vs price | Use correct weight calculation |

### Currency Constraint Validation

The implementation MUST verify:

| Rule | Validation |
|------|------------|
| Account currencies | Only declared currencies allowed |
| Unconstrained accounts | Any currency if not specified |
| Commodity declarations | Optional but checked if present |

### Balance Assertion Validation

The implementation MUST verify:

| Rule | Validation |
|------|------------|
| Assertion accuracy | Actual balance matches expected |
| Tolerance handling | Within specified or default tolerance |
| Currency matching | Correct commodity checked |
| Date ordering | Assertion after relevant transactions |

### Duplicate Detection

The implementation SHOULD detect:

| Duplicate Type | Action |
|----------------|--------|
| Duplicate open | Error |
| Duplicate close | Error |
| Duplicate transaction | Warning (optional) |

### Error Codes

Level 2 implementations MUST report semantic errors with codes:

| Error Code | Description |
|------------|-------------|
| E1001 | Account not opened |
| E1002 | Account already opened |
| E1003 | Account not open at posting date |
| E1004 | Account already closed |
| E1005 | Transaction does not balance |
| E1006 | Currency not allowed for account |
| E1007 | Balance assertion failed |
| E1008 | Invalid balance tolerance |

## Test Suite

### Required Tests

| Suite | Purpose | Minimum Pass Rate |
|-------|---------|-------------------|
| `syntax/valid` | Valid syntax parses | 100% |
| `syntax/invalid` | Invalid syntax rejected | 100% |
| `validation` | Semantic validation | 95% |

### Validation Test Categories

- Account lifecycle errors
- Unbalanced transactions
- Currency constraint violations
- Balance assertion failures
- Metadata validation

## Validation Order

Validation SHOULD proceed in this order:

1. Parse all directives
2. Build account registry
3. Sort directives by date
4. Validate each directive chronologically
5. Collect all errors

## Tolerance Calculation

Default tolerance per commodity:

```
tolerance = 0.5 × 10^(-display_precision)
```

| Commodity | Display Precision | Tolerance |
|-----------|-------------------|-----------|
| USD | 2 | 0.005 |
| BTC | 8 | 0.000000005 |
| AAPL | 4 | 0.00005 |

## Example Implementation

```python
def validate(directives: List[Directive]) -> List[Error]:
    """
    Level 2 compliant validator.
    """
    errors = []
    accounts = {}

    for directive in sorted(directives, key=lambda d: d.date):
        if isinstance(directive, Open):
            if directive.account in accounts:
                errors.append(Error(E1002, "Account already opened"))
            accounts[directive.account] = directive

        elif isinstance(directive, Transaction):
            for posting in directive.postings:
                if posting.account not in accounts:
                    errors.append(Error(E1001, "Account not opened"))

            if not is_balanced(directive):
                errors.append(Error(E1005, "Transaction does not balance"))

    return errors
```

## Certification

To achieve Level 2:

1. Achieve Level 1 certification
2. Run validation test suite
3. Achieve 95% pass rate
4. Document any deviations
5. Submit certification

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Wrong balance calculation | Use weight, not units |
| Tolerance too strict | Use commodity-specific tolerance |
| Missing error context | Include related transactions |
| Wrong directive order | Sort by date before validating |

## Non-Requirements

Level 2 does NOT require:
- Query execution
- Plugin support
- Pad expansion
- Booking method support

## See Also

- [Test Suite](/tests/beancount/v3/validation/)
- [Validation Specification](/formats/beancount/v3/spec/validation/)
- [Error Codes](/tooling/errors/codes/beancount.md)
