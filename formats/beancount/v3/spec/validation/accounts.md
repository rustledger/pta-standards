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

### E1001: Account Not Opened

An account MUST be opened before any posting references it.

**Condition:** Posting references an account with no prior `open` directive.

**Example:**
```beancount
; ERROR: No open directive for Assets:Checking
2024-01-15 * "Deposit"
  Assets:Checking   100 USD    ; E1001
  Income:Salary
```

**Fix:**
```beancount
2024-01-01 open Assets:Checking USD

2024-01-15 * "Deposit"
  Assets:Checking   100 USD    ; OK
  Income:Salary
```

### E1002: Account Already Open

An account MUST NOT be opened twice without an intervening close.

**Condition:** `open` directive for an account that is already open.

**Example:**
```beancount
2020-01-01 open Assets:Checking USD
2021-01-01 open Assets:Checking USD    ; E1002: Already open
```

**Fix:**
```beancount
2020-01-01 open Assets:Checking USD
; Remove duplicate, or close first:
; 2020-12-31 close Assets:Checking
; 2021-01-01 open Assets:Checking USD
```

### E1003: Account Closed

An account MUST NOT be used in postings after its close date.

**Condition:** Posting date is on or after the account's close date.

**Example:**
```beancount
2020-01-01 open Assets:OldAccount USD
2023-12-31 close Assets:OldAccount

2024-01-15 * "Late transaction"
  Assets:OldAccount   100 USD    ; E1003: Closed on 2023-12-31
  Income:Salary
```

**Fix:** Use a different account or adjust dates.

### E1004: Account Close Not Empty

Closing an account with non-zero balance produces a warning.

**Condition:** `close` directive when account has non-zero balance.

**Severity:** Warning (configurable)

**Example:**
```beancount
2024-01-01 open Assets:Checking USD

2024-06-01 * "Deposit"
  Assets:Checking  100 USD
  Income:Gift

2024-12-31 close Assets:Checking    ; E1004: Balance is 100 USD
```

**Fix:**
```beancount
2024-12-30 * "Transfer out"
  Assets:Checking  -100 USD
  Assets:NewAccount

2024-12-31 close Assets:Checking    ; OK: Balance is 0
```

### E1005: Invalid Account Name

Account names MUST follow naming conventions.

**Conditions:**
- Does not start with valid root type
- Contains invalid characters
- Component doesn't start with capital letter

**Examples:**
```beancount
; Invalid root type
2024-01-01 open Savings:Emergency    ; E1005: "Savings" not valid

; Lowercase component
2024-01-01 open Assets:checking      ; E1005: Must be "Checking"

; Invalid characters
2024-01-01 open Assets:My Account    ; E1005: Space not allowed
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

An account can be reopened after closing:

```beancount
2020-01-01 open Assets:Checking USD
2022-12-31 close Assets:Checking

; Transactions between close and reopen are invalid

2024-01-01 open Assets:Checking USD    ; OK: Reopen
2024-01-15 * "Deposit"
  Assets:Checking  100 USD             ; OK
  Income:Gift
```

### Same-Day Open and Use

Using an account on its open date is valid:

```beancount
2024-01-15 open Assets:Checking USD

2024-01-15 * "First deposit"
  Assets:Checking  100 USD    ; OK: Same day as open
  Income:Gift
```

### Close Date Boundary

The close date is exclusive—transactions ON the close date are invalid:

```beancount
2024-01-01 open Assets:Checking USD
2024-06-30 close Assets:Checking

2024-06-30 * "Final transaction"
  Assets:Checking  100 USD    ; E1003: Close is 2024-06-30
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

### Implicit Open

Some implementations allow implicit account opening:

```beancount
option "allow_implicit_open" "TRUE"

; Account auto-opened on first use
2024-01-15 * "Deposit"
  Assets:Checking  100 USD    ; Implicitly opens Assets:Checking
  Income:Salary
```

This is NOT recommended for production ledgers.

### Strict Mode

Require explicit currency constraints:

```beancount
option "strict" "TRUE"

; Must specify currencies
2024-01-01 open Assets:Checking USD,EUR    ; Required in strict mode
```

## Implementation Notes

1. Build account state map during parsing
2. Sort directives chronologically before validation
3. Track open date, close date, and constraints per account
4. Validate postings against current account state
5. Report all errors with account name and dates
