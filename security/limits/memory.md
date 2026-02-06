# Memory Limits

## Overview

Implementations SHOULD enforce memory limits to prevent denial of service through memory exhaustion.

## Requirements

### Peak Memory Usage

| Limit | Guideline |
|-------|-----------|
| Per-file overhead | < 10x file size |
| AST size | < 5x file size |
| Working memory | < 2x AST size |

### Memory Growth

Implementations SHOULD:
- Use streaming/incremental parsing where possible
- Release intermediate data structures promptly
- Avoid copying entire file contents unnecessarily

### Large Collections

For hash maps and vectors that grow with input:

| Collection | Growth Strategy |
|------------|-----------------|
| Accounts map | Pre-allocate estimate, grow 2x |
| Directives list | Pre-allocate estimate, grow 1.5x |
| Posting inventory | Bounded by unique lots |

## Implementation Guidance

### Streaming Parsing

```
File → Lexer → Parser → Directive → Process → Discard
         ↑                              ↓
         └────── Bounded Buffer ────────┘
```

### Memory Monitoring

Implementations MAY provide memory tracking:

```bash
beancount --max-memory=1GB ledger.beancount
```

### Out-of-Memory Handling

When memory limits are approached:

1. Attempt garbage collection
2. Report warning with current usage
3. Abort gracefully if limit exceeded
4. Never crash without error message

## Platform Considerations

| Platform | Memory Limit Mechanism |
|----------|------------------------|
| Linux | `setrlimit(RLIMIT_AS, ...)` |
| macOS | `setrlimit(RLIMIT_RSS, ...)` |
| Windows | Job objects |
| WASM | Linear memory limit |

## Rationale

- Memory limits protect shared systems (servers, CI)
- 10x overhead allows efficient data structures
- Streaming reduces peak usage for large files
