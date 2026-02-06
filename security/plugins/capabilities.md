# Plugin Capability System

## Overview

Implementations SHOULD use a capability-based security model for plugins, granting only the minimum permissions required for each plugin's functionality.

## Design Principles

### Principle of Least Privilege

Each plugin should have access to only what it needs:

```
+---------------------------------------------------------+
|                    Capability Model                      |
+---------------------------------------------------------+
|  Plugin A (price fetcher)                               |
|    [x] read_prices                                      |
|    [x] network_https (api.example.com only)             |
|    [ ] write_directives                                 |
|    [ ] filesystem                                       |
+---------------------------------------------------------+
|  Plugin B (auto_accounts)                               |
|    [x] read_accounts                                    |
|    [x] write_directives (open only)                     |
|    [ ] network                                          |
|    [ ] filesystem                                       |
+---------------------------------------------------------+
```

### Capability Tokens

Capabilities are unforgeable tokens that grant specific permissions:

```rust
/// A capability token granting specific permissions
pub struct Capability {
    kind: CapabilityKind,
    scope: CapabilityScope,
    // Cryptographically signed by host
}

pub enum CapabilityKind {
    ReadDirectives,
    WriteDirectives,
    ReadAccounts,
    ReadPrices,
    Network,
    FileRead,
    FileWrite,
}

pub enum CapabilityScope {
    All,
    Filtered { accounts: Vec<AccountPattern> },
    Domain { hosts: Vec<String> },
    Path { prefix: PathBuf },
}
```

## Standard Capabilities

### Directive Access

| Capability | Description | Risk Level |
|------------|-------------|------------|
| `read:directives` | Read all directives | Low |
| `read:directives:transactions` | Read transactions only | Low |
| `read:directives:prices` | Read price directives | Low |
| `write:directives` | Emit new directives | Medium |
| `write:directives:open` | Emit Open directives only | Low |
| `modify:directives` | Modify existing directives | High |

### Account Access

| Capability | Description | Risk Level |
|------------|-------------|------------|
| `read:accounts` | Read account names | Low |
| `read:accounts:balances` | Read account balances | Medium |
| `read:accounts:pattern:Assets:*` | Read matching accounts | Low |

### Network Access

| Capability | Description | Risk Level |
|------------|-------------|------------|
| `network:none` | No network access (default) | None |
| `network:https:*.example.com` | HTTPS to specific domains | Medium |
| `network:all` | Unrestricted network | High |

### Filesystem Access

| Capability | Description | Risk Level |
|------------|-------------|------------|
| `file:none` | No filesystem access (default) | None |
| `file:read:ledger` | Read files in ledger directory | Low |
| `file:read:path:/data/*` | Read from specific path | Medium |
| `file:write:path:/output/*` | Write to specific path | High |

## Capability Declaration

### In Plugin Manifest

Plugins declare required capabilities:

```toml
# plugin.toml
[plugin]
name = "price_fetcher"
version = "1.0.0"

[capabilities.required]
read = ["directives:prices", "accounts"]
network = ["https:api.exchangerate.com"]

[capabilities.optional]
file = ["read:ledger"]  # For caching
```

### At Load Time

Host verifies and grants capabilities:

```rust
fn load_plugin(path: &Path, policy: &SecurityPolicy) -> Result<Plugin> {
    let manifest = PluginManifest::load(path)?;

    // Check required capabilities against policy
    for cap in &manifest.capabilities.required {
        if !policy.allows(cap) {
            return Err(PluginError::CapabilityDenied(cap.clone()));
        }
    }

    // Grant capabilities as tokens
    let capabilities = manifest.capabilities.required
        .iter()
        .map(|c| policy.grant(c))
        .collect();

    Plugin::new(path, capabilities)
}
```

## Capability Enforcement

### At Runtime

