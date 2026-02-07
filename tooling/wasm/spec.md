# WASM Interface Specification for PTA

This document specifies WebAssembly interfaces for PTA tools.

## Overview

WASM compilation enables:
- Browser-based editors
- Cross-platform tools
- Sandboxed execution
- JavaScript integration

## Interface

### Memory Model

```wat
(memory (export "memory") 1)
```

Linear memory for string passing.

### Core Functions

```typescript
// Parse journal and return AST
export function parse(input: string): ParseResult;

// Validate parsed journal
export function validate(input: string): ValidationResult;

// Format journal
export function format(input: string): string;

// Check balance
export function check_balance(input: string): BalanceResult;
```

### Types

```typescript
interface ParseResult {
  success: boolean;
  ast?: AST;
  errors?: Error[];
}

interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

interface BalanceResult {
  balanced: boolean;
  accounts: AccountBalance[];
}

interface Error {
  line: number;
  column: number;
  message: string;
}
```

## String Passing

### Input

```javascript
// Allocate memory
const encoder = new TextEncoder();
const bytes = encoder.encode(input);
const ptr = wasm.alloc(bytes.length);

// Copy to WASM memory
const memory = new Uint8Array(wasm.memory.buffer);
memory.set(bytes, ptr);

// Call function
const result = wasm.parse(ptr, bytes.length);
```

### Output

```javascript
// Read result
const resultPtr = wasm.get_result_ptr();
const resultLen = wasm.get_result_len();
const resultBytes = memory.slice(resultPtr, resultPtr + resultLen);
const result = new TextDecoder().decode(resultBytes);

// Free memory
wasm.free(resultPtr);
```

## Exported Functions

### parse

```rust
#[wasm_bindgen]
pub fn parse(input: &str) -> JsValue {
    match parser::parse(input) {
        Ok(ast) => serde_wasm_bindgen::to_value(&ast).unwrap(),
        Err(errors) => serde_wasm_bindgen::to_value(&errors).unwrap(),
    }
}
```

### validate

```rust
#[wasm_bindgen]
pub fn validate(input: &str) -> JsValue {
    let ast = parser::parse(input)?;
    let errors = validator::validate(&ast);
    serde_wasm_bindgen::to_value(&errors).unwrap()
}
```

### format

```rust
#[wasm_bindgen]
pub fn format(input: &str) -> String {
    let ast = parser::parse(input).unwrap();
    formatter::format(&ast)
}
```

## JavaScript API

### High-Level Wrapper

```javascript
class PTAParser {
  constructor(wasmModule) {
    this.wasm = wasmModule;
  }

  parse(input) {
    return JSON.parse(this.wasm.parse(input));
  }

  validate(input) {
    return JSON.parse(this.wasm.validate(input));
  }

  format(input) {
    return this.wasm.format(input);
  }
}
```

### Usage

```javascript
import init, { PTAParser } from 'pta-wasm';

async function main() {
  await init();
  const parser = new PTAParser();

  const result = parser.parse(`
    2024-01-15 * "Test"
      Expenses:Food  50.00 USD
      Assets:Cash
  `);

  console.log(result);
}
```

## Error Handling

### Error Format

```json
{
  "type": "parse_error",
  "errors": [
    {
      "line": 5,
      "column": 10,
      "message": "Expected amount",
      "code": "P-002"
    }
  ]
}
```

### Exception Handling

```javascript
try {
  const result = parser.parse(input);
} catch (e) {
  if (e instanceof PTAParseError) {
    console.error("Parse error:", e.errors);
  }
}
```

## Performance

### Compilation

```bash
# Release build with size optimization
wasm-pack build --release -- --features wasm
wasm-opt -Os pkg/pta_bg.wasm -o pkg/pta_bg.wasm
```

### Streaming Instantiation

```javascript
const wasm = await WebAssembly.instantiateStreaming(
  fetch('pta_bg.wasm'),
  imports
);
```

## Browser Compatibility

### Requirements

- WebAssembly MVP
- JavaScript BigInt (for large numbers)
- TextEncoder/TextDecoder

### Polyfills

```html
<script src="text-encoding-polyfill.js"></script>
```

## Package Distribution

### npm

```json
{
  "name": "pta-wasm",
  "version": "1.0.0",
  "main": "pkg/pta.js",
  "types": "pkg/pta.d.ts",
  "files": ["pkg/"]
}
```

### CDN

```html
<script type="module">
  import init from 'https://unpkg.com/pta-wasm/pkg/pta.js';
  await init();
</script>
```

## See Also

- [Tooling Overview](../README.md)
- [Rust wasm-bindgen](https://rustwasm.github.io/wasm-bindgen/)
