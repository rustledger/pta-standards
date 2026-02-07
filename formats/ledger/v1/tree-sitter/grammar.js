/**
 * Tree-sitter grammar for Ledger
 *
 * This grammar produces a concrete syntax tree suitable for syntax highlighting,
 * code folding, and other editor features.
 *
 * @see https://www.ledger-cli.org/
 * @see https://tree-sitter.github.io/
 */

module.exports = grammar({
  name: 'ledger',

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
      $.automated_transaction,
      $.directive,
      $.comment,
      $._newline,
    )),

    // =========================================================================
    // TRANSACTIONS
    // =========================================================================

    transaction: $ => seq(
      $.date,
      optional(seq('=', $.effective_date)),
      optional($.status),
      optional($.code),
      optional($.payee),
      optional($.comment),
      $._newline,
      repeat1(choice($.posting, $.note_line)),
    ),

    date: $ => /\d{4}[\/\-]\d{2}[\/\-]\d{2}/,

    effective_date: $ => /\d{4}[\/\-]\d{2}[\/\-]\d{2}/,

    status: $ => choice('*', '!'),

    code: $ => seq('(', /[^)]*/, ')'),

    payee: $ => /[^\n;]+/,

    // =========================================================================
    // POSTINGS
    // =========================================================================

    posting: $ => seq(
      $._indent,
      optional($.posting_status),
      $.account,
      optional(seq(
        $.amount,
        optional($.lot_price),
        optional($.price),
        optional($.balance_assertion),
      )),
      optional($.comment),
      $._newline,
      repeat($.posting_metadata),
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

    quantity: $ => /[0-9,]+(\.[0-9]+)?/,

    commodity: $ => choice(
      /\$|€|£|¥/,
      /[A-Z][A-Z0-9]*/,
      seq('"', /[^"]+/, '"'),
    ),

    // =========================================================================
    // PRICE AND COST
    // =========================================================================

    price: $ => seq(
      choice('@', '@@'),
      $.amount,
    ),

    lot_price: $ => choice(
      seq('{', $.amount, '}'),
      seq('{{', $.amount, '}}'),
    ),

    lot_date: $ => seq('[', $.date, ']'),

    lot_note: $ => seq('(', /[^)]+/, ')'),

    balance_assertion: $ => seq(
      choice('=', '=='),
      $.amount,
    ),

    // =========================================================================
    // PERIODIC TRANSACTIONS
    // =========================================================================

    periodic_transaction: $ => seq(
      '~',
      $.period_expression,
      optional($.payee),
      optional($.comment),
      $._newline,
      repeat1($.posting),
    ),

    period_expression: $ => /[^\n;]+/,

    // =========================================================================
    // AUTOMATED TRANSACTIONS
    // =========================================================================

    automated_transaction: $ => seq(
      '=',
      choice(
        seq('expr', $.expression),
        $.account_pattern,
      ),
      optional($.comment),
      $._newline,
      repeat1($.auto_posting),
    ),

    account_pattern: $ => /[^\n;]+/,

    expression: $ => /[^\n;]+/,

    auto_posting: $ => seq(
      $._indent,
      $.account,
      optional($.auto_amount),
      optional($.comment),
      $._newline,
    ),

    auto_amount: $ => choice(
      $.amount,
      seq('(', $.value_expression, ')'),
    ),

    value_expression: $ => /[^)\n]+/,

    // =========================================================================
    // DIRECTIVES
    // =========================================================================

    directive: $ => choice(
      $.account_directive,
      $.commodity_directive,
      $.price_directive,
      $.include_directive,
      $.alias_directive,
      $.bucket_directive,
      $.year_directive,
      $.default_directive,
      $.tag_directive,
      $.payee_directive,
      $.assert_directive,
      $.check_directive,
      $.define_directive,
      $.apply_directive,
      $.end_apply_directive,
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
        seq('note', /[^\n]+/),
        seq('alias', /[^\n]+/),
        seq('payee', /[^\n]+/),
        seq('check', $.expression),
        seq('assert', $.expression),
        seq('eval', $.expression),
        'default',
      ),
      $._newline,
    ),

    // Commodity directive
    commodity_directive: $ => seq(
      'commodity',
      $.commodity,
      optional($.comment),
      $._newline,
      repeat($.commodity_subdirective),
    ),

    commodity_subdirective: $ => seq(
      $._indent,
      choice(
        seq('format', $.amount),
        seq('note', /[^\n]+/),
        seq('alias', /[^\n]+/),
        'nomarket',
        'default',
      ),
      $._newline,
    ),

    // Price directive
    price_directive: $ => seq(
      'P',
      $.date,
      optional($.time),
      $.commodity,
      $.amount,
      optional($.comment),
      $._newline,
    ),

    time: $ => /\d{2}:\d{2}(:\d{2})?/,

    // Include directive
    include_directive: $ => seq(
      'include',
      $.path,
      optional($.comment),
      $._newline,
    ),

    path: $ => /[^\n;]+/,

    // Alias directive
    alias_directive: $ => seq(
      'alias',
      /[^\n=]+/,
      '=',
      /[^\n]+/,
      $._newline,
    ),

    // Bucket directive
    bucket_directive: $ => seq(
      choice('bucket', 'A'),
      $.real_account,
      optional($.comment),
      $._newline,
    ),

    // Year directive
    year_directive: $ => seq(
      choice('year', 'Y'),
      /\d{4}/,
      optional($.comment),
      $._newline,
    ),

    // Default commodity directive
    default_directive: $ => seq(
      'D',
      $.amount,
      optional($.comment),
      $._newline,
    ),

    // Tag directive
    tag_directive: $ => seq(
      'tag',
      $.tag_name,
      optional($.comment),
      $._newline,
      repeat($.tag_subdirective),
    ),

    tag_name: $ => /[a-zA-Z][a-zA-Z0-9_-]*/,

    tag_subdirective: $ => seq(
      $._indent,
      choice(
        seq('check', $.expression),
        seq('assert', $.expression),
      ),
      $._newline,
    ),

    // Payee directive
    payee_directive: $ => seq(
      'payee',
      /[^\n;]+/,
      optional($.comment),
      $._newline,
      repeat($.payee_subdirective),
    ),

    payee_subdirective: $ => seq(
      $._indent,
      choice(
        seq('alias', /[^\n]+/),
        seq('uuid', /[^\n]+/),
      ),
      $._newline,
    ),

    // Assert directive
    assert_directive: $ => seq(
      'assert',
      $.expression,
      optional($.comment),
      $._newline,
    ),

    // Check directive
    check_directive: $ => seq(
      'check',
      $.expression,
      optional($.comment),
      $._newline,
    ),

    // Define directive
    define_directive: $ => seq(
      'define',
      $.identifier,
      '=',
      $.expression,
      optional($.comment),
      $._newline,
    ),

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_]*/,

    // Apply directive
    apply_directive: $ => seq(
      'apply',
      choice('account', 'tag'),
      /[^\n;]+/,
      optional($.comment),
      $._newline,
    ),

    end_apply_directive: $ => seq(
      'end',
      'apply',
      choice('account', 'tag'),
      optional($.comment),
      $._newline,
    ),

    // =========================================================================
    // METADATA AND COMMENTS
    // =========================================================================

    note_line: $ => seq(
      $._indent,
      $.comment,
      $._newline,
    ),

    posting_metadata: $ => seq(
      $._indent,
      $._indent,
      $.comment,
      $._newline,
    ),

    comment: $ => choice(
      seq(';', /[^\n]*/),
      seq('#', /[^\n]*/),
      seq('*', /[^\n]*/),
    ),

    // =========================================================================
    // TAGS
    // =========================================================================

    tag: $ => seq(':', $.tag_name, ':'),

    metadata_tag: $ => seq($.tag_name, ':', optional(/[^,\n]+/)),
  },
});
