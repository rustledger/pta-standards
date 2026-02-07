# Include Processing

## Overview

This document describes the semantics of file inclusion: how included files are resolved, merged, and how options and directives interact across file boundaries.

## Include Directive

```beancount
include "path/to/file.beancount"
```

See [directives/include.md](directives/include.md) for syntax details.

## Processing Model

### Phase 1: Parse

1. Parse the main file
2. Collect all `include` directives
3. Recursively parse each included file
4. Detect and reject cycles

### Phase 2: Merge

1. Combine all directives from all files
2. Apply tag/metadata stacks per-file
3. Preserve source location metadata

### Phase 3: Sort

1. Sort directives chronologically by date
2. Within same date, apply stable ordering rules
3. Undated directives (options, plugins) maintain file order

### Phase 4: Process

1. Apply plugins in declaration order
2. Execute validation
3. Generate output

## File Resolution

### Relative Paths

Relative paths resolve from the **including file's directory**:

```
/home/user/finances/
├── main.beancount          ; include "yearly/2024.beancount"
└── yearly/
    ├── 2024.beancount      ; include "q1.beancount"
    └── q1.beancount
```

Resolution:
- `main.beancount` includes `yearly/2024.beancount` → `/home/user/finances/yearly/2024.beancount`
- `2024.beancount` includes `q1.beancount` → `/home/user/finances/yearly/q1.beancount`

### Absolute Paths

Absolute paths are used as-is:

```beancount
include "/shared/common/accounts.beancount"
```

### Path Normalization

Before resolution:
1. Expand `~` to home directory (platform-specific)
2. Normalize `.` and `..` components
3. Convert separators to platform native

## Cycle Detection

Circular includes MUST be detected and rejected:

```
a.beancount → b.beancount → c.beancount → a.beancount
```

### Detection Algorithm

```python
def load_file(path, include_chain=None):
    if include_chain is None:
        include_chain = set()

    resolved = path.resolve()

    if resolved in include_chain:
        raise CycleError(f"Circular include: {format_chain(include_chain, resolved)}")

    include_chain.add(resolved)

    content = parse(resolved)
    for include in content.includes:
        load_file(include.path, include_chain.copy())

    include_chain.remove(resolved)
    return content
```

### Cycle Error

```
error: Circular include detected
  --> c.beancount:5:1
  |
5 | include "a.beancount"
  | ^^^^^^^^^^^^^^^^^^^^^ creates cycle
  |
  = chain: a.beancount → b.beancount → c.beancount → a.beancount
```

## Option Scoping

### Top-Level Options Win

Most options from included files are ignored - only the **main file** (entry point) values apply:

```beancount
; main.beancount
option "title" "Main Ledger"
include "other.beancount"

; other.beancount
option "title" "Other Ledger"      ; Ignored - main file's value used
```

Result: title = "Main Ledger"

### Rationale

This prevents included files from unexpectedly changing global behavior.

### Exception: Additive Options

The `operating_currency` option is additive across files - values from all files accumulate:

```beancount
; main.beancount
option "operating_currency" "USD"
include "other.beancount"

; other.beancount
option "operating_currency" "EUR"  ; Added to list (NOT ignored!)
```

Result: operating_currency = ["USD", "EUR"]

## Plugin Scoping

### Declaration Order

Plugins are loaded in declaration order across all files:

```beancount
; main.beancount
plugin "plugin_a"
include "other.beancount"
plugin "plugin_c"

; other.beancount
plugin "plugin_b"
```

Load order: plugin_a → plugin_b → plugin_c

### Plugin Application

Plugins see the merged directive stream:

```python
# All directives from all files, sorted by date
all_directives = merge_and_sort(main_file, included_files)

# Plugins process the complete stream
for plugin in plugins:
    all_directives = plugin.process(all_directives)
```

## Tag and Metadata Stacks

### Per-File Scoping

Tag and metadata stacks are scoped to their file:

```beancount
; main.beancount
pushtag #main-tag
include "other.beancount"
2024-01-15 * "In main"        ; Has #main-tag
  ...
poptag #main-tag

; other.beancount
pushtag #other-tag
2024-01-10 * "In other"       ; Has #other-tag, NOT #main-tag
  ...
poptag #other-tag
```

### Cross-File Inheritance

The stack does NOT propagate into included files.

### Stack Balance

Each file MUST balance its own stack:

```beancount
; ERROR: Unbalanced stack
pushtag #tag
include "other.beancount"
; Missing poptag!
```

## Directive Merging

### Date-Based Sorting

All directives are sorted by date after merging:

```beancount
; main.beancount (loaded first)
2024-02-01 * "February entry"
  ...

; other.beancount (included)
2024-01-15 * "January entry"
  ...
```

After merge and sort:
1. 2024-01-15: "January entry" (from other.beancount)
2. 2024-02-01: "February entry" (from main.beancount)

### Same-Date Ordering

Directives on the same date are ordered:

1. Balance assertions
2. Other non-transaction directives
3. Transactions

Within category, file order then line order is preserved.

## Source Location

### Metadata Injection

Each directive receives source location:

```python
directive.meta['filename'] = '/path/to/file.beancount'
directive.meta['lineno'] = 42
```

### Error Reporting

Errors reference the original file:

```
error: Account not opened
  --> yearly/q1.beancount:15:3
   |
15 |   Assets:Unknown  100 USD
   |   ^^^^^^^^^^^^^^
```

## Diamond Includes

### Handling

The same file included from multiple paths is loaded once:

```
main.beancount
├── a.beancount → common.beancount
└── b.beancount → common.beancount
```

`common.beancount` is parsed once; its directives appear once.

### Implementation

Track loaded files by canonical path:

```python
loaded_files = set()

def load_file(path):
    canonical = path.resolve()
    if canonical in loaded_files:
        return []  # Already loaded
    loaded_files.add(canonical)
    return parse(canonical)
```

## Security

### Path Traversal

See [security/includes/path-traversal.md](../../../../security/includes/path-traversal.md).

### Symlinks

See [security/includes/symlinks.md](../../../../security/includes/symlinks.md).

### Cycles

See [security/includes/cycles.md](../../../../security/includes/cycles.md).

## Implementation Notes

1. Resolve paths relative to including file
2. Canonicalize paths for cycle/diamond detection
3. Track include chain for error messages
4. Merge directives before sorting
5. Apply options from main file only
6. Process plugins after merge
7. Preserve source locations for errors
