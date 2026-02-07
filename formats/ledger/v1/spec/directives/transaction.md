# Transaction Directive

Transactions are the primary directive in Ledger, representing transfers of value between accounts.

## Syntax

```
DATE [=EFFECTIVE] [FLAG] [(CODE)] PAYEE [| NARRATION] [; COMMENT]
    POSTING...
```

## Components

### Date

The transaction date in one of the supported formats:

```ledger
2024/01/15 Grocery Store     ; Canonical
2024-01-15 Grocery Store     ; ISO format
01/15 Grocery Store          ; Uses default year
```

### Effective Date

An optional secondary date following `=`:

```ledger
2024/01/15=2024/01/20 Scheduled Payment
    ; Posted on 01/15, effective 01/20
    Expenses:Bills  $100
    Assets:Checking
```

Use cases:
- Checks with future effective date
- Credit card purchases vs statement date
- Scheduled payments

### Transaction Flag

Optional status indicator:

| Flag | Meaning |
|------|---------|
| `*` | Cleared/reconciled |
| `!` | Pending |
| (none) | Unmarked |

```ledger
2024/01/15 * Cleared Transaction
    Expenses:Food  $50
    Assets:Checking

2024/01/15 ! Pending Transaction
    Expenses:Food  $50
    Assets:Checking

2024/01/15 Unmarked Transaction
    Expenses:Food  $50
    Assets:Checking
```

### Code

Optional transaction code in parentheses:

```ledger
2024/01/15 * (1234) Check Payment
    ; Check number 1234
    Expenses:Rent  $1500
    Assets:Checking

2024/01/15 * (ACH) Direct Deposit
    Assets:Checking  $2000
    Income:Salary
```

Common uses:
- Check numbers
- Reference numbers
- Transaction IDs

### Payee and Narration

The description can optionally have payee and narration separated by `|`:

```ledger
2024/01/15 * Grocery Store | Weekly shopping
    ; Payee: "Grocery Store"
    ; Narration: "Weekly shopping"
    Expenses:Food  $50
    Assets:Checking

2024/01/15 * Just a description
    ; Entire string is payee/description
    Expenses:Food  $50
    Assets:Checking
```

### Transaction Comment

End-of-line comment:

```ledger
2024/01/15 * Grocery Store  ; Don't forget receipt
    Expenses:Food  $50
    Assets:Checking
```

## Postings

Every transaction contains one or more postings:

```ledger
2024/01/15 * Multi-posting Transaction
    Expenses:Food:Groceries     $30.00
    Expenses:Food:Snacks        $10.00
    Expenses:Household          $10.00
    Assets:Checking            $-50.00
```

### Posting Format

```
    ACCOUNT  [AMOUNT] [@ PRICE | @@ TOTAL] [= BALANCE] [; COMMENT]
```

### Elided Amount

One posting amount can be omitted; Ledger calculates it:

```ledger
2024/01/15 * Transaction with elided amount
    Expenses:Food  $50.00
    Assets:Checking           ; Amount inferred as -$50.00
```

### Multiple Elided Amounts

Only one amount can be elided per commodity:

```ledger
; INVALID - two elided USD amounts
2024/01/15 * Bad Transaction
    Expenses:Food
    Assets:Checking

; VALID - different commodities
2024/01/15 * Currency Exchange
    Assets:USD               ; Elided USD
    Assets:EUR    50.00 EUR  ; Explicit EUR
```

## Balance Assertions

Assert the account balance after this posting:

```ledger
2024/01/15 * Reconciliation
    Assets:Checking  $100.00 = $1500.00
    ; After this posting, Checking should be $1500.00
    Income:Salary
```

### Partial Balance Assertion

Assert balance for specific commodity only:

```ledger
2024/01/15 * Deposit
    Assets:Brokerage  10 AAPL = 50 AAPL
    ; Assert 50 AAPL (ignoring other commodities)
    Assets:Checking  $-1500.00
```

## Metadata

Transaction and posting metadata:

```ledger
2024/01/15 * Grocery Store
    ; Project: home
    ; Category: food
    Expenses:Food  $50.00
        ; Receipt: IMG_001.jpg
        ; Tax-deductible: no
    Assets:Checking
```

### Tags

Colon-delimited tags:

```ledger
2024/01/15 * Business Trip
    ; :travel:business:tax-deductible:
    Expenses:Travel  $500
    Assets:Checking
```

## Virtual Postings

### Unbalanced Virtual

Postings in `()` don't affect transaction balance:

```ledger
2024/01/15 * With Budget Tracking
    Expenses:Food      $50.00
    (Budget:Food)     $-50.00    ; Not balanced
    Assets:Checking
```

### Balanced Virtual

Postings in `[]` must balance among themselves:

```ledger
2024/01/15 * Savings Allocation
    Assets:Checking     $1000.00
    [Savings:Goal]     $-500.00
    [Savings:Emergency] $-500.00  ; These two must balance
    Income:Salary
```

## Price Annotations

### Per-unit Price (@)

```ledger
2024/01/15 * Buy Stock
    Assets:Brokerage  10 AAPL @ $150.00
    Assets:Checking  $-1500.00
```

### Total Price (@@)

```ledger
2024/01/15 * Currency Exchange
    Assets:EUR    100 EUR @@ $110.00
    Assets:USD   $-110.00
```

## Lot Specifications

### Cost Basis

```ledger
2024/01/15 * Buy with Cost
    Assets:Brokerage  10 AAPL {$150.00}
    Assets:Checking  $-1500.00
```

### Lot Date

```ledger
2024/01/15 * Buy with Lot Date
    Assets:Brokerage  10 AAPL {$150.00} [2024/01/15]
    Assets:Checking  $-1500.00
```

### Lot Selection for Sales

```ledger
2024/06/15 * Sell Specific Lot
    Assets:Brokerage  -5 AAPL {$150.00} [2024/01/15] @ $180.00
    Assets:Checking   $900.00
    Income:Capital-Gains
```

## Examples

### Simple Transaction

```ledger
2024/01/15 * Grocery Store
    Expenses:Food:Groceries    $50.00
    Assets:Checking
```

### Multi-currency

```ledger
2024/01/15 * International Purchase
    Expenses:Shopping    100.00 EUR @ $1.10
    Assets:Checking     $-110.00
```

### Complex Transaction

```ledger
2024/01/15=2024/01/20 * (1234) Acme Corp | Monthly invoice payment
    ; Project: acme
    ; Invoice: INV-2024-001
    Expenses:Contractors     $5000.00
        ; Category: development
        ; Tax-deductible: yes
    Expenses:Tax             $500.00
    [Budget:Projects:Acme]  $-5500.00
    Assets:Checking                     = $10000.00
```

## Validation Rules

1. **Balance**: Real postings must sum to zero per commodity
2. **Elision**: Maximum one elided amount per commodity
3. **Date**: Must be valid date
4. **Accounts**: Must be valid account names
5. **Amounts**: Must be valid amount expressions

## See Also

- [Posting Specification](../posting.md)
- [Amounts Specification](../amounts.md)
- [Virtual Postings](../advanced/virtual.md)
