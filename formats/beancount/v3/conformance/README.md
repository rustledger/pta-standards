# Beancount v3 Conformance

This directory tracks how implementations conform to the Beancount v3 specification.

## Structure

Each implementation has its own conformance file:

| File | Implementation |
|------|----------------|
| `python-beancount.md` | Python beancount (reference implementation) |

## Purpose

The specification in `../spec/` defines **what SHOULD happen** (normative).

Conformance files document **how well implementations meet the spec** (informative):

- :white_check_mark: Fully conformant
- :warning: Partial - missing features or minor deviations
- :x: Non-conformant - significant deviation from spec
- :hourglass: Spec undefined - awaiting clarification

## Pending Issues

When spec behavior is unclear (marked UNDEFINED in spec), issues are filed with the respective project to get clarification. These are tracked in each conformance file's "Pending Issues" section.

## Adding a New Implementation

To track a new implementation:

1. Create `<implementation-name>.md`
2. Use the existing files as a template
3. Document conformance status for each spec area
4. Note any deviations with details

## CI Testing

*Future: Automated conformance tests will run against implementations and update status.*
