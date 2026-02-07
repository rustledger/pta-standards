/*
 * Decimal Type Formal Model
 *
 * Specifies the decimal number representation used in PTA systems.
 * Decimals have fixed precision and support exact arithmetic.
 */

module core/types/decimal

open util/integer

/*
 * A decimal number represented as an integer mantissa and exponent.
 * value = mantissa * 10^(-exponent)
 *
 * Examples:
 *   123.45 = mantissa: 12345, exponent: 2
 *   -0.001 = mantissa: -1, exponent: 3
 *   42     = mantissa: 42, exponent: 0
 */
sig Decimal {
  mantissa: Int,
  exponent: Int
}

-- Exponent must be non-negative (we represent precision as positive)
pred ValidDecimal[d: Decimal] {
  d.exponent >= 0
}

-- Scale factor for given exponent (10^exp)
-- Simplified for small exponents due to Alloy integer limits
fun scaleFactor[exp: Int]: Int {
  exp = 0 implies 1
  else exp = 1 implies 10
  else exp = 2 implies 100
  else exp = 3 implies 1000
  else exp = 4 implies 10000
  else exp = 5 implies 100000
  else 1  -- Fallback
}

-- Convert decimal to a comparable integer representation
-- (For comparison at same exponent)
fun normalizedMantissa[d: Decimal, targetExp: Int]: Int {
  targetExp >= d.exponent implies
    mul[d.mantissa, scaleFactor[sub[targetExp, d.exponent]]]
  else
    div[d.mantissa, scaleFactor[sub[d.exponent, targetExp]]]
}

-- Decimal comparison (equal)
pred DecimalEqual[a, b: Decimal] {
  let maxExp = (a.exponent >= b.exponent implies a.exponent else b.exponent) |
    normalizedMantissa[a, maxExp] = normalizedMantissa[b, maxExp]
}

-- Decimal comparison (less than)
pred DecimalLessThan[a, b: Decimal] {
  let maxExp = (a.exponent >= b.exponent implies a.exponent else b.exponent) |
    normalizedMantissa[a, maxExp] < normalizedMantissa[b, maxExp]
}

-- Addition: align to common exponent and add mantissas
fun decimalAdd[a, b: Decimal]: Decimal {
  let maxExp = (a.exponent >= b.exponent implies a.exponent else b.exponent) |
  { d: Decimal |
    d.exponent = maxExp and
    d.mantissa = add[normalizedMantissa[a, maxExp], normalizedMantissa[b, maxExp]]
  }
}

-- Subtraction
fun decimalSub[a, b: Decimal]: Decimal {
  let maxExp = (a.exponent >= b.exponent implies a.exponent else b.exponent) |
  { d: Decimal |
    d.exponent = maxExp and
    d.mantissa = sub[normalizedMantissa[a, maxExp], normalizedMantissa[b, maxExp]]
  }
}

-- Multiplication
-- (m1 * 10^-e1) * (m2 * 10^-e2) = (m1 * m2) * 10^-(e1+e2)
fun decimalMul[a, b: Decimal]: Decimal {
  { d: Decimal |
    d.mantissa = mul[a.mantissa, b.mantissa] and
    d.exponent = add[a.exponent, b.exponent]
  }
}

-- Negation
fun decimalNeg[a: Decimal]: Decimal {
  { d: Decimal |
    d.mantissa = negate[a.mantissa] and
    d.exponent = a.exponent
  }
}

-- Absolute value
fun decimalAbs[a: Decimal]: Decimal {
  { d: Decimal |
    d.mantissa = (a.mantissa >= 0 implies a.mantissa else negate[a.mantissa]) and
    d.exponent = a.exponent
  }
}

-- Zero decimal
pred IsZero[d: Decimal] {
  d.mantissa = 0
}

-- Positive decimal
pred IsPositive[d: Decimal] {
  d.mantissa > 0
}

-- Negative decimal
pred IsNegative[d: Decimal] {
  d.mantissa < 0
}

-- Rounding to fewer decimal places
fun roundToExponent[d: Decimal, targetExp: Int]: Decimal {
  targetExp <= d.exponent implies d
  else {
    result: Decimal |
      result.exponent = targetExp and
      -- Simple truncation (could be extended for proper rounding)
      result.mantissa = div[d.mantissa, scaleFactor[sub[d.exponent, targetExp]]]
  }
}

-- Common precision in PTA: typically 2-4 decimal places for currency
pred StandardPrecision[d: Decimal] {
  d.exponent <= 4
}

-- Assertions
assert AdditionCommutative {
  all a, b: Decimal |
    ValidDecimal[a] and ValidDecimal[b] implies
    let sum1 = decimalAdd[a, b], sum2 = decimalAdd[b, a] |
    one sum1 and one sum2 implies DecimalEqual[sum1, sum2]
}

assert ZeroIdentity {
  all a: Decimal, zero: Decimal |
    ValidDecimal[a] and IsZero[zero] implies
    let result = decimalAdd[a, zero] |
    one result implies DecimalEqual[result, a]
}

assert NegationInverse {
  all a: Decimal |
    ValidDecimal[a] implies
    let negA = decimalNeg[a] |
    one negA implies
    let result = decimalAdd[a, negA] |
    one result implies IsZero[result]
}

check AdditionCommutative for 3
check ZeroIdentity for 3
check NegationInverse for 3

-- Example: simple decimal arithmetic
pred DecimalArithmeticExample {
  some disj a, b, sum: Decimal |
    -- a = 10.50 (mantissa: 1050, exponent: 2)
    a.mantissa = 1050 and a.exponent = 2 and
    -- b = 3.75 (mantissa: 375, exponent: 2)
    b.mantissa = 375 and b.exponent = 2 and
    -- sum = 14.25 (mantissa: 1425, exponent: 2)
    sum = decimalAdd[a, b] and
    sum.mantissa = 1425 and sum.exponent = 2
}

run DecimalArithmeticExample for 4
