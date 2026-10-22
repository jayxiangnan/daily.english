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
        'max-width:760px;margin:auto;padding:18px 16px;color:#2c3e50;line-height:1.8;background:#f3f5f9;">',
        '<header style="padding:28px 22px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);'
        'border-radius:14px;margin-bottom:22px;color:#fff;">'
        f'<p style="margin:0 0 10px;font-size:13px;color:#ecedff;">每日英文历史 · {date}</p>'
        f'<h1 style="font-size:27px;line-height:1.35;margin:0 0 10px;color:#fff;">{title}</h1>'
        f'<p style="font-size:16px;line-height:1.6;margin:0;color:#f1ecff;">{zh_title}</p></header>',
        '<section style="margin:0 0 22px;padding:18px 20px;background:#fff;border-radius:12px;">'
        f'<p style="font-size:15px;color:#526070;margin:0;">{e(data["lead"])}</p></section>',
        '<section style="margin:0 0 22px;padding:22px 20px;background:#fff;border-radius:12px;'
        'box-shadow:0 2px 12px rgba(0,0,0,0.05);">',
        '<h2 style="font-size:20px;color:#394f8a;margin:0 0 18px;">English Story</h2>',
    ]
    for i, p in enumerate(data["paragraphs"], 1):
        parts.append(
            f'<p lang="en" style="font-size:17px;line-height:1.85;margin:0 0 18px;">'
            f'<span style="font-size:12px;color:#667eea;font-weight:bold;margin-right:9px;">{i:02d}</span>'
            f'{e(p["en"])}</p>'
        )
    parts.append('</section><section style="margin:0 0 22px;padding:22px 20px;background:#fff;border-radius:12px;'
                 'box-shadow:0 2px 12px rgba(0,0,0,0.05);">'
                 '<h2 style="font-size:20px;color:#394f8a;margin:0 0 18px;">中文译文</h2>')
    for i, p in enumerate(data["paragraphs"], 1):
        parts.append(
            f'<p lang="zh-CN" style="font-size:16px;line-height:1.9;color:#46576b;margin:0 0 18px;">'
            f'<span style="font-size:12px;color:#667eea;font-weight:bold;margin-right:9px;">{i:02d}</span>'
            f'{e(p["zh"])}</p>'
        )
    parts.append('</section><section style="margin:0 0 22px;padding:22px 20px;background:#fff;border-radius:12px;">'
                 '<h2 style="font-size:20px;color:#394f8a;margin:0 0 14px;">重点表达 · Key expressions</h2><ul>')
    parts.extend(f'<li><strong>{e(x["en"])}</strong> — {e(x["zh"])}</li>' for x in data["expressions"])
    parts.append('</ul></section><section style="margin:0 0 22px;padding:22px 20px;background:#fff;border-radius:12px;">'
                 '<h2 style="font-size:20px;color:#394f8a;margin:0 0 14px;">阅读理解 · Reading check</h2><ol>')
    parts.extend(f'<li>{e(x["q"])}</li>' for x in data["questions"])
    parts.append('</ol><h3 style="font-size:18px;color:#2c3e50;">参考答案 · Answers</h3><ol>')
    parts.extend(f'<li>{e(x["a"])}</li>' for x in data["questions"])
    parts.append('</ol></section><section style="padding:22px 20px;background:#fff;border-radius:12px;">'
                 '<h2 style="font-size:20px;color:#394f8a;margin:0 0 14px;">资料来源 · Sources</h2><ul>')
    parts.extend(
        f'<li><a href="{e(x["url"], quote=True)}">{e(x["label"])}</a>'
        + (f'<br><span>{e(x["url"])}</span>' if wechat else '')
        + '</li>'
        for x in data["sources"]
    )
    parts.append('</ul></section></article>')
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
        '## English Story',
        '',
    ]
    for i, p in enumerate(data["paragraphs"], 1):
        lines += [f'**{i:02d}** {p["en"]}', '']
    lines += ['## 中文译文', '']
    for i, p in enumerate(data["paragraphs"], 1):
        lines += [f'**{i:02d}** {p["zh"]}', '']
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
                same_history_date = "英文历史" in title and data["date"] in title
                same_title = data["title_en"] in title or data["title_zh"] in title
                if same_history_date or same_title:
                    matches.append((item["media_id"], index, article))
        offset += len(items)
        if not items or offset >= response.get("total_count", offset):
            return matches


def new_cover(token, data):
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (900, 383))
    draw = ImageDraw.Draw(image)
    for x in range(900):
        ratio = x / 899
        draw.line((x, 0, x, 383), fill=(
            round(72 + 40 * ratio),
            round(88 - 20 * ratio),
            round(155 + 12 * ratio),
        ))
    font_path = "/System/Library/Fonts/PingFang.ttc"
    heading = ImageFont.truetype(font_path, 34)
    size = 44
    while True:
        subtitle = ImageFont.truetype(font_path, size)
        if draw.textbbox((0, 0), data["title_zh"], font=subtitle)[2] <= 760 or size <= 26:
            break
        size -= 2
    meta = ImageFont.truetype(font_path, 24)
    draw.text((66, 60), "英文历史阅读  /  HISTORY", font=heading, fill="#f2f2ff")
    draw.text((66, 143), data["title_zh"], font=subtitle, fill="white")
    draw.text((70, 285), data["date"], font=meta, fill="#e4ebff")
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
        "title": f'英文历史｜{data["title_zh"]}（{data["date"]}）',
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
    old = matches[0][2]
    target_title = f'英文历史｜{data["title_zh"]}（{data["date"]}）'
    thumb = old.get("thumb_media_id") if old.get("title") == target_title else None
    thumb = thumb or new_cover(token, data)
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
