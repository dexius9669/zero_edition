import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("convert", ROOT / "scripts" / "convert.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)

class ConversionTests(unittest.TestCase):
    def test_entire_book(self):
        report = converter.build(check=True)
        self.assertEqual(report["chapters"], 17)
        self.assertEqual(report["tables"], 169)
        self.assertEqual(report["blocks"]["note"], 6)
        self.assertEqual(report["blocks"]["center"], 13)

    def test_combined_encounter_table(self):
        source = (ROOT / "CoZ_книга.md").read_text(encoding="utf-8")
        self.assertIn("| d8 | Открытая местность | Лес | Озёра и реки | Болото |", source)
        self.assertIn("| 6 | Человек | Человек | Негуманоид | Нежить |", source)
        self.assertIn("| 8 | Дракон | Дракон | Негуманоид | Дракон |", source)
        self.assertNotIn("таблицы по террейнам", source)

    def test_note(self):
        result, counts = converter.convert_divs("::: {.note}\nПример *заметки*.\n:::\n")
        self.assertIn("Пример *заметки*.", result)
        self.assertIn("coz-note", result)
        self.assertEqual(counts["note"], 1)

    def test_fences(self):
        with self.assertRaises(ValueError):
            converter.convert_divs("::: {.note}\nНезакрытый блок")

if __name__ == "__main__":
    unittest.main()
