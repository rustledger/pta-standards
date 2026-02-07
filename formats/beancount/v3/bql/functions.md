# BQL Functions Reference

Complete reference for all BQL functions.

## Position/Amount Functions

### NUMBER

Extract numeric value from an amount or position.

```sql
NUMBER(amount) → Decimal
NUMBER(position) → Decimal
```

**Examples:**
```sql
SELECT NUMBER(units)                    -- 100.00
SELECT NUMBER(position)                 -- Units number from position
```

### CURRENCY

Extract currency from an amount or position.

```sql
CURRENCY(amount) → String
CURRENCY(position) → String
```

**Examples:**
```sql
SELECT CURRENCY(units)                  -- "USD"
```

### UNITS

Extract units (amount without cost) from a position.

```sql
UNITS(position) → Amount
UNITS(amount) → Amount
UNITS(inventory) → String
```

For inventories, returns a formatted string of all positions.

### COST

Calculate total cost of a position or inventory.

```sql
COST(position) → Amount
COST(inventory) → Amount
```

Formula: `|units.number| × cost.number`

Returns NULL if no cost basis.

### WEIGHT

Calculate balancing weight of a position.

```sql
WEIGHT(position) → Amount
WEIGHT(amount) → Amount
```

Weight calculation:
- Position with cost: `units × cost`
- Position without cost: `units`
- Amount with price: handled at posting level

### VALUE

Convert to market value using price database.

```sql
VALUE(position) → Amount
VALUE(position, currency) → Amount
VALUE(inventory) → Amount
VALUE(inventory, currency) → Amount
```

Uses most recent price as of transaction date.

**Examples:**
```sql
SELECT VALUE(position, "USD")           -- Convert to USD
SELECT VALUE(position)                  -- Use default operating currency
```

### GETITEM / GET

Extract amount for specific currency from inventory.

```sql
GETITEM(inventory, currency) → Amount
GET(inventory, currency) → Amount
```

Returns NULL if currency not in inventory.

### GETPRICE

Look up price from price database.

```sql
GETPRICE(base, quote) → Decimal
GETPRICE(base, quote, date) → Decimal
```

Returns NULL if no price found.

## Date Functions

### YEAR

Extract year from date.

```sql
YEAR(date) → Integer
```

**Example:**
```sql
SELECT YEAR(date)                       -- 2024
```

### MONTH

Extract month from date (1-12).

```sql
MONTH(date) → Integer
```

### DAY

Extract day of month from date (1-31).

```sql
DAY(date) → Integer
```

### QUARTER

Extract quarter from date.

```sql
QUARTER(date) → String
```

Returns format like "2024-Q1" (year and quarter).

### WEEKDAY

Extract day of week as abbreviated name.

```sql
WEEKDAY(date) → String
```

Returns "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", or "Sun".

## String Functions

### LENGTH

Get string length.

```sql
LENGTH(string) → Integer
LENGTH(set) → Integer
```

For sets (tags, links), returns number of elements.

### UPPER

Convert to uppercase.

```sql
UPPER(string) → String
```

### LOWER

Convert to lowercase.

```sql
LOWER(string) → String
```

### SUBSTR / SUBSTRING

Extract substring.

```sql
SUBSTR(string, start) → String
SUBSTR(string, start, length) → String
```

0-indexed start position.

## Account Functions

### PARENT

Get parent account (remove last component).

```sql
PARENT(account) → String
```

**Example:**
```sql
PARENT("Assets:Bank:Checking")          -- "Assets:Bank"
```

### LEAF

Get last account component.

```sql
LEAF(account) → String
```

**Example:**
```sql
LEAF("Assets:Bank:Checking")            -- "Checking"
```

### ROOT

Get first N components of account.

```sql
ROOT(account, n) → String
```

**Example:**
```sql
ROOT("Assets:Bank:Checking", 2)         -- "Assets:Bank"
```

## Aggregate Functions

### COUNT

Count rows or non-NULL values.

```sql
COUNT(*) → Integer
COUNT(expr) → Integer
```

### SUM

Sum values (works with amounts, positions, inventories).

```sql
SUM(amount) → Amount
SUM(position) → Inventory
SUM(number) → Decimal
```

**Example:**
```sql
SELECT account, SUM(position)
GROUP BY account;
```

### MIN / MAX

Minimum or maximum value.

```sql
MIN(expr) → same type
MAX(expr) → same type
```

Works with numbers, dates, strings.

### FIRST / LAST

First or last value in group (by sort order).

```sql
FIRST(expr) → same type
LAST(expr) → same type
```

Useful with ORDER BY:
```sql
SELECT account, FIRST(date), LAST(date)
GROUP BY account
ORDER BY date;
```

## Inventory Functions

### EMPTY

Check if inventory is empty.

```sql
EMPTY(inventory) → Boolean
```

Returns TRUE for NULL inventories.

### FILTER_CURRENCY

Filter inventory to single currency.

```sql
FILTER_CURRENCY(inventory, currency) → Inventory
```

**Example:**
```sql
FILTER_CURRENCY(balance, "USD")         -- Only USD positions
```

### POSSIGN

Adjust sign based on account type (debit-normal vs credit-normal).

```sql
POSSIGN(amount, account) → Amount
```

Credit-normal accounts (Liabilities, Equity, Income) have signs inverted.

**Example:**
```sql
SELECT POSSIGN(units, account)          -- Positive for debit-normal
```

## Type Conversion

### COALESCE

Return first non-NULL argument.

```sql
COALESCE(expr1, expr2, ...) → same type
```

**Example:**
```sql
COALESCE(payee, "Unknown")

```

### ABS

Absolute value.

```sql
ABS(number) → Decimal
ABS(amount) → Amount
```

## Metadata Access

### META

Access metadata value by key.

```sql
META(key) → MetaValue
```

**Example:**
```sql
SELECT META("category")
WHERE META("reviewed") = TRUE;
```

## Special Functions

### ENTRY_META

Access transaction-level metadata (from posting context).

```sql
ENTRY_META(key) → MetaValue
```

### ANY_META

Check if any metadata key matches pattern.

```sql
ANY_META(pattern) → Boolean
```
