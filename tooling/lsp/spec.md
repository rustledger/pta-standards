# Beancount Language Server Protocol Specification

This document specifies the Language Server Protocol (LSP) capabilities for Beancount language servers.

## Overview

A Beancount LSP server provides IDE features for Beancount files including:
- Syntax highlighting (via semantic tokens)
- Diagnostics (errors and warnings)
- Completions (accounts, commodities, payees, etc.)
- Hover information
- Go to definition
- Find references
- Document symbols
- Code actions
- Formatting

## Server Capabilities

### Required Capabilities

All conformant Beancount LSP servers MUST implement:

| Capability | LSP Method | Description |
|------------|------------|-------------|
| Text Document Sync | `textDocument/didOpen`, `didChange`, `didClose` | Full or incremental sync |
| Diagnostics | `textDocument/publishDiagnostics` | Syntax and validation errors |
| Completion | `textDocument/completion` | Account, commodity, payee completion |

### Recommended Capabilities

Conformant servers SHOULD implement:

| Capability | LSP Method | Description |
|------------|------------|-------------|
| Hover | `textDocument/hover` | Account balances, commodity prices |
| Go to Definition | `textDocument/definition` | Jump to account open directive |
| Find References | `textDocument/references` | Find all uses of account/commodity |
| Document Symbols | `textDocument/documentSymbol` | List accounts, transactions |
| Formatting | `textDocument/formatting` | Format document |
| Semantic Tokens | `textDocument/semanticTokens` | Rich syntax highlighting |

### Optional Capabilities

| Capability | LSP Method | Description |
|------------|------------|-------------|
| Code Actions | `textDocument/codeAction` | Quick fixes, refactoring |
| Code Lens | `textDocument/codeLens` | Inline balance display |
| Folding | `textDocument/foldingRange` | Fold transactions, sections |
| Selection Range | `textDocument/selectionRange` | Smart selection expansion |
| Rename | `textDocument/rename` | Rename accounts |
| Workspace Symbols | `workspace/symbol` | Search all accounts |
| Inlay Hints | `textDocument/inlayHint` | Computed amounts |

---

## Diagnostics

### Diagnostic Severity Levels

| Severity | Usage |
|----------|-------|
| Error | Parse errors, validation errors, balance failures |
| Warning | Deprecated syntax, potential issues |
| Information | Suggestions, style hints |
| Hint | Minor improvements |

### Error Codes

Servers SHOULD use structured error codes. Recommended format:

```
beancount/parse/syntax-error
beancount/validation/account-not-opened
beancount/balance/assertion-failed
beancount/booking/ambiguous-match
```

### Diagnostic Tags

| Tag | Usage |
|-----|-------|
| `Unnecessary` | Unused accounts, redundant directives |
| `Deprecated` | Deprecated syntax features |

### Example Diagnostic

```json
{
  "range": {
    "start": {"line": 10, "character": 2},
    "end": {"line": 10, "character": 25}
  },
  "severity": 1,
  "code": "beancount/validation/account-not-opened",
  "source": "beancount",
  "message": "Account 'Assets:Checking' has not been opened",
  "relatedInformation": [
    {
      "location": {
        "uri": "file:///path/to/ledger.beancount",
        "range": {"start": {"line": 10, "character": 2}, "end": {"line": 10, "character": 25}}
      },
      "message": "First use of account here"
    }
  ]
}
```

---

## Completion

### Completion Triggers

| Trigger | Context | Completions |
|---------|---------|-------------|
| `:` after root type | `Assets:` | Account components |
| Space after date | `2024-01-15 ` | Directive keywords |
| Space after flag | `2024-01-15 * ` | Payees, narrations |
| `"` in transaction | String context | Payees from history |
| Space in posting | Posting line | Accounts |
| Space after amount | `100 ` | Currencies |
| `#` | Tag context | Existing tags |
| `^` | Link context | Existing links |
| `:` on new line | Metadata context | Metadata keys |

### Completion Item Kinds

| Kind | Usage |
|------|-------|
| `Class` | Accounts |
| `Unit` | Currencies/Commodities |
| `Text` | Payees, narrations |
| `Keyword` | Directives (`open`, `close`, etc.) |
| `Property` | Metadata keys |
| `Constant` | Tags, links |
| `Value` | Boolean (`TRUE`, `FALSE`) |

