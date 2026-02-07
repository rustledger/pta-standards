# Note Directive

## Overview

The `note` directive attaches a dated comment to an account. Notes provide a timeline of account-related information that doesn't fit in transaction metadata.

## Syntax

```ebnf
note = date WHITESPACE "note" WHITESPACE account WHITESPACE comment
       (NEWLINE metadata)*

comment = string
```

## Components

### Date

The date the note applies to.

### Account

The account the note is attached to. MUST be a valid, opened account.

### Comment

A string containing the note text.

## Examples

### Basic Note

```beancount
2024-01-01 open Assets:Checking USD

2024-01-15 note Assets:Checking "Called bank about missing deposit"
2024-01-17 note Assets:Checking "Bank confirmed deposit will post tomorrow"
2024-01-18 note Assets:Checking "Deposit received, issue resolved"
```

### Account Changes

```beancount
2024-03-01 note Assets:Checking "Account number changed from ****1234 to ****5678"
2024-06-15 note Assets:Checking "Switched to premium account tier"
2024-09-01 note Assets:Checking "Updated linked phone number"
```

### Investment Notes

```beancount
2024-01-01 open Assets:Brokerage USD,AAPL

2024-02-15 note Assets:Brokerage "Earnings call next week - hold position"
2024-04-01 note Assets:Brokerage "Stock split 4:1 announced"
2024-05-15 note Assets:Brokerage "Dividend reinvestment enabled"
```

### With Metadata

```beancount
2024-01-15 note Assets:Checking "Fraud alert triggered"
  case-number: "FA-2024-1234"
  contacted-by: "phone"
  resolved: FALSE
```

## Use Cases

### Issue Tracking

```beancount
2024-01-10 note Liabilities:CreditCard "Disputed charge: $50 at unknown merchant"
2024-01-15 note Liabilities:CreditCard "Dispute case #12345 opened"
2024-02-01 note Liabilities:CreditCard "Dispute resolved - credit issued"
```

### Account Maintenance

```beancount
2024-01-01 note Assets:Savings "Interest rate changed from 0.5% to 1.2%"
2024-06-01 note Assets:Savings "Interest rate changed from 1.2% to 2.5%"
```

### Communication Log

```beancount
2024-03-15 note Liabilities:Mortgage "Called about refinancing options"
2024-03-20 note Liabilities:Mortgage "Received quote: 5.5% for 30yr fixed"
2024-04-01 note Liabilities:Mortgage "Decided to wait for better rates"
```

### Reminder

```beancount
2024-12-15 note Assets:CD "Matures on 2025-06-15 - review renewal options"
```

## Note vs. Transaction Metadata

Use **notes** for:
- Account-level information not tied to a specific transaction
- Timeline of events related to the account
- Communication logs
- Status changes

Use **transaction metadata** for:
- Information specific to one transaction
- Receipt references
- Categories
- Tags

## Querying Notes

Notes can be queried in BQL:

```sql
-- All notes for an account
SELECT date, comment FROM notes
WHERE account = "Assets:Checking"
ORDER BY date

-- Search notes
SELECT date, account, comment FROM notes
WHERE comment ~ "dispute"
```

## Relationship to Account Lifecycle

Notes require the account to exist:

```beancount
; ERROR: Account not opened
2024-01-15 note Assets:Unknown "This will fail"

; Valid
2024-01-01 open Assets:Checking
2024-01-15 note Assets:Checking "This works"

; Notes can be added after close (for historical reference)
2024-12-31 close Assets:OldAccount
2025-01-15 note Assets:OldAccount "Archived records in folder X"
```

## Validation

The following conditions produce errors:

| Condition | Error Type |
|-----------|------------|
| Account not opened | `ValidationError` |

Note: Unlike postings, notes MAY be added to closed accounts for historical documentation.

## Multiple Notes

Multiple notes on the same date for the same account are allowed:

```beancount
2024-01-15 note Assets:Checking "Called bank at 9am"
2024-01-15 note Assets:Checking "Issue escalated to supervisor"
2024-01-15 note Assets:Checking "Problem resolved at 2pm"
```

## Implementation Notes

1. Store notes indexed by account and date
2. Validate account exists (opened)
3. Allow notes on closed accounts (for historical context)
4. Notes don't affect financial calculations
5. Support full-text search on note content
