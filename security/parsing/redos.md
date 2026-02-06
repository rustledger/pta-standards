# Regular Expression Denial of Service (ReDoS)

## Overview

Implementations MUST avoid regular expressions vulnerable to catastrophic backtracking.

## The Problem

Certain regex patterns exhibit exponential time complexity on specific inputs:

```regex
# Vulnerable pattern
(a+)+$

# Attack string: "aaaaaaaaaaaaaaaaaaaaaaaaaaaa!"
# Time: O(2^n) where n = number of 'a's
```

## Vulnerable Patterns

### Nested Quantifiers

```regex
# Bad
(a+)+
(a*)*
(a+)*
(.*)+

# Good
a+
a*
```

### Overlapping Alternations

```regex
# Bad
(a|a)+
(ab|a)+b

# Good
a+
a+b?
```

### Patterns in Beancount Context

| Use Case | Vulnerable | Safe Alternative |
|----------|------------|------------------|
| Account match | `(:[A-Za-z]+)+` | `(:[A-Za-z]+)*` with length limit |
| Currency | `[A-Z]+` | `[A-Z]{1,24}` |
| Number | `[0-9,]+` | `[0-9]{1,50}(,[0-9]{3})*` |

## Requirements

Implementations MUST:

1. **Audit all regex patterns** for ReDoS vulnerability
2. **Use non-backtracking engines** when available (RE2, rust regex)
3. **Set match timeouts** if using backtracking engines
4. **Limit input length** before regex matching

## Safe Regex Engines

| Engine | Backtracking | ReDoS Safe |
|--------|--------------|------------|
| RE2 (Google) | No | Yes |
| Rust `regex` | No | Yes |
| Hyperscan | No | Yes |
| PCRE | Yes | No |
| Python `re` | Yes | No |
| JavaScript | Yes | No |

## Mitigation Strategies

### 1. Use Linear-Time Engines

```rust
// Rust: regex crate is safe by design
use regex::Regex;
let re = Regex::new(r"pattern").unwrap();  // guaranteed O(n)
```

### 2. Set Timeouts

```python
# Python: use regex with timeout
import regex
regex.match(pattern, string, timeout=1.0)
```

### 3. Limit Input Length

```python
# Check length before matching
if len(input) > MAX_LENGTH:
    raise ValueError("Input too long")
result = re.match(pattern, input)
```

### 4. Avoid Regex for Simple Parsing

```python
# Bad: regex for fixed format
date = re.match(r"(\d{4})-(\d{2})-(\d{2})", line)

# Good: direct parsing
year, month, day = line[:4], line[5:7], line[8:10]
```

## Testing

Test with attack strings:

```python
attack_strings = [
    "a" * 30 + "!",           # Nested quantifier attack
    "a" * 30 + "b" * 30,      # Overlapping alternation
    " " * 1000 + "x",         # Leading whitespace
]
```

Verify each completes in < 100ms.

## References

- [OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
- [RE2 Syntax](https://github.com/google/re2/wiki/Syntax)
