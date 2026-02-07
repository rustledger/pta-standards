# Interchange Format Specification

This document defines a universal interchange format for plain text accounting data.

## Overview

The interchange format provides a common representation for PTA data that:

1. Captures the semantic content of all three formats
2. Enables lossless round-trip for common features
3. Uses standard serialization (JSON, Protocol Buffers)

## Design Principles

### Semantic Preservation

The format captures accounting semantics, not syntax:
- Account hierarchies
- Transaction structure
- Amount precision
- Metadata

### Extensibility

Format-specific features are preserved in extension fields:
- Beancount-specific: plugins, custom directives
- Ledger-specific: virtual postings, expressions
- hledger-specific: assertions, forecasts

### Validation

The schema enforces:
- Required fields (date, postings)
- Type constraints (amounts, dates)
- Referential integrity (accounts exist)

## Data Model

### Journal

Top-level container for all accounting data.

```json
{
  "version": "1.0",
  "source_format": "beancount",
  "options": {},
  "commodities": [],
  "accounts": [],
  "prices": [],
  "directives": []
}
```

### Commodity

Currency or commodity definition.

```json
{
  "symbol": "USD",
  "name": "US Dollar",
  "precision": 2,
  "format": {
    "symbol_position": "prefix",
    "thousands_separator": ",",
    "decimal_separator": "."
  }
}
```

### Account

Account definition with metadata.

```json
{
  "name": "Assets:Bank:Checking",
  "type": "asset",
  "opened": "2020-01-01",
  "closed": null,
  "currencies": ["USD"],
  "metadata": {
    "institution": "Chase"
  }
}
```

### Transaction

Complete transaction with postings.

```json
{
  "type": "transaction",
  "date": "2024-01-15",
  "flag": "*",
  "payee": "Whole Foods",
  "narration": "Weekly groceries",
  "tags": ["food"],
  "links": [],
  "metadata": {},
  "postings": [
    {
      "account": "Assets:Bank:Checking",
      "amount": {
        "number": "-50.00",
        "currency": "USD"
      },
      "cost": null,
      "price": null,
      "metadata": {}
    },
    {
      "account": "Expenses:Food:Groceries",
      "amount": null,
      "cost": null,
      "price": null,
      "metadata": {}
    }
  ]
}
```

### Amount

Precise decimal amount with currency.

```json
{
  "number": "185.50",
  "currency": "USD"
}
```

Note: `number` is a string to preserve precision.

### Cost

Cost basis for lot tracking.

```json
{
  "amount": {
    "number": "185.50",
    "currency": "USD"
  },
  "date": "2024-01-15",
  "label": null
}
```

### Price Annotation

Price at time of transaction.

```json
{
  "amount": {
    "number": "195.00",
    "currency": "USD"
  },
  "total": false
}
```

### Balance Assertion

```json
{
  "type": "balance",
  "date": "2024-01-31",
  "account": "Assets:Bank:Checking",
  "amount": {
    "number": "1000.00",
    "currency": "USD"
  }
}
```

### Price Directive

```json
{
  "type": "price",
  "date": "2024-01-15",
  "commodity": "AAPL",
  "amount": {
    "number": "185.00",
    "currency": "USD"
  }
}
```

## Format-Specific Extensions

### Beancount Extensions

```json
{
  "beancount": {
    "documents": [
      {
        "date": "2024-01-15",
        "account": "Assets:Bank:Checking",
        "path": "/path/to/statement.pdf"
      }
    ],
    "events": [
      {
        "date": "2024-01-15",
        "type": "location",
        "value": "New York"
      }
    ],
    "notes": [],
    "queries": [],
    "customs": []
  }
}
```

### Ledger Extensions

```json
{
  "ledger": {
    "virtual_postings": [
      {
        "posting_index": 2,
        "type": "unbalanced"
      }
    ],
    "automated_transactions": [
      {
        "pattern": "/Groceries/",
        "postings": []
      }
    ],
    "periodic_transactions": []
  }
}
```

### hledger Extensions

```json
{
  "hledger": {
    "assertion_type": "inclusive",
    "forecasts": [],
    "timedot_entries": []
  }
}
```

## Serialization

### JSON

Primary format for portability.

```json
{
  "version": "1.0",
  "source_format": "beancount",
  "commodities": [...],
  "accounts": [...],
  "directives": [...]
}
```

### Protocol Buffers

For performance-critical applications. See [journal.proto](journal.proto).

## Validation Rules

1. **Dates** must be valid ISO 8601 (YYYY-MM-DD)
2. **Amounts** must be valid decimal strings
3. **Accounts** referenced in postings must be defined
4. **Currencies** in amounts must be defined
5. **Transaction postings** must balance (within tolerance)

## Conversion Workflow

```
Source Format ──parse──► AST ──convert──► Interchange ──convert──► Target AST ──emit──► Target Format
```

### Example

```bash
# Convert Beancount to Ledger via interchange
bean-to-interchange input.beancount > journal.json
interchange-to-ledger journal.json > output.ledger
```

## Use Cases

1. **Format migration** - Move between tools
2. **Backup/archive** - Tool-independent storage
3. **Analysis tools** - Standard input format
4. **Web services** - API interchange
5. **Testing** - Compare implementations

## See Also

- [JSON Schema](journal.schema.json)
- [Protocol Buffers](journal.proto)
