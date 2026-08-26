# PTA-Standards Addendum: Defined Behavior for Unspecified Cases

## Purpose

The beancount v3 format leaves certain behaviors unspecified. This
addendum defines normative behavior for these cases within the
PTA-standards specification. Implementations targeting PTA-standards
conformance MUST implement the behavior described here.

This document uses RFC 2119 / RFC 8174 keywords (MUST, SHOULD, MAY).

---

## 1. Posting on Account Close Date

**Beancount status**: Unspecified. The close directive documentation
says postings "after" the close date are errors, but does not define
whether posting ON the close date is permitted.

**PTA-standards definition**: Posting on the close date MUST be
permitted. The close date is the **last day** the account is active.
Postings dated strictly after the close date MUST produce a validation
error.

**Rationale**: The word "after" in the existing spec text means
strictly greater than. An account closed on December 31 should accept
that day's transactions — the closure is effective end-of-day. This
matches standard accounting practice where the close date is the final
day of activity.

**Test**: `account-closed-posting-same-day`

---

## 2. Duplicate Metadata Keys

**Beancount status**: Unspecified. No documentation addresses whether
duplicate keys on the same directive are permitted.

**PTA-standards definition**: Duplicate metadata keys MUST be accepted
without error. When duplicate keys are present, the **last value**
MUST take precedence.

**Rationale**: Beancount's reference implementation stores metadata
in a Python dict and uses `dict.update()`, which silently overwrites
with the last value. Rejecting duplicates would break existing files
and serves no accounting purpose — metadata is free-form annotation,
not a controlled field. Last-value-wins matches dict/JSON semantics
and is the least surprising behavior.

**Test**: `metadata-duplicate-key`

---

## 3. Transactions with No Postings

**Beancount status**: Unspecified. No documentation addresses whether
a transaction header with zero postings is valid.

**PTA-standards definition**: Transactions with no postings MUST be
accepted. They are trivially balanced (the empty sum equals zero for
all currencies).

**Rationale**: The grammar permits zero postings. An empty transaction
may serve as a memo entry, a placeholder, or a carrier for metadata
and tags. It satisfies the balance invariant vacuously. Both beancount
and rustledger accept this input without error.

**Test**: `invalid-transaction-no-postings` (note: despite the test ID
containing "invalid", the defined behavior is that this input is valid)

---

## 4. Empty Lines Within Transactions

**Beancount status**: Unspecified. No documentation addresses whether
blank lines between postings terminate the transaction or are ignored.

**PTA-standards definition**: Blank lines within a transaction (between
postings or metadata lines) SHOULD be accepted. Implementations MAY
treat a blank line as a transaction terminator, but this is NOT
RECOMMENDED.

**Rationale**: Both beancount and rustledger accept blank lines within
transactions. Users commonly insert blank lines for readability when
a transaction has many postings. Strict termination on blank lines
would break existing files.

**Test**: `empty-lines-in-transaction`

---

## 5. Unicode Characters in Account Names

**Beancount status**: The v3 spec requires account name components to
start with an ASCII uppercase letter (`[A-Z]`). This restriction
originates from the C flex lexer used in beancount v1/v2, which had
poor Unicode support. The v3 spec codified this limitation rather than
fixing it.

This has been an open issue in upstream beancount since 2015:
- [beancount#161](https://github.com/beancount/beancount/issues/161) — Russian (2015)
- [beancount#398](https://github.com/beancount/beancount/issues/398) — CJK (2017)
- [beancount#733](https://github.com/beancount/beancount/issues/733) — Chinese (2023)

**PTA-standards definition**: Account name components MAY start with
any Unicode uppercase letter (`\p{Lu}`), titlecase letter (`\p{Lt}`),
or ideographic character (`\p{Lo}`). The ASCII-only restriction is
removed.

Valid account starts include:
- Latin uppercase: `A-Z` (unchanged)
- Cyrillic uppercase: `А-Я` (e.g., `Активы:Банк`)
- Greek uppercase: `Α-Ω` (e.g., `Ενεργητικό:Τράπεζα`)
- CJK ideographs: `漢字` (e.g., `資産:銀行口座`)
- Other Unicode letters without case: `\p{Lo}`

Subsequent characters in account components follow the same rules as
the base spec (ASCII alphanumeric, hyphens, and UTF-8 characters).

**Rationale**: There is no semantic reason to restrict account names
to ASCII. The restriction excludes every non-Latin writing system,
affecting users of Cyrillic, CJK, Arabic, Devanagari, and other
scripts. Plain text accounting should be accessible to all languages.
The `name_assets`, `name_liabilities`, etc. options already allow
non-ASCII account type roots, making the component restriction
inconsistent.

**Test**: `unicode-account-name-edge`

---

## Changelog

- 2026-04-18: Add section 5 — Unicode account names
- 2026-04-12: Initial addendum with 4 behavior definitions
