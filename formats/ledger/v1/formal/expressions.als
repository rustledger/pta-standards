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

abstract sig TruthValue {}
one sig True, False extends TruthValue {}

-- Evaluation context. Alloy functions cannot recurse, so evaluation is
-- defined relationally: `val` and `truth` hold the value of every expression
-- in this context, pinned down case by case by fact Evaluation below, and
-- `defined` is the set of expressions that evaluate without error.
sig Context {
  balances: Account -> one Int,  -- Account balances
  val: Expr -> one Int,
  truth: BoolExpr -> one TruthValue,
  defined: set Expr
}

-- Direct subexpressions (BoolExpr conditions included via their operands)
fun children: Expr -> Expr {
  BinaryExpr <: left + BinaryExpr <: right + operand + thenExpr + elseExpr
    + condition.(CompareExpr <: left + CompareExpr <: right)
}

-- Arithmetic subexpressions: always evaluated (unlike if/else branches)
fun arithChildren: Expr -> Expr {
  BinaryExpr <: left + BinaryExpr <: right + operand
}

-- Expressions are finite trees: no expression contains itself
fact Acyclic {
  no e: Expr | e in e.^children
}

fact Evaluation {
  all ctx: Context {
    all e: LiteralExpr | ctx.val[e] = e.value
    all e: AccountRef | ctx.val[e] = ctx.balances[e.account]
    all e: UnaryExpr | let x = ctx.val[e.operand] |
      ctx.val[e] = (e.op = Neg implies negate[x] else (x >= 0 implies x else negate[x]))
    all e: BinaryExpr | let l = ctx.val[e.left], r = ctx.val[e.right] |
      ctx.val[e] = (e.op = Add implies add[l, r]
        else e.op = Sub implies sub[l, r]
        else e.op = Mul implies mul[l, r]
        -- div by zero is an error (see `defined`); its value is irrelevant, and
        -- is pinned to 0 so the analyzer never evaluates an x/0 term, which
        -- no-overflow mode would treat as an overflow and silently discard
        else r = 0 implies 0 else div[l, r])
    all e: IfExpr |
      ctx.val[e] = (ctx.truth[e.condition] = True implies ctx.val[e.thenExpr] else ctx.val[e.elseExpr])
    all b: CompareExpr | let l = ctx.val[b.left], r = ctx.val[b.right] |
      ctx.truth[b] = (((b.compareOp = Lt and l < r) or (b.compareOp = Le and l <= r)
        or (b.compareOp = Eq and l = r) or (b.compareOp = Ne and l != r)
        or (b.compareOp = Ge and l >= r) or (b.compareOp = Gt and l > r))
        implies True else False)

    -- Definedness: division by zero is an error (spec: expressions/spec.md
    -- "Division by Zero", errors.md X-001); errors propagate through
    -- arithmetic, and through an if/else only from the condition and the
    -- branch actually taken.
    all e: LiteralExpr + AccountRef | e in ctx.defined
    all e: UnaryExpr | e in ctx.defined iff e.operand in ctx.defined
    all e: BinaryExpr | e in ctx.defined iff
      (e.left + e.right in ctx.defined and not (e.op = Div and ctx.val[e.right] = 0))
    all e: IfExpr | e in ctx.defined iff
      (e.condition.(CompareExpr <: left + CompareExpr <: right) in ctx.defined and
       (ctx.truth[e.condition] = True implies e.thenExpr else e.elseExpr) in ctx.defined)
  }
}

-- Evaluate an expression in a context
fun eval[e: Expr, ctx: Context]: Int {
  ctx.val[e]
}

-- Evaluate a boolean expression
fun evalBool[e: BoolExpr, ctx: Context]: TruthValue {
  ctx.truth[e]
}

-- Example: computed amount expression
-- = (account_balance * 0.1)  -- 10% of balance
-- (balance scaled from 1000 to 30 to fit Alloy's small integers)
pred PercentageExpression {
  some e: BinaryExpr, ref: AccountRef, lit: LiteralExpr |
  some acct: Account, ctx: Context |
    ctx.balances[acct] = 30 and
    ref.account = acct and
    lit.value = 10 and
    e.op = Div and e.left = ref and e.right = lit and
    -- Result should be 3 (10% of 30, using integer division)
    eval[e, ctx] = 3 and e in ctx.defined
}

-- Conditional: use different rates based on amount
-- (scaled: balance 5000 -> 20, threshold 1000 -> 10, fees 50/10 -> 5/1)
pred ConditionalExpression {
  some ifE: IfExpr, cmp: CompareExpr |
  some thenE, elseE: LiteralExpr, amtRef: AccountRef |
  some threshold: LiteralExpr |
  some acct: Account, ctx: Context |
    ctx.balances[acct] = 20 and
    amtRef.account = acct and
    threshold.value = 10 and
    cmp.left = amtRef and cmp.right = threshold and cmp.compareOp = Gt and
    thenE.value = 5 and   -- Higher fee for large amounts
    elseE.value = 1 and   -- Lower fee for small amounts
    ifE.condition = cmp and ifE.thenExpr = thenE and ifE.elseExpr = elseE and
    -- Since 20 > 10, result should be 5
    eval[ifE, ctx] = 5
}

-- Assertions

-- Division by zero is an error, and the error is not masked by any
-- enclosing arithmetic: an expression with a zero-divisor division among its
-- arithmetic subexpressions has no value.
assert DivisionByZeroUndefined {
  all e: Expr, ctx: Context, d: e.*arithChildren & BinaryExpr |
    (d.op = Div and eval[d.right, ctx] = 0) implies e not in ctx.defined
}

-- (abs of the most negative machine integer would overflow; Ledger amounts
-- are unbounded, and the analyzer runs in no-overflow mode, which excludes it)
assert AbsNonNegative {
  all e: UnaryExpr, ctx: Context |
    e.op = Abs implies eval[e, ctx] >= 0
}

check DivisionByZeroUndefined for 4
check AbsNonNegative for 4

run PercentageExpression for 4 but 6 Int
run ConditionalExpression for 5 but 6 Int
