# 這是一個示範程式，雖然能執行，但充滿程式碼異味
# 程式碼異味包含：過度物件導向、濫用繼承、過度複雜結構、無意義的抽象化、奇怪的命名

class BaseProcessor:
    # 過度抽象化，沒有必要的基底類別
    def process(self, data):
        return data

class StringProcessor(BaseProcessor):
    # 繼承但沒有真正需要
    def process(self, data):
        # 過度複雜的字串處理
        if isinstance(data, str):
            result = ""
            for ch in data:
                if ch.isalpha():
                    result += ch.upper()
                else:
                    result += str(ord(ch))  # 把非字母轉成 ASCII
            return result
        return super().process(data)

class NumberProcessor(BaseProcessor):
    # 濫用繼承，邏輯不清楚
    def process(self, data):
        if isinstance(data, int):
            # 過度複雜的計算，沒有意義
            return (data * 1234) % 5678 + 9999
        return super().process(data)

class DataPipeline:
    # 過度設計的管線，實際上只是呼叫函式
    def __init__(self):
        self.steps = []

    def add_step(self, processor):
        self.steps.append(processor)

    def run(self, data):
        result = data
        for step in self.steps:
            result = step.process(result)
        return result

# 全域常數濫用
GLOBAL_CONFIG = {
    "mode": "weird",
    "threshold": 123456,  # 魔法數字
    "flag": True
}

def main():
    pipeline = DataPipeline()
    pipeline.add_step(StringProcessor())
    pipeline.add_step(NumberProcessor())

    # 過度複雜的呼叫，硬塞參數
    input_data = "abc123"
    output = pipeline.run(input_data)

    print("Input:", input_data)
    print("Output:", output)

    # 過度巢狀的邏輯
    val = 7
    if GLOBAL_CONFIG["flag"]:
        if val > 5:
            if val < GLOBAL_CONFIG["threshold"]:
                if GLOBAL_CONFIG["mode"] == "weird":
                    print("Strange mode active:", val)
                else:
                    print("Normal mode:", val)
            else:
                print("Value too large")
        else:
            print("Value too small")
    else:
        print("Flag disabled")

if __name__ == "__main__":
    main()