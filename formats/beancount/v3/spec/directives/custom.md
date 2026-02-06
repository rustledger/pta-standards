# Custom Directive

## Overview

The `custom` directive allows users and plugins to define their own directive types with arbitrary values. It provides an extension mechanism for data that doesn't fit other directive types.

## Syntax

```ebnf
custom = date WHITESPACE "custom" WHITESPACE type [WHITESPACE value]*
         (NEWLINE metadata)*

type  = string
value = string | date | boolean | amount | account | number
```

## Components

### Date

The date of the custom directive.

### Type

A string identifying the custom directive type. Conventionally uses a namespace prefix.

### Values

Zero or more values of various types:
- Strings (quoted)
- Dates (YYYY-MM-DD)
- Booleans (TRUE/FALSE)
- Amounts (number + currency)
- Accounts
- Numbers

## Examples

### Budget Entry

```beancount
2024-01-01 custom "budget" Expenses:Food 500 USD "monthly"
2024-01-01 custom "budget" Expenses:Transport 200 USD "monthly"
2024-01-01 custom "budget" Expenses:Entertainment 150 USD "monthly"
```

### Recurring Transaction Template

```beancount
2024-01-01 custom "recurring" "rent" Assets:Checking -2000 USD Expenses:Rent "monthly" 1
  description: "Monthly rent payment"
  payee: "Landlord LLC"
```

### Goal Tracking

```beancount
2024-01-01 custom "goal" "emergency-fund" Assets:Savings 10000 USD
2024-01-01 custom "goal" "vacation" Assets:Savings 3000 USD 2024-12-31
```

### Account Alias

```beancount
2024-01-01 custom "alias" Assets:Bank:Checking "checking"
2024-01-01 custom "alias" Liabilities:CreditCard:Chase "chase"
```

### Import Configuration

```beancount
2024-01-01 custom "import" "chase-csv" Assets:CreditCard:Chase
  file-pattern: "Chase*.csv"
  date-format: "MM/DD/YYYY"
  skip-rows: 1
```

## Plugin-Defined Customs

Plugins often define their own custom directives:

### Fava Budget Plugin

```beancount
2024-01-01 custom "fava-budget" Expenses:Food 500 USD "monthly"
2024-01-01 custom "fava-budget" Expenses:Rent 2000 USD "monthly"
```

### Auto-Accounts Plugin

```beancount
2024-01-01 custom "auto-accounts" "pattern" "Expenses:.*" "FIFO"
```

### Report Configuration

```beancount
2024-01-01 custom "report-config" "balance-sheet"
  title: "Personal Balance Sheet"
  accounts: "Assets,Liabilities,Equity"
  format: "tree"
```

## Value Types

### String

```beancount
2024-01-01 custom "note" "This is a string value"
```

### Date

```beancount
2024-01-01 custom "deadline" 2024-12-31
```

### Boolean

```beancount
2024-01-01 custom "feature" "dark-mode" TRUE
2024-01-01 custom "feature" "auto-complete" FALSE
```

### Amount

```beancount
2024-01-01 custom "target" 10000 USD
```

### Account

```beancount
2024-01-01 custom "default-account" Assets:Checking
```

### Number

```beancount
2024-01-01 custom "rate" 0.05
2024-01-01 custom "count" 12
```

### Mixed Values

```beancount
2024-01-01 custom "complex" "type" Assets:Account 100 USD 2024-12-31 TRUE
```

## Namespacing

Convention: prefix type names to avoid conflicts:

```beancount
; Plugin-specific
2024-01-01 custom "fava-budget" ...
2024-01-01 custom "beancount-import" ...

; User-specific
2024-01-01 custom "my-budget" ...
2024-01-01 custom "acme-corp-expense" ...
```

## Processing Custom Directives

Custom directives are:
1. Parsed and stored with all directives
2. Available to plugins for processing
3. Ignored by core validation (no built-in semantics)

Plugins access custom directives:

```python
def process_customs(entries, options):
    for entry in entries:
        if isinstance(entry, Custom) and entry.type == "budget":
            # Process budget directive
            account = entry.values[0]
            amount = entry.values[1]
            period = entry.values[2]
```

## Querying Custom Directives

In BQL:

```sql
SELECT date, type, values FROM custom
WHERE type = "budget"
```

## Validation

Custom directives have no built-in validation. Plugins may define their own validation rules.

Common conventions:
- Type should be a meaningful identifier
- Values should be documented for each type
- Use metadata for optional configuration

## Use Cases

### Configuration Storage

```beancount
2024-01-01 custom "config" "operating-currency" "USD"
2024-01-01 custom "config" "fiscal-year-start" 2024-04-01
```

### Workflow Markers

```beancount
2024-01-15 custom "review-needed" Assets:Checking "Monthly reconciliation"
2024-02-01 custom "audit-complete" 2024-01-01 2024-01-31 "John Smith"
```

### External System Links

```beancount
2024-01-15 custom "quickbooks-sync" "INV-2024-001" 1500 USD
2024-01-15 custom "stripe-payout" "po_abc123" Assets:Stripe
```

### Analytics Tags

```beancount
2024-01-01 custom "segment" Expenses:Marketing "acquisition" 0.6
2024-01-01 custom "segment" Expenses:Marketing "retention" 0.4
```

## Implementation Notes

1. Parse all value types (string, date, bool, amount, account, number)
2. Store values in order as a list
3. Make available to plugins
4. No built-in semantic validation
5. Support querying by type
