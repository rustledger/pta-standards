# Issue Drafts

This directory contains draft issues for undefined specification items.

## Workflow

```
1. File issue in pta-standards repo
   ├── Discuss and validate the question
   ├── Gather community input
   └── Refine understanding of the problem

2. Once validated, file consolidated issue in upstream repo
   └── beancount/beancount (or other project)

3. When upstream responds, update spec
   ├── Remove UNDEFINED marker
   ├── Document the clarified behavior
   └── Update conformance file
```

## Status

| # | Topic | Draft Ready | pta-standards Issue | Upstream Issue | Resolved |
|---|-------|-------------|---------------------|----------------|----------|
| 1 | Amount elision rule | ✓ | - | - | No |
| 2 | Close date semantics | ✓ | - | - | No |
| 3 | Close with non-zero balance | ✓ | - | - | No |
| 4 | Empty transaction validity | ✓ | - | - | No |
| 5 | Duplicate metadata behavior | ✓ | - | - | No |
| 6 | Currency name length limit | ✓ | - | - | No |

## Draft Files

| File | Topic |
|------|-------|
| `001-amount-elision-rule.md` | One posting per currency vs one total |
| `002-close-date-semantics.md` | Posting ON close date allowed? |
| `003-close-with-balance.md` | Non-zero balance when closing |
| `004-empty-transactions.md` | Transactions with no postings |
| `005-duplicate-metadata.md` | Duplicate metadata key behavior |
| `006-currency-length-limit.md` | Maximum currency name length |

## Labels for pta-standards Issues

- `spec-clarification` - Needs clarification from upstream
- `beancount-v3` - Beancount v3 specification
- `undefined` - Currently marked UNDEFINED in spec

## Notes

- Validate thoroughly before filing upstream
- Batch related questions into single upstream issues where appropriate
- Reference pta-standards discussion in upstream issue
