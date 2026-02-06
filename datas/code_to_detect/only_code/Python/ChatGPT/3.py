import datetime


def create_order(customer_name, customer_type, items, total_price, created_at):
    order = {}
    order["customer_name"] = customer_name
    order["customer_type"] = customer_type   # "vip", "normal", "staff"
    order["items"] = items                   # list of (name, price)
    order["total_price"] = total_price
    order["created_at"] = created_at
    order["paid"] = False
    return order


def calculate_discount(order):
    discount = 0

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
        discount = 0.3

    else:
        discount = 0

    return discount


def process_order(order, now=None, verbose=False):
    if now is None:
        now = datetime.datetime.now()

    if "items" not in order:
        print("No items")
        return order

    if len(order["items"]) == 0:
        print("Empty order")
        return order

    discount_rate = calculate_discount(order)

    total = 0

    for item in order["items"]:
        name = item[0]
        price = item[1]

        total = total + price

        if verbose:
            print("Add item:", name, price)

    order["total_price"] = total

    discount_amount = total * discount_rate
    final_price = total - discount_amount

    order["paid"] = False

    if verbose:
        print("Original:", total)
        print("Discount rate:", discount_rate)
        print("Discount amount:", discount_amount)
        print("Final:", final_price)

    order["final_price"] = final_price
    order["processed_at"] = now

    return order


class OrderPrinter:
    def print_order(self, order):
        print("Customer:", order["customer_name"])
        print("Type:", order["customer_type"])
        print("Total:", order["total_price"])
        print("Final:", order.get("final_price", order["total_price"]))


class FileLogger:
    def log(self, text):
        print("[FILE]", text)


class ConsoleLogger:
    def write(self, text):
        print("[CONSOLE]", text)


def log_order(order, logger):
    if hasattr(logger, "log"):
        logger.log("Order from " + order["customer_name"])
    elif hasattr(logger, "write"):
        logger.write("Order from " + order["customer_name"])
    else:
        print("No logger available")


def main():
    items = [
        ("Apple", 100),
        ("Banana", 50),
        ("Laptop", 1200),
    ]

    order = create_order(
        "Tom",
        "vip",
        items,
        0,
        datetime.datetime.now()
    )

    processed = process_order(order, verbose=True)

    printer = OrderPrinter()
    printer.print_order(processed)

    logger1 = FileLogger()
    logger2 = ConsoleLogger()

    log_order(processed, logger1)
    log_order(processed, logger2)


if __name__ == "__main__":
    main()
