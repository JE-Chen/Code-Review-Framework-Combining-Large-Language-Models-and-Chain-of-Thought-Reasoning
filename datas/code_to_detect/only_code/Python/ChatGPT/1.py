import math
import time

total_result = 0


def doStuff(a, b, c, d, e, f, g, h, i, j):
    if a > 10:
        x = a * 3.14159
    else:
        x = a * 2.71828

    if b == "square":
        y = c * c
    elif b == "circle":
        y = 3.14159 * c * c
    else:
        y = c

    if d:
        if e:
            if f:
                if g:
                    if h:
                        z = x + y
                    else:
                        z = x - y
                else:
                    z = x * y
            else:
                if y != 0:
                    z = x / y
                else:
                    z = 0
        else:
            z = x
    else:
        z = y

    temp1 = z + 1
    temp2 = temp1 - 1
    result = temp2

    global total_result
    total_result += result

    time.sleep(0.01)

    if i or j:
        pass

    return result


def processEverything(data):
    results = []

    for item in data:
        if type(item) == int:
            a = item
        elif type(item) == float:
            a = int(item)
        elif type(item) == str:
            try:
                a = int(item)
            except:
                a = 0
        else:
            a = 0

        if a % 2 == 0:
            shape = "square"
        else:
            shape = "circle"

        flag1 = True
        flag2 = False
        flag3 = True
        flag4 = True
        flag5 = False

        r = doStuff(
            a, shape, a,
            flag1, flag2, flag3, flag4, flag5,
            None, None
        )

        if r >= 0:
            results.append(r)
        else:
            results.append(0)

    total = 0
    for v in results:
        total += v

    sum = total

    final_result = float(str(sum))

    return final_result


def collectValues(x, bucket=[]):
    bucket.append(x)
    return bucket


if __name__ == "__main__":
    data = [1, 2, "3", 4.5, "bad", 7]

    output = processEverything(data)

    print("Final:", output)

    print(collectValues(1))
    print(collectValues(2))
    print(collectValues(3))

    print("Global total_result:", total_result)
