# Decimal-Mark Directive

The `decimal-mark` directive specifies the character used as the decimal separator.

## Syntax

```hledger
decimal-mark CHAR
```

Where `CHAR` is `.` (period) or `,` (comma).

## Basic Usage

### Period Decimal (US/UK Style)

```hledger
decimal-mark .

2024-01-15 Transaction
    Expenses:Food    $1,234.56
    Assets:Checking
```

### Comma Decimal (European Style)

```hledger
decimal-mark ,

2024-01-15 Transaction
    Expenses:Food    1.234,56 EUR
    Assets:Checking
```

## Purpose

The directive clarifies ambiguous number formats:

```hledger
; Without directive, "1,234" could mean:
; - 1234 (thousand separator)
; - 1.234 (decimal 1 point 234)

decimal-mark ,
; Now "1,234" means 1.234 (decimal)
```

## Separator Interpretation

### With `decimal-mark .`

| Input | Interpreted As |
|-------|---------------|
| `1.50` | 1.50 |
| `1,000` | 1000 |
| `1,234.56` | 1234.56 |
| `1.234` | 1.234 |

### With `decimal-mark ,`

| Input | Interpreted As |
|-------|---------------|
| `1,50` | 1.50 |
| `1.000` | 1000 |
| `1.234,56` | 1234.56 |
| `1,234` | 1.234 |

## Scope

The directive affects all entries after it:

```hledger
; Default: period is decimal mark

2024-01-01 US format
    Expenses:A    $1,234.56    ; 1234.56 USD
    Assets:Bank

decimal-mark ,

2024-01-02 European format
    Expenses:B    1.234,56 EUR ; 1234.56 EUR
    Assets:Bank
```

## Multiple Directives

Can switch within file (use carefully):

```hledger
; US section
decimal-mark .

2024-01-15 US Transaction
    Assets:USD    $1,234.56
    Equity:Opening

; European section
decimal-mark ,

2024-01-15 EU Transaction
    Assets:EUR    1.234,56 EUR
    Equity:Opening
```

## Interaction with Commodity

Works together with commodity directive:

```hledger
decimal-mark ,

commodity 1.000,00 EUR

2024-01-15 European purchase
    Expenses:Food    50,00 EUR
    Assets:Bank     -50,00 EUR
```

## Regional Examples

### United States

```hledger
decimal-mark .
commodity $1,000.00

2024-01-15 Groceries
    Expenses:Food    $1,234.56
    Assets:Checking
```

### Germany

```hledger
decimal-mark ,
commodity 1.000,00 EUR

2024-01-15 Lebensmittel
    Ausgaben:Essen    1.234,56 EUR
    Vermögen:Girokonto
```

### France

```hledger
decimal-mark ,
commodity 1 000,00 EUR

2024-01-15 Épicerie
    Dépenses:Alimentation    1 234,56 EUR
    Actifs:Compte
```

### Switzerland

```hledger
decimal-mark .
commodity CHF 1'000.00

2024-01-15 Einkauf
    Ausgaben:Essen    CHF 1'234.56
    Vermögen:Konto
```

## Best Practices

1. **Set once at file start** for consistency
2. **Match local conventions** of your region
3. **Be consistent** across all files
4. **Document the choice** for other users

## Common Pitfalls

### Ambiguous Amounts

```hledger
; Without decimal-mark, this is ambiguous:
    Expenses:A    1,234

; Is it 1234 or 1.234?
; Set decimal-mark to clarify
```

### Mixing Conventions

```hledger
; DON'T mix within related files
decimal-mark .
    Expenses:A    1,234.56    ; US style

decimal-mark ,
    Expenses:B    1.234,56    ; European style
```

### Include Files

```hledger
; main.journal
decimal-mark ,
include transactions.journal

; transactions.journal
; Inherits decimal-mark , from including file
2024-01-15 Transaction
    Expenses:A    1.234,56 EUR
    Assets:Bank
```

## Complete Example

```hledger
; ===== European Finance Setup =====

; Set decimal mark first
decimal-mark ,

; Commodity declarations
commodity 1.000,00 EUR
commodity 1.000,00 CHF
commodity $1.000,00

; Account declarations
account Aktiva:Bank:Girokonto
account Aktiva:Bank:Sparkonto
account Ausgaben:Lebensmittel
account Ausgaben:Wohnung
account Einnahmen:Gehalt

; ===== Transactions =====

2024-01-01 Eröffnungsbilanz
    Aktiva:Bank:Girokonto    5.000,00 EUR
    Eigenkapital:Eröffnung

2024-01-15 Gehalt
    Aktiva:Bank:Girokonto    3.500,00 EUR
    Einnahmen:Gehalt

2024-01-16 Supermarkt
    Ausgaben:Lebensmittel    125,50 EUR
    Aktiva:Bank:Girokonto

2024-01-20 Miete
    Ausgaben:Wohnung    850,00 EUR
    Aktiva:Bank:Girokonto
```

## Command Line

The decimal mark can also be set via command line:

```bash
hledger -f journal.hledger --decimal-mark=, bal
```

## See Also

- [Commodity Directive](commodity.md)
- [Amounts Specification](../amounts.md)
- [Syntax Specification](../syntax.md)
