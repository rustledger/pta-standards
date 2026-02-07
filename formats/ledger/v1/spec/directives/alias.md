# Alias Directive

The `alias` directive creates a shorthand name for an account.

## Syntax

```
alias ALIAS = ACCOUNT
```

Or as an account subdirective:

```
account ACCOUNT
    alias ALIAS
```

## Examples

### Basic Alias

```ledger
alias checking = Assets:Bank:Checking

2024/01/15 Deposit
    checking    $1000.00
    Income:Salary
```

### Multiple Aliases

```ledger
alias checking = Assets:Bank:Checking
alias savings = Assets:Bank:Savings
alias cc = Liabilities:CreditCard:Visa

2024/01/15 Transfer
    savings     $500.00
    checking   $-500.00
```

### As Account Subdirective

```ledger
account Assets:Bank:Checking
    alias checking
    alias chk

account Expenses:Food:Groceries
    alias groceries
    alias food
```

## Use Cases

### Short Names

```ledger
; Long account names
alias food = Expenses:Food:Groceries
alias rent = Expenses:Housing:Rent
alias utils = Expenses:Housing:Utilities

2024/01/15 Weekly shopping
    food    $150.00
    checking

2024/01/01 Monthly rent
    rent    $1500.00
    checking
```

### Category Shortcuts

```ledger
alias personal = Expenses:Personal
alias business = Expenses:Business

2024/01/15 Office supplies
    business    $50.00
    Assets:Checking
```

### Import Mapping

```ledger
; Map bank CSV categories to accounts
alias GROCERY = Expenses:Food:Groceries
alias GAS = Expenses:Transportation:Gas
alias RESTAURANT = Expenses:Food:Restaurants
```

## Alias Resolution

Aliases are resolved during parsing:

```ledger
alias chk = Assets:Checking

2024/01/15 Test
    chk    $100    ; Becomes Assets:Checking
    Income:Salary
```

The alias is replaced with the full account name.

## Scope

Aliases are global once defined:

```ledger
alias food = Expenses:Food

; All subsequent uses of 'food' resolve to Expenses:Food
```

## Alias vs Account Alias

### Standalone Alias

```ledger
alias groceries = Expenses:Food:Groceries
```

### Account Subdirective Alias

```ledger
account Expenses:Food:Groceries
    alias groceries
```

Both achieve the same result, but the subdirective form keeps the alias with its account definition.

## Regex Aliases

Ledger supports regex-based account transformation:

```ledger
alias /^Exp:/ = Expenses:
alias /^Inc:/ = Income:

2024/01/15 Transaction
    Exp:Food    $50    ; Becomes Expenses:Food
    Inc:Salary         ; Becomes Income:Salary
```

## Removing Aliases

Use `unalias` to remove:

```ledger
alias food = Expenses:Food:Groceries

; Later in file...
unalias food
```

## Best Practices

1. **Define aliases at top** of main ledger file
2. **Use short, memorable names**
3. **Document alias meanings** with comments
4. **Be consistent** across files
5. **Avoid ambiguous names**

## Example: Complete Setup

```ledger
; ===== Account Aliases =====

; Assets
alias checking = Assets:Bank:Checking
alias savings = Assets:Bank:Savings
alias cash = Assets:Cash

; Liabilities
alias visa = Liabilities:CreditCard:Visa
alias amex = Liabilities:CreditCard:Amex

; Expenses
alias food = Expenses:Food:Groceries
alias dining = Expenses:Food:Restaurants
alias gas = Expenses:Transportation:Gas
alias rent = Expenses:Housing:Rent

; Income
alias salary = Income:Salary
alias bonus = Income:Bonus

; ===== Transactions =====

2024/01/15 * Grocery Store
    food    $75.00
    visa

2024/01/15 * Gas Station
    gas    $45.00
    checking
```

## Conflicts

If an alias conflicts with an account name, the alias takes precedence:

```ledger
account Food
alias Food = Expenses:Food

2024/01/15 Test
    Food    $50    ; Uses alias (Expenses:Food), not account
    Checking
```

## See Also

- [Account Directive](account.md)
- [Payee Directive](payee.md)
