; Beancount syntax highlighting queries for tree-sitter
; Compatible with Neovim, Helix, and other tree-sitter editors

; =============================================================================
; COMMENTS
; =============================================================================

(comment) @comment

; =============================================================================
; KEYWORDS
; =============================================================================

[
  "open"
  "close"
  "balance"
  "pad"
  "commodity"
  "price"
  "event"
  "note"
  "document"
  "query"
  "custom"
  "option"
  "include"
  "plugin"
  "pushtag"
  "poptag"
  "pushmeta"
  "popmeta"
  "txn"
] @keyword

; =============================================================================
; DATES
; =============================================================================

(date) @number.date

; =============================================================================
; ACCOUNTS
; =============================================================================

(account) @type

; Account root types for special highlighting
((account) @type.builtin
  (#match? @type.builtin "^(Assets|Liabilities|Equity|Income|Expenses):"))

; =============================================================================
; CURRENCIES / COMMODITIES
; =============================================================================

(currency) @constant

; =============================================================================
; NUMBERS AND AMOUNTS
; =============================================================================

(number) @number
(amount (number) @number)
(amount (currency) @constant)

; =============================================================================
; STRINGS
; =============================================================================

(string) @string

; =============================================================================
; TRANSACTION FLAGS
; =============================================================================

(txn_flag) @operator

; Complete transaction
((txn_flag) @constant.builtin
  (#eq? @constant.builtin "*"))

; Incomplete/pending transaction
((txn_flag) @warning
  (#eq? @warning "!"))

; Posting flags
(posting_flag) @operator

; =============================================================================
; TAGS AND LINKS
; =============================================================================

(tag) @label
(link) @label.link

; =============================================================================
; METADATA
; =============================================================================

(metadata_key) @property

; =============================================================================
; BOOLEANS
; =============================================================================

(boolean) @boolean

; =============================================================================
; PUNCTUATION
; =============================================================================

[
  "{"
  "}"
  "{{"
  "}}"
] @punctuation.bracket

[
  ":"
  ","
] @punctuation.delimiter

[
  "@"
  "@@"
  "~"
] @operator

; =============================================================================
; SPECIAL HIGHLIGHTING
; =============================================================================

; Option names
(option
  name: (string) @variable.parameter)

; Option values
(option
  value: (string) @string.special)

; Plugin module
(plugin
  module: (string) @module)

; Include path
(include (string) @string.special.path)

; Event type and value
(event
  type: (string) @variable.parameter
  value: (string) @string)

; Query name
(query
  name: (string) @function
  query_string: (string) @string.special)

; Custom directive type
(custom
  type: (string) @type)

; Pad accounts
(pad
  account: (account) @type
  pad_account: (account) @type.definition)

; Balance tolerance
(amount_with_tolerance
  (number) @number
  "~" @operator
  (number) @number)

; Cost specification star (merge)
(cost_comp
  "*" @operator.special)

; =============================================================================
; ERRORS (if your editor supports error highlighting)
; =============================================================================

(ERROR) @error
