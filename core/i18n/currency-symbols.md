# Currency Symbols

This document specifies currency symbol handling for internationalization in plain text accounting.

## Input vs. Output

### Input (Commodity Codes)

Source files use commodity codes, not symbols:

```
100.00 USD    ; Canonical (code)
100.00 EUR
100.00 GBP
```

### Output (Symbols Optional)

Reports MAY display currency symbols:

```
$100.00       ; USD with symbol
€100.00       ; EUR with symbol
£100.00       ; GBP with symbol
```

## ISO 4217 Currency Codes

### Major Currencies

| Code | Name | Symbol | Decimals |
|------|------|--------|----------|
| USD | US Dollar | $ | 2 |
| EUR | Euro | € | 2 |
| GBP | British Pound | £ | 2 |
| JPY | Japanese Yen | ¥ | 0 |
| CHF | Swiss Franc | CHF | 2 |
| CNY | Chinese Yuan | ¥ / 元 | 2 |
| AUD | Australian Dollar | A$ | 2 |
| CAD | Canadian Dollar | C$ | 2 |
| INR | Indian Rupee | ₹ | 2 |
| KRW | South Korean Won | ₩ | 0 |
| BRL | Brazilian Real | R$ | 2 |
| MXN | Mexican Peso | $ | 2 |
| RUB | Russian Ruble | ₽ | 2 |

### Cryptocurrencies

| Code | Name | Symbol | Decimals |
|------|------|--------|----------|
| BTC | Bitcoin | ₿ | 8 |
| ETH | Ethereum | Ξ | 18 |
| USDT | Tether | ₮ | 6 |
| USDC | USD Coin | USDC | 6 |

## Symbol Placement

### Prefix Symbols

Symbol before the amount:

| Currency | Format | Example |
|----------|--------|---------|
| USD | $X | $100.00 |
| EUR | €X | €100.00 |
| GBP | £X | £100.00 |
| JPY | ¥X | ¥10,000 |

### Suffix Symbols

Symbol after the amount:

| Currency | Format | Example |
|----------|--------|---------|
| EUR (some) | X € | 100,00 € |
| SEK | X kr | 100 kr |
| CZK | X Kč | 100 Kč |
| PLN | X zł | 100 zł |

### Locale-Dependent Placement

| Currency | en-US | de-DE | fr-FR |
|----------|-------|-------|-------|
| EUR | €100.00 | 100,00 € | 100,00 € |
| USD | $100.00 | 100,00 $ | 100,00 $ |

## Symbol Characters

### Unicode Currency Symbols

| Symbol | Code Point | Name |
|--------|------------|------|
| $ | U+0024 | Dollar Sign |
| € | U+20AC | Euro Sign |
| £ | U+00A3 | Pound Sign |
| ¥ | U+00A5 | Yen Sign |
| ₹ | U+20B9 | Indian Rupee Sign |
| ₩ | U+20A9 | Won Sign |
| ₽ | U+20BD | Ruble Sign |
| ₿ | U+20BF | Bitcoin Sign |
| ฿ | U+0E3F | Thai Baht Sign |

### Multi-Character Symbols

| Currency | Symbol | Characters |
|----------|--------|------------|
| AUD | A$ | A + $ |
| CAD | C$ | C + $ |
| HKD | HK$ | H + K + $ |
| NZD | NZ$ | N + Z + $ |
| BRL | R$ | R + $ |

## Symbol Ambiguity

### Dollar Variants

Multiple currencies use `$`:

| Currency | Disambiguation |
|----------|----------------|
| USD | $ or US$ |
| AUD | A$ |
| CAD | C$ |
| HKD | HK$ |
| MXN | Mex$ |
| NZD | NZ$ |

### Yen/Yuan

Both use ¥:

| Currency | Disambiguation |
|----------|----------------|
| JPY | ¥ |
| CNY | ¥ or 元 or CN¥ |

### Resolution in PTA

Use ISO codes to avoid ambiguity:

```
100.00 USD    ; Unambiguous
100.00 AUD    ; Unambiguous
100.00 CNY    ; Unambiguous
```

## Formatting Rules

### With Symbol (Display)

```python
def format_currency_symbol(amount: Amount, locale: str) -> str:
    """Format amount with currency symbol."""
    # Example outputs:
    # $1,234.56 (en-US)
    # 1.234,56 € (de-DE)
    # ¥1,234 (ja-JP)
```

### Without Symbol (Code)

```python
def format_currency_code(amount: Amount) -> str:
    """Format amount with currency code."""
    # Example output:
    # 1234.56 USD
```

### Negative Amounts

| Style | USD Example | EUR Example (de) |
|-------|-------------|------------------|
| Prefix minus | -$100.00 | -100,00 € |
| Parentheses | ($100.00) | (100,00 €) |
| Minus after | $-100.00 | 100,00- € |

## Narrow Symbols

### Space-Efficient Variants

| Currency | Normal | Narrow |
|----------|--------|--------|
| USD | US$ | $ |
| EUR | EUR | € |
| GBP | GB£ | £ |

### Usage Context

| Context | Symbol Type |
|---------|-------------|
| Tables | Narrow |
| Headers | Normal |
| Inline | Narrow |

## Commodity Declarations

### Symbol in Metadata

```
2024-01-01 commodity USD
  symbol: "$"
  symbol-position: "prefix"

2024-01-01 commodity EUR
  symbol: "€"
  symbol-position: "suffix"
```

### Precision in Metadata

```
2024-01-01 commodity JPY
  symbol: "¥"
  precision: 0

2024-01-01 commodity BTC
  symbol: "₿"
  precision: 8
```

## Report Formatting

### Balance Report

```
Account              Balance
──────────────────────────────
Assets:Checking     $1,234.56
Assets:Savings     €5,000.00
Assets:Investment  ¥100,000
```

### Mixed Currencies

When showing multiple currencies, use codes for clarity:

```
Total Holdings:
  1,234.56 USD
  5,000.00 EUR
  100,000 JPY
  0.5 BTC
```

## Configuration

### Symbol Display Option

```
option "currency_symbols" "TRUE"
option "symbol_position" "prefix"
```

### Per-Currency Configuration

```
option "currency_symbol" "USD:$"
option "currency_symbol" "EUR:€"
option "symbol_position" "EUR:suffix"
```

## Implementation

### Symbol Lookup

```python
CURRENCY_SYMBOLS = {
    'USD': ('$', 'prefix'),
    'EUR': ('€', 'prefix'),  # locale-dependent
    'GBP': ('£', 'prefix'),
    'JPY': ('¥', 'prefix'),
    'CNY': ('¥', 'prefix'),
    'INR': ('₹', 'prefix'),
    'KRW': ('₩', 'prefix'),
    'BTC': ('₿', 'prefix'),
}

def get_symbol(currency: str) -> tuple[str, str]:
    return CURRENCY_SYMBOLS.get(currency, (currency, 'suffix'))
```

### Formatting

```python
def format_with_symbol(amount: Amount, locale: str = 'en_US') -> str:
    symbol, position = get_symbol(amount.commodity)
    formatted_number = format_number(amount.number, locale)

    if position == 'prefix':
        return f"{symbol}{formatted_number}"
    else:
        return f"{formatted_number} {symbol}"
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Input symbols | No | Yes ($100) | Yes ($100) |
| Output symbols | Code only | Yes | Yes |
| Symbol definition | Metadata | Commodity directive | Commodity directive |
| Position config | No | Yes | Yes |
| Decimal override | No | Yes | Yes |
