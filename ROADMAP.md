# PTA Spec Roadmap

This document outlines the planned structure for a comprehensive Plain Text Accounting specification project.

```
pta-spec/
│
├── README.md                           # Project overview, quick links, badges
├── LICENSE                             # CC-BY-4.0 for docs, MIT for code
├── CONTRIBUTING.md                     # Contribution guide with CLA
├── GOVERNANCE.md                       # Decision-making process, maintainers
├── SECURITY.md                         # Security policy, reporting vulnerabilities
├── CODE_OF_CONDUCT.md                  # Community standards
│
│
│   ════════════════════════════════════════════════════════════════════════
│   META: Project governance, process, decisions
│   ════════════════════════════════════════════════════════════════════════
│
├── meta/
│   ├── README.md                       # About the meta/ directory
│   │
│   ├── rfcs/                           # Request for Comments (major changes)
│   │   ├── README.md                   # RFC process explanation
│   │   ├── 0000-template.md            # RFC template
│   │   └── accepted/                   # Accepted RFCs (moved here)
│   │
│   ├── adrs/                           # Architecture Decision Records
│   │   ├── README.md                   # ADR format and index
│   │   ├── 0001-three-separate-specs.md
│   │   ├── 0002-alloy-over-tlaplus.md
│   │   ├── 0003-ebnf-plus-abnf.md
│   │   ├── 0004-json-schema-2020-12.md
│   │   ├── 0005-tree-sitter-primary.md
│   │   └── template.md
│   │
│   └── process/
│       ├── versioning.md               # Semantic versioning policy
│       ├── releases.md                 # Release process and cadence
│       ├── deprecation.md              # How features get deprecated
│       └── breaking-changes.md         # When breaking changes allowed
│
│
│   ════════════════════════════════════════════════════════════════════════
│   CORE: Shared foundations used by all formats
│   ════════════════════════════════════════════════════════════════════════
│
├── core/
│   ├── README.md                       # Core concepts overview
│   │
│   ├── conventions/
│   │   ├── rfc2119.md                  # MUST/SHALL/SHOULD definitions
│   │   ├── notation.md                 # Grammar notation guide
│   │   └── stability-markers.md        # 🟢stable 🟡experimental 🔴deprecated
│   │
│   ├── model/                          # Universal data model
│   │   ├── README.md                   # Data model overview
│   │   ├── journal.md                  # What is a journal
│   │   ├── transaction.md              # Transaction concept
│   │   ├── posting.md                  # Posting concept
│   │   ├── account.md                  # Account model, hierarchy
│   │   ├── commodity.md                # Commodity/currency model
│   │   ├── amount.md                   # Number + commodity
│   │   ├── lot.md                      # Lot/cost basis concept
│   │   ├── price.md                    # Market price concept
│   │   └── metadata.md                 # Key-value metadata
│   │
│   ├── types/                          # Primitive type specifications
│   │   ├── README.md                   # Type system overview
│   │   ├── decimal.md                  # Arbitrary precision decimals
│   │   ├── decimal.als                 # Alloy model for decimal math
│   │   ├── date.md                     # Date handling
│   │   ├── string.md                   # String encoding, escaping
│   │   └── unicode.md                  # UTF-8, normalization, BOM
│   │
│   ├── numerics/                       # Numeric computation rules
│   │   ├── README.md                   # Numeric handling overview
│   │   ├── precision.md                # Minimum precision guarantees
│   │   ├── rounding.md                 # Rounding modes and rules
│   │   └── tolerance.md                # Balance tolerance algorithms
│   │
│   ├── formal/                         # Alloy models (mathematical proofs)
│   │   ├── README.md                   # How to run Alloy, what's verified
│   │   ├── inventory.als               # Inventory tracking invariants
│   │   ├── balance_equation.als        # Assets = Liabilities + Equity
│   │   ├── booking/
│   │   │   ├── fifo.als
│   │   │   ├── lifo.als
│   │   │   ├── hifo.als
│   │   │   ├── average.als
│   │   │   └── specific.als
│   │   └── reports/
│   │       ├── trial_balance.als
│   │       └── balance_sheet.als
│   │
│   ├── i18n/                           # Internationalization
│   │   ├── README.md
│   │   ├── number-formats.md           # 1,234.56 vs 1.234,56
│   │   ├── date-formats.md             # Regional date formats
│   │   └── currency-symbols.md         # Symbol placement
│   │
│   ├── glossary.md                     # Canonical term definitions
│   └── bibliography.md                 # Academic references, prior art
│
│
│   ════════════════════════════════════════════════════════════════════════
│   FORMATS: Individual format specifications
│   ════════════════════════════════════════════════════════════════════════
│
├── formats/
│   │
│   ├── beancount/
│   │   ├── README.md                   # Beancount overview, history
│   │   ├── CHANGELOG.md                # All versions changelog
│   │   │
│   │   ├── v3/
│   │   │   ├── README.md               # v3 overview
│   │   │   │
│   │   │   ├── spec/                   # Normative specification
│   │   │   │   ├── introduction.md
│   │   │   │   ├── lexical.md
│   │   │   │   ├── syntax.md
│   │   │   │   │
│   │   │   │   ├── directives/
│   │   │   │   │   ├── transaction.md
│   │   │   │   │   ├── open.md
│   │   │   │   │   ├── close.md
│   │   │   │   │   ├── balance.md
│   │   │   │   │   ├── pad.md
│   │   │   │   │   ├── commodity.md
│   │   │   │   │   ├── price.md
│   │   │   │   │   ├── event.md
│   │   │   │   │   ├── note.md
│   │   │   │   │   ├── document.md
│   │   │   │   │   ├── query.md
│   │   │   │   │   ├── custom.md
│   │   │   │   │   ├── option.md
│   │   │   │   │   ├── plugin.md
│   │   │   │   │   └── include.md
│   │   │   │   │
│   │   │   │   ├── posting.md
│   │   │   │   ├── amounts.md
│   │   │   │   ├── costs.md
│   │   │   │   ├── prices.md
│   │   │   │   ├── metadata.md
│   │   │   │   ├── tags-links.md
│   │   │   │   │
│   │   │   │   ├── validation/
│   │   │   │   │   ├── balance.md
│   │   │   │   │   ├── accounts.md
│   │   │   │   │   ├── commodities.md
│   │   │   │   │   └── duplicates.md
│   │   │   │   │
│   │   │   │   ├── booking.md
│   │   │   │   ├── tolerances.md
│   │   │   │   ├── includes.md
│   │   │   │   └── errors.md
│   │   │   │
│   │   │   ├── grammar/
│   │   │   │   ├── beancount.ebnf      # ISO 14977 EBNF (source of truth)
│   │   │   │   └── beancount.abnf      # RFC 5234 ABNF
│   │   │   │
│   │   │   ├── schema/
│   │   │   │   ├── ast.schema.json     # JSON Schema 2020-12
│   │   │   │   └── ast.proto           # Protocol Buffers v3
│   │   │   │
│   │   │   ├── tree-sitter/
│   │   │   │   ├── grammar.js
│   │   │   │   ├── package.json
│   │   │   │   └── queries/
│   │   │   │       ├── highlights.scm
│   │   │   │       ├── injections.scm
│   │   │   │       ├── locals.scm
│   │   │   │       ├── folds.scm
│   │   │   │       ├── indents.scm
│   │   │   │       └── textobjects.scm
│   │   │   │
│   │   │   ├── formal/
│   │   │   │   ├── pad.als
│   │   │   │   ├── booking.als
│   │   │   │   └── tolerance.als
│   │   │   │
│   │   │   ├── bql/                    # Beancount Query Language
│   │   │   │   ├── spec.md
│   │   │   │   ├── grammar.ebnf
│   │   │   │   ├── functions.md
│   │   │   │   ├── ast.schema.json
│   │   │   │   └── tree-sitter/
│   │   │   │       └── grammar.js
│   │   │   │
│   │   │   └── migration/
│   │   │       ├── guide.md
│   │   │       └── breaking-changes.md
│   │   │
│   │   ├── v2/                         # Previous version (same structure)
│   │   │
│   │   ├── plugins/
│   │   │   ├── spec.md
│   │   │   ├── hooks.md
│   │   │   └── sandboxing.md
│   │   │
│   │   └── compliance.md
│   │
│   │
│   ├── ledger/
│   │   ├── README.md
│   │   ├── CHANGELOG.md
│   │   │
│   │   ├── v1/
│   │   │   ├── README.md
│   │   │   │
│   │   │   ├── spec/
│   │   │   │   ├── introduction.md
│   │   │   │   ├── lexical.md
│   │   │   │   ├── syntax.md
│   │   │   │   │
│   │   │   │   ├── directives/
│   │   │   │   │   ├── transaction.md
│   │   │   │   │   ├── account.md
│   │   │   │   │   ├── commodity.md
│   │   │   │   │   ├── tag.md
│   │   │   │   │   ├── payee.md
│   │   │   │   │   ├── alias.md
│   │   │   │   │   ├── price.md
│   │   │   │   │   ├── assert.md
│   │   │   │   │   ├── check.md
│   │   │   │   │   ├── default.md
│   │   │   │   │   ├── bucket.md
│   │   │   │   │   ├── year.md
│   │   │   │   │   └── include.md
│   │   │   │   │
│   │   │   │   ├── posting.md
│   │   │   │   ├── amounts.md
│   │   │   │   ├── costs.md
│   │   │   │   ├── lots.md
│   │   │   │   ├── metadata.md
│   │   │   │   ├── tags.md
│   │   │   │   │
│   │   │   │   ├── advanced/
│   │   │   │   │   ├── automated.md    # = automated transactions
│   │   │   │   │   ├── periodic.md     # ~ periodic transactions
│   │   │   │   │   ├── virtual.md      # () and [] postings
│   │   │   │   │   ├── expressions.md  # Value expressions
│   │   │   │   │   └── effective-dates.md
│   │   │   │   │
│   │   │   │   ├── validation/
│   │   │   │   │   ├── balance.md
│   │   │   │   │   └── accounts.md
│   │   │   │   │
│   │   │   │   ├── implicit.md
│   │   │   │   ├── includes.md
│   │   │   │   └── errors.md
│   │   │   │
│   │   │   ├── grammar/
│   │   │   │   ├── ledger.ebnf
│   │   │   │   └── ledger.abnf
│   │   │   │
│   │   │   ├── schema/
│   │   │   │   ├── ast.schema.json
│   │   │   │   └── ast.proto
│   │   │   │
│   │   │   ├── tree-sitter/
│   │   │   │   ├── grammar.js
│   │   │   │   ├── package.json
│   │   │   │   └── queries/
│   │   │   │
│   │   │   ├── formal/
│   │   │   │   ├── virtual.als
│   │   │   │   ├── automated.als
│   │   │   │   └── expressions.als
│   │   │   │
│   │   │   └── expressions/            # Value expression sublanguage
│   │   │       ├── spec.md
│   │   │       ├── grammar.ebnf
│   │   │       └── functions.md
│   │   │
│   │   └── compliance.md
│   │
│   │
│   └── hledger/
│       ├── README.md
│       ├── CHANGELOG.md
│       │
│       ├── v1/
│       │   ├── README.md
│       │   │
│       │   ├── spec/
│       │   │   ├── introduction.md
│       │   │   ├── lexical.md
│       │   │   ├── syntax.md
│       │   │   │
│       │   │   ├── directives/
│       │   │   │   ├── transaction.md
│       │   │   │   ├── account.md
│       │   │   │   ├── commodity.md
│       │   │   │   ├── decimal-mark.md
│       │   │   │   ├── payee.md
│       │   │   │   ├── tag.md
│       │   │   │   └── include.md
│       │   │   │
│       │   │   ├── posting.md
│       │   │   ├── amounts.md
│       │   │   ├── costs.md
│       │   │   ├── metadata.md
│       │   │   ├── tags.md
│       │   │   │
│       │   │   ├── advanced/
│       │   │   │   ├── assertions.md
│       │   │   │   ├── forecasting.md
│       │   │   │   └── auto-postings.md
│       │   │   │
│       │   │   ├── validation/
│       │   │   │
│       │   │   ├── includes.md
│       │   │   └── errors.md
│       │   │
│       │   ├── grammar/
│       │   │   ├── hledger.ebnf
│       │   │   └── hledger.abnf
│       │   │
│       │   ├── schema/
│       │   │   ├── ast.schema.json
│       │   │   └── ast.proto
│       │   │
│       │   ├── tree-sitter/
│       │   │   ├── grammar.js
│       │   │   ├── package.json
│       │   │   └── queries/
│       │   │
│       │   ├── formal/
│       │   │   ├── assertions.als
│       │   │   └── forecast.als
│       │   │
│       │   ├── timedot/                # Timedot sublanguage
│       │   │   ├── spec.md
│       │   │   ├── grammar.ebnf
│       │   │   ├── ast.schema.json
│       │   │   └── tree-sitter/
│       │   │       └── grammar.js
│       │   │
│       │   └── csv-rules/              # CSV import rules
│       │       ├── spec.md
│       │       ├── grammar.ebnf
│       │       ├── ast.schema.json
│       │       └── tree-sitter/
│       │           └── grammar.js
│       │
│       └── compliance.md
│
│
│   ════════════════════════════════════════════════════════════════════════
│   IMPORTS: External format import specifications
│   ════════════════════════════════════════════════════════════════════════
│
├── imports/
│   ├── README.md
│   │
│   ├── csv/
│   │   ├── spec.md
│   │   ├── rules.md
│   │   └── rules.ebnf
│   │
│   ├── ofx/
│   │   ├── spec.md
│   │   └── mapping.md
│   │
│   └── qif/
│       ├── spec.md
│       └── mapping.md
│
│
│   ════════════════════════════════════════════════════════════════════════
│   REPORTS: Standard report format specifications
│   ════════════════════════════════════════════════════════════════════════
│
├── reports/
│   ├── README.md
│   │
│   ├── model/
│   │   ├── balance-sheet.md
│   │   ├── income-statement.md
│   │   ├── trial-balance.md
│   │   ├── register.md
│   │   └── budget.md
│   │
│   ├── schema/
│   │   └── report.schema.json          # JSON output schema
│   │
│   └── formal/
│       ├── balance-sheet.als
│       └── trial-balance.als
│
│
│   ════════════════════════════════════════════════════════════════════════
│   CONVERSIONS: Format-to-format conversion specifications
│   ════════════════════════════════════════════════════════════════════════
│
├── conversions/
│   ├── README.md
│   │
│   ├── matrix.md                       # Feature support matrix
│   ├── loss-matrix.md                  # What's lost in each direction
│   │
│   ├── beancount-ledger/
│   │   ├── spec.md
│   │   └── edge-cases.md
│   │
│   ├── beancount-hledger/
│   │   ├── spec.md
│   │   └── edge-cases.md
│   │
│   ├── ledger-hledger/
│   │   ├── spec.md
│   │   └── edge-cases.md
│   │
│   └── interchange/
│       ├── spec.md                     # Universal interchange format
│       ├── journal.schema.json
│       └── journal.proto
│
│
│   ════════════════════════════════════════════════════════════════════════
│   TESTS: Conformance test suite
│   ════════════════════════════════════════════════════════════════════════
│
├── tests/
│   ├── README.md
│   ├── INTERPRETING.md                 # How to interpret results
│   │
│   ├── harness/
│   │   ├── README.md
│   │   ├── spec.md                     # Test format specification
│   │   ├── test-case.schema.json
│   │   ├── manifest.schema.json
│   │   ├── interface.md                # Implementation interface
│   │   └── runners/
│   │       ├── python/
│   │       │   ├── runner.py
│   │       │   └── requirements.txt
│   │       └── rust/
│   │           ├── src/
│   │           └── Cargo.toml
│   │
│   ├── beancount/
│   │   └── v3/
│   │       ├── manifest.json
│   │       │
│   │       ├── syntax/
│   │       │   ├── valid/
│   │       │   │   ├── minimal/
│   │       │   │   │   ├── empty.beancount
│   │       │   │   │   └── empty.json      # Expected AST
│   │       │   │   ├── transactions/
│   │       │   │   ├── directives/
│   │       │   │   ├── costs/
│   │       │   │   ├── metadata/
│   │       │   │   └── unicode/
│   │       │   │
│   │       │   └── invalid/
│   │       │       ├── lexical/
│   │       │       └── syntax/
│   │       │
│   │       ├── validation/
│   │       │   ├── pass/
│   │       │   └── fail/
│   │       │       ├── unbalanced/
│   │       │       ├── duplicate-open/
│   │       │       └── orphan-close/
│   │       │
│   │       ├── booking/
│   │       │   ├── fifo/
│   │       │   ├── lifo/
│   │       │   └── average/
│   │       │
│   │       ├── bql/
│   │       │   ├── syntax/
│   │       │   └── execution/
│   │       │
│   │       └── regression/
│   │
│   ├── ledger/
│   │   └── v1/
│   │       ├── manifest.json
│   │       ├── syntax/
│   │       ├── validation/
│   │       ├── automated/
│   │       ├── periodic/
│   │       ├── virtual/
│   │       ├── expressions/
│   │       └── regression/
│   │
│   ├── hledger/
│   │   └── v1/
│   │       ├── manifest.json
│   │       ├── syntax/
│   │       ├── validation/
│   │       ├── timedot/
│   │       ├── csv-rules/
│   │       ├── forecast/
│   │       └── regression/
│   │
│   ├── cross-format/
│   │   ├── beancount-ledger/
│   │   ├── ledger-hledger/
│   │   └── roundtrip/
│   │
│   ├── differential/
│   │   ├── README.md
│   │   └── config.json                 # Implementation pairs to compare
│   │
│   └── fuzzing/
│       ├── README.md
│       ├── corpus/
│       │   ├── beancount/
│       │   └── ledger/
│       └── dictionaries/
│           ├── beancount.dict
│           └── ledger.dict
│
│
│   ════════════════════════════════════════════════════════════════════════
│   TOOLING: Tool interface specifications
│   ════════════════════════════════════════════════════════════════════════
│
├── tooling/
│   ├── README.md
│   │
│   ├── cli/
│   │   ├── spec.md
│   │   ├── commands/
│   │   │   ├── parse.md
│   │   │   ├── validate.md
│   │   │   ├── format.md
│   │   │   ├── query.md
│   │   │   ├── convert.md
│   │   │   ├── check.md
│   │   │   └── import.md
│   │   └── exit-codes.md
│   │
│   ├── lsp/
│   │   ├── spec.md
│   │   ├── capabilities.json
│   │   └── extensions/
│   │       ├── balance-preview.md
│   │       ├── account-completion.md
│   │       └── amount-completion.md
│   │
│   ├── errors/
│   │   ├── spec.md
│   │   ├── codes/
│   │   │   ├── beancount.md            # E1xxx
│   │   │   ├── ledger.md               # E2xxx
│   │   │   ├── hledger.md              # E3xxx
│   │   │   └── common.md               # E0xxx
│   │   ├── sarif.schema.json
│   │   └── messages.md                 # Error message style guide
│   │
│   ├── canonical/
│   │   ├── spec.md
│   │   ├── beancount.md
│   │   ├── ledger.md
│   │   └── hledger.md
│   │
│   ├── linting/
│   │   ├── spec.md
│   │   ├── rules/
│   │   │   ├── style.md
│   │   │   ├── correctness.md
│   │   │   └── consistency.md
│   │   └── config.schema.json
│   │
│   ├── wasm/
│   │   ├── spec.md
│   │   └── interface.wit
│   │
│   ├── mcp/
│   │   ├── spec.md
│   │   └── tools.json
│   │
│   └── diff/
│       ├── spec.md
│       └── semantic.md
│
│
│   ════════════════════════════════════════════════════════════════════════
│   SECURITY: Security specifications
│   ════════════════════════════════════════════════════════════════════════
│
├── security/
│   ├── README.md
│   ├── threat-model.md
│   │
│   ├── limits/
│   │   ├── spec.md
│   │   ├── input.md
│   │   ├── nesting.md
│   │   └── memory.md
│   │
│   ├── parsing/
│   │   ├── redos.md
│   │   └── stack-overflow.md
│   │
│   ├── includes/
│   │   ├── path-traversal.md
│   │   ├── symlinks.md
│   │   └── cycles.md
│   │
│   └── plugins/
│       ├── sandboxing.md
│       └── capabilities.md
│
│
│   ════════════════════════════════════════════════════════════════════════
│   CONFORMANCE: Compliance program
│   ════════════════════════════════════════════════════════════════════════
│
├── conformance/
│   ├── README.md
│   │
│   ├── levels/
│   │   ├── overview.md
│   │   ├── level-1-parse.md
│   │   ├── level-2-validate.md
│   │   ├── level-3-query.md
│   │   └── level-4-full.md
│   │
│   ├── process/
│   │   ├── self-certification.md
│   │   ├── test-requirements.md
│   │   └── badge-usage.md
│   │
│   ├── registry.json                   # Machine-readable registry
│   │
│   └── benchmarks/
│       ├── spec.md
│       └── methodology.md
│
│
│   ════════════════════════════════════════════════════════════════════════
│   EXTENSIONS: Community extensions registry
│   ════════════════════════════════════════════════════════════════════════
│
├── extensions/
│   ├── README.md
│   │
│   ├── process/
│   │   ├── proposal.md
│   │   └── graduation.md
│   │
│   ├── registry.json
│   │
│   └── catalog/
│       └── template/
│           ├── README.md
│           ├── spec.md
│           └── grammar.ebnf
│
│
│   ════════════════════════════════════════════════════════════════════════
│   EXAMPLES: Non-normative examples
│   ════════════════════════════════════════════════════════════════════════
│
├── examples/
│   ├── README.md
│   │
│   ├── beancount/
│   │   ├── personal/
│   │   │   ├── journal.beancount
│   │   │   └── README.md
│   │   ├── business/
│   │   ├── investments/
│   │   └── multi-currency/
│   │
│   ├── ledger/
│   │   ├── personal/
│   │   ├── time-tracking/
│   │   └── budgeting/
│   │
│   └── hledger/
│       ├── personal/
│       ├── timedot/
│       └── csv-import/
│
│
│   ════════════════════════════════════════════════════════════════════════
│   REFERENCE: Quick reference materials
│   ════════════════════════════════════════════════════════════════════════
│
├── reference/
│   ├── README.md
│   │
│   ├── cheatsheets/
│   │   ├── beancount.md
│   │   ├── ledger.md
│   │   ├── hledger.md
│   │   └── conversion.md
│   │
│   ├── comparison/
│   │   ├── syntax.md
│   │   ├── features.md
│   │   └── philosophy.md
│   │
│   └── faq.md
│
│
│   ════════════════════════════════════════════════════════════════════════
│   RATIONALE: Design rationale (non-normative)
│   ════════════════════════════════════════════════════════════════════════
│
├── rationale/
│   ├── README.md
│   ├── history.md
│   ├── design-principles.md
│   ├── why-three-specs.md
│   ├── grammar-format.md
│   ├── schema-format.md
│   ├── formal-methods.md
│   └── test-philosophy.md
│
│
│   ════════════════════════════════════════════════════════════════════════
│   IMPLEMENTATIONS: Implementation guidance
│   ════════════════════════════════════════════════════════════════════════
│
├── implementations/
│   ├── README.md
│   │
│   ├── guide/
│   │   ├── getting-started.md
│   │   ├── parser.md
│   │   ├── validator.md
│   │   ├── error-messages.md
│   │   ├── incremental.md
│   │   └── performance.md
│   │
│   └── registry.json                   # Known implementations
│
│
│   ════════════════════════════════════════════════════════════════════════
│   BUILD: Build system and CI
│   ════════════════════════════════════════════════════════════════════════
│
├── build/
│   ├── README.md
│   ├── Makefile
│   │
│   ├── deps/
│   │   ├── package.json
│   │   ├── requirements.txt
│   │   └── Cargo.toml
│   │
│   ├── scripts/
│   │   ├── build-docs.py
│   │   ├── validate-grammars.py
│   │   ├── validate-schemas.py
│   │   ├── generate-railroad.py        # Generates to dist/
│   │   ├── generate-types.py           # Generates to dist/
│   │   ├── run-alloy.sh
│   │   ├── run-tests.py
│   │   └── check-links.py
│   │
│   └── templates/
│       └── spec.typ
│
│
│   ════════════════════════════════════════════════════════════════════════
│   CI/CD
│   ════════════════════════════════════════════════════════════════════════
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   ├── spec_clarification.yml
│   │   └── test_case.yml
│   │
│   ├── PULL_REQUEST_TEMPLATE.md
│   │
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── validate-grammars.yml
│   │   ├── validate-schemas.yml
│   │   ├── conformance-tests.yml
│   │   ├── run-alloy.yml
│   │   ├── build-docs.yml
│   │   └── check-links.yml
│   │
│   ├── CODEOWNERS
│   └── dependabot.yml
│
│
│   ════════════════════════════════════════════════════════════════════════
│   CONFIG
│   ════════════════════════════════════════════════════════════════════════
│
├── .editorconfig
├── .gitignore
├── .gitattributes
└── .markdownlint.json
```

