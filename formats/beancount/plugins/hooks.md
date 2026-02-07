# Beancount Plugin Hooks

This document specifies plugin hook points in Beancount.

## Overview

Hooks define when plugins execute:
- After parsing
- During validation
- Before reporting

## Hook Points

### Post-Parse Hook

Primary hook - runs after parsing:

```python
def my_plugin(entries, options_map):
    """Called after file is parsed."""
    return entries, []
```

### Entry-Specific Hooks

Process specific entry types:

```python
def process_transactions(entries, options_map):
    for entry in entries:
        if isinstance(entry, Transaction):
            # Process transaction
            pass
    return entries, []
```

## Hook Execution Order

1. File parsed into entries
2. Plugins execute in declaration order
3. Built-in validation runs
4. Reports generated

```beancount
; Plugins run in this order:
plugin "plugin_a"  ; First
plugin "plugin_b"  ; Second
plugin "plugin_c"  ; Third
; Then: validation, then reports
```

## Available Data

### Options Map

```python
def my_plugin(entries, options_map):
    title = options_map.get('title', 'Untitled')
    operating_currency = options_map.get('operating_currency', ['USD'])
    # Access any option...
```

### Entry Metadata

```python
for entry in entries:
    filename = entry.meta.get('filename')
    lineno = entry.meta.get('lineno')
    custom_meta = entry.meta.get('my-tag')
```

## Modifying Entries

### Replace Entry

```python
from beancount.core.data import Transaction

def modify_plugin(entries, options_map):
    new_entries = []
    for entry in entries:
        if isinstance(entry, Transaction):
            # Create modified copy
            modified = entry._replace(
                narration=entry.narration.upper()
            )
            new_entries.append(modified)
        else:
            new_entries.append(entry)
    return new_entries, []
```

### Add Entries

```python
def add_entries_plugin(entries, options_map):
    new_entries = list(entries)

    # Add new entry
    new_txn = Transaction(...)
    new_entries.append(new_txn)

    return new_entries, []
```

### Remove Entries

```python
def filter_plugin(entries, options_map):
    filtered = [e for e in entries if should_keep(e)]
    return filtered, []
```

## Error Hooks

### Reporting Errors

```python
from beancount.core.data import new_error

def validation_plugin(entries, options_map):
    errors = []

    for entry in entries:
        if not is_valid(entry):
            errors.append(new_error(
                entry.meta,
                "Validation failed: reason",
                entry
            ))

    return entries, errors
```

### Error Severity

- Errors stop processing
- Return empty list for no errors

## Chaining Plugins

Output of one plugin feeds into next:

```beancount
plugin "normalize"    ; Normalizes entries
plugin "validate"     ; Validates normalized entries
plugin "transform"    ; Transforms validated entries
```

```python
# Plugin A output becomes Plugin B input
entries_a, errors_a = plugin_a(entries, options)
entries_b, errors_b = plugin_b(entries_a, options)
```

## Context Access

### Account Information

```python
from beancount.core import getters

def account_plugin(entries, options_map):
    accounts = getters.get_accounts(entries)
    # Set of all account names
```

### Commodity Information

```python
from beancount.core import getters

def commodity_plugin(entries, options_map):
    commodities = getters.get_commodities(entries)
```

## Examples

### Tagging Hook

```python
def auto_tag(entries, options_map):
    """Add tags based on account."""
    new_entries = []

    for entry in entries:
        if isinstance(entry, Transaction):
            new_tags = set(entry.tags)

            for posting in entry.postings:
                if 'Food' in posting.account:
                    new_tags.add('food')

            entry = entry._replace(tags=frozenset(new_tags))

        new_entries.append(entry)

    return new_entries, []
```

### Validation Hook

```python
def require_payee(entries, options_map):
    """Require payee on all transactions."""
    errors = []

    for entry in entries:
        if isinstance(entry, Transaction):
            if not entry.payee:
                errors.append(new_error(
                    entry.meta,
                    "Transaction requires payee",
                    entry
                ))

    return entries, errors
```

### Generation Hook

```python
def monthly_summary(entries, options_map):
    """Generate monthly summary entries."""
    new_entries = list(entries)

    # Group by month
    by_month = group_entries_by_month(entries)

    # Generate summary entries
    for month, month_entries in by_month.items():
        summary = create_summary(month, month_entries)
        new_entries.append(summary)

    return new_entries, []
```

## Best Practices

1. **Order matters** - Consider plugin dependencies
2. **Preserve entries** - Don't lose input entries
3. **Fail fast** - Report errors immediately
4. **Document hooks** - Explain when plugin runs
5. **Test thoroughly** - Test with various inputs

## See Also

- [Plugin Specification](spec.md)
- [Plugin Sandboxing](sandboxing.md)
