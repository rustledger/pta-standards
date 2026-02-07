# Account Validation

## Overview

Account validation ensures the integrity of account lifecycles: accounts must be opened before use, must not be used after closing, and must follow naming conventions.

## Account Lifecycle

```
                    open
    [Not Exists] ─────────► [Open] ◄────────┐
                              │              │
                              │ close        │ reopen
                              ▼              │
                           [Closed] ─────────┘
```

## Validation Rules

### Account Not Opened

An account MUST be opened before any posting references it. Using an unopened account produces a `ValidationError`.

**Condition:** Posting references an account with no prior `open` directive.

**Example:**
```beancount
; ERROR: No open directive for Assets:Checking
2024-01-15 * "Deposit"
  Assets:Checking   100 USD    ; ValidationError
  Income:Salary
```

**Fix:**
```beancount
2024-01-01 open Assets:Checking USD

2024-01-15 * "Deposit"
  Assets:Checking   100 USD    ; OK
  Income:Salary
```

### Account Already Open

An account MUST NOT be opened twice without an intervening close. Opening an already-open account produces a `ValidationError`.

**Condition:** `open` directive for an account that is already open.

**Example:**
```beancount
2020-01-01 open Assets:Checking USD
2021-01-01 open Assets:Checking USD    ; ValidationError: Already open
```

### Account Closed

An account MUST NOT be used in postings AFTER its close date.

> **UNDEFINED**: Whether posting ON the close date is allowed is pending clarification.
> See: [Pending Issue - Close Date Semantics](https://github.com/beancount/beancount/issues/TBD)

**Example:**
```beancount
2020-01-01 open Assets:OldAccount USD
2023-12-31 close Assets:OldAccount

; Posting AFTER close date is always an error
2024-01-15 * "Late transaction"
  Assets:OldAccount   100 USD    ; ERROR: Invalid reference to closed account
  Income:Salary
```

### Account Close with Non-Zero Balance

> **UNDEFINED**: Whether closing an account with non-zero balance produces an error is pending clarification.
> See: [Pending Issue - Close with Balance](https://github.com/beancount/beancount/issues/TBD)

**Example:**
```beancount
2024-01-01 open Assets:Checking USD

2024-06-01 * "Deposit"
  Assets:Checking  100 USD
  Income:Gift

2024-12-31 close Assets:Checking    ; OK: No error even with 100 USD balance
```

**Best Practice:** Zero the balance before closing for cleaner bookkeeping:
```beancount
2024-12-30 * "Transfer out"
  Assets:Checking  -100 USD
  Assets:NewAccount

2024-12-31 close Assets:Checking    ; Balance is 0
```

**Note:** The `beancount.plugins.check_closing` plugin can be used to enforce zero balance at close.

### Invalid Account Name

Account names MUST follow naming conventions. Invalid names produce a `ParserError`.

**Conditions:**
- Does not start with valid root type
- Contains invalid characters
- Component doesn't start with uppercase letter or digit

**Examples:**
```beancount
; Invalid root type
2024-01-01 open Savings:Emergency    ; ParserError: "Savings" not valid root

; Lowercase component
2024-01-01 open Assets:checking      ; ParserError: Must start with uppercase

; Invalid characters
2024-01-01 open Assets:My Account    ; ParserError: Space not allowed
```

## Account Name Rules

### Root Types

Every account MUST begin with one of:

| Root | Purpose |
|------|---------|
| `Assets` | Things you own |
| `Liabilities` | Things you owe |
| `Equity` | Net worth, opening balances |
| `Income` | Money received |
| `Expenses` | Money spent |

### Component Rules

```ebnf
account   = root_type (":" component)+
root_type = "Assets" | "Liabilities" | "Equity" | "Income" | "Expenses"
component = capital_start (alphanumeric | "-")*

capital_start = [A-Z] | [0-9]
alphanumeric  = [A-Za-z0-9]
```

### Valid Names

```
Assets:Checking
Assets:US:BofA:Checking
Liabilities:CreditCard:Chase-Sapphire
Expenses:Food:Groceries
Income:Salary:2024
Equity:Opening-Balances
Assets:401k
```

### Invalid Names

```
assets:Checking           ; Lowercase root
Assets:checking           ; Lowercase component start
Assets:My Checking        ; Space in component
Assets::Checking          ; Empty component
Savings:Account           ; Invalid root
Assets                    ; No components after root
```

## Validation Timing

Account validation occurs during the chronological scan:

1. **Parse all directives**
2. **Sort by date**
3. **Scan chronologically:**
   - Track open/close state per account
   - Validate each posting against current state
   - Validate each close against current state

## Account State Tracking

```python
class AccountState:
    open_date: Optional[Date]
    close_date: Optional[Date]
    currencies: Optional[List[Currency]]
    booking_method: Optional[str]

# Per-account state machine
account_states: Dict[Account, AccountState]
```

## Edge Cases

### Reopening Accounts

**Note:** In Python beancount 3.x, accounts **cannot** be reopened after closing. A second `open` directive after a `close` produces a duplicate open error:

```beancount
2020-01-01 open Assets:Checking USD
2022-12-31 close Assets:Checking

2024-01-01 open Assets:Checking USD    ; ValidationError: Duplicate open
```

If you need to reuse an account after closing, you must use a new account name.

### Same-Day Open and Use

Using an account on its open date is valid:

```beancount
2024-01-15 open Assets:Checking USD

2024-01-15 * "First deposit"
  Assets:Checking  100 USD    ; OK: Same day as open
  Income:Gift
```

### Close Date Boundary

> **UNDEFINED**: Whether posting ON the close date is allowed is pending clarification.

Posting AFTER the close date is always an error:

```beancount
2024-01-01 open Assets:Checking USD
2024-06-30 close Assets:Checking

; What should happen for posting ON close date?
2024-06-30 * "Same-day transaction"
  Assets:Checking  100 USD    ; UNDEFINED behavior
  Income:Gift

; Posting AFTER close date is always an error
2024-07-01 * "After close"
  Assets:Checking  100 USD    ; ValidationError: Invalid reference to inactive account
  Income:Gift
```

### Notes and Documents After Close

Notes and documents MAY reference closed accounts:

```beancount
2024-06-30 close Assets:OldAccount

2024-07-15 note Assets:OldAccount "Records archived"    ; OK
2024-07-15 document Assets:OldAccount "final-statement.pdf"  ; OK
```

## Configuration

**Note:** Python beancount 3.x does NOT support implicit account opening. All accounts must be explicitly opened before use.

The `operating_currency` option can be set to specify the main reporting currency, but this does not affect account validation requirements.

## Implementation Notes

1. Build account state map during parsing
2. Sort directives chronologically before validation
3. Track open date, close date, and constraints per account
4. Validate postings against current account state
5. Report all errors with account name and dates
