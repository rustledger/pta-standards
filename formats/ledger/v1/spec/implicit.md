# Implicit Behavior Specification

This document specifies implicit and inferred behaviors in Ledger.

## Overview

Ledger allows omitting certain information that can be inferred:
- Elided amounts
- Default commodities
- Implicit accounts
- Date inheritance
- Balance completion

## Amount Elision

### Single Elision

One posting per commodity can omit its amount:

```ledger
2024/01/15 Purchase
    Expenses:Food    $50.00
    Assets:Checking          ; Implicitly $-50.00
```

Ledger infers:
```ledger
    Assets:Checking    $-50.00
```

### Multi-Commodity

Each commodity can have one elided amount:

```ledger
2024/01/15 Currency Exchange
    Assets:EUR        100 EUR
    Assets:USD        $110.00
    Expenses:Fees     $2.00
    Assets:Checking           ; Implicitly $-112.00
```

### Elision Rules

| Scenario | Behavior |
|----------|----------|
| One posting without amount | Infer balancing amount |
| Two postings without amount (same commodity) | Error |
| Two postings without amount (different commodities) | OK |
| All postings have amounts | Must balance exactly |

### Error: Multiple Elisions

```ledger
2024/01/15 Bad Transaction
    Expenses:Food
    Expenses:Entertainment
    Assets:Checking    $-100

; ERROR: V-002 - Multiple elided amounts for same commodity
```

## Default Commodity

### Setting Default

```ledger
D $1,000.00
```

Or:

```ledger
commodity $
    format $1,000.00
    default
```

### Implicit Commodity

With default set, bare numbers get the default:

```ledger
D $1,000.00

2024/01/15 Purchase
    Expenses:Food    50.00    ; Implicitly $50.00
    Assets:Checking
```

## Bucket Account

### Setting Bucket

```ledger
bucket Assets:Checking
```

### Implicit Posting

With bucket set, single-posting transactions are completed:

```ledger
bucket Assets:Checking

2024/01/15 Grocery
    Expenses:Food    $50
    ; Implicit: Assets:Checking  $-50
```

## Date Inheritance

### Transaction Date

Postings inherit the transaction date:

```ledger
2024/01/15 Purchase
    Expenses:Food    $50    ; Date: 2024/01/15
    Assets:Checking         ; Date: 2024/01/15
```

### Effective Dates

Postings can override with effective dates:

```ledger
2024/01/15 Credit Card Payment
    Assets:Checking    $-500    ; Date: 2024/01/15
    Liabilities:Credit [=2024/01/20]  ; Effective: 2024/01/20
```

## Status Inheritance

### Transaction Status

Postings inherit transaction status:

```ledger
2024/01/15 * Cleared Transaction
    Expenses:Food    $50    ; Status: cleared
    Assets:Checking         ; Status: cleared
```

### Posting Override

Postings can have their own status:

```ledger
2024/01/15 * Transaction
    ! Expenses:Food    $50  ; Status: pending (override)
    Assets:Checking         ; Status: cleared (inherited)
```

## Implicit Account Creation

### No Declaration Required

By default, accounts are created on first use:

```ledger
2024/01/15 First Transaction
    Expenses:Food:Groceries    $50  ; Account created implicitly
    Assets:Checking                  ; Account created implicitly
```

### Strict Mode

Require declaration with `--strict` or `--pedantic`:

```bash
ledger --strict bal
```

```ledger
account Expenses:Food
account Assets:Checking

2024/01/15 Purchase
    Expenses:Food    $50
    Assets:Checking
```

## Implicit Commodity Creation

### Default Behavior

Commodities are created on first use:

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 NEWSTOCK    ; Commodity created
    Assets:Cash        $-500
```

### Strict Mode

Require declaration:

```ledger
commodity NEWSTOCK

2024/01/15 Buy Stock
    Assets:Brokerage    10 NEWSTOCK
    Assets:Cash        $-500
```

## Balance Inference

### Cost Inference

When buying with price, infer total cost:

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 AAPL @ $150
    Assets:Cash         ; Inferred: $-1500
```

### Conversion Inference

```ledger
2024/01/15 Exchange
    Assets:EUR    100 EUR @@ $110
    Assets:USD    ; Inferred: $110
```

## Precision Inference

### From Transactions

Ledger infers display precision from usage:

```ledger
commodity $
    ; If transactions use $10.00, display with 2 decimals
    ; If transactions use $10.000, display with 3 decimals
```

### From Format

```ledger
commodity $
    format $1,000.00    ; 2 decimal places
```

## Payee Inference

### From Transaction

```ledger
2024/01/15 Whole Foods
    ; Payee: Whole Foods (from transaction line)
    Expenses:Food    $50
    Assets:Checking
```

### Payee Metadata Override

```ledger
2024/01/15 Store Purchase
    ; Payee: Whole Foods Market
    Expenses:Food    $50
    Assets:Checking
```

## Account Type Inference

### From Name Prefix

| Prefix | Inferred Type |
|--------|---------------|
| `Assets:` | Asset |
| `Liabilities:` | Liability |
| `Equity:` | Equity |
| `Income:` or `Revenue:` | Income |
| `Expenses:` | Expense |

### Explicit Override

```ledger
account Assets:Receivable
    type: Liability    ; Override inferred type
```

## Virtual Account Inference

### Balanced Virtual

Square brackets create balanced virtual accounts:

```ledger
2024/01/15 Budget Entry
    [Budget:Food]     $500
    [Budget:Available]    ; Inferred: $-500
```

### Unbalanced Virtual

Parentheses create unbalanced virtual accounts:

```ledger
2024/01/15 Expense
    Expenses:Food       $50
    (Budget:Food)      $-50    ; Does not need to balance
    Assets:Checking    $-50
```

## Examples

### Full Implicit Transaction

```ledger
D $1,000.00
bucket Assets:Checking

2024/01/15 * Grocery Store
    Expenses:Food:Groceries    50
    ; Implicit commodity: $
    ; Implicit posting: Assets:Checking $-50.00
```

Expands to:

```ledger
2024/01/15 * Grocery Store
    Expenses:Food:Groceries    $50.00
    Assets:Checking           $-50.00
```

### Multi-Way Split

```ledger
2024/01/15 Costco Run
    Expenses:Food:Groceries    $200.00
    Expenses:Household         $50.00
    Expenses:Entertainment     $25.00
    Assets:Checking    ; Inferred: $-275.00
```

### Investment Purchase

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 AAPL {$150} @ $152
    Expenses:Fees       $7.00
    Assets:Cash         ; Inferred: $-1527.00
```

## Ambiguity Resolution

### Precedence

When multiple rules could apply:

1. Explicit values take precedence
2. Posting-level overrides transaction-level
3. Most recent declaration wins

### Error Cases

- Multiple amount elisions for same commodity
- Conflicting prices/costs
- Circular references

## Best Practices

1. **Explicit over implicit** - For clarity in complex transactions
2. **Use elision sparingly** - Only for simple two-posting transactions
3. **Declare commodities** - In strict/production use
4. **Set bucket carefully** - Can cause unexpected behavior
5. **Review inferred amounts** - Verify with reports

## See Also

- [Amount Specification](amounts.md)
- [Posting Specification](posting.md)
- [Bucket Directive](directives/bucket.md)
- [Default Directive](directives/default.md)
