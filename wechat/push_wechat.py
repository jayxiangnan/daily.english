#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号每日单词推送脚本
- 默认只创建草稿（安全，可预览）
- 加 --publish 参数才会真正群发推送给关注者（不可撤销，请谨慎）
"""
import json, sys, os, ssl, time, urllib.request, urllib.parse, argparse, html

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(BASE, "config.json")
API = "https://api.weixin.qq.com/cgi-bin"


def tls_context():
    """在系统 Python 缺少自带 CA 包时使用 macOS 的系统证书。"""
    cafile = os.environ.get("SSL_CERT_FILE")
    if not cafile and os.path.isfile("/etc/ssl/cert.pem"):
        cafile = "/etc/ssl/cert.pem"
    return ssl.create_default_context(cafile=cafile)


def load_cfg():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def http(url, data=None, raw=False, retries=3):
    """带重试的请求，应对微信 API 偶发 SSL/超时抖动"""
    ctx = tls_context()
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else None
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers={
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/json; charset=utf-8",
            })
            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                txt = r.read().decode("utf-8")
            return txt if raw else json.loads(txt)
        except Exception as e:
            last = e
            if attempt < retries - 1:
                wait = 2 * (attempt + 1)
                print(f"  请求失败({type(e).__name__})，{wait}s 后重试 {attempt + 2}/{retries}...")
                time.sleep(wait)
    raise last


def get_token(appid, secret):
    r = http(f"{API}/token?grant_type=client_credential&appid={appid}&secret={secret}")
    if "access_token" not in r:
        raise RuntimeError(f"获取 access_token 失败: {r}")
    return r["access_token"]


def make_cover(word_list, episode, date_cn, out_path):
    """按当期内容生成封面图：渐变底 + 标题 + 期数 + 本期 5 个词"""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 900, 383
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    c1, c2 = (102, 126, 234), (118, 75, 162)
    for x in range(W):
        t = x / (W - 1)
        d.line([(x, 0), (x, H)], fill=(
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)))
    fp = "/System/Library/Fonts/PingFang.ttc"
    f_title = ImageFont.truetype(fp, 72)
    f_sub = ImageFont.truetype(fp, 28)

    def center(text, font, y, fill):
        w = int(d.textlength(text, font=font))
        d.text(((W - w) / 2, y), text, font=font, fill=fill)
        return w

    center("每日 5 词", f_title, 92, (255, 255, 255))
    center(f"第 {episode} 期 · {date_cn}", f_sub, 182, (236, 239, 252))

    line = "  ·  ".join(word_list)
    size = 26
    while True:
        f = ImageFont.truetype(fp, size)
        bb = d.textbbox((0, 0), line, font=f)
        if bb[2] - bb[0] <= W - 90 or size <= 14:
            break
        size -= 2
    center(line, f, 272, (232, 235, 250))

    img.save(out_path, "PNG")
    return out_path


def upload_image(token, path, retries=3):
    """上传图片为永久素材，返回 media_id（带重试，应对偶发连接被断）"""
    import uuid
    url = f"{API}/material/add_material?access_token={token}&type=image"
    boundary = "----WBForm" + uuid.uuid4().hex
    with open(path, "rb") as fp:
        data = fp.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="media"; filename="{os.path.basename(path)}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode("utf-8") + data + f"\r\n--{boundary}--\r\n".encode("utf-8")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    ctx = tls_context()
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            if i < retries - 1:
                wait = 2 * (i + 1)
                print(f"      封面上传失败({type(e).__name__})，{wait}s 后重试 {i+2}/{retries}...")
                time.sleep(wait)
    raise last


def lesson_html(lesson):
    """可选的情境讲解，草稿正文也完整呈现，不依赖外链。"""
    if not lesson:
        return "", "", ""
    esc = html.escape
    lead = (f'<section style="margin:0 0 22px;padding:20px 18px;background:#fff;border-radius:12px;line-height:1.8;">'
            f'<p style="margin:0 0 8px;color:#667eea;font-size:13px;">今日情境</p>'
            f'<h2 style="margin:0 0 10px;color:#2c3e50;font-size:20px;">{esc(lesson["title"])}</h2>'
            f'<p style="margin:0;color:#4a5568;font-size:15px;">{esc(lesson["lead"])}</p></section>')
    lines = "".join(
        f'<p style="margin:0 0 12px;line-height:1.7;"><strong style="color:#2c3e50;">{esc(line["en"])}</strong>'
        f'<br><span style="color:#718096;font-size:14px;">{esc(line["zh"])}</span></p>'
        for line in lesson["dialogue"]
    )
    dialogue = (f'<section style="margin:0 0 22px;padding:20px 18px;background:#fff;border-radius:12px;">'
                f'<h2 style="margin:0 0 16px;color:#2c3e50;font-size:19px;">情境对话</h2>{lines}</section>')
    practice = "".join(
        f'<p style="margin:0 0 12px;line-height:1.7;"><strong>{i}. {esc(item["question"])}</strong>'
        f'<br><span style="color:#667eea;">答案：{esc(item["answer"])}</span>'
        f'<br><span style="color:#718096;font-size:14px;">{esc(item["explanation"])}</span></p>'
        for i, item in enumerate(lesson["practice"], 1)
    )
    creation_note = lesson.get("creation_note", "")
    creation_note_html = (
        f'<p style="margin:16px 0 0;color:#9aa0a6;font-size:12px;">{esc(creation_note)}</p>'
        if creation_note else ""
    )
    end = (f'<section style="margin:0 0 22px;padding:20px 18px;background:#fff;border-radius:12px;">'
           f'<h2 style="margin:0 0 14px;color:#2c3e50;font-size:19px;">用一分钟检验是否会用</h2>{practice}'
           f'<p style="margin:16px 0 0;line-height:1.8;color:#4a5568;">{esc(lesson["closing"])}</p>'
           f'{creation_note_html}</section>')
    return lead, dialogue, end


def build_html(words, date_cn, episode, online_url=None, lesson=None):
    """生成公众号兼容正文：纯内联样式，无 JS、无外链 CSS"""
    cards = []
    notes_cards = []
    for i, w in enumerate(words, 1):
        notes = lesson.get("notes", {}).get(w["word"], {}) if lesson else {}
        notes_html = "".join(
            f'<p style="margin:10px 0 0;font-size:14px;color:#4a5568;line-height:1.7;">'
            f'<strong>{label}</strong> {html.escape(notes[key])}</p>'
            for key, label in (("usage", "怎么用："), ("pitfall", "易错点：")) if notes.get(key)
        )
        tip_html = (
            f'<p style="margin:14px 0 0;padding:12px 14px;background:#fdf6ec;border-radius:8px;'
            f'font-size:14px;color:#a3661a;line-height:1.7;">💡 {w["tip"]}</p>'
        ) if w.get("tip") else ""
        if notes_html:
            notes_cards.append(
                f'<section style="margin:0 0 18px;padding-bottom:16px;border-bottom:1px solid #edf0f4;">'
                f'<h3 style="margin:0;color:#2c3e50;font-size:17px;">{html.escape(w["word"])}</h3>'
                f'{notes_html}</section>'
            )
        cards.append(f"""
