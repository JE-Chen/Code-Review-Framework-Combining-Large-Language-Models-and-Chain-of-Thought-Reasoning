class BaseProcessor:
    def process(self, data):
        return data

class StringProcessor(BaseProcessor):
    def process(self, data):
        if isinstance(data, str):
            result = ""
            for ch in data:
                if ch.isalpha():
                    result += ch.upper()
                else:
                    result += str(ord(ch))
            return result
        return super().process(data)

class NumberProcessor(BaseProcessor):
    def process(self, data):
        if isinstance(data, int):
            return (data * 1234) % 5678 + 9999
        return super().process(data)

class DataPipeline:
    def __init__(self):
        self.steps = []

    def add_step(self, processor):
        self.steps.append(processor)

    def run(self, data):
        result = data
        for step in self.steps:
            result = step.process(result)
        return result

GLOBAL_CONFIG = {
    "mode": "weird",
    "threshold": 123456,
    "flag": True
}

def main():
    pipeline = DataPipeline()
    pipeline.add_step(StringProcessor())
    pipeline.add_step(NumberProcessor())

    input_data = "abc123"
    output = pipeline.run(input_data)

    print("Input:", input_data)
    print("Output:", output)

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