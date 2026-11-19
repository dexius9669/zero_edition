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
        self.assertEqual(report["tables"], 172)
        self.assertEqual(report["blocks"]["note"], 7)
        self.assertEqual(report["blocks"]["center"], 13)

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
