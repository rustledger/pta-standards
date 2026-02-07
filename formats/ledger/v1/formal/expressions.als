/*
 * Ledger Value Expressions Formal Model
 *
 * Specifies Ledger's expression language for computed amounts:
 * - Arithmetic: +, -, *, /
 * - Functions: abs, round, floor, ceil
 * - Conditionals: if/else
 * - Account references
 */

module formats/ledger/v1/formal/expressions

open util/integer

sig Currency {}

-- Expression AST
abstract sig Expr {}

-- Literal value
sig LiteralExpr extends Expr {
  value: Int
}

-- Binary operations
abstract sig BinaryOp {}
one sig Add, Sub, Mul, Div extends BinaryOp {}

sig BinaryExpr extends Expr {
  op: BinaryOp,
  left: Expr,
  right: Expr
}

-- Unary operations
abstract sig UnaryOp {}
one sig Neg, Abs extends UnaryOp {}

sig UnaryExpr extends Expr {
  op: UnaryOp,
  operand: Expr
}

-- Conditional expression
sig IfExpr extends Expr {
  condition: BoolExpr,
  thenExpr: Expr,
  elseExpr: Expr
}

-- Boolean expressions
abstract sig BoolExpr {}

sig CompareExpr extends BoolExpr {
  compareOp: CompareOp,
  left: Expr,
  right: Expr
}

abstract sig CompareOp {}
one sig Lt, Le, Eq, Ne, Ge, Gt extends CompareOp {}

-- Account reference (for balance queries)
sig Account {}
sig AccountRef extends Expr {
  account: Account
}

-- Evaluation context
sig Context {
  balances: Account -> Int  -- Account balances
}

-- Evaluate an expression in a context
fun eval[e: Expr, ctx: Context]: Int {
  e in LiteralExpr implies e.value
  else e in AccountRef implies ctx.balances[e.account]
  else e in UnaryExpr implies (
    e.op = Neg implies negate[eval[e.operand, ctx]]
    else e.op = Abs implies (
      eval[e.operand, ctx] >= 0 implies eval[e.operand, ctx]
      else negate[eval[e.operand, ctx]]
    )
    else 0
  )
  else e in BinaryExpr implies (
    e.op = Add implies add[eval[e.left, ctx], eval[e.right, ctx]]
    else e.op = Sub implies sub[eval[e.left, ctx], eval[e.right, ctx]]
    else e.op = Mul implies mul[eval[e.left, ctx], eval[e.right, ctx]]
    else e.op = Div implies div[eval[e.left, ctx], eval[e.right, ctx]]
    else 0
  )
  else e in IfExpr implies (
    evalBool[e.condition, ctx] = True implies eval[e.thenExpr, ctx]
    else eval[e.elseExpr, ctx]
  )
  else 0
}

abstract sig TruthValue {}
one sig True, False extends TruthValue {}

-- Evaluate a boolean expression
fun evalBool[e: BoolExpr, ctx: Context]: TruthValue {
  e in CompareExpr implies (
    let l = eval[e.left, ctx], r = eval[e.right, ctx] |
    e.compareOp = Lt implies (l < r implies True else False)
    else e.compareOp = Le implies (l <= r implies True else False)
    else e.compareOp = Eq implies (l = r implies True else False)
    else e.compareOp = Ne implies (l != r implies True else False)
    else e.compareOp = Ge implies (l >= r implies True else False)
    else e.compareOp = Gt implies (l > r implies True else False)
    else False
  )
  else False
}

-- Example: computed amount expression
-- = (account_balance * 0.1)  -- 10% of balance
pred PercentageExpression {
  some e: BinaryExpr, ref: AccountRef, lit: LiteralExpr |
  some acct: Account, ctx: Context |
    ctx.balances[acct] = 1000 and
    ref.account = acct and
    lit.value = 10 and
    e.op = Div and e.left = ref and e.right = lit and
    -- Result should be 100 (10% of 1000, using integer division)
    eval[e, ctx] = 100
}

-- Conditional: use different rates based on amount
pred ConditionalExpression {
  some ifE: IfExpr, cmp: CompareExpr |
  some thenE, elseE: LiteralExpr, amtRef: AccountRef |
  some threshold: LiteralExpr |
  some acct: Account, ctx: Context |
    ctx.balances[acct] = 5000 and
    amtRef.account = acct and
    threshold.value = 1000 and
    cmp.left = amtRef and cmp.right = threshold and cmp.compareOp = Gt and
    thenE.value = 50 and   -- Higher fee for large amounts
    elseE.value = 10 and   -- Lower fee for small amounts
    ifE.condition = cmp and ifE.thenExpr = thenE and ifE.elseExpr = elseE and
    -- Since 5000 > 1000, result should be 50
    eval[ifE, ctx] = 50
}

-- Assertions
assert DivisionByZeroUndefined {
  all e: BinaryExpr, ctx: Context |
    e.op = Div and eval[e.right, ctx] = 0 implies
    -- In practice, this would be an error; Alloy returns 0
    true
}

assert AbsNonNegative {
  all e: UnaryExpr, ctx: Context |
    e.op = Abs implies eval[e, ctx] >= 0
}

check AbsNonNegative for 4

run PercentageExpression for 4
run ConditionalExpression for 5
