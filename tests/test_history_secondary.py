import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


WECHAT = Path(__file__).resolve().parents[1] / "wechat"
sys.path.insert(0, str(WECHAT))
spec = importlib.util.spec_from_file_location("history_article", WECHAT / "history_article.py")
history_article = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history_article)


class HistorySecondaryTests(unittest.TestCase):
    def test_retitle_generates_matching_cover(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "card.json"
            path.write_text(json.dumps({"title": "英文历史｜旧标题（2026-10-24）", "thumb_media_id": "old-cover"}))
            data = {"date": "2026-10-24", "title_zh": "河西走廊", "title_en": "Hexi", "lead": "导语", "paragraphs": [{"en": "English.", "zh": "中文。"}], "expressions": [], "questions": [], "sources": [{"label": "One", "url": "https://example.org/1"}, {"label": "Two", "url": "https://example.org/2"}]}
            with mock.patch.object(history_article, "load_cfg", return_value={"appid": "id", "appsecret": "secret"}), mock.patch.object(history_article, "get_token", return_value="token"), mock.patch.object(history_article, "new_cover", return_value="new-cover") as cover:
                history_article.export_secondary(data, path)
            cover.assert_called_once_with("token", data)
            self.assertEqual(json.loads(path.read_text())["thumb_media_id"], "new-cover")

    def test_existing_history_draft_matches_date_after_retitle(self):
        data = {
            "date": "2026-10-22",
            "title_en": "New English title",
            "title_zh": "新中文标题",
        }
        old_article = {"title": "英文历史｜旧中文标题（2026-10-22）"}
        response = {
            "total_count": 1,
            "item": [{"media_id": "existing", "content": {"news_item": [old_article]}}],
        }
        with mock.patch.object(history_article, "http", return_value=response):
            self.assertEqual(
                history_article.matching_drafts("token", data),
                [("existing", 0, old_article)],
            )

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

    def test_english_story_precedes_complete_chinese_translation(self):
        data = {
            "date": "2026-10-24",
            "title_en": "A Historical Choice",
            "title_zh": "一个历史抉择",
            "lead": "导语",
            "paragraphs": [
                {"en": "First English paragraph.", "zh": "第一段中文译文。"},
                {"en": "Second English paragraph.", "zh": "第二段中文译文。"},
            ],
            "expressions": [],
            "questions": [],
            "sources": [
                {"label": "Source 1", "url": "https://example.org/one"},
                {"label": "Source 2", "url": "https://example.org/two"},
            ],
        }
        for rendered in (
            history_article.article_markdown(data),
            history_article.article_html(data),
            history_article.article_html(data, wechat=True),
        ):
            self.assertLess(rendered.index("First English paragraph."), rendered.index("Second English paragraph."))
            self.assertLess(rendered.index("Second English paragraph."), rendered.index("第一段中文译文。"))
            self.assertLess(rendered.index("第一段中文译文。"), rendered.index("第二段中文译文。"))


if __name__ == "__main__":
    unittest.main()
