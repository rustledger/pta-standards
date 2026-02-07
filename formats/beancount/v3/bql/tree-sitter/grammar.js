/**
 * Tree-sitter grammar for Beancount Query Language (BQL)
 *
 * BQL is a SQL-like language for querying Beancount ledgers.
 * It supports SELECT, BALANCES, JOURNAL, and PRINT statements.
 *
 * @see https://beancount.github.io/docs/beancount_query_language.html
 * @see https://tree-sitter.github.io/
 */

module.exports = grammar({
  name: 'bql',

  extras: $ => [
    /\s/,
    $.comment,
  ],

  word: $ => $.identifier,

  rules: {
    // =========================================================================
    // TOP LEVEL
    // =========================================================================

    query: $ => choice(
      $.select_statement,
      $.balances_statement,
      $.journal_statement,
      $.print_statement,
      $.run_statement,
      $.explain_statement,
    ),

    // =========================================================================
    // SELECT STATEMENT
    // =========================================================================

    select_statement: $ => seq(
      caseInsensitive('SELECT'),
      optional(caseInsensitive('DISTINCT')),
      $.select_list,
      optional($.from_clause),
      optional($.where_clause),
      optional($.group_by_clause),
      optional($.having_clause),
      optional($.order_by_clause),
      optional($.limit_clause),
      optional(caseInsensitive('FLATTEN')),
    ),

    select_list: $ => choice(
      '*',
      $.column_list,
    ),

    column_list: $ => seq(
      $.column,
      repeat(seq(',', $.column)),
    ),

    column: $ => seq(
      $.expression,
      optional(seq(
        optional(caseInsensitive('AS')),
        $.alias,
      )),
    ),

    alias: $ => $.identifier,

    // =========================================================================
    // FROM CLAUSE
    // =========================================================================

    from_clause: $ => seq(
      caseInsensitive('FROM'),
      $.from_expression,
    ),

    from_expression: $ => choice(
      $.identifier,
      seq(caseInsensitive('OPEN'), caseInsensitive('ON'), $.date),
      seq(caseInsensitive('CLOSE'), caseInsensitive('ON'), $.date),
      caseInsensitive('CLEAR'),
    ),

    // =========================================================================
    // WHERE CLAUSE
    // =========================================================================

    where_clause: $ => seq(
      caseInsensitive('WHERE'),
      $.expression,
    ),

    // =========================================================================
    // GROUP BY CLAUSE
    // =========================================================================

    group_by_clause: $ => seq(
      caseInsensitive('GROUP'),
      caseInsensitive('BY'),
      $.expression_list,
    ),

    expression_list: $ => seq(
      $.expression,
      repeat(seq(',', $.expression)),
    ),

    // =========================================================================
    // HAVING CLAUSE
    // =========================================================================

    having_clause: $ => seq(
      caseInsensitive('HAVING'),
      $.expression,
    ),

    // =========================================================================
    // ORDER BY CLAUSE
    // =========================================================================

    order_by_clause: $ => seq(
      caseInsensitive('ORDER'),
      caseInsensitive('BY'),
      $.order_list,
    ),

    order_list: $ => seq(
      $.order_item,
      repeat(seq(',', $.order_item)),
    ),

    order_item: $ => seq(
      $.expression,
      optional(choice(
        caseInsensitive('ASC'),
        caseInsensitive('DESC'),
      )),
    ),

    // =========================================================================
    // LIMIT CLAUSE
    // =========================================================================

    limit_clause: $ => seq(
      caseInsensitive('LIMIT'),
      $.integer,
    ),

    // =========================================================================
    // OTHER STATEMENTS
    // =========================================================================

    balances_statement: $ => seq(
      caseInsensitive('BALANCES'),
      optional($.from_clause),
      optional($.where_clause),
    ),

    journal_statement: $ => seq(
      caseInsensitive('JOURNAL'),
      optional($.account_pattern),
      optional($.from_clause),
      optional($.where_clause),
    ),

    account_pattern: $ => choice(
      $.account,
      $.string,
    ),

    print_statement: $ => seq(
      caseInsensitive('PRINT'),
      optional($.from_clause),
      optional($.where_clause),
    ),

    run_statement: $ => seq(
      caseInsensitive('RUN'),
      $.string,
    ),

    explain_statement: $ => seq(
      caseInsensitive('EXPLAIN'),
      choice(
        $.select_statement,
        $.balances_statement,
        $.journal_statement,
        $.print_statement,
      ),
    ),

    // =========================================================================
    // EXPRESSIONS
    // =========================================================================

    expression: $ => choice(
      $.or_expression,
    ),

    or_expression: $ => prec.left(1, seq(
      $.and_expression,
      repeat(seq(caseInsensitive('OR'), $.and_expression)),
    )),

    and_expression: $ => prec.left(2, seq(
      $.not_expression,
      repeat(seq(caseInsensitive('AND'), $.not_expression)),
    )),

    not_expression: $ => choice(
      seq(caseInsensitive('NOT'), $.comparison_expression),
      $.comparison_expression,
    ),

    comparison_expression: $ => prec.left(3, choice(
      seq($.additive_expression, $.comparison_operator, $.additive_expression),
      $.in_expression,
      $.between_expression,
      $.additive_expression,
    )),

    comparison_operator: $ => choice(
      '=', '==', '!=', '<>', '<', '<=', '>', '>=', '~', '!~',
    ),

    in_expression: $ => seq(
      $.additive_expression,
      optional(caseInsensitive('NOT')),
      caseInsensitive('IN'),
      '(',
      $.expression_list,
      ')',
    ),

    between_expression: $ => seq(
      $.additive_expression,
      optional(caseInsensitive('NOT')),
      caseInsensitive('BETWEEN'),
      $.additive_expression,
      caseInsensitive('AND'),
      $.additive_expression,
    ),

    additive_expression: $ => prec.left(4, seq(
      $.multiplicative_expression,
      repeat(seq(choice('+', '-'), $.multiplicative_expression)),
    )),

    multiplicative_expression: $ => prec.left(5, seq(
      $.unary_expression,
      repeat(seq(choice('*', '/'), $.unary_expression)),
    )),

    unary_expression: $ => choice(
      seq('-', $.postfix_expression),
      $.postfix_expression,
    ),

    postfix_expression: $ => prec.left(6, seq(
      $.primary_expression,
      repeat(seq('.', $.identifier)),
    )),

    primary_expression: $ => choice(
      $.literal,
      $.identifier,
      $.function_call,
      seq('(', $.expression, ')'),
      $.case_expression,
    ),

    // =========================================================================
    // FUNCTION CALLS
    // =========================================================================

    function_call: $ => seq(
      $.function_name,
      '(',
      optional($.argument_list),
      ')',
    ),

    function_name: $ => $.identifier,

    argument_list: $ => seq(
      $.expression,
      repeat(seq(',', $.expression)),
    ),

    // =========================================================================
    // CASE EXPRESSION
    // =========================================================================

    case_expression: $ => seq(
      caseInsensitive('CASE'),
      optional($.expression),
      repeat1($.when_clause),
      optional($.else_clause),
      caseInsensitive('END'),
    ),

    when_clause: $ => seq(
      caseInsensitive('WHEN'),
      $.expression,
      caseInsensitive('THEN'),
      $.expression,
    ),

    else_clause: $ => seq(
      caseInsensitive('ELSE'),
      $.expression,
    ),

    // =========================================================================
    // LITERALS
    // =========================================================================

    literal: $ => choice(
      $.null,
      $.boolean,
      $.number,
      $.string,
      $.date,
      $.account,
      $.currency,
    ),

    null: $ => caseInsensitive('NULL'),

    boolean: $ => choice(
      caseInsensitive('TRUE'),
      caseInsensitive('FALSE'),
    ),

    number: $ => /-?\d+(\.\d+)?/,

    integer: $ => /\d+/,

    string: $ => choice(
      seq('"', /[^"]*/, '"'),
      seq("'", /[^']*/, "'"),
    ),

    date: $ => /\d{4}-\d{2}-\d{2}/,

    account: $ => /[A-Z][A-Za-z0-9-]*(:[A-Z][A-Za-z0-9-]*)*/,

    currency: $ => /[A-Z][A-Z0-9._-]*/,

    // =========================================================================
    // IDENTIFIERS
    // =========================================================================

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_]*/,

    // =========================================================================
    // COMMENTS
    // =========================================================================

    comment: $ => seq('--', /.*/),
  },
});

// Helper function for case-insensitive keywords
function caseInsensitive(keyword) {
  return new RegExp(
    keyword
      .split('')
      .map(c => `[${c.toLowerCase()}${c.toUpperCase()}]`)
      .join('')
  );
}
