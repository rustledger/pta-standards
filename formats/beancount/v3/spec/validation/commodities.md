# Commodity Validation

## Overview

Commodity validation ensures currencies and commodities are used consistently, optionally requiring explicit declaration and enforcing account currency constraints.

## Validation Rules

### E5001: Currency Not Declared

In strict mode, all currencies MUST be declared with a `commodity` directive.

**Condition:** Currency used without prior `commodity` directive (when strict mode enabled).

**Severity:** Warning (Error in strict mode)

**Example:**
```beancount
option "strict" "TRUE"

2024-01-01 commodity USD
2024-01-01 commodity EUR

2024-01-15 * "Purchase"
  Assets:Checking  -100 GBP    ; E5001: GBP not declared
  Expenses:Food
```

**Fix:**
```beancount
option "strict" "TRUE"

2024-01-01 commodity USD
2024-01-01 commodity EUR
2024-01-01 commodity GBP       ; Add declaration

2024-01-15 * "Purchase"
  Assets:Checking  -100 GBP    ; OK
  Expenses:Food
```

### E5002: Currency Constraint Violation

Postings MUST only use currencies allowed by the account's `open` directive.

**Condition:** Posting uses currency not in account's constraint list.

**Example:**
```beancount
2024-01-01 open Assets:USDOnly USD

2024-01-15 * "Invalid currency"
  Assets:USDOnly   100 EUR    ; E5002: Account only allows USD
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
  Assets:Checking  100 EUR    ; E5002
  Income:Gift

; No constraint - anything allowed
2024-01-01 open Expenses:General

2024-01-15 * "OK"
  Expenses:General  50 JPY    ; OK - no constraint
  Assets:Cash
```

## Strict Mode

### Enabling Strict Mode

```beancount
option "strict" "TRUE"
```

Or:

```beancount
option "operating_currency" "USD"  ; Enables strict for USD
```

### Strict Mode Behavior

| Check | Default Mode | Strict Mode |
|-------|--------------|-------------|
| Undeclared currency | Allowed | Warning/Error |
| Account constraints | Enforced | Enforced |
| Operating currency | Optional | Required |

### Operating Currency

The primary currency for reporting:

```beancount
option "operating_currency" "USD"
option "operating_currency" "EUR"  ; Can have multiple
```

Operating currencies MUST be declared in strict mode.

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
currency = uppercase (currency_char)* uppercase?
uppercase = [A-Z]
currency_char = [A-Z0-9'._-]
```

### Length

1-24 characters.

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
usd           ; Lowercase
$USD          ; Special character at start
ABCDEFGHIJKLMNOPQRSTUVWXYZ  ; Too long (>24)
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
  Assets:Brokerage  5 GOOGL {140 USD}    ; E5002: GOOGL not allowed
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
  Assets:Travel  10000 JPY    ; E5002: JPY not allowed
  Assets:Checking
```

### Crypto Portfolio

```beancount
option "strict" "TRUE"

2024-01-01 commodity USD
2024-01-01 commodity BTC
2024-01-01 commodity ETH
2024-01-01 commodity SOL

2024-01-01 open Assets:Crypto USD,BTC,ETH,SOL

2024-01-15 * "Buy"
  Assets:Crypto  0.5 BTC {42000 USD}
  Assets:Crypto  2 ETH {2500 USD}
  Assets:Fiat   -47000 USD
```

## Error Messages

### E5001 Format
```
warning: Currency not declared
  --> ledger.beancount:15:20
   |
15 |   Assets:Checking  100 GBP
   |                        ^^^ currency "GBP" is not declared
   |
   = hint: add '2024-01-01 commodity GBP'
```

### E5002 Format
```
error: Currency not allowed in account
  --> ledger.beancount:15:20
   |
15 |   Assets:USDOnly  100 EUR
   |                       ^^^ "EUR" not allowed
   |
   = account: Assets:USDOnly
   = allowed: USD
```

## Configuration Options

```beancount
; Enable strict mode
option "strict" "TRUE"

; Set operating currency(ies)
option "operating_currency" "USD"

; Infer currencies from file (experimental)
option "infer_commodities" "TRUE"
```

## Implementation Notes

1. Build set of declared commodities from `commodity` directives
2. Extract currency constraints from `open` directives
3. For each posting, validate currency against account constraints
4. In strict mode, also validate against declared commodities
5. Report constraint violations with account and allowed list
