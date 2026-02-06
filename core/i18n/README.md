# Internationalization (i18n)

This document provides an overview of internationalization support in plain text accounting systems.

## Overview

Plain text accounting systems support international use through:

- **Unicode text** for narrations, payees, and accounts in any language
- **Flexible date formats** for regional conventions
- **Locale-aware number formatting** for display
- **Currency symbols** for familiar representation

## Scope

### What is Internationalized

| Component | Internationalization |
|-----------|---------------------|
| File encoding | UTF-8 universal support |
| Text content | Any Unicode script |
| Date display | Regional format options |
| Number display | Locale-aware formatting |
| Currency display | Symbol placement options |

### What is NOT Internationalized

| Component | Standard |
|-----------|----------|
| Date input | ISO 8601 (YYYY-MM-DD) |
| Decimal separator | Period (.) |
| Keywords | English (open, close, etc.) |
| Error messages | English (typically) |

## Design Principle

**Storage is canonical; display is localized.**

- Source files use a single, unambiguous canonical format
- Reports and output can be localized for display
- Round-trip preservation is guaranteed

## i18n Documents

| Document | Description |
|----------|-------------|
| [date-formats.md](date-formats.md) | Date formatting for different locales |
| [number-formats.md](number-formats.md) | Number and decimal formatting |
| [currency-symbols.md](currency-symbols.md) | Currency symbol placement |

## Locale Model

### Locale Identifier

Locales follow BCP 47 format:

```
en-US     ; English, United States
de-DE     ; German, Germany
ja-JP     ; Japanese, Japan
zh-Hans   ; Chinese, Simplified
```

### Locale Components

| Component | Description | Example |
|-----------|-------------|---------|
| Language | ISO 639-1 | `en`, `de`, `ja` |
| Region | ISO 3166-1 | `US`, `DE`, `JP` |
| Script | ISO 15924 | `Hans`, `Hant` |

### Default Locale

When no locale is specified:

- Input parsing uses canonical format
- Output uses implementation default (typically `en-US`)

## Text Content

### Unicode Support

All text fields support full Unicode:

```
2024-01-15 * "カフェ" "朝のコーヒー"
  資産:銀行:普通預金  -500 JPY
  費用:食費:外食

2024-01-15 * "Кафе" "Утренний кофе"
  Активы:Банк:Текущий  -200 RUB
  Расходы:Еда:Кафе
```

### Account Names

Account names support Unicode letters:

```
; Japanese
資産:銀行:普通預金

; German
Vermögen:Bank:Girokonto

; Arabic
الأصول:البنك:الحساب-الجاري
```

### Character Restrictions

Some characters are restricted in identifiers:

| Context | Restriction |
|---------|-------------|
| Account separator | `:` reserved |
| Commodity | Format-specific rules |
| Metadata keys | Alphanumeric + limited symbols |

## Date Handling

### Input Format

Source files use ISO 8601:

```
2024-01-15    ; Unambiguous
```

### Display Format

Reports can localize dates:

| Locale | Display |
|--------|---------|
| en-US | January 15, 2024 |
| en-GB | 15 January 2024 |
| de-DE | 15. Januar 2024 |
| ja-JP | 2024年1月15日 |

See [date-formats.md](date-formats.md) for details.

## Number Handling

### Input Format

Source files use period decimal separator:

```
1234.56       ; Canonical
```

### Display Format

Reports can localize numbers:

| Locale | Display |
|--------|---------|
| en-US | 1,234.56 |
| de-DE | 1.234,56 |
| fr-FR | 1 234,56 |
| ja-JP | 1,234.56 |

See [number-formats.md](number-formats.md) for details.

## Currency Handling

### Input Format

Source files use commodity codes:

```
100.00 USD
50.00 EUR
5000 JPY
```

### Display Format

Reports can use currency symbols:

| Currency | Symbol | Placement |
|----------|--------|-----------|
| USD | $ | Prefix |
| EUR | € | Prefix or suffix |
| GBP | £ | Prefix |
| JPY | ¥ | Prefix |

See [currency-symbols.md](currency-symbols.md) for details.

## Implementation Guidance

### Separation of Concerns

```
┌─────────────────┐
│   Source File   │  Canonical format
│  (UTF-8, ISO)   │
└────────┬────────┘
         │ Parse
         ▼
┌─────────────────┐
│  Internal Model │  Normalized data
│   (in memory)   │
└────────┬────────┘
         │ Format
         ▼
┌─────────────────┐
│     Output      │  Localized display
│    (Reports)    │
└─────────────────┘
```

### Locale Configuration

```
option "locale" "de-DE"
option "date_format" "%d.%m.%Y"
option "number_format" "1.234,56"
```

### Format Functions

```python
def format_date(date: Date, locale: str) -> str:
    """Format date for display in given locale."""
    ...

def format_amount(amount: Amount, locale: str) -> str:
    """Format amount with localized number and symbol."""
    ...
```

## Error Messages

### Localized Errors

Error messages MAY be localized:

```
; English
ERROR: Account not opened

; German
FEHLER: Konto nicht eröffnet

; Japanese
エラー: 口座が開設されていません
```

### Location References

Source locations use universal format:

```
  --> ledger.beancount:42:3
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Unicode content | Full | Full | Full |
| Date input | ISO only | Multiple | Multiple |
| Number input | Period only | Period only | Period only |
| Locale config | Limited | Yes | Yes |
| Symbol display | Code only | Symbols | Symbols |
