# ADR 0006: Enterprise/Regulated Scope with Layered Semantic Model

## Status

Proposed

## Context

### The current spec is a file format, not an accounting standard

The pta-standards repository today specifies three plain-text accounting
file formats (Beancount v3, Ledger v1, hledger v1) at the level of tokens,
grammar, directives, and parser behavior. It is a high-quality _serialization_
specification.

It is **not** an accounting standard. It:

- Defines account roots (`Assets`, `Liabilities`, `Equity`, `Income`, `Expenses`)
  as bare strings with no reference to any framework. There is no concept of
  subtype (current vs non-current, contra accounts), normal balance
  (debit-normal vs credit-normal), or mapping to XBRL taxonomies.
- Requires currency tokens to be "2+ character uppercase strings" without
  referencing ISO 4217. There is no minor-unit specification.
- Describes booking methods (FIFO, LIFO, HIFO, AVERAGE, STRICT) without
  citing IAS 2, ASC 330, or IRS cost basis rules, and without noting that
  LIFO is prohibited under IFRS.
- Has no concept of fiscal periods, period close, closing entries, opening
  balances, adjusting entries, reversing entries, or reclassification entries.
- Does not specify how to derive financial statements (Balance Sheet,
  Income Statement, Cash Flow, Statement of Changes in Equity).
- Does not reference GAAP (ASC), IFRS (IAS/IFRS), XBRL taxonomies, SAF-T,
  OFX, ISO 20022, or any other regulatory standard.
- Provides no mechanism for multi-entity consolidation, intercompany
  eliminations, or currency translation per IAS 21.
- Has no audit trail, immutability, or period-close enforcement model.
  "Undefined behavior" appears repeatedly in the validation specs.

As a result, an implementer conformant to the current spec can produce a
file that parses and validates correctly but is not usable for any regulated
purpose — tax filing, financial statement preparation, audit, or statutory
reporting.

### The opportunity

Plain-text double-entry accounting is a more elegant representation of
bookkeeping than most commercial alternatives. Git gives us natural audit
trails. Text is diffable, grep-able, and archival-friendly. The core format
is fundamentally compatible with rigorous accounting — the only thing
missing is the formal semantic layer that ties it to accepted standards.

No other open, community-maintained standard targets this space. XBRL is
powerful but too verbose for daily bookkeeping. Proprietary formats (QIF,
QFX) are consumer-grade. ERP systems (SAP, Oracle, NetSuite) are closed.
SAF-T is export-only, not a working format.

pta-standards can fill this gap: **plain text for everyday use, formal
semantics for regulatory compliance, open source and vendor-neutral.**

## Decision

We will **target enterprise/regulated-grade accounting** as the scope of
pta-standards, implemented via a **layered specification architecture**.

### Layered architecture

The specification is organized into four layers. Each layer has its own
normative document, its own conformance tests, and its own independent
evolution.

```
Layer 4: Regulatory Output
  XBRL GL mapping, SAF-T profiles, iXBRL generation, tax filings
           ↑ (derived from)
Layer 3: Reporting & Consolidation
  Fiscal periods, closing entries, financial statements,
  multi-entity consolidation, currency translation (IAS 21)
           ↑ (derived from)
Layer 2: Accounting Semantic Model
  Account types with subtypes & normal balance, XBRL taxonomy mapping,
  debit/credit semantics, cost basis methods (IAS 2/ASC 330),
  audit trail model, immutability after close
           ↑ (serialized to)
Layer 1: Concrete Syntax
  Beancount v3, Ledger v1, hledger v1 text formats
  (the current spec, substantially unchanged)
```

**Key property**: Layer 1 remains a faithful specification of the existing
text formats. Nothing in Layer 1 breaks today. Layers 2-4 are _added above_
it, not bolted into it. An implementation targeting only Layer 1 remains
valid as a "syntax-conformant" implementation.

**Conformance levels** extend to reflect the layered model:

