# Beancount Error Codes (E1xxx)

These error codes are specific to Beancount format.

## Account Errors (E11xx)

### E1101: Account Not Opened

An account was used before being opened.

**Message**: `Account '{account}' not opened`

**Example**:
```beancount
2024-01-15 * "Deposit"
  Assets:Checking  100 USD  ; Error: not opened
  Income:Salary
```

**Fix**: Add an `open` directive before first use:
```beancount
2024-01-01 open Assets:Checking USD
```

---

### E1102: Account Already Opened

An account was opened more than once.

**Message**: `Account '{account}' already opened on {date}`

**Example**:
```beancount
2024-01-01 open Assets:Checking
2024-02-01 open Assets:Checking  ; Error: duplicate
```

**Fix**: Remove the duplicate `open` directive.

---

### E1103: Account Already Closed

A posting references an account after it was closed.

**Message**: `Account '{account}' closed on {date}`

**Example**:
```beancount
2024-06-30 close Assets:Old

2024-07-15 * "Late posting"
  Assets:Old  100 USD  ; Error: account closed
  Income:Salary
```

**Fix**: Use posting date before close date, or reopen the account.

---

### E1104: Account Never Opened

Attempted to close an account that was never opened.

**Message**: `Cannot close account '{account}': never opened`

**Fix**: Ensure the account is opened before closing.

---

### E1105: Invalid Account Root

Account name doesn't start with a valid root.

**Message**: `Invalid account root '{root}', expected one of: Assets, Liabilities, Equity, Income, Expenses`

**Fix**: Use a valid account type as the first component.

---

### E1106: Currency Not Allowed

A posting uses a currency not allowed for the account.

**Message**: `Currency '{currency}' not allowed for account '{account}'`

**Example**:
```beancount
2024-01-01 open Assets:Checking USD

2024-01-15 * "Deposit"
  Assets:Checking  100 EUR  ; Error: only USD allowed
  Income:Salary
```

**Fix**: Use an allowed currency or update the `open` directive.

---

## Balance Errors (E12xx)

### E1201: Transaction Does Not Balance

The sum of posting weights is not zero.

**Message**: `Transaction does not balance: residual is {amount}`

**Example**:
```beancount
2024-01-15 * "Unbalanced"
  Assets:Checking  100 USD
  Expenses:Food     50 USD  ; Missing 50 USD
```

**Fix**: Ensure all postings sum to zero.

---

### E1202: Balance Assertion Failed

A balance assertion did not match the actual balance.

**Message**: `Balance assertion failed: expected {expected}, actual {actual}`

**Example**:
```beancount
2024-01-31 balance Assets:Checking 1000 USD
; Actual balance is 950 USD
```

**Fix**: Correct the assertion or find the missing transaction.

---

### E1203: Multiple Elided Amounts

More than one posting has an elided amount.

**Message**: `Only one posting may have an elided amount`

**Example**:
```beancount
2024-01-15 * "Invalid"
  Assets:Checking
  Expenses:Food     ; Both elided - error
```

**Fix**: Provide amounts for all but one posting.

---

### E1204: Cannot Infer Amount

The elided amount cannot be computed.

**Message**: `Cannot infer amount: multiple currencies without price`

**Fix**: Provide explicit amounts or prices.

---

### E1205: Tolerance Exceeded

The balance residual exceeds the allowed tolerance.

**Message**: `Residual {residual} exceeds tolerance {tolerance}`

**Fix**: Correct the amounts or adjust tolerance.

---

## Booking Errors (E13xx)

### E1301: No Matching Lot

No lot matches the reduction specification.

**Message**: `No lot matches cost specification {spec}`

**Example**:
```beancount
2024-03-15 * "Sell"
  Assets:Stock  -10 AAPL {999 USD}  ; No lot at this cost
  Assets:Cash    9990 USD
```

**Fix**: Use correct cost specification or `{*}` for auto-match.

---

### E1302: Ambiguous Lot

Multiple lots match the reduction specification.

