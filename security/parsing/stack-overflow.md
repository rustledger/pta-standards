# Stack Overflow Prevention

## Overview

Implementations MUST prevent stack overflow from deeply nested or recursive input.

## The Problem

Recursive descent parsers use the call stack for nesting:

```beancount
; Each level of nesting = one stack frame
2024-01-01 * "Transaction"
  Assets:A  1 USD {1 USD, 2024-01-01, "label"} @ 1 USD
    metadata: "deeply"
      nested: "value"
```

Malicious input with excessive nesting can exhaust the stack.

## Attack Vectors

### 1. Deep Include Chains

```
file1.beancount includes file2.beancount
file2.beancount includes file3.beancount
...
file1000.beancount includes file1001.beancount
```

### 2. Nested Expressions

If arithmetic expressions are supported:

```
((((((((((((((((((((1+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)+1)
```

### 3. Deep Metadata

```beancount
2024-01-01 open Assets:Test
  meta1: "value"
  ; Parser stores metadata stack
```

## Requirements

### Depth Limits

| Structure | Minimum Limit | Recommended |
|-----------|---------------|-------------|
| Include depth | 10 | 100 |
| Expression nesting | 50 | 200 |
| Parser call depth | 100 | 1000 |

### Implementation

Implementations MUST either:

1. **Use iterative parsing** with explicit stack
2. **Track recursion depth** and reject at limit
3. **Increase stack size** with hard upper bound

## Iterative Parsing

Convert recursive algorithms to iterative:

```python
# Recursive (vulnerable)
def parse_expr(tokens):
    left = parse_term(tokens)
    if tokens.peek() == '+':
        tokens.consume()
        right = parse_expr(tokens)  # Recursive call
        return Add(left, right)
    return left

# Iterative (safe)
def parse_expr(tokens):
    stack = []
    while True:
        term = parse_term(tokens)
        if not stack or tokens.peek() != '+':
            break
        tokens.consume()
        stack.append(term)
    result = term
    while stack:
        result = Add(stack.pop(), result)
    return result
```

## Depth Tracking

```rust
fn parse_expr(&mut self, depth: usize) -> Result<Expr, Error> {
    if depth > MAX_DEPTH {
        return Err(Error::MaxDepthExceeded);
    }
    // ... parsing logic
    self.parse_expr(depth + 1)?  // Pass depth
}
```

## Stack Size Considerations

| Platform | Default Stack | Configurable |
|----------|---------------|--------------|
| Linux | 8 MB | `ulimit -s` |
| macOS | 8 MB | `ulimit -s` |
| Windows | 1 MB | Linker flag |
| WASM | 1 MB | Compile option |

## Error Messages

```
error: Maximum nesting depth exceeded
  --> malicious.beancount:1000:1
  |
  = depth: 101
  = limit: 100
  = hint: simplify expression or increase --max-depth
```

## Testing

Create test files with:

1. Include depth at exactly limit → accept
2. Include depth at limit + 1 → reject
3. Expression nesting at limit → accept
4. Expression nesting at limit + 1 → reject

Verify no crash, only clean error.
