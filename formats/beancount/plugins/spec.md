# Beancount Plugin Specification

This document specifies the Beancount plugin system.

## Overview

Plugins extend Beancount's functionality:
- Custom validation rules
- Automatic transaction generation
- Data transformation
- External integrations

## Plugin Interface

### Basic Structure

```python
def plugin_function(entries, options_map):
    """
    Process entries and return modified entries with errors.

    Args:
        entries: List of directive objects
        options_map: Dictionary of beancount options

    Returns:
        Tuple of (new_entries, errors)
    """
    errors = []
    new_entries = []

    for entry in entries:
        # Process entry
        new_entries.append(entry)

    return new_entries, errors
```

### With Configuration

```python
def plugin_function(entries, options_map, config_string):
    """Plugin with configuration string."""
    pass
```

## Loading Plugins

### In Beancount File

```beancount
plugin "beancount.plugins.leafonly"
plugin "mypackage.myplugin"
plugin "mypackage.myplugin" "config string"
```

### Built-in Plugins

| Plugin | Description |
|--------|-------------|
| `leafonly` | Only allow postings to leaf accounts |
| `onecommodity` | One commodity per account |
| `noduplicates` | Detect duplicate transactions |
| `check_commodity` | Validate commodity directives |

## Entry Types

Plugins receive these entry types:

```python
from beancount.core.data import (
    Open, Close, Commodity, Pad, Balance,
    Transaction, Note, Event, Query,
    Document, Custom, Directive
)
```

## Creating Entries

### Transaction

```python
from beancount.core.data import Transaction, TxnPosting
from beancount.core.amount import Amount
from decimal import Decimal

txn = Transaction(
    meta={'filename': 'plugin', 'lineno': 0},
    date=date(2024, 1, 15),
    flag='*',
    payee='Generated',
    narration='Auto-generated transaction',
    tags=frozenset(),
    links=frozenset(),
    postings=[
        TxnPosting(
            account='Expenses:Test',
            units=Amount(Decimal('100'), 'USD'),
            cost=None,
            price=None,
            flag=None,
            meta=None
        ),
        TxnPosting(
            account='Assets:Bank',
            units=Amount(Decimal('-100'), 'USD'),
            cost=None,
            price=None,
            flag=None,
            meta=None
        )
    ]
)
```

## Error Reporting

```python
from beancount.core.data import new_error

error = new_error(
    meta,
    "Error message",
    entry
)
errors.append(error)
```

## Common Patterns

### Validation Plugin

```python
def validate_amounts(entries, options_map):
    """Validate all amounts are positive."""
    errors = []

    for entry in entries:
        if isinstance(entry, Transaction):
            for posting in entry.postings:
                if posting.units.number < 0:
                    errors.append(new_error(
                        entry.meta,
                        f"Negative amount in {posting.account}",
                        entry
                    ))

    return entries, errors
```

### Transformation Plugin

```python
def split_transactions(entries, options_map):
    """Split transactions by some criteria."""
    new_entries = []

    for entry in entries:
        if isinstance(entry, Transaction):
            # Transform transaction
            new_entries.extend(transform(entry))
        else:
            new_entries.append(entry)

    return new_entries, []
```

### Generation Plugin

```python
def auto_categorize(entries, options_map):
    """Auto-generate category postings."""
    new_entries = list(entries)

    for entry in entries:
        if isinstance(entry, Transaction):
            # Generate additional entries
            generated = create_category_entry(entry)
            if generated:
                new_entries.append(generated)

    return new_entries, []
```

## Plugin Ordering

Plugins execute in order of declaration:

```beancount
plugin "first_plugin"   ; Runs first
plugin "second_plugin"  ; Runs second
plugin "third_plugin"   ; Runs third
```

## Configuration

### Passing Config

```beancount
plugin "myplugin" "threshold=100,currency=USD"
```

### Parsing Config

```python
def myplugin(entries, options_map, config_string):
    config = parse_config(config_string)
    threshold = config.get('threshold', 50)
    currency = config.get('currency', 'USD')
    # Use config...
```

## Best Practices

1. **Immutable entries** - Don't modify input entries
2. **Return all entries** - Include unmodified entries
3. **Report errors properly** - Use new_error()
4. **Document configuration** - Clear config format
5. **Idempotent** - Same input, same output
6. **Handle edge cases** - Empty entries, missing fields

## Testing Plugins

```python
import unittest
from beancount import loader

class TestMyPlugin(unittest.TestCase):
    def test_basic(self):
        content = '''
        plugin "myplugin"

        2024-01-01 open Assets:Bank USD
        '''
        entries, errors, options = loader.load_string(content)
        self.assertEqual(len(errors), 0)
```

## See Also

- [Plugin Hooks](hooks.md)
- [Plugin Sandboxing](sandboxing.md)
- [Beancount Documentation](https://beancount.github.io/docs/)
