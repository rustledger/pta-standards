; Beancount locals queries for tree-sitter
; Defines scopes and references for semantic analysis

; File is a scope
(file) @local.scope

; Account definitions (open directive)
(open
  (account) @local.definition)

; Account references (in postings)
(posting
  (account) @local.reference)

; Account references (in other directives)
(close
  (account) @local.reference)

(balance
  (account) @local.reference)

(pad
  account: (account) @local.reference
  pad_account: (account) @local.reference)

(note
  (account) @local.reference)

(document
  (account) @local.reference)

; Commodity definitions
(commodity
  (currency) @local.definition)

; Tag references
(tag) @local.reference

; Link references
(link) @local.reference
