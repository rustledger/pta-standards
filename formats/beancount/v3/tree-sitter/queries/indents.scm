; Beancount indentation queries for tree-sitter

; Indent after transaction header
(transaction
  (txn_flag)
  (txn_strings)? @indent)

; Indent postings within transaction
(posting) @indent

; Indent metadata
(metadata) @indent
(posting_metadata) @indent.always

; Dedent at end of transaction
(transaction) @dedent

; Dedent at start of new directive
[
  (open)
  (close)
  (balance)
  (pad)
  (commodity)
  (price)
  (event)
  (note)
  (document)
  (query)
  (custom)
  (option)
  (include)
  (plugin)
] @dedent
