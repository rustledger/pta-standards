# Error Message Style Guide

This document provides guidelines for writing clear, helpful error messages.

## Principles

### 1. Be Specific

**Bad**: "Syntax error"
**Good**: "Expected account name after 'open' keyword"

### 2. Show Context

**Bad**: "Invalid date"
**Good**: "Invalid date '2024-13-45': month must be 1-12"

### 3. Suggest Fixes

**Bad**: "Balance assertion failed"
**Good**: "Balance assertion failed: expected 1000 USD, actual 950 USD. Check transaction on line 38."

### 4. Use Active Voice

**Bad**: "Account was not found"
**Good**: "Account 'Assets:Unknown' not opened"

### 5. Avoid Jargon

**Bad**: "AST node validation failed"
**Good**: "Invalid posting format"

## Message Structure

### Primary Message

The main error description should:
- Start with the problem
- Use present tense
- Be one sentence
- Be under 80 characters

```
Account 'Assets:Checking' not opened before use
```

### Secondary Information

Additional context in the hint:
- Explain why it's an error
- Suggest how to fix it
- Reference documentation

```
= hint: Add '2024-01-01 open Assets:Checking' before this transaction
```

## Common Patterns

### Not Found

```
Account 'Assets:Unknown' not declared
Commodity 'XYZ' not defined
```

### Already Exists

```
Account 'Assets:Checking' already opened on line 5
Duplicate transaction on 2024-01-15 (possible duplicate of line 42)
```

### Type Mismatch

```
Expected amount, got string "hello"
Cannot compare date with number
```

### Constraint Violation

```
Currency 'EUR' not allowed for account 'Assets:Checking' (allowed: USD)
Transaction does not balance: residual is 0.50 USD
```

### Range Errors

```
Date '2024-13-45' is invalid: month must be 1-12
Tolerance 0.1 exceeds maximum allowed (0.05)
```

## Formatting

### Numbers

- Use locale-appropriate formatting
- Show full precision for debugging
- Use thousands separators for readability

```
Balance mismatch: expected 1,234.56 USD, actual 1,234.00 USD
```

### Accounts

- Show full account path
- Use quotes for clarity

```
Account 'Assets:Bank:Checking' closed on 2024-06-30
```

### Dates

- Use ISO format (YYYY-MM-DD)
- Include day of week for context when helpful

```
Transaction date 2024-01-15 (Monday) is after close date 2024-01-10
```

### Code Examples

Include correct syntax in hints:

```
= hint: Use format: 2024-01-15 * "Payee" "Narration"
```

## Error Categories

### Syntax Errors

Focus on what was expected vs. found:

```
Expected 'open' keyword, found 'opne'
Unterminated string starting at column 15
Missing closing brace in cost specification
```

### Semantic Errors

Focus on the logical problem:

```
Account used before being opened
Transaction references closed account
Balance assertion cannot be satisfied
```

### Validation Errors

Focus on the constraint violated:

```
Transaction does not balance
Currency not allowed for this account
Duplicate entry detected
```

## Multi-Line Context

For complex errors, show relevant context:

```
ERROR[E1102]: Transaction does not balance
  --> ledger.beancount:42:1
   |
42 | 2024-01-15 * "Grocery shopping"
43 |   Assets:Checking  -100 USD
44 |   Expenses:Food:Groceries
45 |   Expenses:Food:Snacks
   |
   = The sum of all postings is -100 USD, but it should be 0
   = hint: Add amounts to the elided postings, or remove one
```

## Related Information

Link to related source locations:

```
ERROR[E1103]: Account closed before last posting
  --> ledger.beancount:100:1
    |
100 | 2024-06-30 close Assets:Checking
    | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |
note: Last posting to this account:
  --> ledger.beancount:95:3
   |
95 |   Assets:Checking  -50 USD
   |   ^^^^^^^^^^^^^^^^^^^^^^^
```

## Internationalization

### Message Keys

Use message keys that can be translated:

```python
# Internal
raise Error("E1101", account=account_name)

# Template
E1101 = "Account '{account}' not opened"
```

### Placeholders

Use named placeholders:

```
"Expected {expected}, got {actual}"
"Account '{account}' not allowed currency '{currency}'"
```

## Testing Messages

Error messages should be tested:

1. Check message contains key information
2. Verify placeholders are filled
3. Test edge cases (empty strings, long names)
4. Validate location information

## See Also

- [Error Specification](spec.md)
- [Error Codes](codes/)
