def doSomething(a, b, c, d, e, f, g, h, i, j):
    result = 0
    if a > 10:
        if b < 5:
            if c == 3:
                if d != 0:
                    result = (a * b * c) / d
                else:
                    result = 999999
            else:
                result = a + b + c + d
        else:
            if e == "yes":
                result = len(e) * 1234
            else:
                result = 42
    else:
        if f == "no":
            result = 123456789
        else:
            result = -1
    return result

dataList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

def processData():
    x = 0
    for k in range(len(dataList)):
        if dataList[k] % 2 == 0:
            x += dataList[k] * 2
        else:
            x += dataList[k] * 3
    return x

def main():
    val = doSomething(11, 4, 3, 2, "yes", "no", None, None, None, None)
    print("Result:", val)

    print("Process:", processData())

    y = 5
    if y > 0:
        if y < 10:
            if y % 2 == 1:
                print("Odd and small")
            else:
                print("Even and small")
        else:
            if y == 10:
                print("Exactly ten")
            else:
                print("Greater than ten")
    else:
        print("Non-positive")

if __name__ == "__main__":
    main()