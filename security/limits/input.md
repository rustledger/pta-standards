# Input Limits

## Overview

Implementations MUST enforce limits on input size to prevent resource exhaustion attacks.

## Requirements

### File Size

| Limit | Minimum | Recommended | Maximum |
|-------|---------|-------------|---------|
| Single file | 10 MB | 100 MB | 1 GB |
| Total (with includes) | 50 MB | 500 MB | 5 GB |

Implementations MUST:
- Check file size before reading into memory
- Reject files exceeding the configured limit
- Report clear error messages with the limit value

### Line Length

| Limit | Minimum | Recommended |
|-------|---------|-------------|
| Line length | 4 KB | 64 KB |

Implementations MUST:
- Handle lines up to the limit without truncation
- Reject or truncate lines exceeding the limit
- Not allocate unbounded memory for a single line

### Line Count

| Limit | Minimum | Recommended |
|-------|---------|-------------|
| Lines per file | 100,000 | 10,000,000 |

### Include Count

| Limit | Minimum | Recommended |
|-------|---------|-------------|
| Total includes | 100 | 10,000 |

Implementations MUST:
- Track number of included files
- Reject when limit exceeded
- Count each unique file only once

## Configuration

Implementations SHOULD allow configuration of limits:

```beancount
option "max_file_size" "100MB"
option "max_include_count" "1000"
```

Or via command-line:

```bash
beancount --max-file-size=100MB ledger.beancount
```

## Error Messages

When limits are exceeded, report:

```
error: File size limit exceeded
  --> large-file.beancount
  |
  = file size: 150 MB
  = limit: 100 MB
  = hint: increase limit with --max-file-size or split into multiple files
```

## Rationale

- **10 MB minimum**: Handles typical personal ledgers (10+ years)
- **100 MB recommended**: Handles large business ledgers
- **1 GB maximum**: Prevents accidental DoS, still allows enterprise use

## Test Vectors

Implementations SHOULD pass these tests:

1. Accept file at exactly the limit
2. Reject file 1 byte over the limit
3. Accept total includes at exactly the limit
4. Reject when include count exceeds limit
