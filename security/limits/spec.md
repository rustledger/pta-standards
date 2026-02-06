# Limits Specification Summary

## Overview

This document summarizes all resource limits that implementations MUST or SHOULD enforce.

## Required Limits (MUST)

| Category | Limit | Minimum Value |
|----------|-------|---------------|
| File size | Single file | 10 MB |
| File size | Total with includes | 50 MB |
| Line length | Maximum | 4 KB |
| Include depth | Maximum | 10 |
| Include count | Total files | 100 |
| Parser recursion | Expression depth | 50 |

## Recommended Limits (SHOULD)

| Category | Limit | Recommended Value |
|----------|-------|-------------------|
| File size | Single file | 100 MB |
| File size | Total with includes | 500 MB |
| Line length | Maximum | 64 KB |
| Include depth | Maximum | 100 |
| Include count | Total files | 10,000 |
| Memory | Peak usage | 10x file size |
| Parser recursion | Expression depth | 200 |

## Configuration Options

Implementations SHOULD support these options:

| Option | Type | Default |
|--------|------|---------|
| `max_file_size` | Size | 100 MB |
| `max_total_size` | Size | 500 MB |
| `max_line_length` | Size | 64 KB |
| `max_include_depth` | Integer | 100 |
| `max_include_count` | Integer | 10,000 |
| `max_memory` | Size | unlimited |

## Size Format

Accept human-readable sizes:
- `100` - bytes
- `100KB` or `100K` - kilobytes
- `100MB` or `100M` - megabytes
- `100GB` or `100G` - gigabytes

## Behavior When Exceeded

| Limit Type | Behavior |
|------------|----------|
| File size | Reject before parsing |
| Line length | Reject line, continue if possible |
| Include depth | Reject include, report error |
| Include count | Reject include, report error |
| Memory | Abort with error message |
| Parser recursion | Reject expression, report error |

## Conformance Testing

Implementations MUST pass:

1. Accept input at exactly each limit
2. Reject input exceeding each limit
3. Report meaningful error messages
4. Not crash or hang on malicious input
