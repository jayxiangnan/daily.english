#!/usr/bin/env python3
"""Render a bilingual history article and prepare its WeChat secondary card."""

import argparse
import html
import json
from pathlib import Path

from push_wechat import API, get_token, http, load_cfg, upload_image

ROOT = Path(__file__).resolve().parent.parent


def checked_data(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not data["paragraphs"] or any(not p["en"].strip() or not p["zh"].strip() for p in data["paragraphs"]):
        raise ValueError("Every English paragraph needs a complete Chinese translation")
    if len(data["sources"]) < 2:
        raise ValueError("At least two sources are required")
    return data


def article_html(data, wechat=False):
    e = html.escape
    date = e(data["date"])
    title = e(data["title_en"])
    zh_title = e(data["title_zh"])
    parts = [
        '<article style="font-family:-apple-system,BlinkMacSystemFont,\'PingFang SC\',sans-serif;'
        'max-width:760px;margin:auto;padding:24px 18px;color:#263445;line-height:1.8;">',
        f'<header style="border-bottom:2px solid #667eea;padding-bottom:14px;margin-bottom:24px;">'
        f'<p style="color:#667eea;margin:0;">每日英文历史 · {date}</p>'
        f'<h1 style="font-size:28px;line-height:1.35;margin:9px 0;">{title}</h1>'
        f'<p style="font-size:18px;margin:0;color:#58677a;">{zh_title}</p></header>',
        f'<p style="color:#596779;">{e(data["lead"])}</p>',
    ]
    for p in data["paragraphs"]:
        parts.append(
            '<section style="margin:0 0 23px;">'
            f'<p lang="en" style="font-size:17px;line-height:1.85;margin:0 0 9px;">{e(p["en"])}</p>'
            f'<p lang="zh-CN" style="font-size:15px;line-height:1.85;color:#526070;margin:0;">{e(p["zh"])}</p>'
            '</section>'
        )
    parts.append('<h2 style="font-size:20px;color:#334d78;">重点表达 · Key expressions</h2><ul>')
    parts.extend(f'<li><strong>{e(x["en"])}</strong> — {e(x["zh"])}</li>' for x in data["expressions"])
    parts.append('</ul><h2 style="font-size:20px;color:#334d78;">阅读理解 · Reading check</h2><ol>')
    parts.extend(f'<li>{e(x["q"])}</li>' for x in data["questions"])
    parts.append('</ol><h3 style="font-size:18px;">参考答案 · Answers</h3><ol>')
    parts.extend(f'<li>{e(x["a"])}</li>' for x in data["questions"])
    parts.append('</ol><h2 style="font-size:20px;color:#334d78;">资料来源 · Sources</h2><ul>')
    parts.extend(
        f'<li><a href="{e(x["url"], quote=True)}">{e(x["label"])}</a>'
        + (f'<br><span>{e(x["url"])}</span>' if wechat else '')
        + '</li>'
        for x in data["sources"]
    )
    parts.append('</ul></article>')
    body = "\n".join(parts)
    if wechat:
        return body
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{title} | daily.english</title></head><body style="background:#f5f7fb;">'
        f'{body}</body></html>\n'
    )


def article_markdown(data):
    lines = [
        f'# {data["title_en"]}｜{data["title_zh"]}',
        '',
        f'每日英文历史 · {data["date"]}',
        '',
        data["lead"],
        '',
    ]
    for p in data["paragraphs"]:
        lines += [p["en"], '', p["zh"], '']
    lines += ['## 重点表达 · Key expressions', '']
    lines += [f'- **{x["en"]}**：{x["zh"]}' for x in data["expressions"]]
    lines += ['', '## 阅读理解 · Reading check', '']
    lines += [f'{i}. {x["q"]}' for i, x in enumerate(data["questions"], 1)]
    lines += ['', '### 参考答案 · Answers', '']
    lines += [f'{i}. {x["a"]}' for i, x in enumerate(data["questions"], 1)]
    lines += ['', '## 资料来源 · Sources', '']
    lines += [f'- [{x["label"]}]({x["url"]})' for x in data["sources"]]
    return "\n".join(lines) + "\n"


def render(data):
    date = data["date"]
    md = ROOT / "archive" / f"history-{date}.md"
    page = ROOT / "outputs" / f"history-{date}.html"
    md.write_text(article_markdown(data), encoding="utf-8")
    page.write_text(article_html(data), encoding="utf-8")
    return md, page


