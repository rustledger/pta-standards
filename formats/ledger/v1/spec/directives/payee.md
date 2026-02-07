# Payee Directive

The `payee` directive declares and validates payees (vendors, merchants).

## Syntax

```
payee NAME
    [SUBDIRECTIVE...]
```

## Examples

### Basic Declaration

```ledger
payee Whole Foods
```

### With Subdirectives

```ledger
payee Whole Foods
    alias WholeFds
    alias WHOLEFDS
    note Organic grocery store
```

### With Account Mapping

```ledger
payee Shell Gas Station
    alias SHELL
    alias Shell Oil
    uuid 12345
    note Gas station
```

## Subdirectives

### alias

Create alternative names for payee matching:

```ledger
payee Whole Foods Market
    alias WHOLEFDS
    alias WFM
    alias "WHOLE FOODS"

; All of these match:
2024/01/15 WHOLEFDS #1234
    Expenses:Food    $87.50
    Assets:Checking
```

### note

Add documentation:

```ledger
payee Amazon
    note Online shopping - review for categories
```

### uuid

Assign a unique identifier:

```ledger
payee Acme Corp
    uuid client-001
```

## Payee Matching

Ledger normalizes and matches payees:

```ledger
payee Starbucks Coffee
    alias STARBUCKS
    alias "STARBUCKS STORE"

; These all match the same payee:
2024/01/15 Starbucks Coffee
2024/01/16 STARBUCKS
2024/01/17 starbucks
2024/01/18 STARBUCKS STORE #123
```

## Account Association

In the account directive:

```ledger
account Expenses:Food:Coffee
    payee ^(Starbucks|Peet|Blue Bottle)
```

Transactions with matching payees auto-categorize.

## Regex Patterns

Use regular expressions for flexible matching:

```ledger
payee Amazon
    alias /^AMZN/
    alias /^Amazon\.com/

2024/01/15 AMZN MKTP US*123
    ; Matches Amazon payee
    Expenses:Shopping    $50.00
    Assets:Checking
```

## Unknown Payee Handling

With `--strict` or `--pedantic`:

```bash
ledger --strict -f journal.ledger
```

Undeclared payees generate warnings/errors.

## Payee Reports

### List Payees

```bash
ledger payees
```

### Transactions by Payee

```bash
ledger reg @"Whole Foods"
```

### Payee Statistics

```bash
ledger reg --group-by payee Expenses
```

## Use Cases

### Bank Import Cleanup

```ledger
; Map bank descriptions to clean names
payee Whole Foods Market
    alias WHOLEFDS MKT
    alias WFM #
    alias "WHOLE FOODS"

payee Shell
    alias SHELL OIL
    alias SHELL SERVICE

payee Amazon
    alias AMZN MKTP
    alias AMAZON.COM
    alias AMZN.COM
```

### Vendor Management

```ledger
payee Acme Supplies
    uuid vendor-001
    note Office supply vendor
    ; Last order: 2024/01/15

payee Tech Solutions Inc
    uuid vendor-002
    note IT consulting
```

### Expense Categorization

Combined with account directives:

```ledger
account Expenses:Food:Groceries
    payee ^(Whole Foods|Trader Joe|Safeway|Costco)

account Expenses:Food:Coffee
    payee ^(Starbucks|Peet|Blue Bottle|Philz)

account Expenses:Transportation:Gas
    payee ^(Shell|Chevron|Exxon|BP|Costco Gas)
```

## Querying by Payee

### Exact Match

```bash
ledger reg @"Whole Foods"
```

### Pattern Match

```bash
ledger reg @/Starbucks/
```

### Combined Queries

```bash
ledger reg @"Whole Foods" and Expenses:Food
```

## Best Practices

1. **Declare common payees** at file start
2. **Add aliases** for bank import variations
3. **Use regex patterns** for flexible matching
4. **Document with notes** for context
5. **Combine with account payee** subdirective

## Example: Complete Payee Setup

```ledger
; ===== Payee Declarations =====

; Groceries
payee Whole Foods Market
    alias WHOLEFDS
    alias WFM
    note Organic grocery store

payee Trader Joe's
    alias TRADER JOE
    alias TJ'S
    note Budget-friendly groceries

payee Costco
    alias COSTCO WHSE
    note Bulk shopping

; Coffee
payee Starbucks
    alias STARBUCKS STORE
    alias SBUX
    note Coffee and snacks

; Gas
payee Shell
    alias SHELL OIL
    alias SHELL SERVICE
    note Gas station

payee Chevron
    alias CHEVRON STATION
    note Gas station

; Online
payee Amazon
    alias AMZN MKTP
    alias AMAZON.COM
    alias AMZN.COM
    note Online shopping - check category

; ===== Account Mappings =====

account Expenses:Food:Groceries
    payee ^(Whole Foods|Trader Joe|Costco)

account Expenses:Food:Coffee
    payee ^(Starbucks)

account Expenses:Transportation:Gas
    payee ^(Shell|Chevron)

; ===== Transactions =====

2024/01/15 WHOLEFDS MKT #1234
    Expenses:Food:Groceries    $87.50
    Assets:Checking

2024/01/16 SHELL OIL 54321
    Expenses:Transportation:Gas    $45.00
    Assets:Checking
```

## See Also

- [Account Directive](account.md)
- [Alias Directive](alias.md)
- [Tag Directive](tag.md)
