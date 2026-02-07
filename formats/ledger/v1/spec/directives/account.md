# Account Directive

The `account` directive declares an account and its properties.

## Syntax

```
account ACCOUNT_NAME
    [SUBDIRECTIVE...]
```

## Examples

### Basic Declaration

```ledger
account Assets:Checking
```

### With Subdirectives

```ledger
account Assets:Checking
    note My primary checking account
    alias checking
    default
```

### Full Example

```ledger
account Expenses:Food:Groceries
    note Weekly grocery expenses
    alias groceries
    alias food
    payee ^(Whole Foods|Trader Joe|Safeway)
    check commodity == "$"
    assert amount < 500
```

## Subdirectives

### note

Adds a description to the account:

```ledger
account Assets:Savings
    note Emergency fund - do not touch
```

### alias

Creates a shorthand name for the account:

```ledger
account Expenses:Transportation:Gas
    alias gas
    alias fuel

; Now you can use:
2024/01/15 Shell
    gas    $50.00
    Assets:Checking
```

Multiple aliases can be defined for one account.

### payee

Associates payee patterns with the account:

```ledger
account Expenses:Food:Restaurants
    payee ^(Chipotle|McDonald|Starbucks)

; Transactions with matching payees auto-categorize
2024/01/15 Chipotle
    Expenses:Food:Restaurants    $12.00
    Assets:Checking
```

### check

Defines a validation check for postings:

```ledger
account Assets:Checking
    check commodity == "$"
    check amount >= -1000
```

### assert

Similar to check but causes an error if false:

```ledger
account Assets:Savings
    assert amount >= 0  ; Must never go negative
```

### default

Marks as the default account for unbalanced transactions:

```ledger
account Assets:Checking
    default

; This transaction auto-balances to Assets:Checking
2024/01/15 Grocery Store
    Expenses:Food    $50.00
```

### eval

Executes an expression when account is referenced:

```ledger
account Assets:Brokerage
    eval print("Brokerage account accessed")
```

## Account Types

Ledger recognizes these root account types:

| Type | Description |
|------|-------------|
| `Assets` | Things you own |
| `Liabilities` | Things you owe |
| `Income` | Money received |
| `Expenses` | Money spent |
| `Equity` | Net worth adjustments |

Custom root types are also allowed.

## Implicit Declaration

Accounts are implicitly declared on first use:

```ledger
; No explicit declaration needed
2024/01/15 Transaction
    Expenses:Food    $50.00
    Assets:Checking
```

However, explicit declaration enables:
- Aliases
- Validation rules
- Documentation
- Payee matching

## Validation

With `--strict` or `--pedantic` flags, Ledger can require explicit account declarations.

```bash
ledger --strict -f journal.ledger balance
```

## See Also

- [Alias Directive](alias.md)
- [Bucket Directive](bucket.md)
- [Posting Specification](../posting.md)
