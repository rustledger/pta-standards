#!/usr/bin/env python3
"""Generate benchmark ledger files for performance testing.

Creates synthetic but realistic-looking ledger files with configurable
number of transactions, accounts, and commodities.
"""

from __future__ import annotations

import argparse
import random
from datetime import date, timedelta
from pathlib import Path


# Account templates
ACCOUNT_TEMPLATES = {
    "assets": [
        "Assets:Bank:Checking",
        "Assets:Bank:Savings",
        "Assets:Cash",
        "Assets:Investment:Brokerage",
        "Assets:Investment:401k",
        "Assets:Investment:IRA",
        "Assets:Receivables",
    ],
    "liabilities": [
        "Liabilities:CreditCard:Visa",
        "Liabilities:CreditCard:Amex",
        "Liabilities:Mortgage",
        "Liabilities:StudentLoan",
    ],
    "income": [
        "Income:Salary",
        "Income:Bonus",
        "Income:Interest",
        "Income:Dividends",
        "Income:Freelance",
    ],
    "expenses": [
        "Expenses:Food:Groceries",
        "Expenses:Food:Restaurants",
        "Expenses:Food:Coffee",
        "Expenses:Transport:Gas",
        "Expenses:Transport:PublicTransit",
        "Expenses:Transport:Parking",
        "Expenses:Housing:Rent",
        "Expenses:Housing:Utilities:Electric",
        "Expenses:Housing:Utilities:Gas",
        "Expenses:Housing:Utilities:Water",
        "Expenses:Housing:Utilities:Internet",
        "Expenses:Shopping:Clothing",
        "Expenses:Shopping:Electronics",
        "Expenses:Shopping:Home",
        "Expenses:Health:Insurance",
        "Expenses:Health:Medical",
        "Expenses:Health:Pharmacy",
        "Expenses:Entertainment:Movies",
        "Expenses:Entertainment:Games",
        "Expenses:Entertainment:Subscriptions",
        "Expenses:Travel:Flights",
        "Expenses:Travel:Hotels",
        "Expenses:Travel:CarRental",
        "Expenses:Education:Books",
        "Expenses:Education:Courses",
        "Expenses:Taxes:Federal",
        "Expenses:Taxes:State",
        "Expenses:Taxes:Property",
    ],
    "equity": [
        "Equity:OpeningBalances",
        "Equity:Adjustments",
    ],
}

# Payees by expense category
PAYEES = {
    "Groceries": ["Whole Foods", "Trader Joe's", "Safeway", "Costco", "Walmart"],
    "Restaurants": ["Chipotle", "Olive Garden", "Local Cafe", "Pizza Hut", "Thai Place"],
    "Coffee": ["Starbucks", "Blue Bottle", "Philz Coffee", "Local Roaster"],
    "Gas": ["Shell", "Chevron", "Costco Gas", "BP", "Exxon"],
    "Clothing": ["Target", "Nordstrom", "Amazon", "Old Navy", "Gap"],
    "Electronics": ["Best Buy", "Amazon", "Apple Store", "Newegg"],
    "default": ["Generic Vendor", "Local Store", "Online Purchase"],
}

COMMODITIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF"]
STOCKS = ["AAPL", "GOOG", "MSFT", "AMZN", "TSLA", "META", "NVDA", "VTI", "VOO", "BND"]


def generate_accounts(count: int) -> list[str]:
    """Generate a list of account names."""
    accounts = []

    # Always include base accounts
    for category in ACCOUNT_TEMPLATES.values():
        accounts.extend(category)

    # Add more if needed
    while len(accounts) < count:
        category = random.choice(list(ACCOUNT_TEMPLATES.keys()))
        base = random.choice(ACCOUNT_TEMPLATES[category])
        suffix = f":Sub{len(accounts)}"
        accounts.append(base + suffix)

    return accounts[:count]


def get_payee(account: str) -> str:
    """Get a random payee based on account type."""
    for key, payees in PAYEES.items():
        if key in account:
            return random.choice(payees)
    return random.choice(PAYEES["default"])


def generate_transaction(
    txn_date: date,
    accounts: list[str],
    commodities: list[str],
    complexity: str = "medium",
) -> str:
    """Generate a single transaction."""
    lines = []

    # Pick expense and funding accounts
    expense_accounts = [a for a in accounts if a.startswith("Expenses:")]
    asset_accounts = [a for a in accounts if a.startswith("Assets:")]

    if not expense_accounts or not asset_accounts:
        expense_accounts = ["Expenses:Misc"]
        asset_accounts = ["Assets:Checking"]

    expense = random.choice(expense_accounts)
    asset = random.choice(asset_accounts)

    payee = get_payee(expense)
    narration = f"Purchase at {payee}"
    commodity = random.choice(commodities[:3])  # Use main currencies

    # Generate amount
    if complexity == "low":
        amount = round(random.uniform(5, 100), 2)
    elif complexity == "high":
        amount = round(random.uniform(1, 10000), 2)
    else:
        amount = round(random.uniform(10, 500), 2)

    # Transaction header
    flag = random.choice(["*", "*", "*", "!"])  # Mostly complete
    lines.append(f'{txn_date} {flag} "{payee}" "{narration}"')

    # Add metadata sometimes
    if complexity == "high" and random.random() < 0.3:
        lines.append(f'  category: "{expense.split(":")[-1].lower()}"')

    # Postings
    lines.append(f"  {expense}  {amount:.2f} {commodity}")
    lines.append(f"  {asset}")

    return "\n".join(lines)