### Completion Item Details

Account completions SHOULD include:

```json
{
  "label": "Assets:Checking",
  "kind": 7,
  "detail": "USD | Balance: 1,234.56 USD",
  "documentation": {
    "kind": "markdown",
    "value": "**Opened:** 2024-01-01\n\n**Currencies:** USD\n\n**Balance:** 1,234.56 USD"
  },
  "sortText": "0001-Assets:Checking",
  "filterText": "Assets:Checking checking"
}
```

### Completion Sorting

1. Frequently used items first
2. Recently used items second
3. Alphabetical within groups

---

## Hover

### Hover Content

| Element | Hover Content |
|---------|---------------|
| Account | Open date, currencies, current balance, metadata |
| Commodity | Commodity directive metadata, latest price |
| Transaction | Balance impact, computed amounts |
| Posting amount | Price in operating currency |
| Cost specification | Total cost, per-unit cost |
| Date | Day of week, relative date |

### Account Hover Example

```markdown
## Assets:Checking

**Status:** Open since 2024-01-01
**Currencies:** USD

### Current Balance
| Currency | Balance |
|----------|---------|
| USD | 1,234.56 |

### Metadata
- `institution`: "Bank of America"
- `account-number`: "****1234"

### Recent Activity
- 2024-01-15: +500.00 USD (Salary)
- 2024-01-14: -50.00 USD (Groceries)
```

---

## Go to Definition

### Definition Targets

| Source Element | Definition Target |
|----------------|-------------------|
| Account in posting | `open` directive for account |
| Account in balance | `open` directive for account |
| Commodity | `commodity` directive |
| Include path | Included file |
| Plugin name | Plugin definition (if resolvable) |

---

## Find References

### Reference Sources

| Element | References Include |
|---------|-------------------|
| Account | All postings, balance assertions, pad directives |
| Commodity | All amounts, price directives, open directives |
| Tag | All tagged transactions |
| Link | All linked transactions |
| Payee | All transactions with same payee |

---

## Document Symbols

### Symbol Kinds

| Symbol Kind | Beancount Element |
|-------------|-------------------|
| `Namespace` | Account hierarchy root (Assets, Liabilities, etc.) |
| `Class` | Individual accounts |
| `Method` | Transactions |
| `Property` | Balance assertions |
| `Event` | Events, notes |
| `Constant` | Price directives |
| `Variable` | Pad directives |

### Symbol Hierarchy

```
Assets (Namespace)
├── Checking (Class)
│   └── 2024-01-15 * "Salary" (Method)
├── Savings (Class)
Liabilities (Namespace)
└── CreditCard (Class)
```

---

## Semantic Tokens

### Token Types

| Type | Elements |
|------|----------|
| `namespace` | Account root types (Assets, Liabilities, etc.) |
| `class` | Account names |
| `type` | Commodities/currencies |
| `number` | Amounts, dates |
| `string` | Narrations, payees, metadata values |
| `keyword` | Directive names (open, close, etc.) |
| `operator` | `@`, `@@`, `{}`, flags |
| `comment` | Comments |
| `variable` | Metadata keys |
| `macro` | Tags, links |

### Token Modifiers

| Modifier | Usage |
|----------|-------|
| `definition` | Account in `open` directive |
| `deprecated` | Closed accounts |
| `readonly` | Computed/elided amounts |

---

## Code Actions

### Quick Fixes

| Diagnostic | Code Action |
|------------|-------------|
| Account not opened | Insert `open` directive |
| Commodity not declared | Insert `commodity` directive |
| Balance assertion failed | Update amount to actual balance |
| Transaction doesn't balance | Add balancing posting |
| Duplicate metadata | Remove duplicate |

### Refactoring

| Action | Description |
|--------|-------------|
| Extract account | Create new account from posting pattern |
| Rename account | Rename account across all files |
| Split transaction | Split into multiple transactions |
| Merge transactions | Combine related transactions |

### Source Actions

| Action | Description |
|--------|-------------|
| Sort directives | Sort by date |
| Organize includes | Sort and dedupe includes |
| Format document | Apply standard formatting |
| Add missing opens | Auto-generate open directives |

---

## Formatting

