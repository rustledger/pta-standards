# Breaking Changes: v2 to v3

## Overview

This document lists all breaking changes between Beancount v2 and v3. Most changes are minor and affect edge cases.

> **Note**: This document has been validated against beancount 3.2.0 (January 2025).

## Syntax Changes

### None

The core syntax is unchanged. All valid v2 directives parse in v3.

## Option Changes

### Removed Options

| Option | Reason | Alternative |
|--------|--------|-------------|
| `experiment_explicit_tolerances` | Now default behavior | Remove option |
| `encoding` | UTF-8 only in v3 | Convert files to UTF-8 |

### Deprecated Options (Still Work)

| Option | Status | Notes |
|--------|--------|-------|
| `allow_deprecated_none_for_tags_and_links` | Deprecated | Produces warning, still accepted |

### Type Changes

| Option | v2 Type | v3 Type |
|--------|---------|---------|
| `operating_currency` | String | List of strings |

### Unchanged Options

The following options use the same names in v3 as in v2:

- `name_assets` - Root name for asset accounts (default: "Assets")
- `name_liabilities` - Root name for liability accounts (default: "Liabilities")
- `name_equity` - Root name for equity accounts (default: "Equity")
- `name_income` - Root name for income accounts (default: "Income")
- `name_expenses` - Root name for expense accounts (default: "Expenses")

## Plugin Changes

### Plugin Path Changes

| v2 Path | v3 Path | Status |
|---------|---------|--------|
| `beancount.plugins.auto` | `beancount.plugins.auto_accounts` | Both work (aliased) |
| `beancount.plugins.prices` | `beancount.plugins.implicit_prices` | **Breaking**: Only v3 path works |
| `beancount.plugins.check_closing` | `beancount.plugins.close_tree` | Both work (aliased) |

Only `beancount.plugins.prices` is a true breaking change.

### Removed Plugins

| Plugin | Reason | Alternative |
|--------|--------|-------------|
| `beancount.plugins.fill_account` | Rarely used | Custom plugin |
| `beancount.plugins.tag_pending` | Superseded | Use metadata |

### Plugin API Changes

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
tolerance = 0.5 * 10^(-precision)
```

Where precision is the maximum decimal places used in the transaction.

**Impact:** Some transactions that balanced in v2 may not balance in v3, or vice versa.

**Example:**
```beancount
; For 2 decimal places, tolerance = 0.005 USD
; 0.004 imbalance - PASSES
2024-01-15 * "Within tolerance"
  Expenses:Food      10.00 USD
  Assets:Checking   -10.004 USD

; 0.01 imbalance - FAILS
2024-01-15 * "Outside tolerance"
  Expenses:Food      10.00 USD
  Assets:Checking   -10.01 USD
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

Valid booking methods: `STRICT`, `FIFO`, `LIFO`, `HIFO`, `AVERAGE`, `NONE`

### Balance Assertion Timing

**v2:** Checked at end of day.

**v3:** Checked at start of day (before same-day transactions).

**Impact:** Assertions may need date adjustment:

```beancount
2024-01-15 * "Deposit"
  Assets:Checking  100 USD
  Income:Salary   -100 USD

; v3: This checks balance BEFORE the deposit
; Asserts 0 USD (starting balance) - PASSES
2024-01-15 balance Assets:Checking 0 USD

; v3: To check AFTER same-day transactions, use next day
2024-01-16 balance Assets:Checking 100 USD
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

## Error Handling

### Error Types

Beancount 3.x uses Python exception classes:

| Error Class | Description |
|-------------|-------------|
| `ParserError` | Syntax and parsing errors |
| `ValidationError` | Semantic validation errors |
| `DeprecatedError` | Deprecated feature warnings |

### Error Format

Errors are Python objects with structured data:

```python
ValidationError(
    source={'filename': 'ledger.beancount', 'lineno': 42},
    message="Invalid reference to unknown account 'Assets:Unknown'",
    entry=<Transaction object>
)
```

## File Handling Changes

### Encoding

**v2:** Multiple encodings supported via option.

**v3:** UTF-8 only.

```beancount
; v2 (worked)
option "encoding" "latin-1"

; v3 (removed - produces error)
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

## Compatibility Matrix

| Feature | v2 | v3 | Action |
|---------|----|----|--------|
| Core syntax | Y | Y | None |
| Old option names | Y | Y | None needed |
| `beancount.plugins.prices` | Y | N | Update to `implicit_prices` |
| Lowercase booking methods | Y | N | Uppercase |
| Non-UTF8 files | Y | N | Convert to UTF-8 |
| `operating_currency` as string | Y | N | Handle as list |

Legend: Y = Works, N = Error
