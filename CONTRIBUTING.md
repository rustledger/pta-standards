# Contributing to PTA Standards

Thank you for your interest in contributing to the Plain Text Accounting Standards!

## How to Contribute

### Reporting Issues

- **Spec clarifications**: Use the "Spec Clarification" issue template
- **Bugs in test cases**: Use the "Bug Report" template
- **New test cases**: Use the "Test Case" template
- **Feature requests**: Use the "Feature Request" template

### Making Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Make your changes
4. Run validation (`make validate`)
5. Submit a pull request

### Pull Request Guidelines

- One logical change per PR
- Include rationale for spec changes
- Add/update test cases as needed
- Follow existing formatting conventions

## RFC Process

Major changes require an RFC:

1. Copy `meta/rfcs/0000-template.md` to `meta/rfcs/XXXX-my-proposal.md`
2. Fill in the template
3. Submit as a PR
4. Discuss and iterate
5. Once accepted, implement the change

## Style Guide

### Markdown

- Use ATX headers (`#`, `##`, etc.)
- One sentence per line (for better diffs)
- Use fenced code blocks with language tags

### Grammar Files

- EBNF follows ISO 14977
- ABNF follows RFC 5234
- Include comments explaining non-obvious rules

### Test Cases

- One concept per test file
- Include both positive and negative tests
- Document expected behavior in comments

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under:
- CC-BY-4.0 for documentation
- MIT for code
