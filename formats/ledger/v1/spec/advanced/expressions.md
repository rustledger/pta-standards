# Value Expressions Specification

This document specifies value expressions in Ledger.

## Overview

Value expressions are a powerful feature enabling:
- Calculated amounts
- Conditional logic
- Query filtering
- Automated transaction rules
- Report formatting

## Expression Contexts

### In Amounts

```ledger
2024/01/15 Calculated
    Expenses:A    ($100 / 3)
    Expenses:B    ($100 / 3)
    Expenses:C    ($100 / 3)
    Assets:Cash
```

### In Automated Transactions

```ledger
= expr account =~ /Expenses/
    (Tracking)  amount
```

### In Queries

```bash
ledger reg expr 'amount > 100'
```

### In Format Strings

```bash
ledger reg --format "%(date) %(payee): %(amount)\n"
```

## Arithmetic Operators

### Basic Math

| Operator | Meaning |
|----------|---------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulo |

### Examples

```ledger
($100 + $50)      ; $150
($100 - $50)      ; $50
($100 * 2)        ; $200
($100 / 4)        ; $25
(17 % 5)          ; 2
```

### Negation

```ledger
(-$100)           ; Negative $100
(amount * -1)     ; Negate amount
```

## Comparison Operators

| Operator | Meaning |
|----------|---------|
| `==` | Equal |
| `!=` | Not equal |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal |
| `>=` | Greater than or equal |
| `=~` | Regex match |
| `!~` | Regex not match |

### Examples

```ledger
= expr amount > $100
    (Large)  1

= expr account =~ /^Expenses/
    (Track)  amount
```

## Logical Operators

| Operator | Meaning |
|----------|---------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

### Examples

```ledger
= expr amount > $50 and account =~ /Food/
    (Budget:Food)  -1

= expr not has_tag("reviewed")
    (Pending:Review)  1
```

## Built-in Variables

### Transaction Variables

| Variable | Type | Description |
|----------|------|-------------|
| `date` | Date | Transaction date |
| `effective_date` | Date | Effective date |
| `payee` | String | Transaction payee |
| `note` | String | Transaction note |
| `code` | String | Transaction code |
| `cleared` | Boolean | Is cleared? |
| `pending` | Boolean | Is pending? |

### Posting Variables

| Variable | Type | Description |
|----------|------|-------------|
| `account` | String | Account name |
| `amount` | Amount | Posting amount |
| `total` | Amount | Running total |
| `cost` | Amount | Cost basis |
| `price` | Amount | Price annotation |
| `commodity` | String | Commodity symbol |
| `quantity` | Number | Numeric quantity |

### Report Variables

| Variable | Type | Description |
|----------|------|-------------|
| `today` | Date | Current date |
| `now` | DateTime | Current time |
| `depth` | Number | Account depth |
| `count` | Number | Transaction count |

## Functions

### Amount Functions

```ledger
abs(amount)          ; Absolute value
round(amount)        ; Round to precision
floor(amount)        ; Round down
ceiling(amount)      ; Round up
truncate(amount)     ; Truncate decimals
```

### Aggregation Functions

```ledger
total(account)       ; Sum of account
sum(expr)            ; Sum of expression
count(expr)          ; Count matching
min(expr)            ; Minimum value
max(expr)            ; Maximum value
average(expr)        ; Average value
```

### String Functions

```ledger
format(value, fmt)   ; Format value
join(list, sep)      ; Join with separator
trim(string)         ; Trim whitespace
```

### Date Functions

```ledger
date                 ; Transaction date
today                ; Current date
year(date)           ; Extract year
month(date)          ; Extract month
day(date)            ; Extract day
```

### Tag Functions

```ledger
has_tag(name)        ; Check for tag
tag(name)            ; Get tag value
```

### Account Functions

```ledger
account              ; Account name
parent               ; Parent account
depth                ; Account depth level
any(predicate)       ; Any match
all(predicate)       ; All match
```

## Conditional Expressions

### Ternary Operator

```ledger
(condition ? true_value : false_value)
```

### Examples

```ledger
= expr account =~ /Income/
    (Taxes)  (amount > $1000 ? amount * 0.25 : amount * 0.15)
```

## Regular Expressions

### Syntax

```ledger
/pattern/            ; Match pattern
```

### Account Matching

```ledger
= expr account =~ /^Expenses:Food/
    (Budget:Food)  -1

= expr account =~ /^Income/
    (Tracking:Income)  amount
```

### Payee Matching

```ledger
= expr payee =~ /Grocery|Market/
    ; :food:
```

## Date Expressions

### Date Literals

```ledger
[2024/01/15]         ; Specific date
[today]              ; Current date
[this month]         ; Current month
```

### Date Comparisons

```ledger
= expr date >= [2024/01/01]
    (Year:2024)  amount

= expr date < [today]
    (Historical)  1
```

## Complex Examples

### Tax Calculation

```ledger
= expr account =~ /^Income:Salary/
    (Taxes:Federal)   (amount * 0.22)
    (Taxes:State)     (amount * 0.05)
    (Taxes:FICA)      (amount * 0.0765)
    (Net:Income)      (amount * (1 - 0.22 - 0.05 - 0.0765))
```

### Tiered Commission

```ledger
= expr account =~ /Income:Sales/ and amount > $10000
    (Commission)   (amount * 0.15)

= expr account =~ /Income:Sales/ and amount <= $10000
    (Commission)   (amount * 0.10)
```

### Category Detection

```ledger
= expr payee =~ /Amazon|Best Buy|Walmart/
    ; :shopping:

= expr payee =~ /Uber|Lyft/
    ; :transportation:

= expr amount < $0 and account =~ /Assets:Checking/
    (Outflows)  (amount * -1)
```

### Savings Rate

```ledger
= expr account =~ /^Income/
    (Stats:Income)  amount

= expr account =~ /^Expenses/
    (Stats:Expenses)  amount

; Savings = Income - Expenses
```

### Large Transaction Alert

```ledger
= expr abs(amount) > $1000
    ; :large:
    (Review:Large)  amount
```

## Format Expressions

### Basic Format

```bash
ledger reg --format "%(date) %(payee)\n"
```

### Conditional Formatting

```bash
ledger reg --format "%(date) %(ansify_if(amount > 100, \"red\"))%(amount)%(ansify_end)\n"
```

### Alignment

```bash
ledger bal --format "%(20(account)) %(12(total))\n"
```

## Error Handling

### Division by Zero

```
X-001: Division by zero
  Line 5:     Expenses:A    ($100 / 0)
  Cannot divide by zero
```

### Type Mismatch

```
X-002: Type mismatch in expression
  Line 10: assert $100 + "text"
  Cannot add amount and string
```

### Undefined Variable

```
X-003: Undefined variable
  Line 15: = expr unknown_var > 0
  Variable 'unknown_var' is not defined
```

## Best Practices

1. **Parenthesize** - Use parentheses for clarity
2. **Test expressions** - Verify with simple cases first
3. **Document complex logic** - Add comments
4. **Use functions** - Prefer built-ins over complex expressions
5. **Handle edge cases** - Consider zero amounts, missing data
6. **Keep it simple** - Break complex expressions into parts

## See Also

- [Automated Transactions](automated.md)
- [Lexical Specification](../lexical.md)
- [Error Codes](../errors.md)
