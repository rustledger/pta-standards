# MCP Server Specification for PTA

This document specifies Model Context Protocol (MCP) server interfaces for PTA tools.

## Overview

MCP enables AI assistants to interact with PTA accounting data:
- Query balances and transactions
- Validate journal files
- Generate reports
- Assist with data entry

## Server Interface

### Resources

```json
{
  "resources": [
    {
      "uri": "pta://ledger/accounts",
      "name": "Account List",
      "mimeType": "application/json"
    },
    {
      "uri": "pta://ledger/transactions",
      "name": "Transaction List",
      "mimeType": "application/json"
    }
  ]
}
```

### Tools

```json
{
  "tools": [
    {
      "name": "balance",
      "description": "Get account balances",
      "inputSchema": {
        "type": "object",
        "properties": {
          "account": {"type": "string"},
          "date": {"type": "string", "format": "date"}
        }
      }
    },
    {
      "name": "register",
      "description": "Get transaction register",
      "inputSchema": {
        "type": "object",
        "properties": {
          "account": {"type": "string"},
          "start": {"type": "string", "format": "date"},
          "end": {"type": "string", "format": "date"}
        }
      }
    },
    {
      "name": "validate",
      "description": "Validate journal file",
      "inputSchema": {
        "type": "object",
        "properties": {
          "file": {"type": "string"}
        },
        "required": ["file"]
      }
    }
  ]
}
```

## Tool Definitions

### balance

Get account balances.

**Input:**
```json
{
  "account": "Assets:Bank",
  "date": "2024-01-31"
}
```

**Output:**
```json
{
  "balances": [
    {"account": "Assets:Bank:Checking", "amount": "1500.00", "commodity": "USD"},
    {"account": "Assets:Bank:Savings", "amount": "5000.00", "commodity": "USD"}
  ]
}
```

### register

Get transaction register.

**Input:**
```json
{
  "account": "Expenses:Food",
  "start": "2024-01-01",
  "end": "2024-01-31"
}
```

**Output:**
```json
{
  "transactions": [
    {
      "date": "2024-01-15",
      "payee": "Grocery Store",
      "amount": "50.00",
      "commodity": "USD",
      "balance": "150.00"
    }
  ]
}
```

### validate

Check journal for errors.

**Input:**
```json
{
  "file": "/path/to/journal.beancount"
}
```

**Output:**
```json
{
  "valid": false,
  "errors": [
    {
      "line": 42,
      "message": "Account not opened",
      "severity": "error"
    }
  ]
}
```

### add_transaction

Add a new transaction.

**Input:**
```json
{
  "date": "2024-01-15",
  "payee": "Store",
  "postings": [
    {"account": "Expenses:Food", "amount": "50.00", "commodity": "USD"},
    {"account": "Assets:Cash", "amount": "-50.00", "commodity": "USD"}
  ]
}
```

**Output:**
```json
{
  "success": true,
  "transaction": "2024-01-15 * \"Store\"\n  Expenses:Food  50.00 USD\n  Assets:Cash"
}
```

## Resource URIs

### Accounts

```
pta://ledger/accounts
pta://ledger/accounts/Assets
pta://ledger/accounts/Assets:Bank
```

### Transactions

```
pta://ledger/transactions
pta://ledger/transactions?start=2024-01-01&end=2024-01-31
pta://ledger/transactions?account=Expenses:Food
```

### Commodities

```
pta://ledger/commodities
pta://ledger/commodities/USD
```

## Prompts

### analyze_spending

```json
{
  "name": "analyze_spending",
  "description": "Analyze spending patterns",
  "arguments": [
    {"name": "period", "description": "Time period (e.g., 'this month')"}
  ]
}
```

### suggest_categorization

```json
{
  "name": "suggest_categorization",
  "description": "Suggest account for transaction",
  "arguments": [
    {"name": "payee", "description": "Payee name"},
    {"name": "amount", "description": "Transaction amount"}
  ]
}
```

## Implementation

### Python Example

```python
from mcp.server import Server
from mcp.types import Resource, Tool

server = Server("pta-mcp")

@server.list_resources()
async def list_resources():
    return [
        Resource(uri="pta://ledger/accounts", name="Accounts")
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "balance":
        return get_balances(arguments.get("account"))
```

## Security Considerations

1. **Read-only by default** - Write operations require explicit permission
2. **Path validation** - Prevent path traversal attacks
3. **Rate limiting** - Prevent abuse
4. **Audit logging** - Log all operations

## See Also

- [MCP Specification](https://modelcontextprotocol.io/)
- [Tooling Overview](../README.md)
