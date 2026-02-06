# Nesting Limits

## Overview

Implementations MUST limit recursion and nesting depth to prevent stack overflow.

## Requirements

### Include Depth

| Limit | Minimum | Recommended |
|-------|---------|-------------|
| Include depth | 10 | 100 |

Example at depth 3:
```
main.beancount
└── include accounts.beancount     (depth 1)
    └── include assets.beancount   (depth 2)
        └── include bank.beancount (depth 3)
```

Implementations MUST:
- Track current include depth
- Reject includes exceeding the limit
- Report the include chain in error messages

### Parser Recursion

| Limit | Minimum | Recommended |
|-------|---------|-------------|
| Expression depth | 50 | 200 |
| Metadata nesting | 10 | 50 |

### Cost Specification Nesting

Cost specs have limited nesting by grammar, but implementations MUST NOT allow unbounded recursion in cost parsing.

## Error Messages

```
error: Include depth limit exceeded
  --> deeply/nested/file.beancount
  |
  = depth: 101
  = limit: 100
  = chain: main.beancount → ... → file.beancount
```

## Implementation Guidance

### Iterative vs Recursive

Prefer iterative algorithms with explicit stacks:

```python
# Bad: recursive (can overflow)
def process(node):
    for child in node.children:
        process(child)

# Good: iterative with bounded stack
def process(root):
    stack = [root]
    while stack and len(stack) < MAX_DEPTH:
        node = stack.pop()
        stack.extend(node.children)
```

### Stack Size Estimation

| Language | Default Stack | Safe Recursion Depth |
|----------|---------------|----------------------|
| Python | 1 MB | ~1000 frames |
| Rust | 2-8 MB | ~10000 frames |
| JavaScript | ~1 MB | ~10000 frames |

## Rationale

- 10 depth minimum handles typical modular ledgers
- 100 recommended handles complex organizational structures
- Limits prevent stack overflow on all platforms
