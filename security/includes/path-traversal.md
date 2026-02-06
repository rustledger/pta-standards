# Path Traversal Prevention

## Overview

Implementations MUST prevent `include` directives from accessing files outside the intended directory tree.

## The Threat

```beancount
; Malicious include attempts
include "../../../etc/passwd"
include "/etc/shadow"
include "C:\Windows\System32\config\SAM"
```

## Requirements

### Path Resolution

Implementations MUST:

1. **Resolve paths** to absolute form before access
2. **Verify containment** within allowed directory
3. **Reject escaping paths** with clear error message

### Allowed Directories

By default, includes are allowed within:
- Directory containing the main ledger file
- Subdirectories thereof

### Blocked Patterns

| Pattern | Example | Action |
|---------|---------|--------|
| Parent traversal | `../secret.beancount` | REJECT |
| Absolute path | `/etc/passwd` | REJECT (unless in allowed) |
| Null bytes | `file\x00.txt` | REJECT |
| URL schemes | `file:///etc/passwd` | REJECT |

## Implementation

### Algorithm

```python
def is_safe_include(base_dir: Path, include_path: str) -> bool:
    # 1. Reject null bytes
    if '\x00' in include_path:
        return False

    # 2. Resolve to absolute path
    if os.path.isabs(include_path):
        resolved = Path(include_path).resolve()
    else:
        resolved = (base_dir / include_path).resolve()

    # 3. Check containment
    try:
        resolved.relative_to(base_dir.resolve())
        return True
    except ValueError:
        return False
```

### Platform Considerations

| Platform | Path Separator | Case Sensitive |
|----------|----------------|----------------|
| Linux | `/` | Yes |
| macOS | `/` | No (usually) |
| Windows | `\` or `/` | No |

Implementations MUST normalize paths for the platform.

## Configuration

Optional: Allow additional include directories:

```beancount
option "include_paths" "/shared/ledgers:/home/user/includes"
```

Or command-line:

```bash
beancount --include-path=/shared/ledgers ledger.beancount
```

## Error Messages

```
error: Path traversal blocked
  --> main.beancount:5:1
  |
5 | include "../../../etc/passwd"
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ path escapes allowed directory
  |
  = resolved: /etc/passwd
  = allowed: /home/user/ledgers/**
```

## Test Vectors

### Must Reject

```
include "../secret.beancount"
include "../../etc/passwd"
include "/etc/passwd"
include "subdir/../../secret.beancount"
include "subdir/../../../etc/passwd"
```

### Must Accept

```
include "accounts.beancount"
include "subdir/file.beancount"
include "./accounts.beancount"
include "subdir/../accounts.beancount"  ; Resolves within allowed
```

## Security Modes

| Mode | Behavior |
|------|----------|
| **Strict** (default) | Only subdirectories of main file |
| **Permissive** | Allow configured paths |
| **Disabled** | No path checking (DANGEROUS) |

Implementations SHOULD default to strict mode.