<section style="margin:0 0 22px;padding:20px 18px;background:#ffffff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.06);">
  <section style="display:flex;align-items:center;margin-bottom:12px;">
    <span style="display:inline-block;width:30px;height:30px;line-height:30px;text-align:center;background:#667eea;color:#fff;border-radius:50%;font-size:15px;font-weight:bold;">{i}</span>
    <span style="margin-left:12px;font-size:22px;font-weight:bold;color:#2c3e50;">{w['word']}</span>
  </section>
  <p style="margin:0 0 10px;font-size:14px;color:#8a8a8a;font-family:Menlo,Consolas,monospace;">{w['phonetic']}</p>
  <p style="margin:0 0 14px;font-size:16px;color:#34495e;font-weight:bold;line-height:1.6;">{w['meaning']}</p>
  <section style="padding:12px 14px;background:#f6f8fa;border-left:3px solid #667eea;border-radius:0 8px 8px 0;margin-bottom:12px;">
    <p style="margin:0 0 6px;font-size:15px;color:#2c3e50;line-height:1.7;">{w['en']}</p>
    <p style="margin:0;font-size:13px;color:#9aa0a6;line-height:1.6;">{w['zh']}</p>
  </section>
  {tip_html}
</section>""")

    online_html = (
        f'<p style="margin:24px 0 0;padding:16px;background:#eef3ff;border-radius:10px;font-size:14px;'
        f'color:#4a5568;line-height:1.8;text-align:center;">🔊 点击文末「阅读原文」可在线听单词发音</p>'
    ) if online_url else ""

    lead_html, dialogue_html, end_html = lesson_html(lesson)
    notes_section = (
        '<section style="margin:0 0 22px;padding:20px 18px;background:#fff;border-radius:12px;">'
        '<h2 style="margin:0 0 16px;color:#2c3e50;font-size:19px;">用法辨析与易错点</h2>'
        + ''.join(notes_cards) + '</section>'
    ) if notes_cards else ""
    return f"""
<section style="padding:18px 16px;background:#f3f5f9;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;">
  <section style="text-align:center;padding:26px 16px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:14px;margin-bottom:22px;">
    <p style="margin:0;font-size:24px;font-weight:bold;color:#ffffff;">每日 5 词</p>
    <p style="margin:10px 0 0;font-size:14px;color:rgba(255,255,255,0.9);">{date_cn} · 第 {episode} 期</p>
    <p style="margin:12px 0 0;font-size:13px;color:rgba(255,255,255,0.75);">生活 & 职场高频实用词汇</p>
  </section>
  {''.join(cards)}
  {lead_html}
  {dialogue_html}
  {notes_section}
  {end_html}
  {online_html}
  <p style="margin:26px 0 0;text-align:center;font-size:13px;color:#a0a0a0;line-height:1.8;">
    每天 5 个词，日拱一卒<br/>坚持积累，静待花开
  </p>
