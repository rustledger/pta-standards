# Price Directive

## Overview

The `price` directive records the market exchange rate between two currencies at a specific point in time. These prices are used for currency conversion, market value calculations, and reporting.

## Syntax

```ebnf
price = date WHITESPACE "price" WHITESPACE base_currency WHITESPACE amount
        (NEWLINE metadata)*

base_currency = currency
amount        = number currency
```

## Components

### Date

The date and time the price was observed. Prices are effective from this date forward until a newer price is recorded.

### Base Currency

The currency being priced.

### Quote Amount

The price expressed as an amount in the quote currency.

## Interpretation

```beancount
2024-01-15 price AAPL  185.50 USD
```

This means: "On 2024-01-15, 1 AAPL = 185.50 USD"

Or equivalently: the exchange rate from AAPL to USD is 185.50.

## Examples

### Stock Prices

```beancount
2024-01-15 price AAPL  185.50 USD
2024-01-15 price MSFT  390.25 USD
2024-01-15 price GOOGL 141.80 USD
```

### Currency Exchange Rates

```beancount
2024-01-15 price EUR  1.0875 USD
2024-01-15 price GBP  1.2650 USD
2024-01-15 price JPY  0.0067 USD
```

### Cryptocurrency

```beancount
2024-01-15 price BTC  42500.00 USD
2024-01-15 price ETH   2520.00 USD
```

### Mutual Funds

```beancount
2024-01-15 price VTSAX  118.45 USD
2024-01-15 price VTIAX   31.22 USD
```

### With Metadata

```beancount
2024-01-15 price AAPL  185.50 USD
  source: "Yahoo Finance"
  time: "16:00:00"
  type: "close"
```

## Price Database

Implementations maintain a price database mapping:

```
(base_currency, quote_currency, date) → price
```

### Price Lookup

When looking up a price:

1. Find the most recent price on or before the requested date
2. If no direct price exists, attempt conversion through intermediate currencies

### Price Chain

```beancount
2024-01-15 price EUR  1.10 USD
2024-01-15 price GBP  1.15 EUR

; To convert GBP to USD:
; GBP → EUR → USD
; 1 GBP = 1.15 EUR = 1.15 × 1.10 USD = 1.265 USD
```

## Implicit Prices

Transactions with price annotations create implicit prices:

```beancount
2024-01-15 * "Buy stock"
  Assets:Stock  10 AAPL {185.50 USD}
  Assets:Cash  -1855.00 USD

; Implicitly creates:
; 2024-01-15 price AAPL  185.50 USD
```

This requires loading the `implicit_prices` plugin:

```beancount
plugin "beancount.plugins.implicit_prices"
```

> **Note**: There is no `infer_implicit_prices` option. Implicit price generation is provided by a plugin, not a core option.

## Inverted Prices

Prices can be inverted for reverse conversion:

```beancount
2024-01-15 price USD  0.92 EUR  ; 1 USD = 0.92 EUR
```

Implementations SHOULD support both directions:
- USD → EUR: use price directly
- EUR → USD: use 1/0.92 = 1.087 USD

## Use Cases

### Portfolio Valuation

```beancount
; Record daily prices for holdings
2024-01-15 price AAPL  185.50 USD
2024-01-16 price AAPL  187.25 USD
2024-01-17 price AAPL  184.00 USD

; Query market value of portfolio at any date
```

### Currency Conversion

```beancount
; Track exchange rates
2024-01-15 price EUR  1.0875 USD

; Convert EUR holdings to USD for reporting
```

### Historical Analysis

```beancount
; Load historical prices for analysis
2023-01-01 price BTC  16500 USD
2023-06-01 price BTC  27000 USD
2024-01-01 price BTC  42000 USD
```

## Price Sources

Common price sources and their metadata:

```beancount
2024-01-15 price AAPL  185.50 USD
  source: "yahoo"

2024-01-15 price EUR  1.0875 USD
  source: "ecb"  ; European Central Bank

2024-01-15 price BTC  42500 USD
  source: "coinbase"
```

## Validation

Prices have no specific validation errors, but:

- Currency symbols must be valid
- Numbers must be positive
- Date must be valid

## Price Fetching

Beancount implementations often include tools to fetch prices automatically:

```bash
# Fetch missing prices
bean-price ledger.beancount

# Fetch prices for specific date range
bean-price --date 2024-01-15 ledger.beancount
```

Price sources are configured via commodity metadata:

```beancount
2024-01-01 commodity AAPL
  price: "USD:yahoo/AAPL"

2024-01-01 commodity EUR
  price: "USD:oanda/EUR"
```

## Multiple Prices Per Day

Multiple prices for the same currency pair on the same date are allowed:

```beancount
2024-01-15 price BTC  42500 USD
  time: "09:00:00"

2024-01-15 price BTC  43200 USD
  time: "12:00:00"

2024-01-15 price BTC  42800 USD
  time: "16:00:00"
```

Implementations typically use the last price for the day when querying.

## Implementation Notes

1. Store prices in a database indexed by (base, quote, date)
2. Support price lookup with date range
3. Implement transitive price conversion
4. Optionally generate prices from transaction annotations
5. Handle inverted prices for bidirectional conversion
