# Plugin Sandboxing

## Overview

Implementations that support plugins MUST isolate plugin execution to prevent malicious or buggy plugins from compromising the host system.

## Threat Model

Plugins are untrusted code that may:
- Access the filesystem beyond the ledger
- Make network requests
- Execute arbitrary system commands
- Consume excessive resources
- Leak sensitive financial data

## Sandbox Requirements

### Isolation Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **None** | Full host access | Trusted, audited plugins only |
| **Process** | Separate process, limited IPC | Native plugins |
| **Container** | OS-level isolation | Untrusted plugins |
| **WebAssembly** | Memory-safe sandbox | Recommended default |

### WebAssembly Sandbox (Recommended)

WASM provides strong isolation by design:

```
+---------------------------------------------+
|                Host Process                 |
|  +---------------------------------------+  |
|  |           WASM Runtime                |  |
|  |  +---------------------------------+  |  |
|  |  |         Plugin Module           |  |  |
|  |  |  - Linear memory (isolated)     |  |  |
|  |  |  - No direct syscalls           |  |  |
|  |  |  - Imported functions only      |  |  |
|  |  +---------------------------------+  |  |
|  +---------------------------------------+  |
+---------------------------------------------+
```

### WASM Capabilities

| Capability | Default | Can Enable |
|------------|---------|------------|
| Memory access | Own linear memory only | No |
| File system | None | Via WASI (limited) |
| Network | None | No |
| System calls | None | No |
| Host functions | Explicitly imported | Yes |

### Implementation

#### WASM Runtime Selection

| Runtime | Language | Features |
|---------|----------|----------|
| Wasmtime | Rust | Full WASI, async |
| Wasmer | Rust | WASI, multiple backends |
| wasm3 | C | Lightweight, embedded |
| V8 | C++ | Browser compatible |

#### Host-Plugin Interface

```rust
// Host provides these functions to plugins
#[link(wasm_import_module = "beancount")]
extern "C" {
    // Read-only access to directives
    fn get_directive_count() -> u32;
    fn get_directive(index: u32) -> DirectiveRef;

    // Plugin output
    fn emit_directive(ptr: *const u8, len: u32);
    fn emit_error(ptr: *const u8, len: u32);

    // No filesystem, network, or other capabilities
}
```

#### Memory Limits

```rust
// Configure WASM instance limits
let engine = Engine::new(&Config::new()
    .max_memory_size(64 * 1024 * 1024)  // 64 MB max
    .max_table_elements(10000)
    .max_instances(1)
)?;
```

## Native Plugin Sandbox

For native (non-WASM) plugins:

### Process Isolation

```
+-----------------+     IPC      +-----------------+
|   Main Process  |<------------>|  Plugin Process |
|   (privileged)  |              |  (sandboxed)    |
+-----------------+              +-----------------+
```

### Linux Sandboxing

```rust
use seccomp::*;

fn sandbox_plugin() -> Result<()> {
    // Allow only safe syscalls
    let filter = SeccompFilter::new(vec![
        allow_syscall(Syscall::read),
        allow_syscall(Syscall::write),  // stdout/stderr only
        allow_syscall(Syscall::mmap),
        allow_syscall(Syscall::exit_group),
        // Block everything else
    ])?;
    filter.load()?;
    Ok(())
}
```

### macOS Sandboxing

```c
// sandbox-exec profile
(version 1)
(deny default)
(allow process-exec)
(allow file-read-data (subpath "/path/to/ledger"))
(deny network*)
(deny file-write*)
```

### Windows Sandboxing

```rust
// Use AppContainer or restricted token
use windows::Win32::Security::*;

fn create_restricted_token() -> HANDLE {
    // Remove all privileges
    // Deny admin SIDs
    // Add restricted SIDs
}
```

## Resource Limits

### Execution Time

```rust
// Timeout plugin execution
let result = tokio::time::timeout(
    Duration::from_secs(30),
    plugin.run(directives)
).await?;
```

### Memory Usage

```rust
// Monitor and limit memory
if plugin_memory_usage() > MAX_PLUGIN_MEMORY {
    plugin.terminate();
    return Err(PluginError::MemoryExceeded);
}
```

### CPU Usage

```rust
// Limit CPU time (WASM fuel metering)
let mut store = Store::new(&engine, ());
store.add_fuel(1_000_000)?;  // 1M instructions max

match instance.call(&mut store, "run", &[]) {
    Err(e) if e.is::<Trap>() => {
        // Out of fuel - plugin took too long
    }
    ...
}
```

## Data Isolation

### Read-Only Input

Plugins MUST NOT be able to modify input directives:

```rust
// Pass immutable references
fn run_plugin(plugin: &Plugin, directives: &[Directive]) -> Vec<Directive> {
    // Plugin receives read-only view
    // Returns new directives (additions/modifications)
}
```

### Output Validation

Validate all plugin output:

```rust
fn validate_plugin_output(output: &[Directive]) -> Result<()> {
    for directive in output {
        // Verify directive is well-formed
        // Check for injection attempts
        // Validate metadata
    }
    Ok(())
}
```

## Security Modes

| Mode | WASM | Native | Trust Level |
|------|------|--------|-------------|
| **Strict** | Yes, full sandbox | Reject | Untrusted |
| **Standard** | Yes, full sandbox | Process isolated | Semi-trusted |
| **Permissive** | Yes, minimal limits | Allowed | Trusted |

## Configuration

```beancount
; Plugin security settings
option "plugin_sandbox" "strict"     ; Enforce WASM sandbox
option "plugin_timeout" "30"         ; Seconds
option "plugin_memory_limit" "64MB"  ; Max memory per plugin
```

## Error Handling

```
error: Plugin execution blocked by sandbox
  --> main.beancount:1:1
  |
1 | plugin "malicious_plugin"
  | ^^^^^^^^^^^^^^^^^^^^^^^^^
  |
  = reason: attempted filesystem access outside allowed paths
  = path: /etc/passwd
  = hint: plugins cannot access files outside the ledger directory
```

## Recommendations

1. **Default to WASM** for all plugins
2. **Reject native plugins** unless explicitly allowed
3. **Set resource limits** (time, memory, CPU)
4. **Validate all output** from plugins
5. **Log plugin activity** for auditing
6. **Use process isolation** for native plugins if WASM not available
