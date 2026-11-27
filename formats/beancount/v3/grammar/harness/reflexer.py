"""Executable form of the lexical specification (``../LEXICAL.md``).

The rule table below *is* the lexical spec in machine-readable form; this
module only adds the matching discipline around it.  It was written from
black-box experiments on beancount 3.2.3's ``lex_iter_string`` and is checked
against it by ``lexcheck.py``.  It is not derived from beancount's lexer
sources.

Matching discipline (flex-like):

* At each position every rule that is *active* is tried.  Rules marked
  ``bol`` are active only at the start of a line.
* The longest match wins, where a rule's trailing context counts towards
  its length but is not consumed.  Ties go to the earlier rule.
* A rule with a ``check`` post-validates its text; if the check fails the
  text is emitted as an ``error`` token instead (and lexing continues right
  after it).
* If no rule matches, an *invalid run* is emitted as a single ``error``
  token: everything up to (not including) the next space, tab, CR or
  newline.
* The line number of a token is the line on which it *ends*; the newline
  of an ``EOL`` token counts, so an ``EOL`` reports the following line.
"""

from __future__ import annotations

import datetime
import re

# Valid UTF-8 encoded non-ASCII code point (RFC 3629).
U8 = (
    rb"(?:[\xC2-\xDF][\x80-\xBF]|\xE0[\xA0-\xBF][\x80-\xBF]|[\xE1-\xEC\xEE\xEF][\x80-\xBF]{2}"
    rb"|\xED[\x80-\x9F][\x80-\xBF]|\xF0[\x90-\xBF][\x80-\xBF]{2}|[\xF1-\xF3][\x80-\xBF]{3}"
    rb"|\xF4[\x80-\x8F][\x80-\xBF]{2})"
)

TAGCHARS = rb"A-Za-z0-9\-_/."
CURCHARS = rb"A-Z0-9'._\-"


def _date_ok(text: bytes) -> bool:
    y, m, d = (int(x) for x in re.split(rb"[-/]", text))
    try:
        datetime.date(y, m, d)
    except (ValueError, OverflowError):
        return False
    return True


def _number_ok(text: bytes) -> bool:
    if len(text.replace(b",", b"")) > 255:
        return False
    intpart = text.split(b".")[0]
    if b"," not in intpart:
        return True
    return bool(re.fullmatch(rb"[0-9]{1,3}(,[0-9]{3})*|[0-9],,[0-9]{3}(,[0-9]{3})*", intpart))


def _string_ok(text: bytes) -> bool:
    try:
        text.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


KEYWORDS = [
    (b"txn", "TXN"),
    (b"balance", "BALANCE"),
    (b"open", "OPEN"),
    (b"close", "CLOSE"),
    (b"commodity", "COMMODITY"),
    (b"pad", "PAD"),
    (b"event", "EVENT"),
    (b"price", "PRICE"),
    (b"note", "NOTE"),
    (b"document", "DOCUMENT"),
    (b"query", "QUERY"),
    (b"custom", "CUSTOM"),
    (b"pushtag", "PUSHTAG"),
    (b"poptag", "POPTAG"),
    (b"pushmeta", "PUSHMETA"),
    (b"popmeta", "POPMETA"),
    (b"option", "OPTION"),
    (b"include", "INCLUDE"),
    (b"plugin", "PLUGIN"),
]

