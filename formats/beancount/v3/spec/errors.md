# Beancount Error Catalog

This document catalogs all validation errors and warnings with their trigger conditions.

## Error Categories

| Category | Code Range | Description |
|----------|------------|-------------|
| ACCOUNT | E1xxx | Account lifecycle violations |
| BALANCE | E2xxx | Balance assertion failures |
| TXN | E3xxx | Transaction structure errors |
| BOOKING | E4xxx | Inventory/lot matching errors |
| CURRENCY | E5xxx | Currency/commodity violations |
| META | E6xxx | Metadata errors |
| OPTION | E7xxx | Option errors |
| DOCUMENT | E8xxx | Document errors |
| INCLUDE | E9xxx | Include errors |
| DATE | E10xxx | Date errors |

## Severity Levels

| Severity | Meaning |
|----------|---------|
| **Error** | Ledger is invalid; MUST be corrected |
| **Warning** | Suspicious but valid; SHOULD be reviewed |
| **Info** | Informational; MAY be ignored |

---

## Account Errors

### E1001: ACCOUNT_NOT_OPENED

**Condition:** Posting references an account that has no prior `open` directive.

**Message:** `Account "{account}" is not open`

**Severity:** Error

```beancount
; No open directive for Assets:Checking
2024-01-15 * "Deposit"
  Assets:Checking   100 USD   ; ERROR: Account not opened
  Income:Salary
```

### E1002: ACCOUNT_ALREADY_OPEN

**Condition:** `open` directive for an account that is already open.

**Message:** `Account "{account}" is already open (opened on {date})`

**Severity:** Error

```beancount
2020-01-01 open Assets:Checking
2021-01-01 open Assets:Checking  ; ERROR: Already open
```

### E1003: ACCOUNT_ALREADY_CLOSED

**Condition:** Posting references an account after its `close` directive.

**Message:** `Account "{account}" was closed on {date}`

**Severity:** Error

```beancount
2020-01-01 open Assets:Checking
2023-12-31 close Assets:Checking
2024-01-15 * "Late deposit"
  Assets:Checking   100 USD   ; ERROR: Account closed
  Income:Salary
```

### E1004: ACCOUNT_CLOSE_NOT_EMPTY

**Condition:** `close` directive when account has non-zero balance.

**Message:** `Cannot close account "{account}" with non-zero balance: {balance}`

**Severity:** Warning (configurable to Error)

### E1005: ACCOUNT_INVALID_NAME

**Condition:** Account name doesn't match expected pattern.

**Message:** `Invalid account name "{account}": {reason}`

**Reasons:**
- Does not start with valid root (Assets, Liabilities, Equity, Income, Expenses)
- Contains invalid characters
- Component doesn't start with capital letter

**Severity:** Error

---

## Balance Errors

### E2001: BALANCE_ASSERTION_FAILED

**Condition:** Account balance doesn't match assertion.

**Message:** `Balance assertion failed for {account}: expected {expected} {currency}, got {actual} (difference: {diff})`

**Severity:** Error

```beancount
2024-01-01 open Assets:Checking
2024-01-15 * "Deposit"
  Assets:Checking   100 USD
  Income:Salary

2024-01-16 balance Assets:Checking  200 USD  ; ERROR: Actually 100 USD
```

### E2002: BALANCE_TOLERANCE_EXCEEDED

**Condition:** Balance is within default tolerance but exceeds explicit tolerance.

**Message:** `Balance {actual} exceeds tolerance {tolerance} for assertion {expected}`

**Severity:** Error

### E2003: PAD_WITHOUT_BALANCE

**Condition:** `pad` directive without subsequent `balance` for same account/currency.

**Message:** `Pad directive for {account} has no subsequent balance assertion for {currency}`

**Severity:** Error

### E2004: MULTIPLE_PAD_FOR_BALANCE

**Condition:** Multiple `pad` directives between balance assertions for same account/currency.

**Message:** `Multiple pad directives for {account} {currency} before balance assertion`

**Severity:** Error

---

## Transaction Errors

### E3001: TXN_NOT_BALANCED

**Condition:** Transaction weights don't sum to zero (per currency).

**Message:** `Transaction does not balance: residual {amount} {currency}`

**Severity:** Error

```beancount
2024-01-15 * "Unbalanced"
  Assets:Checking   100 USD
  Expenses:Food      50 USD  ; ERROR: Missing -150 USD
```

### E3002: TXN_MULTIPLE_MISSING_AMOUNTS

**Condition:** More than one posting has missing amount for same currency.

