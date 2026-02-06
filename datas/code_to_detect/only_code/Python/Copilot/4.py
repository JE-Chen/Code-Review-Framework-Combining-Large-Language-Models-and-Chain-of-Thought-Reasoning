def risky_division(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 9999
    except Exception as e:
        print("Unexpected error:", e)
        return -1

def convert_to_int(value):
    try:
        return int(value)
    except ValueError:
        return 0
    except Exception:
        return -999

def read_file(filename):
    try:
        f = open(filename, "r")
        data = f.read()
        f.close()
        return data
    except FileNotFoundError:
        return "FILE_NOT_FOUND"
    except Exception as e:
        print("Error occurred:", e)
        return ""

def process_data(data):
    try:
        try:
            numbers = [convert_to_int(x) for x in data.split(",")]
        except Exception:
            numbers = []
        total = 0
        for n in numbers:
            try:
                total += risky_division(n, 2)
            except Exception:
                total += 0
        return total
    except Exception:
        return None

def main():
    try:
        content = read_file("data.txt")
        result = process_data(content)
        print("Result:", result)
    except Exception as e:
        print("Main error:", e)

if __name__ == "__main__":
    main()