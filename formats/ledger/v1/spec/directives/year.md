# Year Directive

The `Y` or `year` directive sets the default year for dates.

## Syntax

```
Y YEAR
year YEAR
```

## Examples

### Basic Usage

```ledger
Y 2024

01/15 Grocery Store
    Expenses:Food    $50.00
    Assets:Checking

02/01 Rent
    Expenses:Housing    $1500.00
    Assets:Checking
```

Dates are interpreted as 2024/01/15 and 2024/02/01.

### Explicit Year

```ledger
year 2024

; These are equivalent:
01/15 Transaction A
    Expenses:A    $50
    Assets:Checking

2024/01/15 Transaction B
    Expenses:B    $50
    Assets:Checking
```

## Scope

The year directive affects all subsequent dates:

```ledger
Y 2023

12/15 December 2023
    Expenses:A    $50
    Assets:Checking

Y 2024

01/15 January 2024
    Expenses:B    $50
    Assets:Checking
```

## Use Cases

### Annual Files

When organizing by year:

```ledger
; File: 2024.ledger

Y 2024

01/01 New Year
    Expenses:Entertainment    $100
    Assets:Checking

01/15 Groceries
    Expenses:Food    $75
    Assets:Checking

; ... rest of year
```

### Import Processing

When importing bank data:

```ledger
; Imported from bank CSV
Y 2024

01/02 WHOLEFDS #1234
    Expenses:Food    $87.50
    Assets:Checking

01/03 SHELL OIL
    Expenses:Gas    $45.00
    Assets:Checking
```

## Date Format with Default Year

### Two-digit Dates

```ledger
Y 2024

01/15 Transaction    ; Becomes 2024/01/15
    Expenses:A    $50
    Assets:Checking
```

### Full Dates Override

```ledger
Y 2024

01/15 Uses default year
    Expenses:A    $50
    Assets:Checking

2023/12/31 Overrides default
    Expenses:B    $25
    Assets:Checking
```

## Month/Day Format

With default year, you can use:

```ledger
Y 2024

1/5 Single digits
    Expenses:A    $10
    Assets:Checking

01/05 Leading zeros
    Expenses:B    $20
    Assets:Checking

Jan 5 Month name
    Expenses:C    $30
    Assets:Checking
```

## Changing Years

```ledger
Y 2023

12/15 Late 2023
    Expenses:A    $50
    Assets:Checking

12/31 Year end
    Expenses:B    $25
    Assets:Checking

Y 2024

01/01 New year
    Expenses:C    $100
    Assets:Checking
```

## Without Year Directive

Without a default year, full dates are required:

```ledger
2024/01/15 Full date required
    Expenses:A    $50
    Assets:Checking

01/15 Error - no year specified
    Expenses:B    $50
    Assets:Checking
```

## Multiple Year Files

### Main File

```ledger
; main.ledger
include 2023.ledger
include 2024.ledger
```

### Year Files

```ledger
; 2023.ledger
Y 2023
include 2023/*.ledger
```

```ledger
; 2024.ledger
Y 2024
include 2024/*.ledger
```

## Best Practices

1. **Set year at file start** for clarity
2. **One year per file** when organizing by year
3. **Use full dates** for cross-year references
4. **Reset year** when including files
5. **Document year changes** with comments

## Example: Year-Based Organization

```ledger
; 2024.ledger

Y 2024

; January
01/01 New Year celebration
    Expenses:Entertainment    $150.00
    Assets:Checking

01/15 Groceries
    Expenses:Food    $200.00
    Assets:Checking

01/31 Rent
    Expenses:Housing    $1500.00
    Assets:Checking

; February
02/01 Gym membership
    Expenses:Health    $50.00
    Assets:Checking

02/14 Valentine's dinner
    Expenses:Food:Dining    $100.00
    Assets:Checking

; ... continues through year
```

## Interaction with Include

Year directive scope includes included files:

```ledger
Y 2024

include january.ledger
; january.ledger uses 2024 as default year

Y 2025

include january-next.ledger
; january-next.ledger uses 2025
```

## See Also

- [Syntax Specification](../syntax.md)
- [Include Directive](include.md)
