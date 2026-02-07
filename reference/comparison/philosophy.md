# Philosophy Comparison

Design philosophy and approach comparison between Beancount, Ledger, and hledger.

## Origins & History

### Ledger (2003)
- Created by **John Wiegley**
- The original plain text accounting tool
- Inspired by traditional accounting software
- Written in C++ for performance
- Philosophy: Power and flexibility

### hledger (2007)
- Created by **Simon Michael**
- Started as a Haskell learning project
- Compatible with Ledger format
- Philosophy: Reliability and usability

### Beancount (2008)
- Created by **Martin Blais**
- Clean-slate redesign of PTA concepts
- Written in Python for extensibility
- Philosophy: Correctness and simplicity

## Core Design Principles

### Beancount: Strictness

**"Explicit is better than implicit"**

- Accounts must be declared before use
- Currencies must be declared
- Strict validation by default
- No implicit behaviors

```beancount
; Must declare before use
2020-01-01 open Assets:Checking USD

; Error if not declared
2024-01-15 * "Store"
  Assets:Checking  -50.00 USD
  Expenses:Food    ; Must exist
```

### Ledger: Flexibility

**"Trust the user, provide power"**

- No declarations required
- Implicit account creation
- Value expressions for computation
- Maximum configurability

```ledger
; Just use accounts directly
2024/01/15 * Store
    Assets:Checking    $-50.00
    Expenses:Food      (amount * 1)  ; Expressions work
```

### hledger: Balance

**"Practical reliability"**

- Optional strictness (`--strict`)
- Good defaults
- Clear error messages
- Compatibility with Ledger

```hledger
; Works without declarations
2024-01-15 * Store
    Assets:Checking    $-50.00
    Expenses:Food

; But can opt into strictness
; hledger check --strict
```

## Validation Philosophy

### Beancount
- **Fail early, fail loudly**
- Validation is mandatory
- Every error must be fixed
- No processing of invalid files

### Ledger
- **Warn but continue**
- Validation is optional
- Tools work with partial data
- User decides what to enforce

### hledger
- **Configurable strictness**
- Multiple check levels
- Default: lenient
- `--strict`: enforce rules

## Data Integrity

### Beancount
```
Source File → Parser → Plugins → Validation → Output
                                    ↓
                              All errors block output
```

### Ledger
```
Source File → Parser → Output
                ↓
           Warnings shown, output continues
```

### hledger
```
Source File → Parser → Optional Checks → Output
                            ↓
                    Configurable behavior
```

## Extension Mechanisms

### Beancount: Python Plugins
- Full access to parsed data
- Can generate new transactions
- Can modify existing entries
- Run at load time

```python
def my_plugin(entries, options):
    new_entries = []
    for entry in entries:
        # Process and potentially modify
        new_entries.append(entry)
    return new_entries, []
```

### Ledger: Value Expressions
- Inline computation
- Query-time evaluation
- No file modification

```ledger
= /Expenses:Food/
    (Budget:Food)    (amount * 1)
```

### hledger: Multiple Approaches
- Auto postings (like Ledger)
- External tools for transforms
- CSV rules for imports

## Query Philosophy

### Beancount: SQL-like (BQL)
- Familiar SQL syntax
- Full query language
- Aggregation and grouping

```sql
SELECT account, sum(position)
WHERE account ~ 'Expenses'
GROUP BY account
ORDER BY sum(position) DESC
```

### Ledger: Filter Expressions
- Command-line focused
- Expression language
- Inline with reports

```bash
ledger balance Expenses --limit "amount > 100"
```

### hledger: Simple Filters
- Command-line patterns
- Multiple filter types
- Composable

```bash
hledger balance expenses amt:'>100'
```

## Error Messages

### Beancount
- Precise line/column info
- Structured error format
- Clear problem description

```
file.beancount:15: Invalid account name
  Assets:Invalid Name
        ^
```

### Ledger
- Line numbers
- Context shown
- Can be cryptic

### hledger
- Clear, friendly messages
- Suggestions when possible
- Good for beginners

```
hledger: account "Assets:Foo" not declared
Perhaps you meant: Assets:Food
```

## Community & Development

### Beancount
- Mailing list focused
- Conservative changes
- Strong documentation
- Fava (web UI) community

### Ledger
- GitHub issues
- Long history
- Many forks/variants
- Extensive documentation

### hledger
- Active GitHub
- Regular releases
- Growing documentation
- Web UI included

## Use Case Fit

| Use Case | Best Fit | Why |
|----------|----------|-----|
| Personal finance | All three | Simple needs |
| Business accounting | Beancount | Strict validation |
| Quick tracking | Ledger/hledger | No setup needed |
| Extensibility | Beancount | Python plugins |
| Compatibility | hledger | Reads both formats |
| Performance | Ledger | C++ speed |
| Web interface | Beancount/hledger | Fava / hledger-web |

## Summary

| Aspect | Beancount | Ledger | hledger |
|--------|-----------|--------|---------|
| Philosophy | Correctness | Power | Practicality |
| Strictness | Required | Optional | Configurable |
| Learning curve | Medium | Steep | Gentle |
| Flexibility | Lower | Highest | Medium |
| Reliability | Highest | Medium | High |
| Extensions | Plugins | Expressions | Tools |

## See Also

- [Syntax Comparison](syntax.md)
- [Feature Comparison](features.md)
