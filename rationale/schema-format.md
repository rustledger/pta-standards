# Schema Format Choices

This document explains why we provide AST schemas in multiple formats.

## Context

The Abstract Syntax Tree (AST) is the programmatic representation of parsed ledger files. Schemas define the structure of this AST for validation, serialization, and code generation.

## Decision

We provide AST schemas in two formats:

1. **JSON Schema** - For validation and documentation
2. **Protocol Buffers** - For efficient serialization

## Rationale

### Why Schema Definitions?

Schemas serve multiple purposes:

| Purpose | Benefit |
|---------|---------|
| Validation | Verify AST structure correctness |
| Documentation | Precise type definitions |
| Code generation | Generate types in multiple languages |
| Serialization | Binary format for interchange |
| Testing | Generate test cases from schema |

### Why These Two Formats?

#### JSON Schema

**Strengths**:
- Human-readable JSON format
- Widely supported validation libraries
- Good for API documentation
- Web-friendly
- IDE support (autocomplete, validation)

**Use cases**:
- Validating JSON exports
- API response validation
- Documentation generation
- Editor tooling

**Example**:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "date": { "type": "string", "format": "date" },
    "flag": { "enum": ["*", "!", "txn"] },
    "narration": { "type": "string" }
  },
  "required": ["date", "flag", "narration"]
}
```

#### Protocol Buffers

**Strengths**:
- Efficient binary serialization
- Strong typing with code generation
- Language-neutral (generates code for many languages)
- Backwards-compatible evolution
- Industry standard (Google)

**Use cases**:
- Inter-process communication
- Cache serialization
- High-performance tools
- Cross-language libraries

**Example**:
```protobuf
message Transaction {
  string date = 1;
  string flag = 2;
  optional string payee = 3;
  string narration = 4;
  repeated Posting postings = 5;
}
```

## Alternatives Considered

### Alternative 1: JSON Schema Only

**Approach**: Provide only JSON Schema.

**Problems**:
- JSON is verbose for large files
- No efficient binary format
- Limited code generation

**Rejected because**: Performance-sensitive applications need binary format.

### Alternative 2: Protocol Buffers Only

**Approach**: Provide only Protocol Buffers.

**Problems**:
- Less accessible for web developers
- Requires protobuf toolchain
- Less readable for documentation

**Rejected because**: Limits accessibility and documentation use.

### Alternative 3: TypeScript Types

**Approach**: Use TypeScript as schema language.

**Problems**:
- Language-specific
- No validation runtime
- Limited to JS/TS ecosystem

**Rejected because**: Not language-neutral.

### Alternative 4: XML Schema (XSD)

**Approach**: Use XML Schema.

**Problems**:
- Verbose
- Declining usage
- XML less common in PTA tooling

**Rejected because**: JSON is more aligned with PTA ecosystem.

### Alternative 5: Apache Avro

**Approach**: Use Avro schema format.

**Problems**:
- Less widely known
- Primarily for Hadoop ecosystem
- Smaller tool ecosystem than protobuf

**Rejected because**: Protocol Buffers has broader adoption.

### Alternative 6: Cap'n Proto / FlatBuffers

**Approach**: Use zero-copy serialization formats.

**Problems**:
- Smaller ecosystems
- More complex tooling
- Less familiar to most developers

**Rejected because**: Marginal benefits don't justify reduced accessibility.

## Implementation

### File Organization

```
formats/beancount/v3/schema/
├── ast.schema.json    # JSON Schema
└── ast.proto          # Protocol Buffers
```

### Consistency Requirements

Both schemas MUST:

1. Define equivalent types
2. Use consistent naming
3. Handle optional fields the same way
4. Be generated from common source if possible

### Canonical Format

Neither format is canonical. Both are maintained as primary artifacts because they serve different purposes.

### Version Alignment

Schema versions align with specification versions:

```
formats/beancount/v3/schema/ast.schema.json  # v3 AST
formats/beancount/v2/schema/ast.schema.json  # v2 AST (if needed)
```

## Schema Design Principles

### 1. Match the Specification

Schemas reflect the specification exactly:

```protobuf
// Matches spec: Transaction has optional payee
message Transaction {
  optional string payee = 3;  // Optional per spec
}
```

### 2. Preserve All Information

Round-trip preservation:

```
Source File → AST → Schema → AST → Source File
             (parse)     (serialize/deserialize)   (unparse)
```

### 3. Clear Optionality

Explicitly mark optional vs required:

```json
{
  "required": ["date", "flag", "narration"],
  "properties": {
    "payee": { "type": "string" }  // Not in required = optional
  }
}
```

### 4. Extensible Design

Allow for future additions:

```protobuf
message Directive {
  oneof directive {
    Transaction transaction = 1;
    Open open = 2;
    // Future directives can be added
  }
  map<string, string> metadata = 100;  // Extensible metadata
}
```

## Consequences

### Benefits

1. **Validation** - Verify tool output correctness
2. **Interoperability** - Exchange ASTs between tools
3. **Code generation** - Reduce manual type definitions
4. **Documentation** - Precise, machine-readable type specs
5. **Testing** - Property-based testing from schemas

### Costs

1. **Maintenance** - Two schemas to maintain
2. **Synchronization** - Must stay aligned with spec
3. **Complexity** - Additional artifacts to understand

### Mitigation

- Generate tests verifying schema equivalence
- Update schemas as part of spec changes
- Document schema versioning clearly

## Usage Guidance

### For Validation

Use JSON Schema:

```python
import jsonschema

with open('ast.schema.json') as f:
    schema = json.load(f)

jsonschema.validate(ast_data, schema)
```

### For Serialization

Use Protocol Buffers:

```python
from generated import ast_pb2

txn = ast_pb2.Transaction()
txn.date = "2024-01-15"
txn.narration = "Purchase"

binary_data = txn.SerializeToString()
```

### For Code Generation

From Protocol Buffers:

```bash
protoc --python_out=. --rust_out=. ast.proto
```

From JSON Schema:

```bash
quicktype --lang rust --src ast.schema.json
```

## References

- [JSON Schema](https://json-schema.org/) - JSON Schema specification
- [Protocol Buffers](https://protobuf.dev/) - Google's Protocol Buffers
- [quicktype](https://quicktype.io/) - Code generation from JSON Schema
