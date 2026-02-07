# Format Conversion Cheatsheet

Quick reference for converting between PTA formats.

## Date Formats

| Beancount | Ledger | hledger |
|-----------|--------|---------|
| `2024-01-15` | `2024/01/15` | `2024-01-15` |

## Transaction Structure

### Beancount
```beancount
2024-01-15 * "Payee" "Narration"
  #tag
  key: "value"
  Assets:Checking  -50.00 USD
  Expenses:Food
```

### Ledger
```ledger
2024/01/15 * Payee | Narration
  ; :tag:
  ; key: value
  Assets:Checking  $-50.00
  Expenses:Food
```

### hledger
```hledger
2024-01-15 * Payee | Narration
  ; tag:
  ; key: value
  Assets:Checking  $-50.00
  Expenses:Food
```

## Amount Syntax

| Beancount | Ledger | hledger |
|-----------|--------|---------|
| `100.00 USD` | `$100.00` | `$100.00` |
| `100.00 USD` | `100.00 USD` | `100.00 USD` |
| `100.00 EUR` | `€100.00` | `€100.00` |

## Tags

| Beancount | Ledger | hledger |
|-----------|--------|---------|
| `#tag` | `:tag:` | `tag:` |
| `#foo #bar` | `:foo:bar:` | `foo:, bar:` |

## Links

| Beancount | Ledger | hledger |
|-----------|--------|---------|
| `^link-id` | `; link: link-id` | `; link: link-id` |

## Metadata

| Beancount | Ledger | hledger |
|-----------|--------|---------|
| `key: "value"` | `; key: value` | `; key: value` |

## Balance Assertions

### Beancount
```beancount
2024-01-31 balance Assets:Checking 1000.00 USD
```

### Ledger
```ledger
2024/01/30 Balance check
    Assets:Checking    $0 = $1000.00
```

### hledger
```hledger
2024-01-30 Balance check
    Assets:Checking    $0 = $1000.00
```

Note: Beancount checks at start of day; others check after posting.

## Price Directives

### Beancount
```beancount
2024-01-15 price AAPL 185.00 USD
```

### Ledger/hledger
```
P 2024/01/15 AAPL $185.00
```

## Account Open/Close

### Beancount
```beancount
2020-01-01 open Assets:Checking USD
2024-12-31 close Assets:OldAccount
```

### Ledger/hledger
```ledger
account Assets:Checking
    ; opened: 2020-01-01
    ; currencies: USD
```

## Cost Basis

### Beancount
```beancount
10 AAPL {185.00 USD}
10 AAPL {185.00 USD, 2024-01-15}
10 AAPL {185.00 USD, 2024-01-15, "lot1"}
```

### Ledger
```ledger
10 AAPL {$185.00}
10 AAPL {$185.00} [2024/01/15]
10 AAPL {$185.00} [2024/01/15] (lot1)
```

### hledger
```hledger
10 AAPL @ $185.00
  ; lot-date: 2024-01-15
```

## Price Annotation

| Beancount | Ledger | hledger |
|-----------|--------|---------|
| `@ 185.00 USD` | `@ $185.00` | `@ $185.00` |
| `@@ 1850.00 USD` | `@@ $1850.00` | `@@ $1850.00` |

## Virtual Postings

### Ledger/hledger (not in Beancount)
```ledger
(Budget:Food)      $50.00    ; Unbalanced
[Budget:Spent]     $50.00    ; Balanced
```

## Automated Transactions

### Ledger/hledger (not in Beancount)
```ledger
= /Expenses:Food/
    (Budget:Food)    (amount)
```

## Periodic Transactions

### Ledger/hledger (not in Beancount)
```ledger
~ Monthly
    Expenses:Rent    $1,500
    Assets:Checking
```

## Quick Conversion Rules

### Beancount → Ledger

1. Change date: `-` → `/`
2. Move payee/narration: `"P" "N"` → `P | N`
3. Change tags: `#tag` → `:tag:`
4. Change currency: `100.00 USD` → `$100.00`
5. Change metadata: `key: "val"` → `; key: val`
6. Balance directive → assertion on previous day

### Beancount → hledger

1. Keep date format (both use `-`)
2. Move payee/narration: `"P" "N"` → `P | N`
3. Change tags: `#tag` → `tag:`
4. Currency can stay or change
5. Change metadata: `key: "val"` → `; key: val`
6. Balance directive → assertion on previous day

### Ledger → hledger

1. Mostly compatible syntax
2. Pre-evaluate value expressions
3. Check function compatibility
4. Adjust alias spacing: `alias x=y` → `alias x = y`

## Feature Availability

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Virtual postings | ❌ | ✅ | ✅ |
| Automated txns | ❌ | ✅ | ✅ |
| Periodic txns | ❌ | ✅ | ✅ |
| Pad directive | ✅ | ❌ | ❌ |
| Documents | ✅ | ❌ | ❌ |
| Events | ✅ | ❌ | ❌ |
| Plugins | ✅ | ❌ | ❌ |
| Expressions | ❌ | ✅ | ⚠️ |
| Timedot | ❌ | ❌ | ✅ |

## See Also

- [Full Conversion Specs](../../conversions/)
- [Feature Matrix](../../conversions/matrix.md)
- [Loss Matrix](../../conversions/loss-matrix.md)