```rust
impl PluginRuntime {
    fn read_accounts(&self, pattern: &str) -> Result<Vec<Account>> {
        // Check capability
        self.require_capability(Capability::ReadAccounts)?;

        // If scoped, filter results
        let accounts = self.ledger.accounts();
        if let Some(scope) = self.capability_scope(Capability::ReadAccounts) {
            return Ok(accounts.filter(|a| scope.matches(a)).collect());
        }

        Ok(accounts.collect())
    }

    fn emit_directive(&mut self, directive: Directive) -> Result<()> {
        // Check capability
        self.require_capability(Capability::WriteDirectives)?;

        // If scoped, validate directive type
        if let Some(scope) = self.capability_scope(Capability::WriteDirectives) {
            if !scope.allows_directive(&directive) {
                return Err(PluginError::CapabilityViolation);
            }
        }

        self.output.push(directive);
        Ok(())
    }
}
```

### Capability Revocation

Capabilities can be revoked mid-execution:

```rust
impl PluginRuntime {
    fn revoke(&mut self, capability: CapabilityKind) {
        self.capabilities.remove(&capability);
        // Future calls using this capability will fail
    }
}
```

## Security Policies

### Built-in Policies

```rust
pub enum SecurityPolicy {
    /// No capabilities (maximum security)
    Deny,

    /// Read-only access to directives
    ReadOnly,

    /// Standard plugin permissions
    Standard,

    /// Custom policy
    Custom(CapabilitySet),
}

impl SecurityPolicy {
    pub fn standard() -> Self {
        Self::Custom(CapabilitySet::new()
            .add(Capability::ReadDirectives)
            .add(Capability::ReadAccounts)
            .add(Capability::WriteDirectives)
        )
    }
}
```

### User Configuration

```beancount
; Global plugin policy
option "plugin_policy" "standard"

; Per-plugin overrides
plugin "price_fetcher" {
  capabilities: [
    "read:directives:prices",
    "network:https:api.exchangerate.com"
  ]
}

plugin "custom_validator" {
  capabilities: [
    "read:directives",
    "read:accounts"
  ]
}
```

### Command Line

```bash
# Run with strict policy
beancount --plugin-policy=readonly ledger.beancount

# Grant specific capability to plugin
beancount --plugin-capability=price_fetcher:network:https:* ledger.beancount
```

## Capability Audit

### Logging

```rust
impl PluginRuntime {
    fn use_capability(&self, cap: &Capability) {
        // Log all capability usage
        log::info!(
            plugin = self.name,
            capability = %cap,
            "Plugin used capability"
        );
    }
}
```

### Audit Report

```
Plugin Capability Audit
=======================

price_fetcher v1.0.0
  Used capabilities:
    - read:directives:prices (152 times)
    - network:https:api.exchangerate.com (12 requests)
  Unused declared capabilities:
    - file:read:ledger (optional, never used)

auto_accounts v2.1.0
  Used capabilities:
    - read:accounts (1 time)
    - write:directives:open (3 times)
  Attempted denied capabilities:
    - write:directives:transaction (BLOCKED)
```

## Error Messages

```
error: Plugin capability denied
  --> main.beancount:3:1
  |
3 | plugin "untrusted_plugin"
  | ^^^^^^^^^^^^^^^^^^^^^^^^^ requires capability not granted
  |
  = plugin: untrusted_plugin
  = required: network:https:*
  = policy: standard (no network access)
  = hint: add --plugin-capability=untrusted_plugin:network:https:example.com
```

```
error: Plugin capability violation
  --> [plugin: auto_accounts]
  |
  = attempted: write transaction directive
  = granted: write:directives:open only
  = hint: plugin tried to emit Transaction but only has Open permission
```

## Recommendations

1. **Declare capabilities explicitly** in plugin manifests
2. **Default to minimal permissions** - deny by default
3. **Scope capabilities narrowly** - use patterns and domains
4. **Audit capability usage** - log all access
5. **Review capability requests** before granting
6. **Separate read and write** capabilities
7. **Time-limit capabilities** for sensitive operations
