/**
 * Tree-sitter grammar for hledger Timedot format
 *
 * Timedot is a simple time-logging format where each dot represents
 * 0.25 hours (15 minutes) of time spent on an activity.
 *
 * @see https://hledger.org/timedot.html
 * @see https://tree-sitter.github.io/
 */

module.exports = grammar({
  name: 'timedot',

  extras: $ => [
    / /,
    /\t/,
  ],

  rules: {
    // =========================================================================
    // TOP LEVEL
    // =========================================================================

    file: $ => repeat(choice(
      $.day_entry,
      $.comment,
      $._newline,
    )),

    // =========================================================================
    // DAY ENTRIES
    // =========================================================================

    // A day entry starts with a date and is followed by activity lines
    day_entry: $ => seq(
      $.date_line,
      repeat($.activity_line),
    ),

    // Date line marks the start of a day
    date_line: $ => seq(
      $.date,
      optional($.description),
      optional($.comment),
      $._newline,
    ),

    // Activity line records time for an account
    activity_line: $ => seq(
      $.account,
      optional($.duration),
      optional($.comment),
      $._newline,
    ),

    // =========================================================================
    // DATES
    // =========================================================================

    date: $ => choice(
      $.full_date,
      $.partial_date,
      $.day_name,
    ),

    // YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD
    full_date: $ => seq(
      $.year,
      choice('-', '/', '.'),
      $.month,
      choice('-', '/', '.'),
      $.day,
    ),

    // MM-DD or MM/DD
    partial_date: $ => seq(
      $.month,
      choice('-', '/', '.'),
      $.day,
    ),

    // Day of week name
    day_name: $ => choice(
      'monday', 'tuesday', 'wednesday', 'thursday',
      'friday', 'saturday', 'sunday',
      'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
      'Monday', 'Tuesday', 'Wednesday', 'Thursday',
      'Friday', 'Saturday', 'Sunday',
      'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun',
    ),

    year: $ => /\d{4}/,
    month: $ => /\d{1,2}/,
    day: $ => /\d{1,2}/,

    // =========================================================================
    // ACCOUNTS
    // =========================================================================

    account: $ => /[^\s:;#][^\s;#]*(?::[^\s:;#]+)*/,

    // =========================================================================
    // DURATIONS
    // =========================================================================

    duration: $ => choice(
      $.dot_duration,
      $.numeric_duration,
      $.time_range,
    ),

    // Dots: each dot/symbol represents 0.25 hours
    dot_duration: $ => /[.+\-oO0]+/,

    // Numeric duration with optional unit
    numeric_duration: $ => seq(
      $.number,
      optional($.time_unit),
    ),

    // Time range: HH:MM-HH:MM
    time_range: $ => seq(
      $.time,
      '-',
      $.time,
    ),

    time: $ => /\d{1,2}(:\d{2}(:\d{2})?)?/,

    time_unit: $ => choice(
      'h', 'hr', 'hrs', 'hour', 'hours',
      'm', 'min', 'mins', 'minute', 'minutes',
      's', 'sec', 'secs', 'second', 'seconds',
    ),

    number: $ => /-?\d+(\.\d+)?/,

    // =========================================================================
    // DESCRIPTION & COMMENTS
    // =========================================================================

    description: $ => /[^;#\n]+/,

    comment: $ => seq(
      choice(';', '#'),
      optional(/[^\n]*/),
    ),

    // =========================================================================
    // PRIMITIVES
    // =========================================================================

    _newline: $ => /\r?\n/,
  },
});
