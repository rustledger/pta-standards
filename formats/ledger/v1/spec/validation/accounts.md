# Account Validation Specification

This document specifies account validation rules in Ledger.

## Overview

Account validation ensures:
- Account names are well-formed
- Declared accounts exist
- Account types are consistent
- Account hierarchies are valid

## Account Name Rules

### Valid Characters

```
segment = (letter | digit | space | "-" | "_" | "'")+
account = segment (":" segment)+
```

### Valid Names

```ledger
Assets:Bank:Checking
Expenses:Food & Dining
Liabilities:Credit-Card
Income:Salary_2024
Assets:John's Account
```

### Invalid Names

```ledger
; Empty segment
Assets::Checking           ; ERROR: Empty segment

; Leading colon
:Assets:Checking           ; ERROR: Leading colon

; Trailing colon
Assets:Checking:           ; ERROR: Trailing colon

; Invalid characters
Assets:Bank@Home           ; ERROR: @ not allowed
Expenses:50%Off            ; ERROR: % not allowed
```

### Error: Invalid Account Name

```
P-007: Invalid account name
  Line 3:     :Empty:Segment    $50
  Account segments cannot be empty
```

## Account Declaration

### Optional Declaration

By default, accounts are created implicitly:

```ledger
2024/01/15 Transaction
    Expenses:Food    $50    ; Created implicitly
    Assets:Checking         ; Created implicitly
```

### Explicit Declaration

```ledger
account Expenses:Food
account Assets:Checking

2024/01/15 Transaction
    Expenses:Food    $50
    Assets:Checking
```

### Declaration with Metadata

```ledger
account Expenses:Food
    ; For grocery and restaurant expenses
    note Food and dining expenses
    alias food

account Assets:Bank:Checking
    note Primary checking account
    assert amount >= 0
```

## Strict Mode

### Enforcing Declarations

```bash
ledger --strict bal
```

In strict mode, undeclared accounts cause errors:

```
V-004: Account not declared
  Line 5:     Expenses:Foood    $50
  Account 'Expenses:Foood' not found
  Did you mean: Expenses:Food ?
```

### Pedantic Mode

```bash
ledger --pedantic bal
```

Even stricter validation:
- All accounts must be declared
- Account types must be specified
- Warns on unusual patterns

## Account Types

### Standard Types

| Type | Typical Prefixes |
|------|------------------|
| Asset | `Assets:` |
| Liability | `Liabilities:` |
| Equity | `Equity:` |
| Income | `Income:`, `Revenue:` |
| Expense | `Expenses:` |

### Type Inference

Ledger infers type from account name prefix:

```ledger
Assets:Checking        ; Type: Asset
Liabilities:Mortgage   ; Type: Liability
Equity:Opening         ; Type: Equity
Income:Salary          ; Type: Income
Expenses:Food          ; Type: Expense
```

### Explicit Type

```ledger
account Assets:Receivable
    type: Asset

account Liabilities:Payable
    type: Liability
```

### Type Override

Override inferred type when needed:

```ledger
account Assets:Short-Term-Debt
    type: Liability    ; Actually a liability
```

## Account Hierarchy

### Parent-Child Relationship

Accounts form a tree:

```
Assets
├── Bank
│   ├── Checking
│   └── Savings
├── Cash
└── Investments
    ├── Stocks
    └── Bonds
```

### Implicit Parent Creation

Using a child creates parents implicitly:

```ledger
2024/01/15 Transaction
    Assets:Bank:Checking    $100
    ; Creates: Assets, Assets:Bank, Assets:Bank:Checking
    Income:Salary
```

### Explicit Parent Declaration

```ledger
account Assets
    ; Top-level asset account

account Assets:Bank
    ; Bank accounts

account Assets:Bank:Checking
    ; Primary checking
```

## Account Aliases

### Defining Aliases

```ledger
alias food = Expenses:Food:Groceries
alias rent = Expenses:Housing:Rent
```

### Using Aliases

