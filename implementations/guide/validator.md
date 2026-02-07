# Validator Implementation Guide

This guide covers implementing validation for PTA formats.

## Validation Phases

Validation occurs in distinct phases:

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌─────────┐
│  Parse  │───▶│  Resolve │───▶│  Booking  │───▶│  Check  │
└─────────┘    └──────────┘    └───────────┘    └─────────┘
     │              │               │               │
   Syntax      Includes &       Lots &          Balances &
   Errors      Options        Interpolation     Constraints
```

## Phase 1: Syntax Validation

Handled during parsing:

| Check | Example Error |
|-------|---------------|
| Valid date | `2024-13-01` - invalid month |
| Valid account format | `assets:bank` - must be capitalized |
| Valid number | `1,000.00` - comma not allowed |
| Balanced quotes | `"unclosed` - missing close quote |
| Indentation | Transaction without indented postings |

## Phase 2: Resolution

### Include Resolution

Process include directives:

```
load_with_includes(path):
    content = read(path)
    ast = parse(content)

    for directive in ast:
        if directive is Include:
            included_path = resolve_path(path, directive.path)
            included_ast = load_with_includes(included_path)
            merge(ast, included_ast)

    return ast
```

Validations:
- [ ] Include path exists
- [ ] No circular includes
- [ ] Path is within allowed directories

### Option Processing

Apply options before validation:

```
process_options(directives):
    for opt in directives where opt is Option:
        match opt.name:
            "operating_currency" => set_operating_currencies(opt.value)
            "booking_method" => set_default_booking(opt.value)
            "account_open_date" => set_account_open_date(opt.value)
            ...
```

## Phase 3: Account Validation

### Open/Close Tracking

Track account lifecycle:

```
AccountState = {
    opened: Option<Date>,
    closed: Option<Date>,
    currencies: Set<Currency>,
    booking: BookingMethod,
}

accounts: Map<Account, AccountState>

validate_account_usage(posting, date):
    state = accounts.get(posting.account)

    if state is None and require_open_accounts:
        error("Account not opened", posting.span)

    if state.opened > date:
        error("Account used before open date", posting.span)

    if state.closed and state.closed <= date:
        error("Account used after close date", posting.span)

    if state.currencies and posting.currency not in state.currencies:
        warning("Currency not in account's allowed currencies", posting.span)
```

### Account Hierarchy

Validate account types:

```
validate_account_type(account, posting):
    // Assets and Expenses normally have debits (positive)
    // Liabilities, Equity, Income normally have credits (negative)

    if is_unusual_sign(account.type, posting.amount):
        warning("Unusual sign for account type", posting.span)
```

## Phase 4: Transaction Validation

### Balance Check

Verify transactions balance:

```
validate_transaction_balance(transaction):
    balances: Map<Currency, Decimal> = {}

    for posting in transaction.postings:
        if posting.units:
            balances[posting.units.currency] += posting.units.number

    for (currency, balance) in balances:
        tolerance = get_tolerance(currency)
        if abs(balance) > tolerance:
            error("Transaction does not balance", transaction.span)
            note(f"Residual: {balance} {currency}")
```

### Tolerance Calculation

Calculate allowed rounding tolerance:

```
get_tolerance(currency):
    // Use inferred precision from file
    precision = max_decimal_places_seen.get(currency, 2)

    // Tolerance is half the smallest unit
    return 0.5 * (10 ** -precision)
```

### Interpolation

Fill in missing amounts:

```
interpolate_postings(transaction):
    incomplete = postings.filter(p => p.units is None)

    if incomplete.len() == 0:
        return  // Fully specified

    if incomplete.len() > 1:
        error("Too many postings without amounts", transaction.span)
        return

    // Calculate residual
    residual = -sum(postings.filter(p => p.units).map(p => p.units))

    if residual.currencies().len() > 1:
        error("Cannot interpolate with multiple currencies", incomplete[0].span)
        return

    incomplete[0].units = residual
```

## Phase 5: Booking Validation

### Lot Tracking

Track inventory for each account:

```
Inventory = {
    lots: Map<LotKey, Lot>,
}

LotKey = (Currency, Option<Cost>)

Lot = {
    amount: Decimal,
    cost: Cost,
    acquisition_date: Date,
}

process_posting(posting, inventory):
    if posting.cost:
        // Adding to position
        lot = find_or_create_lot(inventory, posting)
        lot.amount += posting.units.number
    else if posting.units.number < 0:
        // Reducing position - apply booking method
        reduce_inventory(inventory, posting)
```

### Booking Methods

Implement all booking methods:

```
reduce_inventory(inventory, posting, method):
    amount_to_reduce = abs(posting.units.number)

    match method:
        FIFO:
            lots = inventory.lots_sorted_by(lot => lot.acquisition_date, ASC)
        LIFO:
            lots = inventory.lots_sorted_by(lot => lot.acquisition_date, DESC)
        HIFO:
            lots = inventory.lots_sorted_by(lot => lot.cost.number, DESC)
        STRICT:
            lots = inventory.lots_matching(posting.cost_spec)
        NONE:
            // Create negative lot
            return
        AVERAGE:
            // Special handling for average cost
            return reduce_average(inventory, posting)

    for lot in lots:
        if amount_to_reduce <= 0:
            break

        reduction = min(lot.amount, amount_to_reduce)
        lot.amount -= reduction
        amount_to_reduce -= reduction

    if amount_to_reduce > 0:
        error("Insufficient lots for reduction", posting.span)
```

### Cost Matching

Match cost specifications to lots:

```
match_lot(lots, cost_spec):
    candidates = lots.filter(lot =>
        (cost_spec.currency is None or lot.cost.currency == cost_spec.currency) and
        (cost_spec.number is None or lot.cost.number == cost_spec.number) and
        (cost_spec.date is None or lot.acquisition_date == cost_spec.date) and
        (cost_spec.label is None or lot.cost.label == cost_spec.label)
    )

    if candidates.len() == 0:
        error("No matching lot found", cost_spec.span)

    if candidates.len() > 1 and not cost_spec.allows_multiple:
        error("Ambiguous cost specification matches multiple lots", cost_spec.span)

    return candidates
```

## Phase 6: Balance Assertions

### Balance Checks

Validate balance assertions:

```
validate_balance(assertion):
    account = assertion.account
    date = assertion.date

    // Get inventory at START of day (Beancount semantics)
    inventory = compute_inventory(account, date - 1 day)

    actual = inventory.balance_for(assertion.currency)
    expected = assertion.amount.number

    tolerance = get_tolerance(assertion.currency)
    if abs(actual - expected) > tolerance:
        error("Balance assertion failed", assertion.span)
        note(f"Expected: {expected} {assertion.currency}")
        note(f"Actual: {actual} {assertion.currency}")
        note(f"Difference: {actual - expected} {assertion.currency}")
```

### Partial Balance Assertions

Some formats support partial assertions:

```
// Check only specific currency, ignore others
2024-01-15 balance Assets:Bank  100 USD

// Check exact inventory (all currencies must match)
2024-01-15 balance* Assets:Bank  100 USD, 50 EUR
```

## Phase 7: Pad Directives

### Pad Expansion

Expand pad directives into transactions:

```
expand_pad(pad, next_balance):
    inventory = compute_inventory(pad.account, pad.date - 1 day)

    for (currency, expected) in next_balance:
        actual = inventory.balance_for(currency)
        difference = expected - actual

        if difference != 0:
            emit Transaction {
                date: pad.date,
                flag: "P",
                narration: "Padding",
                postings: [
                    Posting { account: pad.account, units: difference currency },
                    Posting { account: pad.source, units: -difference currency },
                ],
            }
```

## Error Severity Levels

Categorize validation issues:

| Level | Description | Action |
|-------|-------------|--------|
| Error | Invalid ledger | Reject |
| Warning | Suspicious but valid | Report |
| Info | Informational | Optional |

```
ValidationResult = {
    errors: Vec<Error>,
    warnings: Vec<Warning>,
    info: Vec<Info>,
}

is_valid(result):
    return result.errors.is_empty()
```

## Error Messages

### Format

Use consistent error formatting:

```
error[E0042]: Transaction does not balance
  --> finances.beancount:142:1
    |
142 | 2024-01-15 * "Groceries"
143 |   Expenses:Food  50.00 USD
144 |   Assets:Cash   -49.00 USD
    |                 ^^^^^^^^^^ residual: -1.00 USD
    |
    = help: add missing amount to a posting or adjust existing amounts
```

### Error Codes

Use structured error codes:

| Code | Category | Description |
|------|----------|-------------|
| E0001-E0099 | Syntax | Parse errors |
| E0100-E0199 | Account | Account lifecycle |
| E0200-E0299 | Balance | Transaction balance |
| E0300-E0399 | Booking | Lot and cost errors |
| E0400-E0499 | Assertion | Balance assertions |
| E0500-E0599 | Include | File resolution |

## Testing Validation

### Unit Tests

Test individual validators:

```
test_balance_check():
    txn = parse_transaction("""
2024-01-15 * "Test"
  Assets:Cash  100 USD
  Expenses:Food  -100 USD
""")
    errors = validate_balance(txn)
    assert errors.is_empty()

test_balance_check_fails():
    txn = parse_transaction("""
2024-01-15 * "Test"
  Assets:Cash  100 USD
  Expenses:Food  -99 USD
""")
    errors = validate_balance(txn)
    assert errors.len() == 1
    assert "does not balance" in errors[0].message
```

### Integration Tests

Test full validation pipeline:

```
test_full_validation():
    ledger = load("test-data/complete.beancount")
    result = validate(ledger)

    assert result.is_valid()
    assert result.warnings.len() < 10
```

### Conformance Tests

Run specification tests:

```bash
# Run validation test suite
python tests/harness/runners/python/runner.py \
    --manifest tests/beancount/v3/manifest.json \
    --suite validation \
    --format tap
```
