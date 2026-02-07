# Beancount to hledger Edge Cases

This document covers edge cases for Beancount to hledger conversion.

## Balance Assertion Timing

Same issue as with Ledger: Beancount checks at start of day, hledger checks after posting.

**Solution:** Use previous day for balance assertions.

## Lot Tracking

### Beancount Lots

**Beancount:**
```beancount
Assets:Brokerage  10 AAPL {185.00 USD, 2024-01-15, "lot1"}
```

hledger doesn't have built-in lot tracking with the same syntax.

**hledger workaround:**
```hledger
Assets:Brokerage  10 AAPL @ 185.00 USD
  ; lot-date: 2024-01-15
  ; lot-label: lot1
```

### Booking Methods

Beancount's booking methods (`FIFO`, `LIFO`, etc.) have no hledger equivalent. Document as metadata.

## Cost Basis Reduction

**Beancount:**
```beancount
Assets:Brokerage  -5 AAPL {185.00 USD, 2024-01-15}
```

**hledger:**
```hledger
Assets:Brokerage  -5 AAPL @ 185.00 USD
  ; original-cost: 185.00 USD
  ; original-date: 2024-01-15
```

## Multi-Currency Transactions

**Beancount:**
```beancount
2024-01-15 * "Exchange"
  Assets:USD  -100.00 USD
  Assets:EUR  85.00 EUR @ 1.1765 USD
```

**hledger:**
```hledger
2024-01-15 * Exchange
  Assets:USD  -100.00 USD
  Assets:EUR  85.00 EUR @ 1.1765 USD
```

Both formats handle this similarly.

## Tolerance

Beancount's `inferred_tolerance_default` option has no hledger equivalent.

**Workaround:** Ensure transactions are exactly balanced.

## Plugins

Beancount plugins must be executed before conversion. The output includes plugin-generated transactions.

## Options

Many Beancount options have no hledger equivalent:

| Beancount Option | hledger Equivalent |
|------------------|-------------------|
| `operating_currency` | None |
| `inferred_tolerance_default` | None |
| `booking_method` | None |
| `title` | None |

Document as comments:
```hledger
; Beancount options:
; operating_currency: USD
; title: My Ledger
```

## Account Types

**Beancount:** Uses prefix convention (Assets:, Liabilities:, etc.)

**hledger:** Can use `account` directive with type:
```hledger
account Assets:Checking  ; type: A
account Liabilities:CreditCard  ; type: L
```

## Payee Handling

**Beancount:**
```beancount
2024-01-15 * "The Store" "Bought supplies"
```

**hledger:**
```hledger
2024-01-15 * The Store | Bought supplies
```

If payee contains `|`:
```hledger
2024-01-15 * The Store - Division | Bought supplies
```

## Decimal Mark

Beancount uses `.` as decimal mark. hledger can use `.` or `,` with `decimal-mark` directive.

If source uses `.`:
```hledger
decimal-mark .
```

## Recommendations

1. **Execute plugins first**
2. **Preserve all metadata** as comments
3. **Document lost features** with comments
4. **Validate output** with `hledger check`
5. **Round-trip test** critical data
