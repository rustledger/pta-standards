# CLI Specification

This document specifies the standard command-line interface for plain text accounting tools.

## Overview

A standard CLI interface enables:

- Consistent user experience across implementations
- Script and automation compatibility
- Editor and IDE integration
- CI/CD pipeline integration

## Command Structure

### Basic Pattern

```
<tool> [global-options] <command> [command-options] [arguments]
```

### Examples

```bash
pta check ledger.beancount
pta query ledger.beancount "SELECT account, sum(position)"
pta format --in-place ledger.beancount
pta convert --from beancount --to ledger input.beancount
```

## Standard Commands

| Command | Description | Document |
|---------|-------------|----------|
| `check` | Validate ledger file | [check.md](commands/check.md) |
| `validate` | Detailed validation | [validate.md](commands/validate.md) |
| `query` | Run BQL query | [query.md](commands/query.md) |
| `format` | Format/pretty-print | [format.md](commands/format.md) |
| `convert` | Convert between formats | [convert.md](commands/convert.md) |
| `import` | Import from external sources | [import.md](commands/import.md) |
| `parse` | Parse and dump AST | [parse.md](commands/parse.md) |

## Global Options

### Help

```bash
pta --help              # General help
pta <command> --help    # Command-specific help
```

### Version

```bash
pta --version
# Output: pta 1.0.0 (beancount-v3 compatible)
```

### Input File

```bash
pta check ledger.beancount           # Positional argument
pta check --file ledger.beancount    # Explicit option
pta check -f ledger.beancount        # Short form
pta check -                          # Read from stdin
```

### Output Control

```bash
pta check --quiet           # Suppress non-error output
pta check --verbose         # Verbose output
pta check --color=auto      # Color output (auto|always|never)
pta check --format=json     # Output format (text|json|csv)
```

### Error Handling

```bash
pta check --strict          # Treat warnings as errors
pta check --max-errors=10   # Stop after N errors
pta check --ignore=E1001    # Ignore specific error codes
```

## Input/Output

### File Arguments

```bash
# Single file
pta check ledger.beancount

# Multiple files (merged)
pta check main.beancount accounts.beancount

# Glob patterns
pta check "*.beancount"

# Directory (find all .beancount files)
pta check ./ledgers/
```

### Standard Input

```bash
# Read from stdin
cat ledger.beancount | pta check -

# Here document
pta check - <<EOF
2024-01-15 * "Test"
  Assets:Cash  100 USD
  Income:Test
EOF
```

### Standard Output

Commands write results to stdout:

```bash
pta query ledger.beancount "SELECT account" > accounts.txt
```

### Standard Error

Errors and diagnostics go to stderr:

```bash
pta check ledger.beancount 2> errors.txt
```

## Output Formats

### Text (Default)

Human-readable output:

```
error: Account not opened
  --> ledger.beancount:42:3
   |
42 |   Assets:Unknown  100 USD
   |   ^^^^^^^^^^^^^^
   |
   = hint: add 'open' directive before this transaction
```

### JSON

Machine-readable output:

```bash
pta check --format=json ledger.beancount
```

```json
{
  "errors": [
    {
      "level": "error",
      "code": "E1001",
      "message": "Account not opened",
      "location": {
        "file": "ledger.beancount",
        "line": 42,
        "column": 3
      }
    }
  ],
  "summary": {
    "errors": 1,
    "warnings": 0
  }
}
```

### CSV

Tabular output for queries:

```bash
pta query --format=csv ledger.beancount "SELECT date, account, amount"
```

```csv
date,account,amount
2024-01-15,Assets:Checking,100.00 USD
2024-01-16,Expenses:Food,-25.00 USD
```

## Exit Codes

See [exit-codes.md](exit-codes.md) for complete list.

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation errors |
| 2 | Command-line usage error |
| 3 | Input file not found |
| 4 | Parse error |

## Configuration

### Configuration File

```bash
# Explicit config
pta check --config=.ptarc ledger.beancount

# Auto-discovery (search up directory tree)
# .ptarc, .pta.toml, pta.config.json
```

### Configuration Format

```toml
# .ptarc
[check]
strict = true
ignore = ["W1001", "W1002"]

[format]
indent = 2
align_amounts = true

[query]
default_format = "csv"
```

### Environment Variables

```bash
PTA_COLOR=never pta check ledger.beancount
PTA_CONFIG=/path/to/.ptarc pta check ledger.beancount
```

## Shell Integration

### Completion

```bash
# Bash
eval "$(pta completion bash)"

# Zsh
eval "$(pta completion zsh)"

# Fish
pta completion fish | source
```

### Shell Aliases

```bash
alias ptac="pta check"
alias ptaq="pta query"
alias ptaf="pta format"
```

## Scripting

### Exit Code Checking

```bash
if pta check ledger.beancount; then
  echo "Ledger is valid"
else
  echo "Ledger has errors"
  exit 1
fi
```

### Capturing Output

```bash
# Capture errors
errors=$(pta check --format=json ledger.beancount 2>&1)

# Count errors
error_count=$(echo "$errors" | jq '.summary.errors')
```

### Pipeline Integration

```bash
# Git pre-commit hook
pta check ledger.beancount || exit 1

# CI validation
pta check --strict --format=json ledger.beancount > results.json
```

## Cross-Platform

### Path Handling

- Accept both `/` and `\` as path separators
- Handle spaces in paths (quote if needed)
- Support Unicode paths

### Line Endings

- Accept LF, CRLF, or CR
- Output uses platform default (or `--line-ending` option)

### Terminal Detection

- Auto-detect terminal capabilities
- Disable color when not a TTY
- Respect `NO_COLOR` environment variable

## Implementation Requirements

### MUST

- Support `--help` and `--version`
- Use exit codes correctly
- Write errors to stderr
- Support `-` for stdin

### SHOULD

- Support `--format=json` for machine parsing
- Support `--quiet` and `--verbose`
- Provide shell completion
- Auto-discover config files

### MAY

- Support additional output formats
- Provide interactive modes
- Support plugins/extensions

## See Also

- [Exit Codes](exit-codes.md) - Complete exit code reference
- [Commands](commands/) - Individual command specifications
- [Error Codes](../errors/README.md) - Validation error codes
