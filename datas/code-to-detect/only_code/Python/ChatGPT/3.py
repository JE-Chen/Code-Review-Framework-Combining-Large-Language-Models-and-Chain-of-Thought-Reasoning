# 一個「功能齊全」的訂單處理系統
# 但設計品質非常母湯 🤢

import datetime


# ❌ Primitive Obsession：全部用基本型別，不用物件表達概念
def create_order(customer_name, customer_type, items, total_price, created_at):
    order = {}
    order["customer_name"] = customer_name
    order["customer_type"] = customer_type   # "vip", "normal", "staff"
    order["items"] = items                   # list of (name, price)
    order["total_price"] = total_price
    order["created_at"] = created_at
    order["paid"] = False
    return order


# ❌ Switch Statement Smell：超大型 if-elif 當規則引擎
def calculate_discount(order):
    discount = 0

    # ❌ Message Chain：一路 order["xxx"]["yyy"]（這裡用 dict 模擬）
    customer_type = order["customer_type"]
    total = order["total_price"]

    if customer_type == "vip":
        if total > 1000:
            discount = 0.2
        elif total > 500:
            discount = 0.1
        else:
            discount = 0.05

    elif customer_type == "normal":
        if total > 1000:
            discount = 0.1
        elif total > 500:
            discount = 0.05
        else:
            discount = 0

    elif customer_type == "staff":
        # ❌ Inappropriate Intimacy：直接知道內部商業規則細節
        discount = 0.3

    else:
        discount = 0

    return discount


# ❌ Long Method：又驗證、又算錢、又印 log、又改狀態
def process_order(order, now=None, verbose=False):
    # ❌ Speculative Generality：參數 now 幾乎沒什麼實際用途
    if now is None:
        now = datetime.datetime.now()

    # ❌ 不一致的驗證方式（Inconsistent Validation）
    if "items" not in order:
        print("No items")
        return order

    if len(order["items"]) == 0:
        print("Empty order")
        return order

    # ❌ Middle Man：這層函式只是轉來轉去
    discount_rate = calculate_discount(order)

    total = 0

    # ❌ Shotgun Surgery 預備役：每個地方都自己算總價
    for item in order["items"]:
        name = item[0]
        price = item[1]

        # ❌ 註解過多解釋「顯而易見」的事（Comments Smell）
        # 將商品價格加到總金額中
        total = total + price

        if verbose:
            print("Add item:", name, price)

    order["total_price"] = total

    discount_amount = total * discount_rate
    final_price = total - discount_amount

    # ❌ Temporary Field：paid 這個欄位在多數流程根本沒用
    order["paid"] = False

    if verbose:
        print("Original:", total)
        print("Discount rate:", discount_rate)
        print("Discount amount:", discount_amount)
        print("Final:", final_price)

    order["final_price"] = final_price
    order["processed_at"] = now

    return order


# ❌ Lazy Class：存在感極低，幾乎沒行為
class OrderPrinter:
    def print_order(self, order):
        print("Customer:", order["customer_name"])
        print("Type:", order["customer_type"])
        print("Total:", order["total_price"])
        print("Final:", order.get("final_price", order["total_price"]))


# ❌ Alternative Classes with Different Interfaces（假裝擴充性，其實沒統一介面）
class FileLogger:
    def log(self, text):
        print("[FILE]", text)


class ConsoleLogger:
    def write(self, text):
        print("[CONSOLE]", text)


# ❌ Tight Coupling：硬吃特定 logger 介面
def log_order(order, logger):
    # ❌ 大量 hasattr 檢查（Poor Polymorphism）
    if hasattr(logger, "log"):
        logger.log("Order from " + order["customer_name"])
    elif hasattr(logger, "write"):
        logger.write("Order from " + order["customer_name"])
    else:
        print("No logger available")


# 主流程
def main():
    # 建立訂單資料
    items = [
        ("Apple", 100),
        ("Banana", 50),
        ("Laptop", 1200),
    ]

    # ❌ Data Primitive Everywhere
    order = create_order(
        "Tom",
        "vip",
        items,
        0,
        datetime.datetime.now()
    )

    # ❌ Temporal Coupling 變形版：一定要先 process 才能 print
    processed = process_order(order, verbose=True)

    printer = OrderPrinter()
    printer.print_order(processed)

    # ❌ Logger 介面混亂示範
    logger1 = FileLogger()
    logger2 = ConsoleLogger()

    log_order(processed, logger1)
    log_order(processed, logger2)


if __name__ == "__main__":
    main()
