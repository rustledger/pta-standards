# CSV Rules Specification

CSV rules files define how to import CSV bank statements into hledger format.

## Overview

A rules file maps CSV columns to hledger transaction fields:

```csv-rules
skip 1
fields date, description, amount
account1 Assets:Checking
```

## File Extension

- `.rules`
- `.csv.rules`

## Basic Structure

```csv-rules
# Comments start with #

# Skip header row(s)
skip 1

# Define field mappings
fields date, description, amount

# Set the main account
account1 Assets:Checking

# Set default expense account
account2 Expenses:Uncategorized
```

## Field Mappings

### Fields Directive

Map CSV columns to transaction fields:

```csv-rules
fields date, , description, amount, balance
```

Empty fields (double comma) skip that column.

### Available Fields

| Field | Description |
|-------|-------------|
| `date` | Transaction date |
| `date2` | Secondary date |
| `status` | Status marker |
| `code` | Transaction code |
| `description` | Transaction description |
| `comment` | Transaction comment |
| `account1` | First posting account |
| `account2` | Second posting account |
| `amount` | Transaction amount |
| `amount-in` | Positive amount |
| `amount-out` | Negative amount |
| `balance` | Balance for assertion |
| `currency` | Amount commodity |

## Skip Directive

Skip header rows:

```csv-rules
# Skip one header row
skip 1

# Skip multiple rows
skip 3
```

## Account Directives

### Static Accounts

```csv-rules
account1 Assets:Bank:Checking
account2 Expenses:Unknown
```

### Conditional Accounts

```csv-rules
if AMAZON
  account2 Expenses:Shopping

if WHOLE FOODS
  account2 Expenses:Food:Groceries
```

## If/Rules Conditionals

### Pattern Matching

```csv-rules
if PATTERN
  FIELD VALUE
```

### Examples

```csv-rules
# Match description containing "AMAZON"
if AMAZON
  account2 Expenses:Shopping

# Match description containing "PAYROLL"
if PAYROLL
  account2 Income:Salary

# Match description containing "TRANSFER"
if TRANSFER
  account2 Assets:Savings
```

### Regex Patterns

```csv-rules
if %description AMAZON|AMZN
  account2 Expenses:Shopping

if %description ^PAYROLL
  account2 Income:Salary
```

### Multiple Patterns

```csv-rules
if
AMAZON
AMZN
  account2 Expenses:Shopping
```

## Amount Handling

### Single Amount Column

```csv-rules
fields date, description, amount
# Positive = inflow, negative = outflow
```

### Separate In/Out Columns

```csv-rules
fields date, description, amount-in, amount-out
# amount-in for deposits, amount-out for withdrawals
```

### Currency Column

```csv-rules
fields date, description, amount, currency
# Uses currency column for commodity
```

### Fixed Currency

```csv-rules
fields date, description, amount
currency $
```

## Date Formats

### Date Format Directive

```csv-rules
date-format %m/%d/%Y
# Matches: 01/15/2024

date-format %d-%b-%Y
# Matches: 15-Jan-2024

date-format %Y%m%d
# Matches: 20240115
```

### Common Formats

| Format | Example |
|--------|---------|
| `%Y-%m-%d` | 2024-01-15 |
| `%m/%d/%Y` | 01/15/2024 |
| `%d/%m/%Y` | 15/01/2024 |
| `%Y%m%d` | 20240115 |
| `%d-%b-%Y` | 15-Jan-2024 |

## Balance Assertions

```csv-rules
fields date, description, amount, balance
balance-type =
```

Generates postings with balance assertions:

```hledger
2024-01-15 Transaction
    Assets:Checking    $100 = $1500
    Expenses:Unknown
```

## Status Markers

```csv-rules
# Set all as cleared
status *

# Conditional status
if PENDING
  status !
```

## Description Formatting

```csv-rules
# Use raw description
description %description

# Combine fields
description %description | %reference

# Clean up description
description %description
  & /^CHECKCARD /
  & / *$/
```

## Complete Example

```csv-rules
# ===== Bank CSV Rules =====

# Skip header row
skip 1

# CSV columns: Date, Reference, Description, Amount, Balance
fields date, code, description, amount, balance

# Date format: MM/DD/YYYY
date-format %m/%d/%Y

# Currency
currency $

# Main account
account1 Assets:Bank:Checking

# Default expense account
account2 Expenses:Uncategorized

# Balance assertions
balance-type =

# All imported as cleared
status *

# ===== Category Rules =====

# Income
if PAYROLL|DIRECT DEP
  account2 Income:Salary

if INTEREST
  account2 Income:Interest

# Transfers
if TRANSFER TO SAVINGS
  account2 Assets:Bank:Savings

if TRANSFER FROM SAVINGS
  account2 Assets:Bank:Savings

# Bills
if ELECTRIC|PG&E|UTILITY
  account2 Expenses:Utilities:Electric

if WATER|SEWER
  account2 Expenses:Utilities:Water

if INTERNET|COMCAST|AT&T
  account2 Expenses:Utilities:Internet

# Shopping
if AMAZON|AMZN
  account2 Expenses:Shopping:Online

if TARGET|WALMART|COSTCO
  account2 Expenses:Shopping:Retail

# Food
if WHOLE FOODS|TRADER JOE|SAFEWAY|GROCERY
  account2 Expenses:Food:Groceries

if DOORDASH|GRUBHUB|UBER EATS
  account2 Expenses:Food:Delivery

if STARBUCKS|DUNKIN|COFFEE
  account2 Expenses:Food:Coffee

# Transportation
if SHELL|CHEVRON|76|GAS
  account2 Expenses:Transportation:Gas

if UBER|LYFT
  account2 Expenses:Transportation:Rideshare

# Entertainment
if NETFLIX|HULU|SPOTIFY|DISNEY
  account2 Expenses:Entertainment:Streaming

if MOVIE|THEATER|AMC
  account2 Expenses:Entertainment:Movies

# Medical
if PHARMACY|CVS|WALGREENS
  account2 Expenses:Medical:Pharmacy

if DOCTOR|MEDICAL|HOSPITAL
  account2 Expenses:Medical:Provider
```

## Command Usage

```bash
# Import CSV with rules
hledger -f bank.csv --rules-file bank.rules print

# Import directly
hledger import bank.csv --rules-file bank.rules

# Add to existing journal
hledger import bank.csv --rules-file bank.rules >> journal.hledger
```

## Multiple CSV Formats

Create separate rules for each bank/format:

```
rules/
├── chase-checking.rules
├── chase-credit.rules
├── bofa-savings.rules
└── fidelity-brokerage.rules
```

## Best Practices

1. **Start with common patterns** and add specific ones
2. **Test rules** with `--dry-run` before importing
3. **Review imported transactions** for accuracy
4. **Refine rules** as new transaction types appear
5. **Keep rules files** in version control

## See Also

- [hledger Import Documentation](https://hledger.org/import.html)
- [CSV Format Reference](https://hledger.org/csv.html)
