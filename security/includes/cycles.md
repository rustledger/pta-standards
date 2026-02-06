# Include Cycle Detection

## Overview

Implementations MUST detect and reject circular include chains.

## The Threat

```
a.beancount:  include "b.beancount"
b.beancount:  include "c.beancount"
c.beancount:  include "a.beancount"  ; Cycle!
```

Without detection, this causes:
- Infinite loops
- Stack overflow
- Memory exhaustion

## Requirements

### Detection

Implementations MUST:

1. Track all files in the current include chain
2. Detect when a file is included that's already in the chain
3. Report the cycle with the full chain

### Handling

When a cycle is detected:

1. **Stop processing** the cyclic include
2. **Report an error** with the cycle path
3. **Continue processing** other includes (if error recovery enabled)

## Implementation

### Using a Set

```python
def load_file(path: Path, include_chain: set[Path] = None):
    if include_chain is None:
        include_chain = set()

    resolved = path.resolve()

    # Check for cycle
    if resolved in include_chain:
        raise CycleError(include_chain, resolved)

    # Add to chain
    include_chain.add(resolved)

    try:
        content = resolved.read_text()
        for include in parse_includes(content):
            load_file(include, include_chain.copy())
    finally:
        include_chain.remove(resolved)
```

### Using a Stack

```python
def load_file(path: Path, include_stack: list[Path] = None):
    if include_stack is None:
        include_stack = []

    resolved = path.resolve()

    # Check for cycle
    if resolved in include_stack:
        cycle_start = include_stack.index(resolved)
        cycle = include_stack[cycle_start:] + [resolved]
        raise CycleError(cycle)

    include_stack.append(resolved)
    try:
        content = resolved.read_text()
        for include in parse_includes(content):
            load_file(include, include_stack)
    finally:
        include_stack.pop()
```

## Error Messages

```
error: Include cycle detected
  --> c.beancount:3:1
  |
3 | include "a.beancount"
  | ^^^^^^^^^^^^^^^^^^^^^ creates cycle
  |
  = cycle: a.beancount → b.beancount → c.beancount → a.beancount
```

## Edge Cases

### Self-Inclusion

```beancount
; file.beancount
include "file.beancount"  ; Direct self-cycle
```

MUST be detected as a cycle of length 1.

### Diamond Includes (Not a Cycle)

```
main.beancount includes a.beancount and b.beancount
a.beancount includes common.beancount
b.beancount includes common.beancount
```

This is NOT a cycle. `common.beancount` should be loaded once.

### Implementation Note

Track by **canonical path** (resolved, normalized) to detect cycles regardless of how the path is written:

```beancount
include "accounts/../accounts.beancount"  ; Same as accounts.beancount
include "./accounts.beancount"            ; Same file
```

## Test Vectors

### Must Detect

1. Direct self-inclusion
2. Two-file cycle (A→B→A)
3. Three-file cycle (A→B→C→A)
4. Cycle via different path spellings

### Must Allow

1. Diamond pattern (shared include)
2. Same file included from multiple places (once)
