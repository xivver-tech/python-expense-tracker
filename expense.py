#!/usr/bin/env python3
"""
Personal Expense Tracker
- Add expenses with categories
- List / filter by month or category
- Show monthly summary
- Export to CSV
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict

DATA_FILE = Path(__file__).parent / "expenses.json"

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_expense(amount, category, description=""):
    data = load_data()
    entry = {
        "id": len(data) + 1,
        "amount": float(amount),
        "category": category.lower().strip(),
        "description": description.strip(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat()
    }
    data.append(entry)
    save_data(data)
    print(f"✓ Added: ${entry['amount']:.2f} in '{entry['category']}'")

def list_expenses(month=None, category=None):
    data = load_data()
    if not data:
        print("No expenses yet.")
        return

    filtered = data
    if month:
        filtered = [e for e in filtered if e["date"].startswith(month)]
    if category:
        filtered = [e for e in filtered if e["category"] == category.lower()]

    if not filtered:
        print("No matching expenses.")
        return

    print(f"{'ID':<5} {'Date':<12} {'Amount':>10}  {'Category':<15} Description")
    print("-" * 65)
    total = 0
    for e in filtered:
        print(f"{e['id']:<5} {e['date']:<12} ${e['amount']:>8.2f}  {e['category']:<15} {e['description']}")
        total += e["amount"]
    print("-" * 65)
    print(f"{'TOTAL':<5} {'':<12} ${total:>8.2f}")

def summary(month=None):
    data = load_data()
    if month:
        data = [e for e in data if e["date"].startswith(month)]

    if not data:
        print("No data for summary.")
        return

    by_cat = defaultdict(float)
    for e in data:
        by_cat[e["category"]] += e["amount"]

    print("\n=== Expense Summary ===")
    if month:
        print(f"Month: {month}")
    print()
    total = 0
    for cat, amount in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"  {cat:<20} ${amount:>8.2f}")
        total += amount
    print("-" * 35)
    print(f"  {'TOTAL':<20} ${total:>8.2f}\n")

def export_csv(filename="expenses_export.csv"):
    data = load_data()
    if not data:
        print("Nothing to export.")
        return

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "amount", "category", "description"])
        writer.writeheader()
        for e in data:
            writer.writerow({
                "id": e["id"],
                "date": e["date"],
                "amount": e["amount"],
                "category": e["category"],
                "description": e["description"]
            })
    print(f"✓ Exported {len(data)} expenses to {filename}")

def delete_expense(expense_id):
    data = load_data()
    new_data = [e for e in data if e["id"] != expense_id]
    if len(new_data) == len(data):
        print("Expense ID not found.")
        return
    save_data(new_data)
    print(f"✓ Deleted expense #{expense_id}")

def help_text():
    print("""
Personal Expense Tracker
========================
Commands:
  add <amount> <category> [description]   Add a new expense
  list [--month YYYY-MM] [--cat name]     List expenses
  summary [--month YYYY-MM]               Category breakdown
  export [filename.csv]                   Export to CSV
  delete <id>                             Delete an expense
  help                                    Show this help
  quit                                    Exit

Examples:
  add 12.50 food Lunch with friends
  add 45 transport Uber to airport
  list --month 2026-09
  summary
  export my_expenses.csv
""")

def main():
    print("Personal Expense Tracker  |  type 'help' for commands\n")
    while True:
        try:
            raw = input("> ").strip()
            if not raw:
                continue

            parts = raw.split()
            cmd = parts[0].lower()

            if cmd in ("quit", "exit", "q"):
                print("Bye!")
                break

            elif cmd == "help":
                help_text()

            elif cmd == "add":
                if len(parts) < 3:
                    print("Usage: add <amount> <category> [description]")
                    continue
                try:
                    amount = float(parts[1])
                    category = parts[2]
                    description = " ".join(parts[3:]) if len(parts) > 3 else ""
                    add_expense(amount, category, description)
                except ValueError:
                    print("Amount must be a number.")

            elif cmd == "list":
                month = None
                category = None
                i = 1
                while i < len(parts):
                    if parts[i] == "--month" and i + 1 < len(parts):
                        month = parts[i + 1]
                        i += 2
                    elif parts[i] == "--cat" and i + 1 < len(parts):
                        category = parts[i + 1]
                        i += 2
                    else:
                        i += 1
                list_expenses(month, category)

            elif cmd == "summary":
                month = None
                if "--month" in parts:
                    idx = parts.index("--month")
                    if idx + 1 < len(parts):
                        month = parts[idx + 1]
                summary(month)

            elif cmd == "export":
                filename = parts[1] if len(parts) > 1 else "expenses_export.csv"
                export_csv(filename)

            elif cmd == "delete":
                if len(parts) < 2:
                    print("Usage: delete <id>")
                    continue
                try:
                    delete_expense(int(parts[1]))
                except ValueError:
                    print("ID must be a number.")

            else:
                print("Unknown command. Type 'help'.")

        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

if __name__ == "__main__":
    main()
