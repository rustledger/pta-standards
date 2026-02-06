# Prices

This document specifies the price model for plain text accounting systems.

## Definition

A **Price** represents the exchange rate between two commodities at a specific point in time.

```
Price = {
  date: Date,
  base: Commodity,
  quote: Amount
}
```

Interpretation: On `date`, 1 unit of `base` is worth `quote`.

## Terminology

| Term | Definition | Example |
|------|------------|---------|
| Base | The commodity being priced | EUR |
| Quote | The value in another commodity | 1.08 USD |
| Rate | The numeric exchange rate | 1.08 |
| Quote Currency | The commodity of the quote | USD |

## Price Directive Syntax

### Basic Syntax

```
2024-01-15 price EUR 1.08 USD
```

Meaning: On 2024-01-15, 1 EUR = 1.08 USD

### Components

```
<date> price <base> <amount>
```

- `date`: When this price applies
- `base`: The commodity being priced
- `amount`: Value per unit (number + quote commodity)

## Examples

### Currency Exchange Rate

```
2024-01-15 price EUR 1.08 USD
2024-01-15 price GBP 1.27 USD
2024-01-15 price JPY 0.0067 USD
```

### Stock Prices

```
2024-01-15 price AAPL 185.92 USD
2024-01-15 price GOOG 140.25 USD
2024-01-15 price MSFT 390.50 USD
```

### Cryptocurrency

```
2024-01-15 price BTC 42500.00 USD
2024-01-15 price ETH 2500.00 USD
```

### Cross Rates

```
2024-01-15 price EUR 0.85 GBP
2024-01-15 price EUR 158.50 JPY
```

## Implicit Prices

### From Transactions

Prices are implicitly recorded from transaction postings:

```
2024-01-15 * "Currency exchange"
  Assets:EUR  100 EUR @ 1.08 USD
  Assets:USD
```

This creates implicit price: 2024-01-15: EUR = 1.08 USD

### From Cost Specifications

```
2024-01-15 * "Buy stock"
  Assets:Stock  10 AAPL {185.92 USD}
  Assets:Cash
```

This creates implicit price: 2024-01-15: AAPL = 185.92 USD

## Price Database

### Structure

The price database stores all known prices:

```python
PriceDatabase = Dict[
    (Commodity, Commodity),  # (base, quote)
    List[(Date, Decimal)]    # sorted by date
]
```

### Operations

| Operation | Description |
|-----------|-------------|
| `add(date, base, quote, rate)` | Add a price point |
| `get(date, base, quote)` | Get price on date |
| `latest(base, quote)` | Get most recent price |
| `range(start, end, base, quote)` | Get prices in range |

## Price Lookup

### Exact Match

Find price on specific date:

```python
price = db.get(date=2024-01-15, base="EUR", quote="USD")
# Returns: 1.08
```

### Fallback to Previous

If no price on exact date, use most recent:

```python
# No price on 2024-01-16
# Falls back to 2024-01-15 price
price = db.get(date=2024-01-16, base="EUR", quote="USD")
# Returns: 1.08 (from 2024-01-15)
```

### No Price Available

```python
price = db.get(date=2024-01-15, base="XYZ", quote="USD")
# Returns: None (no price history for XYZ)
```

## Inverse Prices

### Automatic Inversion

If only one direction is stored, the inverse can be computed:

```
Stored: 2024-01-15 price EUR 1.08 USD

Query: USD → EUR
Computed: 1 USD = 1/1.08 EUR ≈ 0.926 EUR
```

### Implementation

```python
def get_price(base, quote, date):
    # Try direct lookup
    if (base, quote) in prices:
        return lookup(base, quote, date)

    # Try inverse
    if (quote, base) in prices:
        rate = lookup(quote, base, date)
        return 1 / rate

    return None
```

## Price Chains

### Indirect Conversion

When no direct price exists, chain through intermediate:

```
Stored:
  2024-01-15 price EUR 1.08 USD
  2024-01-15 price GBP 1.27 USD

Query: EUR → GBP
Computed: 1 EUR = 1.08 USD = 1.08/1.27 GBP ≈ 0.850 GBP
```

### Chain Limits

Implementations MAY limit chain length:

```
Max chain length: 2 (base → intermediate → quote)
```

## Market Value Calculation

### Single Commodity

```python
holdings = 100 EUR
price = 1.08 USD/EUR
market_value = 100 × 1.08 = 108 USD
```

### Portfolio Valuation

