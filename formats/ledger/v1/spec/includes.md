# Include Specification

This document specifies file inclusion in Ledger.

## Overview

The `include` directive incorporates external files into a journal. This enables:
- Modular journal organization
- Separation of concerns
- Shared configuration
- Multi-year accounting

## Syntax

```
include = "include" path

path = relative_path | absolute_path | glob_pattern
```

## Basic Include

### Relative Path

```ledger
include accounts.ledger
include 2024/january.ledger
include ../shared/commodities.ledger
```

Relative paths are resolved from the including file's directory.

### Absolute Path

```ledger
include /home/user/accounting/main.ledger
include C:\Users\Me\Accounting\main.ledger
```

### Glob Patterns

```ledger
include 2024/*.ledger
include transactions/**/*.ledger
```

## Include Order

Includes are processed in order of appearance:

```ledger
; main.ledger

include accounts.ledger      ; First
include commodities.ledger   ; Second
include 2024/january.ledger  ; Third
include 2024/february.ledger ; Fourth
```

## Path Resolution

### Relative to Including File

```
/home/user/accounting/
├── main.ledger
├── config/
│   └── accounts.ledger
└── 2024/
    └── january.ledger
```

In `main.ledger`:
```ledger
include config/accounts.ledger
include 2024/january.ledger
```

In `config/accounts.ledger`:
```ledger
include ../commodities.ledger  ; Goes up to accounting/
```

### Search Path

Ledger can search additional paths:

```bash
ledger -f main.ledger --include /path/to/includes/
```

## Circular Include Prevention

Ledger detects and rejects circular includes:

```ledger
; a.ledger
include b.ledger

; b.ledger
include a.ledger   ; ERROR: Circular include detected
```

Error message:
```
V-009: Circular include detected
  Include cycle: a.ledger -> b.ledger -> a.ledger
```

## Common Organization Patterns

### By Year

```
accounting/
├── main.ledger
├── accounts.ledger
├── 2023/
│   ├── main.ledger
│   ├── january.ledger
│   └── december.ledger
└── 2024/
    ├── main.ledger
    └── january.ledger
```

```ledger
; main.ledger
include accounts.ledger
include 2023/main.ledger
include 2024/main.ledger

; 2024/main.ledger
include january.ledger
; ... more months
```

### By Category

```
accounting/
├── main.ledger
├── config/
│   ├── accounts.ledger
│   ├── commodities.ledger
│   └── payees.ledger
├── income/
│   └── salary.ledger
├── expenses/
│   ├── housing.ledger
│   └── food.ledger
└── assets/
    └── investments.ledger
```

```ledger
; main.ledger
include config/accounts.ledger
include config/commodities.ledger
include config/payees.ledger
include income/*.ledger
include expenses/*.ledger
include assets/*.ledger
```

### By Account

```
accounting/
├── main.ledger
├── checking.ledger
├── savings.ledger
├── credit-card.ledger
└── investments.ledger
```

### Shared Configuration

```
shared/
├── accounts.ledger
└── commodities.ledger

personal/
├── main.ledger
└── 2024.ledger

business/
├── main.ledger
└── 2024.ledger
```

```ledger
; personal/main.ledger
include ../shared/accounts.ledger
include ../shared/commodities.ledger
include 2024.ledger
```

## Include with Globs

### All Files in Directory

```ledger
include 2024/*.ledger
```

### Recursive

```ledger
include transactions/**/*.ledger
```

### Specific Pattern

```ledger
include 2024/q1-*.ledger
```

## Conditional Includes

### Environment Variable

Some implementations support environment-based includes:

```ledger
include ${LEDGER_DIR}/main.ledger
```

### Apply Directive

Limit scope of included directives:

```ledger
apply account Personal
include personal-transactions.ledger
end apply
```

## Error Handling

### File Not Found

```
V-008: Included file not found
  Line 5: include missing.ledger
  File 'missing.ledger' does not exist
```

### Permission Denied

```
Error: Cannot read included file
  Line 5: include /root/secret.ledger
  Permission denied
```

### Invalid Path

```
Error: Invalid include path
  Line 5: include ../../../etc/passwd
  Path escapes allowed directory
```

## Examples

### Minimal Setup

```ledger
; main.ledger
include accounts.ledger

2024/01/15 Opening Balance
    Assets:Checking    $1000
    Equity:Opening
```

### Full Organization

```ledger
; main.ledger - Primary entry point

; ===== Configuration =====
include config/accounts.ledger
include config/commodities.ledger
include config/payees.ledger
include config/tags.ledger

; ===== Prices =====
include prices.ledger

; ===== Transactions by Year =====
include 2023/main.ledger
include 2024/main.ledger

; ===== Automated Transactions =====
include automation/budgets.ledger
include automation/taxes.ledger
```

### Monthly Files

```ledger
; 2024/main.ledger

include 01-january.ledger
include 02-february.ledger
include 03-march.ledger
include 04-april.ledger
include 05-may.ledger
include 06-june.ledger
include 07-july.ledger
include 08-august.ledger
include 09-september.ledger
include 10-october.ledger
include 11-november.ledger
include 12-december.ledger
```

## Best Practices

1. **Single entry point** - Use one main.ledger file
2. **Logical grouping** - Organize by year, category, or account
3. **Prefix with numbers** - For controlled ordering (01-, 02-, etc.)
4. **Shared config** - Keep accounts/commodities in separate files
5. **Avoid deep nesting** - Keep include depth reasonable
6. **Document structure** - Add comments explaining organization
7. **Consistent naming** - Use clear, predictable file names

## See Also

- [Include Directive](directives/include.md)
- [Syntax Specification](syntax.md)
- [Validation: Accounts](validation/accounts.md)
