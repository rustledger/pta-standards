/**
 * Tree-sitter grammar for hledger
 *
 * This grammar produces a concrete syntax tree suitable for syntax highlighting,
 * code folding, and other editor features.
 *
 * @see https://hledger.org/
 * @see https://tree-sitter.github.io/
 */

module.exports = grammar({
  name: 'hledger',

  extras: $ => [
    /[ \t]/,
  ],

  externals: $ => [
    $._newline,
    $._indent,
    $._dedent,
  ],

  rules: {
    // =========================================================================
    // TOP LEVEL
    // =========================================================================

    file: $ => repeat(choice(
      $.transaction,
      $.periodic_transaction,
      $.auto_posting_rule,
      $.directive,
      $.comment,
      $._newline,
    )),

    // =========================================================================
    // TRANSACTIONS
    // =========================================================================

    transaction: $ => seq(
      $.date,
      optional(seq('=', $.date2)),
      optional($.status),
      optional($.code),
      $.description,
      optional($.comment),
      $._newline,
      repeat1(choice($.posting, $.comment_line)),
    ),

    date: $ => /\d{4}[-\/\.]\d{2}[-\/\.]\d{2}/,

    date2: $ => /\d{4}[-\/\.]\d{2}[-\/\.]\d{2}/,

    status: $ => choice('*', '!'),

    code: $ => seq('(', /[^)]*/, ')'),

    description: $ => /[^\n;]+/,

    // =========================================================================
    // POSTINGS
    // =========================================================================

    posting: $ => seq(
      $._indent,
      optional($.posting_status),
      $.account,
      optional(seq(
        $.amount,
        optional($.price),
        optional($.balance_assertion),
      )),
      optional($.comment),
      $._newline,
    ),

    posting_status: $ => choice('*', '!'),

    account: $ => choice(
      $.real_account,
      $.virtual_account,
      $.balanced_virtual_account,
    ),

    real_account: $ => /[A-Za-z][A-Za-z0-9 ]*(?::[A-Za-z0-9 ]+)*/,

    virtual_account: $ => seq('(', $.real_account, ')'),

    balanced_virtual_account: $ => seq('[', $.real_account, ']'),

    // =========================================================================
    // AMOUNTS
    // =========================================================================

    amount: $ => seq(
      optional('-'),
      choice(
        seq($.commodity, $.quantity),
        seq($.quantity, $.commodity),
        $.quantity,
      ),
    ),

    quantity: $ => /[0-9,.' ]+(\.[0-9]+)?/,

    commodity: $ => choice(
      /\$|€|£|¥/,
      /[A-Z][A-Z0-9]*/,
      seq('"', /[^"]+/, '"'),
    ),

    // =========================================================================
    // PRICE AND ASSERTIONS
    // =========================================================================

    price: $ => seq(
      choice('@', '@@'),
      $.amount,
    ),

    balance_assertion: $ => seq(
      choice('=', '=*'),
      $.amount,
    ),

    balance_assignment: $ => seq(
      '=',
      $.amount,
    ),

    // =========================================================================
    // PERIODIC TRANSACTIONS
    // =========================================================================

    periodic_transaction: $ => seq(
      '~',
      $.period_expression,
      optional($.description),
      optional($.comment),
      $._newline,
      repeat1($.posting),
    ),

    period_expression: $ => /[^\n;]+/,

    // =========================================================================
    // AUTO-POSTING RULES
    // =========================================================================

    auto_posting_rule: $ => seq(
      '=',
      $.query_expression,
      optional($.comment),
      $._newline,
      repeat1($.auto_posting),
    ),

    query_expression: $ => /[^\n;]+/,

    auto_posting: $ => seq(
      $._indent,
      $.account,
      optional($.auto_amount),
      optional($.comment),
      $._newline,
    ),

    auto_amount: $ => choice(
      $.amount,
      seq('*', $.number),
    ),

    number: $ => /-?[0-9]+(\.[0-9]+)?/,

    // =========================================================================
    // DIRECTIVES
    // =========================================================================

    directive: $ => choice(
      $.account_directive,
      $.commodity_directive,
      $.payee_directive,
      $.tag_directive,
      $.include_directive,
      $.decimal_mark_directive,
      $.comment_block,
    ),

    // Account directive
    account_directive: $ => seq(
      'account',
      $.real_account,
      optional($.comment),
      $._newline,
      repeat($.account_subdirective),
    ),

    account_subdirective: $ => seq(
      $._indent,
      choice(
        seq('type:', $.account_type),
        seq('alias:', /[^\n]+/),
        seq('note:', /[^\n]+/),
        'default',
      ),
      $._newline,
    ),

    account_type: $ => choice(
      'Asset', 'Liability', 'Equity', 'Revenue', 'Expense', 'Cash',
    ),

    // Commodity directive
    commodity_directive: $ => seq(
      'commodity',
      choice(
        $.amount,  // Format: commodity $1,000.00
        seq($.commodity, $._newline, repeat($.commodity_subdirective)),  // With subdirectives
      ),
      optional($.comment),
      $._newline,
    ),

    commodity_subdirective: $ => seq(
      $._indent,
      seq('format', $.amount),
      $._newline,
    ),

    // Payee directive
    payee_directive: $ => seq(
      'payee',
      /[^\n;]+/,
      optional($.comment),
      $._newline,
    ),

    // Tag directive
    tag_directive: $ => seq(
      'tag',
      $.tag_name,
      optional($.comment),
      $._newline,
    ),

    tag_name: $ => /[a-zA-Z][a-zA-Z0-9_-]*/,

    // Include directive
    include_directive: $ => seq(
      'include',
      $.path,
      optional($.comment),
      $._newline,
    ),

    path: $ => /[^\n;]+/,

    // Decimal mark directive
    decimal_mark_directive: $ => seq(
      'decimal-mark',
      choice('.', ','),
      optional($.comment),
      $._newline,
    ),

    // Comment block
    comment_block: $ => seq(
      'comment',
      $._newline,
      repeat($.comment_block_line),
      'end',
      'comment',
      $._newline,
    ),

    comment_block_line: $ => seq(/[^\n]*/, $._newline),

    // =========================================================================
    // COMMENTS AND TAGS
    // =========================================================================

    comment_line: $ => seq(
      $._indent,
      $.comment,
      $._newline,
    ),

    comment: $ => choice(
      seq(';', /[^\n]*/),
      seq('#', /[^\n]*/),
      seq('*', /[^\n]*/),
    ),

    // Inline tags
    tag: $ => seq($.tag_name, ':', optional(/[^,\n]+/)),

    tags: $ => seq($.tag, repeat(seq(',', $.tag))),
  },
});
