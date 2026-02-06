# Date Formats

This document specifies date formatting for internationalization in plain text accounting.

## Input vs. Output

### Input (Canonical)

Source files MUST use ISO 8601 format:

```
YYYY-MM-DD
```

This format is:
- Unambiguous (no day/month confusion)
- Sortable (lexicographic = chronological)
- Universal (no locale dependency)

### Output (Localized)

Reports and displays MAY use locale-specific formats:

```
January 15, 2024    ; en-US
15 January 2024     ; en-GB
15. Januar 2024     ; de-DE
2024年1月15日        ; ja-JP
```

## ISO 8601 Format

### Full Date

```
YYYY-MM-DD

2024-01-15    ; January 15, 2024
2024-12-31    ; December 31, 2024
```

### Alternative Separators

Some formats accept alternatives:

```
2024/01/15    ; Slash separator
2024.01.15    ; Dot separator (rare)
```

Implementations SHOULD accept slash; MUST accept hyphen.

### Leading Zeros

Month and day MUST have leading zeros:

```
2024-01-05    ; Valid
2024-1-5      ; Invalid
```

## Locale Date Patterns

### Pattern Symbols

| Symbol | Meaning | Example |
|--------|---------|---------|
| `YYYY` | 4-digit year | 2024 |
| `YY` | 2-digit year | 24 |
| `MM` | 2-digit month | 01 |
| `M` | Month number | 1 |
| `MMMM` | Full month name | January |
| `MMM` | Abbreviated month | Jan |
| `DD` | 2-digit day | 05 |
| `D` | Day number | 5 |
| `dddd` | Full weekday | Monday |
| `ddd` | Abbreviated weekday | Mon |

### Common Patterns by Locale

| Locale | Pattern | Example |
|--------|---------|---------|
| en-US | `MMMM D, YYYY` | January 15, 2024 |
| en-GB | `D MMMM YYYY` | 15 January 2024 |
| de-DE | `D. MMMM YYYY` | 15. Januar 2024 |
| fr-FR | `D MMMM YYYY` | 15 janvier 2024 |
| es-ES | `D de MMMM de YYYY` | 15 de enero de 2024 |
| ja-JP | `YYYY年M月D日` | 2024年1月15日 |
| zh-CN | `YYYY年M月D日` | 2024年1月15日 |
| ko-KR | `YYYY년 M월 D일` | 2024년 1월 15일 |

### Short Patterns

| Locale | Pattern | Example |
|--------|---------|---------|
| en-US | `M/D/YYYY` | 1/15/2024 |
| en-GB | `DD/MM/YYYY` | 15/01/2024 |
| de-DE | `DD.MM.YYYY` | 15.01.2024 |
| ja-JP | `YYYY/MM/DD` | 2024/01/15 |
| ISO | `YYYY-MM-DD` | 2024-01-15 |

## Month Names

### English

| Number | Full | Abbreviated |
|--------|------|-------------|
| 1 | January | Jan |
| 2 | February | Feb |
| 3 | March | Mar |
| 4 | April | Apr |
| 5 | May | May |
| 6 | June | Jun |
| 7 | July | Jul |
| 8 | August | Aug |
| 9 | September | Sep |
| 10 | October | Oct |
| 11 | November | Nov |
| 12 | December | Dec |

### German

| Number | Full | Abbreviated |
|--------|------|-------------|
| 1 | Januar | Jan |
| 2 | Februar | Feb |
| 3 | März | Mär |
| 4 | April | Apr |
| 5 | Mai | Mai |
| 6 | Juni | Jun |
| 7 | Juli | Jul |
| 8 | August | Aug |
| 9 | September | Sep |
| 10 | Oktober | Okt |
| 11 | November | Nov |
| 12 | Dezember | Dez |

### Japanese

| Number | Name |
|--------|------|
| 1 | 1月 (ichigatsu) |
| 2 | 2月 (nigatsu) |
| 3 | 3月 (sangatsu) |
| ... | ... |
| 12 | 12月 (jūnigatsu) |

