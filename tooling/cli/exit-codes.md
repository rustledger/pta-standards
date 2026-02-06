# Exit Codes

This document specifies standard exit codes for plain text accounting CLI tools.

## Overview

Exit codes enable scripts and automation to detect success or failure and take appropriate action. Consistent exit codes across implementations improve interoperability.

## Exit Code Ranges

| Range | Category |
|-------|----------|
| 0 | Success |
| 1-9 | Common errors |
| 10-19 | Parse errors |
| 20-29 | Validation errors |
| 30-39 | Query errors |
| 40-49 | I/O errors |
| 50-59 | Configuration errors |
| 60-99 | Reserved |
| 100-199 | Implementation-specific |
| 200-255 | Reserved |

## Standard Exit Codes

### Success (0)

```
0   SUCCESS
```

Command completed successfully with no errors.

```bash
$ pta check valid.beancount
$ echo $?
0
```

### Common Errors (1-9)

```
1   ERROR_VALIDATION
    Validation errors found (ledger has errors)

2   ERROR_USAGE
    Invalid command-line usage

3   ERROR_FILE_NOT_FOUND
    Input file does not exist

4   ERROR_PERMISSION_DENIED
    Cannot read input file

5   ERROR_INTERRUPTED
    Operation interrupted (SIGINT)

6   ERROR_INTERNAL
    Internal error (bug)

7   ERROR_NOT_IMPLEMENTED
    Feature not implemented

8   ERROR_TIMEOUT
    Operation timed out

9   (Reserved)
```

### Parse Errors (10-19)

```
10  ERROR_PARSE
    General parse error

11  ERROR_SYNTAX
    Syntax error in input

12  ERROR_ENCODING
    Invalid file encoding (not UTF-8)

13  ERROR_INCLUDE_NOT_FOUND
    Included file not found

14  ERROR_INCLUDE_CYCLE
    Circular include detected

15  ERROR_LEXER
    Lexical analysis error

16-19 (Reserved)
```

### Validation Errors (20-29)

```
20  ERROR_VALIDATE
    General validation error

21  ERROR_BALANCE
    Transaction balance error

22  ERROR_ACCOUNT
    Account-related error

23  ERROR_DUPLICATE
    Duplicate entry detected

24  ERROR_ASSERTION
    Balance assertion failed

25  ERROR_BOOKING
    Booking/inventory error

26-29 (Reserved)
```

### Query Errors (30-39)

```
30  ERROR_QUERY
    General query error

31  ERROR_QUERY_SYNTAX
    Query syntax error

32  ERROR_QUERY_SEMANTIC
    Query semantic error (invalid column, etc.)

33  ERROR_QUERY_EXECUTION
    Query execution error

34-39 (Reserved)
```

### I/O Errors (40-49)

```
40  ERROR_IO
    General I/O error

41  ERROR_READ
    Error reading file

42  ERROR_WRITE
    Error writing file

43  ERROR_STDIN
    Error reading stdin

44  ERROR_STDOUT
    Error writing stdout

45-49 (Reserved)
```

### Configuration Errors (50-59)

```
50  ERROR_CONFIG
    General configuration error

51  ERROR_CONFIG_PARSE
    Configuration file parse error

52  ERROR_CONFIG_INVALID
    Invalid configuration value

53  ERROR_PLUGIN_LOAD
    Plugin load error

54  ERROR_PLUGIN_EXECUTE
    Plugin execution error

55-59 (Reserved)
```

## Exit Code Combinations

### Multiple Error Types

When multiple error types occur, use the most severe:

| Priority | Exit Code | Meaning |
|----------|-----------|---------|
| 1 | 6 | Internal error |
| 2 | 10-19 | Parse errors |
| 3 | 20-29 | Validation errors |
| 4 | 30-39 | Query errors |
| 5 | 40-49 | I/O errors |
| 6 | 1 | General validation |

### Warnings Only

If only warnings (no errors) are found:

```bash
$ pta check --strict ledger.beancount   # Warnings as errors → exit 1
$ pta check ledger.beancount            # Warnings allowed → exit 0
```

## Usage Examples

### Shell Scripts

```bash
#!/bin/bash

pta check ledger.beancount
status=$?

case $status in
  0)
    echo "Ledger is valid"
    ;;
  1)
    echo "Validation errors found"
    exit 1
    ;;
  3)
    echo "File not found"
    exit 1
    ;;
  10|11)
    echo "Parse error"
    exit 1
    ;;
  *)
    echo "Unexpected error: $status"
    exit 1
    ;;
esac
```

### Makefile

```makefile
.PHONY: check
check:
	@pta check ledger.beancount || (echo "Ledger check failed"; exit 1)
```

### CI/CD

```yaml
# GitHub Actions
- name: Validate ledger
  run: |
    pta check ledger.beancount
    if [ $? -ne 0 ]; then
      echo "::error::Ledger validation failed"
      exit 1
    fi
```

### Git Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

if ! pta check ledger.beancount; then
  echo "Commit rejected: ledger has errors"
  exit 1
fi
```

## Semantic Interpretation

### Exit 0: Success

- All validations passed
- No errors (warnings may be present unless `--strict`)
- Output was generated successfully

### Exit 1: Validation Errors

- File was parsed successfully
- Semantic validation found errors
- Ledger is not valid

### Exit 2: Usage Error

- Invalid command-line arguments
- Missing required arguments
- Unknown options

```bash
$ pta check --unknown-option
error: unknown option '--unknown-option'
$ echo $?
2
```

### Exit 3: File Not Found

- Specified input file does not exist
- Include file not found (may use 13 instead)

```bash
$ pta check nonexistent.beancount
error: file not found: nonexistent.beancount
$ echo $?
3
```

### Exit 10: Parse Error

- File could not be parsed
- Syntax is invalid
- Different from validation error (exit 1)

```bash
$ echo "invalid syntax @@@ here" | pta check -
error: parse error at line 1
$ echo $?
10
```

## Implementation Notes

### Exit Code Selection

When returning an exit code:

1. Use the most specific code available
2. Prefer lower numbers for more severe errors
3. Document any implementation-specific codes (100-199)

### Signal Handling

Exit codes 128+ indicate signal termination:

```bash
# Killed by SIGINT (2): 128 + 2 = 130
# Killed by SIGTERM (15): 128 + 15 = 143
```

Tools SHOULD handle SIGINT gracefully (exit 5).

### Cross-Platform

Exit codes should work consistently across:

- Unix/Linux
- macOS
- Windows (uses `%ERRORLEVEL%`)

## Reserved Ranges

### 60-99: Reserved for Future

These codes may be assigned in future versions.

### 100-199: Implementation-Specific

Implementations MAY use these for tool-specific errors:

```
100  Implementation-specific error A
101  Implementation-specific error B
...
```

Document these in implementation documentation.

### 200-255: Reserved

Do not use. Some systems have special meanings for these values.

## Cross-Tool Consistency

### Common Tools

| Exit Code | bean-check | hledger | ledger |
|-----------|------------|---------|--------|
| Success | 0 | 0 | 0 |
| Validation error | 1 | 1 | 1 |
| Parse error | 1 | 1 | 1 |
| File not found | 1 | 1 | 1 |

This specification recommends more granular exit codes for better automation.
