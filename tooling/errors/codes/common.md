# Common Error Codes (E0xxx)

These error codes are shared across all plain text accounting formats.

## Syntax Errors (E00xx)

### E0001: Unexpected Token

The parser encountered an unexpected token.

**Message**: `Unexpected token '{token}'`

**Example**:
```
2024-01-15 *** "Invalid flag"
           ^^^
```

**Fix**: Use a valid token at this position.

---

### E0002: Unterminated String

A string literal was not properly closed.

**Message**: `Unterminated string starting at column {column}`

**Example**:
```
2024-01-15 * "Missing end quote
             ^
```

**Fix**: Add closing quote to the string.

---

### E0003: Invalid Date

The date format is invalid.

**Message**: `Invalid date '{date}': {reason}`

**Example**:
```
2024-13-45 open Assets:Checking
^^^^^^^^^^
```

**Fix**: Use valid date format YYYY-MM-DD.

---

### E0004: Invalid Number

The number format is invalid.

**Message**: `Invalid number '{number}'`

**Example**:
```
  Assets:Checking  1.2.3 USD
                   ^^^^^
```

**Fix**: Use valid number format.

---

### E0005: Invalid Account Name

The account name contains invalid characters or structure.

**Message**: `Invalid account name '{account}'`

**Example**:
```
  assets:checking  100 USD
  ^^^^^^^
```

**Fix**: Account names must start with a valid root (Assets, Liabilities, etc.).

---

### E0006: Invalid Currency

The currency/commodity name is invalid.

**Message**: `Invalid currency '{currency}'`

**Example**:
```
  Assets:Checking  100 usd
                       ^^^
```

**Fix**: Currency names must be uppercase letters.

---

### E0007: Missing Required Field

A required field is missing.

**Message**: `Missing required {field}`

**Example**:
```
2024-01-15 * "Test"
  Assets:Checking
  ; missing second posting
```

**Fix**: Add the required field.

---

### E0008: Unexpected End of File

The file ended unexpectedly.

**Message**: `Unexpected end of file`

**Example**:
```
2024-01-15 * "Incomplete
```

**Fix**: Complete the statement or directive.

---

### E0009: Invalid Escape Sequence

An invalid escape sequence was found in a string.

**Message**: `Invalid escape sequence '\\{char}'`

**Example**:
```
2024-01-15 * "Test \q invalid"
                   ^^
```

**Fix**: Use valid escape sequences: `\\`, `\"`, `\n`, `\t`.

---

## File Errors (E01xx)

### E0101: File Not Found

The specified file does not exist.

**Message**: `File not found: '{path}'`

**Fix**: Check the file path and ensure the file exists.

---

### E0102: Permission Denied

Cannot read the file due to permissions.

**Message**: `Permission denied: '{path}'`

**Fix**: Check file permissions.

---

### E0103: Encoding Error

The file contains invalid UTF-8.

**Message**: `Invalid UTF-8 encoding at byte {offset}`

**Fix**: Ensure the file is saved as UTF-8.

---

### E0104: Include Cycle

Circular include detected.

**Message**: `Circular include detected: {chain}`

**Example**:
```
; a.beancount includes b.beancount
; b.beancount includes a.beancount
```

**Fix**: Remove circular include reference.

---

### E0105: Include Not Found

Included file does not exist.

**Message**: `Included file not found: '{path}'`

**Fix**: Check the include path.

---

### E0106: Path Traversal

Attempted path traversal in include.

**Message**: `Path traversal not allowed: '{path}'`

**Fix**: Use paths within the allowed directory.

---

## Internal Errors (E09xx)

### E0901: Internal Error

An unexpected internal error occurred.

**Message**: `Internal error: {details}`

**Fix**: Report this bug to the tool maintainers.

---

### E0902: Resource Limit

A resource limit was exceeded.

**Message**: `{resource} limit exceeded: {value} > {limit}`

**Fix**: Reduce complexity or increase limits.

---

### E0903: Timeout

Processing timed out.

**Message**: `Processing timed out after {seconds} seconds`

**Fix**: Simplify the journal or increase timeout.

---

## Error Code Ranges

| Range | Category |
|-------|----------|
| E0001-E0099 | Syntax errors |
| E0100-E0199 | File errors |
| E0900-E0999 | Internal errors |

## See Also

- [Beancount Errors](beancount.md)
- [Ledger Errors](ledger.md)
- [hledger Errors](hledger.md)
