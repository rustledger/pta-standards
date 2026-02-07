# Incremental Parsing and Validation

This guide covers implementing incremental updates for editor integration.

## Why Incremental?

Full re-parsing is too slow for interactive use:

| File Size | Full Parse | Target Response |
|-----------|------------|-----------------|
| 1K lines | 50ms | Acceptable |
| 10K lines | 500ms | Noticeable lag |
| 100K lines | 5 seconds | Unacceptable |

For responsive editing, updates must complete in < 100ms.

## Incremental Strategies

### Strategy 1: Line-Based Reparsing

Parse only changed lines plus context:

```
on_change(file, change_range):
    // Find directive boundaries
    start_directive = find_directive_start(change_range.start)
    end_directive = find_directive_end(change_range.end)

    // Reparse affected section
    section = file.text[start_directive:end_directive]
    new_ast = parse(section)

    // Replace in full AST
    ast.replace_range(start_directive, end_directive, new_ast)

    // Revalidate affected accounts
    affected_accounts = new_ast.accounts_mentioned()
    revalidate_accounts(affected_accounts)
```

### Strategy 2: Tree Diffing

Compare old and new AST, update incrementally:

```
on_change(file, change):
    // Parse new version
    new_text = apply_change(file.text, change)
    new_ast = parse(new_text)

    // Diff against old AST
    diff = diff_ast(old_ast, new_ast)

    // Apply changes to derived data
    for change in diff:
        match change:
            Add(directive) => add_to_indices(directive)
            Remove(directive) => remove_from_indices(directive)
            Modify(old, new) => update_indices(old, new)
```

### Strategy 3: Tree-sitter Integration

Use tree-sitter for incremental parsing:

```
// Tree-sitter handles incremental parsing natively
parser = TreeSitter.Parser()
parser.set_language(beancount_language())

tree = parser.parse(source)

// On edit, update incrementally
tree.edit(Edit {
    start_byte: change.start,
    old_end_byte: change.old_end,
    new_end_byte: change.new_end,
    ...
})

new_tree = parser.parse(new_source, old_tree: tree)
// tree-sitter reuses unchanged nodes
```

## Directive Dependencies

Track what depends on what:

```
DependencyGraph = {
    directive_depends_on: Map<DirectiveId, Set<DirectiveId>>,
    directive_affects: Map<DirectiveId, Set<DirectiveId>>,
}

// When directive changes, invalidate dependents
on_directive_change(directive):
    affected = dependency_graph.directive_affects.get(directive.id)
    for dep in affected:
        invalidate(dep)
```

### Dependency Types

| Source | Depends On | Reason |
|--------|------------|--------|
| Transaction | Open directive | Account must be open |
| Balance | All transactions | Computes running total |
| Pad | Balance assertion | Fills gap to target |
| Include | Included file | Content comes from file |
| Plugin output | Plugin input | Plugin transforms |

## Caching Strategy

### Cache Layers

```
┌─────────────────────────────────────┐
│          Query Results              │ (invalidate on any change)
├─────────────────────────────────────┤
│        Computed Balances            │ (invalidate on posting change)
├─────────────────────────────────────┤
│        Validated Ledger             │ (invalidate on directive change)
├─────────────────────────────────────┤
│           Parsed AST                │ (invalidate on text change)
├─────────────────────────────────────┤
│          Source Text                │ (from file/editor)
└─────────────────────────────────────┘
```

### Cache Keys

```
CacheKey = {
    file_path: Path,
    file_hash: Hash,
    region: Option<Range>,
}

Cache<K, V> = {
    entries: Map<K, CacheEntry<V>>,
}

CacheEntry<V> = {
    value: V,
    dependencies: Set<CacheKey>,
    last_valid: Timestamp,
}
```

### Invalidation

```
invalidate(key):
    entry = cache.remove(key)

    // Cascade to dependents
    for dependent in find_dependents(key):
        invalidate(dependent)

find_dependents(key):
    return cache.entries
        .filter(e => e.dependencies.contains(key))
        .map(e => e.key)
```

## Account Index

Maintain fast account lookups:

```
AccountIndex = {
    by_name: Map<Account, AccountInfo>,
    by_type: Map<AccountType, Set<Account>>,
    by_currency: Map<Currency, Set<Account>>,
}

AccountInfo = {
    open_directive: Option<DirectiveId>,
    close_directive: Option<DirectiveId>,
    transactions: Vec<DirectiveId>,
    balance_assertions: Vec<DirectiveId>,
}

// Update on change
on_directive_add(directive):
    if directive is Open:
        index.by_name.insert(directive.account, ...)
    if directive is Transaction:
        for posting in directive.postings:
            index.by_name[posting.account].transactions.push(directive.id)

on_directive_remove(directive):
    // Reverse of add
```

