/**
 * Tree-sitter grammar for hledger CSV import rules
 *
 * CSV rules files specify how to transform CSV data into journal entries.
 * They support field mapping, conditionals, and transformations.
 *
 * @see https://hledger.org/csv.html
 * @see https://tree-sitter.github.io/
 */

module.exports = grammar({
  name: 'hledger_csv_rules',

  extras: $ => [
    / /,
    /\t/,
  ],

  rules: {
    // =========================================================================
    // TOP LEVEL
    // =========================================================================

    file: $ => repeat(choice(
      $.rule,
      $.conditional_block,
      $.comment,
      $._newline,
    )),

    // =========================================================================
    // RULES
    // =========================================================================

    rule: $ => choice(
      $.skip_rule,
      $.separator_rule,
      $.fields_rule,
      $.field_assignment,
      $.date_format_rule,
      $.decimal_mark_rule,
      $.currency_rule,
      $.newest_first_rule,
      $.include_rule,
      $.source_rule,
    ),

    // Skip N header lines
    skip_rule: $ => seq(
      'skip',
      optional(choice($.number, 'end')),
      $._newline,
    ),

    // Field separator character
    separator_rule: $ => seq(
      'separator',
      $.separator_value,
      $._newline,
    ),

    separator_value: $ => choice(
      $.quoted_char,
      /[^\s\n]/,
    ),

    quoted_char: $ => seq(
      '"',
      /./,
      '"',
    ),

    // Define field names for CSV columns
    fields_rule: $ => seq(
      'fields',
      $.field_list,
      $._newline,
    ),

    field_list: $ => seq(
      $.field_name,
      repeat(seq(',', $.field_name)),
    ),

    // Assign value to a field
    field_assignment: $ => seq(
      $.field_name,
      $.value_template,
      $._newline,
    ),

    field_name: $ => choice(
      'date', 'date2', 'status', 'code',
      'description', 'payee', 'comment',
      'account1', 'account2',
      'amount', 'amount-in', 'amount-out',
      'currency', 'balance',
      $.identifier,
    ),

    // Value template with variable substitution
    value_template: $ => repeat1(choice(
      $.variable_ref,
      $.literal_text,
    )),

    variable_ref: $ => choice(
      seq('%', $.field_name),
      seq('%', $.number),
      seq('%', '(', /[^)]+/, ')'),
      seq('%', 'default'),
    ),

    literal_text: $ => /[^%\n]+/,

    // Date format specification
    date_format_rule: $ => seq(
      'date-format',
      $.date_format_spec,
      $._newline,
    ),

    date_format_spec: $ => /[^\n]+/,

    // Decimal mark
    decimal_mark_rule: $ => seq(
      'decimal-mark',
      choice('.', ','),
      $._newline,
    ),

    // Default currency
    currency_rule: $ => seq(
      'currency',
      $.currency_symbol,
      $._newline,
    ),

    currency_symbol: $ => /[^\s\n]+/,

    // Newest transactions first
    newest_first_rule: $ => seq(
      'newest-first',
      $._newline,
    ),

    // Include another rules file
    include_rule: $ => seq(
      'include',
      $.file_path,
      $._newline,
    ),

    file_path: $ => /[^\n]+/,

    // Source file pattern
    source_rule: $ => seq(
      'source',
      $.glob_pattern,
      $._newline,
    ),

    glob_pattern: $ => /[^\n]+/,

    // =========================================================================
    // CONDITIONAL BLOCKS
    // =========================================================================

    conditional_block: $ => seq(
      $.if_clause,
      repeat($.conditional_rule),
    ),

    if_clause: $ => seq(
      'if',
      $.condition,
      $._newline,
    ),

    condition: $ => choice(
      $.regex_condition,
      $.field_condition,
      $.amount_condition,
    ),

    // Regex match against description
    regex_condition: $ => seq(
      optional('!'),
      $.regex,
    ),

    regex: $ => seq(
      '/',
      /[^\/\n]+/,
      '/',
    ),

    // Field comparison
    field_condition: $ => seq(
      optional('!'),
      $.field_name,
      $.comparison_op,
      $.comparison_value,
    ),

    comparison_op: $ => choice(
      '=', '==', '!=', '<', '<=', '>', '>=', '=~', '!~',
    ),

    comparison_value: $ => /[^\n]+/,

    // Amount-based condition
    amount_condition: $ => seq(
      optional('!'),
      'amount',
      choice(
        seq($.comparison_op, $.number),
        'positive',
        'negative',
        'zero',
      ),
    ),

    // Rule inside conditional block (indented)
    conditional_rule: $ => seq(
      /[ \t]+/,
      $.rule,
    ),

    // =========================================================================
    // COMMENTS
    // =========================================================================

    comment: $ => seq(
      choice(';', '#'),
      optional(/[^\n]*/),
      $._newline,
    ),

    // =========================================================================
    // PRIMITIVES
    // =========================================================================

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_-]*/,

    number: $ => /-?\d+(\.\d+)?/,

    _newline: $ => /\r?\n/,
  },
});
