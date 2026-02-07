# Frequently Asked Questions

Common questions about plain text accounting and this specification.

## General

### What is plain text accounting?

Plain text accounting (PTA) is a method of managing finances using human-readable text files instead of proprietary software. Transactions are recorded in a simple text format that can be version-controlled, edited with any text editor, and processed by command-line tools.

### Why use plain text accounting?

- **Longevity** - Text files never become obsolete
- **Control** - Your data is yours, no vendor lock-in
- **Transparency** - Human-readable format
- **Version control** - Track changes with git
- **Automation** - Script imports and reports
- **Privacy** - Data stays on your computer

### Which tool should I use?

| Choose | If you need |
|--------|-------------|
| Beancount | Strict validation, Python plugins, Fava web UI |
| Ledger | Maximum flexibility, value expressions, speed |
| hledger | Gentle learning curve, JSON output, web UI |

All three are excellent choices. Try each and see which fits your workflow.

### Can I switch between tools?

Yes, with some effort. See the [conversion specifications](../conversions/) for details. Common features convert well; format-specific features may be lost.

## This Specification

### What is the PTA Specification?

This project provides formal specifications for PTA formats, enabling:
- Consistent implementations
- Interoperability between tools
- Conformance testing
- Documentation of format details

### Is this an official specification?

This is a community effort to document existing formats. It's not affiliated with the original tool authors but aims to accurately describe their formats.

### How do I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines. We welcome:
- Corrections and clarifications
- Additional test cases
- Edge case documentation
- Tool implementation reports

## Format Questions

### Why are there three different formats?

Each tool evolved independently to serve different needs:
- **Ledger** (2003) - The original, prioritizing power
- **hledger** (2007) - Focused on reliability and usability
- **Beancount** (2008) - Emphasized correctness and simplicity

### Are the formats compatible?

Partially. Basic transactions work across all three. Advanced features differ:

| Feature | Compatibility |
|---------|---------------|
| Basic transactions | ✅ High |
| Metadata | 🔄 Syntax differs |
| Balance assertions | 🔄 Timing differs |
| Virtual postings | ❌ Beancount lacks |
| Plugins | ❌ Beancount only |

### Why doesn't X format have Y feature?

Each tool makes design choices based on its philosophy:
- Beancount omits virtual postings for simplicity
- Ledger omits strict validation for flexibility
- hledger balances between strictness and ease

## Technical Questions

### How precise are amounts?

All three tools use arbitrary precision decimal arithmetic. Amounts like `100.123456789` are stored exactly. Display may be rounded.

### How are currencies handled?

- **Beancount**: Must declare commodities; suffix position only
- **Ledger/hledger**: Auto-detect commodities; prefix or suffix

### What character encoding should I use?

UTF-8 is recommended and widely supported. Avoid BOM (Byte Order Mark).

### Can I use non-ASCII characters?

Yes, in account names, payees, and metadata:
```
2024-01-15 * "Café Müller" "Kaffee und Kuchen"
  Expenses:Essen:Café    5.50 EUR
```

## Workflow Questions

### How do I import bank data?

1. Export from bank (CSV, OFX, QIF)
2. Use import tool:
   - Beancount: `bean-import` with importers
   - hledger: `hledger import` with CSV rules
   - Ledger: `ledger convert` or external tools
3. Review and categorize

### How do I handle multiple currencies?

Record transactions in their native currency:
```beancount
2024-01-15 * "Hotel" "Paris trip"
  Expenses:Travel:Lodging  150.00 EUR
  Liabilities:CreditCard  -165.00 USD @@ 150.00 EUR
```

Use price directives for market rates:
```
P 2024-01-15 EUR 1.10 USD
```

### How do I track investments?

Use cost basis tracking:
```beancount
; Buy
2024-01-15 * "Buy AAPL"
  Assets:Brokerage  10 AAPL {185.00 USD}
  Assets:Cash  -1850.00 USD

; Sell
2024-03-15 * "Sell AAPL"
  Assets:Brokerage  -10 AAPL {185.00 USD} @ 200.00 USD
  Assets:Cash  2000.00 USD
  Income:Capital-Gains  -150.00 USD
```

### How do I reconcile with bank statements?

1. Get statement ending balance
2. Mark cleared transactions as `*`
3. Add balance assertion:
   ```
   2024-01-31 balance Assets:Checking 1234.56 USD
   ```
4. Run validation
5. Investigate any discrepancies

## Troubleshooting

### "Transaction does not balance"

Check:
1. All amounts have correct signs
2. Currencies match
3. Auto-balance posting exists
4. Decimal precision is correct

### "Unknown account"

In Beancount, declare accounts first:
```beancount
2020-01-01 open Expenses:Food USD
```

### "Balance assertion failed"

Check:
- Correct date (Beancount: start of day)
- Correct currency
- No missing transactions
- Correct account name

### Import duplicates transactions

Use duplicate detection:
- Track imported transaction IDs
- Use `bean-import` deduplication
- Check date ranges

## Resources

### Where can I learn more?

- [Beancount Documentation](https://beancount.github.io/docs/)
- [Ledger Manual](https://ledger-cli.org/doc/ledger3.html)
- [hledger Manual](https://hledger.org/hledger.html)
- [Plain Text Accounting](https://plaintextaccounting.org/)

### Community

- [r/plaintextaccounting](https://reddit.com/r/plaintextaccounting)
- [Beancount Mailing List](https://groups.google.com/g/beancount)
- [hledger Chat](https://matrix.hledger.org/)
- [Ledger Mailing List](https://groups.google.com/g/ledger-cli)

## See Also

- [Cheatsheets](cheatsheets/)
- [Comparisons](comparison/)
- [Examples](../examples/)
