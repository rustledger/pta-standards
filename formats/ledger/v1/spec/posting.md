# Posting Specification

A posting represents a single line item within a transaction, recording a change to an account's balance.

## Syntax

```
    ACCOUNT  [AMOUNT] [@ PRICE | @@ TOTAL] [= BALANCE] [; COMMENT]
```

## Components

### Indentation

Postings MUST be indented:

```ledger
2024/01/15 Transaction
    Expenses:Food    $50.00     ; Indented with spaces
	Assets:Checking            ; Indented with tab
```

Minimum: 1 space or 1 tab. Convention: 4 spaces or 1 tab.

### Account

The account being affected:

```ledger
    Expenses:Food:Groceries    $50.00
    Assets:Bank:Checking      $-50.00
```

### Amount

The quantity and commodity:

```ledger
    Expenses:Food     $50.00        ; Positive
    Assets:Checking  $-50.00        ; Negative
    Assets:Stock      10 AAPL       ; Shares
    Assets:Checking                 ; Elided (calculated)
```

### Price Annotation (@)

Per-unit market price:

```ledger
    Assets:Stock    10 AAPL @ $150.00
    ; 10 shares at $150 each
```

### Total Price (@@)

Total price for all units:

```ledger
    Assets:EUR    100 EUR @@ $110.00
    ; 100 EUR for $110 total
```

### Balance Assertion (=)

Assert balance after posting:

```ledger
    Assets:Checking    $100 = $1500
    ; Balance must be $1500 after
```

### Comment

End-of-line comment:

```ledger
    Expenses:Food    $50.00  ; Weekly groceries
```

## Amount Elision

One posting per commodity can omit amount:

```ledger
2024/01/15 Transaction
    Expenses:Food    $50.00
    Assets:Checking          ; Calculated as $-50.00
```

### Multiple Commodities

```ledger
2024/01/15 Multi-currency
    Assets:EUR    100 EUR
    Assets:USD              ; Elided USD amount
    Expenses:Fees    5 EUR
```

### Elision Rules

1. Only ONE posting per commodity can be elided
2. Elided amount is calculated to balance transaction
3. Error if transaction cannot balance

## Price Annotations

### Per-Unit Price (@)

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 AAPL @ $150.00
    ; Implies $1500 total
    Assets:Checking    $-1500.00
```

### Total Price (@@)

```ledger
2024/01/15 Currency Exchange
    Assets:EUR    100 EUR @@ $110.00
    ; Total is $110 (not 100 * $110)
    Assets:Checking    $-110.00
```

### Price vs Cost

| Syntax | Meaning |
|--------|---------|
| `@ $150` | Market price per unit |
| `{$150}` | Cost basis per unit |

## Cost Basis

### Per-Unit Cost

```ledger
    Assets:Brokerage    10 AAPL {$150.00}
    ; Cost basis: $150 per share
```

### Total Cost

```ledger
    Assets:Brokerage    10 AAPL {{$1500.00}}
    ; Total cost: $1500
```

### Cost with Date

```ledger
    Assets:Brokerage    10 AAPL {$150.00} [2024/01/15]
    ; Acquired on 2024/01/15
```

### Cost with Lot Label

```ledger
    Assets:Brokerage    10 AAPL {$150.00} (lot1)
    ; Named lot for tracking
```

### Full Cost Specification

```ledger
    Assets:Brokerage    10 AAPL {$150.00} [2024/01/15] (lot1) @ $180.00
    ; Cost $150, acquired 01/15, labeled "lot1", current price $180
```

## Balance Assertions

### After Posting

```ledger
    Assets:Checking    $100 = $1500
    ; After this posting, balance is $1500
```

### Commodity-Specific

```ledger
    Assets:Brokerage    10 AAPL = 50 AAPL
    ; Assert 50 AAPL (ignores other commodities)
```

### Total Balance

```ledger
    Assets:Checking    $100 == $1500
    ; Double = asserts total (all commodities)
```

## Virtual Postings

### Unbalanced Virtual ()

```ledger
    (Budget:Food)    $-50.00
    ; Not included in balance
```

### Balanced Virtual []

```ledger
    [Savings:Goal]    $-50.00
    ; Must balance with other [] postings
```

### Example

```ledger
2024/01/15 Expense with Budget
    Expenses:Food        $50.00    ; Real
    (Budget:Food)       $-50.00    ; Virtual unbalanced
    Assets:Checking     $-50.00    ; Real

2024/01/15 Savings Allocation
    Assets:Checking      $100.00   ; Real
    [Savings:Emergency]  $-50.00   ; Virtual balanced
    [Savings:Vacation]   $-50.00   ; Virtual balanced
    Income:Salary                  ; Real
```

## Posting Metadata

### Comments

```ledger
    Expenses:Food    $50.00  ; Receipt #1234
```

### Metadata

```ledger
    Expenses:Food    $50.00
        ; Category: groceries
        ; Receipt: IMG_001.jpg
```

### Tags

```ledger
    Expenses:Food    $50.00
        ; :groceries:weekly:
```

## Posting Flags

Status can be on individual postings:

```ledger
2024/01/15 Mixed Transaction
    * Expenses:Food    $30.00    ; Cleared
    ! Expenses:Misc    $20.00    ; Pending
    Assets:Checking
```

## Examples

### Simple Posting

```ledger
    Expenses:Food    $50.00
```

### With All Components

```ledger
    Assets:Brokerage    10 AAPL {$150.00} [2024/01/15] (lot1) @ $180.00 = 50 AAPL  ; Purchase
```

### Virtual with Metadata

```ledger
    (Budget:Food)    $-50.00
        ; category: variable
        ; :monthly-budget:
```

## Validation Rules

1. **Account required** - Every posting needs an account
2. **Amount optional** - Can be elided if calculable
3. **Indentation required** - Must be indented
4. **Price/cost match** - Commodity and price commodity differ
5. **Balance assertions** - Checked at parse time

## See Also

- [Amounts Specification](amounts.md)
- [Transaction Directive](directives/transaction.md)
- [Virtual Postings](advanced/virtual.md)
