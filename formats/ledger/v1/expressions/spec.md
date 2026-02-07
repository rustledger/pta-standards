# Value Expressions Specification

Ledger's value expression language allows arithmetic, conditionals, and function calls within the ledger file.

## Overview

Value expressions appear in:
- Amounts: `($100 * 2)`
- Automated transactions: `= expr account =~ /Expenses/`
- Assertions: `assert total(Assets) > 0`
- Report formatting: `--format` option

## Basic Arithmetic

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `$100 + $50` |
| `-` | Subtraction | `$100 - $25` |
| `*` | Multiplication | `$100 * 2` |
| `/` | Division | `$100 / 4` |
| `%` | Modulo | `$100 % 30` |
| `-` | Negation | `-$50` |

### Precedence

1. Parentheses `()`
2. Unary minus `-`
3. Multiplication, Division, Modulo `* / %`
4. Addition, Subtraction `+ -`

### Examples

```ledger
2024/01/15 Split Bill
    Expenses:Food    ($150 / 3)
    Assets:Checking

2024/01/15 Tax
    Expenses:Tax     ($1000 * 0.25)
    Assets:Checking

2024/01/15 Complex
    Expenses:A       (($100 + $50) * 2 / 3)
    Assets:Checking
```

## Comparison Operators

| Operator | Description |
|----------|-------------|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less or equal |
| `>=` | Greater or equal |
| `=~` | Regex match |
| `!~` | Regex not match |

### Examples

```ledger
assert account == $1000
assert amount != $0
assert total(Assets) > total(Liabilities)
```

## Logical Operators

| Operator | Description |
|----------|-------------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

### Examples

```ledger
assert account >= $0 and account <= $10000
assert total(Assets) > 0 or total(Income) > 0
assert not (account < $0)
```

## String Operations

### Regex Matching

```ledger
= expr account =~ /Expenses:Food/
    (Budget:Food)  -1

= expr payee =~ /^Whole Foods/
    ; :groceries:
```

### String Functions

```ledger
= expr commodity == "USD"
    ; tag: us-currency
```

## Variables

### Built-in Variables

| Variable | Description |
|----------|-------------|
| `account` | Current account |
| `amount` | Posting amount |
| `total` | Running total |
| `date` | Transaction date |
| `payee` | Transaction payee |
| `note` | Transaction note |
| `commodity` | Amount commodity |
| `quantity` | Numeric quantity |

### Usage

```ledger
= expr amount > $100
    ; :large-expense:

= expr date >= [2024/01/01]
    ; :this-year:
```

## Conditional Expressions

### If-Then-Else

```ledger
= expr (amount > $100 ? "large" : "small")
```

### In Assertions

```ledger
assert (has_transactions ? total(Assets) > 0 : true)
```

## Date Expressions

### Date Literals

```ledger
[2024/01/15]
[2024/01]
[2024]
```

### Date Arithmetic

```ledger
= expr date >= [2024/01/01] and date < [2025/01/01]
    ; :year-2024:
```

### Special Dates

| Variable | Description |
|----------|-------------|
| `today` | Current date |
| `now` | Current datetime |

## Amount Expressions

### In Postings

```ledger
2024/01/15 Calculated Amount
    Expenses:Food    ($price * $quantity)
    Assets:Checking
```

### With Functions

```ledger
2024/01/15 Rounded
    Expenses:Food    (round($33.333))
    Assets:Checking
```

## Automated Transaction Expressions

### Basic Match

```ledger
= /Grocery/
    (Budget:Food)  -1
```

### Expression Match

```ledger
= expr account =~ /Expenses/ and amount > $50
    ; :review-needed:
```

### Value Calculation

```ledger
= expr account =~ /Expenses:Food/
    (Budget:Food)  (amount * -1)
```

## Report Expressions

### Format Strings

```bash
ledger -f journal.ledger reg --format "%(date) %(payee) %(amount)\n"
```

### Calculations in Reports

```bash
ledger -f journal.ledger bal --format "%(account): %(market(display_total))\n"
```

## Expression Grammar

```ebnf
expression = or_expr ;

or_expr = and_expr { "or" and_expr } ;

and_expr = not_expr { "and" not_expr } ;

not_expr = "not" not_expr | comparison ;

comparison = additive { comparison_op additive } ;

comparison_op = "==" | "!=" | "<" | ">" | "<=" | ">=" | "=~" | "!~" ;

additive = multiplicative { ("+" | "-") multiplicative } ;

multiplicative = unary { ("*" | "/" | "%") unary } ;

unary = "-" unary | primary ;

primary = number | string | date | variable | function_call | "(" expression ")" ;

function_call = identifier "(" [ expression { "," expression } ] ")" ;
```

## Type Coercion

| From | To | Method |
|------|-----|--------|
| Amount | Number | Extract quantity |
| String | Amount | Parse |
| Boolean | Number | 0/1 |
| Number | Boolean | 0=false |

## Error Handling

### Division by Zero

```ledger
; Error: division by zero
    Expenses:A    ($100 / $0)
```

### Type Mismatch

```ledger
; Error: cannot compare amount with string
assert $100 == "hundred"
```

## Best Practices

1. **Use parentheses** for clarity
2. **Test expressions** with simple cases first
3. **Avoid complex nesting** when possible
4. **Document calculations** with comments
5. **Consider precision** in division

## Examples

### Tax Calculation

```ledger
2024/01/15 Income with Tax
    Assets:Checking    $3000
    Expenses:Tax       ($3000 * 0.22)
    Income:Salary

; Or using variables
= expr account == "Income:Salary"
    Expenses:Tax    (amount * -0.22)
```

### Percentage Split

```ledger
2024/01/15 Shared Expense
    Expenses:Rent    $1500
    Assets:Alice     ($1500 * 0.50)
    Assets:Bob       ($1500 * 0.30)
    Assets:Carol     ($1500 * 0.20)
```

### Currency Conversion

```ledger
2024/01/15 International
    Expenses:Travel    ($hotel_eur * $eur_rate)
    Assets:Checking
```

## See Also

- [Functions Reference](functions.md)
- [Automated Transactions](../spec/advanced/automated.md)
- [Amounts Specification](../spec/amounts.md)
