/**
 * Tree-sitter grammar for Beancount v3
 *
 * This grammar produces a concrete syntax tree suitable for syntax highlighting,
 * code folding, and other editor features.
 *
 * @see https://beancount.io/
 * @see https://tree-sitter.github.io/
 */

module.exports = grammar({
  name: 'beancount',

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
      $.directive,
      $.option,
      $.include,
      $.plugin,
      $.pushtag,
      $.poptag,
      $.pushmeta,
      $.popmeta,
      $.comment,
      $._newline,
    )),

    // =========================================================================
    // DIRECTIVES
    // =========================================================================

    directive: $ => choice(
      $.transaction,
      $.open,
      $.close,
      $.balance,
      $.pad,
      $.commodity,
      $.price,
      $.event,
      $.note,
      $.document,
      $.query,
      $.custom,
    ),

    // Transaction
    transaction: $ => seq(
      $.date,
      $.txn_flag,
      optional($.txn_strings),
      optional($.tags_links),
      $._newline,
      repeat1(choice($.posting, $.metadata)),
    ),

    txn_flag: $ => choice('*', '!', 'txn', 'P', '#'),

    txn_strings: $ => seq(
      $.string,
      optional($.string),
    ),

    posting: $ => seq(
      $._indent,
      optional($.posting_flag),
      $.account,
      optional(seq(
        $.amount,
        optional($.cost_spec),
        optional($.price_annotation),
      )),
      optional($.comment),
      $._newline,
      repeat($.posting_metadata),
    ),

    posting_flag: $ => choice('*', '!'),

    posting_metadata: $ => seq(
      $._indent,
      $._indent,
      $.metadata_key,
      ':',
      $.metadata_value,
      optional($.comment),
      $._newline,
    ),

    cost_spec: $ => choice(
      seq('{', optional($.cost_comp_list), '}'),
      seq('{{', optional($.cost_comp_list), '}}'),
    ),

    cost_comp_list: $ => seq(
      $.cost_comp,
      repeat(seq(',', $.cost_comp)),
    ),

    cost_comp: $ => choice(
      $.amount,
      $.date,
      $.string,
      '*',
    ),

    price_annotation: $ => seq(
      choice('@', '@@'),
      $.amount,
    ),

    // Open
    open: $ => seq(
      $.date,
      'open',
      $.account,
      optional($.currency_list),
      optional($.booking_method),
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    currency_list: $ => seq(
      $.currency,
      repeat(seq(',', $.currency)),
    ),

    booking_method: $ => $.string,

    // Close
    close: $ => seq(
      $.date,
      'close',
      $.account,
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    // Balance
    balance: $ => seq(
      $.date,
      'balance',
      $.account,
      $.amount_with_tolerance,
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    amount_with_tolerance: $ => seq(
      $.amount,
      optional(seq('~', $.number)),
    ),

    // Pad
    pad: $ => seq(
      $.date,
      'pad',
      field('account', $.account),
      field('pad_account', $.account),
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    // Commodity
    commodity: $ => seq(
      $.date,
      'commodity',
      $.currency,
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    // Price
    price: $ => seq(
      $.date,
      'price',
      $.currency,
      $.amount,
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    // Event
    event: $ => seq(
      $.date,
      'event',
      field('type', $.string),
      field('value', $.string),
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    // Note
    note: $ => seq(
      $.date,
      'note',
      $.account,
      $.string,
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    // Document
    document: $ => seq(
      $.date,
      'document',
      $.account,
      $.string,
      optional($.tags_links),
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    // Query
    query: $ => seq(
      $.date,
      'query',
      field('name', $.string),
      field('query_string', $.string),
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    // Custom
    custom: $ => seq(
      $.date,
      'custom',
      field('type', $.string),
      repeat($.custom_value),
      optional($.comment),
      $._newline,
      repeat($.metadata),
    ),

    custom_value: $ => choice(
      $.string,
      $.date,
      $.boolean,
      $.amount,
      $.account,
      $.number,
    ),

    // =========================================================================
    // META DIRECTIVES (undated)
    // =========================================================================

    option: $ => seq(
      'option',
      field('name', $.string),
      field('value', $.string),
      optional($.comment),
      $._newline,
    ),

    include: $ => seq(
      'include',
      $.string,
      optional($.comment),
      $._newline,
    ),

    plugin: $ => seq(
      'plugin',
      field('module', $.string),
      optional(field('config', $.string)),
      optional($.comment),
      $._newline,
    ),

    pushtag: $ => seq(
      'pushtag',
      $.tag,
      optional($.comment),
      $._newline,
    ),

    poptag: $ => seq(
      'poptag',
      $.tag,
      optional($.comment),
      $._newline,
    ),

    pushmeta: $ => seq(
      'pushmeta',
      $.metadata_key,
      ':',
      $.metadata_value,
      optional($.comment),
      $._newline,
    ),

    popmeta: $ => seq(
      'popmeta',
      $.metadata_key,
      ':',
      optional($.comment),
      $._newline,
    ),

    // =========================================================================
    // METADATA
    // =========================================================================

    metadata: $ => seq(
      $._indent,
      $.metadata_key,
      ':',
      $.metadata_value,
      optional($.comment),
      $._newline,
    ),

    metadata_key: $ => /[a-z][a-zA-Z0-9_-]*/,

    metadata_value: $ => choice(
      $.string,
      $.account,
      $.currency,
      $.date,
      $.tag,
      $.amount,
      $.number,
      $.boolean,
    ),

    // =========================================================================
    // PRIMITIVES
    // =========================================================================

    date: $ => /\d{4}[-\/]\d{2}[-\/]\d{2}/,

    account: $ => token(seq(
      choice('Assets', 'Liabilities', 'Equity', 'Income', 'Expenses'),
      repeat1(seq(':', /[A-Z0-9][A-Za-z0-9-]*/)),
    )),

    currency: $ => /[A-Z][A-Z0-9'._-]*[A-Z0-9]?/,

    amount: $ => seq(
      $.number,
      $.currency,
    ),

    number: $ => token(seq(
      optional('-'),
      choice(
        seq(/[0-9,]+/, optional(seq('.', /[0-9]+/))),
        seq('.', /[0-9]+/),
      ),
    )),

    string: $ => seq(
      '"',
      repeat(choice(
        /[^"\\]+/,
        /\\./,
      )),
      '"',
    ),

    tag: $ => /#[A-Za-z0-9_/-]+/,

    link: $ => /\^[A-Za-z0-9_/-]+/,

    tags_links: $ => repeat1(choice($.tag, $.link)),

    boolean: $ => choice('TRUE', 'FALSE'),

    // =========================================================================
    // COMMENTS
    // =========================================================================

    comment: $ => /;[^\n]*/,
  },
});
