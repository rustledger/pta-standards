# Ledger Error Codes (E2xxx)

These error codes are specific to Ledger CLI format.

## Account Errors (E21xx)

### E2101: Unknown Account

An account was used that hasn't been declared (when strict mode enabled).

**Message**: `Unknown account '{account}'`

---

### E2102: Account Assertion Failed

An account assertion did not match.

**Message**: `Account assertion failed for '{account}'`

---

## Balance Errors (E22xx)

### E2201: Transaction Does Not Balance

The transaction postings do not sum to zero.

**Message**: `Transaction does not balance`

---

### E2202: Balance Check Failed

A balance assertion failed.

**Message**: `Balance check failed: expected {expected}, actual {actual}`

---

### E2203: Virtual Balance Error

A virtual posting balance is incorrect.

**Message**: `Virtual balance error in '{account}'`

---

## Expression Errors (E23xx)

### E2301: Invalid Expression

A value expression is invalid.

**Message**: `Invalid expression: {details}`

---

### E2302: Division By Zero

An expression resulted in division by zero.

**Message**: `Division by zero in expression`

---

### E2303: Undefined Variable

An expression references an undefined variable.

**Message**: `Undefined variable '{name}'`

---

## Automated Transaction Errors (E24xx)

### E2401: Invalid Automated Transaction

An automated transaction definition is invalid.

**Message**: `Invalid automated transaction: {details}`

---

### E2402: Automated Regex Error

The regex in an automated transaction is invalid.

**Message**: `Invalid regex in automated transaction: {pattern}`

---

## Periodic Transaction Errors (E25xx)

### E2501: Invalid Period

A periodic transaction has an invalid period.

**Message**: `Invalid period expression: {expression}`

---

### E2502: Period Parse Error

The period expression could not be parsed.

**Message**: `Cannot parse period: {details}`

---

## Error Code Ranges

| Range | Category |
|-------|----------|
| E2100-E2199 | Account errors |
| E2200-E2299 | Balance errors |
| E2300-E2399 | Expression errors |
| E2400-E2499 | Automated transaction errors |
| E2500-E2599 | Periodic transaction errors |

## See Also

- [Common Errors](common.md)
- [Beancount Errors](beancount.md)
