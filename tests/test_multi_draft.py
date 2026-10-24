import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "wechat" / "push_wechat.py"
spec = importlib.util.spec_from_file_location("push_wechat", SCRIPT)
push_wechat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(push_wechat)


class MultiDraftTests(unittest.TestCase):
    def setUp(self):
        self.main = {"title": "每日 5 词 · 第 28 期（2026年10月24日）"}
        self.history = {"title": "英语读史｜一座桥的故事"}

    def test_builds_main_then_history(self):
        self.assertEqual(
            push_wechat.draft_articles(self.main, self.history),
            [self.main, self.history],
        )

    def test_converts_card_date_for_pairing(self):
        self.assertEqual(push_wechat.date_cn_to_iso("2026年10月24日"), "2026-10-24")

    def test_refuses_to_update_single_article_draft_as_pair(self):
        with self.assertRaisesRegex(ValueError, "两篇"):
            push_wechat.check_existing_pair([self.main], self.main, self.history)

    def test_refuses_to_update_wrong_pair(self):
        with self.assertRaisesRegex(ValueError, "标题"):
            push_wechat.check_existing_pair(
                [self.main, {"title": "别的次条"}], self.main, self.history
            )

    def test_accepts_matching_pair(self):
        push_wechat.check_existing_pair([self.main, self.history], self.main, self.history)

    def test_allows_history_retitle_on_same_date(self):
        old_history = {"title": "每日英文历史｜旧标题（2026-10-24）"}
        new_history = {"title": "每日英文历史｜新标题（2026-10-24）"}
        push_wechat.check_existing_pair([self.main, old_history], self.main, new_history, "2026-10-24")

    def test_allows_current_history_title_replacement_on_same_date(self):
        old_history = {"title": "英文历史｜柏林空运（2026-10-24）"}
        new_history = {"title": "英文历史｜河西走廊（2026-10-24）"}
        push_wechat.check_existing_pair([self.main, old_history], self.main, new_history, "2026-10-24")

    def test_finds_existing_main_before_creating_pair(self):
        with mock.patch.object(push_wechat, "http", return_value={"total_count": 1, "item": [{"media_id": "old", "content": {"news_item": [self.main]}}]}):
            self.assertEqual(push_wechat.find_existing_main_drafts("token", self.main["title"]), ["old"])

    def test_cli_sends_one_ordered_two_article_draft(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            words = root / "words.json"
            lesson = root / "lesson.json"
            history = root / "history.json"
            words.write_text(json.dumps([{"word": "test", "phonetic": "/test/", "meaning": "测试", "en": "A test.", "zh": "一次测试。", "tip": "test"}]))
            lesson.write_text(json.dumps({"wechat_title": self.main["title"], "wechat_digest": "主稿摘要"}))
            history.write_text(json.dumps({"title": self.history["title"], "digest": "次稿摘要", "content": "<p>History.</p>", "thumb_media_id": "history-cover", "target_date": "2026-10-24"}))
            calls = []

            def fake_http(url, data=None, **kwargs):
                calls.append((url, data))
                if "/draft/batchget?" in url:
                    return {"total_count": 0, "item": []}
                if "/draft/add?" in url:
                    return {"media_id": "combined-draft"}
                raise AssertionError(url)

            argv = ["push_wechat.py", "--words", str(words), "--lesson", str(lesson), "--secondary-article", str(history), "--date", "2026年10月24日", "--episode", "28", "--auto-cover"]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(push_wechat, "load_cfg", return_value={"appid": "id", "appsecret": "secret", "thumb_media_id": "main-cover"}), mock.patch.object(push_wechat, "get_token", return_value="token"), mock.patch.object(push_wechat, "build_html", return_value="<p>Words.</p>"), mock.patch.object(push_wechat, "make_cover"), mock.patch.object(push_wechat, "upload_image", return_value={"media_id": "fresh-main-cover"}), mock.patch.object(push_wechat, "http", side_effect=fake_http), redirect_stdout(io.StringIO()):
                push_wechat.main()
            self.assertEqual(len(calls), 2)
            self.assertEqual([a["title"] for a in calls[1][1]["articles"]], [self.main["title"], self.history["title"]])
            self.assertEqual(calls[1][1]["articles"][1]["thumb_media_id"], "history-cover")


if __name__ == "__main__":
    unittest.main()
