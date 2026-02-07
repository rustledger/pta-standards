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

**Note:** The v2 to v3 transition in Python beancount is largely backward compatible. Most option names and plugin paths remained the same.

#### Key Changes

1. **Query tool**: `bean-query` is now a separate package (`beanquery`)
2. **Booking methods**: Must be uppercase (`"FIFO"` not `"fifo"`)
3. **Boolean options**: Must be uppercase (`"TRUE"` not `"true"`)

### Step 3: Update Custom Plugins

If you have custom plugins, update them for v3 API changes:

#### Options Map

The `operating_currency` option returns a list:

```python
def plugin_fn(entries, options_map):
    currencies = options_map['operating_currency']  # List of strings
    currency = currencies[0] if currencies else 'USD'
```

**Note:** `TxnPosting` still exists in v3—it was not removed as some documentation suggested.

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

**Note:** There is no official `bean-migrate` tool. Migration from v2 to v3 is typically done by:

1. Running `bean-check` to identify any parsing errors
2. Manually fixing any issues (usually just uppercase booking methods/booleans)
3. Verifying results match v2 output

Most v2 ledgers work without modification in v3.

## Common Issues

### Issue: Booking Method Case

**v2:** Mixed case may have worked.

**v3:** Uppercase required.

**Before:**
```beancount
2024-01-01 open Assets:Stock AAPL "fifo"
```

**After:**
```beancount
2024-01-01 open Assets:Stock AAPL "FIFO"
```

### Issue: Boolean Option Case

**v2:** Mixed case may have worked.

**v3:** Uppercase required.

**Before:**
```beancount
option "insert_pythonpath" "True"
```

**After:**
```beancount
option "insert_pythonpath" "TRUE"
```

### Issue: Query Tool Change

In v3, the query functionality is in a separate package:

**v2:**
```bash
bean-query ledger.beancount "SELECT ..."
```

**v3:**
```bash
pip install beanquery
bean-query ledger.beancount "SELECT ..."
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
# Backup before making any changes
cp ledger.beancount ledger-v2-backup.beancount

# Make edits to fix any issues
# ...

# If issues, restore from backup
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
