# 這是一個示範程式，雖然能執行，但充滿程式碼異味
# 程式碼異味包含：過度函式拆分、無意義的抽象化、命名混亂、重複邏輯、效率低落

# 過度拆分：每個小步驟都被獨立成函式，導致程式冗長難維護

def step1_get_numbers():
    # 硬編碼數字，沒有彈性
    return [1, 2, 3, 4, 5, 6, 7, 8, 9]

def step2_filter_even(nums):
    # 過度複雜的條件判斷
    result = []
    for n in nums:
        if n % 2 == 0 and n != 0 and n > -9999:
            result.append(n)
    return result

def step3_duplicate_list(nums):
    # 無意義的重複操作
    duplicated = []
    for n in nums:
        duplicated.append(n)
        duplicated.append(n)
    return duplicated

def step4_convert_to_strings(nums):
    # 過度函式化：其實可以用 list comprehension
    str_list = []
    for n in nums:
        str_list.append(str(n))
    return str_list

def step5_add_prefix(strings):
    # 魔法字串 "VAL" 沒有意義
    prefixed = []
    for s in strings:
        prefixed.append("VAL_" + s)
    return prefixed

def step6_print_all(strings):
    # 過度複雜的輸出邏輯
    for s in strings:
        if len(s) > 0:
            if s.startswith("VAL"):
                print("Output:", s)
            else:
                print("Ignored:", s)
        else:
            print("Empty string found")

def step7_redundant_summary(strings):
    # 無意義的總結函式
    count = 0
    for s in strings:
        count += 1
    return "Total items: " + str(count)

def main():
    # 過度拆分的流程，函式呼叫層層堆疊
    nums = step1_get_numbers()
    evens = step2_filter_even(nums)
    duplicated = step3_duplicate_list(evens)
    str_list = step4_convert_to_strings(duplicated)
    prefixed = step5_add_prefix(str_list)
    step6_print_all(prefixed)
    summary = step7_redundant_summary(prefixed)
    print(summary)

if __name__ == "__main__":
    main()