# Check Directive

The `check` directive (also `assert`) validates conditions in the ledger.

## Syntax

```
check EXPRESSION
assert EXPRESSION
```

Or within a transaction:

```
2024/01/15 Transaction
    Account    $100 = $500  ; Balance assertion
```

## Balance Assertions

### After Posting

Assert balance after a posting:

```ledger
2024/01/15 Deposit
    Assets:Checking    $100.00 = $1500.00
    Income:Salary
```

### Standalone Check

```ledger
2024/01/15 check Assets:Checking == $1500.00
```

## Examples

### Basic Balance Check

```ledger
2024/01/01 Opening
    Assets:Checking    $1000.00
    Equity:Opening

2024/01/15 Deposit
    Assets:Checking    $500.00 = $1500.00
    ; Assert balance is exactly $1500 after this posting
    Income:Salary
```

### Monthly Reconciliation

```ledger
; End of month check
2024/01/31 check Assets:Checking >= $1000.00
```

### Expression Checks

```ledger
; Check total assets
check total(Assets) > 0

; Check no negative expenses
check all(Expenses, amount >= 0)
```

## Check vs Assert

### check

Produces a warning if false:

```ledger
check Assets:Checking == $1000
; Warning: check failed, but processing continues
```

### assert

Produces an error if false:

```ledger
assert Assets:Checking == $1000
; Error: assertion failed, processing stops
```

## Inline Balance Assertions

### Single Commodity

```ledger
2024/01/15 Transaction
    Assets:Checking    $100 = $1500
    ; After this posting, Checking = $1500
    Expenses:Food
```

### Total Assertion

```ledger
2024/01/15 Transaction
    Assets:Checking    $100 == $1500
    ; Double = means "total balance" (all commodities)
    Expenses:Food
```

## Expression Syntax

### Comparison Operators

```ledger
check account == $1000     ; Equal
check account != $0        ; Not equal
check account >= $100      ; Greater or equal
check account <= $5000     ; Less or equal
check account > $0         ; Greater than
check account < $10000     ; Less than
```

### Logical Operators

```ledger
check account >= $100 and account <= $1000
check account < $0 or account > $10000
check not (account == $0)
```

### Functions

```ledger
check total(Assets) > total(Liabilities)
check abs(account) < $1000
check any(Expenses:Food, amount > $100)
```

## Partial Balance Assertions

### Commodity-Specific

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 AAPL = 50 AAPL
    ; Assert 50 AAPL (ignoring USD balance)
    Assets:Checking    $-1500
```

### Subaccount Assertion

```ledger
2024/01/15 check Assets:Bank =* $5000
; =* includes subaccounts
```

## Timing

Assertions are checked at the date specified:

```ledger
2024/01/15 check Assets:Checking == $1000
; Checked using balance as of 2024/01/15
```

## Error Messages

Failed assertions produce descriptive errors:

```
Error: Assertion failed on line 25:
  check Assets:Checking == $1000
  Actual balance: $950.00
  Expected: $1000.00
  Difference: $50.00
```

## Use Cases

### Reconciliation

```ledger
; After reconciling with bank statement
2024/01/31 check Assets:Checking == $2543.87
```

### Data Validation

```ledger
; Ensure expenses never go negative
assert all(Expenses, amount >= 0)

; Ensure assets always positive
assert total(Assets) > 0
```

### Running Balance

```ledger
2024/01/01 Opening
    Assets:Checking    $1000 = $1000
    Equity:Opening

2024/01/15 Expense
    Expenses:Food    $50
    Assets:Checking        = $950

2024/01/20 Deposit
    Assets:Checking    $500 = $1450
    Income:Salary
```

## Command Line Options

### Strict Mode

```bash
ledger --strict -f journal.ledger
# Treats check as assert
```

### Pedantic Mode

```bash
ledger --pedantic -f journal.ledger
# Additional validation checks
```

## Best Practices

1. **Check at reconciliation** - After reviewing bank statements
2. **Use assert for critical** - Things that should never fail
3. **Use check for warnings** - Things to review
4. **Document expected values** - Comment why
5. **Regular intervals** - Monthly, quarterly checks

## Example: Monthly Reconciliation

```ledger
; === January 2024 ===

2024/01/05 Grocery Store
    Expenses:Food    $150.00
    Assets:Checking

2024/01/15 Paycheck
    Assets:Checking    $3000.00
    Income:Salary

2024/01/20 Rent
    Expenses:Housing:Rent    $1500.00
    Assets:Checking

; Reconciled with bank statement 2024/01/31
2024/01/31 check Assets:Checking == $4850.00

; === February 2024 ===
; ...
```

## See Also

- [Transaction Directive](transaction.md)
- [Value Expressions](../expressions/spec.md)
