import importlib.util
import sys
import unittest
from pathlib import Path


WECHAT = Path(__file__).resolve().parents[1] / "wechat"
sys.path.insert(0, str(WECHAT))
spec = importlib.util.spec_from_file_location("history_article", WECHAT / "history_article.py")
history_article = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history_article)


class HistorySecondaryTests(unittest.TestCase):
    def test_secondary_article_contains_full_bilingual_body(self):
        data = {
            "date": "2026-10-24",
            "title_en": "A Historical Choice",
            "title_zh": "一个历史抉择",
            "lead": "导语",
            "paragraphs": [{"en": "An English paragraph.", "zh": "一段中文翻译。"}],
            "expressions": [],
            "questions": [],
            "sources": [{"label": "Source 1", "url": "https://example.org/one"}, {"label": "Source 2", "url": "https://example.org/two"}],
        }
        article = history_article.secondary_article(data, "cover-id")
        self.assertEqual(article["thumb_media_id"], "cover-id")
        self.assertEqual(article["target_date"], "2026-10-24")
        self.assertIn("2026-10-24", article["title"])
        self.assertIn("An English paragraph.", article["content"])
        self.assertIn("一段中文翻译。", article["content"])


if __name__ == "__main__":
    unittest.main()