**Message**: `Ambiguous reduction: {count} lots match`

**Fix**: Provide more specific cost specification (date, label, or exact cost).

---

### E1303: Insufficient Units

Not enough units in lot to reduce.

**Message**: `Insufficient units: lot has {available}, need {requested}`

**Fix**: Reduce the quantity or split across lots.

---

### E1304: Invalid Booking Method

The specified booking method is not valid.

**Message**: `Invalid booking method '{method}'`

**Valid methods**: STRICT, FIFO, LIFO, HIFO, AVERAGE, NONE

**Fix**: Use a valid booking method.

---

### E1305: Cost Required

A position requires cost basis but none was provided.

**Message**: `Cost required for commodity '{commodity}' in account '{account}'`

**Fix**: Add cost specification: `10 AAPL {150 USD}`.

---

## Price Errors (E14xx)

### E1401: No Price Found

No price available for currency conversion.

**Message**: `No price found for {base}/{quote} on {date}`

**Fix**: Add a price directive or use explicit `@` price.

---

### E1402: Circular Price

Price definitions create a circular reference.

**Message**: `Circular price reference: {chain}`

**Fix**: Remove circular price dependencies.

---

### E1403: Price Date Mismatch

Price date doesn't match transaction date.

**Message**: `Price dated {price_date} used for transaction on {txn_date}`

This is usually a warning, not an error.

---

## Directive Errors (E15xx)

### E1501: Invalid Option

An unknown or invalid option was specified.

**Message**: `Unknown option '{name}'`

**Fix**: Use a valid option name.

---

### E1502: Plugin Not Found

The specified plugin could not be loaded.

**Message**: `Plugin not found: '{module}'`

**Fix**: Install the plugin or correct the module path.

---

### E1503: Plugin Error

A plugin raised an error.

**Message**: `Plugin '{name}' error: {details}`

**Fix**: Check plugin configuration and input.

---

### E1504: Invalid Pad

Pad directive is invalid.

**Message**: `Pad directive invalid: {reason}`

**Fix**: Ensure pad has valid source and target accounts.

---

### E1505: Duplicate Entry

A duplicate directive was detected.

**Message**: `Duplicate {type} for '{subject}' on {date}`

This may be a warning depending on configuration.

---

## Query Errors (E16xx)

### E1601: Query Syntax Error

The BQL query has a syntax error.

**Message**: `Query syntax error: {details}`

**Fix**: Correct the query syntax.

---

### E1602: Unknown Column

The query references an unknown column.

**Message**: `Unknown column '{name}'`

**Fix**: Use a valid column name.

---

### E1603: Unknown Function

The query uses an unknown function.

**Message**: `Unknown function '{name}'`

**Fix**: Use a valid function name.

---

### E1604: Type Mismatch

A query operation has incompatible types.

**Message**: `Cannot {operation}: {type1} and {type2} are incompatible`

**Fix**: Use compatible types in the expression.

---

### E1605: Aggregate Without Group

An aggregate function is used without GROUP BY.

**Message**: `Aggregate function '{func}' requires GROUP BY`

**Fix**: Add GROUP BY clause or remove aggregate.

---

## Metadata Errors (E17xx)

### E1701: Invalid Metadata Key

The metadata key is invalid.

**Message**: `Invalid metadata key '{key}'`

**Fix**: Use lowercase letters, numbers, and hyphens.

---

### E1702: Duplicate Metadata

The same metadata key appears twice.

**Message**: `Duplicate metadata key '{key}'`

**Fix**: Remove the duplicate key.

---

## Error Code Ranges

| Range | Category |
|-------|----------|
| E1100-E1199 | Account errors |
| E1200-E1299 | Balance errors |
| E1300-E1399 | Booking errors |
| E1400-E1499 | Price errors |
| E1500-E1599 | Directive errors |
| E1600-E1699 | Query errors |
| E1700-E1799 | Metadata errors |

## See Also

- [Common Errors](common.md)
- [Error Specification](../spec.md)
