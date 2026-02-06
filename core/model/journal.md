# Journal

This document specifies the journal model for plain text accounting systems.

## Definition

A **Journal** is an ordered collection of directives that together form a complete accounting record. Also called a "ledger" or "book."

```
Journal = {
  directives: List[Directive],
  options: Options,
  errors: List[Error]
}
```

## Journal Structure

### Components

| Component | Description |
|-----------|-------------|
| Directives | All parsed entries |
| Options | Configuration settings |
| Errors | Parse and validation errors |

### Directive Types

| Category | Directives |
|----------|------------|
| Account lifecycle | `open`, `close` |
| Transactions | `transaction` |
| Assertions | `balance`, `pad` |
| Reference data | `commodity`, `price` |
| Annotations | `note`, `document`, `event` |
| Extensions | `query`, `custom` |
| Configuration | `option`, `plugin`, `include` |

## Loading Process

### Phase 1: Parse

```
Source Files → Tokens → AST → Directives
```

1. Read source file(s)
2. Tokenize (lexical analysis)
3. Parse (syntactic analysis)
4. Build directive objects

### Phase 2: Include Resolution

```
Main File + Includes → Merged Directives
```

1. Process `include` directives
2. Recursively load included files
3. Detect and reject cycles
4. Merge all directives

### Phase 3: Sort

```
Merged Directives → Sorted Directives
```

1. Sort by date (primary)
2. Sort by directive type (secondary)
3. Preserve file order (tertiary)

### Phase 4: Process

```
Sorted Directives → Processed Journal
```

1. Apply plugins in order
2. Expand `pad` directives
3. Process interpolations

### Phase 5: Validate

```
Processed Journal → Validated Journal + Errors
```

1. Check account lifecycle
2. Verify transaction balance
3. Check balance assertions
4. Validate currency constraints

## File Structure

### Single-File Journal

```
; ledger.beancount

option "title" "My Finances"
option "operating_currency" "USD"

2024-01-01 open Assets:Checking
2024-01-01 open Expenses:Food

2024-01-15 * "Grocery Store"
  Assets:Checking  -50 USD
  Expenses:Food
```

### Multi-File Journal

```
; main.beancount
option "title" "My Finances"
include "accounts.beancount"
include "2024/january.beancount"
include "2024/february.beancount"

; accounts.beancount
2024-01-01 open Assets:Checking
2024-01-01 open Expenses:Food

; 2024/january.beancount
2024-01-15 * "Grocery Store"
  Assets:Checking  -50 USD
  Expenses:Food
```

## Options

### Global Configuration

Options set journal-wide behavior:

```
option "title" "Personal Finances"
option "operating_currency" "USD"
option "account_root_assets" "Assets"
```

### Option Scoping

Only options in the main file apply (not included files):

```
; main.beancount
option "title" "Main"         ; Applies
include "other.beancount"

; other.beancount
option "title" "Other"        ; Ignored
```

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `title` | Journal title | `"Personal Finances"` |
| `operating_currency` | Primary currencies | `"USD"` |
| `name_assets` | Assets root name | `"Assets"` |
| `name_liabilities` | Liabilities root | `"Liabilities"` |
| `name_equity` | Equity root | `"Equity"` |
| `name_income` | Income root | `"Income"` |
| `name_expenses` | Expenses root | `"Expenses"` |

## Plugins

### Plugin Loading

```
plugin "beancount.plugins.auto_accounts"
plugin "my_custom_plugin" "config_string"
```

### Plugin Processing Order

Plugins process in declaration order:

```
plugin "plugin_a"     ; Runs first
include "other.beancount"
plugin "plugin_c"     ; Runs third

; other.beancount
plugin "plugin_b"     ; Runs second
```

### Plugin API

```python
def plugin(entries: List[Directive], options: Dict) -> Tuple[List[Directive], List[Error]]:
    # Transform entries
    new_entries = transform(entries)
    errors = validate(entries)
    return new_entries, errors
```

## Directive Ordering

### Primary Sort: Date

All directives sorted chronologically:

```
2024-01-01 ...  ; First
2024-01-15 ...
2024-02-01 ...  ; Last
```

### Secondary Sort: Type Priority

Same-date directives ordered by type:

| Priority | Type |
|----------|------|
| 0 | open |
| 1 | commodity |
| 2 | pad |
| 3 | balance |
| 4 | transaction |
| 5 | note |
| 6 | document |
| 7 | event |
| 8 | query |
| 9 | price |
| 10 | close |
| 11 | custom |

### Tertiary Sort: File Order

Same date and type preserve source order.

