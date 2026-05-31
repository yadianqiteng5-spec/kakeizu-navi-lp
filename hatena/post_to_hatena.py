# -*- coding: utf-8 -*-
"""
はてなブログ AtomPub 自動投稿スクリプト（ドリップ投稿・送客型）

- LP の全44記事から、はてな用「要約＋送客」記事を生成
- 未投稿のうち先頭1件を投稿し、posted.json に記録
- 重複コンテンツを避けるため全文転載はせず、要点＋「詳しくはLPへ」リンク構成

環境変数（GitHub Secrets 推奨）:
  HATENA_ID        : はてなID（例: taro123）
  HATENA_BLOG_ID   : ブログID（例: taro123.hatenablog.com）
  HATENA_API_KEY   : AtomPub APIキー
  POST_LIMIT       : 1回の実行で投稿する本数（既定 1）
  DRAFT            : "yes" で下書き投稿（テスト用）。既定 "no"

使い方:
  python post_to_hatena.py            # 実投稿
  python post_to_hatena.py --dry-run  # 投稿せずプレビュー出力
"""
import os, sys, json, base64, hashlib, secrets, datetime, html, time
import urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO))
import _generate as g  # noqa: E402

SITE = "https://yadianqiteng5-spec.github.io/kakeizu-navi-lp"
APP = "https://kakeizu-navi-3joa5l78sjkams2axwbxix.streamlit.app/"
POSTED = ROOT / "posted.json"


# ────────────────────────────────────────────────
# はてな用記事HTMLの生成（送客型・重複回避）
# ────────────────────────────────────────────────
def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


def first_paragraph(body):
    """セクション本文から最初の<p>または<li>のテキストを要約として取り出す。
    表だけのセクションはセル文字列が連結して読みにくいので避ける。"""
    import re
    m = re.search(r"<p>(.*?)</p>", body, re.DOTALL)
    if m:
        return strip_tags(m.group(1)).strip()
    m = re.search(r"<li>(.*?)</li>", body, re.DOTALL)
    if m:
        return strip_tags(m.group(1)).strip()
    # 表のみ等：要約を作らず空を返す
    return ""


def build_body(art):
    url = f"{SITE}/{art['slug']}/"
    # リード
    parts = [f"<p>{art['lead']}</p>"]
    # 要点（各セクション見出し＋本文を短く要約：先頭120字）
    parts.append("<h3>この記事のポイント</h3>")
    parts.append("<ul>")
    for h2, body in art["sections"][:4]:
        summary = first_paragraph(body).replace("\n", "")
        if summary:
            if len(summary) > 110:
                summary = summary[:110] + "…"
            parts.append(f"<li><strong>{h2}</strong>：{summary}</li>")
        else:
            # 表中心のセクションは見出しのみ提示（詳細はLPへ）
            parts.append(f"<li><strong>{h2}</strong>（詳しくは本文の早見表をご覧ください）</li>")
    parts.append("</ul>")
    # FAQ から1つ抜粋（独自性を足す）
    if art.get("faqs"):
        q, a = art["faqs"][0]
        parts.append("<h3>よくある質問</h3>")
        parts.append(f"<p><strong>Q. {q}</strong><br>A. {strip_tags(a)}</p>")
    # 送客（LP全文）
    parts.append(
        f'<p>📖 図解・早見表つきの詳しい解説はこちら → '
        f'<a href="{url}">{html.escape(art["h1"])}（家系図Navi）</a></p>'
    )
    # 送客（アプリ）
    parts.append(
        '<div style="border:2px solid #27AE60;border-radius:10px;padding:14px 18px;margin:18px 0;background:#f8fdf9;">'
        '<strong>🧮 あなたの家の相続税を無料で試算</strong><br>'
        '家族構成を入力するだけで、法定相続分・相続税・遺留分を自動計算（登録不要・完全無料・課金要素なし）。<br>'
        f'<a href="{APP}">家系図Navi を試す →</a></div>'
    )
    # 免責
    parts.append(
        '<p style="font-size:13px;color:#888;">※本記事は一般的な情報提供であり法的助言ではありません。'
        '個別事案は弁護士・税理士等の専門家にご相談ください。</p>'
    )
    return "\n".join(parts)


