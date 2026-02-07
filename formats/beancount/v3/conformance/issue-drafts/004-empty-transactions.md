# Issue Draft: Empty Transaction Validity

**Repository:** pta-standards
**Labels:** spec-clarification, beancount-v3, undefined

---

## Title

[beancount-v3] Clarify: should transactions with no postings be valid?

## Body

### Spec Reference

- `formats/beancount/v3/spec/transaction.md` - Transaction Structure
- `formats/beancount/v3/spec/validation/balance.md` - Balance Validation

### Current Status

Marked as **UNDEFINED** in the spec.

### Question

Should a transaction with zero postings be considered valid?

```beancount
2024-01-15 * "Empty transaction"
; No postings at all
```

### Options

1. **Allow (current)** - Empty transactions are valid (sum of nothing is zero)
2. **Error** - Transactions MUST have at least one posting
3. **Error** - Transactions MUST have at least two postings (to be meaningful)
4. **Warning** - Allow but produce a warning

### Python Beancount Behavior

Python beancount 3.2.0 implements **Option 1**:
- Empty transactions are accepted
- No error or warning is produced
- The transaction trivially balances (sum of zero postings is zero)

### Discussion

Which should be the normative behavior?

**For allowing (Option 1):**
- Useful as placeholders during editing
- Some tools may generate them as intermediate states
- Trivially satisfies balance requirements

**For requiring postings (Options 2-3):**
- Empty transactions are almost certainly user errors
- Forces meaningful transactions
- More rigorous bookkeeping

### Resolution Needed

Once consensus is reached here, we will:
1. Update the spec to document the normative behavior
2. File upstream issue if clarification from beancount maintainers is needed
