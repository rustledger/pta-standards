# Posting Specification

A posting represents a single line item within a transaction, recording a change to an account's balance.

## Syntax

```
    [STATUS] ACCOUNT  [AMOUNT] [@ PRICE | @@ TOTAL] [= BALANCE] [; COMMENT]
```

## Components

### Indentation

Postings MUST be indented:

```hledger
2024-01-15 Transaction
    Expenses:Food    $50.00     ; Indented with spaces
	Assets:Checking            ; Indented with tab
```

Minimum: 1 space or 1 tab. Convention: 2-4 spaces.

### Account

The account being affected:

```hledger
    Expenses:Food:Groceries    $50.00
    Assets:Bank:Checking      $-50.00
```

### Amount

The quantity and commodity:

```hledger
    Expenses:Food     $50.00        ; Positive
    Assets:Checking  $-50.00        ; Negative
    Assets:Stock      10 AAPL       ; Shares
    Assets:Checking                 ; Elided (calculated)
```

### Price Annotation (@)

Per-unit market price:

```hledger
    Assets:Stock    10 AAPL @ $150.00
    ; 10 shares at $150 each
```

### Total Price (@@)

Total price for all units:

```hledger
    Assets:EUR    100 EUR @@ $110.00
    ; 100 EUR for $110 total
```

### Balance Assertion (=)

Assert balance after posting:

```hledger
    Assets:Checking    $100 = $1500
    ; Balance must be $1500 after
```

### Balance Assignment

Set balance to specific value:

```hledger
    Assets:Checking    = $1500
    ; Set balance TO $1500, infer amount
```

### Comment

End-of-line comment:

```hledger
    Expenses:Food    $50.00  ; Weekly groceries
```

## Amount Elision

One posting per commodity can omit amount:

```hledger
2024-01-15 Transaction
    Expenses:Food    $50.00
    Assets:Checking          ; Calculated as $-50.00
```

### Multiple Commodities

```hledger
2024-01-15 Multi-currency
    Assets:EUR    100 EUR
    Assets:USD              ; Elided USD amount
    Expenses:Fees    5 EUR
```

### Elision Rules

1. Only ONE posting per commodity can be elided
2. Elided amount is calculated to balance transaction
3. Error if transaction cannot balance

## Balance Assertions

### Single-Commodity Assertion (=)

```hledger
    Assets:Checking    $100 = $1500
    ; After this posting, USD balance is $1500
```

### Subaccount-Inclusive Assertion (=*)

```hledger
    Assets:Bank    $0 =* $5000
    ; Assert Assets:Bank plus all subaccounts = $5000
```

### Zero Assertion

```hledger
    Assets:Checking    $0 = $0
    ; Confirm account is empty
```

## Balance Assignments

### Set Balance

```hledger
2024-01-15 Reconciliation
    Assets:Checking    = $1234.56
    ; Calculate amount needed to reach $1234.56
    Equity:Adjustments
```

### With Amount

```hledger
2024-01-15 Deposit
    Assets:Checking    $500 = $1734.56
    ; Add $500, assert new balance is $1734.56
    Income:Gift
```

## Virtual Postings

### Unbalanced Virtual (Parentheses)

```hledger
    (Budget:Food)    $-50.00
    ; Not included in balance
```

### Balanced Virtual (Brackets)

```hledger
    [Savings:Goal]    $-50.00
    ; Must balance with other [] postings
```

### Example

```hledger
2024-01-15 Expense with Budget
    Expenses:Food        $50.00    ; Real
    (Budget:Food)       $-50.00    ; Virtual unbalanced
    Assets:Checking     $-50.00    ; Real

2024-01-15 Savings Allocation
    Assets:Checking      $100.00   ; Real
    [Savings:Emergency]  $-50.00   ; Virtual balanced
    [Savings:Vacation]   $-50.00   ; Virtual balanced
    Income:Salary                  ; Real
```

## Posting Metadata

### Comments

```hledger
    Expenses:Food    $50.00  ; Receipt #1234
```

### Tags

```hledger
    Expenses:Food    $50.00
        ; category:groceries, location:downtown
```

### Multi-Line Metadata

```hledger
    Expenses:Food    $50.00
        ; vendor:Whole Foods
        ; receipt:IMG_001.jpg
```

## Posting Status

Status can be on individual postings:

```hledger
2024-01-15 Mixed Transaction
    * Expenses:Food    $30.00    ; Cleared
    ! Expenses:Misc    $20.00    ; Pending
    Assets:Checking
```

## Posting Dates

### Using Tags

```hledger
    Expenses:Bill    $100  ; date:2024-01-20
```

### Bracket Syntax

```hledger
    Expenses:Bill    $100  ; [2024-01-20]
```

### Secondary Date

The posting date overrides transaction date for this posting in date-filtered reports.

## Two-Space Rule

At least two spaces (or a tab) required between account and amount:

```hledger
    Expenses:Food  $50.00    ; Correct: 2 spaces
    Expenses:Food $50.00     ; WRONG: parsed as "Expenses:Food $50.00"
```

## Account Separators

```hledger
    Assets:Bank:Checking    ; Colon-separated
```

## Whitespace Handling

- Leading whitespace: Required for posting (indent)
- Account/amount separator: 2+ spaces or tab
- Trailing whitespace: Ignored

## Validation Rules

1. **Account required** - Every posting needs an account
2. **Amount optional** - Can be elided if calculable
3. **Indentation required** - Must be indented
4. **Two-space separation** - Between account and amount
5. **Balance assertions** - Checked at parse time

## Examples

### Simple Posting

```hledger
    Expenses:Food    $50.00
```

### With Balance Assertion

```hledger
    Assets:Checking    $100 = $1500
```

### Virtual with Metadata

```hledger
    (Budget:Food)    $-50.00
        ; category:variable
        ; period:monthly
```

### Stock Purchase

```hledger
    Assets:Brokerage:AAPL    10 AAPL @ $150.00
```

### Complete Example

```hledger
2024-01-15 * Grocery shopping
    ; trip:weekly
    Expenses:Food:Groceries    $75.00
        ; store:Whole Foods
    Expenses:Food:Snacks    $15.00
    (Budget:Food)    $-90.00
    Assets:Checking    = $1234.56
        ; reconciled:true
```

## See Also

- [Amounts Specification](amounts.md)
- [Transaction Directive](directives/transaction.md)
- [Syntax Specification](syntax.md)
