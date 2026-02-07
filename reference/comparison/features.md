# Feature Comparison

Detailed feature comparison between Beancount, Ledger, and hledger.

## Core Accounting

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Double-entry | ✅ | ✅ | ✅ |
| Multiple currencies | ✅ | ✅ | ✅ |
| Auto-balance postings | ✅ | ✅ | ✅ |
| Transaction comments | ✅ | ✅ | ✅ |
| Posting comments | ✅ | ✅ | ✅ |
| File includes | ✅ | ✅ | ✅ |

## Account Management

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Account declaration | Required | Optional | Optional |
| Open date | ✅ | ❌ | ❌ |
| Close date | ✅ | ❌ | ❌ |
| Currency constraints | ✅ | ❌ | ❌ |
| Account aliases | ❌ | ✅ | ✅ |
| Account types | Prefix-based | Directive | Directive |
| Default account | ❌ | ✅ `bucket` | ✅ |

## Amount Handling

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Currency prefix | ❌ | ✅ | ✅ |
| Currency suffix | ✅ | ✅ | ✅ |
| Thousands separator | ❌ | ✅ | ✅ |
| Commodity formatting | ✅ | ✅ | ✅ |
| Arbitrary precision | ✅ | ✅ | ✅ |
| Balance tolerance | ✅ | ❌ | ❌ |

## Cost Basis & Lots

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Cost tracking | ✅ `{}` | ✅ `{}` | ✅ `@` |
| Lot dates | ✅ | ✅ `[]` | Metadata |
| Lot labels | ✅ | ✅ `()` | Metadata |
| FIFO booking | ✅ | ✅ | ⚠️ |
| LIFO booking | ✅ | ✅ | ⚠️ |
| Average cost | ✅ | ❌ | ❌ |
| Specific ID | ✅ | ✅ | ⚠️ |

## Balance & Validation

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Balance assertion | ✅ Directive | ✅ `=` | ✅ `=` |
| Partial assertion | ❌ | ❌ | ✅ `==` |
| Subaccount assertion | ❌ | ❌ | ✅ `=*` |
| Pad directive | ✅ | ❌ | ❌ |
| Strict validation | ✅ | ❌ | ✅ check |

## Metadata & Organization

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Key-value metadata | ✅ `key: "val"` | ✅ `; key: val` | ✅ `; key: val` |
| Tags | ✅ `#tag` | ✅ `:tag:` | ✅ `tag:` |
| Links | ✅ `^link` | ❌ | ❌ |
| Documents | ✅ | ❌ | ❌ |
| Notes | ✅ | ❌ | ❌ |
| Events | ✅ | ❌ | ❌ |

## Advanced Features

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Virtual postings | ❌ | ✅ `()` `[]` | ✅ `()` `[]` |
| Automated transactions | ❌ | ✅ `=` | ✅ `=` |
| Periodic transactions | ❌ | ✅ `~` | ✅ `~` |
| Value expressions | ❌ | ✅ | ❌ |
| Effective dates | ❌ | ✅ | ✅ |
| Plugins | ✅ Python | ❌ | ❌ |
| Custom directives | ✅ | ❌ | ❌ |

## Query & Reporting

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Balance report | ✅ | ✅ | ✅ |
| Register report | ✅ | ✅ | ✅ |
| Balance sheet | ✅ | ✅ | ✅ |
| Income statement | ✅ | ✅ | ✅ |
| Query language | ✅ BQL | ✅ Expressions | ✅ Filters |
| SQL-like queries | ✅ | ❌ | ❌ |

## Output Formats

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Text | ✅ | ✅ | ✅ |
| CSV | ✅ | ✅ | ✅ |
| JSON | ⚠️ | ⚠️ | ✅ |
| HTML | ✅ | ❌ | ✅ |
| Charts | ✅ Fava | ❌ | ✅ web |

## Tooling

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| CLI tool | bean-* | ledger | hledger |
| Web interface | Fava | ❌ | hledger-web |
| Editor plugins | ✅ | ✅ | ✅ |
| Import tools | ✅ | ✅ | ✅ |
| Mobile apps | Community | Community | Community |

## Format-Specific Features

### Beancount Only

- **Pad directive** - Auto-generate balancing transactions
- **Document directive** - Link files to accounts
- **Event directive** - Track events over time
- **Note directive** - Add dated notes to accounts
- **Query directive** - Store queries in journal
- **Custom directive** - User-defined directives
- **Python plugins** - Extend with custom logic
- **Operating currency** - Balance checking options
- **Booking methods** - Per-account booking configuration

### Ledger Only

- **Value expressions** - Compute amounts dynamically
- **Rich function library** - `market()`, `lot_date()`, etc.
- **Payee directive** - Pre-define payees
- **Check directive** - Runtime balance checks
- **Apply directive** - Apply rules to transactions
- **Assert directive** - Runtime assertions
- **Year directive** - Set default year
- **Bucket directive** - Default account

### hledger Only

- **Timedot format** - Time tracking format
- **CSV rules** - Declarative CSV import
- **Decimal-mark directive** - Regional decimal format
- **Total assertions `==`** - Assert total balance
- **Inclusive assertions `=*`** - Include subaccounts
- **Forecast mode** - Generate future transactions
- **hledger-web** - Built-in web interface
- **JSON output** - Native JSON support

## See Also

- [Syntax Comparison](syntax.md)
- [Philosophy Comparison](philosophy.md)
