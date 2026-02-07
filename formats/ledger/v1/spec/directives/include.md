# Include Directive

The `include` directive imports another ledger file.

## Syntax

```
include PATH
```

## Examples

### Basic Include

```ledger
include accounts.ledger
```

### Relative Path

```ledger
include ./2024/january.ledger
include ../shared/commodities.ledger
```

### Absolute Path

```ledger
include /home/user/finances/accounts.ledger
```

### Home Directory

```ledger
include ~/finances/accounts.ledger
```

### Glob Patterns

```ledger
include 2024/*.ledger
include transactions/**/*.ledger
```

## Path Resolution

Paths are resolved relative to the including file:

```
finances/
├── main.ledger          # Contains: include accounts/checking.ledger
├── accounts/
│   └── checking.ledger  # Resolved relative to main.ledger
└── 2024/
    └── january.ledger
```

## Glob Patterns

### Single Directory

```ledger
include 2024/*.ledger
```
Matches all `.ledger` files in `2024/` directory.

### Recursive

```ledger
include 2024/**/*.ledger
```
Matches all `.ledger` files in `2024/` and subdirectories.

### Multiple Extensions

```ledger
include data/*.{ledger,dat}
```
Matches both `.ledger` and `.dat` files.

## Include Order

Files are processed in order:

```ledger
; 1. First, account definitions
include accounts.ledger

; 2. Then, commodity formats
include commodities.ledger

; 3. Finally, transactions
include 2024/*.ledger
```

Glob matches are sorted alphabetically.

## Circular Includes

Circular includes are detected and cause an error:

```ledger
; a.ledger
include b.ledger

; b.ledger
include a.ledger  ; ERROR: circular include
```

## File Organization

### By Year

```
finances/
├── main.ledger
├── 2023/
│   ├── q1.ledger
│   ├── q2.ledger
│   ├── q3.ledger
│   └── q4.ledger
└── 2024/
    └── q1.ledger
```

```ledger
; main.ledger
include 2023/*.ledger
include 2024/*.ledger
```

### By Category

```
finances/
├── main.ledger
├── accounts.ledger
├── commodities.ledger
├── income/
│   └── salary.ledger
├── expenses/
│   ├── food.ledger
│   └── housing.ledger
└── investments/
    └── brokerage.ledger
```

### By Purpose

```ledger
; main.ledger

; Configuration
include config/accounts.ledger
include config/commodities.ledger
include config/payees.ledger

; Automated rules
include rules/auto-categorize.ledger

; Transactions
include transactions/*.ledger
```

## Environment Variables

Environment variables can be used:

```ledger
include $LEDGER_HOME/accounts.ledger
include ${HOME}/finances/main.ledger
```

## Conditional Include

Using Ledger's value expressions:

```ledger
; Include based on conditions (advanced)
include =(format "%s/%s.ledger" (year today) (month today))
```

## Error Handling

### Missing File

```ledger
include missing.ledger  ; ERROR: file not found
```

### Permission Denied

```ledger
include /root/secret.ledger  ; ERROR: permission denied
```

## Command Line Include

Include from command line:

```bash
ledger -f main.ledger -f extra.ledger balance
```

## Best Practices

1. **Use relative paths** for portability
2. **Include configuration first** (accounts, commodities)
3. **Use glob patterns** for transaction files
4. **Organize by date** for large journals
5. **Keep includes at top** of main file

## Example Structure

```ledger
; main.ledger - Entry point

; === Configuration ===
include config/accounts.ledger
include config/commodities.ledger
include config/payees.ledger

; === Recurring/Automated ===
include rules/auto-postings.ledger

; === Historical Data ===
include archive/2022/*.ledger
include archive/2023/*.ledger

; === Current Year ===
include 2024/*.ledger
```

## See Also

- [Syntax Overview](../syntax.md)
- [File Organization Best Practices](../../README.md)