</section>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", required=True, help="单词数据 JSON 文件路径")
    ap.add_argument("--lesson", default=None, help="情境、用法和练习 JSON；不传则沿用旧版五词格式")
    ap.add_argument("--update-media-id", default=None, help="更新已有草稿，避免重复建稿；不用于群发")
    ap.add_argument("--title", default=None)
    ap.add_argument("--digest", default="每天 5 个生活与职场高频实用词汇")
    ap.add_argument("--date", required=True, help="中文日期，如 2026年9月24日")
    ap.add_argument("--episode", required=True, help="期数")
    ap.add_argument("--online-url", default=None)
    ap.add_argument("--thumb", default=None, help="封面 thumb_media_id，默认用配置里的")
    ap.add_argument("--author", default="词汇拾光")
    ap.add_argument("--auto-cover", action="store_true", help="按当期内容自动生成封面图并上传使用")
    ap.add_argument("--publish", action="store_true", help="真正群发推送（不加则只建草稿）")
    args = ap.parse_args()

    cfg = load_cfg()
    with open(args.words, encoding="utf-8") as f:
        words = json.load(f)
    lesson = None
    if args.lesson:
        with open(args.lesson, encoding="utf-8") as f:
            lesson = json.load(f)
    if args.update_media_id and args.publish:
        ap.error("更新草稿时不能传 --publish")

    token = get_token(cfg["appid"], cfg["appsecret"])
    print("[1/3] access_token 获取成功")

    content = build_html(words, args.date, args.episode, args.online_url, lesson)
    title = args.title or (f'{lesson["title"]}｜第 {args.episode} 期' if lesson else f"每日 5 词 · 第 {args.episode} 期（{args.date}）")
    thumb = args.thumb or cfg.get("thumb_media_id")
    if args.update_media_id and not args.thumb:
        existing = http(f"{API}/draft/get?access_token={token}", {"media_id": args.update_media_id})
        old_articles = existing.get("news_item") or existing.get("articles") or []
        old_title = old_articles[0].get("title", "") if old_articles else ""
        if f"第 {args.episode} 期" not in old_title and f"第{args.episode}期" not in old_title:
            raise RuntimeError("目标草稿期数不匹配，停止更新")
        thumb = old_articles[0].get("thumb_media_id") or thumb
    if not thumb:
        raise RuntimeError("缺少封面 thumb_media_id")
    if args.auto_cover:
        try:
            cover = os.path.join(BASE, f"cover-ep{args.episode}.png")
            make_cover([w["word"] for w in words], args.episode, args.date, cover)
            print(f"      封面已生成: {cover}")
            up = upload_image(token, cover)
            if "media_id" in up:
                thumb = up["media_id"]
                print(f"      封面已上传素材库 media_id={thumb}")
            else:
                print("      封面上传失败，回退原封面:", json.dumps(up, ensure_ascii=False))
        except Exception as e:
            print(f"      封面生成失败({type(e).__name__}: {e})，回退原封面")

    article = {
        "articles": [{
            "title": title,
            "author": args.author,
            "digest": args.digest,
            "content": content,
            "content_source_url": args.online_url or "",
            "thumb_media_id": thumb,
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }]
    }

    if args.update_media_id:
        r = http(f"{API}/draft/update?access_token={token}", {
            "media_id": args.update_media_id,
            "index": 0,
            "articles": article["articles"][0],
        })
        if r.get("errcode") != 0:
            if r.get("errcode") == 53407:
                print("该草稿正在定时发布，微信不允许修改；请先在公众号后台处理定时状态。")
            print("更新草稿失败:", json.dumps(r, ensure_ascii=False))
            sys.exit(1)
        print(f"[2/3] 草稿更新成功 media_id={args.update_media_id}")
        print("[3/3] 仅更新草稿，未群发。")
        return

    r = http(f"{API}/draft/add?access_token={token}", article)
    if "media_id" not in r:
        print("创建草稿失败:", json.dumps(r, ensure_ascii=False))
        sys.exit(1)
    media_id = r["media_id"]
    print(f"[2/3] 草稿创建成功  media_id={media_id}")

    if not args.publish:
        print("\n[3/3] 未加 --publish，仅创建草稿。请到公众号后台「素材管理 → 草稿箱」预览确认后再发布。")
        print(f"      确认无误后重跑本命令并加 --publish 即可群发。")
        return

    r2 = http(f"{API}/freepublish/submit?access_token={token}", {"media_id": media_id})
    if r2.get("errcode") not in (0, None):
        print("发布失败:", json.dumps(r2, ensure_ascii=False))
        sys.exit(1)
    print(f"[3/3] 已发布群发成功！publish_id={r2.get('publish_id')}")


if __name__ == "__main__":
    main()