def check_response(response, action):
    if response.get("errcode") not in (None, 0):
        raise RuntimeError(f"{action} failed: {response.get('errcode')} {response.get('errmsg', '')}")
    return response


def matching_drafts(token, data):
    matches = []
    offset = 0
    while True:
        response = check_response(
            http(f"{API}/draft/batchget?access_token={token}",
                 {"offset": offset, "count": 20, "no_content": 1}),
            "draft/batchget",
        )
        items = response.get("item", [])
        for item in items:
            for index, article in enumerate(item.get("content", {}).get("news_item", [])):
                title = article.get("title", "")
                same_history_date = "每日英文历史" in title and data["date"] in title
                same_title = data["title_en"] in title or data["title_zh"] in title
                if same_history_date or same_title:
                    matches.append((item["media_id"], index, article))
        offset += len(items)
        if not items or offset >= response.get("total_count", offset):
            return matches


def new_cover(token, data):
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (900, 383), "#334d78")
    draw = ImageDraw.Draw(image)
    font_path = "/System/Library/Fonts/PingFang.ttc"
    heading = ImageFont.truetype(font_path, 64)
    subtitle = ImageFont.truetype(font_path, 31)
    draw.text((66, 84), "每日英文历史", font=heading, fill="white")
    draw.text((70, 207), data["title_zh"], font=subtitle, fill="#e4ebff")
    draw.text((70, 281), data["date"], font=subtitle, fill="#e4ebff")
    path = ROOT / "wechat" / f'cover-history-{data["date"]}.png'
    image.save(path)
    response = check_response(upload_image(token, str(path)), "material/add_material")
    if "media_id" not in response:
        raise RuntimeError("Cover upload returned no media_id")
    return response["media_id"]


def secondary_article(data, thumb_media_id):
    content = article_html(data, wechat=True)
    if len(content) >= 20000:
        raise ValueError("WeChat body exceeds 20,000 characters")
    return {
        "target_date": data["date"],
        "title": f'每日英文历史｜{data["title_zh"]}（{data["date"]}）',
        "author": "词汇拾光",
        "digest": data["lead"],
        "content": content,
        "content_source_url": "",
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }


def export_secondary(data, path):
    """Upload a cover and save the secondary card without creating a draft."""
    path = Path(path)
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    thumb = previous.get("thumb_media_id")
    if not thumb:
        cfg = load_cfg()
        token = get_token(cfg["appid"], cfg["appsecret"])
        thumb = new_cover(token, data)
    article = secondary_article(data, thumb)
    path.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def sync_draft(data):
    cfg = load_cfg()
    token = get_token(cfg["appid"], cfg["appsecret"])
    matches = matching_drafts(token, data)
    if len(matches) > 1:
        raise RuntimeError(f"Found {len(matches)} matching drafts; no draft was changed")

    if not matches:
        raise RuntimeError("不再单独新建历史草稿；请先准备同日单词头条，再创建双篇草稿")
    old = matches[0][2] if matches else {}
    thumb = old.get("thumb_media_id") or new_cover(token, data)
    if not thumb:
        raise RuntimeError("Missing cover thumb_media_id")
    article = secondary_article(data, thumb)
    media_id, index, _ = matches[0]
    response = http(f"{API}/draft/update?access_token={token}",
                    {"media_id": media_id, "index": index, "articles": article})
    if response.get("errcode") == 53407:
        return f"scheduled draft retained, media_id={media_id}"
    check_response(response, "draft/update")
    return f"draft updated, media_id={media_id}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", help="History article JSON")
    outputs = parser.add_mutually_exclusive_group()
    outputs.add_argument("--sync-draft", action="store_true", help="Update an existing legacy history draft only")
    outputs.add_argument("--export-secondary", metavar="PATH", help="Write a secondary card JSON for a combined draft")
    args = parser.parse_args()
    data = checked_data(args.data)
    md, page = render(data)
    print(f"Rendered {md} and {page}")
    if args.sync_draft:
        print(sync_draft(data))
    if args.export_secondary:
        print(f"Secondary card written to {export_secondary(data, args.export_secondary)}")


if __name__ == "__main__":
    main()