# (token or None to skip, regex, trailing-context regex or None, bol-only, check)
RULES = [
    # --- start-of-line rules -------------------------------------------------
    # Indentation: leading blanks followed by something other than a blank,
    # CR or newline (a comment counts).  Blank-only lines produce no INDENT.
    ("INDENT", rb"[ \t]+", rb"[^ \t\r\n]", True, None),
    # Ignored lines: one of * : ! & ? % in column 0, followed by any
    # character, swallows the rest of the line (org-mode headings etc.).
    (None, rb"[*:!&?%][^\n]+", None, True, None),
    # '#' in column 0 followed by a character that cannot continue a tag.
    (None, rb"#[^\n" + TAGCHARS + rb"][^\n]*", None, True, None),
    # --- everywhere ----------------------------------------------------------
    (None, rb"[ \t\r]+", None, False, None),
    ("EOL", rb"\n", None, False, None),
    (None, rb";[^\n]*", None, False, None),
    ("DATE", rb"[0-9]{4,}[-/][0-9]+[-/][0-9]+", None, False, _date_ok),
    *[(tok, re.escape(kw), None, False, None) for kw, tok in KEYWORDS],
    ("BOOL", rb"TRUE|FALSE", None, False, None),
    ("NONE", rb"NULL", None, False, None),
    (
        "ACCOUNT",
        rb"(?:[A-Z]|" + U8 + rb")(?:[A-Za-z0-9\-]|" + U8 + rb")*"
        rb"(?::(?:[A-Z0-9]|" + U8 + rb")(?:[A-Za-z0-9\-]|" + U8 + rb")*)+",
        None,
        False,
        None,
    ),
    ("CURRENCY", rb"[A-Z][" + CURCHARS + rb"]*[A-Z0-9]", None, False, None),
    ("CURRENCY", rb"/[0-9'._\-]*[A-Z](?:[" + CURCHARS + rb"]*[A-Z0-9])?", None, False, None),
    ("STRING", rb'"(?:[^"\\]|\\[^\n])*"', None, False, _string_ok),
    ("NUMBER", rb"[0-9](?:[0-9,]*[0-9])?(?:\.[0-9]*)?", None, False, _number_ok),
    ("TAG", rb"#[" + TAGCHARS + rb"]+", None, False, None),
    ("LINK", rb"\^[" + TAGCHARS + rb"]+", None, False, None),
    ("KEY", rb"[a-z][a-zA-Z0-9\-_]+", rb":", False, None),
    ("ATAT", rb"@@", None, False, None),
    ("AT", rb"@", None, False, None),
    ("LCURLCURL", rb"\{\{", None, False, None),
    ("RCURLCURL", rb"\}\}", None, False, None),
    ("LCURL", rb"\{", None, False, None),
    ("RCURL", rb"\}", None, False, None),
    ("COMMA", rb",", None, False, None),
    ("TILDE", rb"~", None, False, None),
    ("PLUS", rb"\+", None, False, None),
    ("MINUS", rb"-", None, False, None),
    ("SLASH", rb"/", None, False, None),
    ("LPAREN", rb"\(", None, False, None),
    ("RPAREN", rb"\)", None, False, None),
    ("PIPE", rb"\|", None, False, None),
    ("ASTERISK", rb"\*", None, False, None),
    ("COLON", rb":", None, False, None),
    ("HASH", rb"#", None, False, None),
    ("FLAG", rb"[!&?%]", None, False, None),
]

_COMPILED = [
    (tok, re.compile(rx), re.compile(tc) if tc else None, bol, chk)
    for tok, rx, tc, bol, chk in RULES
]
# A single capital letter needs a following blank or newline.  It is listed
# separately because its single-letter match must lose to CURRENCY.
_CAPITAL = re.compile(rb"[A-Z](?=[ \t\n])")
_INVALID = re.compile(rb"[^ \t\r\n]+")


def lex(data: bytes):
    """Yield ``(token_name, line, text)`` like ``lex_iter_string`` does."""
    pos, line, n = 0, 1, len(data)
    while pos < n:
        bol = pos == 0 or data[pos - 1 : pos] == b"\n"
        best = None  # (length, -rule_index, tok, text_len, check)
        for i, (tok, rx, tc, only_bol, chk) in enumerate(_COMPILED):
            if only_bol and not bol:
                continue
            m = rx.match(data, pos)
            if not m:
                continue
            ln = m.end() - pos
            tot = ln
            if tc is not None:
                t = tc.match(data, m.end())
                if not t:
                    continue
                tot += t.end() - m.end()
            if best is None or tot > best[0]:
                best = (tot, i, tok, ln, chk)
        m = _CAPITAL.match(data, pos)
        if m and (best is None or best[0] < 2):
            best = (2, len(_COMPILED), "CAPITAL", 1, None)
        if best is None:
            m = _INVALID.match(data, pos)
            text = m.group()
            line += text.count(b"\n")
            yield ("error", line, text)
            pos = m.end()
            continue
        _, _, tok, ln, chk = best
        text = data[pos : pos + ln]
        pos += ln
        line += text.count(b"\n")
        if tok is None:
            continue
        if chk is not None and not chk(text):
            tok = "error"
        yield (tok, line, text)
