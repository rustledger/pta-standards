# Migration Guide: Beancount v2 to v3

## Overview

This guide helps users migrate existing Beancount v2 ledgers to v3. Most ledgers require minimal or no changes.

## Compatibility

Beancount v3 is largely backward compatible with v2. Most valid v2 files parse correctly in v3.

### Unchanged

- All directive syntax
- Account naming rules
- Currency/commodity format
- Cost and price specifications
- Metadata syntax
- Tag and link syntax
- Comment syntax

### Changed

See [breaking-changes.md](breaking-changes.md) for the complete list.

## Migration Steps

### Step 1: Check Compatibility

Run the v3 parser on your existing ledger:

```bash
bean-check ledger.beancount
```

Note any errors or warnings.

### Step 2: Update Deprecated Syntax

#### Option Names

Some option names have changed:

| v2 Option | v3 Option |
|-----------|-----------|
| `name_assets` | `account_root_assets` |
| `name_liabilities` | `account_root_liabilities` |
| `name_equity` | `account_root_equity` |
| `name_income` | `account_root_income` |
| `name_expenses` | `account_root_expenses` |

**Before (v2):**
```beancount
option "name_assets" "Actifs"
```

**After (v3):**
```beancount
option "account_root_assets" "Actifs"
```

#### Plugin Module Paths

Some built-in plugin paths have changed:

| v2 Path | v3 Path |
|---------|---------|
| `beancount.plugins.auto` | `beancount.plugins.auto_accounts` |
| `beancount.plugins.prices` | `beancount.plugins.implicit_prices` |

**Before (v2):**
```beancount
plugin "beancount.plugins.auto"
```

**After (v3):**
```beancount
plugin "beancount.plugins.auto_accounts"
```

### Step 3: Update Custom Plugins

If you have custom plugins, update them for v3 API changes:

#### Entry Type Changes

```python
# v2
from beancount.core.data import TxnPosting

# v3
from beancount.core.data import Posting  # TxnPosting removed
```

#### Options Map

```python
# v2
def plugin_fn(entries, options_map):
    currency = options_map['operating_currency']  # String

# v3
def plugin_fn(entries, options_map):
    currencies = options_map['operating_currency']  # List
    currency = currencies[0] if currencies else 'USD'
```

### Step 4: Verify Results

After migration, verify your ledger:

```bash
# Check for errors
bean-check ledger.beancount

# Compare reports
bean-report ledger.beancount balances > v3-balances.txt
diff v2-balances.txt v3-balances.txt

# Run queries
bean-query ledger.beancount "SELECT sum(position) WHERE account ~ 'Assets'"
```

## Automated Migration

### Migration Script

Use the migration tool:

```bash
bean-migrate v2-to-v3 ledger.beancount > ledger-v3.beancount
```

The script:
1. Updates deprecated option names
2. Updates plugin paths
3. Fixes known syntax differences
4. Reports issues requiring manual attention

### Dry Run

Preview changes without modifying:

```bash
bean-migrate v2-to-v3 --dry-run ledger.beancount
```

## Common Issues

### Issue: Implicit Plugin Loading

**v2 Behavior:** Some plugins loaded automatically.

**v3 Behavior:** All plugins must be explicit.

**Fix:**
```beancount
; Add explicit plugin declarations
plugin "beancount.plugins.auto_accounts"
plugin "beancount.plugins.implicit_prices"
```

### Issue: Option Value Types

**v2:** Some options accepted strings.

**v3:** Stricter type checking.

**Example:**
```beancount
; v2 (worked)
option "insert_pythonpath" "True"

; v3 (required)
option "insert_pythonpath" "TRUE"
```

### Issue: Tolerance Defaults

**v2:** Different default tolerance calculation.

**v3:** Standardized tolerance (0.5 × 10^-precision).

**Fix:** Add explicit tolerances if needed:
```beancount
option "tolerance" "0.01"
```

### Issue: Booking Method Names

**v2:** Mixed case accepted.

**v3:** Uppercase required.

**Before:**
```beancount
2024-01-01 open Assets:Stock AAPL "fifo"
```

**After:**
```beancount
2024-01-01 open Assets:Stock AAPL "FIFO"
```

## Testing Migration

### Create Test Suite

Before migrating, create reference outputs:

```bash
# v2 outputs
bean-report ledger.beancount balances > v2-balances.txt
bean-report ledger.beancount holdings > v2-holdings.txt
bean-query ledger.beancount "SELECT * FROM postings" > v2-postings.csv
```

### Compare After Migration

```bash
# v3 outputs
bean-report ledger-v3.beancount balances > v3-balances.txt

# Compare
diff v2-balances.txt v3-balances.txt
```

### Key Comparisons

1. **Balances** - Should be identical
2. **Holdings** - Should be identical
3. **Error count** - Should be equal or fewer
4. **Query results** - Should match

## Rollback

Keep your v2 files until migration is verified:

```bash
# Backup
cp ledger.beancount ledger-v2-backup.beancount

# Migrate
bean-migrate v2-to-v3 ledger.beancount > ledger.beancount

# If issues, rollback
cp ledger-v2-backup.beancount ledger.beancount
```

## Getting Help

- Check [breaking-changes.md](breaking-changes.md) for specific changes
- Search the [mailing list](https://groups.google.com/g/beancount)
- File issues on [GitHub](https://github.com/beancount/beancount/issues)

## Timeline

- **v3.0**: Current stable release
- **v2.x**: Maintenance mode (security fixes only)
- **v2 EOL**: TBD

We recommend migrating to v3 for new features and continued support.
