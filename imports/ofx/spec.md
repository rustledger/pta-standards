# OFX Import Specification

This document specifies how to import OFX (Open Financial Exchange) files into plain text accounting formats.

## Overview

OFX is a standardized format used by financial institutions for downloading account data. It provides structured transaction data that maps cleanly to PTA transactions.

## OFX Structure

### Sample OFX

```xml
<OFX>
  <BANKMSGSRSV1>
    <STMTTRNRS>
      <STMTRS>
        <CURDEF>USD</CURDEF>
        <BANKACCTFROM>
          <BANKID>123456789</BANKID>
          <ACCTID>987654321</ACCTID>
          <ACCTTYPE>CHECKING</ACCTTYPE>
        </BANKACCTFROM>
        <BANKTRANLIST>
          <DTSTART>20240101</DTSTART>
          <DTEND>20240131</DTEND>
          <STMTTRN>
            <TRNTYPE>DEBIT</TRNTYPE>
            <DTPOSTED>20240115</DTPOSTED>
            <TRNAMT>-45.67</TRNAMT>
            <FITID>202401150001</FITID>
            <NAME>GROCERY STORE</NAME>
          </STMTTRN>
        </BANKTRANLIST>
        <LEDGERBAL>
          <BALAMT>1234.56</BALAMT>
          <DTASOF>20240131</DTASOF>
        </LEDGERBAL>
      </STMTRS>
    </STMTTRNRS>
  </BANKMSGSRSV1>
</OFX>
```

## Field Mapping

### Transaction Fields

| OFX Field | PTA Field | Description |
|-----------|-----------|-------------|
| `DTPOSTED` | date | Transaction date |
| `TRNAMT` | amount | Signed amount |
| `NAME` | payee/narration | Description |
| `FITID` | metadata | Unique transaction ID |
| `TRNTYPE` | (derived) | DEBIT, CREDIT, etc. |
| `MEMO` | narration | Additional details |
| `CHECKNUM` | metadata | Check number |

### Account Fields

| OFX Field | Usage |
|-----------|-------|
| `BANKID` | Routing number |
| `ACCTID` | Account number |
| `ACCTTYPE` | CHECKING, SAVINGS, etc. |
| `CURDEF` | Currency code |

## Configuration

### Account Mapping

```yaml
# ofx-accounts.yaml
accounts:
  - bank_id: "123456789"
    account_id: "987654321"
    account: Assets:Bank:Chase:Checking
    currency: USD

  - bank_id: "123456789"
    account_id: "111222333"
    account: Assets:Bank:Chase:Savings
    currency: USD
```

### Transaction Rules

```yaml
rules:
  - match: "GROCERY|SAFEWAY"
    account: Expenses:Food:Groceries

  - match: "DIRECT DEP"
    account: Income:Salary

  - default:
    account: Expenses:Uncategorized
```

## Transaction Types

| TRNTYPE | Meaning | Handling |
|---------|---------|----------|
| DEBIT | Withdrawal | Negative amount |
| CREDIT | Deposit | Positive amount |
| INT | Interest | Income:Interest |
| DIV | Dividend | Income:Dividends |
| FEE | Fee | Expenses:Fees |
| SRVCHG | Service charge | Expenses:Fees:Bank |
| DEP | Deposit | Positive amount |
| ATM | ATM transaction | Use sign |
| POS | Point of sale | Use sign |
| XFER | Transfer | Special handling |
| CHECK | Check | Include check number |
| PAYMENT | Payment | Use sign |
| OTHER | Other | Use sign |

## Date Handling

OFX dates use format: `YYYYMMDDHHMMSS`

```
20240115120000 → 2024-01-15
```

Time portion is typically ignored for PTA.

## Duplicate Detection

Use FITID (Financial Institution Transaction ID):

```yaml
duplicate_detection:
  field: fitid
  store: ~/.pta/imported-fitids.db
```

## Investment Accounts

### Investment Transactions

```xml
<INVSTMTRS>
  <INVTRANLIST>
    <BUYSTOCK>
      <INVBUY>
        <INVTRAN>
          <FITID>BUY20240115</FITID>
          <DTTRADE>20240115</DTTRADE>
        </INVTRAN>
        <SECID>
          <UNIQUEID>037833100</UNIQUEID>
          <UNIQUEIDTYPE>CUSIP</UNIQUEIDTYPE>
        </SECID>
        <UNITS>100</UNITS>
        <UNITPRICE>150.00</UNITPRICE>
        <TOTAL>-15000.00</TOTAL>
      </INVBUY>
      <BUYTYPE>BUY</BUYTYPE>
    </BUYSTOCK>
  </INVTRANLIST>
</INVSTMTRS>
```

### Mapping

```beancount
2024-01-15 * "Buy AAPL"
  fitid: "BUY20240115"
  Assets:Brokerage  100 AAPL {150.00 USD}
  Assets:Brokerage:Cash  -15000.00 USD
```

## Balance Assertions

Generate from LEDGERBAL:

```beancount
2024-01-31 balance Assets:Bank:Chase:Checking 1234.56 USD
```

## Output Example

```beancount
; Imported from OFX: chase-jan-2024.ofx
; Account: Assets:Bank:Chase:Checking

2024-01-15 * "GROCERY STORE"
  fitid: "202401150001"
  Assets:Bank:Chase:Checking  -45.67 USD
  Expenses:Food:Groceries

2024-01-16 * "DIRECT DEPOSIT"
  fitid: "202401160001"
  Assets:Bank:Chase:Checking  2500.00 USD
  Income:Salary

2024-01-31 balance Assets:Bank:Chase:Checking 1234.56 USD
```

## Error Handling

| Error | Action |
|-------|--------|
| Invalid OFX format | Reject with error |
| Unknown account | Prompt or use default |
| Duplicate FITID | Skip transaction |
| Missing required field | Reject transaction |

## See Also

- [CSV Import](../csv/spec.md)
- [QIF Import](../qif/spec.md)
- [OFX Specification](https://www.ofx.net/)
