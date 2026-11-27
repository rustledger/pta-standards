# Beancount v3 lexical specification (clean-room)

This document specifies how beancount 3.2.3 splits a file into the tokens consumed by the LALR grammar in [`beancount.y`](beancount.y).
It was written from black-box experiments with `beancount.parser.lexer.lex_iter_string` and from public documentation, never from beancount's lexer source (see [PROVENANCE.md](PROVENANCE.md)).

The rule table is also available in executable form in [`harness/reflexer.py`](harness/reflexer.py).
`harness/equivalence.py --check-lexer` compares that implementation token-for-token (name and line) with beancount's lexer over the test corpora; see "Verification" below.

## Input

The input is a sequence of bytes.
It is not decoded first: invalid UTF-8 simply fails to match any rule and becomes part of an invalid run.
A UTF-8 byte-order mark is not special: at the start of a line it begins an invalid run (so `EF BB BF 2024-01-01 ...` is one `error` token).

Whitespace is space (`20`), tab (`09`) and carriage return (`0D`).
Form feed, vertical tab, NUL and the other control characters are *not* whitespace; they are ordinary bytes that only an invalid run accepts.
A line ends at LF (`0A`) only.
A CR is skipped like a space wherever it occurs, so CRLF files lex like LF files, and a lone CR separates tokens but does not end a line.

## Matching discipline

The lexer works like a flex scanner:

1. At each position, every active rule is tried.
   Rules marked *BOL* are active only at the start of a line (position 0 or right after a LF).
2. The longest match wins.
   A rule's trailing context counts towards the length but is not consumed.
   Ties go to the rule listed first.
3. If the winning rule has a post-check and the check fails, the matched text is returned as an `error` token, and scanning continues right after it.
4. If no rule matches, an **invalid run** is returned as one `error` token: every byte up to, not including, the next space, tab, CR or LF.
   An invalid run is not a competing rule: `USD$` is `CURRENCY` then `error($)`, not one error.
   Inside an invalid run nothing else is recognised: `x;y` is one error token (no comment), `x"a b"` is `error(x"a)` `error(b")`.

Every `error` token reaches the parser as bison's `YYerror` (recovery without a report) and is also reported by beancount as a `LexerError`.

**Line numbers.** A token's line is the line on which it *ends*.
An `EOL` token therefore carries the number of the line that follows it, and a multi-line string carries the line of its closing quote.
The parser reports a syntax error at the line of its lookahead token, so this convention fixes error lines.