def generate_income_transaction(
    txn_date: date,
    accounts: list[str],
    commodities: list[str],
) -> str:
    """Generate an income transaction (e.g., salary)."""
    income_accounts = [a for a in accounts if a.startswith("Income:")]
    asset_accounts = [a for a in accounts if a.startswith("Assets:")]

    income = random.choice(income_accounts) if income_accounts else "Income:Salary"
    asset = random.choice(asset_accounts) if asset_accounts else "Assets:Checking"

    commodity = random.choice(commodities[:3])
    amount = round(random.uniform(2000, 8000), 2)

    lines = [
        f'{txn_date} * "Employer" "Paycheck"',
        f"  {asset}  {amount:.2f} {commodity}",
        f"  {income}",
    ]

    return "\n".join(lines)


def generate_beancount_file(
    transactions: int,
    accounts: int,
    commodities: int,
    start_date: date,
    complexity: str,
) -> str:
    """Generate a complete Beancount file."""
    lines = []

    # Header
    lines.append(f'; Benchmark file generated with {transactions} transactions')
    lines.append(f'; Accounts: {accounts}, Commodities: {commodities}')
    lines.append(f'; Complexity: {complexity}')
    lines.append('')
    lines.append('option "title" "Benchmark Ledger"')
    lines.append('option "operating_currency" "USD"')
    lines.append('')

    # Generate accounts and commodities
    account_list = generate_accounts(accounts)
    commodity_list = COMMODITIES[:commodities]

    # Commodity declarations
    for comm in commodity_list:
        lines.append(f'1900-01-01 commodity {comm}')
    lines.append('')

    # Account declarations (day before start date)
    open_date = start_date - timedelta(days=1)
    for account in account_list:
        lines.append(f'{open_date} open {account}')
    lines.append('')

    # Opening balance
    lines.append(f'{open_date} * "Opening Balance"')
    lines.append(f'  Assets:Bank:Checking  10000.00 USD')
    lines.append(f'  Equity:OpeningBalances')
    lines.append('')

    # Generate transactions
    current_date = start_date
    days_span = transactions // 3  # Average ~3 transactions per day

    for i in range(transactions):
        # Advance date occasionally
        if random.random() < 0.3:
            current_date += timedelta(days=random.randint(1, 3))

        # Mix of transaction types
        if i % 30 == 0:  # Monthly income
            txn = generate_income_transaction(current_date, account_list, commodity_list)
        else:
            txn = generate_transaction(current_date, account_list, commodity_list, complexity)

        lines.append(txn)
        lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate benchmark ledger files",
    )
    parser.add_argument(
        "--transactions", "-n",
        type=int,
        default=10000,
        help="Number of transactions (default: 10000)",
    )
    parser.add_argument(
        "--accounts", "-a",
        type=int,
        default=100,
        help="Number of accounts (default: 100)",
    )
    parser.add_argument(
        "--commodities", "-c",
        type=int,
        default=5,
        help="Number of commodities (default: 5)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2020-01-01",
        help="Start date (default: 2020-01-01)",
    )
    parser.add_argument(
        "--complexity",
        choices=["low", "medium", "high"],
        default="medium",
        help="Transaction complexity (default: medium)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--preset",
        choices=["small", "medium", "large", "huge"],
        help="Use preset configuration",
    )

    args = parser.parse_args()

    # Apply presets
    if args.preset:
        presets = {
            "small": {"transactions": 100, "accounts": 20, "commodities": 3},
            "medium": {"transactions": 10000, "accounts": 100, "commodities": 5},
            "large": {"transactions": 100000, "accounts": 200, "commodities": 10},
            "huge": {"transactions": 1000000, "accounts": 500, "commodities": 20},
        }
        preset = presets[args.preset]
        args.transactions = preset["transactions"]
        args.accounts = preset["accounts"]
        args.commodities = preset["commodities"]

    # Set random seed
    if args.seed:
        random.seed(args.seed)
    else:
        random.seed(42)  # Default seed for reproducibility

    # Parse start date
    start_date = date.fromisoformat(args.start_date)

    # Generate file
    content = generate_beancount_file(
        transactions=args.transactions,
        accounts=args.accounts,
        commodities=args.commodities,
        start_date=start_date,
        complexity=args.complexity,
    )

    # Output
    if args.output:
        args.output.write_text(content)
        print(f"Generated {args.output} ({len(content)} bytes, {args.transactions} transactions)")
    else:
        print(content)


if __name__ == "__main__":
    main()
