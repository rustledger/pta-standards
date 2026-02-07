# hledger Include Specification

This document specifies file inclusion in hledger.

## Overview

The `include` directive incorporates external files:
- Modular organization
- Shared configuration
- Multi-year journals

## Syntax

```hledger
include PATH
```

## Basic Include

### Relative Path

```hledger
include accounts.journal
include 2024/january.journal
include ../shared/commodities.journal
```

### Absolute Path

```hledger
include /home/user/accounting/main.journal
```

### Glob Patterns

```hledger
include 2024/*.journal
include transactions/**/*.journal
```

## Path Resolution

Relative paths resolve from the including file's directory:

```
accounting/
├── main.journal
├── config/
│   └── accounts.journal
└── 2024/
    └── january.journal
```

In `main.journal`:
```hledger
include config/accounts.journal
include 2024/january.journal
```

## Include Order

Files are processed in order:

```hledger
include accounts.journal      ; First
include commodities.journal   ; Second
include 2024/january.journal  ; Third
```

## Circular Include Prevention

hledger detects and rejects cycles:

```hledger
; a.journal
include b.journal

; b.journal
include a.journal  ; ERROR: cycle detected
```

## Common Patterns

### By Year

```hledger
; main.journal
include accounts.journal
include 2023/main.journal
include 2024/main.journal
```

### By Category

```hledger
include config/accounts.journal
include config/commodities.journal
include income/*.journal
include expenses/*.journal
```

### Shared Configuration

```hledger
; personal/main.journal
include ../shared/accounts.journal
include 2024.journal
```

## Environment Variables

```hledger
include $LEDGER_FILE
include ${HOME}/accounting/main.journal
```

## Error Handling

### File Not Found

```
hledger: error: could not read include file
  include missing.journal
  File does not exist
```

### Permission Denied

```
hledger: error: could not read include file
  include /secret/file.journal
  Permission denied
```

## Examples

### Minimal Setup

```hledger
; main.journal
include accounts.journal

2024-01-15 Opening
    assets:checking    $1000
    equity:opening
```

### Full Organization

```hledger
; main.journal

; Configuration
include config/accounts.journal
include config/commodities.journal
include config/payees.journal

; Data by year
include 2023/main.journal
include 2024/main.journal

; Automation
include rules/auto.journal
```

### Monthly Files

```hledger
; 2024/main.journal
include 01-january.journal
include 02-february.journal
include 03-march.journal
; ...
include 12-december.journal
```

## Best Practices

1. **Single entry point** - One main.journal
2. **Logical grouping** - By year, category, or account
3. **Number prefixes** - For ordering (01-, 02-)
4. **Separate config** - Accounts/commodities in config/
5. **Avoid deep nesting** - Keep simple
6. **Document structure** - Comments explaining layout

## See Also

- [Syntax Specification](syntax.md)
- [Account Directive](directives/account.md)
