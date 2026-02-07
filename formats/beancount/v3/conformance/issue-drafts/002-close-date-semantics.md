# Issue Draft: Close Date Semantics

**Repository:** pta-standards
**Labels:** spec-clarification, beancount-v3, undefined

---

## Title

[beancount-v3] Clarify close date semantics: is posting ON close date allowed?

## Body

### Spec Reference

- `formats/beancount/v3/spec/validation/accounts.md` - Account Closed section

### Current Status

Marked as **UNDEFINED** in the spec.

### Question

When an account is closed on a given date, can transactions occur on that same date?

**Option A: Inclusive (close at end of day)**
```beancount
2023-12-31 close Assets:Account

2023-12-31 * "Final transaction"
  Assets:Account   100 USD    ; ALLOWED - same day as close
  Income:Salary

2024-01-01 * "After close"
  Assets:Account   100 USD    ; ERROR - after close
  Income:Salary
```

**Option B: Exclusive (close at start of day)**
```beancount
2023-12-31 close Assets:Account

2023-12-31 * "Same day"
  Assets:Account   100 USD    ; ERROR - on or after close
  Income:Salary
```

### Python Beancount Behavior

Python beancount 3.2.0 implements **Option A**:
- Posting ON the close date is allowed
- Only postings AFTER the close date produce an error
- Semantic interpretation: "closed at end of day"

### Discussion

Which should be the normative behavior?

- Option A allows final transactions on the close date
- Option B is stricter and unambiguous
- Most real-world use: close at year-end, may have year-end transactions

### Resolution Needed

Once consensus is reached here, we will:
1. Update the spec to document the normative behavior
2. File upstream issue if clarification from beancount maintainers is needed
