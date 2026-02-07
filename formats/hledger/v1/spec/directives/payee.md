# Payee Directive

The `payee` directive declares a payee name for validation and completion.

## Syntax

```hledger
payee NAME
```

## Basic Declaration

```hledger
payee Amazon
payee Whole Foods Market
payee Pacific Gas & Electric
```

## Purpose

Payee declarations enable:

1. **Validation** - Check for unknown payees
2. **Completion** - Enable editor autocomplete
3. **Consistency** - Ensure consistent naming

## Validation Mode

With `--strict` or strict checking:

```hledger
payee Amazon
payee Whole Foods

2024-01-15 Amazon              ; OK
    Expenses:Shopping    $50
    Assets:Checking

2024-01-15 Amazonn             ; Warning: unknown payee
    Expenses:Shopping    $50
    Assets:Checking
```

## Payee Names

### Simple Names

```hledger
payee Amazon
payee Target
payee Costco
```

### Names with Special Characters

```hledger
payee McDonald's
payee Trader Joe's
payee AT&T
payee 7-Eleven
```

### Names with Spaces

```hledger
payee Whole Foods Market
payee Pacific Gas & Electric
payee First National Bank
```

## Usage in Transactions

Transaction description is the payee:

```hledger
payee Whole Foods Market

2024-01-15 Whole Foods Market
    Expenses:Food    $75
    Assets:Checking
```

## Multiple Declarations

```hledger
; Grocery stores
payee Whole Foods Market
payee Trader Joe's
payee Safeway
payee Costco

; Utilities
payee Pacific Gas & Electric
payee Water Department
payee Internet Provider

; Restaurants
payee McDonald's
payee Chipotle
payee Starbucks
```

## Combined with Accounts

Often declared together with accounts:

```hledger
; accounts.journal
account Assets:Checking
account Expenses:Food
account Expenses:Utilities

; payees.journal
payee Whole Foods Market
payee Pacific Gas & Electric
payee Starbucks
```

## Auto-Completion

Editors with hledger support use payee declarations for:
- Autocomplete suggestions
- Spell checking
- Fuzzy matching

## Best Practices

1. **Consistent naming** - Use exact same name each time
2. **Avoid abbreviations** - Use full names when possible
3. **Group by category** - Organize payees logically
4. **Update regularly** - Add new payees as encountered

## Complete Example

```hledger
; ===== Payee Declarations =====

; Groceries
payee Whole Foods Market
payee Trader Joe's
payee Safeway
payee Costco Wholesale

; Restaurants
payee Starbucks
payee Chipotle Mexican Grill
payee In-N-Out Burger

; Utilities
payee Pacific Gas & Electric
payee City Water Department
payee Comcast Internet

; Financial
payee Bank of America
payee Fidelity Investments
payee Chase Credit Card

; Shopping
payee Amazon
payee Target
payee Best Buy

; ===== Transactions =====

2024-01-15 Whole Foods Market
    Expenses:Food:Groceries    $85.50
    Assets:Checking

2024-01-15 Starbucks
    Expenses:Food:Coffee    $6.75
    Assets:Cash

2024-01-20 Pacific Gas & Electric
    Expenses:Utilities:Electric    $125.00
    Assets:Checking
```

## Command Line

```bash
# List all payees
hledger payees

# Check for unknown payees
hledger check payees
```

## See Also

- [Account Directive](account.md)
- [Transaction Directive](transaction.md)
- [Tag Directive](tag.md)
