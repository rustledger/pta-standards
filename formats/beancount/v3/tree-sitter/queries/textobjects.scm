; Beancount text objects for tree-sitter
; Used by editors like Neovim with nvim-treesitter-textobjects

; =============================================================================
; FUNCTION-LIKE OBJECTS (directives)
; =============================================================================

; Transaction as a "function" (af/if for around/inner function)
(transaction) @function.outer

(transaction
  (posting)+ @function.inner)

; Other directives as functions
(open) @function.outer
(close) @function.outer
(balance) @function.outer
(pad) @function.outer
(commodity) @function.outer
(price) @function.outer
(event) @function.outer
(note) @function.outer
(document) @function.outer
(query) @function.outer
(custom) @function.outer

; =============================================================================
; PARAMETER-LIKE OBJECTS (postings)
; =============================================================================

; Posting as a "parameter" (aa/ia for around/inner argument)
(posting) @parameter.outer

(posting
  (account) @parameter.inner)

; =============================================================================
; CLASS-LIKE OBJECTS (account hierarchies)
; =============================================================================

; Account as a "class"
(account) @class.outer

; =============================================================================
; COMMENT OBJECTS
; =============================================================================

(comment) @comment.outer

; =============================================================================
; STRING OBJECTS
; =============================================================================

(string) @string.outer

; =============================================================================
; NUMBER OBJECTS
; =============================================================================

(number) @number.outer
(amount) @number.outer

; =============================================================================
; BLOCK OBJECTS
; =============================================================================

; Cost specification as a block
(cost_spec) @block.outer

; =============================================================================
; STATEMENT OBJECTS
; =============================================================================

; Each directive is a statement
[
  (transaction)
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
] @statement.outer

; =============================================================================
; SCOPE NAVIGATION
; =============================================================================

; For jumping between directives
(directive) @scope
