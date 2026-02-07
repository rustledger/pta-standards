# Value Expression Functions

This document lists the built-in functions available in Ledger's value expression language.

## Amount Functions

### abs(x)

Returns absolute value:

```ledger
assert abs($-100) == $100
assert abs(amount) < $1000
```

### round(x)

Rounds to commodity precision:

```ledger
2024/01/15 Rounded
    Expenses:A    (round($33.333))  ; $33.33
    Assets:Checking
```

### floor(x)

Rounds down:

```ledger
(floor($33.9))  ; $33.00
```

### ceiling(x)

Rounds up:

```ledger
(ceiling($33.1))  ; $34.00
```

### truncate(x)

Truncates toward zero:

```ledger
(truncate($33.9))   ; $33.00
(truncate($-33.9))  ; $-33.00
```

### commodity(x)

Returns the commodity symbol:

```ledger
= expr commodity(amount) == "$"
    ; :usd:
```

### quantity(x)

Returns numeric quantity without commodity:

```ledger
assert quantity($100.50) == 100.50
```

## Account Functions

### total(account)

Sum of account balances:

```ledger
assert total(Assets) > 0
assert total(Expenses:Food) < $1000
```

### display_total(account)

Formatted total for display:

```ledger
--format "%(account): %(display_total)\n"
```

### has_tag(name)

Check if posting has tag:

```ledger
= expr has_tag("reimbursable")
    Receivables:Reimbursement    (amount)
```

### tag(name)

Get tag value:

```ledger
= expr tag("project") == "alpha"
    ; Additional processing
```

### account

Current account (variable, not function):

```ledger
= expr account =~ /Expenses:Food/
    (Budget:Food)  (amount * -1)
```

## Date Functions

### date

Current transaction date:

```ledger
= expr date >= [2024/01/01]
    ; :this-year:
```

### today

Current calendar date:

```ledger
= expr date < today
    ; :past:
```

### year(d)

Extract year:

```ledger
= expr year(date) == 2024
    ; :2024:
```

### month(d)

Extract month (1-12):

```ledger
= expr month(date) == 12
    ; :december:
```

### day(d)

Extract day (1-31):

```ledger
= expr day(date) == 1
    ; :month-start:
```

## String Functions

### payee

Transaction payee:

```ledger
= expr payee =~ /Whole Foods/
    ; :groceries:
```

### note

Transaction note/narration:

```ledger
= expr note =~ /reimbursable/i
    ; :reimbursable:
```

### format(fmt, ...)

Format string:

```ledger
= format("%s-%04d", commodity, quantity)
```

### join(sep, ...)

Join strings:

```ledger
= join(", ", account, payee)
```

### substr(s, start, len)

Substring:

```ledger
= substr(payee, 0, 10)
```

## Logical Functions

### any(account, expr)

True if any posting matches:

```ledger
assert any(Expenses, amount > $100)
```

### all(account, expr)

True if all postings match:

```ledger
assert all(Expenses, amount >= 0)
```

### count(account)

Number of postings:

```ledger
assert count(Expenses:Food) < 100
```

## Collection Functions

### sum(expr)

Sum over collection:

```ledger
= sum(amount)
```

### min(...)

Minimum value:

```ledger
(min($100, $50, $75))  ; $50
```

### max(...)

Maximum value:

```ledger
(max($100, $50, $75))  ; $100
```

### average(expr)

Average value:

```ledger
= average(amount)
```

## Market Value Functions

### market(amount)

Current market value:

```ledger
--format "%(account): %(market(display_total))\n"
```

### price(commodity)

Current price of commodity:

```ledger
= price(AAPL)  ; Returns price in default commodity
```

### exchange(amount, commodity)

Convert to different commodity:

```ledger
(exchange($100, "EUR"))
```

## Utility Functions

### print(...)

Debug output:

```ledger
= expr print("Processing: ", account)
```

### now

Current datetime:

```ledger
= expr now
```

### default

Check if value is default/empty:

```ledger
= expr default(amount)
    ; Handle empty amount
```

## Report-Specific Functions

These functions are primarily used in `--format` expressions:

### quoted(x)

Quote for output:

```ledger
--format "%(quoted(payee))\n"
```

### justify(x, width)

Right-justify:

```ledger
--format "%(justify(total, 12))\n"
```

### strip(x)

Remove surrounding whitespace:

```ledger
--format "%(strip(payee))\n"
```

### scrub(x)

Clean for display:

```ledger
--format "%(scrub(total))\n"
```

## Function Categories

### Pure Functions

No side effects:
- `abs`, `round`, `floor`, `ceiling`
- `min`, `max`, `sum`, `average`
- `quantity`, `commodity`

### Query Functions

Read state:
- `total`, `has_tag`, `tag`
- `price`, `market`
- `date`, `today`, `now`

### Format Functions

For output:
- `format`, `justify`, `quoted`
- `strip`, `scrub`

## Examples

### Complex Validation

```ledger
assert total(Assets) - total(Liabilities) > $0
  and all(Assets:Cash, amount >= $0)
  and count(Expenses) > 0
```

### Automated Categorization

```ledger
= expr payee =~ /^Amazon/ and amount > $100
    ; :large-amazon-purchase:
    ; review: true

= expr account =~ /Expenses:Food/ and month(date) == 12
    ; :holiday-food:
```

### Report Formatting

```bash
ledger bal --format "%(account)-40s %(justify(market(display_total), 15))\n"
```

### Calculations

```ledger
2024/01/15 Tax Withholding
    Assets:Checking    (income - (income * tax_rate))
    Expenses:Tax       (income * tax_rate)
    Income:Salary      (-income)
```

## See Also

- [Expression Specification](spec.md)
- [Automated Transactions](../spec/advanced/automated.md)
