# Commodity Validation

## Overview

Commodity validation ensures currencies and commodities are used consistently, optionally requiring explicit declaration and enforcing account currency constraints.

## Validation Rules

### Currency Not Declared

**Note:** Python beancount 3.x does NOT require explicit `commodity` declarations. Currencies are implicitly recognized when used. The `commodity` directive is optional and primarily used for adding metadata.

### Currency Constraint Violation

Postings MUST only use currencies allowed by the account's `open` directive. Violations produce a `ValidationError`.

**Condition:** Posting uses currency not in account's constraint list.

**Example:**
```beancount
2024-01-01 open Assets:USDOnly USD

2024-01-15 * "Invalid currency"
  Assets:USDOnly   100 EUR    ; ValidationError: Account only allows USD
  Income:Gift
```

**Fix:**
```beancount
; Option 1: Use allowed currency
2024-01-15 * "Valid"
  Assets:USDOnly   100 USD
  Income:Gift

; Option 2: Change account constraints
2024-01-01 open Assets:Multi USD,EUR
```

## Currency Constraints

### Open Directive Constraints

The `open` directive can specify allowed currencies:

```beancount
; Only USD allowed
2024-01-01 open Assets:Checking USD

; Multiple currencies allowed
2024-01-01 open Assets:Brokerage USD,EUR,AAPL,MSFT

; Any currency allowed (no constraint)
2024-01-01 open Expenses:General
```

### Constraint Checking

For each posting:

1. Find the account's `open` directive
2. If currencies are specified, verify posting currency is in the list
3. If no currencies specified, any currency is allowed

### Constraint Examples

```beancount
2024-01-01 open Assets:Checking USD

; Valid - USD is allowed
2024-01-15 * "OK"
  Assets:Checking  100 USD
  Income:Salary

; Invalid - EUR not in constraint list
2024-01-15 * "Fail"
  Assets:Checking  100 EUR    ; ValidationError
  Income:Gift

; No constraint - anything allowed
2024-01-01 open Expenses:General

2024-01-15 * "OK"
  Expenses:General  50 JPY    ; OK - no constraint
  Assets:Cash
```

## Operating Currency

The `operating_currency` option specifies the primary currency for reporting:

```beancount
option "operating_currency" "USD"
option "operating_currency" "EUR"  ; Can have multiple
```

This option is additive—each declaration adds to the list. It affects reporting but does NOT enable any "strict mode" for commodity validation.

## Commodity Declaration

### Basic Declaration

```beancount
2024-01-01 commodity USD
2024-01-01 commodity EUR
2024-01-01 commodity AAPL
```

### With Metadata

```beancount
2024-01-01 commodity AAPL
  name: "Apple Inc."
  asset-class: "stock"
  exchange: "NASDAQ"
```

### Declaration Timing

Commodities should be declared before first use:

```beancount
; Recommended order
2024-01-01 commodity USD
2024-01-01 commodity AAPL

2024-01-01 open Assets:Brokerage USD,AAPL

2024-01-15 * "Buy"
  Assets:Brokerage  10 AAPL {150 USD}
  Assets:Cash
```

## Currency Naming

### Format Rules

```ebnf
currency = uppercase (currency_char)* uppercase_end?
uppercase = [A-Z]
currency_char = [A-Z0-9'._-]
uppercase_end = [A-Z0-9]
```

- MUST start with uppercase letter (A-Z)
- MUST end with uppercase letter or digit (A-Z, 0-9)

> **UNDEFINED**: Whether there is a maximum currency name length is pending clarification.
> See: [Pending Issue - Currency Length](https://github.com/beancount/beancount/issues/TBD)

### Valid Names

```
USD
EUR
AAPL
VTSAX
BTC
AU
VTI.TO
BRK.B
```

### Invalid Names

```
usd           ; Lowercase not allowed
$USD          ; Special character at start
USD-          ; Cannot end with special character
```

## Common Validation Scenarios

### Investment Account

```beancount
2024-01-01 commodity USD
2024-01-01 commodity AAPL
2024-01-01 commodity MSFT

; Restrict to declared securities
2024-01-01 open Assets:Brokerage USD,AAPL,MSFT

2024-01-15 * "Buy Apple"
  Assets:Brokerage  10 AAPL {150 USD}    ; OK
  Assets:Brokerage  -1500 USD            ; OK

2024-01-16 * "Buy Google"
  Assets:Brokerage  5 GOOGL {140 USD}    ; ValidationError: GOOGL not allowed
  Assets:Brokerage  -700 USD
```

### Multi-Currency Account

```beancount
2024-01-01 open Assets:Travel USD,EUR,GBP

2024-03-15 * "ATM in Paris"
  Assets:Travel    200 EUR    ; OK
  Assets:Checking

2024-03-20 * "ATM in London"
  Assets:Travel    100 GBP    ; OK
  Assets:Checking

2024-03-25 * "ATM in Tokyo"
  Assets:Travel  10000 JPY    ; ValidationError: JPY not allowed
  Assets:Checking
```

### Crypto Portfolio

```beancount
2024-01-01 commodity USD
2024-01-01 commodity BTC
2024-01-01 commodity ETH
2024-01-01 commodity SOL

2024-01-01 open Assets:Crypto BTC,ETH,SOL
2024-01-01 open Assets:Fiat USD

2024-01-15 * "Buy"
  Assets:Crypto  0.5 BTC {42000 USD}
  Assets:Crypto  2 ETH {2500 USD}
  Assets:Fiat   -47000 USD
```

Note: Currency constraints are enforced per-account via the `open` directive, not via a global "strict" mode option.

## Error Messages

### Currency Constraint Error
```
ValidationError: Currency EUR is not allowed in account Assets:USDOnly
  allowed currencies: USD
```

## Configuration Options

```beancount
; Set operating currency(ies) for reporting
option "operating_currency" "USD"
```

**Note:** Options like `"strict"` and `"infer_commodities"` do not exist in Python beancount 3.x.

## Implementation Notes

1. Build set of declared commodities from `commodity` directives (optional, for metadata)
2. Extract currency constraints from `open` directives
3. For each posting, validate currency against account constraints
4. Report constraint violations with account and allowed list
