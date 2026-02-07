# Conversion Loss Matrix

This document details what information is lost when converting between formats.

## Beancount → Ledger

### Lost Features

| Feature | Workaround |
|---------|------------|
| `open` directive dates | Comment with date |
| `close` directive dates | Comment with date |
| `document` directives | Convert to comments |
| `event` directives | Convert to comments |
| `note` directives | Convert to comments |
| `query` directives | Convert to comments |
| `custom` directives | Convert to comments |
| `pad` directives | Generate explicit transactions |
| `^link` syntax | Convert to tags or comments |
| Plugin effects | Must be pre-applied |
| Average cost booking | Manual conversion |

### Syntax Changes

| Beancount | Ledger |
|-----------|--------|
| `2024-01-15 *` | `2024/01/15 *` |
| `100.00 USD` | `$100.00` or `100.00 USD` |
| `{100.00 USD}` | `{$100.00}` |
| `key: "value"` | `; key: value` |
| `#tag` | `:tag:` |

### Preserved

- All transaction amounts and balances
- Account hierarchy
- Cost basis information
- Price directives
- Basic metadata
- Comments

## Beancount → hledger

### Lost Features

| Feature | Workaround |
|---------|------------|
| `open` directive dates | Comment or `account` directive |
| `close` directive dates | Comment |
| `document` directives | Convert to comments |
| `event` directives | Convert to comments |
| `note` directives | Convert to comments |
| `query` directives | Convert to comments |
| `custom` directives | Convert to comments |
| `pad` directives | Generate explicit transactions |
| `^link` syntax | Convert to tags |
| Plugin effects | Must be pre-applied |

### Syntax Changes

| Beancount | hledger |
|-----------|---------|
| `2024-01-15 *` | `2024-01-15 *` |
| `100.00 USD` | `USD 100.00` or `100.00 USD` |
| `balance` directive | `= AMOUNT` assertion |
| `key: "value"` | `; key: value` |
| `#tag` | `tag:` |

### Preserved

- All transaction amounts and balances
- Account hierarchy
- Cost basis information
- Price directives
- Metadata (syntax change)
- Comments

## Ledger → Beancount

### Lost Features

| Feature | Workaround |
|---------|------------|
| Virtual postings `()` | Remove (unbalanced) or balance |
| Balanced virtual `[]` | Convert to real postings |
| Automated transactions `=` | Expand inline |
| Periodic transactions `~` | Generate explicit transactions |
| Value expressions | Pre-evaluate |
| Effective dates | Use primary date only |
| Account aliases | Expand inline |
| Payee directives | Ignore |
| Tag directives | Ignore |

### Required Additions

| Addition | Reason |
|----------|--------|
| `open` directives | Beancount requires account declaration |
| `commodity` directives | Beancount requires currency declaration |
| Operating currency option | For balance checking |

### Syntax Changes

| Ledger | Beancount |
|--------|-----------|
| `2024/01/15 *` | `2024-01-15 *` |
| `$100.00` | `100.00 USD` |
| `= $100.00` (assertion) | `balance` directive |
| `:tag:` | `#tag` |
| `; key: value` | `key: "value"` |

## Ledger → hledger

### Lost Features

| Feature | Workaround |
|---------|------------|
| Value expressions | Pre-evaluate |
| Some expression functions | Approximate or omit |

### Preserved (High Compatibility)

- Virtual postings
- Automated transactions
- Periodic transactions
- Effective dates
- Most syntax identical

### Minor Differences

| Ledger | hledger |
|--------|---------|
| Some functions | Different or missing |
| Expression syntax | Minor variations |

## hledger → Beancount

### Lost Features

| Feature | Workaround |
|---------|------------|
| Virtual postings | Convert or remove |
| Automated transactions | Expand inline |
| Periodic transactions | Generate explicit |
| Forecast transactions | Generate explicit |
| Timedot entries | Convert to transactions |
| `=*` assertions | Use simple assertions |
| `==` assertions | Use simple assertions |

### Required Additions

| Addition | Reason |
|----------|--------|
| `open` directives | Required |
| `commodity` directives | Required |

## hledger → Ledger

### Lost Features

| Feature | Workaround |
|---------|------------|
| `=*` subaccount assertions | Use regular assertions |
| `==` total assertions | Use regular assertions |
| Timedot format | Convert to ledger format |
| Some forecast features | Manual expansion |

### Preserved

- Most syntax identical
- Virtual postings
- Automated transactions
- Periodic transactions

## Round-Trip Considerations

### Beancount → Ledger → Beancount

**Lost permanently:**
- `open`/`close` dates (unless preserved in comments)
- Document/event/note/query directives
- Link syntax (`^link`)
- Plugin-generated data

**Recoverable:**
- Metadata (syntax normalized)
- Tags (syntax change)

### Ledger → Beancount → Ledger

**Lost permanently:**
- Virtual posting semantics
- Value expressions
- Automated/periodic transaction definitions

**Recoverable:**
- Transaction data (expanded form)
- Basic syntax variations

## Recommendations

### For Maximum Portability

1. Use common features only
2. Avoid format-specific directives
3. Use simple metadata syntax
4. Pre-expand automated transactions
5. Document conversion in comments

### For Archival

1. Keep original format
2. Export to interchange format
3. Document any conversions performed