def categories(art):
    base = ["相続", "家系図Navi"]
    kw = [k.strip() for k in art.get("keywords", "").split(",")]
    # 主要キーワードを2つだけカテゴリに（多すぎるとスパム的）
    extra = [k for k in kw if k and k not in base][:2]
    return base + extra


# ────────────────────────────────────────────────
# AtomPub (WSSE認証) で投稿
# ────────────────────────────────────────────────
def wsse_header(hatena_id, api_key):
    nonce = secrets.token_bytes(20)
    created = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    digest = base64.b64encode(
        hashlib.sha1(nonce + created.encode() + api_key.encode()).digest()
    ).decode()
    b64nonce = base64.b64encode(nonce).decode()
    return (f'UsernameToken Username="{hatena_id}", '
            f'PasswordDigest="{digest}", '
            f'Nonce="{b64nonce}", Created="{created}"')


def build_entry_xml(title, body_html, cats, author, draft="no"):
    cat_xml = "\n".join(f'  <category term="{html.escape(c)}" />' for c in cats)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
  <title>{html.escape(title)}</title>
  <author><name>{html.escape(author)}</name></author>
  <content type="text/html">{html.escape(body_html)}</content>
{cat_xml}
  <app:control>
    <app:draft>{draft}</app:draft>
  </app:control>
</entry>"""


def post_entry(hatena_id, blog_id, api_key, xml, draft="no"):
    endpoint = f"https://blog.hatena.ne.jp/{hatena_id}/{blog_id}/atom/entry"
    req = urllib.request.Request(
        endpoint, data=xml.encode("utf-8"), method="POST",
        headers={
            "X-WSSE": wsse_header(hatena_id, api_key),
            "Content-Type": "application/xml; charset=utf-8",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.status, res.read().decode("utf-8", "replace")


# ────────────────────────────────────────────────
def load_posted():
    if POSTED.exists():
        return json.loads(POSTED.read_text(encoding="utf-8"))
    return {"posted": []}


def save_posted(data):
    POSTED.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    dry = "--dry-run" in sys.argv
    limit = int(os.environ.get("POST_LIMIT", "1"))
    draft = os.environ.get("DRAFT", "no")
    author = os.environ.get("HATENA_ID", "DrumNavi")

    state = load_posted()
    done = set(state["posted"])
    queue = [a for a in g.ARTICLES if a["slug"] not in done]

    if not queue:
        print("全記事を投稿済みです。キューは空です。")
        return

    targets = queue[:limit]
    print(f"未投稿 {len(queue)} 件 / 今回 {len(targets)} 件を処理")

    if dry:
        art = targets[0]
        body = build_body(art)
        xml = build_entry_xml(art["title"], body, categories(art), author, draft)
        print("=" * 60)
        print("【DRY-RUN プレビュー】次に投稿される記事")
        print("タイトル:", art["title"])
        print("カテゴリ:", categories(art))
        print("-" * 60, "本文HTML")
        print(body)
        print("-" * 60, "送信XML(先頭600字)")
        print(xml[:600])
        return

    hid = os.environ["HATENA_ID"]
    bid = os.environ["HATENA_BLOG_ID"]
    key = os.environ["HATENA_API_KEY"]

    for art in targets:
        body = build_body(art)
        xml = build_entry_xml(art["title"], body, categories(art), author, draft)
        try:
            status, resp = post_entry(hid, bid, key, xml, draft)
            if status in (200, 201):
                print(f"✅ 投稿成功: {art['slug']} / {art['title']}")
                state["posted"].append(art["slug"])
                save_posted(state)
            else:
                print(f"⚠️ 想定外ステータス {status}: {art['slug']}")
                print(resp[:300])
                sys.exit(1)
        except urllib.error.HTTPError as e:
            print(f"❌ HTTPエラー {e.code}: {art['slug']}")
            print(e.read().decode("utf-8", "replace")[:300])
            sys.exit(1)
        time.sleep(3)

    print(f"完了。累計投稿: {len(state['posted'])} / {len(g.ARTICLES)}")


if __name__ == "__main__":
    main()