**Message:** `Cannot interpolate: multiple postings missing amounts for {currency}`

**Severity:** Error

```beancount
2024-01-15 * "Ambiguous"
  Assets:Checking   100 USD
  Expenses:Food           ; Missing
  Expenses:Drinks         ; ERROR: Also missing same currency
```

### E3003: TXN_NO_POSTINGS

**Condition:** Transaction has zero postings.

**Message:** `Transaction must have at least one posting`

**Severity:** Error

### E3004: TXN_SINGLE_POSTING

**Condition:** Transaction has exactly one posting (cannot balance).

**Message:** `Transaction has only one posting`

**Severity:** Warning

---

## Booking Errors

### E4001: BOOKING_NO_MATCHING_LOT

**Condition:** Reduction specifies cost that doesn't match any lot.

**Message:** `No lot matching {cost_spec} for {currency} in {account}`

**Severity:** Error

```beancount
2024-01-01 * "Buy"
  Assets:Stock   10 AAPL {150 USD}
  Assets:Cash

2024-06-01 * "Sell"
  Assets:Stock  -5 AAPL {160 USD}  ; ERROR: No lot at 160 USD
  Assets:Cash
```

### E4002: BOOKING_INSUFFICIENT_UNITS

**Condition:** Reduction requests more units than available in matching lots.

**Message:** `Insufficient units: requested {requested}, available {available}`

**Severity:** Error

### E4003: BOOKING_AMBIGUOUS_MATCH

**Condition:** Multiple lots match and booking method is STRICT.

**Message:** `Ambiguous lot match for {currency}: {count} lots match. Specify cost, date, or label to disambiguate, or use FIFO/LIFO booking.`

**Severity:** Error

```beancount
2024-01-01 open Assets:Stock "STRICT"

2024-01-01 * "Buy lot 1"
  Assets:Stock   10 AAPL {150 USD}
  Assets:Cash

2024-02-01 * "Buy lot 2"
  Assets:Stock   10 AAPL {160 USD}
  Assets:Cash

2024-06-01 * "Sell"
  Assets:Stock  -5 AAPL {}  ; ERROR: Which lot? 150 or 160?
  Assets:Cash
```

### E4004: BOOKING_NEGATIVE_UNITS

**Condition:** Reduction would create negative position (except with NONE booking).

**Message:** `Reduction would result in negative inventory for {currency}`

**Severity:** Error

---

## Currency Errors

### E5001: CURRENCY_NOT_DECLARED

**Condition:** Currency used but not declared with `commodity` directive (when strict mode enabled).

**Message:** `Currency "{currency}" is not declared`

**Severity:** Warning

### E5002: CURRENCY_CONSTRAINT_VIOLATION

**Condition:** Posting uses currency not in account's allowed list.

**Message:** `Account {account} does not allow currency {currency} (allowed: {allowed})`

**Severity:** Error

```beancount
2024-01-01 open Assets:USDOnly USD

2024-01-15 * "Wrong currency"
  Assets:USDOnly   100 EUR  ; ERROR: Only USD allowed
  Income:Salary
```

---

## Metadata Errors

### E6001: DUPLICATE_METADATA_KEY

**Condition:** Same metadata key specified multiple times on one directive.

**Message:** `Duplicate metadata key "{key}"`

**Severity:** Warning

### E6002: INVALID_METADATA_VALUE

**Condition:** Metadata value doesn't match expected type.

**Message:** `Invalid value for metadata key "{key}": expected {type}`

**Severity:** Warning

---

## Option Errors

### E7001: UNKNOWN_OPTION

**Condition:** Unrecognized option name.

**Message:** `Unknown option "{name}"`

**Severity:** Warning

### E7002: INVALID_OPTION_VALUE

**Condition:** Option value is invalid for option type.

**Message:** `Invalid value "{value}" for option "{name}": {reason}`

**Severity:** Error

### E7003: DUPLICATE_OPTION

**Condition:** Non-repeatable option specified multiple times.

**Message:** `Option "{name}" can only be specified once`

**Severity:** Warning (uses last value)

---

## Document Errors

### E8001: DOCUMENT_FILE_NOT_FOUND

**Condition:** Document directive references non-existent file.

**Message:** `Document file not found: {path}`

**Severity:** Warning (configurable)

---

## Include Errors

### E9001: INCLUDE_FILE_NOT_FOUND

**Condition:** Included file doesn't exist.

**Message:** `Include file not found: {path}`

**Severity:** Error

### E9002: INCLUDE_CYCLE_DETECTED

**Condition:** Circular include dependency.

**Message:** `Include cycle detected: {path} -> {chain}`