**End of input.** No `EOL` is synthesised at end of input; the parser sees end-of-file directly (the grammar's `eol` accepts it).

## Rule table

Rules are listed in priority order (earlier wins ties).
`U8` stands for one validly encoded non-ASCII UTF-8 code point (2–4 bytes, RFC 3629).

| # | Token | Pattern | Trailing context | Notes |
|---|-------|---------|------------------|-------|
| 1 | `INDENT` (BOL) | `[ \t]+` | `[^ \t\r\n]` | Emitted only if the line has a non-blank character after the indentation; a comment counts (`  ;c` is `INDENT EOL`). Blank-only lines produce no `INDENT`, and neither does indentation after a leading CR. Depth is not tracked: any indentation is one `INDENT`. |
| 2 | *(skip)* (BOL) | `[*:!&?%][^\n]+` | | **Ignored line.** One of `* : ! & ? %` in column 0 followed by at least one more character on the line: the rest of the line is skipped (org-mode headings). The LF is still returned as `EOL`. If the character is alone on its line (or at end of input) it lexes normally (`*` → `ASTERISK`, `!` → `FLAG`). |
| 3 | *(skip)* (BOL) | `#[^\n A-Za-z0-9\-_/.][^\n]*` | | **Ignored line** for `#` in column 0 followed by a character that cannot continue a tag (space, `!`, non-ASCII, ...). `#tag` in column 0 is a `TAG`; `#` alone on its line is `HASH`. |
| 4 | *(skip)* | `[ \t\r]+` | | |
| 5 | `EOL` | `\n` | | |
| 6 | *(skip)* | `;[^\n]*` | | Comment. |
| 7 | `DATE` | `[0-9]{4,}[-/][0-9]+[-/][0-9]+` | | Post-check: calendar date (see below). Separators may be mixed (`2024-01/01`). |
| 8 | keywords | `txn balance open close commodity pad event price note document query custom pushtag poptag pushmeta popmeta option include plugin` | | Token names are the upper-cased words (`TXN`, `BALANCE`, ...). No word boundary is required: `opena` is `OPEN error(a)`, `openA` is `OPEN CAPITAL`. A longer `KEY` match wins (`open: 1` is `KEY COLON NUMBER`). |
| 9 | `BOOL` | `TRUE\|FALSE` | | A longer currency wins (`TRUEX` is `CURRENCY`). |
| 10 | `NONE` | `NULL` | | |
| 11 | `ACCOUNT` | `([A-Z]\|U8)([A-Za-z0-9\-]\|U8)*(:([A-Z0-9]\|U8)([A-Za-z0-9\-]\|U8)*)+` | | Any capitalised first component is accepted lexically (`Foo:Bar`); the five root names are a later, semantic check. |
| 12 | `CURRENCY` | `[A-Z][A-Z0-9'._\-]*[A-Z0-9]` | | At least two characters. No length limit is applied by the lexer. |
| 13 | `CURRENCY` | `/[0-9'._\-]*[A-Z]([A-Z0-9'._\-]*[A-Z0-9])?` | | Slash-prefixed (futures-style) currencies: `/ES`, `/6J`, `/A`. Needs at least one letter (`/6` is `SLASH NUMBER`). |
| 14 | `STRING` | `"([^"\\]\|\\[^\n])*"` | | Post-check: valid UTF-8. May span lines. A backslash cannot escape a newline. Post-processing of the value: see below. An unterminated string matches nothing, so the `"` starts an invalid run. |
| 15 | `NUMBER` | `[0-9]([0-9,]*[0-9])?(\.[0-9]*)?` | | No sign (a leading `-` is `MINUS`), no leading `.` (`.5` is an invalid run), a trailing `.` is part of the number (`1.`). Post-check: digit grouping (see below). |
| 16 | `TAG` | `#[A-Za-z0-9\-_/.]+` | | |
| 17 | `LINK` | `\^[A-Za-z0-9\-_/.]+` | | |
| 18 | `KEY` | `[a-z][a-zA-Z0-9\-_]+` | `:` | At least two characters and immediately followed by `:`, which is then returned as `COLON`. Without the colon the word is an invalid run (`kk 1`, `k: 1`, `Kk: 1`). |
| 19 | `ATAT` `AT` | `@@` `@` | | |
| 20 | `LCURLCURL` `RCURLCURL` `LCURL` `RCURL` | `{{` `}}` `{` `}` | | |
| 21 | `COMMA` `TILDE` `PLUS` `MINUS` `SLASH` `LPAREN` `RPAREN` `PIPE` `ASTERISK` `COLON` `HASH` | `, ~ + - / ( ) \| * : #` | | |
| 22 | `FLAG` | `[!&?%]` | | |
| 23 | `CAPITAL` | `[A-Z]` | `[ \t\n]` | A single capital letter, used as a transaction or posting flag or as a one-letter currency. It must be followed by space, tab or LF: `P,`, `P:`, `P;`, `P` followed by CR, and `P` at end of input are invalid runs. |

Characters with no rule of their own (`" $ ' . < = > [ \ ] ^ _` and backquote, lowercase letters not starting a keyword or key, control characters, non-ASCII outside accounts) start an invalid run.

## Post-lex checks

A failed check turns the matched text (exactly that text) into an `error` token.

**Dates.**
The three numbers must form a valid proleptic-Gregorian date with year 1–9999: `2024-02-30`, `2024-00-10`, `0000-01-01` and `12345-01-01` are errors.
Leading zeros are fine in every field (`02024-001-01` is 2024-01-01).
A date needs at least four year digits; `999-01-01` and `24-01-01` lex as `NUMBER MINUS NUMBER MINUS NUMBER`.

**Number grouping.**
If the integer part contains commas it must match `[0-9]{1,3}(,[0-9]{3})*`, or, as an observed quirk, `[0-9],,[0-9]{3}(,[0-9]{3})*` (`1,,000` is the number 1000, but `11,,000` and `1,000,,000` are errors).
Examples of errors: `1,0`, `1,00,000`, `1,0000`, `1111,111`.
Commas are dropped from the value.

**Number length.**
With commas removed, the token text (digits and the decimal point) may be at most 255 characters; a longer number is an error.

**String encoding.**
The bytes between the quotes must be valid UTF-8; otherwise the whole string (quotes included) is an error token.

**String escapes.**
The value is the text between the quotes with each backslash escape replaced: `\n` → LF, `\r` → CR, `\t` → tab, `\b` → backspace, `\f` → form feed; any other escaped character stands for itself (`\"` → `"`, `\\` → `\`, `\q` → `q`, `\a` → `a`, `\0` → `0`).
A raw newline inside the quotes is kept.

## Verification

`harness/reflexer.py` implements the table above.
Over the corpora used by the equivalence harness (see the harness README) it reproduces beancount's token names and lines exactly on every compared input; `equivalence.py --check-lexer` prints the current rate.

## Corrections to `spec/lexical.md`

Experiments contradicted these claims in [`../spec/lexical.md`](../spec/lexical.md):

| Claim in spec/lexical.md | Observed |
|--------------------------|----------|
| Account components after the first must start with an ASCII uppercase letter or digit; UTF-8 only after the first character. | A component may start with a non-ASCII character (`Assets:é`, `Équity:A` are accounts). |
| The root must be one of the five account types. | Lexically, any capitalised first component is an `ACCOUNT` (`Foo:Bar`). |
| Only `\"` and `\\` are escapes; `\n`, `\t`, `\r` are kept literally. | `\n`, `\r`, `\t`, `\b`, `\f` are translated; every other escaped character loses its backslash. |
| Number grouping: `digits ("," digits)*`, separator optional and ignored. | Groups after the first must have exactly three digits and the first one to three (`1,0` is a lexer error), with the `1,,000` quirk above. |
| Currency: at least two characters starting with a letter. | A single capital letter is token `CAPITAL` and is accepted wherever a currency is; slash-prefixed currencies (`/6J`) exist. |
| Date: `YYYY "-" MM "-" DD` or with `/`. | Separators may be mixed; any number of digits per field (year at least four); the date must exist. |
| Lines that don't start with a recognized pattern are silently ignored (e.g. `Random text is also ignored`). | Only lines starting in column 0 with `* : ! & ? %` (followed by something) or `#` followed by a non-tag character are ignored. Other unrecognised text produces lexer errors (`Random` → `error`). |
| Comments are valid after any token. | A `;` inside an invalid run does not start a comment. |
| Tags: `#` followed by tag characters; spec silent on `#` alone. | `#` not followed by a tag character is token `HASH` (a flag, and the compound-cost separator). |
| CR-only line endings are "not supported". | A CR is whitespace: it separates tokens but does not end the line, so a CR-only file is one long line. |
| BOM produces an "Invalid token" error. | Correct, but more precisely the BOM begins an invalid run that swallows the rest of the first non-blank word. |