| Level | Scope | Current status |
|-------|-------|----------------|
| L1 | Parses syntax, enforces balance | Existing levels 1-2 |
| L2 | Implements full semantic model with XBRL typing | New |
| L3 | Generates financial statements, supports period close | New |
| L4 | Produces regulatory output (XBRL, SAF-T, tax filings) | New |

Implementations self-certify against the level they target. Python beancount
and rustledger are currently L1 implementations.

### Relationship to the existing ROADMAP

The project `ROADMAP.md` already envisions a `core/model/` directory with
documents for `account.md`, `transaction.md`, `posting.md`, `lot.md`,
`price.md`, etc., plus `core/formal/` with Alloy models for
`balance-equation.als`, `trial-balance.als`, and `balance-sheet.als`.
This provides structural scaffolding for Layer 2.

What the ROADMAP does **not** specify — and what this ADR adds — is:

- **The explicit enterprise/regulated scope decision.** The ROADMAP is
  scope-neutral; this ADR commits to a scope.
- **External standards references.** The ROADMAP's `core/model/account.md`
  is unspecified; this ADR says it MUST reference XBRL taxonomies,
  define normal balances, and map to GAAP/IFRS account classifications.
- **Fiscal periods, closing entries, and financial statement derivation.**
  Not mentioned in the ROADMAP at all.
- **Multi-entity consolidation.** Not in the ROADMAP.
- **Regulatory output layer (XBRL, SAF-T, iXBRL).** Not in the ROADMAP.
- **Audit trail and immutability model.** Not in the ROADMAP.
- **A phased implementation plan with external-standard citations.**

Implementation of this ADR should use the ROADMAP's directory structure
where it aligns (especially `core/model/` and `core/formal/`) rather
than creating parallel structures.

### Normative references

All four layers cite external standards rather than reinventing them:

- **ISO 4217** — currency codes, minor units
- **ISO 8601** — dates, fiscal period expressions
- **ISO 10383 MIC** — market identifiers for securities
- **ISO 20022** — payment messaging (camt.053/camt.052 for statement import)
- **IFRS (IAS/IFRS standards)** — IAS 1 (presentation), IAS 2 (inventory),
  IAS 7 (cash flow), IAS 21 (foreign currency), IAS 27/IFRS 10 (consolidation)
- **US GAAP (FASB ASC)** — ASC 205 (presentation), ASC 210 (balance sheet),
  ASC 225 (income statement), ASC 230 (cash flow), ASC 330 (inventory),
  ASC 830 (foreign currency), ASC 810 (consolidation)
- **XBRL International** — XBRL 2.1 core, XBRL GL taxonomy, US GAAP Taxonomy,
  IFRS Taxonomy, iXBRL
- **OECD SAF-T** — Standard Audit File for Tax (country profiles as they
  become relevant)
- **RFC 2119 / RFC 8174** — requirement level keywords (MUST/SHOULD/MAY)
- **Pacioli, _Summa de Arithmetica_ (1494)** — origin of double-entry method

### Scope decisions

**In scope:**

- Everything needed to produce audit-ready books under GAAP or IFRS for
  a single entity, including multi-currency, cost basis tracking, period
  close, and financial statements.
- Mapping to and from XBRL taxonomies for financial reporting.
- Consolidation of multiple entities under a common parent.
- Audit trail and immutability guarantees sufficient for SOX Section 404
  and equivalent regulatory regimes.
- SAF-T export profiles for jurisdictions where SAF-T is required.
- Reference mappings from bank statement interchange formats (OFX,
  camt.053) to the transaction model.

**Out of scope:**

- Payroll computation (too jurisdictionally varied; model accommodates
  payroll postings as ordinary transactions).
- Tax computation (same reason; model accommodates tax postings but
  does not compute liability).
- Budgeting and forecasting beyond what current `event` directives support.
- UI/UX for editing; the spec is format-only.
- Enforcement of internal controls (segregation of duties, approval
  workflows); the spec provides an audit-trail substrate but leaves
  controls to implementations.

## Consequences

### Positive

