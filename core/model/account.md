# Accounts

This document specifies the account model for plain text accounting systems.

## Definition

An **Account** is a named container that tracks positions (holdings) of one or more commodities over time. Accounts form a hierarchical namespace and are the fundamental unit of organization in double-entry bookkeeping.

## Account Name Structure

### Hierarchical Names

Account names are hierarchical, with components separated by a delimiter (typically `:`):

```
Assets:Bank:Checking
Expenses:Food:Groceries:Whole-Foods
```

### Components

| Component | Description |
|-----------|-------------|
| Root | First component (account type) |
| Intermediate | Middle components (categories) |
| Leaf | Final component (specific account) |

Example breakdown:
```
Assets:Bank:Checking
│      │    └── Leaf: "Checking"
│      └── Intermediate: "Bank"
└── Root: "Assets"
```

## Account Types

### Standard Types

The five standard account types from double-entry accounting:

| Type | Normal Balance | Purpose |
|------|---------------|---------|
| Assets | Debit | Things you own |
| Liabilities | Credit | Things you owe |
| Equity | Credit | Net worth / opening balances |
| Income | Credit | Money received |
| Expenses | Debit | Money spent |

### Balance Sheet vs. Income Statement

| Category | Account Types | Persists Across Periods |
|----------|--------------|------------------------|
| Balance Sheet | Assets, Liabilities, Equity | Yes |
| Income Statement | Income, Expenses | No (closed to equity) |

### Normal Balance Direction

The "normal balance" indicates whether the account typically has a positive balance from debits or credits:

```
Debit-normal:  Increases with debits    (Assets, Expenses)
Credit-normal: Increases with credits   (Liabilities, Equity, Income)
```

## Account Naming Rules

### Character Set

Valid characters for account name components:

| Category | Characters |
|----------|------------|
| Letters | `A-Z`, `a-z` |
| Digits | `0-9` |
| Symbols | `-`, `_` (implementation-specific) |

### Constraints

1. **Root MUST be a type**: First component identifies the account type
2. **Components MUST be non-empty**: No consecutive delimiters
3. **Case sensitivity**: Implementation-defined (typically case-sensitive)
4. **Length limits**: Implementation-defined

### Valid Names

```
Assets:Checking
Assets:Bank:Savings-Account
Expenses:Food:Groceries
Income:Salary:2024
Equity:Opening-Balances
```

### Invalid Names

```
:Checking              ; Missing root
Assets::Checking       ; Empty component
checking               ; Missing type root
Assets:                ; Trailing delimiter
```

## Account Lifecycle

### Opening

Accounts MUST be opened before use:

```
2024-01-01 open Assets:Checking USD
```

Opening specifies:
- **Date**: When account becomes active
- **Currencies**: Optional commodity constraint
- **Booking method**: Optional lot matching method

### Active Period

While open, the account:
- Accepts postings
- Tracks inventory/balance
- May have metadata attached

### Closing

Accounts MAY be closed when no longer needed:

```
2024-12-31 close Assets:Checking
```

Closing:
- Prevents further postings
- May require zero balance (implementation-specific)
- Preserves historical data

### Lifecycle Diagram

```
[Not Exists] ─── open ───> [Open] ─── close ───> [Closed]
                             │
                             │ postings
                             ▼
                       [Has Balance]
```

## Currency Constraints

### Open Currency

When opening with currencies, only those commodities are allowed:

```
2024-01-01 open Assets:Checking USD, EUR
```

This account accepts only USD and EUR postings.

### No Constraint

Without currency specification, any commodity is allowed:

```
2024-01-01 open Assets:Investment
```

This account accepts any commodity.

### Validation

```
2024-01-01 open Assets:Checking USD

2024-01-15 * "Deposit"
  Assets:Checking  100 USD    ; OK
  Income:Salary

2024-01-16 * "Transfer"
  Assets:Checking  50 EUR     ; ERROR: EUR not allowed
  Assets:Euro-Account
```

## Account Hierarchy

### Implicit Parents

Parent accounts may be implicit:

```
; Only leaf opened, parents implicit
2024-01-01 open Assets:Bank:Checking
```

Creates logical hierarchy:
- `Assets` (implicit)
- `Assets:Bank` (implicit)
- `Assets:Bank:Checking` (explicit)

### Explicit Parents

Some formats require explicit parent accounts:

```
2024-01-01 open Assets
2024-01-01 open Assets:Bank
2024-01-01 open Assets:Bank:Checking
```

### Hierarchy Queries

Reports may aggregate by hierarchy level:

```
Assets:Bank:Checking    1000 USD
Assets:Bank:Savings     5000 USD
─────────────────────────────────
Assets:Bank             6000 USD  (sum of children)
```

## Account Aliases

### Alias Definition

Some formats support account aliases:

```
alias checking = Assets:Bank:Primary-Checking-Account

2024-01-15 * "Deposit"
  checking  100 USD
  Income:Salary
```

### Resolution

Aliases are expanded during parsing:
- Input: `checking`
- Resolved: `Assets:Bank:Primary-Checking-Account`

## Account Metadata

### Per-Account Metadata

Metadata may be attached at account level:

```
2024-01-01 open Assets:Checking
  institution: "First National Bank"
  account-number: "****1234"
```

### Inheritance

Metadata may cascade to children (implementation-specific):

```
2024-01-01 open Assets:Bank
  institution: "First National Bank"

2024-01-01 open Assets:Bank:Checking
  ; May inherit institution metadata
```

## Special Accounts

### Opening Balances

Equity account for initial balances:

```
Equity:Opening-Balances
```

### Retained Earnings

Equity account for period close:

```
Equity:Retained-Earnings
```

### Unrealized Gains

Equity account for mark-to-market:

```
Income:Unrealized-Gains
```

### Pad Source

Account for padding adjustments:

```
Equity:Adjustments
```

## Validation Rules

### Account Existence

```
ERROR: Account not opened
  --> ledger.beancount:42:3
   |
42 |   Assets:Unknown  100 USD
   |   ^^^^^^^^^^^^^^
   |
   = hint: add 'open' directive before this transaction
```

### Closed Account

```
ERROR: Posting to closed account
  --> ledger.beancount:100:3
   |
100|   Assets:Checking  100 USD
   |   ^^^^^^^^^^^^^^^
   |
   = note: account closed on 2024-06-30
```

### Currency Violation

```
ERROR: Currency not allowed for account
  --> ledger.beancount:50:3
   |
50 |   Assets:Checking  100 EUR
   |                        ^^^
   |
   = note: allowed currencies: USD
```

## Implementation Considerations

### Efficient Lookup

Implementations SHOULD:
- Use hash maps for O(1) account lookup
- Cache hierarchy relationships
- Index by account type for filtered queries

### Memory Model

```python
class Account:
    name: str                    # Full hierarchical name
    components: List[str]        # Name components
    type: AccountType            # Root type
    currencies: Set[Commodity]   # Allowed currencies
    booking: BookingMethod       # Lot matching method
    metadata: Dict[str, Any]     # Key-value pairs
    open_date: Date              # When opened
    close_date: Optional[Date]   # When closed (if any)
```

### Serialization

Accounts serialize to their full name string:

```json
{
  "account": "Assets:Bank:Checking"
}
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Delimiter | `:` | `:` | `:` |
| Required root | Yes (typed) | No | No |
| Case sensitivity | Yes | Configurable | Yes |
| Open required | Yes | No | No |
| Currency constraint | Yes | No | No |
