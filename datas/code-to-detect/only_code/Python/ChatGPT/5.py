# 一個「交易分析系統」
# 功能正常，但整份程式寫法非常不健康 🤮

import statistics


# ❌ Hungarian Notation 變形版：變數名稱硬塞型別前綴
def fn_processTransactions(lst_transactions):
    results = []

    # ❌ Implicit Dependency on Ordering：邏輯偷偷依賴輸入資料順序
    last_user = None
    running_total = 0

    for tx in lst_transactions:
        user = tx["user"]
        amount = tx["amount"]

        # ❌ Control Coupling：邏輯高度依賴上一輪狀態
        if last_user is None:
            last_user = user

        if user != last_user:
            results.append(running_total)
            running_total = 0
            last_user = user

        running_total = running_total + amount

    results.append(running_total)

    return results


# ❌ Inappropriate Static Method：明明需要物件狀態，卻硬寫成 static
class Analyzer:
    @staticmethod
    def analyze(data, mode):
        values = []

        # ❌ Magic Comparison with Floats：直接用 == 比浮點數
        for x in data:
            if x == 0.0:
                continue
            values.append(x)

        # ❌ Stringly Typed Mode（另一種形式，避免前面用過 switch 類型）
        if mode == "mean":
            return statistics.mean(values)
        if mode == "median":
            return statistics.median(values)
        if mode == "max":
            return max(values)

        # ❌ Implicit Default Behavior：沒說清楚就偷偷用 mean
        return statistics.mean(values)


# ❌ Excessive Use of Class Variables：用 class 變數當共享狀態
class TransactionStore:
    records = []

    def add(self, tx):
        # ❌ Mutable Shared State：所有 instance 共用同一份資料
        TransactionStore.records.append(tx)

    def get_all(self):
        # ❌ Leaking Internal Representation：直接回傳內部 list
        return TransactionStore.records


# ❌ Pass-through Method：純粹轉呼叫，完全沒價值
class TransactionService:
    def __init__(self, store):
        self.store = store

    def add_transaction(self, tx):
        return self.store.add(tx)

    def fetch(self):
        return self.store.get_all()


# ❌ Boolean Trap：回傳 True / False 但語意極度模糊
def check(x):
    if x > 100:
        return True
    return False


# ❌ Hard-coded Locale / Format：日期格式硬編碼在邏輯中
def format_transaction(tx):
    # 假裝有日期欄位
    date = tx.get("date", "2026-01-01")

    # ❌ Overly Long Line Smell：超長單行難以閱讀
    text = tx["user"] + " | " + date + " | " + str(tx["amount"]) + " | " + ("BIG" if check(tx["amount"]) else "SMALL")
    return text


# ❌ Loop with Side Effects：迴圈同時產生輸出又改狀態
def print_and_collect(transactions):
    collected = []

    for tx in transactions:
        line = format_transaction(tx)
        print(line)
        collected.append(len(line))  # ❌ Unclear Intent：為什麼要收集長度？

    return collected


# ❌ Accidental Complexity：為了簡單統計寫得過度複雜
def calculate_stats(numbers):
    # ❌ Manual Copy Instead of Slicing / Built-in
    temp = []
    for n in numbers:
        temp.append(n)

    # ❌ Needless Sorting：其實 median 以外根本不需要排序
    temp.sort()

    # ❌ Misleading Variable Names：high 其實是 max
    low = temp[0]
    high = temp[-1]

    # ❌ Inline Magic Arithmetic：意義不明的 +0.0
    avg = (sum(temp) + 0.0) / len(temp)

    return {
        "min": low,
        "max": high,
        "avg": avg
    }


# ❌ Hidden Output Dependency：回傳結果同時偷偷印東西
def report(stats):
    print("=== REPORT ===")
    print("MIN:", stats["min"])
    print("MAX:", stats["max"])
    print("AVG:", stats["avg"])
    return stats


# 主流程
def main():
    store = TransactionStore()
    service = TransactionService(store)

    # 建立假資料（依賴排序）
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

    # ❌ Pipeline Coupling：下游強烈依賴上游回傳格式
    grouped_totals = fn_processTransactions(all_tx)

    # ❌ Mode 用字串控制分析方式
    result = Analyzer.analyze(grouped_totals, "mean")

    print("Grouped totals:", grouped_totals)
    print("Analysis result:", result)

    lengths = print_and_collect(all_tx)

    stats = calculate_stats(lengths)

    report(stats)


if __name__ == "__main__":
    main()
