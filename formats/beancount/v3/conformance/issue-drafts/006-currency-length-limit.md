# Issue Draft: Currency Name Length Limit

**Repository:** pta-standards
**Labels:** spec-clarification, beancount-v3, undefined

---

## Title

[beancount-v3] Clarify: is there a maximum length for currency/commodity names?

## Body

### Spec Reference

- `formats/beancount/v3/spec/lexical.md` - Currency Token
- `formats/beancount/v3/spec/validation/commodities.md` - Commodity Validation

### Current Status

Marked as **UNDEFINED** in the spec.

### Question

Is there a maximum length for currency/commodity names?

```beancount
; This is accepted in Python beancount (31 characters)
2024-01-01 commodity VERYLONGCURRENCYNAMEFORTESTING

2024-01-01 open Assets:Test VERYLONGCURRENCYNAMEFORTESTING
```

### Options

1. **No limit (current)** - Any length is allowed
2. **24 characters** - Enforce historically documented limit
3. **Other limit** - Specify a different maximum
4. **Recommended limit** - No enforcement but recommend a maximum for interoperability

### Python Beancount Behavior

Python beancount 3.2.0 implements **Option 1**:
- No maximum length is enforced
- Currency names of any length are accepted
- Older documentation mentioned 24-character limit but this is not enforced

### Discussion

Which should be the normative behavior?

**For no limit (Option 1):**
- Maximum flexibility
- No breaking change to existing ledgers
- Current implementation behavior

**For enforcing a limit (Options 2-3):**
- Shorter names are more practical for display
- Some external systems may have length limits
- Very long names cause display/formatting issues

**For recommended limit (Option 4):**
- Balance between flexibility and practicality
- Implementation MAY warn but not error
- Interoperability guidance without enforcement

### Resolution Needed

Once consensus is reached here, we will:
1. Update the spec to document the normative behavior
2. File upstream issue if clarification from beancount maintainers is needed
