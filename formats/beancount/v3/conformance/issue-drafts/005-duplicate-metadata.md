# Issue Draft: Duplicate Metadata Behavior

**Repository:** pta-standards
**Labels:** spec-clarification, beancount-v3, undefined

---

## Title

[beancount-v3] Clarify: what should happen with duplicate metadata keys?

## Body

### Spec Reference

- `formats/beancount/v3/spec/metadata.md` - Metadata Handling

### Current Status

Marked as **UNDEFINED** in the spec.

### Question

When the same metadata key appears multiple times on a directive, what should happen?

```beancount
2024-01-15 * "Purchase"
  category: "office"
  category: "supplies"    ; Duplicate key - what happens?
  Assets:Checking  -100 USD
  Expenses:Office
```

### Options

1. **Error (current)** - Duplicate keys produce a parser error
2. **Last wins** - Silently use the last value
3. **First wins** - Silently use the first value (and discard later)
4. **List** - Collect all values into a list
5. **Warning** - Allow but produce a warning

### Python Beancount Behavior

Python beancount 3.2.0 implements **Option 1**:
- Duplicate metadata keys produce a parser error
- Error type: `ParserError`
- The first value is retained in the parsed output
- Processing continues after the error

### Discussion

Which should be the normative behavior?

**For error (Option 1):**
- Catches copy-paste mistakes
- Forces explicit intent
- Avoids ambiguity

**For allowing (Options 2-5):**
- May be useful for overriding metadata from includes
- List semantics could enable tags-like metadata
- More forgiving of input

### Resolution Needed

Once consensus is reached here, we will:
1. Update the spec to document the normative behavior
2. File upstream issue if clarification from beancount maintainers is needed