## Date Index

Enable fast date-range queries:

```
DateIndex = {
    by_date: BTreeMap<Date, Vec<DirectiveId>>,
}

// Find directives affecting a balance at date
directives_up_to(date):
    return by_date.range(..=date).flat_map(|(_, ids)| ids)

// Find directives in range
directives_between(start, end):
    return by_date.range(start..=end).flat_map(|(_, ids)| ids)
```

## Incremental Balance Computation

### Approach 1: Dirty Flags

Mark balances as dirty, recompute lazily:

```
BalanceCache = {
    balances: Map<(Account, Date), Balance>,
    dirty_from: Map<Account, Date>,  // Earliest dirty date
}

mark_dirty(account, date):
    existing = dirty_from.get(account)
    if existing is None or date < existing:
        dirty_from[account] = date

get_balance(account, date):
    dirty = dirty_from.get(account)
    if dirty and dirty <= date:
        recompute_balances(account, dirty, date)
    return balances[(account, date)]
```

### Approach 2: Checkpoint Balances

Store periodic checkpoints:

```
// Store balance every N transactions or at month boundaries
Checkpoint = {
    account: Account,
    date: Date,
    balance: Inventory,
    transaction_count: usize,
}

get_balance(account, date):
    // Find nearest checkpoint before date
    checkpoint = find_checkpoint_before(account, date)

    // Compute from checkpoint forward
    balance = checkpoint.balance.clone()
    for txn in transactions_between(checkpoint.date, date):
        apply_postings(balance, txn, account)

    return balance
```

## Error Caching

Cache validation errors per directive:

```
ErrorCache = {
    by_directive: Map<DirectiveId, Vec<Error>>,
    by_file: Map<Path, Vec<Error>>,
}

on_directive_change(old, new):
    // Remove old errors
    error_cache.by_directive.remove(old.id)

    // Validate new directive
    errors = validate_directive(new)
    error_cache.by_directive.insert(new.id, errors)

    // Update file errors
    update_file_errors(new.file)
```

## LSP Integration

### Document Sync

Handle document changes efficiently:

```
on_did_change(params):
    uri = params.document.uri

    for change in params.content_changes:
        if change.range:
            // Incremental change
            apply_incremental_change(uri, change)
        else:
            // Full document replacement
            reparse_full(uri, change.text)

    // Compute diagnostics
    diagnostics = compute_diagnostics(uri)
    publish_diagnostics(uri, diagnostics)
```

### Debouncing

Avoid excessive recomputation during fast typing:

```
pending_changes: Map<Uri, Timer>

on_did_change(params):
    uri = params.document.uri

    // Cancel pending recomputation
    if timer = pending_changes.get(uri):
        timer.cancel()

    // Apply text change immediately (for highlighting)
    apply_text_change(uri, params.content_changes)

    // Debounce validation
    timer = set_timeout(100ms, || {
        revalidate(uri)
        publish_diagnostics(uri)
    })
    pending_changes.insert(uri, timer)
```

### Cancellation

Support cancellation for long operations:

```
validate_with_cancellation(ledger, token):
    for directive in ledger.directives:
        if token.is_cancelled():
            return Cancelled

        validate_directive(directive)

    return Complete
```

## Performance Measurement

Track incremental performance:

```
IncrementalMetrics = {
    reparse_times: Vec<Duration>,
    revalidate_times: Vec<Duration>,
    cache_hit_rate: f64,
    directives_revalidated: usize,
}

measure_change(change):
    start = now()

    // Track what was invalidated
    invalidated_before = count_invalid()

    apply_change(change)

    invalidated_after = count_invalid()
    metrics.directives_revalidated += invalidated_after - invalidated_before
    metrics.reparse_times.push(now() - start)
```

## Testing Incremental Updates

### Correctness Tests

Verify incremental matches full recomputation:

```
test_incremental_correctness():
    ledger = load("test.beancount")

    // Full computation
    full_result = validate(ledger)

    // Incremental: edit and update
    edit = random_edit(ledger)
    apply_edit(ledger, edit)
    incremental_result = validate_incremental(ledger, edit)

    // Full recomputation after edit
    full_after_edit = validate(ledger)

    assert incremental_result == full_after_edit
```

### Performance Tests

Ensure incremental is actually faster:

```
test_incremental_performance():
    large_ledger = load("100k-transactions.beancount")

    // Baseline: full reparse
    full_time = time(|| parse(large_ledger))

    // Incremental: single line change
    change = Change { line: 50000, old: "100", new: "200" }
    incremental_time = time(|| update_incremental(large_ledger, change))

    // Incremental should be at least 10x faster
    assert incremental_time < full_time / 10
```
