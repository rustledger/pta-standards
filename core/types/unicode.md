# Unicode Support

This document specifies Unicode handling in plain text accounting systems.

## Overview

Plain text accounting files are Unicode text documents. This specification defines encoding requirements, normalization rules, and character handling.

## Encoding

### UTF-8 Requirement

Source files MUST be encoded in UTF-8:

- UTF-8 is the only supported encoding
- Other encodings (UTF-16, ISO-8859-1, etc.) MUST be rejected
- Implementations MUST validate UTF-8 sequences

### UTF-8 Validation

Invalid UTF-8 sequences MUST produce errors:

```
ERROR: Invalid UTF-8 sequence
  --> ledger.beancount:42:15
   |
42 |   payee: "Invalid <0xFF> byte"
   |                   ^^^^^^
   |
   = byte 0xFF is not valid in UTF-8
```

### Byte Order Mark

The UTF-8 BOM (EF BB BF) at file start:

- MUST be accepted (ignored)
- MUST NOT be required
- SHOULD NOT be generated in output

## Character Categories

### Allowed Characters

| Category | Code Points | Example |
|----------|-------------|---------|
| Basic Latin | U+0020-U+007E | A-Z, 0-9, punctuation |
| Latin Extended | U+00A0-U+024F | é, ñ, ü |
| Greek | U+0370-U+03FF | α, β, γ |
| Cyrillic | U+0400-U+04FF | А, Б, В |
| CJK | U+4E00-U+9FFF | 日, 本, 語 |
| Currency Symbols | U+20A0-U+20CF | €, £, ¥ |
| Emoji | Various | 💰, 📊 |

### Prohibited Characters

| Category | Code Points | Reason |
|----------|-------------|--------|
| Control (C0) | U+0000-U+001F | Non-printable |
| Delete | U+007F | Control character |
| Control (C1) | U+0080-U+009F | Non-printable |
| Surrogates | U+D800-U+DFFF | UTF-16 only |
| Noncharacters | U+FDD0-U+FDEF | Reserved |

### Whitespace

| Character | Code Point | Handling |
|-----------|------------|----------|
| Space | U+0020 | Standard separator |
| Tab | U+0009 | Indent/alignment |
| Newline | U+000A | Line terminator |
| Carriage Return | U+000D | Ignored (with LF) |
| No-Break Space | U+00A0 | Treated as space |

## Normalization

### NFC Normalization

Implementations SHOULD normalize text to NFC (Canonical Decomposition, followed by Canonical Composition):

```
Input: "café" (e + combining acute)
       U+0063 U+0061 U+0066 U+0065 U+0301

NFC:   "café" (precomposed é)
       U+0063 U+0061 U+0066 U+00E9
```

### When to Normalize

| Context | Normalization |
|---------|---------------|
| Comparison | MUST normalize before comparing |
| Storage | SHOULD store normalized form |
| Display | Preserve user input |
| Hash/Index | MUST use normalized form |

### Normalization Forms

| Form | Description | Use |
|------|-------------|-----|
| NFC | Composed | Preferred for storage |
| NFD | Decomposed | Not recommended |
| NFKC | Compatibility composed | For search |
| NFKD | Compatibility decomposed | For search |

## Case Handling

### Case Sensitivity

Context-dependent case handling:

| Context | Case Handling |
|---------|---------------|
| Account names | Case-sensitive |
| Commodity names | Uppercase (Beancount) or sensitive |
| Metadata keys | Case-sensitive (typically lowercase) |
| Metadata values | Case-preserved |
| Tags | Case-sensitive |

### Case Folding

For case-insensitive comparison, use Unicode case folding:

```python
# Simple lowercase is insufficient for some scripts
"Straße".casefold() == "strasse"  # German sharp s
```

## Grapheme Clusters

### Extended Grapheme Clusters

A user-perceived "character" may be multiple code points:

```
👨‍👩‍👧 (Family emoji)
= U+1F468 U+200D U+1F469 U+200D U+1F467
= 5 code points, 1 grapheme cluster
```

### Length Calculation

