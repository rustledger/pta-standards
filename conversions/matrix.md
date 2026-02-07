# Feature Support Matrix

This matrix shows feature support across plain text accounting formats.

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully supported |
| ⚠️ | Partial support |
| ❌ | Not supported |
| 🔄 | Different syntax |

## Core Features

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Transactions | ✅ | ✅ | ✅ |
| Multiple postings | ✅ | ✅ | ✅ |
| Auto-balancing | ✅ | ✅ | ✅ |
| Comments | ✅ | ✅ | ✅ |
| Includes | ✅ | ✅ | ✅ |

## Account Features

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Account declaration | ✅ Required | ⚠️ Optional | ⚠️ Optional |
| Account open date | ✅ | ❌ | ❌ |
| Account close date | ✅ | ❌ | ❌ |
| Account hierarchy | ✅ | ✅ | ✅ |
| Account aliases | ❌ | ✅ | ✅ |
| Account types | ✅ Prefix-based | 🔄 Directive | 🔄 Directive |

## Amount & Currency

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Multiple currencies | ✅ | ✅ | ✅ |
| Currency declaration | ✅ Required | ⚠️ Optional | ⚠️ Optional |
| Currency position | 🔄 After | 🔄 Before/After | 🔄 Before/After |
| Commodity symbols | ✅ | ✅ | ✅ |
| Decimal precision | ✅ | ✅ | ✅ |
| Thousands separator | ❌ | ✅ | ✅ |

## Cost Basis & Lots

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Cost basis tracking | ✅ | ✅ | ✅ |
| Lot identification | ✅ `{}` | ✅ `{}` | ✅ `{}` |
| FIFO booking | ✅ | ✅ | ⚠️ |
| LIFO booking | ✅ | ✅ | ⚠️ |
| Average cost | ✅ | ❌ | ❌ |
| Specific lot | ✅ | ✅ | ⚠️ |

## Prices

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Price directive | ✅ | ✅ `P` | ✅ `P` |
| Inline price `@` | ✅ | ✅ | ✅ |
| Total price `@@` | ✅ | ✅ | ✅ |
| Price database | ✅ | ✅ | ✅ |

## Balance Assertions

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Balance assertion | ✅ Directive | ✅ `=` | ✅ `=` |
| Assertion timing | Start of day | After posting | After posting |
| Partial assertion | ❌ | ❌ | ✅ `==` |
| Subaccount assertion | ❌ | ❌ | ✅ `=*` |

## Metadata

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Key-value metadata | ✅ `key: "value"` | ✅ `; key: value` | ✅ `; key: value` |
| Tags | ✅ `#tag` | ✅ `:tag:` | ✅ `tag:` |
| Links | ✅ `^link` | ❌ | ❌ |
| Transaction flag | ✅ `*` `!` | ✅ `*` `!` | ✅ `*` `!` |

## Advanced Features

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Padding (pad) | ✅ | ❌ | ❌ |
| Documents | ✅ | ❌ | ❌ |
| Events | ✅ | ❌ | ❌ |
| Notes | ✅ | ❌ | ❌ |
| Custom directives | ✅ | ❌ | ❌ |
| Plugins | ✅ Python | ❌ | ❌ |

## Ledger-Specific

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Virtual postings `()` | ❌ | ✅ | ⚠️ |
| Balanced virtual `[]` | ❌ | ✅ | ⚠️ |
| Automated transactions | ❌ | ✅ `=` | ✅ `=` |
| Periodic transactions | ❌ | ✅ `~` | ✅ `~` |
| Value expressions | ❌ | ✅ | ❌ |
| Effective dates | ❌ | ✅ | ✅ |

## hledger-Specific

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Forecast mode | ❌ | ⚠️ | ✅ |
| Timedot format | ❌ | ❌ | ✅ |
| CSV rules | ❌ | ❌ | ✅ |
| Decimal mark directive | ❌ | ❌ | ✅ |

## Query Languages

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Query language | ✅ BQL (SQL-like) | ✅ Expressions | ✅ Query syntax |
| SELECT queries | ✅ | ❌ | ❌ |
| Aggregations | ✅ | ✅ | ✅ |
| Regex filters | ✅ | ✅ | ✅ |

## Output Formats

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Text output | ✅ | ✅ | ✅ |
| CSV output | ✅ | ✅ | ✅ |
| JSON output | ⚠️ | ⚠️ | ✅ |
| HTML output | ✅ | ❌ | ✅ |
