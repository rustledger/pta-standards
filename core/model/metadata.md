# Metadata

This document specifies the metadata model for plain text accounting systems.

## Definition

**Metadata** is a collection of key-value pairs attached to directives or postings, providing additional structured information beyond the core data model.

```
Metadata = Dict[String, Value]
```

## Purpose

Metadata extends the data model without changing core semantics:

| Use Case | Example |
|----------|---------|
| Source tracking | `filename`, `lineno` |
| Import correlation | `bank-ref`, `import-id` |
| Custom categorization | `project`, `department` |
| External references | `receipt`, `invoice-id` |
| Processing hints | `check`, `cleared-date` |

## Syntax

### Directive Metadata

Metadata appears on lines following the directive header, indented:

```
2024-01-15 * "Purchase"
  order-id: "ABC123"
  category: "office"
  Assets:Checking  -100 USD
  Expenses:Office
```

### Posting Metadata

Metadata on postings is further indented:

```
2024-01-15 * "Purchase"
  Assets:Checking  -100 USD
    cleared: TRUE
  Expenses:Office   100 USD
    project: "Q1-2024"
```

### Multiple Metadata Lines

```
2024-01-15 open Assets:Checking
  institution: "First National Bank"
  account-number: "****1234"
  routing: "123456789"
  nickname: "Primary Checking"
```

## Keys

### Key Format

Keys are identifiers with format-specific rules:

| Format | Allowed Characters | Example |
|--------|-------------------|---------|
| Beancount | `a-z`, `0-9`, `-`, `_` | `order-id` |
| Ledger | Any non-whitespace | `Order ID` |
| hledger | Any non-whitespace | `order_id` |

### Reserved Keys

Some keys have special meaning:

| Key | Purpose |
|-----|---------|
| `filename` | Source file path |
| `lineno` | Source line number |
| `__*__` | Internal/system use |

### Key Conventions

```
lowercase-with-dashes     ; Preferred
snake_case                ; Alternative
camelCase                 ; Discouraged
```

## Values

### Value Types

| Type | Syntax | Example |
|------|--------|---------|
| String | Quoted | `"Hello World"` |
| Number | Decimal | `123.45` |
| Boolean | `TRUE`/`FALSE` | `TRUE` |
| Date | ISO 8601 | `2024-01-15` |
| Currency | Amount | `100 USD` |
| Account | Account name | `Assets:Checking` |
| Tag | Tag literal | `#project-x` |
| Link | Link literal | `^invoice-001` |

### String Values

```
name: "John Doe"
description: "Multi-word string"
path: "/path/to/file.pdf"
```

### Numeric Values

```
quantity: 42
rate: 1.5
percentage: 0.15
```

### Boolean Values

```
cleared: TRUE
pending: FALSE
taxable: TRUE
```

### Date Values

```
due-date: 2024-02-15
filed: 2024-01-20
```

### Amount Values

```
limit: 1000 USD
fee: 9.95 USD
```

### Account Values

```
source: Assets:Checking
destination: Expenses:Food
```

## Attachment Locations

### On Transactions

```
2024-01-15 * "Grocery Store"
  receipt: "receipts/2024-01-15-grocery.pdf"
  Assets:Checking  -50 USD
  Expenses:Food
```

### On Open Directives

```
2024-01-01 open Assets:Checking
  institution: "Bank of America"
  account-number: "****1234"
```

### On Commodity Directives

```
2024-01-01 commodity USD
  name: "US Dollar"
  precision: 2
```

### On Postings

```
2024-01-15 * "Multi-project expense"
  Expenses:Travel  500 USD
    project: "alpha"
    billable: TRUE
  Expenses:Travel  300 USD
    project: "beta"
    billable: FALSE
  Assets:Checking
```

## Metadata Stacks

### Push/Pop Mechanism

Metadata can be pushed onto a stack and automatically applied:

```
pushmeta project: "Q1-2024"

2024-01-15 * "Expense 1"    ; Gets project: "Q1-2024"
  ...

2024-01-20 * "Expense 2"    ; Gets project: "Q1-2024"
  ...

popmeta project
```

### Stack Scoping

Stacks are typically scoped to the current file:

```
; main.beancount
pushmeta department: "Engineering"
include "projects.beancount"
; projects.beancount does NOT inherit department stack
popmeta department
```