**Severity:** Error

---

## Date Errors

### E10001: DATE_OUT_OF_ORDER

**Condition:** Directive date is before previous directive (informational only).

**Message:** `Directive date {date} is before previous directive {prev_date}`

**Severity:** Info (directives are auto-sorted)

### E10002: DATE_IN_FUTURE

**Condition:** Directive date is in the future.

**Message:** `Directive date {date} is in the future`

**Severity:** Warning

---

## Validation Phases

Validation occurs in multiple phases:

### Phase 1: Syntax (during parsing)
- Parse errors
- E1005: ACCOUNT_INVALID_NAME

### Phase 2: Structure (after parsing)
- E3003: TXN_NO_POSTINGS
- E9001: INCLUDE_FILE_NOT_FOUND
- E9002: INCLUDE_CYCLE_DETECTED

### Phase 3: Accounts (chronological scan)
- E1001: ACCOUNT_NOT_OPENED
- E1002: ACCOUNT_ALREADY_OPEN
- E1003: ACCOUNT_ALREADY_CLOSED

### Phase 4: Interpolation
- E3002: TXN_MULTIPLE_MISSING_AMOUNTS

### Phase 5: Booking
- E4001-E4004: All booking errors

### Phase 6: Balancing
- E3001: TXN_NOT_BALANCED

### Phase 7: Assertions
- E2001: BALANCE_ASSERTION_FAILED
- E2003: PAD_WITHOUT_BALANCE

### Phase 8: Optional Checks
- E8001: DOCUMENT_FILE_NOT_FOUND
- E5001: CURRENCY_NOT_DECLARED
- E10002: DATE_IN_FUTURE

---

## Machine-Readable Format

Implementations SHOULD support structured error output for tooling integration.

### JSON Format

```json
{
  "errors": [
    {
      "code": "E3001",
      "severity": "error",
      "message": "Transaction does not balance: residual 50 USD",
      "location": {
        "file": "ledger.beancount",
        "line": 15,
        "column": 1,
        "span": {
          "start": 342,
          "end": 425
        }
      },
      "date": "2024-01-15",
      "context": {
        "expected": "0 USD",
        "actual": "50 USD",
        "currency": "USD"
      }
    }
  ],
  "summary": {
    "total": 1,
    "errors": 1,
    "warnings": 0,
    "info": 0
  }
}
```

### SARIF Format

For IDE integration, implementations MAY output [SARIF](https://sarifweb.azurewebsites.net/) (Static Analysis Results Interchange Format):

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "beancount",
        "version": "3.0.0",
        "rules": [{
          "id": "E3001",
          "name": "TransactionUnbalanced",
          "shortDescription": {
            "text": "Transaction does not balance"
          },
          "helpUri": "https://beancount.io/errors/E3001"
        }]
      }
    },
    "results": [{
      "ruleId": "E3001",
      "level": "error",
      "message": {
        "text": "Transaction does not balance: residual 50 USD"
      },
      "locations": [{
        "physicalLocation": {
          "artifactLocation": {
            "uri": "ledger.beancount"
          },
          "region": {
            "startLine": 15,
            "startColumn": 1
          }
        }
      }]
    }]
  }]
}
```

---

## Error Message Style Guide

Error messages SHOULD:

1. **Be specific**: Include actual values, not just "invalid"
2. **Be actionable**: Suggest how to fix when possible
3. **Reference locations**: Include file, line, column
4. **Use consistent terminology**: Match spec terminology
5. **Avoid jargon**: Prefer "balance assertion failed" over "invariant violation"

### Message Format

```
[code] category: brief description
  --> file:line:column
  |
N | <source line>
  | ^^^^^^^^^^^^^ detailed explanation
  |
  = key: value (context)
  = hint: suggestion for fixing
```

### Example

```
[E3001] error: transaction does not balance
  --> ledger.beancount:15:1
   |
15 | 2024-01-15 * "Coffee"
   | ^^^^^^^^^^^^^^^^^^^^^ residual amount: 50 USD
   |
   = expected: 0 USD
   = actual: 50 USD
   = hint: add a posting for -50 USD to balance
```

---

## Extensibility

Implementations MAY define additional error codes:

| Range | Reserved For |
|-------|--------------|
| E0001-E0999 | Reserved (do not use) |
| E1001-E10999 | Standard errors (this spec) |
| E11000-E19999 | Implementation-specific |
| E20000-E29999 | Plugin errors |
| E30000+ | User-defined |

Custom errors MUST use codes outside the standard range and SHOULD document their meaning.
