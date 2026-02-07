# Level 4: Full Conformance

Level 4 conformance requires complete Beancount feature support, including all booking methods, plugins, and advanced features.

## Requirements

### Level 3 Prerequisites

All Level 1, Level 2, and Level 3 requirements MUST be met.

### Booking Methods

The implementation MUST support all booking methods:

| Method | Description |
|--------|-------------|
| `STRICT` | Exact lot match required (default) |
| `FIFO` | First in, first out |
| `LIFO` | Last in, first out |
| `HIFO` | Highest cost first |
| `NONE` | No automatic booking |
| `AVERAGE` | Average cost basis |

### Lot Matching

The implementation MUST support:

| Feature | Description |
|---------|-------------|
| Cost matching | Match by cost basis |
| Date matching | Match by acquisition date |
| Label matching | Match by lot label |
| Wildcard matching | `{*}` matches any lot |
| Automatic booking | Apply booking method |

### Pad Directive

The implementation MUST support pad expansion:

```beancount
2024-01-01 open Assets:Checking USD
2024-01-01 open Equity:Opening USD

2024-01-01 pad Assets:Checking Equity:Opening
2024-01-02 balance Assets:Checking 1000 USD
```

Pad MUST:
- Generate synthetic transaction
- Balance to assertion amount
- Use correct date

### Plugin Support

The implementation SHOULD support:

| Feature | Description |
|---------|-------------|
| Plugin loading | Load Python plugins |
| Plugin ordering | Process in declaration order |
| Plugin configuration | Pass config string |
| Error propagation | Collect plugin errors |

### Price Database

The implementation MUST support:

| Feature | Description |
|---------|-------------|
| Explicit prices | `price` directive |
| Implicit prices | From `@` annotations |
| Price lookup | Get price at date |
| Interpolation | Nearest price when exact missing |

### Document Directive

The implementation MUST support:

| Feature | Description |
|---------|-------------|
| Path resolution | Relative to journal |
| File existence | Optional validation |
| Document discovery | Optional auto-discovery |

### Include Directive

The implementation MUST support:

| Feature | Description |
|---------|-------------|
| Relative paths | Resolve from parent file |
| Glob patterns | `*.beancount` matching |
| Cycle detection | Prevent infinite loops |
| Error propagation | Errors from included files |

### Query Directive

The implementation MUST support:

| Feature | Description |
|---------|-------------|
| Named queries | Store query for later |
| Query execution | Run stored queries |

### Custom Directive

The implementation MUST support:

| Feature | Description |
|---------|-------------|
| Custom types | Any string type |
| Custom values | String, account, amount, date, bool, number |

### Options

The implementation MUST support core options:

| Option | Description |
|--------|-------------|
| `title` | Journal title |
| `operating_currency` | Primary currencies |
| `name_assets` | Assets root name |
| `name_liabilities` | Liabilities root |
| `name_equity` | Equity root |
| `name_income` | Income root |
| `name_expenses` | Expenses root |
| `account_previous_*` | Period close accounts |
| `inferred_tolerance_default` | Default tolerance |
| `booking_method` | Default booking |

## Test Suite

### Required Tests

| Suite | Purpose | Minimum Pass Rate |
|-------|---------|-------------------|
| All Level 3 tests | Prerequisites | 100% of L3 |
| `booking` | All booking methods | 95% |
| All remaining | Complete coverage | 95% |

### Full Test Categories

- FIFO booking
- LIFO booking
- AVERAGE booking
- Pad expansion
- Include processing
- Plugin execution
- Price database
- All options

## Example: FIFO Booking

```beancount
2024-01-01 open Assets:Stock AAPL "FIFO"
2024-01-01 open Assets:Cash USD

2024-01-15 * "Buy lot 1"
  Assets:Stock  10 AAPL {100 USD}
  Assets:Cash  -1000 USD

2024-02-15 * "Buy lot 2"
  Assets:Stock  10 AAPL {120 USD}
  Assets:Cash  -1200 USD

2024-03-15 * "Sell (FIFO: sells lot 1 first)"
  Assets:Stock  -5 AAPL {100 USD}  ; Auto-selected
  Assets:Cash   600 USD
  Income:Gains -100 USD
```

## Example: Average Booking

```beancount
2024-01-01 open Assets:Stock AAPL "AVERAGE"
2024-01-01 open Assets:Cash USD

2024-01-15 * "Buy lot 1"
  Assets:Stock  10 AAPL {100 USD}
  Assets:Cash  -1000 USD

2024-02-15 * "Buy lot 2"
  Assets:Stock  10 AAPL {120 USD}
  Assets:Cash  -1200 USD

; Average cost = (1000 + 1200) / 20 = 110 USD

2024-03-15 * "Sell at average"
  Assets:Stock  -5 AAPL {110 USD}  ; Average cost
  Assets:Cash   600 USD
  Income:Gains  -50 USD
```

## Inventory Model

Full implementations MUST track:

```python
@dataclass
class Lot:
    units: Decimal
    currency: str
    cost: Amount
    date: date
    label: Optional[str]

@dataclass
class Inventory:
    lots: List[Lot]

    def add(self, units: Amount, cost: CostSpec) -> None:
        """Add units to inventory."""

    def reduce(self, units: Amount, cost_spec: CostSpec,
               booking: BookingMethod) -> Tuple[List[Lot], Amount]:
        """Remove units using booking method, return gains/losses."""
```

## Plugin Interface

```python
def plugin(entries: List[Directive],
           options: Dict[str, Any]) -> Tuple[List[Directive], List[Error]]:
    """
    Plugin entry point.

    Args:
        entries: All directives in date order
        options: Journal options

    Returns:
        Modified entries and any new errors
    """
```

## Certification

To achieve Level 4:

1. Achieve Level 3 certification
2. Run all remaining test suites
3. Achieve 95% pass rate overall
4. Document any limitations
5. Document extensions (if any)
6. Submit certification

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Wrong FIFO order | Sort by date, not insertion |
| Average precision | Use sufficient decimal places |
| Pad timing | Generate before balance assertion |
| Plugin ordering | Process in file order |

## Extensions

Level 4 implementations MAY provide extensions:

| Extension | Description |
|-----------|-------------|
| Additional booking | Custom booking methods |
| Custom plugins | Native plugin support |
| Performance | Parallel processing |
| Caching | Incremental updates |

Extensions MUST be documented and not break conformance.

## Reference Implementations

| Implementation | Language | Notes |
|----------------|----------|-------|
| beancount | Python | Reference implementation |
| rustledger | Rust | High-performance alternative |

## See Also

- [Test Suite](/tests/beancount/v3/booking/)
- [Booking Specification](/formats/beancount/v3/spec/booking.md)
- [Plugin Specification](/formats/beancount/plugins/spec.md)