- **Meaningful to accountants.** A CPA can read the spec and recognize
  the concepts. Adoption conversations become possible with professional
  firms.
- **Regulatory pathway.** Implementations can generate XBRL/SAF-T directly
  from conformant files, opening use cases impossible with the current spec.
- **Reference authority.** pta-standards becomes the authoritative open
  standard for text-based accounting, not "the community cleanup of
  Beancount's undocumented behavior."
- **Clean separation of concerns.** Layer 1 evolves on its own schedule
  for PTA hobbyist use cases; Layers 2-4 evolve for the enterprise track.
- **Community expansion.** Attracts accounting professionals, auditors,
  and regulatory/compliance contributors who would not engage with a
  pure syntax specification.
- **Future-proof.** When regulators require machine-readable books
  (already happening in EU via ESEF, LT/PT via SAF-T, expanding
  globally), pta-standards has a migration story.

### Negative

- **Massive scope increase.** Current spec is ~40 documents. Full
  enterprise scope likely triples that. Multi-year effort.
- **Conceptual errors cost credibility.** Anything wrong about GAAP or
  IFRS will be caught immediately by professional readers. Raises the
  bar for every change.
- **Community friction possible.** The plain-text accounting community
  values minimalism. Some may see this as overreach or scope creep.
  Mitigation: Layer 1 is unchanged, so minimalism is preserved for
  users who want only that.
- **Reference implementation gap.** Neither Python beancount nor
  rustledger implements Layers 2-4 today. The spec cannot be validated
  until at least one reference implementation exists.
- **Regulatory engagement required.** Formal recognition by FASB, IASB,
  national regulators, or auditor bodies (AICPA, ACCA, IFAC) takes years
  of relationship-building and is not guaranteed. XBRL International
  took 11 years from founding (1998) to SEC adoption (2009).
- **Requires sustained authorship effort.** A part-time volunteer
  cannot carry this alone. Needs either full-time maintainer(s) or a
  committed working group with funded time.

### Neutral

- **Version numbering.** Layer 1 remains beancount v3 / ledger v1 /
  hledger v1. Layers 2-4 are versioned independently starting at 0.1.
- **Repository layout.** New top-level `semantics/` directory for Layer 2,
  `reporting/` for Layer 3, and `regulatory/` for Layer 4. `formats/`
  stays as Layer 1.
- **Governance.** Existing governance model (RFC process, ADRs, lazy
  consensus) scales; layer-specific stewardship may be added later.
- **Test infrastructure.** Existing conformance harness extends
  naturally to new layers; each layer has its own test suite.

## Alternatives considered

### A. Stay with personal-finance scope

Keep the current spec as-is, add only short-term improvements (ISO 4217
reference, IAS 2 citation in booking.md). Write nothing about fiscal
periods, financial statements, or regulatory output.

**Rejected because**: the current spec's gaps are not just cosmetic.
"UNDEFINED" appears repeatedly in the validation spec, most of which
would be answered by referencing an accounting standard. Staying at
this scope means the spec never resolves those questions and remains
unusable for any non-hobbyist purpose.

### B. Small-business scope (middle ground)

Add fiscal periods, closing entries, and basic financial statements, but
stop short of XBRL/SAF-T and consolidation.

**Rejected because**: the hard architectural work is the semantic layer
itself. Once Layer 2 exists, adding Layer 4 (regulatory output) is
mechanical mapping work, while adding it retroactively to a small-business
spec requires the same semantic refactor. Doing the work once, at the
right scope, is cheaper than doing it twice.

### C. Fork to a new project

Leave pta-standards as the PTA-community-focused spec and start a separate
"enterprise text accounting" project with different governance.

**Rejected because**: fragmenting the community reduces total momentum.
The layered architecture in this ADR preserves PTA-community focus at
Layer 1 while allowing enterprise work above it, so there is no need to
fork. If the community ultimately rejects Layer 2+, the enterprise work
can be re-homed, but starting with fork is premature.

### D. Build on XBRL instead of beancount

