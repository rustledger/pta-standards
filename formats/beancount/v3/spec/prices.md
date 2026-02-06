# Price Annotations

## Overview

Price annotations record the market exchange rate at the time of a transaction. Unlike cost specifications, prices are informational and typically don't affect transaction balancing when a cost is also present.

## Syntax

```ebnf
price_annotation = "@" amount      ; Per-unit price
                 | "@@" amount     ; Total price
```

## Price Types

### Per-Unit Price `@`

Specifies the price per unit:

```beancount
; 100 EUR at 1.10 USD each
Assets:EUR  100 EUR @ 1.10 USD
```

### Total Price `@@`

Specifies the total price for all units:

```beancount
; 100 EUR for 110 USD total
Assets:EUR  100 EUR @@ 110 USD
```

Per-unit price is computed as: `110 / 100 = 1.10 USD`

## Weight Calculation

### Price Without Cost

When only a price annotation is present (no cost spec), the price determines the posting weight:

```beancount
2024-01-15 * "Currency exchange"
  Assets:EUR   100 EUR @ 1.10 USD    ; Weight: 100 × 1.10 = 110 USD
  Assets:USD  -110 USD               ; Weight: -110 USD
  ; Transaction balances in USD
```

### Price With Cost

When both cost and price are present, the **cost** determines the weight (price is informational):

```beancount
2024-01-15 * "Sell stock"
  Assets:Stock  -10 AAPL {150 USD} @ 185 USD
  ; Weight: 10 × 150 = 1500 USD (uses cost, not price)

  Assets:Cash   1850 USD              ; Weight: 1850 USD
  Income:CapitalGains  -350 USD       ; Weight: -350 USD
  ; Balances: 1500 - 1850 + 350 = 0 ✓
```

The `@ 185 USD` records that AAPL was trading at $185 but doesn't affect balancing.

## Implicit Price Generation

Transactions with price annotations can generate implicit price entries:

```beancount
option "infer_implicit_prices" "TRUE"

2024-01-15 * "Exchange"
  Assets:EUR  100 EUR @ 1.10 USD
  Assets:USD

; Implicitly generates:
; 2024-01-15 price EUR 1.10 USD
```

This populates the price database for later valuation.

## Currency Conversion

### Simple Exchange

```beancount
2024-01-15 * "Buy Euros"
  Assets:EUR   1000 EUR @ 1.0875 USD
  Assets:USD  -1087.50 USD
```

### With Fees

```beancount
2024-01-15 * "Exchange with fee"
  Assets:EUR      1000 EUR @ 1.09 USD
  Expenses:Fees     5.00 USD
  Assets:USD    -1095.00 USD
```

### Triangular Conversion

```beancount
; EUR → GBP via USD rates
2024-01-15 * "EUR to GBP"
  Assets:EUR  -1000 EUR @ 1.10 USD
  Assets:GBP    850 GBP @ 1.2941 USD
  ; EUR: 1000 × 1.10 = 1100 USD
  ; GBP: 850 × 1.2941 = 1100 USD
  ; Balances!
```

## Price vs. Cost

| Aspect | Cost `{...}` | Price `@` |
|--------|--------------|-----------|
| Purpose | Track acquisition basis | Record market rate |
| Creates lots | Yes | No |
| Affects weight | Always | Only without cost |
| For reductions | Matches existing lots | Informational only |
| Capital gains | Determines basis | Records sale price |

### Combined Example

```beancount
2024-01-15 * "Buy stock"
  Assets:Stock  10 AAPL {150 USD}     ; Cost: creates lot at 150
  Assets:Cash  -1500 USD

2024-06-15 * "Sell at profit"
  Assets:Stock  -10 AAPL {150 USD} @ 185 USD
  ; Cost {150 USD}: matches lot, weight = 1500 USD
  ; Price @ 185 USD: records market price (informational)

  Assets:Cash   1850 USD
  Income:CapitalGains  -350 USD       ; Gain: (185-150) × 10
```

## Total Price Precision

Total price (`@@`) avoids rounding issues:

```beancount
; Per-unit: may have rounding
Assets:Stock  7 AAPL @ 185.714285 USD

; Total: exact amount
Assets:Stock  7 AAPL @@ 1300 USD
; Per-unit computed: 1300 / 7 = 185.7142857...
```

## Price Direction

Prices are always "base @ quote":

```beancount
; 1 EUR = 1.10 USD
Assets:EUR  100 EUR @ 1.10 USD

; 1 USD = 0.91 EUR (inverse)
Assets:USD  100 USD @ 0.91 EUR
```

Both express the same exchange rate from different directions.

## Examples

### Stock Sale with Gain

```beancount
2024-06-15 * "Sell Apple stock"
  Assets:Brokerage  -50 AAPL {150.00 USD} @ 195.50 USD
  Assets:Cash       9775.00 USD
  Income:CapitalGains:Long
```

### Currency for Travel

```beancount
2024-03-01 * "Get travel money"
  Assets:Cash:EUR   500 EUR @ 1.08 USD
  Assets:Checking  -540 USD
```

### Crypto Trading

```beancount
2024-01-15 * "Buy Bitcoin"
  Assets:Crypto:BTC  0.5 BTC @ 42000 USD
  Assets:Checking   -21000 USD

2024-06-15 * "Sell Bitcoin"
  Assets:Crypto:BTC  -0.5 BTC {42000 USD} @ 65000 USD
  Assets:Checking    32500 USD
  Income:CapitalGains:Crypto
```

### Multi-Currency Portfolio

```beancount
2024-01-15 * "International purchase"
  Assets:Brokerage:EU  100 BMW.DE {85.50 EUR}
  Assets:Cash:EUR     -8550 EUR @ 1.09 USD
  ; BMW cost: 8550 EUR
  ; EUR weight: 8550 × 1.09 = 9319.50 USD equivalent
```

## Price in Balance Assertions

Balance assertions don't use prices—they check units:

```beancount
; Checks that you have 100 EUR, regardless of USD value
2024-01-15 balance Assets:EUR  100 EUR

; To check USD equivalent, use reporting tools, not balance
```

## Validation

Price annotations have minimal validation:
- Amount must be valid
- Currency must be valid

The price value itself is not validated against market data.

## Implementation Notes

1. Parse `@` as per-unit, `@@` as total
2. Compute weight based on presence of cost
3. Optionally generate implicit price entries
4. Store price for market value calculations
5. Price doesn't create or modify lots
