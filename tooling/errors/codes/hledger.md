# hledger Error Codes (E3xxx)

These error codes are specific to hledger format.

## Account Errors (E31xx)

### E3101: Unknown Account

An account was used that hasn't been declared (when strict mode enabled).

**Message**: `Unknown account '{account}'`

---

### E3102: Account Alias Error

An account alias definition is invalid.

**Message**: `Invalid account alias: {details}`

---

## Balance Errors (E32xx)

### E3201: Transaction Does Not Balance

The transaction postings do not sum to zero.

**Message**: `Transaction does not balance`

---

### E3202: Balance Assertion Failed

A balance assertion failed.

**Message**: `Balance assertion failed: expected {expected}, actual {actual}`

---

### E3203: Multicommodity Balance

A balance assertion involves multiple commodities.

**Message**: `Multicommodity balance assertion not supported`

---

## Directive Errors (E33xx)

### E3301: Invalid Decimal Mark

The decimal-mark directive is invalid.

**Message**: `Invalid decimal mark: must be '.' or ','`

---

### E3302: Duplicate Commodity

A commodity is defined more than once.

**Message**: `Duplicate commodity declaration: '{commodity}'`

---

### E3303: Invalid Tag Directive

A tag directive is invalid.

**Message**: `Invalid tag directive: {details}`

---

## Forecast Errors (E34xx)

### E3401: Invalid Forecast Rule

A forecast rule is invalid.

**Message**: `Invalid forecast rule: {details}`

---

### E3402: Forecast Date Error

A forecast generates invalid dates.

**Message**: `Forecast generates invalid date: {date}`

---

## Auto Posting Errors (E35xx)

### E3501: Invalid Auto Posting

An auto posting rule is invalid.

**Message**: `Invalid auto posting rule: {details}`

---

### E3502: Auto Posting Cycle

Auto postings create a cycle.

**Message**: `Auto posting cycle detected`

---

## Timedot Errors (E36xx)

### E3601: Invalid Timedot Line

A timedot entry is invalid.

**Message**: `Invalid timedot entry: {details}`

---

### E3602: Invalid Time Format

A time duration format is invalid.

**Message**: `Invalid time format: {value}`

---

## CSV Rules Errors (E37xx)

### E3701: Invalid CSV Rule

A CSV import rule is invalid.

**Message**: `Invalid CSV rule: {details}`

---

### E3702: CSV Parse Error

Cannot parse CSV according to rules.

**Message**: `CSV parse error at line {line}: {details}`

---

### E3703: Missing Required Field

A required field is missing in CSV rules.

**Message**: `Missing required field in CSV rules: {field}`

---

## Error Code Ranges

| Range | Category |
|-------|----------|
| E3100-E3199 | Account errors |
| E3200-E3299 | Balance errors |
| E3300-E3399 | Directive errors |
| E3400-E3499 | Forecast errors |
| E3500-E3599 | Auto posting errors |
| E3600-E3699 | Timedot errors |
| E3700-E3799 | CSV rules errors |

## See Also

- [Common Errors](common.md)
- [Beancount Errors](beancount.md)
