# Tree-sitter Grammar Tests

This directory contains conformance tests for the Beancount v3 tree-sitter grammar.

## Test Format

Tests use the standard tree-sitter corpus format. Each `.txt` file in `corpus/` contains multiple test cases:

```
================================================================================
Test name
================================================================================

input source code

--------------------------------------------------------------------------------

(expected_syntax_tree)
```

## Test Files

| File | Coverage |
|------|----------|
| `directives.txt` | All 12 directive types (open, close, balance, pad, commodity, price, event, note, document, query, custom) |
| `transactions.txt` | Transaction variations: flags, payees, tags, links, costs, prices, comments |
| `metadata.txt` | Directive and posting metadata with all value types |
| `meta_directives.txt` | Option, include, plugin, pushtag/poptag, pushmeta/popmeta |
| `primitives.txt` | Dates, accounts, currencies, numbers, strings, tags, links, booleans |
| `comments.txt` | Comment syntax and placement |
| `edge_cases.txt` | Complex and edge-case scenarios |

## Running Tests

### Using tree-sitter CLI

```bash
# Install tree-sitter CLI
npm install -g tree-sitter-cli

# Generate parser from grammar
cd formats/beancount/v3/tree-sitter
tree-sitter generate

# Run tests
tree-sitter test
```

### Using npm scripts (if package.json exists)

```bash
npm test
```

## Test Coverage

The test corpus covers:

### Directives (16 tests)
- Open with currencies and booking methods
- Close
- Balance with tolerance
- Pad
- Commodity with metadata
- Price
- Event
- Note
- Document
- Query
- Custom with various value types

### Transactions (15 tests)
- Flag variations (*, !, txn, P, #)
- Payee and narration
- Tags and links
- Posting flags
- Per-unit and total costs
- Cost with date and label
- Price annotations (@ and @@)
- Cost and price combined

### Metadata (10 tests)
- String, date, amount, number, boolean, tag, account values
- Directive-level metadata
- Posting-level metadata

### Meta Directives (10 tests)
- Option
- Include
- Plugin with and without config
- Pushtag/poptag
- Pushmeta/popmeta

### Primitives (30 tests)
- Date formats (hyphen, slash)
- Account roots (Assets, Liabilities, Equity, Income, Expenses)
- Account components with digits, hyphens
- Currency patterns (letters, numbers, dots, underscores, apostrophes)
- Number formats (integer, decimal, negative, thousands, leading decimal)
- String escapes
- Tags and links with various characters
- Booleans (TRUE, FALSE)

### Comments (8 tests)
- Standalone comments
- Comments after directives
- Unicode in comments

### Edge Cases (14 tests)
- Empty cost spec
- Wildcard cost matching
- Transaction without narration
- Deep account hierarchy
- Complex transactions with all features
- Full ledger structure

## Adding New Tests

1. Add test cases to the appropriate corpus file
2. Use the standard format with separators
3. Ensure the expected S-expression matches tree-sitter output
4. Run `tree-sitter test` to verify

## Test Validation

To validate a specific test:

```bash
# Parse a file and show the syntax tree
tree-sitter parse examples/test.beancount

# Compare with expected output
tree-sitter test -f "Test name"
```
