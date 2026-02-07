# Issue Draft: Close with Non-Zero Balance

**Repository:** pta-standards
**Labels:** spec-clarification, beancount-v3, undefined

---

## Title

[beancount-v3] Clarify: should closing account with non-zero balance produce error?

## Body

### Spec Reference

- `formats/beancount/v3/spec/validation/accounts.md` - Account Close with Non-Zero Balance

### Current Status

Marked as **UNDEFINED** in the spec.

### Question

Should closing an account that still has a balance produce an error?

```beancount
2024-01-01 open Assets:Checking USD

2024-06-15 * "Deposit"
  Assets:Checking  1000 USD
  Income:Salary

2024-12-31 close Assets:Checking
; Account has 1000 USD balance - what should happen?
```

### Options

1. **Allow silently** - No error or warning
2. **Warning** - Allow but produce a warning
3. **Error** - Must have zero balance to close

### Python Beancount Behavior

Python beancount 3.2.0 implements **Option 1**:
- Closing with non-zero balance is allowed
- No error or warning is produced

### Discussion

Which should be the normative behavior?

**For allowing (Options 1-2):**
- User may have transferred funds elsewhere
- Account might be intentionally abandoned
- Balance may be tracked in a different system

**For requiring zero (Option 3):**
- Catches mistakes (forgot to transfer funds)
- Forces explicit handling of remaining balance
- More rigorous bookkeeping

### Resolution Needed

Once consensus is reached here, we will:
1. Update the spec to document the normative behavior
2. File upstream issue if clarification from beancount maintainers is needed
