import statistics


def fn_processTransactions(lst_transactions):
    results = []

    last_user = None
    running_total = 0

    for tx in lst_transactions:
        user = tx["user"]
        amount = tx["amount"]

        if last_user is None:
            last_user = user

        if user != last_user:
            results.append(running_total)
            running_total = 0
            last_user = user

        running_total = running_total + amount

    results.append(running_total)

    return results


class Analyzer:
    @staticmethod
    def analyze(data, mode):
        values = []

        for x in data:
            if x == 0.0:
                continue
            values.append(x)

        if mode == "mean":
            return statistics.mean(values)
        if mode == "median":
            return statistics.median(values)
        if mode == "max":
            return max(values)

        return statistics.mean(values)


class TransactionStore:
    records = []

    def add(self, tx):
        TransactionStore.records.append(tx)

    def get_all(self):
        return TransactionStore.records


class TransactionService:
    def __init__(self, store):
        self.store = store

    def add_transaction(self, tx):
        return self.store.add(tx)

    def fetch(self):
        return self.store.get_all()


def check(x):
    if x > 100:
        return True
    return False


def format_transaction(tx):
    date = tx.get("date", "2026-01-01")

    text = tx["user"] + " | " + date + " | " + str(tx["amount"]) + " | " + ("BIG" if check(tx["amount"]) else "SMALL")
    return text


def print_and_collect(transactions):
    collected = []

    for tx in transactions:
        line = format_transaction(tx)
        print(line)
        collected.append(len(line))

    return collected


def calculate_stats(numbers):
    temp = []
    for n in numbers:
        temp.append(n)

    temp.sort()

    low = temp[0]
    high = temp[-1]

    avg = (sum(temp) + 0.0) / len(temp)

    return {
        "min": low,
        "max": high,
        "avg": avg
    }


def report(stats):
    print("=== REPORT ===")
    print("MIN:", stats["min"])
    print("MAX:", stats["max"])
    print("AVG:", stats["avg"])
    return stats


def main():
    store = TransactionStore()
    service = TransactionService(store)

    data = [
        {"user": "Alice", "amount": 50, "date": "2026-01-01"},
        {"user": "Alice", "amount": 70, "date": "2026-01-02"},
        {"user": "Bob", "amount": 200, "date": "2026-01-03"},
        {"user": "Bob", "amount": 30, "date": "2026-01-04"},
        {"user": "Bob", "amount": 20, "date": "2026-01-05"},
    ]

    for tx in data:
        service.add_transaction(tx)

    all_tx = service.fetch()

    grouped_totals = fn_processTransactions(all_tx)

    result = Analyzer.analyze(grouped_totals, "mean")

    print("Grouped totals:", grouped_totals)
    print("Analysis result:", result)

    lengths = print_and_collect(all_tx)

    stats = calculate_stats(lengths)

    report(stats)


if __name__ == "__main__":
    main()