```python
portfolio = {
    "USD": 1000,
    "EUR": 500,
    "AAPL": 10
}

prices = {
    "EUR": 1.08 USD,
    "AAPL": 185.92 USD
}

market_value = (
    1000 +           # USD (base currency)
    500 × 1.08 +     # EUR → USD
    10 × 185.92      # AAPL → USD
) = 1000 + 540 + 1859.20 = 3399.20 USD
```

## Price Sources

### Manual Entry

```
2024-01-15 price AAPL 185.92 USD
```

### Transaction-Derived

```
2024-01-15 * "Trade"
  Assets:Stock  10 AAPL @ 185.92 USD
  ...
```

### External Fetch

Tools may fetch prices from external sources:

```bash
bean-price ledger.beancount
```

## Price Metadata

### Source Tracking

```
2024-01-15 price AAPL 185.92 USD
  source: "Yahoo Finance"
  time: "16:00 EST"
```

### Bid/Ask Spread

```
2024-01-15 price EUR 1.08 USD
  bid: 1.0795
  ask: 1.0805
```

## Temporal Considerations

### Point-in-Time

Prices are point-in-time snapshots:

```
2024-01-14 price AAPL 184.00 USD  ; Yesterday
2024-01-15 price AAPL 185.92 USD  ; Today
2024-01-16 price AAPL 187.50 USD  ; Tomorrow
```

### Intraday Prices

Some systems support intraday prices:

```
2024-01-15 price AAPL 185.00 USD
  time: "09:30"

2024-01-15 price AAPL 185.92 USD
  time: "16:00"
```

### End-of-Day Convention

Most PTA systems use end-of-day prices:

```
; Price applies to entire day
2024-01-15 price AAPL 185.92 USD
```

## Unrealized Gains

### Calculation

```
Cost basis: 10 AAPL @ 150 USD = 1500 USD
Market value: 10 × 185.92 USD = 1859.20 USD
Unrealized gain: 1859.20 - 1500 = 359.20 USD
```

### Booking Entry

```
2024-01-15 * "Mark to market"
  Assets:Stock            359.20 AAPL-GAIN
  Income:Unrealized-Gains -359.20 USD
```

## Validation

### Invalid Price

```
ERROR: Invalid price directive
  --> ledger.beancount:42:1
   |
42 | 2024-01-15 price AAPL -185 USD
   |                       ^^^^
   |
   = price cannot be negative
```

### Unknown Commodity

```
WARNING: Unknown commodity in price
  --> ledger.beancount:42:15
   |
42 | 2024-01-15 price XYZ 100 USD
   |                  ^^^
   |
   = no other references to XYZ found
```

## Implementation Model

```python
@dataclass
class Price:
    date: date
    base: str
    quote: Amount

    @property
    def rate(self) -> Decimal:
        return self.quote.number

    @property
    def quote_currency(self) -> str:
        return self.quote.commodity


class PriceDatabase:
    def __init__(self):
        self._prices: Dict[Tuple[str, str], List[Tuple[date, Decimal]]] = {}

    def add(self, price: Price):
        key = (price.base, price.quote_currency)
        if key not in self._prices:
            self._prices[key] = []
        bisect.insort(self._prices[key], (price.date, price.rate))

    def get(self, base: str, quote: str, as_of: date) -> Optional[Decimal]:
        key = (base, quote)
        if key in self._prices:
            prices = self._prices[key]
            # Find most recent price <= as_of
            idx = bisect.bisect_right(prices, (as_of, Decimal('inf'))) - 1
            if idx >= 0:
                return prices[idx][1]

        # Try inverse
        inverse_key = (quote, base)
        if inverse_key in self._prices:
            prices = self._prices[inverse_key]
            idx = bisect.bisect_right(prices, (as_of, Decimal('inf'))) - 1
            if idx >= 0:
                return 1 / prices[idx][1]

        return None
```

## Serialization

### Text Format

```
2024-01-15 price EUR 1.08 USD
```

### JSON Format

```json
{
  "date": "2024-01-15",
  "base": "EUR",
  "quote": {
    "number": "1.08",
    "commodity": "USD"
  }
}
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Directive | `price` | `P` | `P` |
| Syntax | `price BASE AMOUNT` | `P DATE BASE RATE QUOTE` | `P DATE BASE RATE QUOTE` |
| Implicit | From `@` prices | From `@` prices | From `@` prices |
| Inversion | Automatic | Manual | Automatic |
| Chains | Limited | No | No |
