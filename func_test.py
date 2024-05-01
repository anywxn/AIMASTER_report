from docx import Document

class TextProcessor:
    def __init__(self, text, keywords):
        self.text = text
        self.keywords = keywords
        self.data = {
            "Объект": None,
            "Работа": None,
            "Начальный пробег": None,
            "Конечный пробег": None
        }

    def process_text(self):
        words = self.text.split()
        i = 0
        while i < len(words):
            word = words[i]
            if word.lower() in self.keywords:
                if word.lower() == "начальный":
                    j = i + 1
                    while j < len(words):
                        if words[j].isdigit():
                            self.data["Начальный пробег"] = words[j]
                            break
                        j += 1
                elif word.lower() == "конечный":
                    j = i + 1
                    while j < len(words):
                        if words[j].isdigit():
                            self.data["Конечный пробег"] = words[j]
                            break
                        j += 1
                else:
                    current_key = word.capitalize()
                    current_value = " ".join(words[i + 1:]).strip()
                    next_keyword_index = len(words)  # По умолчанию, следующее ключевое слово - последнее слово в тексте
                    for keyword in self.keywords:
                        if keyword in words[i+1:]:
                            next_keyword_index = min(next_keyword_index, words[i+1:].index(keyword) + i + 1)
                    current_value = " ".join(words[i + 1:next_keyword_index]).strip()
                    self.data[current_key] = current_value
                    i = next_keyword_index - 1  # Устанавливаем индекс i на следующее ключевое слово
            i += 1

    def generate_report(self):
        report = "Отчет:\n"
        for key, value in self.data.items():
            if value is not None:
                report += f"{key}: {value}\n"
        return report.strip()

    def save_to_word(self, filename):
        doc = Document()
        report = self.generate_report()
        print(report)
        doc.add_paragraph(report)
        doc.save(filename)


# Пример использования
input_text = "объект уфимский авиационный техникум работа дипломная предписание начальный пробег 1 конечный пробег 99"
input_keywords = ["объект", "работа", "начальный", "конечный"]

processor = TextProcessor(input_text, input_keywords)
processor.process_text()
processor.save_to_word("report.docx")
