# Issue Draft: Amount Elision Rule Clarification

**Repository:** pta-standards
**Labels:** spec-clarification, beancount-v3, undefined

---

## Title

[beancount-v3] Clarify amount elision rule: one per currency or one total?

## Body

### Spec Reference

- `formats/beancount/v3/spec/posting.md` - Amount Elision section
- `formats/beancount/v3/spec/validation/balance.md` - Interpolation Algorithm

### Current Status

Marked as **UNDEFINED** in the spec.

### Question

When a transaction has multiple currencies, how many postings can omit their amount?

**Option A: One per currency**
```beancount
2024-01-15 * "Multi-currency"
  Assets:EUR        100 EUR
  Assets:USD        110 USD
  Income:Gift:EUR             ; = -100 EUR
  Income:Gift:USD             ; = -110 USD
```

**Option B: One total**
```beancount
2024-01-15 * "Multi-currency"
  Assets:EUR        100 EUR
  Assets:USD        110 USD
  Income:Gift                 ; Expands to: -100 EUR AND -110 USD
```

### Python Beancount Behavior

Python beancount 3.2.0 implements **Option B**:
- Only one auto-posting allowed per transaction
- The single posting expands to cover all currencies
- Error: `CategorizationError: You may not have more than one auto-posting per currency`
- Note: Error message says "per currency" but behavior is "one total"

### Discussion

Which should be the normative behavior for the spec?

- Option A is more flexible
- Option B is simpler and current implementation
- The error message suggests Option A was intended?

### Resolution Needed

Once consensus is reached here, we will:
1. Update the spec to document the normative behavior
2. File upstream issue if clarification from beancount maintainers is needed