## System Metadata

### Automatic Metadata

Parsers typically inject:

```python
directive.meta['filename'] = "ledger.beancount"
directive.meta['lineno'] = 42
```

### Usage in Error Messages

```
ERROR: Account not opened
  --> ledger.beancount:42:3
```

## Querying Metadata

### BQL Examples

```sql
-- Filter by metadata
SELECT * FROM transactions WHERE META('project') = 'alpha'

-- Include metadata in output
SELECT date, META('project'), SUM(amount)
FROM postings
GROUP BY 1, 2
```

### Programmatic Access

```python
for entry in entries:
    if 'project' in entry.meta:
        print(f"{entry.date}: {entry.meta['project']}")
```

## Inheritance

### Directive to Posting

Postings inherit transaction metadata:

```
2024-01-15 * "Purchase"
  project: "alpha"
  Expenses:Office  100 USD    ; Has project: "alpha"
  Assets:Checking
```

### Override at Posting Level

```
2024-01-15 * "Purchase"
  project: "alpha"
  Expenses:Office:A  50 USD
    project: "beta"           ; Override: "beta"
  Expenses:Office:B  50 USD   ; Inherited: "alpha"
  Assets:Checking
```

## Metadata Semantics

### No Side Effects

Metadata is informational only:

```
2024-01-15 * "Purchase"
  magic-option: "do-something"  ; Does nothing automatically
  ...
```

### Plugin Interpretation

Plugins may interpret metadata:

```python
def plugin(entries, options):
    for entry in entries:
        if entry.meta.get('auto-categorize'):
            # Plugin-specific behavior
            pass
```

## Common Metadata Patterns

### Import Correlation

```
2024-01-15 * "AMZN MKTP"
  import-id: "chase-2024-01-15-001"
  bank-ref: "TXN123456789"
  ...
```

### Document Attachment

```
2024-01-15 * "Office Supplies"
  receipt: "receipts/2024/01/office-supplies.pdf"
  ...
```

### Project Tracking

```
2024-01-15 * "Client Meeting"
  project: "acme-corp"
  billable: TRUE
  hours: 2.5
  ...
```

### Tax Classification

```
2024-01-15 * "Home Office Equipment"
  tax-category: "business-expense"
  depreciation-years: 5
  ...
```

## Validation

### Unknown Metadata Key

Typically a warning, not an error:

```
WARNING: Unknown metadata key 'typo-key'
  --> ledger.beancount:42:3
   |
42 |   typo-key: "value"
   |   ^^^^^^^^
```

### Invalid Value Type

```
ERROR: Invalid metadata value type
  --> ledger.beancount:42:13
   |
42 |   quantity: not-a-number
   |             ^^^^^^^^^^^^
   |
   = expected: number
```

## Implementation Model

```python
@dataclass
class MetadataEntry:
    key: str
    value: Any
    line: int  # Source line for error reporting


class Metadata(dict):
    """Dictionary subclass for metadata with source tracking."""

    def __init__(self):
        super().__init__()
        self._sources: Dict[str, int] = {}

    def set(self, key: str, value: Any, line: int = 0):
        self[key] = value
        self._sources[key] = line

    def get_source_line(self, key: str) -> Optional[int]:
        return self._sources.get(key)


# Attached to directives
@dataclass
class Transaction:
    date: date
    flag: str
    payee: Optional[str]
    narration: str
    metadata: Metadata  # Key-value pairs
    postings: List[Posting]
```

## Serialization

### Text Format

```
2024-01-15 * "Purchase"
  key1: "string value"
  key2: 123
  key3: TRUE
  key4: 2024-01-15
  Assets:Checking  -100 USD
  Expenses:Office
```

### JSON Format

```json
{
  "date": "2024-01-15",
  "flag": "*",
  "narration": "Purchase",
  "metadata": {
    "key1": "string value",
    "key2": 123,
    "key3": true,
    "key4": "2024-01-15"
  },
  "postings": [...]
}
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Syntax | `key: value` | `; key: value` | `; key: value` |
| Position | Own line | Comment | Comment |
| Types | Multiple | String only | String only |
| Stacks | `pushmeta`/`popmeta` | Not standard | Not standard |
| Reserved | `filename`, `lineno` | None | None |