## What Was Removed

| Removed | Reason |
|---------|--------|
| `schema/generated/` (ast.ts, ast.rs, ast.py, etc.) | Generated from JSON Schema / Protobuf |
| `grammar/railroad/` | Generated from EBNF |
| `reference/cheatsheets/*.pdf` | Generated from markdown |
| `dist/` entirely | All build output |
| `ast.cue` | Redundant with JSON Schema |
| `playground/` | Generated/deployed separately |
| `tree-sitter/corpus/` | Generated during tree-sitter test |
| `meta/meetings/` | Not essential, can use GitHub discussions |

## Source of Truth Hierarchy

```
EBNF grammar (source) ──► ABNF (hand-written alternate)
                     ──► Tree-sitter grammar.js (hand-written, different structure)
                     ──► Railroad diagrams (generated)

JSON Schema (source) ──► Protobuf (hand-written alternate for performance)
                     ──► TypeScript/Rust/Python types (generated)

Markdown specs (source) ──► HTML (generated)
                        ──► PDF (generated)
```

## File Count (Source Only)

```
├── ~30 meta/governance files
├── ~35 core foundation files
├── ~60 files per format × 3 = ~180
├── ~15 import format files
├── ~12 report format files
├── ~20 conversion files
├── ~400+ test files (source, not generated)
├── ~40 tooling spec files
├── ~15 security files
├── ~15 conformance files
├── ~12 extension system files
├── ~25 example files
├── ~12 reference files
├── ~10 rationale files
├── ~10 implementation guide files
├── ~20 build/CI files
────────────────────────────
Total: ~850 source files
```
