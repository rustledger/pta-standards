# Ledger v1 Specification

This directory contains the v1 specification for the Ledger format, based on Ledger 3.x behavior.

## Scope

This specification covers:
- Core syntax and parsing rules
- Transaction and posting structure
- Amount and commodity formatting
- All directive types
- Value expression language
- Automated and periodic transactions

## Specification Documents

### Core Syntax

| Document | Description |
|----------|-------------|
| [spec/syntax.md](spec/syntax.md) | Lexical structure and parsing rules |
| [spec/amounts.md](spec/amounts.md) | Amount and commodity formatting |
| [spec/posting.md](spec/posting.md) | Posting syntax and semantics |

### Directives

| Document | Description |
|----------|-------------|
| [spec/directives/transaction.md](spec/directives/transaction.md) | Transaction directive |
| [spec/directives/account.md](spec/directives/account.md) | Account directive |
| [spec/directives/commodity.md](spec/directives/commodity.md) | Commodity directive |
| [spec/directives/price.md](spec/directives/price.md) | Price directive |
| [spec/directives/include.md](spec/directives/include.md) | Include directive |
| [spec/directives/alias.md](spec/directives/alias.md) | Account alias |
| [spec/directives/bucket.md](spec/directives/bucket.md) | Default account |
| [spec/directives/check.md](spec/directives/check.md) | Balance check |
| [spec/directives/tag.md](spec/directives/tag.md) | Tag directive |
| [spec/directives/year.md](spec/directives/year.md) | Default year |
| [spec/directives/payee.md](spec/directives/payee.md) | Payee directive |
| [spec/directives/default.md](spec/directives/default.md) | Default commodity |

### Advanced Features

| Document | Description |
|----------|-------------|
| [expressions/spec.md](expressions/spec.md) | Value expression language |
| [expressions/functions.md](expressions/functions.md) | Built-in functions |

### Schema and Grammar

| Resource | Description |
|----------|-------------|
| [schema/ast.schema.json](schema/ast.schema.json) | JSON Schema for AST |
| [tree-sitter/](tree-sitter/) | Tree-sitter grammar |

## Quick Reference

### Transaction

```ledger
2024/01/15 * (123) Payee | Description  ; comment
    ; metadata: value
    Account:One    $100.00  ; posting comment
    Account:Two   -$100.00
```

### Amounts

```ledger
$1,234.56           ; Symbol prefix
1234.56 USD         ; Code suffix
-$50.00             ; Negative
$100 @ $1.10 CAD    ; With price
10 AAPL {$150.00}   ; With lot cost
```

### Virtual Postings

```ledger
2024/01/15 Test
    Expenses:Food      $50.00
    (Budget:Food)     -$50.00    ; Unbalanced virtual
    [Savings:Goal]     $50.00    ; Balanced virtual
    Assets:Checking
```

### Automated Transaction

```ledger
= /Grocery/
    (Budget:Food)  -1

= expr account =~ /Expenses/
    (Budget)  (amount * -1)
```

### Periodic Transaction

```ledger
~ Monthly
    Expenses:Rent  $1500
    Assets:Checking

~ Every 2 weeks from 2024/01/01
    Income:Salary  $2000
    Assets:Checking
```

### Directives

```ledger
account Assets:Checking
    note My main checking account
    alias checking

commodity $
    format $1,000.00

P 2024/01/15 AAPL $150.00

include other-file.ledger

bucket Assets:Checking

Y 2024

tag project
```

## Conformance Tests

See [tests/ledger/v1/](../../../tests/ledger/v1/) for conformance tests.

| Test Suite | Count | Description |
|------------|-------|-------------|
| syntax/valid | 44 | Valid syntax parsing |
| syntax/invalid | 20 | Invalid syntax detection |
| validation | 19 | Semantic validation |
| expressions | 26 | Value expressions |
| automated | 19 | Automated/periodic transactions |
| reports | 15 | Report output |

## Known Differences from hledger

While hledger aims for Ledger compatibility, some differences exist:

1. **Value expressions** - hledger has limited support
2. **Periodic transaction periods** - Syntax varies slightly
3. **Some command-line options** - Not all options are identical
4. **Report formatting** - Output format differs

## Implementation Notes

### Parsing

- Comments start with `;` or `#`
- Line continuation with trailing `\`
- Whitespace-sensitive (indentation matters)
- Amount position can be anywhere on posting line

### Validation

- Transactions must balance (excluding virtual postings)
- Commodities are implicitly declared
- Accounts are implicitly created on first use
- Balance assertions checked at parse time

### Date Formats

Ledger accepts multiple date formats:
- `YYYY/MM/DD` (canonical)
- `YYYY-MM-DD`
- `YYYY.MM.DD`
- `MM/DD` (uses default year)

## See Also

- [Ledger format overview](../README.md)
- [Compliance requirements](../compliance.md)
- [Test suite](../../../tests/ledger/v1/)
