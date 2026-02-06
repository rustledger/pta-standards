# String Type

This document specifies the string type used for text values in plain text accounting.

## Definition

A **String** is a sequence of Unicode code points representing text. Strings are used for narrations, payees, metadata values, account names, and other textual data.

## Encoding

### Source File Encoding

Source files MUST be encoded in UTF-8:

```
Content-Type: text/plain; charset=utf-8
```

Implementations MUST reject files with invalid UTF-8 sequences.

### BOM Handling

UTF-8 Byte Order Mark (BOM) at file start SHOULD be ignored:

```
EF BB BF ... (UTF-8 BOM)
```

Implementations MUST NOT require BOM and MUST NOT include BOM in output.

## String Literals

### Quoted Strings

String literals are enclosed in double quotes:

```
"Hello, World"
"Monthly salary"
"Café au lait"
```

### Escape Sequences

Standard escape sequences:

| Escape | Meaning |
|--------|---------|
| `\"` | Double quote |
| `\\` | Backslash |
| `\n` | Newline |
| `\t` | Tab |
| `\r` | Carriage return |

### Unicode Escapes

Unicode code points can be escaped:

| Format | Example | Character |
|--------|---------|-----------|
| `\uXXXX` | `\u00E9` | é (U+00E9) |
| `\UXXXXXXXX` | `\U0001F4B0` | 💰 (U+1F4B0) |

### Raw Strings

Some formats support raw strings without escape processing:

```
r"C:\Users\name\file.txt"
```

## Character Classes

### Allowed Characters

String literals MAY contain:

- Printable ASCII (0x20-0x7E)
- Non-ASCII Unicode (U+0080 and above)
- Escaped control characters

### Prohibited Characters

Unescaped control characters (0x00-0x1F, 0x7F) are prohibited:

```
"Hello\x00World"  // Invalid: embedded NUL
"Line1\nLine2"    // Valid: escaped newline
```

### Whitespace

| Character | Allowed | Notes |
|-----------|---------|-------|
| Space (0x20) | Yes | |
| Tab (0x09) | Escaped only | `\t` |
| Newline (0x0A) | Escaped only | `\n` |
| Carriage return (0x0D) | Escaped only | `\r` |

## Identifiers

### Unquoted Identifiers

Some string contexts allow unquoted identifiers:

```
Assets:Checking      ; Account name (unquoted)
USD                  ; Commodity (unquoted)
```

### Identifier Rules

| Context | Allowed Characters | Case |
|---------|-------------------|------|
| Account | `A-Za-z0-9:_-` | Sensitive |
| Commodity | `A-Z0-9'._-` | Uppercase (Beancount) |
| Metadata key | `a-z0-9_-` | Lowercase |

### Quoting Requirement

Identifiers with special characters require quoting:

```
"Account Name"       ; Space requires quotes
"US Dollar"          ; Multi-word
"S&P 500"            ; Special characters
```

## String Operations

### Concatenation

Strings can be concatenated:

```python
"Hello" + " " + "World" = "Hello World"
```

### Comparison

String comparison is byte-for-byte after normalization:

```python
"café" == "café"      # Depends on normalization
"CAFÉ" == "café"      # False (case-sensitive)
```

### Length

Length is measured in:

| Unit | Description |
|------|-------------|
| Code points | Unicode characters |
| Bytes | UTF-8 encoded bytes |
| Graphemes | User-perceived characters |

Implementations SHOULD use code points for length calculations.

## Normalization

### Unicode Normalization

Implementations SHOULD normalize strings to NFC (Canonical Decomposition, followed by Canonical Composition):

```
é (U+00E9)           ; Precomposed
e + ́ (U+0065 U+0301) ; Decomposed

After NFC: é (U+00E9)
```

### Case Normalization

Case handling depends on context:

| Context | Case Handling |
|---------|---------------|
| Account names | Preserved (case-sensitive) |
| Commodities | Uppercase (Beancount) or preserved |
| Metadata keys | Lowercase |
| Metadata values | Preserved |
| Narrations | Preserved |

## Empty Strings

### Empty vs. Null

Empty string is a valid value, distinct from null/missing:

```
""                   ; Empty string (present but empty)
; vs.
; (field omitted)    ; Null/missing
```

### Empty Payee

Empty payee is distinct from no payee:

```
2024-01-15 * "" "Narration"     ; Empty payee
2024-01-15 * "Narration"        ; No payee
```

## String in Different Contexts

### Narration

Free-form transaction description:

```
2024-01-15 * "Weekly grocery shopping at Whole Foods"
```

### Payee

Transaction counterparty:

```
2024-01-15 * "Whole Foods" "Weekly groceries"
```

### Metadata Value

Arbitrary string values:

```
  receipt: "receipts/2024/01/15-grocery.pdf"
  notes: "Bought items for office party"
```

### Tag

Hash-prefixed identifier:

```
#project-2024
#tax-deductible
```

### Link

Caret-prefixed identifier:

```
^invoice-001
^receipt-abc123
```

## Validation

### Encoding Error

```
ERROR: Invalid UTF-8 sequence
  --> ledger.beancount:42:15
   |
42 |   payee: "Invalid \xFF byte"
   |                    ^^^^
   |
   = not a valid UTF-8 sequence
```

### Unterminated String

```
ERROR: Unterminated string literal
  --> ledger.beancount:42:8
   |
42 | 2024-01-15 * "Missing end quote
   |              ^^^^^^^^^^^^^^^^^^
   |
   = expected closing '"'
```

### Invalid Escape

```
ERROR: Invalid escape sequence
  --> ledger.beancount:42:15
   |
42 |   note: "Invalid \q escape"
   |                   ^^
   |
   = valid escapes: \\ \" \n \t \r \uXXXX
```

## Implementation

### Memory Model

```python
@dataclass(frozen=True)
class String:
    value: str  # Unicode string

    def __eq__(self, other: 'String') -> bool:
        # Normalize before comparison
        return unicodedata.normalize('NFC', self.value) == \
               unicodedata.normalize('NFC', other.value)

    def __len__(self) -> int:
        # Length in code points
        return len(self.value)
```

### Interning

Frequently-used strings SHOULD be interned:

```python
class StringInterner:
    _cache: Dict[str, str] = {}

    def intern(self, s: str) -> str:
        if s not in self._cache:
            self._cache[s] = s
        return self._cache[s]
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Encoding | UTF-8 only | Multiple | UTF-8 |
| Quote char | `"` | `"` | `"` |
| Escapes | Yes | Yes | Yes |
| Raw strings | No | No | No |
| Case in accounts | Sensitive | Configurable | Sensitive |
