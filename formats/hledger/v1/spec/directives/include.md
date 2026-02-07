# Include Directive

The `include` directive imports entries from another file.

## Syntax

```hledger
include PATH
```

## Basic Usage

```hledger
include accounts.journal
include transactions/2024.journal
include prices.journal
```

## Path Resolution

### Relative Paths

Relative to the including file:

```hledger
; In /home/user/finances/main.journal
include accounts.journal      ; /home/user/finances/accounts.journal
include 2024/january.journal  ; /home/user/finances/2024/january.journal
include ../shared/prices.journal  ; /home/user/shared/prices.journal
```

### Absolute Paths

```hledger
include /home/user/finances/accounts.journal
include ~/finances/accounts.journal
```

### Home Directory Expansion

```hledger
include ~/finances/main.journal
; Expands to /home/user/finances/main.journal
```

## Glob Patterns

Include multiple files with wildcards:

```hledger
include 2024/*.journal
include transactions/**/*.journal
include accounts-*.journal
```

### Pattern Syntax

| Pattern | Matches |
|---------|---------|
| `*` | Any characters except `/` |
| `**` | Any characters including `/` |
| `?` | Single character |
| `[abc]` | Character class |
| `[!abc]` | Negated character class |

### Examples

```hledger
; All journal files in 2024 directory
include 2024/*.journal

; All journal files recursively
include **/*.journal

; January through March
include 2024/0[123]-*.journal

; Everything except prices
include !prices.journal
include *.journal
```

## Processing Order

Included files are processed in order of inclusion:

```hledger
; main.journal
include accounts.journal    ; Processed first
include prices.journal      ; Processed second
include transactions.journal ; Processed third
```

For glob patterns, files are sorted alphabetically.

## Nested Includes

Included files can include other files:

```hledger
; main.journal
include config.journal

; config.journal
include accounts.journal
include commodities.journal
```

## Cycle Detection

Circular includes are detected and prevented:

```hledger
; a.journal
include b.journal

; b.journal
include a.journal  ; Error: circular include detected
```

## Use Cases

### Yearly Organization

```hledger
; main.journal
include accounts.journal
include commodities.journal
include prices.journal

; Transaction files by year
include 2022.journal
include 2023.journal
include 2024.journal
```

### Monthly Organization

```hledger
; 2024.journal
include 2024/01-january.journal
include 2024/02-february.journal
include 2024/03-march.journal
; ... etc
```

### Category Organization

```hledger
; main.journal
include config/accounts.journal
include config/commodities.journal
include transactions/personal.journal
include transactions/business.journal
include transactions/investments.journal
```

### Shared Configuration

```hledger
; personal.journal
include ~/shared/accounts.journal
include ~/shared/prices.journal

; All files share common configuration
```

## File Not Found

Missing files cause an error:

```
hledger: Error reading included file
  include missing.journal
  File not found: missing.journal
```

## Optional Includes

Not directly supported. Use glob patterns for optional files:

```hledger
; Include if exists (no error if missing)
include local-*.journal
```

## Security Considerations

1. **Path traversal**: Be careful with `..` in paths
2. **Symlinks**: May be followed (implementation dependent)
3. **Permissions**: Must have read access to included files

## Performance

For large ledgers:
- Many small files: More overhead per file
- Fewer large files: Less overhead but harder to edit
- Use glob patterns to avoid listing each file

## Complete Example

```hledger
; ===== ~/finances/main.journal =====

; Configuration (order matters)
include config/accounts.journal
include config/commodities.journal
include config/payees.journal

; Current price database
include prices/current.journal

; Historical transactions by year
include years/2022.journal
include years/2023.journal

; Current year transactions by month
include 2024/**.journal

; ===== ~/finances/2024/01-january.journal =====
; January 2024 transactions

2024-01-01 Opening balance
    Assets:Checking    $5000
    Equity:Opening

2024-01-15 Salary
    Assets:Checking    $3500
    Income:Salary
```

## Command Line

```bash
# Specify main file
hledger -f main.journal bal

# Include multiple explicit files
hledger -f a.journal -f b.journal bal
```

## See Also

- [Account Directive](account.md)
- [Commodity Directive](commodity.md)