```ledger
2024/01/15 Grocery
    food    $50    ; Expands to Expenses:Food:Groceries
    Assets:Checking
```

### Alias Validation

```
V-013: Alias target not found
  Line 5: alias foo = NonExistent:Account
  Account 'NonExistent:Account' not declared
```

## Duplicate Declarations

### Error on Redeclaration

```ledger
account Assets:Checking
    note Primary account

account Assets:Checking    ; ERROR
    note Different note
```

```
V-007: Duplicate account declaration
  Line 5: account Assets:Checking
  Previously declared at line 1
```

### Allowed: Additive Metadata

Some implementations allow adding metadata:

```ledger
account Assets:Checking
    note Primary account

account Assets:Checking
    alias checking    ; Adds alias to existing declaration
```

## Virtual Account Validation

### Parentheses (Unbalanced)

```ledger
(Budget:Food)           ; Valid virtual account
(Budget:Savings:Goal)   ; Valid nested virtual
```

### Brackets (Balanced)

```ledger
[Savings:Goal]          ; Valid balanced virtual
[Assets:Reserve]        ; Valid balanced virtual
```

### Virtual Name Rules

Same naming rules apply:

```ledger
(Budget::Empty)         ; ERROR: Empty segment
[Bad@Character]         ; ERROR: Invalid character
```

## Account Assertions

### Balance Constraints

```ledger
account Assets:Checking
    assert amount >= 0
```

### Expression Assertions

```ledger
account Assets:Investments
    assert total >= $1000
```

### Assertion Failure

```
V-010: Assertion failed
  Line 50: Assets:Checking assertion
  Assertion: amount >= 0
  Actual: $-500
```

## Typo Detection

### Levenshtein Distance

When an undeclared account is used, suggest similar:

```
V-004: Account not declared
  Line 10:     Expenses:Foood    $50
  Account 'Expenses:Foood' not found
  Did you mean: Expenses:Food ?
```

### Common Misspellings

- `Expences` → `Expenses`
- `Assetts` → `Assets`
- `Liabiilities` → `Liabilities`

## Validation Order

1. Parse account name syntax
2. Check for empty segments
3. Verify characters are valid
4. Check declaration (if strict mode)
5. Infer or verify type
6. Check assertions (after balancing)

## Examples

### Minimal Valid

```ledger
2024/01/15 Transaction
    Expenses:Food    $50
    Assets:Checking
```

### Full Declaration

```ledger
; ===== Account Declarations =====

account Assets
    type: Asset

account Assets:Bank
    type: Asset
    note Bank accounts

account Assets:Bank:Checking
    type: Asset
    note Primary checking account
    alias checking
    assert amount >= 0

account Expenses:Food
    type: Expense
    note Food and dining

; ===== Transactions =====

2024/01/15 Grocery
    Expenses:Food       $50
    checking           $-50    ; Uses alias
```

### Organization by Type

```ledger
; ===== Assets =====
account Assets:Bank:Checking
account Assets:Bank:Savings
account Assets:Cash
account Assets:Investments:Stocks
account Assets:Investments:Bonds

; ===== Liabilities =====
account Liabilities:Credit-Card
account Liabilities:Mortgage
account Liabilities:Student-Loan

; ===== Equity =====
account Equity:Opening-Balance
account Equity:Retained-Earnings

; ===== Income =====
account Income:Salary
account Income:Interest
account Income:Dividends

; ===== Expenses =====
account Expenses:Housing:Rent
account Expenses:Housing:Utilities
account Expenses:Food:Groceries
account Expenses:Food:Restaurants
account Expenses:Transportation
```

## Best Practices

1. **Declare accounts** - For validation and documentation
2. **Use consistent naming** - Establish conventions
3. **Validate typos** - Use strict mode
4. **Document with notes** - Add descriptions
5. **Set assertions** - Catch anomalies early
6. **Organize hierarchically** - Logical groupings

## See Also

- [Account Directive](../directives/account.md)
- [Alias Directive](../directives/alias.md)
- [Error Codes](../errors.md)