## State Tracking

### Account State

```python
accounts = {
    "Assets:Checking": AccountState(
        open_date=date(2024, 1, 1),
        close_date=None,
        currencies={"USD"},
        booking=BookingMethod.STRICT
    )
}
```

### Balances

```python
balances = {
    "Assets:Checking": Inventory({
        "USD": Decimal("1000.00")
    })
}
```

### Price Database

```python
prices = PriceDatabase()
prices.add(date(2024, 1, 15), "EUR", "USD", Decimal("1.08"))
```

## Queries

### Iterating Directives

```python
for directive in journal.directives:
    if isinstance(directive, Transaction):
        process_transaction(directive)
```

### Filtering by Date

```python
start = date(2024, 1, 1)
end = date(2024, 12, 31)
year_directives = [
    d for d in journal.directives
    if start <= d.date <= end
]
```

### Filtering by Account

```python
checking_txns = [
    txn for txn in journal.transactions
    if any(p.account == "Assets:Checking" for p in txn.postings)
]
```

## Journal Reports

### Balance Report

```
Assets:Checking      1000.00 USD
Assets:Savings       5000.00 USD
Liabilities:Credit   -500.00 USD
─────────────────────────────────
Net Worth            5500.00 USD
```

### Income Statement

```
Income:Salary       -5000.00 USD
Expenses:Food         500.00 USD
Expenses:Rent        1500.00 USD
───────────────────────────────
Net Income          -3000.00 USD
```

### Trial Balance

```
Account              Debit    Credit
──────────────────────────────────────
Assets:Checking   1000.00
Income:Salary               1000.00
──────────────────────────────────────
Total             1000.00   1000.00
```

## Error Handling

### Parse Errors

```
ERROR: Unexpected token
  --> ledger.beancount:42:15
   |
42 |   Assets:Checking  USD 100
   |                    ^^^
   |
   = expected amount format: <number> <commodity>
```

### Validation Errors

```
ERROR: Account not opened
  --> ledger.beancount:42:3
   |
42 |   Assets:Unknown  100 USD
   |   ^^^^^^^^^^^^^^
```

### Warning Accumulation

Non-fatal issues are collected:

```python
journal.errors = [
    Warning("Unused account", ...),
    Warning("Duplicate metadata key", ...),
]
```

## Journal Mutations

### Immutability Principle

Journal data is typically immutable after loading:

```python
# Good: Create new transaction
new_txn = Transaction(
    date=old_txn.date,
    narration="Modified",
    postings=old_txn.postings
)

# Bad: Mutate in place
old_txn.narration = "Modified"  # Don't do this
```

### Modification Workflow

```
Load → Query/Report
         ↓
       (User edits source file)
         ↓
      Reload → Query/Report
```

## Serialization

### Round-Trip Preservation

A serialized journal should parse to equivalent directives:

```
load(serialize(journal)) ≈ journal
```

### Format Variations

```python
# Compact
"2024-01-15 * \"Note\"\n  Account 100 USD\n  Other"

# Pretty
"""
2024-01-15 * "Note"
  Account  100 USD
  Other
"""
```

## Implementation Model

```python
@dataclass
class Journal:
    directives: List[Directive]
    options: Dict[str, Any]
    errors: List[Error]

    @property
    def transactions(self) -> Iterator[Transaction]:
        for d in self.directives:
            if isinstance(d, Transaction):
                yield d

    @property
    def accounts(self) -> Set[str]:
        accounts = set()
        for d in self.directives:
            if isinstance(d, Open):
                accounts.add(d.account)
        return accounts

    def get_balance(self, account: str, date: date) -> Inventory:
        """Compute balance for account as of date."""
        inventory = Inventory()
        for txn in self.transactions:
            if txn.date > date:
                break
            for posting in txn.postings:
                if posting.account == account:
                    inventory.add(posting.units)
        return inventory


def load(filename: str) -> Journal:
    """Load journal from file."""
    content = read_file(filename)
    directives, errors = parse(content)
    directives = resolve_includes(directives, filename)
    directives = sort_directives(directives)
    directives, plugin_errors = apply_plugins(directives)
    errors.extend(plugin_errors)
    validation_errors = validate(directives)
    errors.extend(validation_errors)
    return Journal(directives, extract_options(directives), errors)
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Entry point | Single file | Single file | Single file |
| Include | `include` | `include` | `include` |
| Options | `option` directive | Command-line/file | Command-line/file |
| Plugins | `plugin` directive | Python hooks | Haskell extensions |
| Sorting | By date + type | By date | By date |
