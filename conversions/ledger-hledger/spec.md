# Ledger to hledger Conversion

This specification defines how to convert Ledger files to hledger format.

## Overview

Ledger and hledger are highly compatible. hledger was designed to be largely compatible with Ledger syntax. Most files work in both tools with minimal or no changes.

## Compatibility Level

**High compatibility:** ~95% of Ledger files work in hledger without modification.

### Differences

| Feature | Ledger | hledger |
|---------|--------|---------|
| Value expressions | Full support | Limited/none |
| Automated transactions | `= PATTERN` | `= PATTERN` (compatible) |
| Periodic transactions | `~ PERIOD` | `~ PERIOD` (compatible) |
| Virtual postings | `(Account)` `[Account]` | Supported |
| Some functions | Full set | Subset |

## Directive Mapping

### Transactions

Identical syntax in most cases:

```ledger
2024/01/15 * Whole Foods
  ; :food:
  Assets:Checking  $-50.00
  Expenses:Food:Groceries
```

```hledger
2024/01/15 * Whole Foods
  ; :food:
  Assets:Checking  $-50.00
  Expenses:Food:Groceries
```

### Date Format

Both support multiple date formats:

| Format | Ledger | hledger |
|--------|--------|---------|
| `2024/01/15` | ✅ | ✅ |
| `2024-01-15` | ✅ | ✅ |
| `2024.01.15` | ✅ | ✅ |

### Account Directive

```ledger
account Assets:Checking
  alias checking
  note My main checking account
```

```hledger
account Assets:Checking
  alias checking
  ; note: My main checking account
```

### Commodity Directive

```ledger
commodity $
  format $1,000.00
  nomarket
```

```hledger
commodity $1,000.00
```

Note: hledger uses format string directly, not separate format directive.

### Price Directive

Identical:

```
P 2024/01/15 AAPL $185.00
```

### Automated Transactions

Identical:

```
= /Groceries/
  Expenses:Tax  0.07
  Assets:Checking
```

### Periodic Transactions

Identical:

```
~ Monthly
  Expenses:Rent  $1500
  Assets:Checking
```

## Value Expressions

The main incompatibility area.

### Ledger Expressions

```ledger
2024/01/15 * Transaction
  Assets:Checking  (amount * 1.1)
  Expenses:Something
```

### hledger

Does not support value expressions in amounts. Must pre-compute:

```hledger
2024/01/15 * Transaction
  Assets:Checking  $-110.00  ; computed from $100 * 1.1
  Expenses:Something
```

## Virtual Postings

### Unbalanced Virtual

```ledger
2024/01/15 * Transaction
  Assets:Checking  $-100.00
  Expenses:Food  $100.00
  (Budget:Food)  $100.00
```

hledger supports this with `--strict` allowing unbalanced virtuals.

### Balanced Virtual

```ledger
2024/01/15 * Transaction
  Assets:Checking  $-100.00
  Expenses:Food  $100.00
  [Budget:Food:Spent]  $100.00
  [Budget:Food:Available]  $-100.00
```

Supported in hledger.

## Balance Assertions

### Standard Assertion

Both use `=`:

```
Assets:Checking  $0 = $1000.00
```

### hledger Extensions

hledger has additional assertion types not in Ledger:

| Syntax | Meaning | Ledger |
|--------|---------|--------|
| `= $1000` | Single commodity | ✅ |
| `== $1000` | Total balance | ❌ |
| `=* $1000` | Including subaccounts | ❌ |
| `==* $1000` | Total with subaccounts | ❌ |

## Functions

### Supported in Both

- `abs()`
- `round()`
- Basic arithmetic

### Ledger Only

- `market()`
- `price()`
- `lot_date()`
- `lot_price()`
- Many others

**Conversion:** Pre-evaluate function calls.

## Effective Dates

```ledger
2024/01/15=2024/01/20 * Transaction
  Assets:Checking  $-100.00
  Expenses:Food
```

Both support effective dates (secondary dates).

## Includes

Identical:

```
include accounts.ledger
```

## Aliases

```ledger
alias checking=Assets:Bank:Checking
```

```hledger
alias checking = Assets:Bank:Checking
```

Note the spacing difference: hledger requires spaces around `=`.

## Tags

Identical:

```
2024/01/15 * Transaction
  ; :tag1:tag2:
  Assets:Checking  $-100.00
```

## Conversion Algorithm

```
1. Parse Ledger file
2. For each element:
   a. Check for value expressions → pre-evaluate
   b. Check for unsupported functions → pre-evaluate or warn
   c. Adjust alias syntax if needed
3. Generate hledger output
4. Validate with hledger
```

## Recommendations

1. **Test with hledger first** - Many files work as-is
2. **Pre-evaluate expressions** - Compute values before conversion
3. **Document incompatibilities** - Add comments for manual review
4. **Use strict mode** - Test with `hledger check --strict`

## See Also

- [Edge Cases](edge-cases.md)
- [hledger Manual: Ledger Compatibility](https://hledger.org/ledger.html)
