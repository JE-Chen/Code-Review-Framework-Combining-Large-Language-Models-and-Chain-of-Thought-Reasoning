import time

CONFIG = {
    "export_format": "text",
    "uppercase": False,
    "retry": 3,
}

class BaseExporter:
    def prepare(self, data):
        raise NotImplementedError()

    def export(self, data):
        raise NotImplementedError()

    def finish(self):
        # ❌ Refused Bequest 預備役：大多子類根本不需要這個方法
        pass


class TextExporter(BaseExporter):
    def prepare(self, data):
        return data

    def export(self, data):
        print("TEXT EXPORT:")
        print(data)

    def finish(self):
        print("Text export finished")


class UpperTextExporter(BaseExporter):
    def prepare(self, data):
        return data.upper()

    def export(self, data):
        print("UPPER TEXT EXPORT:")
        print(data)

    def finish(self):
        print("Upper text export finished")


class JsonLikeExporter(BaseExporter):
    def prepare(self, data):
        return "{'report': '" + data + "'}"

    def export(self, data):
        print("JSON-LIKE EXPORT:")
        print(data)


class Report:
    def __init__(self, title, rows):
        self.title = title
        self.rows = rows


class ReportFormatter:
    def format(self, report):
        text = ""
        for r in report.rows:
            if CONFIG["uppercase"]:
                text = text + r.upper() + "\n"
            else:
                text = text + r + "\n"
        return report.title + "\n" + text


class ReportService:
    def __init__(self, exporter):
        self.exporter = exporter

    def generate(self, report):
        formatter = ReportFormatter()
        content = formatter.format(report)

        report = content

        prepared = self.exporter.prepare(report)

        buffer = ""
        for ch in prepared:
            buffer = buffer + ch

        self.exporter.export(buffer)

        self.after_export()

    def after_export(self):
        pass


class ExportManager:
    def __init__(self):
        self.history = []

    def create_exporter(self):
        fmt = CONFIG["export_format"]

        if fmt == "text":
            if CONFIG["uppercase"]:
                return UpperTextExporter()
            return TextExporter()

        elif fmt == "json":
            return JsonLikeExporter()

        else:
            return TextExporter()

    def run(self, report):
        exporter = self.create_exporter()

        service = ReportService(exporter)

        start = time.time()

        service.generate(report)

        end = time.time()

        duration = end - start

        self.history.append(report.title)


class Application:
    def __init__(self):
        self.manager = ExportManager()

    def execute(self, title, rows):
        report = Report(title, rows)
        self.manager.run(report)


def main():
    rows = [
        "apple 10",
        "banana 5",
        "orange 7"
    ]

    CONFIG["export_format"] = "text"
    CONFIG["uppercase"] = True

    app = Application()
    app.execute("FRUIT REPORT", rows)

    CONFIG["uppercase"] = False
    CONFIG["export_format"] = "json"

    app.execute("FRUIT REPORT 2", rows)


if __name__ == "__main__":
    main()
