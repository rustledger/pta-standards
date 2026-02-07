# OFX to PTA Mapping

This document specifies mapping from OFX (Open Financial Exchange) to PTA formats.

## Overview

OFX is an XML/SGML format used by banks for transaction downloads. This document specifies how to convert OFX data to PTA transactions.

## OFX Structure

### Key Elements

```xml
<OFX>
  <BANKMSGSRSV1>
    <STMTTRNRS>
      <STMTRS>
        <BANKACCTFROM>
          <BANKID>123456789</BANKID>
          <ACCTID>987654321</ACCTID>
          <ACCTTYPE>CHECKING</ACCTTYPE>
        </BANKACCTFROM>
        <BANKTRANLIST>
          <STMTTRN>
            <TRNTYPE>DEBIT</TRNTYPE>
            <DTPOSTED>20240115120000</DTPOSTED>
            <TRNAMT>-50.00</TRNAMT>
            <FITID>20240115001</FITID>
            <NAME>GROCERY STORE</NAME>
            <MEMO>Purchase</MEMO>
          </STMTTRN>
        </BANKTRANLIST>
      </STMTRS>
    </STMTTRNRS>
  </BANKMSGSRSV1>
</OFX>
```

## Basic Mapping

### OFX Transaction

```xml
<STMTTRN>
  <TRNTYPE>DEBIT</TRNTYPE>
  <DTPOSTED>20240115120000</DTPOSTED>
  <TRNAMT>-50.00</TRNAMT>
  <FITID>20240115001</FITID>
  <NAME>GROCERY STORE</NAME>
  <MEMO>Weekly groceries</MEMO>
</STMTTRN>
```

### Beancount Output

```beancount
2024-01-15 * "GROCERY STORE" "Weekly groceries"
  ofx-fitid: "20240115001"
  Expenses:Unknown           50.00 USD
  Assets:Bank:Checking      -50.00 USD
```

### Ledger Output

```ledger
2024/01/15 * GROCERY STORE
    ; Weekly groceries
    ; FITID: 20240115001
    Expenses:Unknown    $50.00
    Assets:Bank:Checking
```

## Field Mapping

### Date (DTPOSTED)

```
20240115120000 → 2024-01-15
```

Format: `YYYYMMDDHHMMSS[.XXX][:TZ]`

### Amount (TRNAMT)

- Negative: Outflow (expense/transfer out)
- Positive: Inflow (income/transfer in)

### Transaction Type (TRNTYPE)

| OFX Type | Meaning |
|----------|---------|
| `CREDIT` | Deposit |
| `DEBIT` | Withdrawal |
| `INT` | Interest |
| `DIV` | Dividend |
| `FEE` | Fee |
| `SRVCHG` | Service charge |
| `DEP` | Deposit |
| `ATM` | ATM transaction |
| `POS` | Point of sale |
| `XFER` | Transfer |
| `CHECK` | Check |
| `PAYMENT` | Payment |
| `CASH` | Cash |
| `DIRECTDEP` | Direct deposit |
| `DIRECTDEBIT` | Direct debit |
| `REPEATPMT` | Recurring payment |
| `OTHER` | Other |

### Unique ID (FITID)

Store as metadata to prevent duplicate imports:

```beancount
  ofx-fitid: "20240115001"
```

## Account Mapping

### Account Identification

```xml
<BANKACCTFROM>
  <BANKID>123456789</BANKID>
  <ACCTID>987654321</ACCTID>
  <ACCTTYPE>CHECKING</ACCTTYPE>
</BANKACCTFROM>
```

### Mapping Configuration

```yaml
account_mapping:
  "123456789:987654321":
    account: "Assets:Bank:Checking"
    currency: "USD"
```

## Investment Transactions

### OFX Investment

```xml
<INVSTMTRS>
  <INVTRANLIST>
    <BUYSTOCK>
      <INVBUY>
        <INVTRAN>
          <FITID>20240115002</FITID>
          <DTTRADE>20240115120000</DTTRADE>
        </INVTRAN>
        <SECID>
          <UNIQUEID>037833100</UNIQUEID>
          <UNIQUEIDTYPE>CUSIP</UNIQUEIDTYPE>
        </SECID>
        <UNITS>10</UNITS>
        <UNITPRICE>150.00</UNITPRICE>
        <TOTAL>-1500.00</TOTAL>
      </INVBUY>
      <BUYTYPE>BUY</BUYTYPE>
    </BUYSTOCK>
  </INVTRANLIST>
</INVSTMTRS>
```