### Formatting Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `tabSize` | number | 2 | Indentation size |
| `insertSpaces` | boolean | true | Use spaces for indent |
| `alignAmounts` | boolean | true | Align amounts in column |
| `amountColumn` | number | 52 | Column for amount alignment |
| `currencyColumn` | number | 61 | Column for currency |
| `sortDirectives` | boolean | false | Sort by date |
| `groupByMonth` | boolean | false | Add blank lines between months |

### Formatted Output Example

```beancount
2024-01-01 open Assets:Checking                        USD

2024-01-15 * "Salary deposit"
  Assets:Checking                                   1000.00 USD
  Income:Salary                                    -1000.00 USD

2024-01-20 * "Grocery shopping"
  Expenses:Food                                      50.00 USD
  Assets:Checking                                   -50.00 USD
```

---

## Configuration

### Server Configuration

```json
{
  "beancount.mainFile": "main.beancount",
  "beancount.pythonPath": "/usr/bin/python3",
  "beancount.formatting.alignAmounts": true,
  "beancount.formatting.amountColumn": 52,
  "beancount.diagnostics.unusedAccounts": "warning",
  "beancount.diagnostics.balanceAssertions": true,
  "beancount.completion.includeClosedAccounts": false,
  "beancount.hover.showBalance": true,
  "beancount.hover.showRecentTransactions": 5
}
```

---

## Custom Requests

Beancount LSP servers MAY implement custom requests:

### `beancount/getAccountBalance`

Get current balance for an account.

**Request:**
```json
{
  "account": "Assets:Checking",
  "date": "2024-01-15"
}
```

**Response:**
```json
{
  "balances": [
    {"currency": "USD", "amount": "1234.56"}
  ]
}
```

### `beancount/getAccountHistory`

Get transaction history for an account.

**Request:**
```json
{
  "account": "Assets:Checking",
  "startDate": "2024-01-01",
  "endDate": "2024-01-31",
  "limit": 100
}
```

### `beancount/runQuery`

Execute a BQL query.

**Request:**
```json
{
  "query": "SELECT account, sum(position) GROUP BY account"
}
```

### `beancount/getErrors`

Get all errors with structured data.

---

## Initialization

### Initialize Request

Server should advertise capabilities:

```json
{
  "capabilities": {
    "textDocumentSync": {
      "openClose": true,
      "change": 2,
      "save": {"includeText": false}
    },
    "completionProvider": {
      "triggerCharacters": [":", "\"", "#", "^", " "],
      "resolveProvider": true
    },
    "hoverProvider": true,
    "definitionProvider": true,
    "referencesProvider": true,
    "documentSymbolProvider": true,
    "workspaceSymbolProvider": true,
    "codeActionProvider": {
      "codeActionKinds": [
        "quickfix",
        "refactor",
        "source.organizeImports",
        "source.fixAll"
      ]
    },
    "documentFormattingProvider": true,
    "semanticTokensProvider": {
      "legend": {
        "tokenTypes": ["namespace", "class", "type", "number", "string", "keyword", "operator", "comment", "variable", "macro"],
        "tokenModifiers": ["definition", "deprecated", "readonly"]
      },
      "full": true
    },
    "foldingRangeProvider": true,
    "inlayHintProvider": true
  },
  "serverInfo": {
    "name": "beancount-lsp",
    "version": "1.0.0"
  }
}
```

---

## File Watching

Servers SHOULD watch for changes to:
- Main beancount file
- All included files
- Document files (for `document` directive)

```json
{
  "capabilities": {
    "workspace": {
      "workspaceFolders": {"supported": true},
      "fileOperations": {
        "didCreate": {"filters": [{"pattern": {"glob": "**/*.beancount"}}]},
        "didRename": {"filters": [{"pattern": {"glob": "**/*.beancount"}}]},
        "didDelete": {"filters": [{"pattern": {"glob": "**/*.beancount"}}]}
      }
    }
  }
}
```

---

## Implementation Notes

### Performance

1. **Incremental parsing:** Re-parse only changed sections
2. **Background validation:** Validate asynchronously
3. **Caching:** Cache parsed entries, account lists
4. **Debouncing:** Debounce diagnostics on rapid edits

### Multi-file Support

1. Resolve `include` directives
2. Track file dependencies
3. Invalidate dependents on change
4. Handle circular includes gracefully

### Error Recovery

1. Parse as much as possible on syntax errors
2. Provide partial completions during errors
3. Show multiple errors, not just first
