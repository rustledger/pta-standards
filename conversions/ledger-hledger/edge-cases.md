# Ledger to hledger Edge Cases

This document covers edge cases when converting Ledger to hledger.

## Value Expressions

The most significant incompatibility.

### Amount Expressions

**Ledger:**
```ledger
2024/01/15 * Shopping
  Expenses:Tax  (amount * 0.08)
  Expenses:Purchase  $100.00
  Assets:Checking
```

**hledger:** Pre-calculate:
```hledger
2024/01/15 * Shopping
  Expenses:Tax  $8.00  ; calculated: 100 * 0.08
  Expenses:Purchase  $100.00
  Assets:Checking
```

### Conditional Expressions

**Ledger:**
```ledger
= /Restaurants/
  Expenses:Tax  (amount > 20 ? amount * 0.1 : 0)
  Assets:Checking
```

**hledger:** Not supported. Expand manually for each transaction.

## Unsupported Functions

### `market()` Function

**Ledger:**
```ledger
2024/01/15 * Check portfolio
  [Assets:Checking]  (market(Assets:Investments))
```

**hledger:** Cannot use. Calculate separately.

### `lot_date()` and `lot_price()`

Used for lot-based calculations in Ledger. No hledger equivalent.

## Commodity Formatting

### Format Directive

**Ledger:**
```ledger
commodity $
  format $1,000.00
  nomarket
  default
```

**hledger:**
```hledger
commodity $1,000.00
; nomarket and default options not directly supported
```

### European Format

**Ledger:**
```ledger
commodity €
  format 1.000,00 €
```

**hledger:**
```hledger
commodity 1.000,00 €
decimal-mark ,
```

## Alias Syntax

### Ledger

```ledger
alias checking=Assets:Bank:Checking
alias /^Expenses:(.*)$/=Costs:\1
```

### hledger

```hledger
alias checking = Assets:Bank:Checking
alias /^Expenses:(.*)$/ = Costs:\1
```

Note: Spaces around `=` required in hledger.

## Assertion Types

### hledger-Only Assertions

If converting from hledger to Ledger:

```hledger
Assets:Checking  $0 == $1000.00 USD, 500.00 EUR
```

**Ledger:** Split into separate assertions or remove.

### Subaccount Assertions

```hledger
Assets  $0 =* $5000.00
```

**Ledger:** No equivalent. Calculate total manually.

## Automated Transaction Amounts

### Calculated Amounts

**Ledger:**
```ledger
= /Expenses:Food/
  (Budget:Food)  (amount)
  (Budget:Available)  (-amount)
```

**hledger:** Limited support for `(amount)`:
```hledger
= /Expenses:Food/
  (Budget:Food)  *1
  (Budget:Available)  *-1
```

## Periodic Transaction Details

### Complex Periods

**Ledger:**
```ledger
~ every 2nd Monday
  Expenses:Payroll  $2000
  Assets:Checking
```

**hledger:** Period parsing may differ. Test specific periods.

## Check/Assert Directives

### Ledger

```ledger
check balance Assets:Checking >= $0
assert balance Assets:Checking > $100
```

### hledger

Not directly supported. Use balance assertions:
```hledger
; Manual balance check needed
2024/01/15 Balance check
  Assets:Checking  $0 = $150.00
```

## Lot Specifications

### Ledger Lot Syntax

```ledger
Assets:Brokerage  10 AAPL {$185.00} [2024/01/15] (lot1)
```

### hledger

```hledger
Assets:Brokerage  10 AAPL @ $185.00
  ; lot-date: 2024-01-15
  ; lot-note: lot1
```

## Comments

### Block Comments

**Ledger:**
```ledger
comment
This is a
multi-line comment
end comment
```

**hledger:** Use line comments:
```hledger
; This is a
; multi-line comment
```

## Year Directive

**Ledger:**
```ledger
year 2024
01/15 * Transaction
  ; Becomes 2024/01/15
```

**hledger:** Supported but use with caution. Prefer full dates.

## Time Logging

### Ledger Time

```ledger
i 2024/01/15 09:00:00 Project
o 2024/01/15 17:30:00
```

### hledger Timedot

```timedot
2024-01-15
Project  8.5
```

Different format entirely. Consider using hledger's native timedot format.

## Conversion Strategy

1. **Parse and validate** in Ledger first
2. **Identify expressions** - Find all value expressions
3. **Pre-evaluate** - Calculate all expression values
4. **Convert syntax** - Adjust minor differences
5. **Validate** - Run `hledger check` on result
6. **Compare reports** - Ensure balances match

## Tools

### hledger's Built-in Conversion

```bash
# hledger can often read Ledger files directly
hledger -f file.ledger balance
```

Test this first before manual conversion.