Start from XBRL GL as the data model and derive a plain-text serialization
of it, rather than starting from beancount's model and mapping up to XBRL.

**Rejected because**: XBRL GL is too verbose and too low-level to be a
good user-facing format. Its semantic richness is a benefit for output
(regulatory filings) but a liability for daily human-authored bookkeeping.
Starting from the ergonomic format and mapping up preserves usability.

## Implementation roadmap

This roadmap is a sketch. Actual execution will generate more RFCs and ADRs.

### Phase 1: Foundations (3-6 months)

Goal: establish the layered architecture and add short-term improvements
without breaking anything.

- Create `semantics/` directory structure (Layer 2 stub)
- Write `semantics/accounting-model.md` with placeholders for all major
  concepts
- Write `semantics/references.md` with external standard citations
- Add ISO 4217 reference to `formats/beancount/v3/spec/lexical.md`
- Add IAS 2 / ASC 330 reference to `formats/beancount/v3/spec/booking.md`
  including LIFO's IFRS prohibition
- Version conformance levels (L1 existing, L2-L4 reserved)
- **Deliverable**: layered spec structure in place; Layer 1 unchanged

### Phase 2: Account taxonomy (3-6 months)

Goal: specify the full account type model with normal balance, subtypes,
and XBRL mapping.

- Define account subtypes (current/non-current assets and liabilities,
  contra accounts, equity components, revenue/expense classification)
- Define normal balance semantics (debit-normal vs credit-normal)
- Map account types to XBRL US GAAP and IFRS Taxonomy concepts
- Add `account_type` metadata directive for explicit typing where
  automatic classification is insufficient
- Formal Alloy model of the semantic account model
- **Deliverable**: `semantics/accounts.md`, XBRL mapping appendix

### Phase 3: Fiscal periods and close (3-6 months)

Goal: add period definition, closing entries, and opening balance
derivation.

- New directives: `period`, `close-period`, plus adjusting/reversing/
  reclassification entry flags
- Closing entry generation algorithm (temporary accounts to retained
  earnings)
- Trial balance specification
- Opening balance derivation from prior period close
- Period status lifecycle (open → soft-close → hard-close → audited)
- **Deliverable**: `semantics/periods.md`; reference test cases

### Phase 4: Financial statements (3-6 months)

Goal: specify derivation of the four primary financial statements.

- Balance Sheet per ASC 210 / IAS 1 (classified, comparative)
- Income Statement per ASC 225 / IAS 1 (single-step and multi-step)
- Cash Flow Statement per ASC 230 / IAS 7 (direct and indirect)
- Statement of Changes in Equity per IAS 1
- Notes linkage
- **Deliverable**: `reporting/financial-statements.md`

### Phase 5: Consolidation and multi-currency (6 months)

Goal: specify multi-entity consolidation and currency translation.

- Entity directive for identifying books within consolidation scope
- Intercompany transaction and elimination rules
- Consolidation adjustments (minority interest, goodwill)
- Currency translation per IAS 21 / ASC 830 (functional currency,
  monetary vs non-monetary items, translation adjustments to OCI)
- **Deliverable**: `reporting/consolidation.md`

### Phase 6: Audit trail and immutability (6 months)

Goal: specify the audit-grade storage model.

- Append-only change log specification
- Hash chaining for tamper-evidence (Git provides a baseline; specify
  any additional requirements)
- Digital signature scheme for period-close attestation (optional
  but required for some jurisdictions)
- User attribution model
- Change history queries
- **Deliverable**: `semantics/audit-trail.md`

### Phase 7: Regulatory output (ongoing)

Goal: define mappings from the semantic model to regulatory formats.

- XBRL GL taxonomy mapping (general ledger export)
- iXBRL financial statement generation for EDGAR (US) and ESEF (EU)
- SAF-T country profiles (prioritize Portugal as simplest, then Poland,
  Germany, Lithuania)
- ISO 20022 camt.053 / camt.052 import specifications
- Tax filing format mappings (country-specific, as volunteer contributors
  appear)
- **Deliverable**: `regulatory/` directory with one profile per format

