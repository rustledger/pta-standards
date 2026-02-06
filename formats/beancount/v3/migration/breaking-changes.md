# Breaking Changes: v2 to v3

## Overview

This document lists all breaking changes between Beancount v2 and v3. Most changes are minor and affect edge cases.

## Syntax Changes

### None

The core syntax is unchanged. All valid v2 directives parse in v3.

## Option Changes

### Renamed Options

| v2 Option | v3 Option | Notes |
|-----------|-----------|-------|
| `name_assets` | `account_root_assets` | Clearer naming |
| `name_liabilities` | `account_root_liabilities` | |
| `name_equity` | `account_root_equity` | |
| `name_income` | `account_root_income` | |
| `name_expenses` | `account_root_expenses` | |

### Removed Options

| Option | Reason | Alternative |
|--------|--------|-------------|
| `experiment_explicit_tolerances` | Now default behavior | Remove option |
| `allow_deprecated_none_for_tags_and_links` | Deprecated syntax removed | Use empty |

### Type Changes

| Option | v2 Type | v3 Type |
|--------|---------|---------|
| `operating_currency` | String | List of strings |
| `insert_pythonpath` | String "True"/"False" | String "TRUE"/"FALSE" |

## Plugin Changes

### Renamed Plugins

| v2 Path | v3 Path |
|---------|---------|
| `beancount.plugins.auto` | `beancount.plugins.auto_accounts` |
| `beancount.plugins.prices` | `beancount.plugins.implicit_prices` |
| `beancount.plugins.check_closing` | `beancount.plugins.close_tree` |

### Removed Plugins

| Plugin | Reason | Alternative |
|--------|--------|-------------|
| `beancount.plugins.fill_account` | Rarely used | Custom plugin |
| `beancount.plugins.tag_pending` | Superseded | Use metadata |

### Plugin API Changes

#### Entry Types

```python
# v2: TxnPosting existed
from beancount.core.data import TxnPosting

# v3: Use Posting directly
from beancount.core.data import Posting
```

#### Options Map

```python
# v2: operating_currency was a single string
currency = options_map['operating_currency']

# v3: operating_currency is a list
currencies = options_map['operating_currency']
```

#### Plugin Signature

```python
# v2: Optional config parameter
def my_plugin(entries, options_map, config=None):
    pass

# v3: Same, but config parsing standardized
def my_plugin(entries, options_map, config=None):
    # Config is always a string if provided
    pass
```

## Semantic Changes

### Tolerance Calculation

**v2:** Multiple tolerance modes, configurable.

**v3:** Single standardized mode:
```
tolerance = 0.5 × 10^(-precision)
```

Where precision is the maximum decimal places used in the transaction.

**Impact:** Some transactions that balanced in v2 may not balance in v3, or vice versa.

**Migration:**
```beancount
; If needed, set explicit tolerance
option "tolerance" "0.005"
```

### Booking Method Case

**v2:** Case-insensitive booking methods.

**v3:** Case-sensitive, uppercase required.

```beancount
; v2 (worked)
2024-01-01 open Assets:Stock AAPL "fifo"

; v3 (required)
2024-01-01 open Assets:Stock AAPL "FIFO"
```

### Balance Assertion Timing

**v2:** Checked at end of day.

**v3:** Checked at start of day (before same-day transactions).

**Impact:** Assertions may need date adjustment:

```beancount
; v2: Checked after 2024-01-15 transactions
2024-01-15 balance Assets:Checking 1000 USD

; v3: Checked before 2024-01-15 transactions
; May need:
2024-01-16 balance Assets:Checking 1000 USD
```

### Empty Cost Specification

**v2:** `{}` sometimes inferred cost from context.

**v3:** `{}` strictly means "use booking method."

```beancount
; v2: Might infer cost
Assets:Stock -10 AAPL {}

; v3: Always uses booking method (FIFO, LIFO, etc.)
Assets:Stock -10 AAPL {}
```

## Error Code Changes

### New Error Codes

| Code | Description |
|------|-------------|
| E1005 | Invalid account name |
| E2002 | Balance tolerance exceeded |
| E4004 | Negative inventory |

### Changed Error Codes

| v2 Code | v3 Code | Change |
|---------|---------|--------|
| Multiple | E1001 | Consolidated account errors |
| Multiple | E3001 | Consolidated balance errors |

### Error Message Format

**v2:** Plain text errors.

**v3:** Structured errors with location:
```
error: Account not opened
  --> ledger.beancount:42:3
   |
42 |   Assets:Unknown  100 USD
   |   ^^^^^^^^^^^^^^
   |
   = hint: add 'open' directive before this transaction
```

## File Handling Changes

### Encoding

**v2:** Multiple encodings supported via option.

**v3:** UTF-8 only.

```beancount
; v2 (worked)
option "encoding" "latin-1"

; v3 (removed)
; Convert files to UTF-8
```

### Include Path Resolution

**v2:** Some edge cases in relative path handling.

**v3:** Strictly relative to including file's directory.

### BOM Handling

**v2:** BOM sometimes caused issues.

**v3:** UTF-8 BOM explicitly ignored.

## Query Language Changes

### BQL Syntax

No breaking changes. All v2 queries work in v3.

### New Functions

v3 adds new BQL functions (non-breaking):
- `root(account, n)` - Get first n components
- `leaf(account)` - Get last component
- `parent(account)` - Get parent account

## Date Handling

### Date Format

No change: `YYYY-MM-DD` and `YYYY/MM/DD` both supported.

### Directive Ordering

**v2:** Implementation-defined ordering for same-date directives.

**v3:** Specified ordering:
1. Balance assertions first
2. Other directives by file order

## Deprecation Warnings

v3 produces warnings for v2 patterns that still work but are deprecated:

| Pattern | Warning | Future |
|---------|---------|--------|
| Old option names | Deprecated | Will error in v4 |
| Old plugin paths | Deprecated | Will error in v4 |

## Compatibility Matrix

| Feature | v2 | v3 | Action |
|---------|----|----|--------|
| Core syntax | ✓ | ✓ | None |
| Old option names | ✓ | ⚠ | Update |
| Old plugin paths | ✓ | ⚠ | Update |
| Booking case | ✓ | ✗ | Uppercase |
| Non-UTF8 files | ✓ | ✗ | Convert |

Legend: ✓ Works, ⚠ Warning, ✗ Error
