# Postings

This document specifies the posting model for plain text accounting systems.

## Definition

A **Posting** is a single line within a transaction that records a change to an account's balance. Each posting specifies an account and optionally an amount, cost, and price.

## Posting Structure

```
Posting = {
  account: Account,
  amount: Amount?,
  cost: CostSpec?,
  price: PriceSpec?,
  metadata: Metadata
}
```

## Components

### Account

The account affected by this posting:

```
Assets:Checking
Expenses:Food:Groceries
Income:Salary
```

### Amount

The quantity and commodity added or removed:

```
100.00 USD
-50 EUR
10 AAPL
```

### Cost (Optional)

Acquisition cost for lot tracking:

```
{150.00 USD}
{150.00 USD, 2024-01-15}
{150.00 USD, 2024-01-15, "lot-1"}
```

### Price (Optional)

Conversion price for this posting:

```
@ 1.08 USD
@@ 108 USD
```

### Metadata

Key-value annotations:

```
2024-01-15 * "Purchase"
  Assets:Stock  10 AAPL {150 USD}
    broker: "Fidelity"
    order-id: "12345"
  Assets:Checking
```

## Basic Syntax

### Simple Posting

```
Assets:Checking  100.00 USD
```

### With Cost

```
Assets:Stock  10 AAPL {150.00 USD}
```

### With Price

```
Assets:Euro  100 EUR @ 1.08 USD
```

### With Cost and Price

```
Assets:Stock  -10 AAPL {150.00 USD} @ 160.00 USD
```

## Amount Inference

### Single Elision

One posting per transaction may omit its amount:

```
2024-01-15 * "Salary"
  Assets:Checking   5000.00 USD
  Income:Salary                    ; Inferred: -5000.00 USD
```

### Inference Rules

The inferred amount is calculated to balance the transaction:

```
inferred_amount = -sum(other_posting_weights)
```

### Multiple Elisions

At most one posting may omit its amount:

```
2024-01-15 * "Invalid"
  Assets:Checking                  ; Error: multiple elisions
  Income:Salary
```

## Weight Calculation

### Purpose

The "weight" of a posting determines its contribution to transaction balance.

### Weight Rules

| Posting Type | Weight Calculation |
|--------------|-------------------|
| Amount only | `units` |
| With price `@` | `units × price` |
| With total price `@@` | `total_price` |
| With cost `{}` | `units × cost` |
| Cost + price | `units × cost` |

### Examples

```
100 USD                    ; Weight: 100 USD
100 EUR @ 1.08 USD         ; Weight: 108 USD
100 EUR @@ 108 USD         ; Weight: 108 USD
10 AAPL {150 USD}          ; Weight: 1500 USD
10 AAPL {150 USD} @ 160    ; Weight: 1500 USD (cost used)
```

## Cost Specifications

### Augmentation (Buying)

When adding to inventory, cost defines the lot:

```
2024-01-15 * "Buy stock"
  Assets:Stock    10 AAPL {150.00 USD}
  Assets:Cash    -1500.00 USD
```

Creates lot: 10 AAPL at 150 USD each, dated 2024-01-15

### Reduction (Selling)

When removing from inventory, cost filters matching lots:

```
2024-03-15 * "Sell stock"
  Assets:Stock   -10 AAPL {150.00 USD}
  Assets:Cash    1600.00 USD
```

Reduces the lot matching 150 USD cost.

### Cost Spec Components

| Component | Syntax | Purpose |
|-----------|--------|---------|
| Amount | `150.00 USD` | Per-unit cost |
| Date | `2024-01-15` | Acquisition date |
| Label | `"lot-1"` | User identifier |
| Merge | `*` | Average cost |

### Cost Spec Examples

```
{150 USD}                           ; Cost only
{2024-01-15}                        ; Date only
{"lot-1"}                           ; Label only
{150 USD, 2024-01-15}               ; Cost and date
{150 USD, 2024-01-15, "lot-1"}      ; All components
{*}                                 ; Merge at average
{}                                  ; Match any lot
```

## Price Specifications

### Per-Unit Price

```
100 EUR @ 1.08 USD
```

Meaning: Each EUR is worth 1.08 USD

### Total Price

```
100 EUR @@ 108 USD
```

Meaning: All 100 EUR together are worth 108 USD

### Price Recording

Prices create implicit price database entries:

```
2024-01-15 * "Exchange"
  Assets:USD   108 USD
  Assets:EUR  -100 EUR @ 1.08 USD
```

Records: 2024-01-15: EUR = 1.08 USD

## Posting Flags

### Transaction Flag Inheritance

Postings inherit the transaction's flag by default:

```
2024-01-15 * "Cleared transaction"
  Assets:Checking  100 USD     ; Inherits *
  Income:Salary                ; Inherits *
```

### Per-Posting Flags

Some formats allow per-posting flags:

```
2024-01-15 * "Mixed"
  * Assets:Checking  100 USD   ; Cleared
  ! Income:Salary              ; Pending
```

## Posting Order

### Within Transaction

Postings are typically ordered:
1. Asset accounts first
2. Then liability accounts
3. Then equity accounts
4. Then income accounts
5. Then expense accounts last

### Formatting Convention

```
2024-01-15 * "Paycheck"
  Assets:Checking     5000.00 USD    ; Asset first
  Expenses:Tax:Federal  500.00 USD   ; Expense
  Income:Salary                       ; Income last
```

## Balance Checking

### Transaction Balance

All postings MUST sum to zero:

```
sum(posting.weight for posting in transaction.postings) == 0
```

### Tolerance

Small rounding differences may be tolerated:

```
2024-01-15 * "Currency exchange"
  Assets:USD    108.00 USD
  Assets:EUR   -100.00 EUR @ 1.0799 USD    ; Weight: 107.99
  ; Residual: 0.01 USD (within tolerance)
```

### Balance Error

```
ERROR: Transaction does not balance
  --> ledger.beancount:42:1
   |
42 | 2024-01-15 * "Unbalanced"
   | ^^^^^^^^^^^^^^^^^^^^^^^^^
   |
   = residual: 0.50 USD
   = hint: add posting to balance transaction
```

## Special Postings

### Padding Posting

Generated by `pad` directive:

```
2024-01-01 pad Assets:Checking Equity:Opening-Balances

; Generates:
;   2024-01-01 * "Padding"
;     Assets:Checking         XXXX USD
;     Equity:Opening-Balances
```

### Auto-Posting

Some plugins generate automatic postings:

```
; With auto-accounts plugin:
2024-01-15 * "Unknown payee"
  Expenses:Misc  100 USD         ; Auto-opened account
  Assets:Cash
```

## Metadata on Postings

### Syntax

```
2024-01-15 * "Purchase"
  Assets:Stock  10 AAPL {150 USD}
    settlement-date: 2024-01-17
    broker: "Fidelity"
  Assets:Cash  -1500 USD
```

### Indentation

Posting metadata is indented further than the posting:

```
  Account  Amount
    key: value
```

## Implementation Model

```python
@dataclass
class Posting:
    account: str
    units: Optional[Amount] = None
    cost: Optional[CostSpec] = None
    price: Optional[Amount] = None
    flag: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def weight(self) -> Amount:
        """Calculate the weight for balance checking."""
        if self.units is None:
            raise ValueError("Cannot compute weight of elided posting")

        if self.cost is not None:
            return Amount(
                self.units.number * self.cost.number_per,
                self.cost.currency
            )
        elif self.price is not None:
            return Amount(
                self.units.number * self.price.number,
                self.price.commodity
            )
        else:
            return self.units
```

## Validation

### Account Not Opened

```
ERROR: Account not opened
  --> ledger.beancount:42:3
   |
42 |   Assets:Unknown  100 USD
   |   ^^^^^^^^^^^^^^
```

### Currency Not Allowed

```
ERROR: Currency not allowed for account
  --> ledger.beancount:42:20
   |
42 |   Assets:Checking  100 EUR
   |                        ^^^
   |
   = allowed: USD
```

### Invalid Cost

```
ERROR: Cannot specify cost for currency
  --> ledger.beancount:42:20
   |
42 |   Assets:Cash  100 USD {1 EUR}
   |                        ^^^^^^^
   |
   = hint: costs are for commodities held at cost basis
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Cost syntax | `{100 USD}` | `{=$100}` | `{100 USD}` |
| Price syntax | `@ 1.08 USD` | `@ $1.08` | `@ 1.08 USD` |
| Total price | `@@ 108 USD` | `@@ $108` | `@@ 108 USD` |
| Posting flags | No | Yes | Yes |
| Metadata | `key: value` | `; key: value` | `; key: value` |
| Multiple elisions | No | Yes | Yes |