### PTA Output

```beancount
2024-01-15 * "Buy AAPL"
  ofx-fitid: "20240115002"
  Assets:Brokerage    10 AAPL {150.00 USD}
  Assets:Brokerage:Cash  -1500.00 USD
```

## Security Mapping

### CUSIP to Symbol

```yaml
security_mapping:
  "037833100": "AAPL"
  "594918104": "MSFT"
```

### Symbol Lookup

```python
def cusip_to_symbol(cusip):
    # Use external API or local mapping
    return security_mapping.get(cusip, cusip)
```

## Duplicate Detection

### By FITID

```python
def is_duplicate(fitid, existing_transactions):
    for txn in existing_transactions:
        if txn.meta.get('ofx-fitid') == fitid:
            return True
    return False
```

### By Content

Match on date + amount + payee if FITID unavailable.

## Categorization

### Rule-Based

```yaml
categorization_rules:
  - match: "GROCERY|WHOLEFDS"
    account: "Expenses:Food:Groceries"

  - match: "AMAZON"
    account: "Expenses:Shopping"

  - type: "INT"
    account: "Income:Interest"

  - type: "FEE|SRVCHG"
    account: "Expenses:Bank:Fees"
```

### Default Categories

```yaml
defaults:
  credit: "Income:Unknown"
  debit: "Expenses:Unknown"
```

## Multi-Currency

### Currency in OFX

```xml
<STMTRS>
  <CURDEF>USD</CURDEF>
  ...
</STMTRS>
```

### Foreign Transactions

```xml
<STMTTRN>
  <TRNAMT>-50.00</TRNAMT>
  <ORIGCURRENCY>
    <CURRATE>1.10</CURRATE>
    <CURSYM>EUR</CURSYM>
  </ORIGCURRENCY>
</STMTTRN>
```

### PTA Output

```beancount
2024-01-15 * "Foreign Purchase"
  Expenses:Unknown    45.45 EUR @ 1.10 USD
  Assets:Bank:Checking  -50.00 USD
```

## Example Conversion

### Complete OFX

```xml
<?xml version="1.0"?>
<OFX>
  <BANKMSGSRSV1>
    <STMTTRNRS>
      <STMTRS>
        <CURDEF>USD</CURDEF>
        <BANKACCTFROM>
          <BANKID>123456</BANKID>
          <ACCTID>98765</ACCTID>
          <ACCTTYPE>CHECKING</ACCTTYPE>
        </BANKACCTFROM>
        <BANKTRANLIST>
          <DTSTART>20240101</DTSTART>
          <DTEND>20240131</DTEND>
          <STMTTRN>
            <TRNTYPE>DEBIT</TRNTYPE>
            <DTPOSTED>20240115</DTPOSTED>
            <TRNAMT>-50.00</TRNAMT>
            <FITID>2024011501</FITID>
            <NAME>GROCERY STORE</NAME>
          </STMTTRN>
          <STMTTRN>
            <TRNTYPE>CREDIT</TRNTYPE>
            <DTPOSTED>20240120</DTPOSTED>
            <TRNAMT>1000.00</TRNAMT>
            <FITID>2024012001</FITID>
            <NAME>DIRECT DEPOSIT PAYROLL</NAME>
          </STMTTRN>
        </BANKTRANLIST>
        <LEDGERBAL>
          <BALAMT>5000.00</BALAMT>
          <DTASOF>20240131</DTASOF>
        </LEDGERBAL>
      </STMTRS>
    </STMTTRNRS>
  </BANKMSGSRSV1>
</OFX>
```

### Converted Output

```beancount
2024-01-15 * "GROCERY STORE"
  ofx-fitid: "2024011501"
  Expenses:Food:Groceries    50.00 USD
  Assets:Bank:Checking      -50.00 USD

2024-01-20 * "DIRECT DEPOSIT PAYROLL"
  ofx-fitid: "2024012001"
  Assets:Bank:Checking     1000.00 USD
  Income:Salary           -1000.00 USD

2024-01-31 balance Assets:Bank:Checking  5000.00 USD
```

## See Also

- [QIF Mapping](../qif/mapping.md)
- [CSV Rules](../csv/rules.md)
- [Import Specification](../README.md)
