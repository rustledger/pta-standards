# Assert Directive

The `assert` directive validates conditions and stops processing on failure.

## Syntax

```
assert EXPRESSION
```

## Comparison with Check

| Directive | On Failure |
|-----------|------------|
| `check` | Warning, continues |
| `assert` | Error, stops |

## Examples

### Basic Assertion

```ledger
assert total(Assets) > 0
```

### Balance Assertion

```ledger
assert Assets:Checking >= $0
```

### Complex Expression

```ledger
assert total(Assets) >= total(Liabilities)
```

## Use Cases

### Prevent Overdraft

```ledger
assert Assets:Checking >= $0

; This transaction would fail:
2024/01/15 Overspend
    Expenses:Shopping    $1000.00
    Assets:Checking              ; Would go negative
```

### Net Worth Check

```ledger
assert total(Assets) - total(Liabilities) > 0
```

### Category Constraints

```ledger
assert total(Expenses:Entertainment) <= $500
```

## Expression Syntax

### Account Totals

```ledger
assert total(Assets) > $0
assert total(Liabilities) < $100000
assert total(Income) > total(Expenses)
```

### Specific Account

```ledger
assert Assets:Checking == $1500
assert Liabilities:CreditCard >= $-5000
```

### Comparisons

```ledger
assert account == $1000     ; Equal
assert account != $0        ; Not equal
assert account >= $100      ; Greater or equal
assert account <= $5000     ; Less or equal
assert account > $0         ; Greater than
assert account < $10000     ; Less than
```

### Logical Operators

```ledger
assert account >= $0 and account <= $10000
assert total(Assets) > 0 or total(Income) > 0
assert not (account < $0)
```

## Inline Balance Assertions

In postings:

```ledger
2024/01/15 Transaction
    Assets:Checking    $100 = $1500
    ; Assert Checking balance is $1500 after posting
    Income:Salary
```

Double equals for total assertion:

```ledger
2024/01/15 Transaction
    Assets:Checking    $100 == $1500
    ; Assert TOTAL balance (all commodities) is $1500
    Income:Salary
```

## Conditional Assertions

Using expressions:

```ledger
; Only assert if account exists and has transactions
assert (has_tag("verified") and account >= $0) or not has_tag("verified")
```

## Error Messages

Failed assertions produce detailed errors:

```
Error: Assertion failed at journal.ledger:25
  assert Assets:Checking >= $0

  Expected: Assets:Checking >= $0.00
  Actual:   Assets:Checking = $-150.00

Processing stopped.
```

## Placement

### At File Level

```ledger
; Check at end of file processing
assert total(Assets) > 0
```

### Between Transactions

```ledger
2024/01/15 First transaction
    Expenses:A    $50
    Assets:Checking

assert Assets:Checking >= $0

2024/01/16 Second transaction
    Expenses:B    $50
    Assets:Checking
```

### In Transactions

```ledger
2024/01/15 Transaction
    Expenses:Food    $50
    Assets:Checking  $-50 = $1000    ; Inline assertion
```

## Built-in Functions

### total()

Sum of account balances:

```ledger
assert total(Assets) > $0
assert total(Expenses:Food) < $1000
```

### abs()

Absolute value:

```ledger
assert abs(account) < $1000
```

### has_tag()

Check for tag presence:

```ledger
assert has_tag("verified") or amount < $100
```

### any() / all()

Collection checks:

```ledger
assert all(Expenses, amount >= 0)
assert any(Assets, amount > $1000)
```

## Account Subdirective

Assert within account definition:

```ledger
account Assets:Checking
    assert amount >= $0

account Liabilities:CreditCard
    assert amount >= $-5000
```

## Validation Timing

Assertions are checked:
1. After each transaction (inline assertions)
2. At the specified date (dated assertions)
3. At end of file (file-level assertions)

## Disabling Assertions

```bash
# Skip assertions
ledger --no-assertions -f journal.ledger balance
```

## Best Practices

1. **Use assert for critical invariants** that should never be violated
2. **Use check for warnings** that may need review
3. **Place early** to catch problems sooner
4. **Document why** the assertion exists
5. **Be specific** in error messages

## Example: Complete Validation

```ledger
; ===== Account Constraints =====

account Assets:Checking
    assert amount >= $0

account Assets:Savings
    assert amount >= $0

account Liabilities:CreditCard
    assert amount >= $-10000

; ===== Global Constraints =====

; Net worth must be positive
assert total(Assets) > total(Liabilities)

; Emergency fund requirement
assert Assets:Savings >= $1000

; ===== Transactions =====

2024/01/15 Paycheck
    Assets:Checking    $3000
    Income:Salary

2024/01/15 Save
    Assets:Savings     $500
    Assets:Checking

2024/01/20 Rent
    Expenses:Housing    $1500
    Assets:Checking

; Verify end-of-month state
2024/01/31 assert Assets:Checking >= $500
```

## See Also

- [Check Directive](check.md)
- [Value Expressions](../../expressions/spec.md)
- [Transaction Directive](transaction.md)
