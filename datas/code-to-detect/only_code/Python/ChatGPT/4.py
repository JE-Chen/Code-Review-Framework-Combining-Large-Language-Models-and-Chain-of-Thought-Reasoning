# 一個「企業風格」的報表產生系統
# 功能正常，但設計品質災難現場 🤮

import time


# ❌ 全域設定物件（Global Configuration Object Smell）
CONFIG = {
    "export_format": "text",
    "uppercase": False,
    "retry": 3,
}


# ❌ Base Class 設計過度（Over-Abstracted Base Class）
class BaseExporter:
    def prepare(self, data):
        raise NotImplementedError()

    def export(self, data):
        raise NotImplementedError()

    def finish(self):
        # ❌ Refused Bequest 預備役：大多子類根本不需要這個方法
        pass


# ❌ Parallel Inheritance Hierarchy（平行繼承結構開端）
class TextExporter(BaseExporter):
    def prepare(self, data):
        return data

    def export(self, data):
        print("TEXT EXPORT:")
        print(data)

    def finish(self):
        print("Text export finished")


class UpperTextExporter(BaseExporter):
    # ❌ Inheritance Misuse：只為了一點點差異就生新類別
    def prepare(self, data):
        return data.upper()

    def export(self, data):
        print("UPPER TEXT EXPORT:")
        print(data)

    def finish(self):
        print("Upper text export finished")


# ❌ 不穩定介面（Unstable Interface）
class JsonLikeExporter(BaseExporter):
    def prepare(self, data):
        return "{'report': '" + data + "'}"

    def export(self, data):
        print("JSON-LIKE EXPORT:")
        print(data)


# ❌ 過度工程（Overengineering）：小功能搞一堆類別
class Report:
    def __init__(self, title, rows):
        self.title = title
        self.rows = rows


class ReportFormatter:
    def format(self, report):
        # ❌ Control Flag Variable：用旗標控制流程
        text = ""
        for r in report.rows:
            if CONFIG["uppercase"]:
                text = text + r.upper() + "\n"
            else:
                text = text + r + "\n"
        return report.title + "\n" + text


# ❌ Leaky Abstraction：Formatter 知道太多 Exporter 的需求
class ReportService:
    def __init__(self, exporter):
        self.exporter = exporter

    def generate(self, report):
        formatter = ReportFormatter()
        content = formatter.format(report)

        # ❌ Parameter Reassignment：重寫參數內容
        report = content

        prepared = self.exporter.prepare(report)

        # ❌ Premature Optimization：無意義的手動 buffer
        buffer = ""
        for ch in prepared:
            buffer = buffer + ch

        self.exporter.export(buffer)

        # ❌ Callback-style 設計但其實沒 callback（Pointless Hook）
        self.after_export()

    def after_export(self):
        # ❌ YAGNI（You Aren’t Gonna Need It）
        pass


# ❌ God Object 變形版：管理太多責任（Configuration + Factory + Logic）
class ExportManager:
    def __init__(self):
        self.history = []

    def create_exporter(self):
        fmt = CONFIG["export_format"]

        # ❌ Magic String Dependency：格式全靠字串硬對
        if fmt == "text":
            if CONFIG["uppercase"]:
                return UpperTextExporter()
            return TextExporter()

        elif fmt == "json":
            return JsonLikeExporter()

        else:
            # ❌ Silent Fallback：錯誤情況默默改用預設
            return TextExporter()

    def run(self, report):
        exporter = self.create_exporter()

        service = ReportService(exporter)

        # ❌ Hidden Timing Dependency：偷偷插入時間行為
        start = time.time()

        service.generate(report)

        end = time.time()

        # ❌ Dead Store：記錄但從來沒用過
        duration = end - start

        self.history.append(report.title)


# ❌ Repeated Abstraction Layer：毫無必要的轉接層
class Application:
    def __init__(self):
        self.manager = ExportManager()

    def execute(self, title, rows):
        report = Report(title, rows)
        self.manager.run(report)


# 主程式
def main():
    rows = [
        "apple 10",
        "banana 5",
        "orange 7"
    ]

    # ❌ Temporal Configuration Smell：一定要先設 CONFIG 才能正常跑
    CONFIG["export_format"] = "text"
    CONFIG["uppercase"] = True

    app = Application()
    app.execute("FRUIT REPORT", rows)

    # ❌ 修改全域設定造成後續行為改變（Action at a Distance）
    CONFIG["uppercase"] = False
    CONFIG["export_format"] = "json"

    app.execute("FRUIT REPORT 2", rows)


if __name__ == "__main__":
    main()
