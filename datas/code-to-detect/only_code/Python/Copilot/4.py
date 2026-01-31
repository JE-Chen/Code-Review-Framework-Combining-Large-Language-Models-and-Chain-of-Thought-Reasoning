# 這是一個示範程式，雖然能執行，但充滿程式碼異味
# 程式碼異味包含：過度使用例外處理、濫用 try-except、無意義的錯誤攔截、命名混亂、效率低落

def risky_division(a, b):
    try:
        # 濫用 try-except：其實可以先檢查 b 是否為零
        return a / b
    except ZeroDivisionError:
        return 9999  # 魔法數字，沒有意義
    except Exception as e:
        # 捕捉所有例外但不處理，直接忽略
        print("Unexpected error:", e)
        return -1  # 不明意義的回傳值

def convert_to_int(value):
    try:
        return int(value)
    except ValueError:
        # 濫用例外處理：其實可以先用 str.isdigit()
        return 0
    except Exception:
        # 過度廣泛的例外攔截
        return -999  # 魔法數字

def read_file(filename):
    try:
        f = open(filename, "r")
        data = f.read()
        f.close()
        return data
    except FileNotFoundError:
        # 沒有錯誤處理策略，直接硬塞字串
        return "FILE_NOT_FOUND"
    except Exception as e:
        # 過度攔截，沒有意義
        print("Error occurred:", e)
        return ""

def process_data(data):
    try:
        # 過度巢狀的 try-except
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
        # 濫用例外處理：其實可以先檢查檔案是否存在
        content = read_file("data.txt")
        result = process_data(content)
        print("Result:", result)
    except Exception as e:
        # 過度廣泛的攔截，沒有意義
        print("Main error:", e)

if __name__ == "__main__":
    main()