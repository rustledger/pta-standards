# Include Directive

## Overview

The `include` directive imports the contents of another file into the current ledger. This enables organizing large ledgers across multiple files.

## Syntax

```ebnf
include = "include" WHITESPACE path

path = string
```

## Components

### Path

A string containing the file path to include:
- Relative paths resolve from the including file's directory
- Absolute paths are used as-is

## Examples

### Basic Include

```beancount
; main.beancount
include "accounts.beancount"
include "2024/january.beancount"
include "2024/february.beancount"
```

### Directory Structure

```
ledger/
├── main.beancount
├── accounts.beancount
├── commodities.beancount
├── 2024/
│   ├── q1.beancount
│   ├── q2.beancount
│   ├── q3.beancount
│   └── q4.beancount
└── config/
    └── options.beancount
```

```beancount
; main.beancount
include "config/options.beancount"
include "accounts.beancount"
include "commodities.beancount"
include "2024/q1.beancount"
include "2024/q2.beancount"
include "2024/q3.beancount"
include "2024/q4.beancount"
```

### Nested Includes

```beancount
; main.beancount
include "2024/all.beancount"

; 2024/all.beancount
include "q1.beancount"
include "q2.beancount"
include "q3.beancount"
include "q4.beancount"
```

## Path Resolution

### Relative Paths

Relative paths resolve from the **including file's directory**:

```
/home/user/finances/
├── main.beancount           ; include "yearly/2024.beancount"
└── yearly/
    └── 2024.beancount       ; include "q1.beancount"
    └── q1.beancount
```

In `main.beancount`:
```beancount
include "yearly/2024.beancount"  ; → /home/user/finances/yearly/2024.beancount
```

In `yearly/2024.beancount`:
```beancount
include "q1.beancount"  ; → /home/user/finances/yearly/q1.beancount
```

### Absolute Paths

```beancount
include "/shared/ledgers/common/accounts.beancount"
```

### Path Normalization

Paths are normalized before resolution:
- `./file.beancount` → `file.beancount`
- `dir/../file.beancount` → `file.beancount`

## Include Behavior

### Merging

Included files are merged into the main file:

1. All directives are combined
2. Directives are sorted chronologically
3. Options from the main file take precedence

### Processing Order

1. Parse main file
2. For each `include`, recursively parse included file
3. Merge all directives
4. Sort by date
5. Apply plugins

## Validation

| Error | Condition |
|-------|-----------|
| E9001 | Include file not found |
| E9002 | Circular include detected |

### File Not Found

```
error: Include file not found
  --> main.beancount:5:1
   |
 5 | include "missing.beancount"
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^ file does not exist
   |
   = path: /home/user/finances/missing.beancount
```

### Circular Include

```
error: Circular include detected
  --> b.beancount:3:1
   |
 3 | include "a.beancount"
   | ^^^^^^^^^^^^^^^^^^^^^ creates cycle
   |
   = cycle: a.beancount → b.beancount → a.beancount
```

## Option Scoping

Options are scoped to the top-level file:

```beancount
; main.beancount
option "title" "Main Ledger"
include "other.beancount"
; Title is "Main Ledger"

; other.beancount
option "title" "Other Ledger"  ; Ignored for final ledger
```

Only options from the main file apply to the final result.

## Security

### Path Traversal Prevention

Include paths MUST NOT escape the allowed directory:

```beancount
; REJECTED: Escapes ledger directory
include "../../../etc/passwd"
include "/etc/passwd"
```

See [security/includes/path-traversal.md](../../../../../security/includes/path-traversal.md).

### Symlink Handling

By default, symlinks are not followed:

```beancount
option "follow_symlinks" "false"  ; Default

; If data.beancount is a symlink, this fails
include "data.beancount"
```

See [security/includes/symlinks.md](../../../../../security/includes/symlinks.md).

## Best Practices

### File Organization

```
ledger/
├── main.beancount          ; Entry point, includes everything
├── accounts.beancount      ; Account definitions (open/close)
├── commodities.beancount   ; Commodity declarations
├── prices.beancount        ; Historical prices
├── config/
│   └── options.beancount   ; Options and plugins
└── transactions/
    ├── 2024/
    │   ├── 01-january.beancount
    │   ├── 02-february.beancount
    │   └── ...
    └── 2023/
        └── ...
```

### Main File Structure

```beancount
; main.beancount
;
; Personal Finance Ledger
; =======================

; Configuration
include "config/options.beancount"

; Account structure
include "accounts.beancount"
include "commodities.beancount"

; Historical prices
include "prices.beancount"

; Transactions by year
include "transactions/2023/all.beancount"
include "transactions/2024/all.beancount"
```

### Year File

```beancount
; transactions/2024/all.beancount
include "01-january.beancount"
include "02-february.beancount"
include "03-march.beancount"
include "04-april.beancount"
include "05-may.beancount"
include "06-june.beancount"
include "07-july.beancount"
include "08-august.beancount"
include "09-september.beancount"
include "10-october.beancount"
include "11-november.beancount"
include "12-december.beancount"
```

## Glob Patterns

Standard Beancount does NOT support glob patterns:

```beancount
; NOT SUPPORTED in standard Beancount
include "2024/*.beancount"
```

Some implementations may support globs as an extension.

## Conditional Includes

Not directly supported. Use plugins or external tools for conditional logic:

```beancount
; Standard approach: include everything
include "production.beancount"
include "development.beancount"

; Plugin filters based on option
option "environment" "production"
```

## Implementation Notes

1. Resolve paths relative to including file
2. Track include chain for cycle detection
3. Normalize paths before checking cycles
4. Apply security checks (path traversal, symlinks)
5. Merge directives after all includes processed
6. Report errors with full include chain context
