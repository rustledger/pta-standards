# Commodities

This document specifies the commodity model for plain text accounting systems.

## Definition

A **Commodity** is a unit of measurement for amounts. Commodities include currencies, securities, cryptocurrencies, and arbitrary units.

## Commodity Types

### Currencies

Traditional fiat currencies:

```
USD    ; US Dollar
EUR    ; Euro
GBP    ; British Pound
JPY    ; Japanese Yen
CHF    ; Swiss Franc
```

### Securities

Stocks, bonds, and funds:

```
AAPL   ; Apple Inc.
GOOG   ; Alphabet Inc.
VTSAX  ; Vanguard Total Stock Market
BRK.A  ; Berkshire Hathaway Class A
```

### Cryptocurrencies

Digital currencies:

```
BTC    ; Bitcoin
ETH    ; Ethereum
USDC   ; USD Coin
```

### Custom Units

User-defined units:

```
HOURS      ; Time tracking
MILES      ; Distance
VACATION   ; Vacation days
POINTS     ; Loyalty points
```

## Naming Rules

### Identifier Format

| Format | Rule | Example |
|--------|------|---------|
| Beancount | Uppercase, starts with letter | `USD`, `AAPL` |
| Ledger | Any characters, quoted if needed | `$`, `"My Stock"` |
| hledger | Any characters, quoted if needed | `EUR`, `"COMP A"` |

### Beancount Rules

```
Character set: A-Z, 0-9, ', ., _, -
First character: A-Z
Length: 1-24 characters
```

Valid:
```
USD
AAPL
BRK.A
VAN-TSAX
US_BONDS
```

Invalid:
```
usd       ; lowercase
123       ; starts with digit
$         ; special character
A-very-long-commodity-name-exceeding-24-chars
```

### Quoted Commodities

Some formats allow quoted commodities with special characters:

```
"US Dollar"
"S&P 500"
"COMP A"
"401(k)"
```

## Commodity Declaration

### Explicit Declaration

```
2024-01-01 commodity USD
  name: "US Dollar"
  precision: 2
```

### Implicit Declaration

Many formats allow commodities without explicit declaration:

```
; First use implicitly declares USD
2024-01-15 * "Salary"
  Assets:Checking  1000 USD
  Income:Salary
```

## Commodity Metadata

### Standard Metadata

| Key | Description | Example |
|-----|-------------|---------|
| `name` | Full name | `"US Dollar"` |
| `precision` | Display decimal places | `2` |
| `symbol` | Display symbol | `"$"` |
| `symbol-position` | Before or after | `"prefix"` |
| `ticker` | Market ticker | `"AAPL"` |
| `isin` | ISIN code | `"US0378331005"` |
| `asset-class` | Classification | `"equity"` |

### Example Declaration

```
2024-01-01 commodity AAPL
  name: "Apple Inc."
  asset-class: "equity"
  ticker: "AAPL"
  isin: "US0378331005"
  exchange: "NASDAQ"
```

## Display Formatting

### Precision

The number of decimal places to display:

```
commodity USD
  precision: 2

; Displays as: 100.00 USD
```

### Symbol Display

```
commodity USD
  symbol: "$"
  symbol-position: "prefix"

; Displays as: $100.00
```

### Thousands Separator

```
commodity USD
  thousands-separator: ","

; Displays as: 1,000,000.00 USD
```

## Commodity Constraints

### Account Currency Constraints

Accounts may restrict allowed commodities:

```
2024-01-01 open Assets:Checking USD
2024-01-01 open Assets:Euro EUR
2024-01-01 open Assets:Investment USD, AAPL, GOOG
```

### Posting Validation

```
2024-01-15 * "Deposit"
  Assets:Checking  100 EUR    ; ERROR: Only USD allowed
  Income:Salary
```

## Operating Currencies

### Definition

Operating currencies are the primary currencies used for reporting:

```
option "operating_currency" "USD"
option "operating_currency" "EUR"
```

### Usage

- Reports may convert to operating currency
- Balance assertions often use operating currency
- Multi-currency totals show operating currencies

## Currency Equivalence

### Same Commodity

Two commodities are equivalent only if their identifiers match exactly:

```
USD == USD     ; true
USD == usd     ; false (case-sensitive in Beancount)
USD == $       ; false (different identifiers)
```

### Commodity Aliases

Some formats support aliases:

```
alias $ = USD

; These are equivalent:
100 $
100 USD
```

## Price Relationships

### Exchange Rates

Commodities relate through prices:

```
2024-01-15 price EUR 1.08 USD
```

This declares: 1 EUR = 1.08 USD

### Price Database

The collection of historical prices:

```
Date        Base  Quote   Rate
2024-01-01  EUR   USD     1.10
2024-01-15  EUR   USD     1.08
2024-02-01  EUR   USD     1.09
```

### Market Value

Convert holdings to operating currency:

```
Holdings: 100 EUR
Price: 1 EUR = 1.08 USD
Market Value: 108 USD
```

## Commodity Categories

### Asset Classes

| Class | Examples | Characteristics |
|-------|----------|-----------------|
| Cash | USD, EUR | Stable, liquid |
| Equity | AAPL, GOOG | Variable, market-valued |
| Fixed Income | BONDS | Interest-bearing |
| Crypto | BTC, ETH | Volatile, 24/7 |
| Real Assets | HOUSE | Illiquid, periodic valuation |

### Currency vs. Commodity

| Feature | Currency | Commodity |
|---------|----------|-----------|
| Cost basis | No | Yes |
| Price tracking | Exchange rates | Market prices |
| Lot tracking | No | Yes |
| Booking method | N/A | FIFO, LIFO, etc. |

## Inventory by Commodity

### Simple Holdings

```
Assets:Checking
  1000.00 USD
```

### Lot-Based Holdings

```
Assets:Investment
  100 AAPL {150.00 USD, 2024-01-15}
  50 AAPL {155.00 USD, 2024-02-01}
```

### Multi-Commodity Holdings

```
Assets:Portfolio
  1000.00 USD
  100 AAPL {150.00 USD}
  0.5 BTC {40000.00 USD}
```

## Validation

### Unknown Commodity

```
WARNING: Unknown commodity
  --> ledger.beancount:42:18
   |
42 |   Assets:Cash  100 XYZ
   |                    ^^^
   |
   = hint: add 'commodity XYZ' directive
```

### Invalid Commodity Name

```
ERROR: Invalid commodity name
  --> ledger.beancount:10:15
   |
10 | commodity 123invalid
   |           ^^^^^^^^^^
   |
   = commodity must start with uppercase letter
```

## Implementation Model

```python
@dataclass
class Commodity:
    name: str                          # Identifier (e.g., "USD")
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        return self.metadata.get('name', self.name)

    @property
    def precision(self) -> int:
        return self.metadata.get('precision', 2)

    @property
    def symbol(self) -> Optional[str]:
        return self.metadata.get('symbol')
```

## Serialization

### Text Format

```
2024-01-01 commodity USD
  name: "US Dollar"
```

### JSON Format

```json
{
  "name": "USD",
  "metadata": {
    "name": "US Dollar",
    "precision": 2,
    "symbol": "$"
  }
}
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Case | Uppercase required | Any | Any |
| Symbols | No (use identifiers) | Yes ($, €) | Yes |
| Quotes | Not for standard | Allowed | Allowed |
| Declaration | Optional | Not needed | Not needed |
| Metadata | Key-value | Comments | Comments |