### Phase 8: Professional validation (continuous, from Phase 1)

Goal: ensure the spec is actually correct by professional standards.

- Recruit at least one CPA / chartered accountant co-author beyond the
  initial authorship team
- Public RFC process for each layer (4-week comment period, similar to
  IFRS exposure drafts but faster)
- Engagement with XBRL International as a potential member organization
- Relationship-building with FASB, IASB, OECD (SAF-T), national
  regulators as the spec stabilizes
- Real-world validation: at least one organization keeps its actual
  books using a Layer 3+ conformant implementation for a full fiscal
  year and an audit

## Open questions

The following are explicitly left unresolved in this ADR and will be
addressed in follow-up RFCs:

1. **Chart of Accounts authority.** Should pta-standards publish a
   canonical CoA, reference an existing one (e.g., IFRS Taxonomy),
   or remain CoA-agnostic? (Probably the third, with Layer 2 defining
   the _shape_ of a CoA without picking specific accounts.)

2. **Backward compatibility for existing beancount files.** A file
   with bare account names like `Assets:Bank:Checking` must still be
   valid. How is implicit account typing inferred? A conservative
   approach: infer subtype from the first segment only
   (`Assets:*` → current/non-current via heuristic), with explicit
   `account_type` metadata as the override.

3. **Implementation priority order.** Which reference implementation
   (rustledger, a new project, or something else) leads Layer 2+
   implementation? This affects Phase 2 onward.

4. **Versioning relationship to beancount v3.** Is Layer 2+ a new
   beancount v4, or an independent "pta semantic model" that beancount
   v3 conforms to? This ADR assumes the latter (independent layering),
   but a v4 framing may be cleaner.

5. **Conformance self-certification vs. third-party certification.**
   Level 4 in particular raises the question of whether regulators will
   accept self-certification or require independent audit.

6. **Licensing.** The current dual-license (CC BY 4.0 for spec, Apache
   2.0 for code) works for Layer 1. Regulatory mappings may incorporate
   material under XBRL International's license or similar; licensing
   compatibility must be checked per-layer.

## Prior art

A comprehensive survey of the open-source landscape (April 2026) found
that **no existing project combines all seven capabilities** this ADR
targets (formal DEB model, account taxonomy with GAAP/IFRS classification,
XBRL mapping, fiscal periods, financial statement derivation, multi-entity,
audit trail). The closest projects each cover a subset:

### Standards and taxonomies

| Standard | Covers | Gap |
|----------|--------|-----|
| **XBRL GL** (Global Ledger Taxonomy) | Most comprehensive GL taxonomy: CoA, journal entries, AP/AR, inventory, multi-currency | No open-source implementation; taxonomy dormant since 2017 PWD |
| **SAF-T** (OECD) | Tax audit export: CoA, GL entries, source documents, fiscal year | Export-only; every country diverges from base; not a working ledger model |
| **ISO 20022** (camt.053/052) | Bank statement interchange | Upstream of GL (single-entry transactions), not a ledger model |
| **OFX** | Consumer banking data exchange | Single-entry, consumer-grade; no GL structure |
| **FIBO** (EDM Council / OMG) | Financial instruments ontology (OWL) | No general ledger, no DEB primitives; instruments/entities only |

### Open-source implementations

| Project | Covers | Gap |
|---------|--------|-----|
| **GnuCash** (GPL-2.0) | Best-documented open-source accounting schema (SQL); tree-structured CoA with account types | Personal-finance scope; no GAAP/IFRS, XBRL, fiscal close, or financial statement derivation |
| **ERPNext** (GPL-3.0) | Full enterprise: hierarchical CoA, multi-company, fiscal year, financial reports, country localizations | Data model embedded in Frappe framework; not a separable specification |
| **Odoo CE** (LGPL-3.0) | `account.move` / `account.move.line` model; integrity hash; fiscal periods; tax reporting | Data model is ORM-defined (Python/XML), not a standalone spec |
| **LedgerSMB** (GPL-2.0+) | PostgreSQL-native DEB with stored procedures; payments as first-class entities | No formal data model documentation beyond SQL DDL |
| **python-accounting** (MIT) | IFRS-compliant reports (IS, BS, CF); account type system (Bank, Receivable, COGS, etc.); multi-entity; tamper protection | No XBRL; largely dormant since 2024; small project (~150 stars) |

