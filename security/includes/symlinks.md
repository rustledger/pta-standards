# Symbolic Link Handling

## Overview

Implementations SHOULD carefully handle symbolic links in include paths to prevent security bypasses.

## The Threat

Symlinks can bypass path traversal checks:

```bash
# Attacker creates symlink
ln -s /etc/passwd /home/user/ledgers/passwords.beancount
```

```beancount
; Appears to be in allowed directory
include "passwords.beancount"  ; Actually reads /etc/passwd
```

## Threat Scenarios

### 1. Symlink Escape

```
/home/user/ledgers/
├── main.beancount
└── secret -> /etc/passwd
```

### 2. Symlink Race (TOCTOU)

```
1. Check: /home/user/ledgers/file.beancount → valid
2. Attacker: ln -sf /etc/passwd /home/user/ledgers/file.beancount
3. Read: /home/user/ledgers/file.beancount → /etc/passwd
```

### 3. Symlink Chain

```
a -> b -> c -> /etc/passwd
```

## Security Levels

| Level | Symlink Behavior |
|-------|------------------|
| **Strict** | Reject all symlinks |
| **Validated** | Follow, but verify final target is allowed |
| **Permissive** | Follow without checking (DANGEROUS) |

## Requirements

### Strict Mode (Recommended)

Implementations SHOULD offer strict mode:

```python
def is_safe_path(path: Path, base: Path) -> bool:
    # Reject if path or any parent is a symlink
    current = path
    while current != current.parent:
        if current.is_symlink():
            return False
        current = current.parent
    return True
```

### Validated Mode

If symlinks are followed:

```python
def is_safe_include(base_dir: Path, include_path: str) -> bool:
    # Resolve ALL symlinks to get real path
    resolved = (base_dir / include_path).resolve(strict=True)

    # Verify real path is within allowed directory
    base_real = base_dir.resolve()
    try:
        resolved.relative_to(base_real)
        return True
    except ValueError:
        return False
```

## Platform Considerations

| Platform | Symlink Support | Notes |
|----------|-----------------|-------|
| Linux | Full | Most common attack vector |
| macOS | Full | Case-insensitive paths |
| Windows | Limited | Requires admin or dev mode |

## Mitigation Strategies

### 1. Use O_NOFOLLOW

```c
// Open without following symlinks
int fd = open(path, O_RDONLY | O_NOFOLLOW);
if (fd < 0 && errno == ELOOP) {
    // Path is a symlink - reject
}
```

### 2. Check Before and After

```python
def safe_read(path: Path) -> str:
    # Check before
    if path.is_symlink():
        raise SecurityError("Symlink not allowed")

    # Open file
    with open(path, 'r') as f:
        # Check that we opened what we expected
        # (using fstat on file descriptor)
        return f.read()
```

### 3. Use realpath()

```python
# Resolve to canonical path first
real_path = os.path.realpath(path)
if not real_path.startswith(allowed_dir):
    raise SecurityError("Path escapes allowed directory")
```

## Configuration

```beancount
option "follow_symlinks" "false"  ; Strict mode (default)
option "follow_symlinks" "true"   ; Validated mode
```

## Error Messages

```
error: Symbolic link not allowed
  --> main.beancount:5:1
  |
5 | include "data/accounts.beancount"
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |
  = path: data/accounts.beancount
  = symlink target: /etc/passwd
  = hint: use --follow-symlinks to allow (not recommended)
```

## Recommendations

1. **Default to strict mode** (reject symlinks)
2. **Document symlink behavior** clearly
3. **Warn users** when symlink following is enabled
4. **Log symlink resolution** for debugging