## Weekday Names

### English

| Number | Full | Abbreviated |
|--------|------|-------------|
| 0 | Sunday | Sun |
| 1 | Monday | Mon |
| 2 | Tuesday | Tue |
| 3 | Wednesday | Wed |
| 4 | Thursday | Thu |
| 5 | Friday | Fri |
| 6 | Saturday | Sat |

### Week Start

| Locale | Week Starts |
|--------|-------------|
| en-US | Sunday |
| en-GB | Monday |
| de-DE | Monday |
| ja-JP | Sunday |
| ISO 8601 | Monday |

## Date Ranges

### Period Display

| Period | en-US | de-DE |
|--------|-------|-------|
| Month | January 2024 | Januar 2024 |
| Quarter | Q1 2024 | Q1 2024 |
| Year | 2024 | 2024 |

### Range Display

| Range | en-US | de-DE |
|-------|-------|-------|
| Same month | Jan 1-15, 2024 | 1.-15. Jan 2024 |
| Different months | Jan 1 - Feb 15, 2024 | 1. Jan - 15. Feb 2024 |

## Fiscal Dates

### Fiscal Year

When fiscal year differs from calendar year:

```
option "fiscal_year_start" "04-01"  ; April 1

FY2024 = April 1, 2023 - March 31, 2024
```

### Fiscal Quarter Display

| Quarter | Calendar | Fiscal (Apr start) |
|---------|----------|-------------------|
| Q1 | Jan-Mar | Apr-Jun |
| Q2 | Apr-Jun | Jul-Sep |
| Q3 | Jul-Sep | Oct-Dec |
| Q4 | Oct-Dec | Jan-Mar |

## Relative Dates

### Keywords (Display Only)

| Keyword | Meaning |
|---------|---------|
| Today | Current date |
| Yesterday | Previous day |
| Tomorrow | Next day |
| This week | Current week |
| Last month | Previous month |
| This year | Current year |

### Relative in Reports

```
Transactions from last 30 days
Balance as of yesterday
```

## Configuration

### Option Syntax

```
option "date_format" "DD.MM.YYYY"
option "locale" "de-DE"
```

### Format String

```python
def format_date(date: Date, pattern: str, locale: str) -> str:
    """
    Format date according to pattern and locale.

    pattern: strftime-like or CLDR pattern
    locale: BCP 47 locale code
    """
```

## Implementation

### Formatting

```python
import babel.dates

def format_date_locale(date, locale='en_US'):
    return babel.dates.format_date(date, format='long', locale=locale)

# Examples:
# format_date_locale(date(2024, 1, 15), 'en_US') → "January 15, 2024"
# format_date_locale(date(2024, 1, 15), 'de_DE') → "15. Januar 2024"
```

### Parsing (Canonical Only)

```python
import re

def parse_date(s: str) -> Date:
    """Parse ISO 8601 date only."""
    match = re.match(r'(\d{4})[-/](\d{2})[-/](\d{2})', s)
    if not match:
        raise ParseError(f"Invalid date format: {s}")
    return Date(int(match[1]), int(match[2]), int(match[3]))
```

## Error Messages

### Ambiguous Date Warning

```
WARNING: Ambiguous date format
  --> ledger.beancount:42:1
   |
42 | 01/02/2024 * "Purchase"
   | ^^^^^^^^^^
   |
   = is this January 2 or February 1?
   = hint: use YYYY-MM-DD format
```

### Invalid Date

```
ERROR: Invalid date
  --> ledger.beancount:42:1
   |
42 | 2024-13-45 * "Purchase"
   | ^^^^^^^^^^
   |
   = month 13 and day 45 are invalid
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Input format | YYYY-MM-DD | Multiple | Multiple |
| Slash separator | Yes | Yes | Yes |
| Locale output | Limited | Yes | Yes |
| Month names | No | Yes | Yes |
| Smart dates | No | Yes | Yes |
