; Beancount injection queries for tree-sitter
; Embeds other languages within Beancount

; BQL queries embedded in query directives
(query
  query_string: (string) @injection.content
  (#set! injection.language "sql"))

; JSON in custom directives (if config looks like JSON)
(custom
  (string) @injection.content
  (#match? @injection.content "^\"\\{")
  (#set! injection.language "json"))

; Plugin config that looks like JSON
(plugin
  config: (string) @injection.content
  (#match? @injection.content "^\"\\{")
  (#set! injection.language "json"))
