; Beancount code folding queries for tree-sitter

; Fold transactions (collapse postings and metadata)
(transaction) @fold

; Fold other directives with metadata
(open) @fold
(close) @fold
(balance) @fold
(pad) @fold
(commodity) @fold
(price) @fold
(event) @fold
(note) @fold
(document) @fold
(query) @fold
(custom) @fold