### Fintech ledgers (not accounting systems)

| Project | Notes |
|---------|-------|
| **Formance Ledger** (MIT) | Multi-posting atomic transactions, Numscript DSL, immutable append-only. Fintech infrastructure, not GAAP/IFRS accounting. |
| **Blnk Finance** (Apache 2.0) | Balance monitoring, inflight transactions. Fintech, not accounting. |
| **Medici** (MIT) | MongoDB DEB library for Node.js. No financial statements or compliance. |

### Formal / academic work

| Work | Contribution | Status |
|------|-------------|--------|
| **Ellerman, "On Double-Entry Bookkeeping: The Mathematical Treatment" (2014)** [arXiv:1407.1898](https://arxiv.org/abs/1407.1898) | Algebraic formalization of DEB using the "Pacioli group" (group of differences on ordered pairs). Shows transactions are zero-elements. | Foundational paper. Essential reading for Layer 2 design. Can inform Alloy models (ADR-0002). |
| **Bjorner, "Double-entry Bookkeeping" (2024, DTU)** [PDF](https://www.imm.dtu.dk/~dibj/2024/debk/DoubleEntryBookKeeping.pdf) | Type-structured formal specification of DEB. Software-engineering approach to accounting domain description. | Most recent formal spec work. Directly applicable to Layer 2. |
| **HAX.Bookkeeping** (Haskell, [Hackage](https://hackage.haskell.org/package/hax-0.0.2/docs/HAX-Bookkeeping.html)) | Uses Haskell's type system to enforce balanced transactions at the type level. | Demonstrates DEB invariants can be enforced by type system. |
| **Cardano Formal Ledger Specs** (Agda, [GitHub](https://github.com/IntersectMBO/formal-ledger-specifications)) | Formally verified blockchain ledger rules in Agda (dependent types, machine-checked proofs). | Shows ledger invariants can be mechanically verified. Not financial accounting but technique is transferable. |
| **REA Ontology** (McCarthy, 1982) | Resource-Event-Agent model. Models economic exchanges directly rather than through debits/credits. Extended versions (OntoREA) add asset-liability-equity. | Philosophically opposed to DEB; influential in ERP design; no production implementation. |

### Commercial (non-open-source)

| Product | Notes |
|---------|-------|
| **IFRS-GAAP.com** | Standardized CoA with XBRL mapping to FASB and IFRS taxonomies. The most complete CoA-to-XBRL mapping available. EUR 149.90/yr subscription. Demonstrates what a complete account taxonomy looks like. |

### The gap

The survey confirms a genuine gap in the open-source ecosystem. The
closest projects each solve part of the problem:

- **XBRL GL** has the taxonomy but no implementation
- **python-accounting** has IFRS reports and account types but is dormant
  and small
- **ERPNext/Odoo** have full features but their data models are
  inseparable from their frameworks
- **GnuCash** has the best-documented schema but targets personal finance
- **Ellerman** provides the mathematical foundation but no implementation
- **SAF-T** provides the regulatory export format but not the working
  ledger model

pta-standards is uniquely positioned to bridge these: plain-text
ergonomics (beancount/ledger/hledger), formal semantics (Alloy + Ellerman),
taxonomy alignment (XBRL GL), and regulatory output (SAF-T, iXBRL).

### What we should build on vs. build from scratch

| Component | Build on | Build from scratch |
|-----------|----------|-------------------|
| Mathematical model of DEB | Ellerman's Pacioli group | — |
| Account type taxonomy | python-accounting's type system + XBRL GL taxonomy | Normal balance semantics, GAAP/IFRS subtype mapping |
| Formal verification | Alloy (ADR-0002) + Ellerman | Layer 2+ invariants |
| Fiscal period model | SAF-T's fiscal year structure | Closing entry generation, period lifecycle |
| Financial statement derivation | — | Full spec (no open-source reference exists) |
| Regulatory output | SAF-T country schemas, Arelle (XBRL tooling) | Mapping from our semantic model to these formats |
| SQL reference schema | GnuCash's documented schema | Extend with subtypes, normal balance, XBRL links |
| Audit trail | Odoo's integrity hash model | Full spec for SOX-grade immutability |

## References

### Internal

- pta-standards README (current scope and structure)
- ADR 0001: Three Separate Specs
- ADR 0002: Alloy over TLA+
- Beancount v3 spec: `formats/beancount/v3/spec/`

### Accounting standards

- IFRS standards index: <https://www.ifrs.org/issued-standards/list-of-standards/>
- FASB Accounting Standards Codification: <https://asc.fasb.org/>
- IAS 1 Presentation of Financial Statements
- IAS 2 Inventories (FIFO, weighted average; LIFO prohibited)
- IAS 7 Statement of Cash Flows
- IAS 21 Effects of Changes in Foreign Exchange Rates
- IAS 27 / IFRS 10 Consolidated Financial Statements
- ASC 205 Presentation of Financial Statements
- ASC 210 Balance Sheet
- ASC 225 Income Statement
- ASC 230 Statement of Cash Flows
- ASC 330 Inventory
- ASC 810 Consolidation
- ASC 830 Foreign Currency Matters

### Data standards

- ISO 4217 Currency codes: <https://www.iso.org/iso-4217-currency-codes.html>
- ISO 8601 Date and time: <https://www.iso.org/iso-8601-date-and-time-format.html>
- ISO 10383 Market Identifier Codes (MIC): <https://www.iso20022.org/market-identifier-codes>
- ISO 20022 Financial messaging: <https://www.iso20022.org/>

### Taxonomy and reporting standards

- XBRL International: <https://www.xbrl.org/>
- XBRL GL (Global Ledger Taxonomy):
  <https://specifications.xbrl.org/work-product-index-gl-gl.html>
- XBRL US GAAP Taxonomy: <https://xbrl.us/xbrl-taxonomy/>
- IFRS Taxonomy: <https://www.ifrs.org/issued-standards/ifrs-taxonomy/>
- OECD SAF-T: <https://www.oecd.org/tax/administration/standard-audit-file-tax-saf-t.htm>
- Arelle (open-source XBRL platform): <https://github.com/Arelle/Arelle>

### Academic and formal

- Ellerman, D. "On Double-Entry Bookkeeping: The Mathematical Treatment"
  (2014): <https://arxiv.org/abs/1407.1898>
- Bjorner, D. "Double-entry Bookkeeping" (2024, DTU):
  <https://www.imm.dtu.dk/~dibj/2024/debk/DoubleEntryBookKeeping.pdf>
- McCarthy, W.E. "The REA Accounting Model: A Generalized Framework for
  Accounting Systems in a Shared Data Environment" (1982)
- HAX.Bookkeeping (type-safe DEB in Haskell):
  <https://hackage.haskell.org/package/hax-0.0.2/docs/HAX-Bookkeeping.html>
- Cardano Formal Ledger Specifications (Agda):
  <https://github.com/IntersectMBO/formal-ledger-specifications>

### Open-source implementations referenced

- GnuCash SQL schema: <https://wiki.gnucash.org/wiki/SQL>
- python-accounting: <https://github.com/ekmungai/python-accounting>
- ERPNext: <https://github.com/frappe/erpnext>
- Odoo CE: <https://github.com/odoo/odoo>
- LedgerSMB: <https://github.com/ledgersmb/LedgerSMB>
- Formance Ledger: <https://github.com/formancehq/ledger>

### Historical

- Pacioli, _Summa de Arithmetica, Geometria, Proportioni et Proportionalita_
  (1494) — Particularis de Computis et Scripturis section defines
  double-entry method
