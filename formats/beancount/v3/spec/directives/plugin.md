# Plugin Directive

## Overview

The `plugin` directive loads a transformation module that processes the ledger's directives. Plugins can validate, modify, or generate new directives.

## Syntax

```ebnf
plugin = "plugin" WHITESPACE module [WHITESPACE config]

module = string
config = string
```

## Components

### Module

A string specifying the plugin to load:
- Python module path: `"beancount.plugins.auto_accounts"`
- Local file: `"plugins/my_plugin"`
- Package name: `"my_package.plugin"`

### Config (Optional)

A string passed to the plugin as configuration. Format is plugin-specific.

## Examples

### Built-in Plugins

```beancount
plugin "beancount.plugins.auto_accounts"
plugin "beancount.plugins.implicit_prices"
plugin "beancount.plugins.check_closing"
```

### With Configuration

```beancount
plugin "beancount.plugins.auto_accounts" "Expenses:Misc"
plugin "beancount.plugins.unrealized_gains" "Unrealized"
```

### Third-Party Plugins

```beancount
plugin "fava.plugins.tag_discovered_documents"
plugin "beancount_import.hooks"
```

### Local Plugins

```beancount
plugin "plugins/validate_categories"
plugin "plugins/auto_tag" "travel:Expenses:Travel"
```

## Plugin Interface

Plugins implement a standard interface:

```python
def plugin_function(entries, options_map, config=None):
    """
    Process ledger entries.

    Args:
        entries: List of directives
        options_map: Dictionary of options
        config: Plugin configuration string

    Returns:
        Tuple of (new_entries, errors)
    """
    new_entries = []
    errors = []

    for entry in entries:
        # Process entry
        new_entries.append(entry)

    return new_entries, errors

__plugins__ = [plugin_function]
```

## Loading Order

Plugins are loaded and applied in order of declaration:

```beancount
; Applied first
plugin "plugin_a"

; Applied second (sees output of plugin_a)
plugin "plugin_b"

; Applied third (sees output of plugin_b)
plugin "plugin_c"
```

Order matters when plugins depend on each other's output.

## Built-in Plugins

### auto_accounts

Automatically opens accounts on first use:

```beancount
plugin "beancount.plugins.auto_accounts"

; No explicit open needed
2024-01-15 * "Coffee"
  Expenses:Food:Coffee  5 USD  ; Auto-opened
  Assets:Cash
```

### implicit_prices

Creates price entries from transaction prices:

```beancount
plugin "beancount.plugins.implicit_prices"

2024-01-15 * "Buy stock"
  Assets:Stock  10 AAPL {150 USD}
  Assets:Cash

; Automatically creates:
; 2024-01-15 price AAPL 150 USD
```

### check_closing

Validates that closed accounts have zero balance:

```beancount
plugin "beancount.plugins.check_closing"

2024-12-31 close Assets:OldAccount
; Error if balance is non-zero
```

### unrealized_gains

Adds unrealized gains/losses transactions:

```beancount
plugin "beancount.plugins.unrealized_gains" "Unrealized"

; Generates entries like:
; 2024-12-31 * "Unrealized gains"
;   Assets:Stock  0 AAPL {0 USD}
;   Income:Unrealized  -500 USD
```

### check_commodity

Validates that all commodities are declared:

```beancount
plugin "beancount.plugins.check_commodity"

2024-01-01 commodity USD  ; Must declare
2024-01-01 commodity EUR

2024-01-15 * "Valid"
  Assets:Cash  100 USD
  Expenses:Food

2024-01-16 * "Error - GBP not declared"
  Assets:Cash  50 GBP  ; Error!
  Expenses:Food
```

## Plugin Configuration

Configuration is passed as a string; plugins parse it themselves:

### Simple Value

```beancount
plugin "plugin" "value"
```

### Key-Value Pairs

```beancount
plugin "plugin" "key1=value1 key2=value2"
```

### JSON Configuration

```beancount
plugin "plugin" '{"threshold": 100, "accounts": ["Expenses:Food"]}'
```

### Multi-line (via Option)

```beancount
option "plugin_config:my_plugin" "
  threshold: 100
  accounts:
    - Expenses:Food
    - Expenses:Transport
"
plugin "my_plugin"
```

## Plugin Categories

### Validation Plugins

Check data integrity:

```beancount
plugin "check_duplicate_transactions"
plugin "check_payee_format"
plugin "check_tag_consistency"
```

### Transformation Plugins

Modify or add directives:

```beancount
plugin "split_expenses"       ; Split shared expenses
plugin "categorize_payee"     ; Auto-categorize by payee
plugin "currency_conversion"  ; Convert to base currency
```

### Generation Plugins

Create new directives:

```beancount
plugin "depreciation"         ; Generate depreciation entries
plugin "amortization"         ; Generate amortization schedule
plugin "forecast"             ; Generate future transactions
```

## Error Handling

Plugins return errors that appear in output:

```
error: [plugin:check_closing] Account closed with non-zero balance
  --> ledger.beancount:50:1
   |
50 | 2024-12-31 close Assets:OldAccount
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ balance: 100 USD
```

## Security

See [security/plugins/](../../../../../security/plugins/) for plugin security guidelines:

- Sandboxing requirements
- Capability restrictions
- Resource limits

## Disabling Plugins

Temporarily disable with comments:

```beancount
; plugin "expensive_validation"  ; Disabled for faster testing
plugin "essential_plugin"
```

Or via command line:

```bash
bean-check --no-plugins ledger.beancount
bean-check --skip-plugin=expensive_validation ledger.beancount
```

## Creating Plugins

See the [Plugin Development Guide](../../../../../implementations/guide/parser.md) for:

1. Plugin interface specification
2. Entry manipulation helpers
3. Error reporting
4. Testing plugins
5. Packaging and distribution

## Implementation Notes

1. Load plugins in declaration order
2. Pass configuration string to plugin
3. Chain plugin outputs (output of one is input to next)
4. Collect and report all plugin errors
5. Support plugin discovery (entry points)
6. Implement security controls (sandboxing)