| Method | "café" | "👨‍👩‍👧" |
|--------|--------|---------|
| Code points | 4 | 5 |
| Grapheme clusters | 4 | 1 |
| UTF-8 bytes | 5 | 18 |

Implementations SHOULD use code points for internal length calculations.

## Identifiers

### Account Name Characters

Valid characters in account names:

```
Letter:     A-Z a-z (Latin)
            Plus letters from other scripts (implementation-defined)
Digit:      0-9
Special:    - _ : (separator)
```

### Commodity Name Characters

Beancount commodities (uppercase requirement):

```
Letter:     A-Z
Digit:      0-9
Special:    ' . _ -
```

### Unicode Letters

For "letter" matching, use Unicode category:

```python
import unicodedata

def is_letter(char):
    return unicodedata.category(char).startswith('L')

is_letter('A')  # True (Latin)
is_letter('日') # True (CJK)
is_letter('1')  # False (digit)
```

## Line Handling

### Line Terminators

Accepted line terminators:

| Sequence | Name | Handling |
|----------|------|----------|
| U+000A | LF | Standard |
| U+000D U+000A | CRLF | Treated as single LF |
| U+000D | CR alone | Converted to LF |

### Line Continuation

No implicit line continuation. Multi-line constructs use explicit syntax.

### Maximum Line Length

Implementations SHOULD support lines up to 10,000 characters.
Lines exceeding this MAY be rejected or truncated.

## String Literals

### Escape Sequences

| Escape | Code Point | Character |
|--------|------------|-----------|
| `\n` | U+000A | Newline |
| `\t` | U+0009 | Tab |
| `\r` | U+000D | Carriage return |
| `\\` | U+005C | Backslash |
| `\"` | U+0022 | Double quote |
| `\uXXXX` | U+XXXX | BMP character |
| `\UXXXXXXXX` | U+XXXXXXXX | Any character |

### Non-BMP Characters

Characters outside the Basic Multilingual Plane (U+10000+):

```
"💰" = "\U0001F4B0"  ; Money bag emoji

; In UTF-16 (for reference, not used in PTA):
; U+D83D U+DCB0 (surrogate pair)
```

## Bidirectional Text

### Right-to-Left Scripts

Hebrew, Arabic, and other RTL scripts are supported:

```
2024-01-15 * "קניה"  ; Hebrew
  הוצאות:מזון  50 ILS
  נכסים:בנק
```

### Bidirectional Algorithm

Display follows Unicode Bidirectional Algorithm (UAX #9).
Storage is always in logical order.

### Explicit Direction

Directional formatting characters (LRM, RLM, etc.) MAY be used but are not recommended.

## Implementation Notes

### String Storage

```python
class UnicodeString:
    _data: str  # Python str (UTF-8 or UTF-32 internal)

    def normalize(self) -> 'UnicodeString':
        import unicodedata
        return UnicodeString(unicodedata.normalize('NFC', self._data))

    def code_points(self) -> int:
        return len(self._data)

    def graphemes(self) -> int:
        import grapheme
        return grapheme.length(self._data)
```

### Comparison

```python
def equals(a: str, b: str) -> bool:
    import unicodedata
    return unicodedata.normalize('NFC', a) == unicodedata.normalize('NFC', b)
```

### Validation

```python
def validate_utf8(data: bytes) -> str:
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError as e:
        raise ParseError(f"Invalid UTF-8 at byte {e.start}")
```

## Error Messages

### Invalid Encoding

```
ERROR: Invalid UTF-8 encoding
  --> ledger.beancount:1:1
   |
   = file is not valid UTF-8
   = hint: convert using 'iconv -f <encoding> -t utf-8'
```

### Prohibited Character

```
ERROR: Prohibited control character
  --> ledger.beancount:42:15
   |
42 |   note: "Text with <NUL> inside"
   |                     ^^^^^
   |
   = U+0000 (NULL) is not allowed
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Encoding | UTF-8 only | Multiple | UTF-8 |
| Normalization | NFC | None | None |
| Case in accounts | Sensitive | Configurable | Sensitive |
| Unicode escapes | Yes | Limited | Yes |
| RTL support | Limited | Limited | Limited |
