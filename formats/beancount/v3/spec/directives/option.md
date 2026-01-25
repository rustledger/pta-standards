# Option Directive

Options are global configuration directives declared without a date.

## Syntax

```beancount
option "name" "value"
```

Options MAY appear anywhere in the file.
All options are collected before processing directives.

---

## Core Configuration

### title

- **Type:** String
- **Default:** (none)
- **Repeatable:** No
- **Description:** The title of this ledger. Shows in reports.

```beancount
option "title" "Personal Finances 2024"
```

### operating_currency

- **Type:** String
- **Default:** (none)
- **Repeatable:** Yes
- **Description:** Main currencies for reporting. Creates dedicated columns in reports.

```beancount
option "operating_currency" "USD"
option "operating_currency" "EUR"
```

---

## Account Root Names

Customize the five root account type names.

| Option | Default | Description |
|--------|---------|-------------|
| `name_assets` | "Assets" | Root name for asset accounts |
| `name_liabilities` | "Liabilities" | Root name for liability accounts |
| `name_equity` | "Equity" | Root name for equity accounts |
| `name_income` | "Income" | Root name for income accounts |
| `name_expenses` | "Expenses" | Root name for expense accounts |

**Example:**
```beancount
option "name_income" "Revenue"
option "name_equity" "Capital"
```

---

## Special Equity Accounts

Used by OPEN/CLOSE statement operators in BQL.

| Option | Default | Purpose |
|--------|---------|---------|
| `account_previous_balances` | "Opening-Balances" | Summarize prior balances |
| `account_previous_earnings` | "Earnings:Previous" | Prior retained earnings |
| `account_previous_conversions` | "Conversions:Previous" | Prior conversion residuals |
| `account_current_earnings` | "Earnings:Current" | Current period net income |
| `account_current_conversions` | "Conversions:Current" | Current conversion residuals |
| `account_rounding` | (disabled) | Accumulate rounding errors |

---

## Tolerance & Precision

### inferred_tolerance_default

- **Type:** Currency:Decimal mapping
- **Default:** (per-currency defaults)
- **Repeatable:** Yes
- **Description:** Default tolerance when not inferrable from amounts.

```beancount
option "inferred_tolerance_default" "CHF:0.01"
option "inferred_tolerance_default" "JPY:1"
```

### inferred_tolerance_multiplier

- **Type:** Decimal
- **Default:** 0.5
- **Repeatable:** No
- **Description:** Multiplier applied to inferred tolerances.

### infer_tolerance_from_cost

- **Type:** Boolean
- **Default:** TRUE
- **Repeatable:** No
- **Description:** Expand tolerance to include values inferred from cost currencies.

---

## Booking

### booking_method

- **Type:** String
- **Default:** "STRICT"
- **Values:** "STRICT", "FIFO", "LIFO", "AVERAGE", "NONE"
- **Repeatable:** No
- **Description:** Default booking method for all accounts. Can be overridden per-account in `open` directive.

```beancount
option "booking_method" "FIFO"
```

---

## Documents

### documents

- **Type:** Path
- **Default:** (none)
- **Repeatable:** Yes
- **Description:** Directory roots to search for document files.

```beancount
option "documents" "/home/user/documents/financial"
option "documents" "receipts/"
```

Document files MUST match pattern: `YYYY-MM-DD.description.extension`

---

## Rendering

### render_commas

- **Type:** Boolean
- **Default:** TRUE
- **Repeatable:** No
- **Description:** Include thousand separators in number output.

### long_string_maxlines

- **Type:** Integer
- **Default:** 64
- **Repeatable:** No
- **Description:** Line threshold for multi-line string warnings.

---

## Currency Conversion

### conversion_currency

- **Type:** String
- **Default:** "NOTHING"
- **Repeatable:** No
- **Description:** Imaginary currency used for conversions at zero rate. Allows currency exchanges without explicit prices.

```beancount
option "conversion_currency" "NOTHING"
```

---

## Plugins

### plugin_processing_mode

- **Type:** String
- **Default:** "default"
- **Values:** "default", "raw"
- **Repeatable:** No
- **Description:** "default" enables built-in plugins; "raw" runs only user plugins.

---

## Legacy & Experimental

### use_legacy_fixed_tolerances

- **Type:** Boolean
- **Default:** TRUE
- **Repeatable:** No
- **Description:** Restore legacy fixed tolerance handling. When true, balance/pad use 0.015 and transactions use 0.005.

### experiment_explicit_tolerances

- **Type:** Boolean
- **Default:** TRUE
- **Repeatable:** No
- **Description:** Enable explicit tolerance syntax on balance assertions: `<number> ~ <tolerance> <currency>`.

---

## Deprecated Options

These options are deprecated and SHOULD NOT be used in new files:

| Option | Replacement |
|--------|-------------|
| `default_tolerance` | `inferred_tolerance_default` |
| `tolerance` | No effect; use tolerance options above |
| `plugin` (as option) | Use `plugin` directive instead |

---

## Option Value Types

| Type | Format | Example |
|------|--------|---------|
| String | Quoted text | `"My Ledger"` |
| Boolean | TRUE/FALSE (case-insensitive) | `"TRUE"`, `"false"` |
| Decimal | Numeric string | `"0.5"` |
| Path | File path (relative to ledger) | `"receipts/"` |
| Currency:Value | Colon-separated pair | `"CHF:0.01"` |

---

## Processing Order

1. Parse all `option` directives from all files (including includes)
2. Apply options in order encountered
3. Later values override earlier for non-repeatable options
4. Repeatable options accumulate values

---

## Validation

- Unknown option names generate warning (E7001)
- Invalid values generate error (E7002)
- Duplicate non-repeatable options generate warning (E7003)
