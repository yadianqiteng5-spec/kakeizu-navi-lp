"""記事ページ一括生成スクリプト。data 配列を編集して python _generate.py で再生成。"""
import os
import json
from pathlib import Path

ROOT = Path(__file__).parent
APP_URL = "https://kakeizu-navi-3joa5l78sjkams2axwbxix.streamlit.app/"
SITE_URL = "https://yadianqiteng5-spec.github.io/kakeizu-navi-lp"
# コンテンツの正規ドメイン(canonical)は本番 kakeizu.appsnavi.net。
# canonicalタグのみ CANONICAL_BASE を使い、再生成してもgithub.ioへ戻らないようにする。
CANONICAL_BASE = "https://kakeizu.appsnavi.net"
ICON = f"{SITE_URL}/icon_512.png"

# ── A8.net アフィリエイト広告（各ページ1枠） ─────────────────────────────
# 広告は ad_block() で中央寄せ＋「広告」ラベル付きで挿入する（景表法/ステマ規制配慮）
_A8_BANNER = (
    '<a href="https://px.a8.net/svt/ejp?a8mat=4B43JE+8V4T8A+5TEW+5YZ75" rel="nofollow sponsored" target="_blank">'
    '<img border="0" width="300" height="250" alt="相続・終活に関する広告" '
    'src="https://www21.a8.net/svt/bgt?aid=260531690536&wid=022&eno=01&mid=s00000027140001003000&mc=1"></a>'
    '<img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4B43JE+8V4T8A+5TEW+5YZ75" alt="">'
)


def ad_block():
    """中央寄せ・広告ラベル付きの広告ブロックHTMLを返す（300x250レクタングル）。"""
    return (
        '<div style="text-align:center;margin:2rem 0;">'
        '<div style="font-size:11px;color:#999;margin-bottom:4px;letter-spacing:1px;">広告</div>'
        f'{_A8_BANNER}'
        '</div>'
    )


# 横長バナー（640x120・記事上部向け／モバイルは縮小）
_A8_BANNER_WIDE = (
    '<a href="https://px.a8.net/svt/ejp?a8mat=4B43JI+BGLV7E+5N2A+60OXD" rel="nofollow sponsored" target="_blank">'
    '<img border="0" width="640" height="120" alt="相続・終活に関する広告" style="max-width:100%;height:auto;" '
    'src="https://www28.a8.net/svt/bgt?aid=260531694693&wid=022&eno=01&mid=s00000026317001011000&mc=1"></a>'
    '<img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=4B43JI+BGLV7E+5N2A+60OXD" alt="">'
)


def ad_block_wide():
    """中央寄せ・広告ラベル付きの横長広告ブロックHTMLを返す（640x120）。"""
    return (
        '<div style="text-align:center;margin:1.5rem 0;">'
        '<div style="font-size:11px;color:#999;margin-bottom:4px;letter-spacing:1px;">広告</div>'
        f'{_A8_BANNER_WIDE}'
        '</div>'
    )


# 税理士ドットコム（accesstrade・468x60・記事中盤向け／相続テーマと高親和性）
_AD_TAX = (
    '<a href="https://h.accesstrade.net/sp/cc?rk=0100npm700otmq" rel="nofollow sponsored" '
    'referrerpolicy="no-referrer-when-downgrade" target="_blank">'
    '<img src="https://h.accesstrade.net/sp/rr?rk=0100npm700otmq" alt="税理士ドットコム" '
    'border="0" width="468" height="60" style="max-width:100%;height:auto;"></a>'
)


def ad_block_tax():
    """中央寄せ・広告ラベル付きの税理士ドットコム広告ブロックHTMLを返す（468x60）。"""
    return (
        '<div style="text-align:center;margin:1.5rem 0;">'
        '<div style="font-size:11px;color:#999;margin-bottom:4px;letter-spacing:1px;">広告</div>'
        f'{_AD_TAX}'
        '</div>'
    )


# ── 本文中の文脈内部リンク（自動相互リンク）─────────────────────────────
# キーワード -> 記事slug。本文テキスト中の初出を関連記事へリンクする。
import re as _re_autolink

KEYWORD_LINKS = {
    "法定相続分": "legal-share",
    "基礎控除": "inheritance-tax",
    "配偶者の税額軽減": "inheritance-tax",
    "遺留分": "legal-reserve",
    "小規模宅地等の特例": "small-residential",
    "二次相続": "secondary-inheritance",
    "暦年贈与": "gift-strategy",
    "相続時精算課税": "gift-strategy",
    "教育資金": "education-gift",
    "家族信託": "family-trust",
    "配偶者居住権": "spouse-residence",
    "自筆証書遺言": "will-template",
    "公正証書遺言": "notarized-will",
    "遺言執行者": "will-executor",
    "相続放棄": "inheritance-renounce",
    "限定承認": "debt-inheritance",
    "遺産分割協議": "estate-division",
    "相続登記": "inheritance-procedure",
    "事業承継税制": "business-succession",
    "非上場株式": "corporate-shares",
    "名義預金": "nominee-deposit",
    "税務調査": "tax-investigation",
    "準確定申告": "estate-tax-return",
    "2割加算": "tax-surcharge",
    "数次相続": "consecutive-inheritance",
    "相次相続控除": "consecutive-inheritance",
    "遺族年金": "survivor-pension",
    "祭祀財産": "grave-succession",
    "相続欠格": "disinheritance",
    "相続廃除": "disinheritance",
    "死因贈与": "bequest-gift",
    "法定相続情報": "legal-heir-info",
    "借地権": "leasehold-inheritance",
    "小規模宅地": "small-residential",
    "配偶者の税額軽減": "spouse-tax-credit",
    "成年後見": "adult-guardianship",
    "任意後見": "voluntary-guardianship",
    "検認": "will-probate",
    "取得費加算": "sell-inherited-property",
    "障害者控除": "disability-minor-credit",
    "未成年者控除": "disability-minor-credit",
    "延滞税": "penalty-tax",
    "重加算税": "penalty-tax",
}

_AUTOLINK_MAX = 6  # 1記事あたりの自動リンク上限（過剰リンク防止）


def autolink(html, current_slug):
    """本文HTML中のキーワード初出を関連記事へリンクする。
    見出し(h1-6)・表(table)・既存リンク(a)・summary の内側はリンクしない。"""
    parts = _re_autolink.split(r'(<[^>]+>)', html)
    # 各テキスト片がリンク可能か（skip要素・aの外）を判定
    linkable = [False] * len(parts)
    depth_skip = 0
    a_depth = 0
    for i, p in enumerate(parts):
        if p.startswith('<'):
            low = p.lower()
            if low.startswith(('<h1', '<h2', '<h3', '<h4', '<h5', '<h6', '<table', '<summary')):
                depth_skip += 1
            elif low.startswith(('</h1', '</h2', '</h3', '</h4', '</h5', '</h6', '</table', '</summary')):
                depth_skip = max(0, depth_skip - 1)
            elif low.startswith('<a'):
                a_depth += 1
            elif low.startswith('</a'):
                a_depth = max(0, a_depth - 1)
        else:
            linkable[i] = (depth_skip == 0 and a_depth == 0)

    used = set()
    count = 0
    for kw in sorted(KEYWORD_LINKS.keys(), key=len, reverse=True):
        if count >= _AUTOLINK_MAX:
            break
        target = KEYWORD_LINKS[kw]
        if target == current_slug or target in used:
            continue
        for i, p in enumerate(parts):
            if not linkable[i]:
                continue
            idx = p.find(kw)
            if idx != -1:
                link = f'<a href="../{target}/" style="color:#16A085;">{kw}</a>'
                parts[i] = p[:idx] + link + p[idx + len(kw):]
                linkable[i] = False  # その片はこれ以上リンクしない（過剰防止）
                used.add(target)
                count += 1
                break
    return ''.join(parts)

ARTICLES = [
    {
        "slug": "legal-share",
        "title": "法定相続分とは？早見表と計算方法をわかりやすく解説",
        "h1": "法定相続分の早見表と計算方法",
        "desc": "民法900条で定められた法定相続分を、配偶者・子・直系尊属・兄弟姉妹のケース別に早見表で解説。代襲相続・半血兄弟・養子の扱いも図解で詳しく説明します。",
        "keywords": "法定相続分,早見表,民法900条,代襲相続,配偶者相続分,子供相続分",
        "lead": "<strong>法定相続分</strong>とは、民法900条で定められた相続人ごとの相続割合のことです。遺言書がない場合、この割合に従って遺産が分けられます。本記事では基本ルールから複雑なケースまで、早見表と図解でわかりやすく解説します。",
        "sections": [
            ("基本の早見表（民法900条）", """
<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
  <thead><tr style="background:#27AE60;color:white;"><th style="padding:.6rem;border:1px solid #ddd;">相続人の組み合わせ</th><th style="padding:.6rem;border:1px solid #ddd;">配偶者</th><th style="padding:.6rem;border:1px solid #ddd;">他の相続人</th></tr></thead>
  <tbody>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">配偶者 + 子</td><td style="padding:.6rem;border:1px solid #ddd;">1/2</td><td style="padding:.6rem;border:1px solid #ddd;">1/2（人数で按分）</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">配偶者 + 直系尊属（親）</td><td style="padding:.6rem;border:1px solid #ddd;">2/3</td><td style="padding:.6rem;border:1px solid #ddd;">1/3（人数で按分）</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">配偶者 + 兄弟姉妹</td><td style="padding:.6rem;border:1px solid #ddd;">3/4</td><td style="padding:.6rem;border:1px solid #ddd;">1/4（人数で按分）</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">配偶者のみ</td><td style="padding:.6rem;border:1px solid #ddd;">全部</td><td style="padding:.6rem;border:1px solid #ddd;">—</td></tr>
  </tbody>
</table>
<p>配偶者は常に相続人になり、第1順位（子）→第2順位（直系尊属）→第3順位（兄弟姉妹）の順で組み合わせが決まります。</p>
"""),
            ("計算例：配偶者と子2人のケース", "<p>遺産が6,000万円、相続人が配偶者と子2人の場合：</p><ul><li><strong>配偶者</strong>：6,000万円 × 1/2 = <strong>3,000万円</strong></li><li><strong>子A</strong>：6,000万円 × 1/2 × 1/2 = <strong>1,500万円</strong></li><li><strong>子B</strong>：6,000万円 × 1/2 × 1/2 = <strong>1,500万円</strong></li></ul>"),
            ("代襲相続が発生するケース", "<p>相続人が被相続人より先に亡くなっている場合、その子が代わりに相続します（民法887条2項）。これを<strong>代襲相続</strong>といいます。</p><ul><li><strong>子の死亡</strong>→ 孫が代襲（無限代襲）</li><li><strong>兄弟姉妹の死亡</strong>→ 甥姪が代襲（一代限り）</li><li><strong>相続放棄者の子</strong>は代襲しません（民法939条）</li></ul>"),
            ("半血兄弟・養子の取り扱い", "<p><strong>半血兄弟</strong>（親の片方のみ同じ兄弟）の相続分は、全血兄弟の<strong>1/2</strong>です（民法900条4号但書）。</p><p><strong>普通養子</strong>は実親・養親の双方から相続できますが、<strong>特別養子</strong>は実親との親族関係が終了するため養親からのみ相続します（民法817条の9）。</p>"),
        ],
        "faqs": [
            ("法定相続分は必ず守らないといけませんか？", "いいえ、相続人全員が同意すれば、法定相続分とは異なる分割（遺産分割協議）が可能です。法定相続分はあくまで合意できなかった場合の基準です。"),
            ("内縁の妻に相続権はありますか？", "民法上の配偶者ではないため、内縁の妻に法定相続分はありません。生前贈与や遺言書、特別縁故者の制度などで対応が必要です。"),
            ("胎児に相続権はありますか？", "あります。民法886条により、胎児は相続については既に生まれたものとみなされます（死産の場合を除く）。"),
        ],
    },
    {
        "slug": "inheritance-tax",
        "title": "相続税の基礎控除と計算方法｜2026年最新の早見表",
        "h1": "相続税の基礎控除と概算計算",
        "desc": "相続税の基礎控除「3,000万円+600万円×法定相続人数」の仕組みと、国税庁速算表を使った概算計算方法を、具体例とともに解説します。",
        "keywords": "相続税,基礎控除,相続税計算,速算表,相続税早見表,2026相続税",
        "lead": "<strong>相続税</strong>は遺産総額が基礎控除を超えた場合にのみ発生します。本記事では基礎控除の計算式、税率表、配偶者控除など主要な節税ポイントを解説します。",
        "sections": [
            ("基礎控除の計算式", "<p><strong>基礎控除 = 3,000万円 + 600万円 × 法定相続人の数</strong>（相続税法15条）</p><ul><li>相続人1人：3,600万円</li><li>相続人2人：4,200万円</li><li>相続人3人：4,800万円</li><li>相続人4人：5,400万円</li></ul><p>遺産総額がこの金額以下なら、相続税はかかりません。</p>"),
            ("相続税の速算表（国税庁公表）", """
<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
  <thead><tr style="background:#27AE60;color:white;"><th style="padding:.6rem;border:1px solid #ddd;">取得金額</th><th style="padding:.6rem;border:1px solid #ddd;">税率</th><th style="padding:.6rem;border:1px solid #ddd;">控除額</th></tr></thead>
  <tbody>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">〜1,000万円</td><td style="padding:.6rem;border:1px solid #ddd;">10%</td><td style="padding:.6rem;border:1px solid #ddd;">—</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">〜3,000万円</td><td style="padding:.6rem;border:1px solid #ddd;">15%</td><td style="padding:.6rem;border:1px solid #ddd;">50万円</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">〜5,000万円</td><td style="padding:.6rem;border:1px solid #ddd;">20%</td><td style="padding:.6rem;border:1px solid #ddd;">200万円</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">〜1億円</td><td style="padding:.6rem;border:1px solid #ddd;">30%</td><td style="padding:.6rem;border:1px solid #ddd;">700万円</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">〜2億円</td><td style="padding:.6rem;border:1px solid #ddd;">40%</td><td style="padding:.6rem;border:1px solid #ddd;">1,700万円</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">〜3億円</td><td style="padding:.6rem;border:1px solid #ddd;">45%</td><td style="padding:.6rem;border:1px solid #ddd;">2,700万円</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">〜6億円</td><td style="padding:.6rem;border:1px solid #ddd;">50%</td><td style="padding:.6rem;border:1px solid #ddd;">4,200万円</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">6億円超</td><td style="padding:.6rem;border:1px solid #ddd;">55%</td><td style="padding:.6rem;border:1px solid #ddd;">7,200万円</td></tr>
  </tbody>
</table>
"""),
            ("計算例：遺産1億円・配偶者+子2人", "<p>① 基礎控除：3,000万円 + 600万円×3 = 4,800万円<br>② 課税遺産：1億円 − 4,800万円 = 5,200万円<br>③ 法定相続分で按分：配偶者2,600万円／子1,300万円×2<br>④ 速算表で各人の税額算出 → 合計 <strong>630万円</strong>（配偶者控除前）<br>⑤ 配偶者控除適用後の実効税額：<strong>315万円</strong></p>"),
            ("配偶者控除（最大1.6億円）", "<p>配偶者は<strong>法定相続分または1億6,000万円</strong>のいずれか大きい方まで相続税が非課税です（相続税法19条の2）。ただし二次相続まで考えると、必ずしも配偶者に集中させるのが得策とは限りません。"),
            ("生命保険の非課税枠", "<p>死亡保険金は<strong>500万円 × 法定相続人数</strong>まで非課税です（相続税法12条）。例えば相続人3人なら1,500万円まで非課税。預貯金で残すより節税効果があります。"),
        ],
        "faqs": [
            ("申告期限はいつまでですか？", "被相続人が亡くなったことを知った日の翌日から<strong>10ヶ月以内</strong>に税務署へ申告・納付する必要があります。期限を過ぎると延滞税・加算税がかかります。"),
            ("相続放棄した人も基礎控除の人数に入りますか？", "はい、入ります。基礎控除の「法定相続人数」は放棄者を含めて数えます（相続税法15条）。これは節税策として放棄を悪用させないための規定です。"),
            ("養子は何人まで人数に算入できますか？", "実子がいる場合は<strong>1人まで</strong>、実子がいない場合は<strong>2人まで</strong>です（相続税法15条2項）。基礎控除や生命保険非課税枠の計算で適用されます。"),
        ],
    },
    {
        "slug": "business-succession",
        "title": "事業承継のリスクと対策｜自社株分散を防ぐ方法",
        "h1": "事業承継のリスクと対策",
        "desc": "中小企業オーナーの相続で頻発する自社株の分散・経営権喪失リスクを解説。納税猶予制度・属人株・信託など実務で使われる対策を網羅します。",
        "keywords": "事業承継,自社株,相続,経営権,事業承継税制,納税猶予,属人株",
        "lead": "中小企業オーナーの相続では、<strong>自社株の分散</strong>が最大のリスクです。複数の相続人に株式が散らばると経営権が不安定になり、最悪の場合は会社が機能不全に陥ります。本記事では主要なリスクと対策を整理します。",
        "sections": [
            ("リスク1：自社株の分散", "<p>後継者以外の相続人にも自社株が法定相続分で渡ると、議決権が分散します。<strong>2/3以上の議決権</strong>を後継者が確保できないと、定款変更・組織再編などの重要決議ができなくなります。</p>"),
            ("リスク2：相続税による株式売却", "<p>非上場株式は換金性が低いにも関わらず、相続税評価額は高くなりがちです。納税資金確保のため自社株や事業用資産を売却せざるを得ないケースが多発しています。</p>"),
            ("対策1：事業承継税制（納税猶予）", "<p>一定要件を満たせば、自社株に対する相続税・贈与税の<strong>100%が猶予・免除</strong>される制度（円滑化法）。後継者が事業継続することが条件で、適用範囲は段階的に拡大されています。</p>"),
            ("対策2：属人株・種類株式の活用", "<p>会社法108条の<strong>種類株式</strong>や109条の<strong>属人株</strong>を活用すれば、議決権を後継者に集約しつつ、他の相続人には配当優先株を渡すなど柔軟な設計が可能です。"),
            ("対策3：民事信託（家族信託）", "<p>議決権行使を信託契約で後継者に集中させながら、経済的利益は他の相続人に分配する設計が可能です。遺留分対応にも有効。"),
        ],
        "faqs": [
            ("事業承継税制を使うデメリットは？", "5年間の事業継続要件・雇用維持要件など縛りが多く、途中で打切ると猶予税額に利子税がかかります。専門家の継続サポートが必須です。"),
            ("後継者がいない場合はどうすべきですか？", "M&A（第三者承継）が現実的な選択肢です。早期に事業承継・引継ぎ支援センター等に相談し、企業価値を高めてからの売却を検討します。"),
            ("生前贈与で自社株を渡せますか？", "可能です。<strong>相続時精算課税制度</strong>を使えば2,500万円まで贈与税ゼロで移転できます。事業承継税制（贈与版）との併用も検討できます。"),
        ],
    },
    {
        "slug": "will-template",
        "title": "自筆証書遺言の書き方｜雛形・必須要件・法務局保管制度",
        "h1": "自筆証書遺言の書き方と雛形",
        "desc": "民法968条に準拠した自筆証書遺言の書き方を、雛形付きで解説。法務局保管制度・財産目録のパソコン作成可能化など2019年改正対応。",
        "keywords": "自筆証書遺言,書き方,雛形,民法968条,法務局保管制度,遺言書",
        "lead": "<strong>自筆証書遺言</strong>は、自分一人で作成できる最も手軽な遺言書です。ただし民法968条の要件を満たさないと無効になります。本記事では雛形と注意点を解説します。",
        "sections": [
            ("自筆証書遺言の必須要件", "<ul><li><strong>全文・日付・氏名を自書</strong>（パソコン・代筆は無効）</li><li><strong>押印</strong>が必要（認印で可、実印推奨）</li><li>加除訂正は変更場所を指示し、付記して署名押印</li><li>財産目録は2019年改正により<strong>パソコン作成可</strong>（各ページに署名押印）</li></ul>"),
            ("雛形テンプレート", """<pre style="background:#f4f4f4;padding:1rem;border-radius:6px;font-size:.85rem;overflow-x:auto;">
遺言書

遺言者 ○○○○ は、本遺言書により次のとおり遺言する。

第1条（財産の特定と承継）
  遺言者は、下記の財産を妻 △△△△ に相続させる。
  記
  1. 不動産：東京都○○区○○1-2-3 宅地150㎡
  2. 預貯金：○○銀行○○支店 普通預金 No.1234567

第2条（その他の財産）
  遺言者は、その他一切の財産を長男 ×××× に相続させる。

第3条（遺言執行者の指定）
  遺言者は、本遺言の遺言執行者として次の者を指定する。
  住所: 東京都○○区○○4-5-6
  氏名: □□□□

第4条（付言事項）
  家族へのメッセージ（任意）

令和○年○月○日

  住所: 東京都○○区○○1-2-3
  氏名: ○○○○                印
</pre>"""),
            ("法務局保管制度（推奨）", "<p>2020年7月開始の<strong>遺言書保管制度</strong>を使えば、全国の遺言書保管所で<strong>3,900円</strong>で原本を保管できます。メリットは：</p><ul><li>紛失・偽造リスクを回避</li><li>家庭裁判所の<strong>検認手続きが不要</strong></li><li>遺言者の死亡時に指定通知人へ自動連絡</li></ul>"),
            ("無効になりやすいパターン", "<ul><li>日付が「令和○年○月吉日」（特定不可で無効）</li><li>夫婦連名の遺言（共同遺言の禁止・民法975条）</li><li>遺留分を無視した極端な配分（遺留分侵害額請求の対象）</li><li>財産の特定が曖昧（「自宅」だけでは不十分、地番まで記載）</li></ul>"),
        ],
        "faqs": [
            ("公正証書遺言との違いは何ですか？", "公正証書遺言は公証人が作成する公文書で、無効リスクがほぼなく検認不要ですが、費用（数万円〜）と証人2名が必要です。資産規模や紛争リスクに応じて選択します。"),
            ("動画・録音で遺言を残せますか？", "民法上、有効な遺言形式は<strong>書面のみ</strong>です。動画・録音は法的効力を持ちません（付言として家族メッセージを残すのは可）。"),
            ("遺留分を無視した遺言は有効ですか？", "有効ですが、遺留分権利者から<strong>遺留分侵害額請求</strong>を受ける可能性があります（民法1046条）。請求を回避するには遺留分を考慮した配分が望ましいです。"),
        ],
    },
    {
        "slug": "legal-reserve",
        "title": "遺留分とは？計算方法と侵害額請求の流れ",
        "h1": "遺留分の計算方法と請求の流れ",
        "desc": "民法1042条で保証された遺留分（最低保証分）の計算方法、配偶者・子・直系尊属の割合、侵害額請求の手続きと時効を解説します。",
        "keywords": "遺留分,民法1042条,遺留分侵害額請求,遺留分計算,相続",
        "lead": "<strong>遺留分</strong>とは、一定の相続人に法律上保証された最低限の取り分です（民法1042条）。遺言で「全財産を長男に」とあっても、配偶者や他の子は遺留分を請求できます。",
        "sections": [
            ("遺留分の総体的割合", "<ul><li>直系尊属のみが相続人 → 遺産の<strong>1/3</strong></li><li>それ以外（配偶者・子がいる場合） → 遺産の<strong>1/2</strong></li><li>兄弟姉妹 → <strong>遺留分なし</strong></li></ul><p>これに各人の法定相続分を掛けたものが「個別的遺留分」です。</p>"),
            ("計算例：配偶者+子2人で遺産1億円", "<p>① 総体的遺留分：1億円 × 1/2 = 5,000万円<br>② 配偶者の個別遺留分：5,000万円 × 1/2 = <strong>2,500万円</strong><br>③ 子1人あたりの個別遺留分：5,000万円 × 1/4 = <strong>1,250万円</strong></p>"),
            ("遺留分侵害額請求の手続き", "<p>2019年改正により、現物返還ではなく<strong>金銭請求権</strong>になりました（民法1046条）。流れは：</p><ol><li>請求の意思表示（内容証明郵便が一般的）</li><li>当事者間での協議</li><li>不調なら家庭裁判所での調停</li><li>調停不成立なら訴訟</li></ol>"),
            ("時効に注意（1年・10年）", "<p>遺留分侵害を知った時から<strong>1年</strong>、または相続開始から<strong>10年</strong>で時効消滅します（民法1048条）。早期に内容証明郵便で意思表示することが重要です。</p>"),
        ],
        "faqs": [
            ("遺留分は放棄できますか？", "相続開始後は自由に放棄可能。相続開始前の放棄は家庭裁判所の許可が必要です（民法1049条）。事業承継対策で後継者以外の遺留分を事前放棄する例があります。"),
            ("生前贈与は遺留分の計算に含まれますか？", "原則として<strong>相続開始前10年以内</strong>の特別受益（民法903条の生前贈与）は遺留分算定基礎に算入されます（民法1044条）。ただし当事者双方が遺留分侵害を知っていた贈与は期間制限なし。"),
            ("遺留分を侵害する遺言は無効ですか？", "無効ではありません。あくまで請求されたら侵害額を支払う義務が生じる、という構造です。請求されなければ遺言通り執行されます。"),
        ],
    },
    {
        "slug": "special-adoption",
        "title": "特別養子縁組と相続｜実親との関係はどうなる？",
        "h1": "特別養子縁組と相続関係",
        "desc": "特別養子と普通養子の違い、相続権の有無、民法817条の9による実親との親族関係終了の効果をわかりやすく解説します。",
        "keywords": "特別養子,普通養子,養子相続,民法817条の9,養子縁組",
        "lead": "養子縁組には「<strong>普通養子</strong>」と「<strong>特別養子</strong>」の2種類があり、相続関係の扱いが大きく異なります。本記事ではその違いと実務上の注意点を解説します。",
        "sections": [
            ("特別養子縁組の特徴", "<p>子の福祉のために設けられた制度で、<strong>実親との親族関係が完全に終了</strong>します（民法817条の9）。要件：</p><ul><li>原則15歳未満の子</li><li>養親は配偶者ある25歳以上</li><li>家庭裁判所の審判による成立</li><li>原則6ヶ月以上の試験養育期間</li></ul>"),
            ("相続関係の違い", """
<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
  <thead><tr style="background:#27AE60;color:white;"><th style="padding:.6rem;border:1px solid #ddd;">区分</th><th style="padding:.6rem;border:1px solid #ddd;">実親からの相続</th><th style="padding:.6rem;border:1px solid #ddd;">養親からの相続</th></tr></thead>
  <tbody>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">普通養子</td><td style="padding:.6rem;border:1px solid #ddd;">○ 可能</td><td style="padding:.6rem;border:1px solid #ddd;">○ 可能</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">特別養子</td><td style="padding:.6rem;border:1px solid #ddd;">✕ 不可</td><td style="padding:.6rem;border:1px solid #ddd;">○ 可能</td></tr>
  </tbody>
</table>
"""),
            ("基礎控除での養子算入制限", "<p>相続税の基礎控除や生命保険非課税枠の計算では、養子の人数に制限があります（相続税法15条2項）：</p><ul><li>実子がいる場合：養子1人まで</li><li>実子がいない場合：養子2人まで</li></ul><p>ただし特別養子は<strong>実子と同じ扱い</strong>でこの制限を受けません。</p>"),
        ],
        "faqs": [
            ("特別養子は実親の遺産を相続できますか？", "原則として相続できません。民法817条の9により、特別養子縁組成立で実親との親族関係（親権・扶養・相続権など）はすべて終了します。"),
            ("特別養子が成立した後で実親が亡くなったら？", "特別養子は実親の相続人にはなりません。実親に他の子や配偶者がいなければ、相続人不存在となり相続財産は最終的に国庫に帰属します。"),
            ("養子縁組で節税効果はありますか？", "あります。法定相続人数が増えるため基礎控除（600万円/人）・生命保険非課税枠（500万円/人）・退職金非課税枠が拡大します。ただし上記の人数制限あり。"),
        ],
    },
    {
        "slug": "secondary-inheritance",
        "title": "二次相続シミュレーション｜配偶者控除の落とし穴",
        "h1": "二次相続を見据えた相続税シミュレーション",
        "desc": "配偶者控除（1.6億円）を最大限活用すると二次相続で大増税になる落とし穴を、配偶者取得0%/50%/100%の比較で解説。",
        "keywords": "二次相続,配偶者控除,相続税シミュレーション,一次相続,節税",
        "lead": "<strong>二次相続</strong>とは、配偶者が亡くなった時の相続を指します。一次相続で配偶者控除を最大活用しても、二次相続で配偶者控除が使えず増税となり、合計税額がかえって増える「配偶者控除の落とし穴」を解説します。",
        "sections": [
            ("なぜ配偶者控除が落とし穴になるか", "<p>配偶者は法定相続分または1.6億円まで相続税ゼロです。しかし配偶者に多く相続させると、その財産が配偶者の元々の資産と合算され、二次相続時の課税遺産が膨らみます。さらに：</p><ul><li>配偶者控除は二次相続では使えない</li><li>相続人が1人減るため基礎控除も減る</li><li>税率の累進性で高税率帯に突入</li></ul>"),
            ("シミュレーション例：遺産2億円・子2人", "<p>配偶者固有資産5,000万円とした場合の一次＋二次合計税額：</p><ul><li>配偶者100%取得：一次0円 + 二次<strong>約6,930万円</strong></li><li>配偶者50%取得：一次1,350万円 + 二次約1,840万円 = <strong>約3,190万円</strong></li><li>配偶者0%取得：一次2,700万円 + 二次約470万円 = <strong>約3,170万円</strong></li></ul><p>配偶者控除をフル活用するパターンが<strong>2倍以上の税額</strong>になる典型例です。</p>"),
            ("最適配分の考え方", "<p>一般に配偶者取得は<strong>30〜50%</strong>程度に抑えるのが税額最小化の目安です。ただし以下も考慮：</p><ul><li>配偶者の生活資金確保</li><li>配偶者居住権の活用（民法1028条）</li><li>配偶者の年齢・余命</li><li>二次相続までの資産変動見込み</li></ul>"),
        ],
        "faqs": [
            ("配偶者居住権は使うべきですか？", "配偶者の生活権を確保しつつ、不動産所有権を子に移して二次相続の課税対象から外せるため、節税と生活保障を両立できる有力な選択肢です。"),
            ("二次相続を考えて配偶者の取得を減らしすぎるリスクは？", "配偶者の生活費が不足する、認知症等で財産管理が困難になるなどのリスクがあります。家族信託や生命保険も組み合わせた総合設計が必要です。"),
            ("二次相続まで何年あれば安全ですか？", "明確な目安はありませんが、配偶者が高齢の場合は二次相続が早期に発生する前提でのシミュレーションが重要です。"),
        ],
    },
    {
        "slug": "small-residential",
        "title": "小規模宅地等の特例｜居住用80%減で相続税を圧縮",
        "h1": "小規模宅地等の特例の使い方",
        "desc": "自宅の土地評価額を80%減額できる小規模宅地等の特例（租税特別措置法69条の4）の要件・面積上限・併用ルールを解説します。",
        "keywords": "小規模宅地等の特例,租税特別措置法69条の4,居住用宅地,事業用宅地,貸付事業用",
        "lead": "<strong>小規模宅地等の特例</strong>は、自宅や事業用の土地評価額を最大80%減額できる強力な節税制度です（租税特別措置法69条の4）。",
        "sections": [
            ("3つの区分と限度面積", """
<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
  <thead><tr style="background:#27AE60;color:white;"><th style="padding:.6rem;border:1px solid #ddd;">区分</th><th style="padding:.6rem;border:1px solid #ddd;">減額率</th><th style="padding:.6rem;border:1px solid #ddd;">限度面積</th></tr></thead>
  <tbody>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">特定居住用宅地（自宅）</td><td style="padding:.6rem;border:1px solid #ddd;">80%</td><td style="padding:.6rem;border:1px solid #ddd;">330㎡</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">特定事業用宅地（事業所）</td><td style="padding:.6rem;border:1px solid #ddd;">80%</td><td style="padding:.6rem;border:1px solid #ddd;">400㎡</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">貸付事業用宅地</td><td style="padding:.6rem;border:1px solid #ddd;">50%</td><td style="padding:.6rem;border:1px solid #ddd;">200㎡</td></tr>
  </tbody>
</table>
"""),
            ("適用要件（居住用）", "<p>配偶者が取得する場合は無条件。それ以外の親族が取得する場合の主な要件：</p><ul><li>同居親族：被相続人と同居しており、相続後も継続して居住・所有</li><li>家なき子特例：被相続人に配偶者・同居親族がおらず、自身も3年以上自己所有家屋に住んでいない</li></ul>"),
            ("計算例：土地評価8,000万円・自宅", "<p>① 通常評価：8,000万円<br>② 特例適用後：8,000万円 × (1 − 0.80) = <strong>1,600万円</strong><br>③ <strong>6,400万円の評価減</strong> → 相続税軽減効果は<strong>数千万円</strong>規模になることも。</p>"),
            ("注意点：申告期限までの保有・居住", "<p>多くの区分で、申告期限（相続開始から10ヶ月）まで保有・居住・事業継続が要件です。途中で売却すると特例適用不可となるため、遺産分割協議は慎重に。</p>"),
        ],
        "faqs": [
            ("二世帯住宅でも特例は使えますか？", "区分所有登記がされていなければ、構造上独立していても同居とみなされ特例適用可能です（2014年改正）。区分所有登記の場合は被相続人居住部分のみ対象。"),
            ("複数の区分を併用できますか？", "居住用と事業用の併用は限度面積を合算できますが、貸付事業用との併用は調整計算（按分）が必要です。"),
            ("申告不要の場合でも特例適用には申告が必要ですか？", "はい、特例適用には<strong>相続税申告が必須</strong>です。特例適用の結果ゼロ円になる場合でも申告書を提出する必要があります。"),
        ],
    },
    {
        "slug": "gift-strategy",
        "title": "生前贈与の節税戦略｜暦年贈与vs相続時精算課税",
        "h1": "生前贈与の節税戦略",
        "desc": "暦年贈与（年110万円非課税）と相続時精算課税（2,500万円非課税）の比較、2024年改正の7年持戻しを踏まえた最適な使い分けを解説。",
        "keywords": "生前贈与,暦年贈与,相続時精算課税,110万円,7年持戻し,贈与税",
        "lead": "<strong>生前贈与</strong>は計画的に行えば大きな節税効果があります。本記事では2024年改正後の暦年贈与と相続時精算課税の使い分けを解説します。",
        "sections": [
            ("暦年贈与の基本", "<p>受贈者1人あたり<strong>年110万円</strong>まで贈与税非課税（相続税法21条の5）。子3人・孫3人に毎年110万円ずつ10年贈与すれば6,600万円を非課税で移転できます。</p>"),
            ("2024年改正：7年持戻しの影響", "<p>改正前は相続開始前<strong>3年</strong>以内の贈与が相続財産に持ち戻されていましたが、改正後は<strong>7年</strong>に延長されました（経過措置あり、完全施行は2031年）。</p><ul><li>持戻し期間が長いほど節税効果は減る</li><li>高齢者は早期着手が有利</li><li>4〜7年目の超過分は100万円控除あり</li></ul>"),
            ("相続時精算課税制度", "<p>原則18歳以上の子・孫への贈与で、累計<strong>2,500万円</strong>まで贈与税ゼロ。超過分は一律20%。ただし相続時に全額を持戻して相続税で精算（相続税法21条の9以下）。</p><p>2024年改正で<strong>年110万円の基礎控除</strong>が新設され使い勝手が向上しました。</p>"),
            ("どちらを選ぶべきか", """
<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
  <thead><tr style="background:#27AE60;color:white;"><th style="padding:.6rem;border:1px solid #ddd;">条件</th><th style="padding:.6rem;border:1px solid #ddd;">おすすめ</th></tr></thead>
  <tbody>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">若い・長期で贈与可能</td><td style="padding:.6rem;border:1px solid #ddd;">暦年贈与</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">高齢・短期で大型移転</td><td style="padding:.6rem;border:1px solid #ddd;">相続時精算課税</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">値上がり確実な資産（自社株等）</td><td style="padding:.6rem;border:1px solid #ddd;">相続時精算課税</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">将来も金額調整したい</td><td style="padding:.6rem;border:1px solid #ddd;">暦年贈与</td></tr>
  </tbody>
</table>
"""),
        ],
        "faqs": [
            ("暦年贈与で「定期贈与」と認定されるリスクは？", "毎年同額・同日に贈与契約書なしで贈与すると、最初から総額を分割贈与する約束だったと認定され、総額に贈与税がかかるリスクがあります。毎年贈与契約書を作成しましょう。"),
            ("孫への贈与で持戻しは適用されますか？", "孫が相続人や遺贈受取人でなければ、原則持戻しの対象外です。ただし代襲相続人になっている場合は持戻し対象。"),
            ("教育資金・結婚資金の一括贈与特例は？", "別途、教育資金1,500万円・結婚子育て資金1,000万円の一括贈与非課税制度があります。期限・要件があるため最新情報の確認を。"),
        ],
    },
]


ARTICLES += [
    {
        "slug": "inheritance-renounce",
        "title": "相続放棄の方法と期限｜3ヶ月以内の家庭裁判所手続き",
        "h1": "相続放棄の方法と期限",
        "desc": "相続放棄は相続開始を知った日から3ヶ月以内に家庭裁判所への申述が必要。手続きの流れ、必要書類、代襲不発生・撤回不可など重要ルールを解説。",
        "keywords": "相続放棄,3ヶ月,家庭裁判所,熟慮期間,限定承認,代襲相続",
        "lead": "借金が多い、相続トラブルを避けたい等の場合、<strong>相続放棄</strong>で相続人の地位を放棄できます（民法939条）。ただし期限と要件が厳格です。",
        "sections": [
            ("3ヶ月の熟慮期間", "<p>相続放棄は<strong>相続開始を知った日から3ヶ月以内</strong>に家庭裁判所へ申述する必要があります（民法915条）。期間内に判断できない場合は<strong>期間伸長の申立て</strong>が可能。</p>"),
            ("手続きの流れ", "<ol><li>被相続人の最後の住所地を管轄する家庭裁判所を確認</li><li>申述書・戸籍謄本・住民票除票等を準備</li><li>収入印紙800円＋郵便切手を添付して申述</li><li>家庭裁判所からの照会書に回答</li><li>受理通知書が届く</li></ol>"),
            ("代襲は発生しない", "<p>相続放棄者の子は<strong>代襲相続しません</strong>（民法939条）。これは死亡や欠格による代襲との大きな違いです。次順位の相続人に権利が移ります。</p>"),
            ("放棄の撤回はできない", "<p>家庭裁判所が受理した相続放棄は<strong>原則撤回不可</strong>です（民法919条）。詐欺・強迫等の例外を除き取消しできないため、慎重な判断が必要。</p>"),
            ("限定承認という選択肢", "<p>プラス財産の範囲でマイナス財産を引き受ける<strong>限定承認</strong>もあります（民法922条）。ただし相続人全員での申述が必要で、税務上のみなし譲渡課税にも注意。</p>"),
        ],
        "faqs": [
            ("形見分けを受け取ると放棄できなくなりますか？", "経済的価値のある財産を処分・消費すると<strong>単純承認とみなされ放棄不可</strong>になります（民法921条）。形見分け程度の常識的な範囲なら問題ないとされますが、慎重を期すなら避けるべきです。"),
            ("全員が放棄したらどうなりますか？", "法定相続人全員が放棄すると、最終的に相続財産は<strong>国庫に帰属</strong>します（民法959条）。ただしその前に相続財産管理人選任の手続きが必要で、申立費用と予納金が必要です。"),
            ("3ヶ月を過ぎたら絶対に放棄できませんか？", "債務を知らなかった等の事情があれば、<strong>知った時から3ヶ月以内</strong>とする例外運用が判例上認められています（最判昭59.4.27）。専門家への早急な相談を推奨。"),
        ],
    },
    {
        "slug": "post-death-timeline",
        "title": "死後手続きタイムライン｜7日以内〜10ヶ月以内の全手続き",
        "h1": "死後手続きの完全タイムライン",
        "desc": "死亡届の7日以内提出から相続税申告の10ヶ月以内まで、期限ごとに必要な手続きを時系列でまとめた完全ガイド。",
        "keywords": "死後手続き,死亡届,相続手続き,スケジュール,7日以内,10ヶ月以内",
        "lead": "親族が亡くなった後、期限の決まった手続きが続きます。期限を逃すと不利益や追加費用が発生するため、本記事の<strong>タイムライン</strong>に沿って漏れなく対応しましょう。",
        "sections": [
            ("7日以内：死亡届の提出", "<ul><li>死亡診断書を医師から受け取る</li><li>死亡届を市区町村役場へ提出</li><li>火葬許可証を受領</li><li>葬儀・埋葬の手配</li></ul>"),
            ("14日以内：年金・健康保険の手続き", "<ul><li>年金受給権者死亡届（厚生年金10日以内、国民年金14日以内）</li><li>健康保険の資格喪失届</li><li>世帯主変更届（同一世帯に新世帯主候補がいる場合）</li><li>介護保険資格喪失届</li></ul>"),
            ("3ヶ月以内：相続放棄の判断", "<ul><li>遺言書の有無確認（自筆証書は検認）</li><li>法定相続人の確定（戸籍収集）</li><li>財産・負債の概要把握</li><li>相続放棄・限定承認の判断と申述</li></ul>"),
            ("4ヶ月以内：所得税準確定申告", "<p>被相続人の<strong>準確定申告</strong>を相続人全員で行います（所得税法125条）。1月1日から死亡日までの所得を申告。事業所得・年金所得などがある場合は必須。</p>"),
            ("10ヶ月以内：相続税申告・納付", "<ul><li>遺産分割協議書の作成</li><li>不動産・預貯金・有価証券の名義変更</li><li>相続税申告書の作成・税務署提出</li><li>納付（金銭一括が原則、延納・物納制度あり）</li></ul>"),
            ("1年以内：遺留分侵害額請求", "<p>遺留分侵害を知った時から<strong>1年</strong>で時効消滅します（民法1048条）。内容証明郵便での意思表示が必須。</p>"),
            ("3年以内：相続登記の義務化", "<p>2024年4月から不動産の<strong>相続登記が義務化</strong>。相続開始を知った日から3年以内に登記しないと過料10万円以下のリスク。</p>"),
        ],
        "faqs": [
            ("葬儀費用は誰が負担しますか？", "原則として喪主負担ですが、相続税の計算上は<strong>債務控除</strong>として遺産から差し引けます（相続税法13条）。領収書は必ず保管しましょう。"),
            ("預貯金は葬儀費用に使えますか？", "2019年改正で<strong>仮払い制度</strong>が新設され、150万円を上限に各金融機関から仮払い可能になりました（民法909条の2）。"),
            ("遺品整理はいつ始めるべきですか？", "相続放棄の判断（3ヶ月）が終わってからが安全です。それ以前に処分すると単純承認とみなされる恐れがあります。"),
        ],
    },
    {
        "slug": "family-trust",
        "title": "家族信託の活用法｜認知症対策と事業承継の柔軟設計",
        "h1": "家族信託（民事信託）の活用法",
        "desc": "認知症による財産凍結を回避し、事業承継・障害者支援にも使える家族信託の仕組みと、遺言・成年後見との違いを解説。",
        "keywords": "家族信託,民事信託,認知症対策,事業承継,信託契約,委託者,受託者",
        "lead": "<strong>家族信託（民事信託）</strong>は、信頼できる家族に財産管理を任せる仕組みです。認知症対策・事業承継・障害者支援など幅広い場面で活用されています。",
        "sections": [
            ("基本構造：委託者・受託者・受益者", "<ul><li><strong>委託者</strong>：財産を預ける人（例：親）</li><li><strong>受託者</strong>：財産を管理・運用する人（例：子）</li><li><strong>受益者</strong>：利益を受け取る人（多くの場合は委託者本人＝自益信託）</li></ul>"),
            ("遺言・成年後見との違い", """
<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
  <thead><tr style="background:#27AE60;color:white;"><th style="padding:.6rem;border:1px solid #ddd;">手段</th><th style="padding:.6rem;border:1px solid #ddd;">特徴</th><th style="padding:.6rem;border:1px solid #ddd;">柔軟性</th></tr></thead>
  <tbody>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">遺言書</td><td style="padding:.6rem;border:1px solid #ddd;">死後に効力</td><td style="padding:.6rem;border:1px solid #ddd;">低</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">成年後見</td><td style="padding:.6rem;border:1px solid #ddd;">家裁監督・柔軟性低</td><td style="padding:.6rem;border:1px solid #ddd;">低</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">家族信託</td><td style="padding:.6rem;border:1px solid #ddd;">生前から死後まで連続設計可</td><td style="padding:.6rem;border:1px solid #ddd;">高</td></tr>
  </tbody>
</table>
"""),
            ("活用シーン1：認知症対策", "<p>親が認知症になると預貯金引出・不動産売却ができなくなり「資産凍結」状態に。元気なうちに信託契約を結べば、判断能力低下後も受託者が継続して管理可能。</p>"),
            ("活用シーン2：事業承継", "<p>株式の議決権を後継者に集中させつつ、配当（受益権）を他の相続人に分配する設計が可能。後継者教育中の経営権安定化に有効。</p>"),
            ("デメリット・注意点", "<ul><li>受託者の責任が重い（善管注意義務）</li><li>身上監護はできない（成年後見が必要）</li><li>節税効果は限定的（贈与税・相続税は通常通り）</li><li>専門家設計費用：30万〜100万円程度</li></ul>"),
        ],
        "faqs": [
            ("受託者は1人でないとダメですか？", "複数選任可能で、過半数決議や役割分担の設計もできます。ただし管理が煩雑になるため、メイン受託者と後継受託者の指定が一般的。"),
            ("信託財産に不動産を入れる際の注意は？", "登記名義が委託者から受託者に移ります（信託登記）。これに伴う登録免許税（固定資産税評価額×0.4%）が必要。"),
            ("信託契約は公正証書で作る必要がありますか？", "法律上は必須ではありませんが、後の紛争防止と金融機関の信託口座開設のため<strong>公正証書化が強く推奨</strong>されます。"),
        ],
    },
    {
        "slug": "spouse-residence",
        "title": "配偶者居住権とは｜2020年新設の制度をわかりやすく解説",
        "h1": "配偶者居住権の仕組みと評価",
        "desc": "2020年4月施行の配偶者居住権（民法1028条）の仕組み、評価方法、二次相続の節税効果を解説。配偶者の住居と相続の最適バランスを実現。",
        "keywords": "配偶者居住権,民法1028条,2020年改正,二次相続節税,配偶者短期居住権",
        "lead": "<strong>配偶者居住権</strong>は2020年4月施行の新制度（民法1028条以下）。配偶者の住居を守りつつ、相続税対策にも活用できます。",
        "sections": [
            ("制度の目的", "<p>従来は配偶者が自宅を相続すると預貯金の取り分が減り、生活資金不足になる問題がありました。配偶者居住権は<strong>居住権と所有権を分離</strong>することで、配偶者が自宅に住み続けながら預貯金も確保できる仕組みです。</p>"),
            ("評価方法（簡易計算）", "<p>配偶者居住権の評価額は、建物の所有権評価額から「<strong>負担付き所有権</strong>」評価額を控除した残額。配偶者の余命に応じて変動します（高齢ほど低評価＝節税効果大）。</p>"),
            ("二次相続での節税効果", "<p>配偶者居住権は配偶者の死亡で<strong>自動消滅</strong>し、所有権は完全所有権に復帰します。この時、配偶者居住権の経済的価値は<strong>相続税の対象外</strong>。一次相続で居住権を配偶者・所有権を子に分けると、二次相続で大幅節税。</p>"),
            ("配偶者短期居住権", "<p>遺産分割協議終了まで（最低6ヶ月）の暫定的な居住権（民法1037条）。配偶者居住権設定がなくても、当面の住居は確保されます。</p>"),
            ("注意点", "<ul><li>登記が必要（しないと第三者に対抗できない）</li><li>譲渡不可・賃貸には所有者の承諾必要</li><li>修繕・改築は配偶者負担</li><li>固定資産税は配偶者負担</li></ul>"),
        ],
        "faqs": [
            ("配偶者居住権を放棄するメリットは？", "高齢者ホーム入居等で自宅居住が不要になった場合、放棄して所有権者に売却益等を渡す柔軟設計が可能。"),
            ("内縁の妻に配偶者居住権は認められますか？", "法律上の配偶者でないため<strong>認められません</strong>。生前贈与や遺言での対応が必要。"),
            ("配偶者居住権はいつ設定しますか？", "遺産分割協議・遺言・家庭裁判所の審判のいずれかで設定。遺言で指定するのが最も確実です。"),
        ],
    },
    {
        "slug": "international-inheritance",
        "title": "国際相続の注意点｜外国籍配偶者・海外資産の相続",
        "h1": "国際相続の基礎と注意点",
        "desc": "外国籍の家族、海外不動産・銀行口座がある場合の相続準拠法、相続税の納税義務者区分、二重課税防止を解説。",
        "keywords": "国際相続,外国籍配偶者,海外資産,準拠法,通則法36条,相続税法1条の3",
        "lead": "外国籍の家族・海外資産がある場合、相続は格段に複雑になります。<strong>準拠法の決定</strong>と<strong>相続税の納税義務範囲</strong>を必ず確認しましょう。",
        "sections": [
            ("準拠法の決定（通則法36条）", "<p>日本の国際私法では、相続は<strong>被相続人の本国法</strong>によると定められています（法の適用に関する通則法36条）。例えば被相続人がアメリカ人なら、アメリカ法（州法）が適用される可能性があります。</p>"),
            ("相続税の納税義務者区分", "<p>相続税法1条の3により、納税義務の範囲は被相続人・相続人の住所と国籍で決まります：</p><ul><li>居住無制限納税義務者：全世界の財産が課税対象</li><li>非居住無制限納税義務者：日本国籍を持つ場合等、全世界対象</li><li>制限納税義務者：日本国内財産のみ対象</li></ul>"),
            ("二重課税の問題", "<p>海外資産が現地でも相続税課税されると二重課税に。日本では<strong>外国税額控除</strong>（相続税法20条の2）で調整しますが、相手国によっては完全には解消されません。</p>"),
            ("実務上の対応ポイント", "<ul><li>早期に国際相続に詳しい専門家へ相談</li><li>各国での遺言書を別途用意（共通遺言は無効リスク）</li><li>海外資産は現地でのプロベイト（裁判所手続き）が必要な場合あり</li><li>為替変動リスクも考慮</li></ul>"),
        ],
        "faqs": [
            ("国際結婚した場合の遺言はどう作るべきですか？", "原則として<strong>各国で別々の遺言書を作成</strong>するのが安全です。日本の自筆証書遺言は他国では効力を持たない場合があります。"),
            ("海外口座は日本の税務署にバレますか？", "CRS（共通報告基準）により、加盟国間で口座情報が自動交換されています。海外資産の隠匿はほぼ不可能と考えるべきです。"),
            ("外国籍配偶者は日本で相続できますか？", "国籍に関わらず、被相続人の本国法が日本法なら日本人と同様に相続権があります。"),
        ],
    },
    {
        "slug": "estate-division",
        "title": "遺産分割協議書の作り方｜雛形と必要事項",
        "h1": "遺産分割協議書の作成方法",
        "desc": "遺産分割協議書の必須記載事項・雛形・印鑑証明書の添付ルール・調印方法を解説。不動産登記・預貯金解約に必須の書類です。",
        "keywords": "遺産分割協議書,雛形,書き方,印鑑証明,相続登記,預貯金解約",
        "lead": "<strong>遺産分割協議書</strong>は、相続人全員で遺産の分け方を確定する重要書類です。不動産の名義変更や預貯金の解約にほぼ必須となります。",
        "sections": [
            ("必須記載事項", "<ul><li>被相続人の氏名・死亡日・最後の本籍・住所</li><li>相続人全員の氏名・住所</li><li>分割する財産の特定（不動産は登記事項のとおり、預貯金は金融機関・支店・口座番号まで）</li><li>各相続人の取得分</li><li>作成日</li><li>相続人全員の署名と実印押印</li></ul>"),
            ("雛形例", """<pre style="background:#f4f4f4;padding:1rem;border-radius:6px;font-size:.85rem;overflow-x:auto;">
遺産分割協議書

被相続人 ○○○○（令和○年○月○日死亡、本籍：東京都○○区○○）の遺産につき、
相続人全員で協議の結果、下記のとおり分割することに合意した。

第1条　相続人 △△△△ は次の財産を取得する。
  (1) 不動産：東京都○○区○○1-2-3 宅地150㎡
  (2) 預貯金：○○銀行○○支店 普通預金 No.1234567 全額

第2条　相続人 ×××× は次の財産を取得する。
  (1) 預貯金：△△銀行△△支店 普通預金 No.7654321 全額

第3条　本協議書記載の財産以外に新たな遺産が発見された場合は、改めて協議する。

令和○年○月○日

  住所：東京都○○区○○1-2-3
  氏名：△△△△               ㊞（実印）

  住所：東京都○○区○○4-5-6
  氏名：××××               ㊞（実印）
</pre>"""),
            ("印鑑証明書の添付", "<p>各相続人の<strong>印鑑証明書</strong>（発行3ヶ月以内が一般的）を添付します。遠隔地の相続人とは郵送で持ち回り調印（順番に署名押印して郵送）が可能。</p>"),
            ("協議書がないとできないこと", "<ul><li>相続登記（不動産名義変更）</li><li>預貯金の解約・名義変更</li><li>有価証券の名義変更</li><li>自動車の名義変更</li><li>相続税申告（基礎控除超過時）</li></ul>"),
        ],
        "faqs": [
            ("相続人の1人が行方不明の場合は？", "家庭裁判所で<strong>不在者財産管理人</strong>の選任を申し立てる必要があります。長期不在なら失踪宣告も検討。"),
            ("協議成立後にやり直しできますか？", "原則として再協議は不可ですが、相続人全員の合意があれば再分割は可能。ただし税務上は<strong>贈与とみなされる</strong>リスクがあるため要注意。"),
            ("未成年の相続人がいる場合は？", "親権者と未成年が共に相続人だと利益相反になるため、<strong>特別代理人</strong>を家庭裁判所で選任する必要があります（民法826条）。"),
        ],
    },
    {
        "slug": "real-estate-valuation",
        "title": "相続不動産の評価方法｜路線価方式と倍率方式の使い分け",
        "h1": "相続税における不動産の評価方法",
        "desc": "土地は路線価方式または倍率方式、建物は固定資産税評価額で評価。借地権・貸家建付地等の評価減も含めて解説。",
        "keywords": "相続税評価,路線価,倍率方式,固定資産税評価額,借地権,貸家建付地",
        "lead": "相続税における不動産評価は、<strong>路線価</strong>と<strong>倍率方式</strong>を使い分けます。市場価格より低めに設定されているのが一般的です。",
        "sections": [
            ("土地評価：路線価方式", "<p>市街地など路線価が定められている地域では、<strong>路線価 × 地積 × 各種補正率</strong>で評価。路線価は国税庁のホームページで毎年7月に公表され、公示地価の約80%水準。</p>"),
            ("土地評価：倍率方式", "<p>路線価が設定されていない地域（郊外・農村など）では、<strong>固定資産税評価額 × 国税局長が定める倍率</strong>で評価。</p>"),
            ("建物の評価", "<p>建物は<strong>固定資産税評価額をそのまま</strong>使用。一般に建築費の40〜70%程度の水準。新築直後は高く、年数経過で減価。</p>"),
            ("特殊な評価", """
<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
  <thead><tr style="background:#27AE60;color:white;"><th style="padding:.6rem;border:1px solid #ddd;">種類</th><th style="padding:.6rem;border:1px solid #ddd;">評価方法</th></tr></thead>
  <tbody>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">借地権</td><td style="padding:.6rem;border:1px solid #ddd;">自用地評価 × 借地権割合（30〜90%）</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">貸宅地（底地）</td><td style="padding:.6rem;border:1px solid #ddd;">自用地評価 × (1 − 借地権割合)</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">貸家建付地</td><td style="padding:.6rem;border:1px solid #ddd;">自用地評価 × (1 − 借地権割合 × 借家権割合 × 賃貸割合)</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">貸家</td><td style="padding:.6rem;border:1px solid #ddd;">固定資産税評価額 × (1 − 借家権割合 × 賃貸割合)</td></tr>
  </tbody>
</table>
"""),
            ("評価減の活用", "<p>賃貸物件は評価額が下がるため、現金より相続税対策になります。ただし空室率が高いと評価減が縮小し、節税効果は減少。</p>"),
        ],
        "faqs": [
            ("広大地評価は今も使えますか？", "2017年12月で廃止され、現在は<strong>「地積規模の大きな宅地の評価」</strong>に置き換わっています。要件と補正率は別ルール。"),
            ("不整形地・がけ地はどう評価しますか？", "国税庁の財産評価基本通達に基づき<strong>不整形地補正・がけ地補正</strong>で減額できます。専門知識が必要なため税理士相談を推奨。"),
            ("マンションの評価は今後どうなりますか？", "2024年から<strong>新評価方式</strong>（市場価格と評価額の乖離を是正）が導入されました。タワマン節税への影響大。"),
        ],
    },
    {
        "slug": "bank-account-freeze",
        "title": "預貯金の凍結と仮払い制度｜葬儀費用を引き出す方法",
        "h1": "預貯金凍結と仮払い制度の活用",
        "desc": "被相続人の口座は死亡を金融機関が知った時点で凍結。2019年新設の仮払い制度で最大150万円を引き出す手続きを解説。",
        "keywords": "預貯金凍結,仮払い制度,民法909条の2,葬儀費用,相続預金",
        "lead": "金融機関は預金者の死亡を知ると<strong>口座を凍結</strong>します。これは相続トラブル防止のためですが、葬儀費用・当座の生活費に困ることも。2019年の改正で仮払い制度が新設されました。",
        "sections": [
            ("いつ凍結されるか", "<p>金融機関が<strong>死亡を知った時点</strong>で凍結。役所への死亡届で自動凍結はしません。新聞のお悔やみ欄や相続人からの連絡で凍結されることが多い。</p>"),
            ("仮払い制度（民法909条の2）", "<p>2019年7月施行。相続人は<strong>遺産分割前でも預金の一部を払い戻し可能</strong>に。上限は：</p><ul><li>口座ごと：預金残高 × 1/3 × 法定相続分</li><li>金融機関ごと：150万円</li></ul><p>例：800万円の預金、法定相続分1/2の場合 → 800万円×1/3×1/2 = 133万円まで仮払い可（150万円以下なので満額OK）</p>"),
            ("仮払いに必要な書類", "<ul><li>被相続人の戸籍（出生から死亡まで）</li><li>相続人全員の戸籍</li><li>請求者の印鑑証明書</li><li>金融機関所定の請求書</li></ul>"),
            ("全額引き出しの手続き", "<p>仮払いを超える金額は、<strong>遺産分割協議書</strong>または遺言書が必要。協議書方式の場合、相続人全員の実印・印鑑証明書を添付します。</p>"),
        ],
        "faqs": [
            ("仮払いした金額は後から精算しますか？", "仮払い受領者の相続分から控除されます。<strong>遺産分割で取得したものとみなす</strong>規定（民法909条の2後段）。"),
            ("ネット銀行も凍結されますか？", "もちろん凍結されます。むしろメガバンクより手続きが煩雑な場合もあるため、生前にIDとパスワード（または相続情報）を共有しておくと安心。"),
            ("口座が凍結される前に引き出すのは問題ですか？", "法律上の罰則はありませんが、後の遺産分割で他の相続人から返還請求される可能性があります。記録を残し、葬儀等の正当な用途に限るべき。"),
        ],
    },
    {
        "slug": "contribution-share",
        "title": "寄与分と特別受益｜公平な遺産分割のための調整制度",
        "h1": "寄与分と特別受益の制度",
        "desc": "親の介護や事業貢献に応える寄与分（民法904条の2）、生前贈与を相続時に考慮する特別受益（民法903条）の計算と請求方法を解説。",
        "keywords": "寄与分,特別受益,民法904条の2,民法903条,介護,生前贈与持戻し",
        "lead": "相続人間で<strong>不公平感が生じる典型例</strong>は、介護に貢献した相続人と、過去に高額な贈与を受けた相続人の存在です。寄与分・特別受益はこれを調整する制度です。",
        "sections": [
            ("寄与分とは（民法904条の2）", "<p>被相続人の財産維持・増加に<strong>特別な貢献</strong>をした相続人の取り分を増やす制度。認められる類型：</p><ul><li>家事従事型（家業を無償で手伝った）</li><li>金銭出資型（医療費・事業資金を負担）</li><li>療養看護型（長期介護を無償で実施）</li><li>扶養型（生活費を継続的に負担）</li></ul>"),
            ("特別受益とは（民法903条）", "<p>相続人が生前に受けた<strong>特別な贈与</strong>を相続財産に持戻して計算する制度。対象例：</p><ul><li>結婚資金・新築祝い</li><li>大学院・留学費用（通常の教育費を超える）</li><li>事業承継のための資産移転</li><li>生命保険金（特別受益とされる場合あり、判例による）</li></ul>"),
            ("計算例：特別受益の持戻し", "<p>遺産6,000万円、相続人が子A・B、子Aが生前に2,000万円贈与を受けていた場合：</p><ul><li>みなし相続財産：6,000 + 2,000 = 8,000万円</li><li>各人の相続分：8,000万円 × 1/2 = 4,000万円</li><li>子Aの取得分：4,000 − 2,000（特別受益）= <strong>2,000万円</strong></li><li>子Bの取得分：<strong>4,000万円</strong></li></ul>"),
            ("特別寄与料（民法1050条）", "<p>2019年新設。相続人以外の親族（息子の妻など）が無償で介護等した場合、<strong>相続人に対して金銭請求</strong>できる制度。請求期限は知った時から6ヶ月。</p>"),
            ("実務上の注意", "<ul><li>寄与分・特別受益の主張は<strong>遺産分割協議や調停</strong>で行う</li><li>客観的な証拠（領収書・介護記録・銀行記録）が重要</li><li>2023年4月から、相続開始後10年経過すると主張不可（民法904条の3）</li></ul>"),
        ],
        "faqs": [
            ("介護したら自動的に寄与分がもらえますか？", "いいえ。<strong>「特別な」貢献</strong>が必要で、扶養義務の範囲を超える長期・無償の貢献が要件です。相続人全員の合意か家裁の認定が必要。"),
            ("生前贈与は何年前まで持戻しされますか？", "従来は無期限でしたが、2019年改正で<strong>遺留分算定では10年以内</strong>に限定（民法1044条）。ただし遺産分割上の持戻しは別ルール。"),
            ("生命保険金は特別受益になりますか？", "原則として<strong>特別受益にあたらない</strong>（判例）ですが、保険金額が相続財産に比して著しく高額な場合は例外的に対象となる場合あり（最判平16.10.29）。"),
        ],
    },
    {
        "slug": "inheritance-procedure",
        "title": "相続手続きの全体像｜何から始めればいい？フローチャート付き",
        "h1": "相続手続きの全体フロー",
        "desc": "家族が亡くなった後の相続手続きを全体像から解説。何から始めるべきか、いつまでに何をすべきか、必要な専門家は誰か。",
        "keywords": "相続手続き,流れ,何から始める,相続フロー,専門家相談,初めての相続",
        "lead": "「家族が亡くなったけど何から手をつければ…」という方へ、相続手続きの<strong>全体フロー</strong>と必要な専門家の選び方を解説します。",
        "sections": [
            ("ステップ1：遺言書の有無を確認", "<ul><li>自宅の金庫・書斎・仏壇付近を捜索</li><li>公証役場で遺言検索（無料・全国共通）</li><li>法務局の遺言書保管所での検索（2020年〜）</li><li>自筆証書遺言が見つかったら家庭裁判所で<strong>検認</strong>申立（保管制度利用なら検認不要）</li></ul>"),
            ("ステップ2：相続人の確定", "<p>被相続人の<strong>出生から死亡まで</strong>の戸籍を全て取得し、法定相続人を確定します。本籍が転々としている場合は順次取り寄せるため数週間〜数ヶ月かかることも。</p>"),
            ("ステップ3：財産・負債の調査", "<ul><li>預貯金：通帳・キャッシュカードから金融機関を特定し残高証明を取得</li><li>不動産：固定資産税納税通知書、名寄帳（市町村）</li><li>有価証券：証券会社の残高証明、特定口座年間取引報告書</li><li>負債：借入残高証明、信用情報機関（CIC・JICC・KSC）への開示請求</li></ul>"),
            ("ステップ4：相続放棄か承認か", "<p>3ヶ月の熟慮期間内に判断。マイナスが大きい場合は<strong>相続放棄</strong>、不明な場合は<strong>限定承認</strong>を検討。</p>"),
            ("ステップ5：遺産分割協議", "<p>相続人全員で分割方法を協議し、<strong>遺産分割協議書</strong>を作成。実印・印鑑証明を準備。</p>"),
            ("ステップ6：名義変更・申告", "<ul><li>不動産：相続登記（2024年4月から義務化、3年以内）</li><li>預貯金：金融機関で解約・名義変更</li><li>相続税：基礎控除超過なら10ヶ月以内に申告・納付</li></ul>"),
            ("どの専門家に相談すべきか", """
<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
  <thead><tr style="background:#27AE60;color:white;"><th style="padding:.6rem;border:1px solid #ddd;">相談内容</th><th style="padding:.6rem;border:1px solid #ddd;">適切な専門家</th></tr></thead>
  <tbody>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">相続税の申告・節税</td><td style="padding:.6rem;border:1px solid #ddd;">税理士</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">相続人間の紛争・訴訟</td><td style="padding:.6rem;border:1px solid #ddd;">弁護士</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">不動産の相続登記</td><td style="padding:.6rem;border:1px solid #ddd;">司法書士</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">遺産分割協議書作成</td><td style="padding:.6rem;border:1px solid #ddd;">行政書士・司法書士・弁護士</td></tr>
    <tr><td style="padding:.6rem;border:1px solid #ddd;">事業承継</td><td style="padding:.6rem;border:1px solid #ddd;">税理士＋経営コンサル</td></tr>
  </tbody>
</table>
"""),
        ],
        "faqs": [
            ("相続が発生してから最初にやることは？", "①死亡届の提出（7日以内）②葬儀③健康保険・年金の手続き（14日以内）と並行して、遺言書の捜索と相続人の確認に着手します。"),
            ("家系図Naviはこの手続きのどこで役立ちますか？", "ステップ2（相続人確定）とステップ5（分割方法の検討）で、法定相続分・相続税・遺留分を即座に計算でき、専門家相談前の事前検討に最適です。"),
            ("専門家への報酬の相場は？", "税理士：遺産総額の0.5〜1%程度、司法書士：相続登記6〜10万円、弁護士：着手金30万円〜＋成功報酬。複数事務所で見積もり比較を推奨。"),
        ],
    },
]


ARTICLES += [
    {
        "slug": "inheritance-trouble",
        "title": "相続トラブル事例集｜兄弟仲が悪い・実家不動産・連絡取れない",
        "h1": "よくある相続トラブル事例と回避法",
        "desc": "実家不動産の押し付け合い、連絡が取れない相続人、認知症の親など、典型的な相続トラブル10事例と予防策を解説します。",
        "keywords": "相続トラブル,事例,兄弟,実家不動産,争続,予防,対策",
        "lead": "相続争い（争続）は他人事ではありません。本記事では実際によく起きる<strong>トラブル10事例</strong>と、生前にできる予防策を紹介します。",
        "sections": [
            ("事例1：実家不動産の押し付け合い", "<p>「田舎の実家は誰も欲しがらない」「兄が独占して住みたいと言うが評価額を払えない」など、不動産の取り扱いは最頻出トラブル。<strong>換価分割</strong>（売却して現金分配）や<strong>代償分割</strong>（取得者が他に金銭支払）が解決策。</p>"),
            ("事例2：行方不明の相続人", "<p>連絡が取れない相続人がいると遺産分割協議が成立しません。<strong>不在者財産管理人</strong>の選任申立（家庭裁判所）が必要。長期不在なら失踪宣告も視野に。</p>"),
            ("事例3：親の認知症で生前対策できず", "<p>親が認知症発症後では、遺言書も贈与契約も無効リスクが高い。<strong>家族信託</strong>や<strong>任意後見契約</strong>を判断能力があるうちに準備するのが正解。</p>"),
            ("事例4：寄与分の評価で対立", "<p>長男の妻が介護したのに評価されない、というケース。<strong>特別寄与料</strong>（民法1050条・2019年新設）で請求可能だが、6ヶ月の時効に注意。</p>"),
            ("事例5：生前贈与の格差で揉める", "<p>「兄だけ家を建ててもらった」等の不公平感。<strong>特別受益の持戻し</strong>（民法903条）で公平化できるが、遺留分算定では10年以内に限定（民法1044条）。</p>"),
            ("予防策まとめ", "<ul><li>元気なうちに遺言書（公正証書推奨）</li><li>家族信託で認知症対策</li><li>家族会議で意向共有</li><li>専門家を含めた事前シミュレーション</li><li>生命保険で代償分割原資を確保</li></ul>"),
        ],
        "faqs": [
            ("相続トラブルが起きる確率は？", "司法統計によると、家庭裁判所の遺産分割事件のうち約75%が遺産5,000万円以下です。「うちは大した財産がないから大丈夫」は誤解で、むしろ少額の方が紛争率が高い傾向。"),
            ("親が「うちは仲が良いから大丈夫」と言いますが？", "実際の相続発生時に配偶者・子の意思や経済状況が変化することは多々あります。意思表示できない状態を防ぐため、遺言書は元気なうちに作成すべきです。"),
            ("家族会議は何を話すべきですか？", "①誰が何を引き継ぎたいか②介護の方針③不動産の処分方針④事業承継の意向。意見対立はあって当然。記録を残しておきましょう。"),
        ],
    },
    {
        "slug": "siblings-dispute",
        "title": "兄弟間の相続争いを防ぐ｜典型パターンと予防策",
        "h1": "兄弟間の相続争いを防ぐ方法",
        "desc": "「長男だけ優遇された」「実家を介護した姉が報われない」など兄弟相続の典型トラブルと、遺言・家族信託・生命保険を使った予防策を解説。",
        "keywords": "兄弟,相続争い,争続,長男,次男,姉妹,予防",
        "lead": "兄弟間の相続争いは、感情のもつれが法的問題と絡み合うため特に深刻化しやすい類型です。<strong>典型パターン</strong>を知り、生前対策で予防しましょう。",
        "sections": [
            ("典型パターン1：長男優遇への反発", "<p>家督相続意識が残る家庭では、長男に多く相続させようとする一方、他の兄弟が反発するケース。遺留分（民法1042条）で最低保証分は確保されているため、長男一人に集中させた遺言は遺留分侵害請求の対象に。</p>"),
            ("典型パターン2：介護負担の評価", "<p>介護した兄弟と何もしなかった兄弟の取り分が同じなのは不公平、というトラブル。<strong>寄与分</strong>（民法904条の2）で増額可能だが、客観的な記録（介護日誌・領収書）が必須。</p>"),
            ("典型パターン3：遠方在住者との温度差", "<p>地元に残った兄弟と都市部の兄弟では実家への思い入れが違うため、不動産の処分方針で対立しがち。<strong>換価分割</strong>で現金化合意が現実解。</p>"),
            ("予防策：遺言書 + 付言事項", "<p>遺言書本文で配分を明確にし、<strong>付言事項</strong>で配分理由（介護への感謝、生前贈与の意図など）を伝えると、感情的な納得を得やすい。</p>"),
            ("予防策：生命保険の活用", "<p>生命保険金は<strong>受取人固有の財産</strong>で遺産分割対象外（最判昭40.2.2）。代償分割の原資として、特定の兄弟に保険金を受け取らせる設計が有効。</p>"),
        ],
        "faqs": [
            ("「長男が全部相続」という遺言は有効ですか？", "遺言自体は有効ですが、他の兄弟から<strong>遺留分侵害額請求</strong>（民法1046条）を受ける可能性が高い。事前に他兄弟への配分も組み込むのが現実的。"),
            ("姉妹で同居していた方が多くもらえますか？", "自動的にはもらえません。同居の事実だけでなく、<strong>家業への貢献・介護等の特別寄与</strong>が認められれば寄与分加算の可能性。"),
            ("兄弟が遺産分割に応じない場合は？", "家庭裁判所の<strong>遺産分割調停</strong>を申し立てます。調停不成立なら審判に移行し、裁判所が分割方法を決定します。"),
        ],
    },
    {
        "slug": "dementia-inheritance",
        "title": "親が認知症になったら｜相続対策はどうする？",
        "h1": "認知症の親と相続対策",
        "desc": "認知症発症後は遺言書作成・生前贈与が原則できなくなります。家族信託・成年後見制度の活用法と、発症前にやるべき対策を解説。",
        "keywords": "認知症,相続対策,家族信託,成年後見,任意後見,遺言能力",
        "lead": "親が<strong>認知症</strong>になると、遺言書作成・贈与・不動産売却などの法律行為が原則できなくなります。本記事では発症前にやるべき対策を整理します。",
        "sections": [
            ("認知症と法律行為の効力", "<p>意思能力を欠く状態で行った法律行為は<strong>無効</strong>（民法3条の2）。遺言能力が必要（民法963条）で、争われると無効リスクがあります。</p>"),
            ("発症前にやるべき対策", "<ul><li><strong>公正証書遺言</strong>の作成（自筆より無効リスク低）</li><li><strong>家族信託</strong>の設定（受託者が継続管理）</li><li><strong>任意後見契約</strong>の締結（信頼できる人を後見人指名）</li><li>定期預金の整理・口座一本化</li><li>不動産の生前対策（贈与・売却）</li></ul>"),
            ("発症後の選択肢：成年後見制度", "<p>家庭裁判所が後見人を選任。報酬月2〜6万円、家裁監督下で柔軟性が低く、相続税対策のための贈与等は<strong>原則認められない</strong>のがネック。</p>"),
            ("家族信託が有効な理由", "<p>判断能力低下後も受託者が継続して財産管理可能。生前から死後までの一貫した設計ができ、成年後見よりも柔軟。設定費用は30〜100万円程度。</p>"),
            ("認知症になる前のチェックリスト", "<ul><li>□ 公正証書遺言を作成済み</li><li>□ 家族信託または任意後見契約を締結済み</li><li>□ 預貯金口座を整理済み</li><li>□ 重要書類の保管場所を家族と共有済み</li><li>□ 暗証番号・パスワードを安全に引き継ぐ準備</li></ul>"),
        ],
        "faqs": [
            ("軽度認知症でも遺言は作れますか？", "軽度であれば<strong>遺言能力ありとされる場合が多い</strong>です。ただし後の紛争を避けるため、医師の診断書を添えて公正証書で作成するのが安全。"),
            ("成年後見人は家族でも務まりますか？", "家族でも可能ですが、近年は第三者（弁護士・司法書士）が選任されるケースが増えています。家裁の判断で決定。"),
            ("認知症の親の不動産を売却したい場合は？", "成年後見人選任後、<strong>家庭裁判所の許可</strong>を得て売却可能。居住用不動産は特に厳格な審査が必要。"),
        ],
    },
    {
        "slug": "debt-inheritance",
        "title": "借金を相続したくない｜放棄・限定承認・3ヶ月期限",
        "h1": "借金を相続したくない時の対処法",
        "desc": "被相続人に借金があった場合の相続放棄・限定承認の選択、3ヶ月期限、後から発見した場合の対応を実例とともに解説。",
        "keywords": "借金,相続,相続放棄,限定承認,3ヶ月,連帯保証,信用情報開示",
        "lead": "被相続人に<strong>借金や連帯保証</strong>があった場合、何もしないと自動的に相続されます（単純承認）。借金から身を守る方法を解説します。",
        "sections": [
            ("3つの選択肢", "<ol><li><strong>単純承認</strong>：プラスもマイナスも全部相続（デフォルト）</li><li><strong>相続放棄</strong>：全部放棄、最初から相続人でなかったものとみなす</li><li><strong>限定承認</strong>：プラス財産の範囲でマイナス財産を引受</li></ol><p>2と3は<strong>3ヶ月以内</strong>に家庭裁判所への申述が必要（民法915条）。</p>"),
            ("借金の調査方法", "<ul><li><strong>CIC</strong>（クレジット系）への開示請求</li><li><strong>JICC</strong>（消費者金融系）への開示請求</li><li><strong>全銀協（KSC）</strong>（銀行系）への開示請求</li><li>請求書・督促状の確認</li><li>銀行通帳の引落履歴チェック</li></ul>"),
            ("連帯保証債務に注意", "<p>表面化しにくいが、相続される代表例。被相続人が事業のために<strong>連帯保証人になっていた</strong>場合、債権者からの請求でいきなり発覚することも。生前に契約書類を確認すべき。</p>"),
            ("3ヶ月経過後の対処", "<p>原則として単純承認とみなされますが、<strong>債務の存在を知らなかった場合</strong>は、知った時から3ヶ月以内なら放棄が認められる判例運用あり（最判昭59.4.27）。早急に弁護士相談を。</p>"),
            ("住宅ローンは団信で消える", "<p>多くの住宅ローンには<strong>団体信用生命保険</strong>が付帯し、死亡時に残債が消えます。ローン残債を理由に相続放棄する前に、団信の有無を確認。</p>"),
        ],
        "faqs": [
            ("プラス財産が多くても放棄すべき場合は？", "①相続人間トラブルから離れたい②借金の総額が不明で不安③家業の連帯保証が残るリスク等。プラス財産があっても合理的判断で放棄するケースは多い。"),
            ("放棄したら遺族年金ももらえなくなりますか？", "いいえ、遺族年金は<strong>受給権者固有の権利</strong>で相続財産ではないため、相続放棄しても受給可能。死亡保険金（受取人指定あり）も同様。"),
            ("奨学金は相続対象ですか？", "はい。日本学生支援機構の貸与型奨学金は債務として相続されます。連帯保証人・保証人がいる場合の請求順序にも注意。"),
        ],
    },
    {
        "slug": "step-family-inheritance",
        "title": "再婚家庭の相続｜連れ子・後妻の権利と養子縁組",
        "h1": "再婚家庭（連れ子・後妻）の相続",
        "desc": "再婚相手の連れ子に相続権はあるのか？後妻と先妻の子の関係は？養子縁組の有無で大きく変わる相続関係をパターン別に解説。",
        "keywords": "再婚,連れ子,後妻,先妻の子,養子縁組,ステップファミリー,相続権",
        "lead": "再婚家庭では、<strong>連れ子の相続権</strong>や<strong>後妻と先妻の子</strong>の関係でトラブルが発生しがち。法律関係を整理しましょう。",
        "sections": [
            ("再婚相手の連れ子に相続権はあるか", "<p>原則<strong>なし</strong>。再婚相手は配偶者として相続権を持つが、その連れ子は被相続人と法律上の親子関係がないため相続人になりません。</p>"),
            ("連れ子に相続させたい場合：養子縁組", "<p><strong>養子縁組</strong>すれば実子と同じ相続権が発生します。普通養子（簡単な手続き）と特別養子（家裁審判・15歳未満）の2種類。</p>"),
            ("後妻と先妻の子の関係", "<p>後妻と先妻の子は<strong>姻族関係</strong>であり、相続関係にはありません。被相続人（父）が亡くなった場合、後妻と先妻の子はいずれも法定相続人です（同じ立場）。</p>"),
            ("典型トラブル：後妻独占への反発", "<p>「後妻が全部持っていく」というのは誤解で、先妻の子にも法定相続分があります。配偶者2分の1、先妻の子と後妻の子で残り2分の1を頭割り。</p>"),
            ("予防策", "<ul><li>遺言書で意向を明確化</li><li>連れ子への遺贈または養子縁組の検討</li><li>生命保険で先妻の子の取り分を確保</li><li>家族会議で関係性を整理</li></ul>"),
        ],
        "faqs": [
            ("再婚相手の連れ子と養子縁組したら実親との関係は？", "普通養子縁組なら<strong>実親との関係も継続</strong>し、両方から相続可能。特別養子縁組なら実親との関係終了（民法817条の9）。"),
            ("内縁関係でも相続権はありますか？", "ありません。婚姻届を出していない事実婚は法定相続人になれません。遺贈や生前贈与で対応する必要があります。"),
            ("離婚した元配偶者に相続権はありますか？", "ありません。離婚により配偶者関係は終了します。ただし<strong>離婚した元配偶者との間の子</strong>には相続権があります（親子関係は継続）。"),
        ],
    },
    {
        "slug": "only-child-inheritance",
        "title": "一人っ子の相続｜全部もらえる？知っておくべき注意点",
        "h1": "一人っ子の相続で気をつけること",
        "desc": "一人っ子は遺産を全部相続できるのか？両親の二次相続・相続税負担・実家の処分など、一人っ子ならではの相続論点を解説。",
        "keywords": "一人っ子,相続,二次相続,実家処分,相続税負担,単独相続",
        "lead": "一人っ子は相続でトラブルが少ない反面、<strong>独特の論点</strong>があります。両親の二次相続まで考えた長期視点が重要です。",
        "sections": [
            ("一人っ子は遺産を全部もらえるか", "<p>母（または父）が存命の場合、配偶者と子で分割：配偶者1/2、子1/2。両親とも亡くなれば<strong>全部単独相続</strong>。</p>"),
            ("二次相続で税負担急増", "<p>一人っ子の場合、二次相続時の法定相続人は1人だけ。基礎控除が3,600万円に縮小し、相続税負担が一気に増えます。一次相続時から二次まで見据えた配分が重要。</p>"),
            ("実家不動産の処分問題", "<p>都市部勤務の一人っ子が地方の実家を相続するパターンが激増中。<strong>空き家のまま放置</strong>すると固定資産税・管理費の負担＋老朽化リスク。早期売却・賃貸活用を検討。</p>"),
            ("親の介護・看護の単独負担", "<p>兄弟がいないため介護負担も一人。<strong>寄与分</strong>の主張対象はいないが、後の相続税で介護費用を経費化できない問題も。生前贈与・家族信託の活用を。</p>"),
            ("代襲・配偶者居住権の活用", "<p>一人っ子が先立った場合、<strong>その子（孫）が代襲相続</strong>。子のいない一人っ子の場合は配偶者居住権を活用し、配偶者の生活を守りつつ親族への財産流出を防ぐ設計も。</p>"),
        ],
        "faqs": [
            ("一人っ子は相続税申告不要ですか？", "基礎控除（3,600万円〜4,200万円）を超えれば申告必要。都市部の実家不動産があれば容易に超えるケースが多い。"),
            ("親が再婚した場合、後妻にも相続権？", "あります。父の遺産は後妻1/2、自分1/2。先妻の子（自分）と後妻が遺産分割協議をする必要があります。"),
            ("一人っ子の親が認知症の場合は？", "成年後見人選任が必要ですが、自分が後見人になれば財産管理可能。家族信託の方が柔軟性が高くおすすめ。"),
        ],
    },
    {
        "slug": "agricultural-succession",
        "title": "農地の相続｜納税猶予制度と農業委員会への届出",
        "h1": "農地の相続と納税猶予制度",
        "desc": "農地相続の手続き（農業委員会への届出）、農地等の納税猶予制度（租特法70条の6）、農地法の規制を解説します。",
        "keywords": "農地相続,農業委員会,納税猶予,租特法70条の6,農地法,農業承継",
        "lead": "<strong>農地の相続</strong>は通常の不動産と異なる手続きが必要で、農業を続ける場合は強力な納税猶予制度が使えます。",
        "sections": [
            ("農業委員会への届出", "<p>農地を相続した場合、<strong>10ヶ月以内</strong>に農業委員会へ届出が必要（農地法3条の3）。怠ると10万円以下の過料。</p>"),
            ("農地等の相続税納税猶予制度", "<p>農業を継続する相続人が農地を相続する場合、<strong>農業投資価格</strong>（通常の評価額より大幅に低い）を超える分の相続税が猶予され、一定期間後免除されます（租特法70条の6）。</p>"),
            ("適用要件", "<ul><li>被相続人：死亡まで農業経営</li><li>相続人：相続後も農業継続</li><li>農地が三大都市圏特定市以外は20年継続で免除</li><li>三大都市圏特定市は終身継続で免除</li></ul>"),
            ("途中でやめたら？", "<p>農業をやめると<strong>猶予税額＋利子税</strong>を一括納付。ただし生前一括贈与・公共事業による収用等の例外あり。</p>"),
            ("市街化区域内の農地（生産緑地）", "<p>三大都市圏の特定市内では<strong>生産緑地</strong>指定により30年間営農義務。2022年問題（指定期間満了）で特定生産緑地への移行が論点に。</p>"),
        ],
        "faqs": [
            ("農業を継がない場合は？", "通常の不動産として相続税課税。納税猶予は使えません。宅地転用・売却を検討。"),
            ("農地を貸している場合の相続は？", "貸付農地として評価減（小規模宅地等の特例の貸付事業用宅地として50%減）が可能な場合あり。"),
            ("耕作放棄地はどう扱われますか？", "農地としての扱いが続きますが、適切に管理されていないと固定資産税の優遇措置がなくなる可能性。市町村と相談を。"),
        ],
    },
    {
        "slug": "art-collection-inheritance",
        "title": "美術品・骨董品の相続｜評価方法と物納の活用",
        "h1": "美術品・骨董品の相続評価",
        "desc": "絵画・茶器・刀剣等の美術品を相続した時の評価方法、所得税のみなし譲渡、相続税物納制度の活用を解説。",
        "keywords": "美術品,骨董品,相続,評価,物納,みなし譲渡,鑑定",
        "lead": "美術品・骨董品の<strong>相続評価</strong>は鑑定が必要で、現金化困難な財産として課題が多い分野です。",
        "sections": [
            ("評価方法", "<p>原則として<strong>売買実例価額・精通者意見価格</strong>等で評価（財産評価基本通達135）。公開された売買実例、専門業者の査定書、有名鑑定人の評価書などを根拠とします。</p>"),
            ("評価減のテクニック", "<ul><li>複数の鑑定で最も低い評価を採用</li><li>真贋未確認なら割引適用</li><li>市場性の低い物は実勢価格で評価</li><li>共有持分での評価減</li></ul>"),
            ("物納制度の活用", "<p>金銭納付困難な場合、<strong>美術品で相続税を納付</strong>する物納制度を活用できます（相続税法41条）。文化財保護法の重要美術品等は優先順位高。</p>"),
            ("生前売却の選択", "<p>相続後の現金化は売却額が評価額を下回ることが多いため、<strong>生前売却</strong>して現金化しておくのも選択肢。譲渡所得税との比較検討が必要。</p>"),
            ("登録美術品制度", "<p>文化庁長官登録の美術品は、相続税納付期限まで<strong>美術館への寄託</strong>条件で物納適格になりやすい優遇あり。</p>"),
        ],
        "faqs": [
            ("コレクションの相続税はいくら？", "個別評価次第ですが、有名作家の絵画・古美術なら数百万円〜億単位。事前の鑑定と保険評価の確認を。"),
            ("家族に美術品の価値が分からない場合は？", "生前にリスト化と評価額の目安を記録しておきましょう。死後の散逸・誤廃棄を防ぐためにも重要。"),
            ("骨董市で売れない物も評価されますか？", "市場性が乏しい物は<strong>低評価または評価ゼロ</strong>とできる場合あり。鑑定人の意見書が根拠になります。"),
        ],
    },
    {
        "slug": "crypto-inheritance",
        "title": "暗号資産（仮想通貨）の相続｜評価・手続き・税負担",
        "h1": "暗号資産（仮想通貨）の相続",
        "desc": "ビットコイン等の暗号資産を相続する際の評価方法、取引所の名義変更手続き、所得税・相続税の二重課税問題を解説。",
        "keywords": "暗号資産,仮想通貨,ビットコイン,相続,評価,取引所,二重課税",
        "lead": "<strong>暗号資産（仮想通貨）</strong>は新しい相続財産で、現行制度の課題が多い分野です。早期の対策が重要。",
        "sections": [
            ("評価方法", "<p>相続開始日の<strong>取引所の終値</strong>で評価（国税庁QA）。複数取引所で価格差がある場合は被相続人の利用取引所の価格を使用。</p>"),
            ("取引所での手続き", "<ul><li>取引所への死亡連絡 → 口座凍結</li><li>戸籍謄本・遺産分割協議書を提出</li><li>相続人の口座に移管または現金化</li><li>取引所ごとに手続きが異なるため要確認</li></ul>"),
            ("プライベートウォレットのリスク", "<p>取引所ではなく<strong>ハードウェアウォレットや自己管理のウォレット</strong>に保管している場合、秘密鍵・シードフレーズが分からないと<strong>永久に取り出せない</strong>リスクが致命的。</p>"),
            ("税負担の問題", "<p>暗号資産の譲渡益は<strong>雑所得（総合課税）</strong>で最大55%。相続後に売却するとさらに譲渡益課税が発生し、<strong>事実上の二重課税</strong>が発生する場合あり。</p>"),
            ("生前にやるべき対策", "<ul><li>保有資産のリスト化（取引所・銘柄・数量）</li><li>秘密鍵・シードフレーズの安全な引継ぎ準備</li><li>取引所のログイン情報の管理</li><li>必要に応じて売却し現金化</li></ul>"),
        ],
        "faqs": [
            ("シードフレーズを家族が知らない場合は？", "<strong>取り出し不可能</strong>になります。エンディングノート・遺言書での明示、または信頼できる家族への分割共有等の対策が必須。"),
            ("DeFi・NFTも相続対象ですか？", "はい、財産的価値があれば相続対象。ただし評価方法が確立しておらず、ケースバイケースで判断。"),
            ("海外取引所の暗号資産は？", "国外財産として相続税対象。CRSにより日本の税務署も把握しやすくなっています。"),
        ],
    },
    {
        "slug": "estate-tax-return",
        "title": "相続税の申告書の書き方｜必要書類と提出先",
        "h1": "相続税申告書の書き方と提出",
        "desc": "相続税申告書（第1表〜第15表）の構成と作成手順、必要な戸籍・残高証明・評価明細書を整理。期限10ヶ月・税務署提出までの流れ。",
        "keywords": "相続税,申告書,書き方,提出先,必要書類,第1表,10ヶ月",
        "lead": "相続税の申告は10ヶ月以内に行う必要があります。本記事では<strong>申告書の構成</strong>と必要書類を整理します。",
        "sections": [
            ("申告書の基本構成", "<p>相続税申告書は<strong>第1表〜第15表</strong>で構成されます。主要なものは：</p><ul><li><strong>第1表</strong>：相続税の課税価格と納付税額</li><li><strong>第2表</strong>：相続税の総額</li><li><strong>第9表〜第15表</strong>：各種特例・控除・財産明細</li></ul>"),
            ("必要書類", "<ul><li>被相続人の戸籍（出生から死亡まで）</li><li>相続人全員の戸籍・印鑑証明書</li><li>遺産分割協議書（または遺言書）</li><li>預貯金残高証明書（死亡日時点）</li><li>不動産の登記事項証明書・固定資産税評価証明書・路線価図</li><li>有価証券残高証明書</li><li>債務証明書（借入残高証明等）</li><li>葬儀費用の領収書</li></ul>"),
            ("提出先", "<p><strong>被相続人の住所地</strong>を管轄する税務署。相続人の住所地ではない点に注意。複数の相続人で共同申告するのが一般的（連名で1通）。</p>"),
            ("税理士に依頼するメリット", "<ul><li>評価減の適用漏れ防止（小規模宅地・配偶者居住権等）</li><li>税務調査リスクの低減</li><li>書面添付制度（税理士法33条の2）で調査確率減</li><li>節税策の事前提案</li></ul><p>報酬相場は遺産総額の<strong>0.5〜1.0%</strong>。"),
            ("自分で申告する場合の注意", "<p>シンプルな相続なら自力申告可能ですが、不動産がある場合や評価が複雑な場合はミスのリスクが高い。<strong>修正申告・延滞税</strong>が発生すると結果的に税理士費用より高額になることも。</p>"),
        ],
        "faqs": [
            ("申告期限を過ぎたらどうなりますか？", "<strong>無申告加算税</strong>（15〜20%）と<strong>延滞税</strong>が課されます。期限内申告ができない場合は期限後でも早急に。"),
            ("分割協議がまとまらない場合は？", "<strong>未分割申告</strong>（法定相続分で仮申告）を行い、後で分割確定時に修正申告。ただし配偶者控除・小規模宅地等の特例が一時的に使えなくなるデメリットあり。"),
            ("修正申告と更正の請求の違いは？", "税額を増やす修正は<strong>修正申告</strong>、減らすのは<strong>更正の請求</strong>（5年以内）。"),
        ],
    },
]


def render(article, related_links):
    title = article["title"]
    desc = article["desc"]
    h1 = article["h1"]
    slug = article["slug"]
    url = f"{SITE_URL}/{slug}/"

    # セクションHTML（各H2にidを付与してTOCとアンカー連動）
    def _slug_id(i):
        return f"sec-{i+1}"

    sections_html = "\n".join(
        f'<h2 id="{_slug_id(i)}">{i+1}. {h2}</h2>\n{body}'
        for i, (h2, body) in enumerate(article["sections"])
    )
    # 本文中の文脈内部リンクを自動付与（関連記事への送客・トピカル強化）
    sections_html = autolink(sections_html, slug)
    # 目次（TOC）
    toc_html = "\n".join(
        f'<li><a href="#{_slug_id(i)}">{h2}</a></li>'
        for i, (h2, _) in enumerate(article["sections"])
    ) + '\n<li><a href="#faq">よくある質問</a></li>'

    faq_html = "\n".join(
        f'<details><summary>{q}</summary><p>{a}</p></details>'
        for q, a in article["faqs"]
    )
    related_html = "\n".join(
        f'<li><a href="../{s}/">{t}</a></li>'
        for s, t in related_links
    )

    # 読了時間（日本語400字/分の概算）
    import re as _re
    plain = _re.sub(r'<[^>]+>', '', article["lead"] + "".join(b for _, b in article["sections"]) + "".join(q + a for q, a in article["faqs"]))
    read_min = max(1, len(plain) // 400)

    # HowTo風記事の判定（procedural keywordsで自動判定）
    howto_slugs = {"will-template", "estate-division", "estate-tax-return", "inheritance-renounce",
                   "inheritance-procedure", "post-death-timeline", "bank-account-freeze"}
    howto_jsonld_str = ""
    if slug in howto_slugs:
        howto = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": h1,
            "description": desc,
            "totalTime": f"PT{read_min}M",
            "step": [
                {
                    "@type": "HowToStep",
                    "position": i + 1,
                    "name": h2,
                    "text": _re.sub(r'<[^>]+>', '', body)[:300],
                    "url": f"{url}#{_slug_id(i)}",
                }
                for i, (h2, body) in enumerate(article["sections"])
            ],
        }
        howto_jsonld_str = f'<script type="application/ld+json">{json.dumps(howto, ensure_ascii=False)}</script>'

    article_jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "description": desc,
        "image": ICON,
        "datePublished": "2026-05-30",
        "dateModified": "2026-05-30",
        "author": {"@type": "Person", "name": "Mirai Navi"},
        "publisher": {
            "@type": "Organization",
            "name": "家系図Navi",
            "logo": {"@type": "ImageObject", "url": ICON},
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "inLanguage": "ja",
    }
    faq_jsonld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a.replace('<strong>', '').replace('</strong>', '')},
            }
            for q, a in article["faqs"]
        ],
    }
    # 所属する柱ページ（トピッククラスター）を取得
    pillar_info = get_article_pillar(slug)  # (pillar_slug, pillar_h1) or None
    if pillar_info:
        p_slug, p_h1 = pillar_info
        breadcrumb_items = [
            {"@type": "ListItem", "position": 1, "name": "家系図Navi", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": p_h1, "item": f"{SITE_URL}/{p_slug}/"},
            {"@type": "ListItem", "position": 3, "name": h1, "item": url},
        ]
        nav_html = (f'<a href="../">🌳 家系図Navi</a> ＞ '
                    f'<a href="../{p_slug}/" style="color:white;text-decoration:none;opacity:.85;">{p_h1}</a> ＞ {h1}')
        pillar_box = (
            f'<div style="background:#eafaf1;border:1px solid #b8e6cc;border-radius:10px;'
            f'padding:.9rem 1.2rem;margin:1.2rem 0;font-size:.92rem;">'
            f'📚 このテーマを体系的に学ぶ：<a href="../{p_slug}/" style="color:#16A085;font-weight:700;">{p_h1}</a></div>'
        )
    else:
        breadcrumb_items = [
            {"@type": "ListItem", "position": 1, "name": "家系図Navi", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "ガイド", "item": f"{SITE_URL}/guides/"},
            {"@type": "ListItem", "position": 3, "name": h1, "item": url},
        ]
        nav_html = ('<a href="../">🌳 家系図Navi</a> ＞ '
                    '<a href="../guides/" style="color:white;text-decoration:none;opacity:.85;">ガイド</a> ＞ ' + h1)
        pillar_box = ""

    breadcrumb_jsonld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_items,
    }

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}｜家系図Navi</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="{article['keywords']}">
  <meta name="robots" content="index, follow">
  <meta name="author" content="Mirai Navi">
  <link rel="canonical" href="{url.replace(SITE_URL, CANONICAL_BASE)}">
  <link rel="alternate" hreflang="ja" href="{url}">
  <link rel="alternate" type="application/rss+xml" title="家系図Navi 記事フィード" href="{SITE_URL}/feed.xml">

  <meta property="og:title" content="{title}｜家系図Navi">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="家系図Navi">
  <meta property="og:locale" content="ja_JP">
  <meta property="og:image" content="{ICON}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{ICON}">

  <script type="application/ld+json">{json.dumps(article_jsonld, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(faq_jsonld, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb_jsonld, ensure_ascii=False)}</script>
  {howto_jsonld_str}

  <link rel="icon" href="../icon_192.png">
  <style>
    :root {{ --green: #27AE60; --light-bg: #f8fdf9; --text: #2c3e50; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: var(--light-bg); color: var(--text); line-height: 1.8; }}
    header {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 2.5rem 1.5rem; text-align: center; }}
    header .nav {{ font-size: .9rem; margin-bottom: 1rem; opacity: .9; }}
    header .nav a {{ color: white; text-decoration: none; opacity: .85; }}
    header h1 {{ font-size: 1.8rem; font-weight: 800; margin: .5rem 0; }}
    header p.lead {{ font-size: .95rem; opacity: .95; max-width: 700px; margin: 1rem auto 0; }}
    .cta {{ display: inline-block; margin-top: 1.5rem; padding: .8rem 2rem; background: white; color: var(--green); font-weight: 700; border-radius: 50px; text-decoration: none; box-shadow: 0 4px 15px rgba(0,0,0,.15); }}
    main {{ max-width: 820px; margin: 0 auto; padding: 2.5rem 1.5rem; }}
    h2 {{ font-size: 1.35rem; color: var(--green); margin: 2rem 0 1rem; border-left: 4px solid var(--green); padding-left: .8rem; }}
    p, ul, ol {{ margin: .8rem 0; }}
    ul, ol {{ padding-left: 1.5rem; }}
    li {{ margin: .3rem 0; }}
    details {{ background: white; border-radius: 8px; margin-bottom: .8rem; padding: 1rem 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,.06); }}
    summary {{ font-weight: 600; cursor: pointer; list-style: none; }}
    summary::before {{ content: "Q. "; color: var(--green); }}
    details p {{ margin-top: .6rem; font-size: .95rem; color: #444; }}
    .related {{ background: white; border-radius: 12px; padding: 1.5rem; margin: 2rem 0; box-shadow: 0 2px 8px rgba(0,0,0,.06); }}
    .related h2 {{ margin-top: 0; }}
    .related a {{ color: var(--green); text-decoration: none; font-weight: 600; }}
    .cta-box {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 2rem; border-radius: 12px; text-align: center; margin: 2.5rem 0; }}
    .cta-box h3 {{ font-size: 1.2rem; margin-bottom: .8rem; }}
    .cta-box a {{ display: inline-block; padding: .8rem 2rem; background: white; color: var(--green); font-weight: 700; border-radius: 50px; text-decoration: none; }}
    .meta-info {{ display: flex; flex-wrap: wrap; gap: .8rem; justify-content: center; margin-top: 1rem; font-size: .85rem; opacity: .9; }}
    .meta-info span {{ background: rgba(255,255,255,.18); padding: .25rem .8rem; border-radius: 50px; }}
    .toc {{ background: white; border-radius: 12px; padding: 1.2rem 1.5rem; margin: 1.5rem 0 2rem; box-shadow: 0 2px 8px rgba(0,0,0,.06); border-left: 4px solid var(--green); }}
    .toc-title {{ font-weight: 700; color: var(--green); margin-bottom: .6rem; font-size: 1rem; }}
    .toc ol {{ margin: 0; padding-left: 1.4rem; }}
    .toc ol li {{ margin: .35rem 0; }}
    .toc a {{ color: var(--text); text-decoration: none; }}
    .toc a:hover {{ color: var(--green); text-decoration: underline; }}
    .share {{ margin: 2rem 0; padding: 1.2rem; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.06); }}
    .share-btn {{ display: inline-block; padding: .5rem 1rem; margin: .25rem .3rem .25rem 0; border-radius: 50px; font-size: .85rem; font-weight: 600; text-decoration: none; color: white; }}
    .share-btn.x {{ background: #000; }}
    .share-btn.fb {{ background: #1877F2; }}
    .share-btn.line {{ background: #06C755; }}
    .share-btn.hb {{ background: #00A4DE; }}
    .disclaimer {{ background: #fff8e1; border-left: 4px solid #f39c12; padding: 1rem 1.2rem; border-radius: 4px; font-size: .9rem; margin: 2rem 0; }}
    footer {{ text-align: center; padding: 2rem; font-size: .85rem; color: #888; border-top: 1px solid #eee; }}
    footer a {{ color: var(--green); text-decoration: none; }}
  </style>
</head>
<body>

<header>
  <div class="nav">{nav_html}</div>
  <h1>{h1}</h1>
  <p class="lead">{desc}</p>
  <div class="meta-info">
    <span>✍ 著者: Mirai Navi</span>
    <span>📅 更新: 2026年5月30日</span>
    <span>⏱ 読了 約{read_min}分</span>
  </div>
  <a class="cta" href="{APP_URL}" rel="noopener">無料シミュレーターを試す →</a>
</header>

<main>

  <p>{article["lead"]}</p>

  {pillar_box}

  {ad_block_wide()}

  <nav class="toc" aria-label="目次">
    <div class="toc-title">📑 目次</div>
    <ol>{toc_html}</ol>
  </nav>

  {sections_html}

  <h2 id="faq">よくある質問</h2>
  {faq_html}

  {ad_block_tax()}

  <div class="cta-box">
    <h3>家族構成を入力するだけで自動診断</h3>
    <p>法定相続分・相続税・遺留分を国税庁公表値準拠で計算。データ保存なしの完全無料アプリ。</p>
    <a href="{APP_URL}" rel="noopener">家系図Naviを開く →</a>
  </div>

  {ad_block()}

  <div class="share">
    <p style="margin-bottom:.6rem;font-weight:600;color:#555;">この記事をシェア</p>
    <a class="share-btn x" href="https://twitter.com/intent/tweet?url={url}&text={title}" target="_blank" rel="noopener">𝕏 Xでポスト</a>
    <a class="share-btn fb" href="https://www.facebook.com/sharer/sharer.php?u={url}" target="_blank" rel="noopener">f Facebook</a>
    <a class="share-btn line" href="https://social-plugins.line.me/lineit/share?url={url}" target="_blank" rel="noopener">LINE</a>
    <a class="share-btn hb" href="https://b.hatena.ne.jp/entry/{url}" target="_blank" rel="noopener">B!はてブ</a>
  </div>

  <div class="related">
    <h2>関連記事</h2>
    <ul>{related_html}</ul>
  </div>

  <div class="disclaimer">
    <strong>⚖️ 免責事項：</strong>本記事は一般的な情報提供を目的としたものであり、法的助言ではありません。個別事案は弁護士・税理士・司法書士等の専門家にご相談ください。
  </div>

</main>

<footer>
  <p>© 2026 Mirai Navi — <a href="../">家系図Navi / Family Tree Guide</a></p>
  <p style="margin-top:.5rem;font-size:.82rem;">🔗 姉妹サイト：<a href="https://mirainavi.net/?utm_source=note&utm_medium=article&utm_campaign=brand-story&utm_content=cta_text_bottom" target="_blank" rel="noopener" style="color:#16A085;">ミライNavi</a> ｜ <a href="https://teso-navi.vercel.app/" target="_blank" rel="noopener" style="color:#16A085;">手相ナビ</a> ｜ <a href="https://kakeizu-souzoku-navi.blog.jp/" target="_blank" rel="noopener" style="color:#16A085;">運営ブログ</a></p>
  <p style="margin-top:.5rem;font-size:.78rem;color:#999;">当サイトはアフィリエイト広告（プロモーション）を利用しています。｜<a href="https://yadianqiteng5-spec.github.io/kakeizu-navi-lp/about/" style="color:#16A085;">運営者情報・プライバシー</a></p>
</footer>

</body>
</html>
"""


# ════════════════════════════════════════════════
# 柱ページ（トピッククラスター）— ヘッドキーワードを狙う総合ガイド
# ════════════════════════════════════════════════
def _meta_map():
    """slug -> (見出し, 説明) のマップ（記事・早見表・ツールを横断）"""
    m = {}
    for a in ARTICLES:
        m[a["slug"]] = (a["h1"], a["desc"])
    for q in QUICK_TABLES:
        m[q["slug"]] = (q["h1"], q["desc"])
    m["calculator"] = ("相続税かんたん計算ツール", "遺産額と家族構成を入力するだけで相続税の概算を自動計算。")
    m["cases"] = ("相続ケーススタディ集（20例）", "配偶者と子・事業承継・二次相続など典型20例で確認。")
    m["glossary"] = ("相続・事業承継用語集", "相続の専門用語40語をやさしく解説。")
    return m


PILLARS = [
    {
        "slug": "guide-inheritance-tax",
        "title": "相続税のすべて｜計算方法・節税・申告の完全ガイド",
        "h1": "相続税まるわかり完全ガイド",
        "desc": "相続税の基礎控除・計算方法・税率・申告期限から、小規模宅地等の特例・二次相続・生前贈与といった節税策、税務調査対策までを体系的に解説する総合ガイド。",
        "keywords": "相続税,計算,節税,基礎控除,申告,税率,特例,完全ガイド",
        "intro": "相続税は「いくらかかるのか」「どう減らせるのか」「いつ申告するのか」が分かりにくい税金です。本ガイドでは、<strong>基礎控除と税率の基本</strong>から、<strong>小規模宅地等の特例・二次相続・生前贈与などの節税策</strong>、そして<strong>申告と税務調査</strong>まで、相続税の全体像を順を追って解説します。各テーマの詳しい記事・早見表・計算ツールへリンクしています。",
        "groups": [
            ("まず基本を押さえる", ["inheritance-tax-threshold", "inheritance-tax", "table-inheritance-tax", "table-basic-deduction", "calculator", "tax-surcharge"]),
            ("評価と特例で税額を下げる", ["small-residential", "real-estate-valuation", "corporate-shares", "nominee-deposit", "leasehold-inheritance", "spouse-tax-credit", "disability-minor-credit", "art-collection-inheritance", "crypto-inheritance"]),
            ("節税の王道：二次相続・生前贈与・保険", ["settlement-taxation-gift", "gift-addback-7year", "spouse-gift-deduction", "housing-fund-gift", "secondary-inheritance", "gift-strategy", "gift-vs-inheritance", "table-gift-tax", "insurance-strategy", "retirement-money", "education-gift"]),
            ("申告・納税・調査・売却", ["estate-tax-return", "tax-investigation", "penalty-tax", "deferred-payment", "consecutive-inheritance", "sell-inherited-property", "vacant-house-deduction", "quasi-final-tax-return", "amended-tax-return", "land-to-state"]),
        ],
    },
    {
        "slug": "guide-procedure",
        "title": "相続手続きの完全ガイド｜流れ・期限・必要書類",
        "h1": "相続手続き完全ガイド",
        "desc": "家族が亡くなった後の相続手続きを、全体の流れ・期限カレンダー・必要書類・専門家費用まで網羅。死亡届から相続登記・相続税申告までを順に解説する総合ガイド。",
        "keywords": "相続手続き,流れ,期限,必要書類,相続登記,遺産分割,完全ガイド",
        "intro": "相続手続きは「何から始めればいいか分からない」という方がほとんどです。本ガイドでは、<strong>手続きの全体像と期限</strong>、<strong>預貯金・不動産・遺産分割の進め方</strong>、<strong>借金・相続放棄の判断</strong>、そして<strong>専門家への依頼</strong>までを、時系列で整理して解説します。",
        "groups": [
            ("全体像と期限をつかむ", ["asset-investigation", "inheritance-procedure", "post-death-timeline", "table-deadlines", "legal-heir-info", "collect-koseki", "diy-inheritance"]),
            ("財産の名義変更・解約", ["life-insurance-claim", "bank-account-freeze", "real-estate-valuation", "mortgage-inheritance", "estate-division", "digital-legacy", "will-probate", "car-inheritance", "shared-property", "inheritance-registration", "international-inheritance", "inheritance-overseas"]),
            ("放棄・借金・トラブル対応", ["division-redo", "renounce-duty", "estate-administrator", "inheritance-renounce", "debt-inheritance", "inheritance-trouble", "disinheritance", "renounce-still-receive", "property-division-methods", "division-mediation"]),
            ("年金・お墓・専門家相談", ["survivor-pension", "grave-succession", "consulting-cost", "inheritance-consultation"]),
        ],
    },
    {
        "slug": "guide-succession",
        "title": "事業承継の完全ガイド｜自社株・納税猶予・後継者対策",
        "h1": "事業承継・自社株 完全ガイド",
        "desc": "中小企業オーナーの事業承継を、自社株の分散リスク・評価方法・事業承継税制（納税猶予）・家族信託の活用まで体系的に解説する総合ガイド。",
        "keywords": "事業承継,自社株,納税猶予,後継者,事業承継税制,家族信託,完全ガイド",
        "intro": "中小企業オーナーの相続では、<strong>自社株の扱い</strong>を誤ると会社の経営権が分散し、事業の継続が危ぶまれます。本ガイドでは、<strong>事業承継の主要リスクと対策</strong>、<strong>非上場株式の評価</strong>、<strong>家族信託や生前贈与の活用</strong>までを解説します。",
        "groups": [
            ("リスクと全体戦略", ["business-succession", "corporate-shares"]),
            ("承継の手法", ["family-trust", "gift-strategy", "freelance-inheritance", "agricultural-succession"]),
        ],
    },
    {
        "slug": "guide-will",
        "title": "遺言・終活の完全ガイド｜遺言書の書き方と生前対策",
        "h1": "遺言・終活 完全ガイド",
        "desc": "自筆証書遺言の書き方・書き換え、遺留分への配慮、認知症対策の家族信託、配偶者居住権、終活チェックリストまで、生前にやるべき対策を体系的に解説する総合ガイド。",
        "keywords": "遺言,終活,遺言書,書き方,遺留分,家族信託,生前対策,完全ガイド",
        "intro": "「元気なうちに準備しておけばよかった」は相続で最も多い後悔です。本ガイドでは、<strong>遺言書の作り方と書き換え</strong>、<strong>遺留分への配慮</strong>、<strong>認知症に備える家族信託</strong>、<strong>配偶者の住まいを守る配偶者居住権</strong>、そして<strong>終活の進め方</strong>までを解説します。",
        "groups": [
            ("遺言書を正しく残す", ["invalid-will", "will-template", "notarized-will", "will-rewrite", "will-executor", "will-probate", "legal-reserve", "will-trust-bank"]),
            ("財産の渡し方", ["bequest-gift", "gift-strategy", "education-gift", "gift-vs-inheritance"]),
            ("認知症・生前の備え", ["endlife-checklist", "family-trust", "dementia-inheritance", "adult-guardianship", "voluntary-guardianship", "spouse-residence", "single-person-endlife", "pet-legacy"]),
        ],
    },
    {
        "slug": "guide-heirs",
        "title": "相続人と相続分の完全ガイド｜誰がいくら相続するか",
        "h1": "相続人・相続分 完全ガイド",
        "desc": "誰が法定相続人になるのか（順位・範囲）、養子や再婚相手の連れ子の扱い、法定相続分の計算と早見表、寄与分・特別受益、兄弟姉妹間のトラブル対策までを体系的に解説する総合ガイド。",
        "keywords": "相続人,法定相続分,順位,養子,寄与分,早見表,兄弟姉妹,完全ガイド",
        "intro": "相続でまず確かめるべきは「<strong>誰が相続人か</strong>」と「<strong>それぞれの取り分（相続分）</strong>」です。本ガイドでは、<strong>相続人の順位と範囲</strong>、<strong>養子・連れ子・特別養子の扱い</strong>、<strong>法定相続分の計算と早見表</strong>、<strong>寄与分や兄弟間のトラブル対策</strong>までを順を追って解説します。各テーマの詳しい記事へリンクしています。",
        "groups": [
            ("だれが相続人になるか（順位と範囲）", ["special-agent-minor", "substitution-inheritance", "legal-heir-info", "siblings-only-inheritance", "only-child-inheritance", "step-family-inheritance"]),
            ("養子・特別養子と相続", ["special-adoption", "adoption-pros-cons"]),
            ("相続分の計算・早見表・寄与分", ["special-contribution-fee", "legal-share", "table-legal-share", "contribution-share"]),
            ("兄弟・親族間のトラブル対策", ["siblings-dispute", "inheritance-trouble"]),
        ],
    },
    {
        "slug": "guide-koseki",
        "title": "戸籍と家系図の完全ガイド｜集め方・読み方・相続関係説明図",
        "h1": "戸籍・家系図 完全ガイド",
        "desc": "相続に必要な戸籍の集め方（広域交付・除籍・改製原戸籍）、古い戸籍の読み方、家系図・相続関係説明図の作り方、先祖をどこまで辿れるかまでを、家系図Naviが体系的に解説する総合ガイド。",
        "keywords": "戸籍,家系図,広域交付,除籍謄本,改製原戸籍,相続関係説明図,ルーツ調査,完全ガイド",
        "intro": "相続手続きでもルーツ調べでも、出発点になるのが「<strong>戸籍</strong>」です。本ガイドでは、<strong>戸籍の集め方（広域交付・除籍・改製原戸籍）</strong>、<strong>古い戸籍の読み方</strong>、<strong>家系図・相続関係説明図の作り方</strong>、そして<strong>先祖をどこまで辿れるか</strong>までを、順を追って解説します。各テーマの詳しい記事へリンクしています。",
        "groups": [
            ("戸籍を集める・取り寄せる", ["collect-koseki", "koseki-wide-area", "koseki-removed", "old-koseki-reading"]),
            ("家系図・相続関係説明図を作る", ["kakeizu-howto", "relationship-chart"]),
            ("ルーツ・先祖をたどる", ["how-far-back"]),
        ],
    },
]


_ARTICLE_PILLAR = None


def get_article_pillar(slug):
    """記事slug -> (柱ページslug, 柱ページh1) を返す（双方向リンク用）。無ければNone。"""
    global _ARTICLE_PILLAR
    if _ARTICLE_PILLAR is None:
        _ARTICLE_PILLAR = {}
        for p in PILLARS:
            for _, slugs in p["groups"]:
                for s in slugs:
                    _ARTICLE_PILLAR.setdefault(s, (p["slug"], p["h1"]))
    return _ARTICLE_PILLAR.get(slug)


def render_pillar(pillar, meta):
    url = f"{SITE_URL}/{pillar['slug']}/"
    groups_html = ""
    item_names = []
    for gtitle, slugs in pillar["groups"]:
        cards = ""
        for s in slugs:
            h1, desc = meta.get(s, (s, ""))
            item_names.append(h1)
            cards += (f'<a class="pcard" href="../{s}/"><h3>{h1}</h3><p>{desc}</p></a>\n')
        groups_html += f'<h2>{gtitle}</h2>\n<div class="pgrid">\n{cards}</div>\n'

    article_jsonld = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": pillar["h1"], "description": pillar["desc"], "image": ICON,
        "datePublished": "2026-05-30", "dateModified": "2026-05-30",
        "author": {"@type": "Person", "name": "Mirai Navi"},
        "publisher": {"@type": "Organization", "name": "家系図Navi",
                      "logo": {"@type": "ImageObject", "url": ICON}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "inLanguage": "ja",
    }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "家系図Navi", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": pillar["h1"], "item": url},
        ],
    }
    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": pillar["h1"],
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n}
            for i, n in enumerate(item_names)
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{pillar['title']}｜家系図Navi</title>
  <meta name="description" content="{pillar['desc']}">
  <meta name="keywords" content="{pillar['keywords']}">
  <meta name="robots" content="index, follow">
  <meta name="author" content="Mirai Navi">
  <link rel="canonical" href="{url.replace(SITE_URL, CANONICAL_BASE)}">
  <meta property="og:title" content="{pillar['title']}｜家系図Navi">
  <meta property="og:description" content="{pillar['desc']}">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="article">
  <meta property="og:image" content="{ICON}">
  <script type="application/ld+json">{json.dumps(article_jsonld, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(itemlist, ensure_ascii=False)}</script>
  <link rel="icon" href="../icon_192.png">
  <style>
    :root {{ --green: #27AE60; --light-bg: #f8fdf9; --text: #2c3e50; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: var(--light-bg); color: var(--text); line-height: 1.8; }}
    header {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 2.5rem 1.5rem; text-align: center; }}
    header h1 {{ font-size: 1.9rem; margin: .5rem 0; }}
    header .nav {{ font-size: .85rem; opacity: .9; }}
    header .nav a {{ color: white; text-decoration: none; }}
    main {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}
    .lead {{ font-size: 1rem; background: white; padding: 1.3rem 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.06); border-left: 4px solid var(--green); }}
    h2 {{ font-size: 1.3rem; color: var(--green); margin: 2rem 0 1rem; border-left: 4px solid var(--green); padding-left: .8rem; }}
    .pgrid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: .9rem; }}
    .pcard {{ background: white; border-radius: 10px; padding: 1.1rem 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,.06); text-decoration: none; color: inherit; border-top: 3px solid var(--green); }}
    .pcard:hover {{ box-shadow: 0 5px 14px rgba(0,0,0,.1); }}
    .pcard h3 {{ font-size: 1rem; color: var(--green); margin-bottom: .4rem; }}
    .pcard p {{ font-size: .85rem; color: #555; }}
    .cta-box {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 1.6rem; border-radius: 12px; text-align: center; margin: 2.5rem 0; }}
    .cta-box a {{ display: inline-block; padding: .7rem 2rem; background: white; color: var(--green); font-weight: 700; border-radius: 50px; text-decoration: none; margin-top: .5rem; }}
    footer {{ text-align: center; padding: 2rem; font-size: .85rem; color: #888; border-top: 1px solid #eee; }}
    footer a {{ color: var(--green); text-decoration: none; }}
  </style>
</head>
<body>
<header>
  <div class="nav"><a href="../">🌳 家系図Navi</a> ＞ <a href="../guides/" style="color:white;">ガイド</a> ＞ {pillar['h1']}</div>
  <h1>{pillar['h1']}</h1>
</header>
<main>
  <p class="lead">{pillar['intro']}</p>

  {ad_block_wide()}

  {groups_html}

  {ad_block_tax()}

  <div class="cta-box">
    <h3 style="margin-bottom:.5rem;">まずは無料でシミュレーション</h3>
    <p style="font-size:.95rem;opacity:.95;">家族構成を入力するだけで、相続分・相続税・遺留分を自動計算（無料・登録不要）。</p>
    <a href="{APP_URL}" rel="noopener">家系図Naviを試す →</a>
  </div>

  {ad_block()}
</main>
<footer>
  <p>© 2026 Mirai Navi — <a href="../">家系図Navi</a> ｜ <a href="../guides/">記事一覧</a></p>
  <p style="margin-top:.5rem;font-size:.82rem;">🔗 姉妹サイト：<a href="https://mirainavi.net/?utm_source=note&utm_medium=article&utm_campaign=brand-story&utm_content=cta_text_bottom" target="_blank" rel="noopener" style="color:#16A085;">ミライNavi</a> ｜ <a href="https://teso-navi.vercel.app/" target="_blank" rel="noopener" style="color:#16A085;">手相ナビ</a> ｜ <a href="https://kakeizu-souzoku-navi.blog.jp/" target="_blank" rel="noopener" style="color:#16A085;">運営ブログ</a></p>
  <p style="margin-top:.5rem;font-size:.78rem;color:#999;">当サイトはアフィリエイト広告（プロモーション）を利用しています。｜<a href="https://yadianqiteng5-spec.github.io/kakeizu-navi-lp/about/" style="color:#16A085;">運営者情報・プライバシー</a></p>
</footer>
</body>
</html>
"""


def render_guides_index():
    cards = "\n".join(
        f'<a class="guide-card" href="../{a["slug"]}/">'
        f'<h3>{a["h1"]}</h3><p>{a["desc"]}</p></a>'
        for a in ARTICLES
    )
    table_cards = "\n".join(
        f'<a class="guide-card" href="../{qt["slug"]}/" style="border-top-color:#E67E22;">'
        f'<h3 style="color:#E67E22;">{qt["h1"]}</h3><p>{qt["desc"]}</p></a>'
        for qt in QUICK_TABLES
    )
    pillar_cards = "\n".join(
        f'<a class="guide-card" href="../{p["slug"]}/" style="border-top-color:#16A085;border-top-width:5px;">'
        f'<h3 style="color:#16A085;">📚 {p["h1"]}</h3><p>{p["desc"]}</p></a>'
        for p in PILLARS
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>相続・事業承継ガイド記事一覧｜家系図Navi</title>
  <meta name="description" content="家系図Naviが提供する相続・事業承継の解説記事一覧。法定相続分・相続税・遺留分・事業承継・遺言書・生前贈与など{len(ARTICLES)}本の専門記事を公開中。">
  <meta name="keywords" content="相続,事業承継,記事一覧,ガイド,家系図Navi">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{CANONICAL_BASE}/guides/">
  <meta property="og:title" content="相続・事業承継ガイド記事一覧｜家系図Navi">
  <meta property="og:description" content="法定相続分・相続税・遺留分・事業承継・遺言書・生前贈与など{len(ARTICLES)}本の専門記事。">
  <meta property="og:url" content="{SITE_URL}/guides/">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{ICON}">
  <link rel="icon" href="../icon_192.png">
  <style>
    :root {{ --green: #27AE60; --light-bg: #f8fdf9; --text: #2c3e50; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: var(--light-bg); color: var(--text); line-height: 1.7; }}
    header {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 2.5rem 1.5rem; text-align: center; }}
    header h1 {{ font-size: 1.9rem; margin: .5rem 0; }}
    header .nav {{ font-size: .9rem; opacity: .9; }}
    header .nav a {{ color: white; text-decoration: none; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 2.5rem 1.5rem; }}
    .guides {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.2rem; }}
    .guide-card {{ background: white; border-radius: 12px; padding: 1.4rem; box-shadow: 0 2px 8px rgba(0,0,0,.06); border-top: 3px solid var(--green); text-decoration: none; color: inherit; transition: transform .2s; }}
    .guide-card:hover {{ transform: translateY(-3px); box-shadow: 0 6px 18px rgba(0,0,0,.1); }}
    .guide-card h3 {{ font-size: 1.05rem; margin-bottom: .5rem; color: var(--green); }}
    .guide-card p {{ font-size: .88rem; color: #555; }}
    footer {{ text-align: center; padding: 2rem; font-size: .85rem; color: #888; border-top: 1px solid #eee; }}
    footer a {{ color: var(--green); text-decoration: none; }}
  </style>
</head>
<body>
<header>
  <div class="nav"><a href="../">🌳 家系図Navi</a> ＞ ガイド記事一覧</div>
  <h1>相続・事業承継ガイド</h1>
  <p style="opacity:.95;margin-top:.6rem;">専門家監修水準の解説記事を{len(ARTICLES)}本公開中</p>
</header>
<main>
  <h2 style="color:#16A085;margin-bottom:1rem;border-left:5px solid #16A085;padding-left:.8rem;">📚 まずはこちら：テーマ別 完全ガイド</h2>
  <div class="guides">
  {pillar_cards}
  </div>

  <h2 style="color:var(--green);margin:2.5rem 0 1rem;border-left:4px solid var(--green);padding-left:.8rem;">📝 解説記事（{len(ARTICLES)}本）</h2>
  <div class="guides">
  {cards}
  </div>

  <h2 style="color:#E67E22;margin:2.5rem 0 1rem;border-left:4px solid #E67E22;padding-left:.8rem;">📊 早見表（{len(QUICK_TABLES)}本）</h2>
  <div class="guides">
  {table_cards}
  </div>

  <h2 style="color:#E67E22;margin:2.5rem 0 1rem;border-left:4px solid #E67E22;padding-left:.8rem;">🛠 便利ツール</h2>
  <div class="guides">
    <a class="guide-card" href="../calculator/" style="border-top-color:#E67E22;"><h3 style="color:#E67E22;">相続税かんたん計算ツール</h3><p>遺産額と家族構成を入力して即計算。</p></a>
    <a class="guide-card" href="../cases/" style="border-top-color:#E67E22;"><h3 style="color:#E67E22;">ケーススタディ集（20例）</h3><p>典型的な相続パターンを具体的に解説。</p></a>
  </div>

  <h2 style="color:var(--green);margin:2.5rem 0 1rem;border-left:4px solid var(--green);padding-left:.8rem;">📖 リファレンス</h2>
  <div class="guides">
    <a class="guide-card" href="../glossary/"><h3>用語集（40語）</h3><p>相続・事業承継の専門用語を解説。</p></a>
    <a class="guide-card" href="../about/"><h3>家系図Naviについて</h3><p>運営方針・編集ポリシー・計算精度。</p></a>
  </div>
  {ad_block()}
</main>
<footer>
  <p>© 2026 Mirai Navi — <a href="../">家系図Navi / Family Tree Guide</a></p>
  <p style="margin-top:.5rem;font-size:.82rem;">🔗 姉妹サイト：<a href="https://mirainavi.net/?utm_source=note&utm_medium=article&utm_campaign=brand-story&utm_content=cta_text_bottom" target="_blank" rel="noopener" style="color:#16A085;">ミライNavi</a> ｜ <a href="https://teso-navi.vercel.app/" target="_blank" rel="noopener" style="color:#16A085;">手相ナビ</a> ｜ <a href="https://kakeizu-souzoku-navi.blog.jp/" target="_blank" rel="noopener" style="color:#16A085;">運営ブログ</a></p>
  <p style="margin-top:.5rem;font-size:.78rem;color:#999;">当サイトはアフィリエイト広告（プロモーション）を利用しています。｜<a href="https://yadianqiteng5-spec.github.io/kakeizu-navi-lp/about/" style="color:#16A085;">運営者情報・プライバシー</a></p>
</footer>
</body>
</html>
"""


ARTICLES += [
    {
        "slug": "retirement-money",
        "title": "退職金の相続税｜500万円×法定相続人数の非課税枠",
        "h1": "退職金の相続税扱い",
        "desc": "在職中の死亡で支給される死亡退職金の相続税評価、500万円×法定相続人数の非課税枠、弔慰金の取り扱いを解説。",
        "keywords": "退職金,相続税,非課税枠,弔慰金,死亡退職金",
        "lead": "在職中に死亡した場合に遺族へ支給される<strong>死亡退職金</strong>は「みなし相続財産」として相続税の課税対象。非課税枠と弔慰金の扱いを整理します。",
        "sections": [
            ("非課税枠（500万円×法定相続人数）", "<p>死亡退職金は<strong>500万円 × 法定相続人数</strong>まで非課税（相続税法12条1項6号）。生命保険金と同じ計算式で、両方とも適用可能。</p>"),
            ("対象となる死亡退職金", "<ul><li>死亡後3年以内に支給が確定したもの</li><li>退職給与規程に基づくもの</li><li>役員退職慰労金（株主総会決議が必要）</li></ul>"),
            ("弔慰金の非課税枠", "<p>弔慰金は死亡退職金とは別枠で：</p><ul><li><strong>業務上死亡</strong>：賃金月額×36ヶ月分まで非課税</li><li><strong>業務外死亡</strong>：賃金月額×6ヶ月分まで非課税</li></ul><p>超過分は退職金として課税対象。</p>"),
            ("受取人による違い", "<p>受取人が指定されていれば<strong>受取人の固有財産</strong>として遺産分割対象外。指定がなければ相続財産として分割対象。</p>"),
        ],
        "faqs": [
            ("死亡退職金は所得税もかかりますか？", "いいえ、相続税の課税対象になるため<strong>所得税は非課税</strong>です（所得税法9条1項16号）。"),
            ("3年経過後に支給された退職金は？", "相続税ではなく<strong>受取人の一時所得</strong>として所得税課税。"),
            ("社葬の香典・供花は誰のものですか？", "原則として<strong>喪主固有の財産</strong>で相続税の課税対象外。社会通念上相当な範囲なら所得税も非課税。"),
        ],
    },
    {
        "slug": "insurance-strategy",
        "title": "生命保険を使った相続対策｜非課税枠と代償分割原資",
        "h1": "生命保険の相続活用法",
        "desc": "500万円×法定相続人数の非課税枠を活用した節税、代償分割の原資確保、納税資金準備など、生命保険を使った相続対策を解説。",
        "keywords": "生命保険,相続対策,非課税枠,代償分割,納税資金,終身保険",
        "lead": "<strong>生命保険</strong>は相続対策の万能ツールです。非課税枠・受取人指定・現金化容易など他の財産にない特性を活用しましょう。",
        "sections": [
            ("非課税枠の活用", "<p>500万円 × 法定相続人数まで非課税（相続税法12条）。預貯金で残すより評価額が下がるため、<strong>現金を保険に変えるだけで節税</strong>に。</p>"),
            ("受取人固有財産", "<p>受取人指定の死亡保険金は<strong>遺産分割の対象外</strong>（最判昭40.2.2）。遺留分の算定基礎にも原則含まれません（特別受益にあたる場合を除く）。特定の相続人に確実に渡せる強み。</p>"),
            ("代償分割の原資", "<p>不動産を長男が取得する代わりに次男に金銭支払（代償分割）する場合、その<strong>原資を保険金で確保</strong>できます。納税資金の準備にも有効。</p>"),
            ("一時払終身保険の活用", "<p>高齢者でも加入可能な一時払終身保険は、預金を保険に変えるだけで非課税枠を作れる節税策。健康診断不要の商品も多い。</p>"),
            ("注意点", "<ul><li>保険金額が著しく高額だと特別受益認定リスク</li><li>受取人が先に死亡した場合の処理</li><li>契約者・被保険者・受取人の関係で課税が変わる（相続税 / 所得税 / 贈与税）</li></ul>"),
        ],
        "faqs": [
            ("受取人を相続人以外にした場合は？", "相続税の課税対象になりますが、<strong>非課税枠は使えません</strong>。非課税枠は法定相続人のみ。"),
            ("生命保険金は遺留分の対象ですか？", "原則として対象外ですが、保険金額が相続財産に比して著しく高額な場合は特別受益として持戻しの対象になり得ます（最判平16.10.29）。"),
            ("契約者と受取人が同じ場合は？", "<strong>所得税（一時所得）</strong>の課税対象に。相続税より高負担になることが多いため要注意。"),
        ],
    },
    {
        "slug": "corporate-shares",
        "title": "非上場株式の相続税評価｜類似業種比準・純資産・配当還元",
        "h1": "非上場株式の相続税評価",
        "desc": "中小企業の自社株評価方法（類似業種比準方式・純資産方式・配当還元方式）、評価減のテクニック、事業承継への影響を解説。",
        "keywords": "非上場株式,自社株,相続税評価,類似業種比準,純資産価額,配当還元",
        "lead": "中小企業オーナーの相続では<strong>非上場株式</strong>の評価額が遺産の大部分を占めるケースが多い。評価方式を理解し、適切な対策が必須です。",
        "sections": [
            ("3つの評価方式", "<ul><li><strong>類似業種比準方式</strong>：同業上場会社の平均値と比較。配当・利益・純資産で評価</li><li><strong>純資産価額方式</strong>：会社の純資産を相続税評価額で計算</li><li><strong>配当還元方式</strong>：少数株主（同族外）が取得する場合の簡易計算</li></ul>"),
            ("会社規模による使い分け", "<p>会社規模を大会社・中会社・小会社に区分し、各規模に応じて方式を併用：</p><ul><li>大会社：類似業種比準方式が原則</li><li>中会社：類似業種比準と純資産価額の併用</li><li>小会社：純資産価額方式が原則（類似との選択可）</li></ul>"),
            ("評価減のテクニック", "<ul><li>役員退職金の支給で純資産を圧縮</li><li>類似業種の比準要素を意図的に下げる（配当抑制等）</li><li>不動産購入による含み損益の活用</li><li>持株会社化（株式保有特定会社判定に注意）</li></ul>"),
            ("事業承継税制との組合せ", "<p>評価額を圧縮した上で<strong>事業承継税制</strong>（円滑化法）を適用すれば、相続税・贈与税の納税猶予で実質ゼロ円承継も可能。要件確認は必須。</p>"),
        ],
        "faqs": [
            ("配当還元方式は誰でも使えますか？", "いいえ、<strong>同族株主以外</strong>または<strong>同族株主の中でも一定要件を満たす者</strong>が取得する株式に限定されます。"),
            ("会社の決算が悪い年に贈与すべき？", "原則そうですが、利益操作と認定されると否認リスク。3年平均で計算する要素もあり単年だけでは効果限定的。"),
            ("自社株を信託に入れる場合の評価は？", "信託受益権としての評価になりますが、実質的には原資産と同じ評価。設計次第で議決権と経済価値を分離可能。"),
        ],
    },
    {
        "slug": "consulting-cost",
        "title": "相続専門家の費用相場｜税理士・弁護士・司法書士",
        "h1": "相続専門家の費用相場",
        "desc": "税理士の相続税申告報酬、弁護士の遺産分割調停費用、司法書士の相続登記費用など、相続専門家への報酬相場を網羅解説。",
        "keywords": "相続,専門家,費用,報酬,税理士,弁護士,司法書士,相場",
        "lead": "相続では複数の専門家への相談が必要になることが多い。<strong>報酬相場</strong>を知り、無駄なく依頼しましょう。",
        "sections": [
            ("税理士：相続税申告", "<p>遺産総額の<strong>0.5〜1.0%</strong>が相場。例：</p><ul><li>遺産5,000万円：30〜50万円</li><li>遺産1億円：50〜100万円</li><li>遺産3億円：150〜300万円</li></ul><p>不動産多数・非上場株式・国際相続は加算あり。書面添付制度対応や事前シミュレーション込みかで変動。</p>"),
            ("弁護士：遺産分割・紛争", "<ul><li>初回相談：30分5,000円〜（無料事務所も多い）</li><li>調停代理：着手金30〜50万円 + 成功報酬（経済的利益の10〜16%）</li><li>訴訟代理：調停より割増</li></ul>"),
            ("司法書士：相続登記", "<ul><li>相続登記：6〜10万円/件（不動産1物件）</li><li>遺産分割協議書作成：3〜10万円</li><li>戸籍収集代行：1〜3万円</li></ul>"),
            ("行政書士：書類作成", "<p>協議書作成・遺言書作成のみなら<strong>3〜10万円</strong>。登記・申告・代理交渉はできないため、シンプル案件向け。</p>"),
            ("費用を抑えるポイント", "<ul><li>複数事務所で見積もり比較</li><li>戸籍収集など自力でできることは自分で</li><li>専門家のワンストップ事務所を選ぶ</li><li>初回無料相談を活用</li></ul>"),
        ],
        "faqs": [
            ("税理士費用は相続税申告で経費にできますか？", "相続税の申告報酬は<strong>準確定申告（所得税）では経費にできません</strong>。相続税の計算上の控除もなし。"),
            ("弁護士費用を相手に請求できますか？", "原則として各自負担。訴訟で勝訴しても弁護士費用全額を相手に請求するのは困難（一部認められる場合あり）。"),
            ("無料相談だけで解決することはありますか？", "シンプルなケースなら可能ですが、登記・申告等の実務は依頼が必要。初回無料相談で見積もりを取り判断するのが現実的。"),
        ],
    },
    {
        "slug": "endlife-checklist",
        "title": "終活チェックリスト｜元気なうちにやるべき30項目",
        "h1": "終活で元気なうちにやるべきこと",
        "desc": "遺言書・エンディングノート・財産目録・延命治療の意思表示など、家族のために生前にやるべき30項目をチェックリスト形式で整理。",
        "keywords": "終活,チェックリスト,エンディングノート,遺言書,生前整理",
        "lead": "<strong>終活</strong>は残される家族への最大の贈り物です。判断能力があるうちに準備すべき項目をチェックリストで整理しました。",
        "sections": [
            ("法的な準備", "<ul><li>□ 遺言書の作成（公正証書推奨）</li><li>□ 家族信託または任意後見契約の検討</li><li>□ 法定相続人の確認（戸籍取得）</li><li>□ 遺留分への配慮確認</li><li>□ 遺言執行者の指定</li></ul>"),
            ("財産の整理", "<ul><li>□ 財産目録の作成（不動産・預貯金・有価証券・暗号資産）</li><li>□ 銀行口座の整理・一本化</li><li>□ 不要な保険・サブスクの解約</li><li>□ 借入金・連帯保証の確認</li><li>□ デジタル資産（SNS・写真）の整理</li><li>□ 暗号資産の秘密鍵引き継ぎ準備</li></ul>"),
            ("税金対策", "<ul><li>□ 相続税の試算（家系図Navi等で概算）</li><li>□ 暦年贈与または相続時精算課税の活用</li><li>□ 小規模宅地等の特例適用要件の確認</li><li>□ 配偶者居住権の検討</li><li>□ 生命保険の非課税枠活用</li></ul>"),
            ("医療・介護の意思表示", "<ul><li>□ 延命治療への意思（リビングウィル）</li><li>□ 臓器提供の意思</li><li>□ かかりつけ医の連絡先共有</li><li>□ お薬手帳・既往歴の整理</li><li>□ 介護方針の家族との共有</li></ul>"),
            ("葬儀・お墓", "<ul><li>□ 葬儀のスタイル（家族葬・直葬等）の意思表示</li><li>□ 葬儀社の事前相談</li><li>□ お墓・納骨先の決定</li><li>□ 遺影写真の準備</li><li>□ 葬儀費用の準備</li></ul>"),
            ("家族へのメッセージ", "<ul><li>□ エンディングノートの作成</li><li>□ 家族写真・思い出の整理</li><li>□ 友人・恩人への連絡先リスト</li><li>□ 大切な人へのメッセージ動画</li></ul>"),
        ],
        "faqs": [
            ("エンディングノートに法的効力はありますか？", "ありません。財産分配の意思を残すには別途<strong>遺言書</strong>が必要。エンディングノートは家族への情報共有として活用。"),
            ("何歳から終活を始めるべきですか？", "明確な目安はありませんが、60代から徐々に着手するのが一般的。判断能力がしっかりしている時期にこそ重要な決定をしておくべき。"),
            ("家族と話すのが気が引けるのですが", "家系図Naviのようなツールで「数字」を一緒に見ながら話すのが切り出しやすい。「子供にいくら税金を払わせるか」の現実が話題提供になります。"),
        ],
    },
]

ARTICLES += [
    {
        "slug": "inheritance-overseas",
        "title": "海外居住者の相続｜在外邦人・海外財産の手続き",
        "h1": "海外居住者の相続手続き",
        "desc": "海外に住む相続人、海外不動産・口座を持つ場合の相続手続き、サイン証明・在留証明の取得、相続税の納税義務範囲を解説。",
        "keywords": "海外居住者,海外相続,在外邦人,サイン証明,在留証明,海外財産",
        "lead": "<strong>海外居住者の相続</strong>は通常の相続より手続きが煩雑です。日本の印鑑証明書がないなど特有の論点を整理します。",
        "sections": [
            ("印鑑証明の代わり：サイン証明", "<p>海外在住者は印鑑登録ができないため、<strong>在外公館（大使館・領事館）でサイン証明</strong>を取得します。遺産分割協議書に署名し、領事の前で確認後に認証してもらう方式が一般的。</p>"),
            ("在留証明", "<p>住民票の代わりに<strong>在留証明</strong>を在外公館で取得。相続税申告や不動産登記で必要になります。発行は無料か手数料数千円程度。</p>"),
            ("相続税の納税義務", "<p>海外在住でも、被相続人または相続人が<strong>10年以内に日本に住所を有していた場合</strong>は全世界財産が課税対象（相続税法1条の3）。最近の改正で課税範囲が拡大されています。</p>"),
            ("海外不動産・口座の扱い", "<ul><li>現地でのプロベイト手続き（裁判所手続き）が必要な国あり（米国・英国等）</li><li>海外口座は<strong>CRS</strong>で自動報告され、隠匿は実質不可能</li><li>為替変動を考慮した評価</li><li>外国税額控除（相続税法20条の2）で二重課税調整</li></ul>"),
            ("実務のポイント", "<ul><li>早期に国際相続に詳しい税理士・弁護士へ相談</li><li>各国で個別の遺言書を作成</li><li>納税資金の為替リスクヘッジ</li><li>申告期限10ヶ月以内の延長制度を検討</li></ul>"),
        ],
        "faqs": [
            ("永住権を持つ場合は？", "国籍ではなく<strong>住所地</strong>で判断されます。日本人で永住権を持ちつつ海外に長期在住なら制限納税義務者になり得ます。"),
            ("海外で作った遺言は日本で有効？", "原則として<strong>遺言作成地の方式</strong>に従っていれば日本でも有効です（遺言の方式の準拠法に関する法律2条）。"),
            ("海外不動産は小規模宅地の特例使える？", "<strong>使えません</strong>。小規模宅地等の特例は国内の土地に限定。"),
        ],
    },
    {
        "slug": "will-rewrite",
        "title": "遺言書の書き換え・撤回｜複数遺言がある場合の優先順位",
        "h1": "遺言書の書き換えと撤回の方法",
        "desc": "遺言書を書き換える方法、複数遺言の優先順位、自筆証書から公正証書への変更、撤回の意思表示など民法1022〜1027条を解説。",
        "keywords": "遺言書,書き換え,撤回,変更,複数遺言,民法1022条",
        "lead": "遺言書は何度でも<strong>書き換え可能</strong>です。複数の遺言がある場合の優先順位や撤回の方法を整理します。",
        "sections": [
            ("遺言の撤回は自由（民法1022条）", "<p>遺言者は生前いつでも遺言の全部または一部を撤回できます。撤回方法は<strong>新しい遺言書を作成</strong>するのが一般的。前の遺言書を破棄しても撤回扱い。</p>"),
            ("複数遺言の優先順位", "<p>新しい遺言と古い遺言が抵触する場合、<strong>抵触する部分について</strong>古い遺言が撤回されたものとみなされます（民法1023条）。一部のみ抵触なら、他の部分は前の遺言が有効。</p>"),
            ("自筆から公正証書への切替", "<p>遺言の方式変更は自由。先に作成した自筆証書遺言を、後で公正証書遺言で全面書き換えるのは安全策として推奨。古い自筆証書は破棄を。</p>"),
            ("撤回が成立する行為", "<ul><li>新しい遺言書の作成（抵触部分のみ撤回）</li><li>遺言書の故意の破棄（民法1024条）</li><li>遺贈目的物の故意の破棄</li><li>遺贈目的物を生前に処分（売却・贈与等）</li></ul>"),
            ("撤回後の復活", "<p>撤回行為（新しい遺言）自体が撤回・取消された場合、原則として<strong>元の遺言は復活しない</strong>（民法1025条）。例外：詐欺・強迫による場合のみ復活。</p>"),
        ],
        "faqs": [
            ("結婚・離婚・出産で遺言は無効になる？", "自動的には無効になりません。ただし家族構成変化で遺留分等の関係が変わるため、<strong>再作成が推奨</strong>。"),
            ("遺言書を訂正したい場合は？", "自筆証書の訂正は厳格な要件（変更場所の指示・付記・署名・押印）あり（民法968条3項）。誤って無効になりやすいため、書き直す方が安全。"),
            ("公正証書遺言を書き直す費用は？", "原則として初回と同じ手数料（数万円〜）が発生します。証人2名も再度必要。"),
        ],
    },
    {
        "slug": "tax-investigation",
        "title": "相続税の税務調査｜対象になりやすいケースと対策",
        "h1": "相続税の税務調査対応",
        "desc": "相続税申告後の税務調査の流れ、対象になりやすいケース、調査官が見るポイント、書面添付制度による調査回避策を解説。",
        "keywords": "相続税,税務調査,書面添付制度,加算税,名義預金,生前贈与",
        "lead": "相続税申告の約<strong>1割が税務調査</strong>の対象に。調査官の着眼点を理解し、適正申告と書面添付制度で調査リスクを下げましょう。",
        "sections": [
            ("税務調査の対象になりやすいケース", "<ul><li>遺産総額が3億円超</li><li>申告漏れの可能性が高い財産（名義預金・タンス預金）</li><li>生前の高額な現金引出</li><li>贈与税申告との不整合</li><li>不動産・株式の評価が複雑</li><li>海外財産の保有</li></ul>"),
            ("調査官が見るポイント", "<ul><li><strong>名義預金</strong>：子・孫名義だが実質被相続人の預金</li><li>10年以内の<strong>生前贈与</strong>の有無（贈与税申告漏れ）</li><li>死亡直前の<strong>現金引出</strong>（葬儀費用以外の使途不明金）</li><li>家族の収入と資産の不一致</li><li>骨董品・貴金属・暗号資産の申告漏れ</li></ul>"),
            ("書面添付制度（税理士法33条の2）", "<p>税理士が「適正に確認した」旨の<strong>書面を添付</strong>すれば、調査前に税理士が意見聴取される機会あり。調査確率が下がり、調査時の修正で済むことも。利用には別途報酬5〜15万円程度。</p>"),
            ("調査が来たら", "<ul><li>事前通知から実地調査まで通常1〜2週間</li><li>通常2日間（1日目：質問、2日目：書類確認）</li><li>申告書・通帳・契約書類等を準備</li><li>必ず税理士の立会いを依頼</li><li>その場で即答せず、不明点は「確認してから回答」</li></ul>"),
            ("修正申告と加算税", "<p>申告漏れが見つかると：</p><ul><li><strong>過少申告加算税</strong>：原則10%、500万円超部分は15%</li><li><strong>重加算税</strong>：仮装隠蔽があれば35〜40%</li><li><strong>延滞税</strong>：年利数%</li></ul>"),
        ],
        "faqs": [
            ("税務調査はいつ来ますか？", "申告後<strong>1〜2年後</strong>に行われることが多い。秋〜冬の調査が多めの傾向。"),
            ("名義預金と判定されないためには？", "①受贈者が口座を管理（通帳・印鑑を自分で保管）②贈与契約書を毎年作成③贈与税申告（110万円超なら必須）。"),
            ("税務調査を拒否できますか？", "正当な理由なく拒否すると<strong>罰則</strong>（1年以下の懲役・50万円以下の罰金）あり。事前通知の日程変更交渉は可。"),
        ],
    },
    {
        "slug": "deferred-payment",
        "title": "相続税の延納と物納｜金銭納付困難な時の対処法",
        "h1": "相続税の延納と物納制度",
        "desc": "相続税を金銭一括納付できない場合の延納（最長20年分割）と物納（不動産等で納付）の要件・手続き・利子税を解説。",
        "keywords": "相続税,延納,物納,利子税,担保,金銭納付困難",
        "lead": "相続税は<strong>金銭一括納付</strong>が原則ですが、不動産中心の遺産等で困難な場合は延納・物納が認められます。",
        "sections": [
            ("延納（最長20年の分割払い）", "<p>金銭納付困難な場合、最長<strong>20年</strong>の分割払いが可能（相続税法38条）。利子税（年0.7〜1.3%程度）がかかります。担保提供が必要（不動産・国債等）。</p>"),
            ("延納の要件", "<ul><li>納付すべき相続税が<strong>10万円超</strong></li><li>金銭納付が困難な事由</li><li>申告期限までに延納申請書を提出</li><li>原則として担保を提供</li><li>延納分相当の利子税の支払い</li></ul>"),
            ("物納（不動産等で納付）", "<p>延納でも金銭納付困難な場合、<strong>不動産・国債・株式</strong>等で納付可能（相続税法41条）。優先順位は①不動産・国債②船舶等③社債・株式・証券。</p>"),
            ("物納適格財産の制限", "<ul><li>抵当権付き不動産はNG</li><li>境界不明・賃貸中の物件は基本NG</li><li>共有持分・係争中物件はNG</li><li>管理処分不適格財産は除外</li></ul>"),
            ("延納と物納の使い分け", """<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
<thead><tr style="background:#27AE60;color:white;"><th style="padding:.5rem;border:1px solid #ddd;">条件</th><th style="padding:.5rem;border:1px solid #ddd;">推奨</th></tr></thead>
<tbody>
<tr><td style="padding:.5rem;border:1px solid #ddd;">将来の現金収入見込みあり</td><td style="padding:.5rem;border:1px solid #ddd;">延納</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">遺産の大半が不動産で売却困難</td><td style="padding:.5rem;border:1px solid #ddd;">物納</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">不動産の収益性低い</td><td style="padding:.5rem;border:1px solid #ddd;">物納検討</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">短期で完納できる見込み</td><td style="padding:.5rem;border:1px solid #ddd;">延納</td></tr>
</tbody></table>"""),
        ],
        "faqs": [
            ("延納中に完納できるようになったら？", "途中で繰上完納すれば<strong>残期間の利子税が不要</strong>になります。資金ができたら早期完納がお得。"),
            ("物納に出した不動産の評価額は？", "<strong>相続税評価額</strong>（路線価ベース）で物納されます。市場価格より低いことが多く、結果的に不利になるケースも。"),
            ("延納・物納の申請却下リスクは？", "金銭納付可能と判断されれば却下。預貯金や有価証券がある場合は先にそちらで納付するよう求められます。"),
        ],
    },
    {
        "slug": "adoption-pros-cons",
        "title": "養子縁組の相続メリット・デメリット｜節税効果と注意点",
        "h1": "養子縁組による相続対策",
        "desc": "孫を養子にする節税効果、基礎控除・生命保険非課税枠の拡大、2割加算、家族関係への影響など、養子縁組による相続対策の全体像を解説。",
        "keywords": "養子縁組,孫養子,相続対策,2割加算,基礎控除,節税",
        "lead": "<strong>養子縁組</strong>は相続税対策として有効な手段ですが、思わぬデメリットもあります。総合的な視点で判断しましょう。",
        "sections": [
            ("メリット1：基礎控除の拡大", "<p>養子1人で基礎控除が<strong>600万円増</strong>。生命保険・退職金の非課税枠も500万円ずつ増えるため、節税効果が大きい。</p>"),
            ("メリット2：法定相続人を増やせる", "<p>子が一人っ子の場合、孫を養子にすることで税率を下げる効果も。累進税率の高い帯域から低い帯域へ移動できる。</p>"),
            ("メリット3：世代飛ばしの相続", "<p>孫を養子にすれば、子の世代を飛ばして孫に直接相続でき、<strong>一段階分の相続税を回避</strong>できます。</p>"),
            ("デメリット1：孫養子の2割加算", "<p>孫養子（代襲相続人を除く）が相続する場合、相続税が<strong>2割加算</strong>されます（相続税法18条）。世代飛ばし効果と相殺評価が必要。</p>"),
            ("デメリット2：人数算入制限", "<p>基礎控除・生命保険非課税枠の計算では、<strong>実子あり1人/実子なし2人</strong>まで（相続税法15条2項）。実子1人と養子2人なら、計算上は実子1人＋養子1人として扱われます。</p>"),
            ("デメリット3：家族関係への影響", "<ul><li>養子は実親との関係も継続（普通養子）</li><li>養子の配偶者・子も相続関係に</li><li>離縁できるが家庭裁判所の手続き要</li><li>遺留分を主張される可能性</li></ul>"),
            ("特別養子との違い", "<p>特別養子は<strong>実親との関係終了</strong>かつ<strong>人数算入制限の対象外</strong>。ただし15歳未満の子のみで家裁審判が必要。節税目的では使えない。</p>"),
        ],
        "faqs": [
            ("養子縁組はいつでもできますか？", "<strong>養子が15歳以上なら本人の意思</strong>、未満なら法定代理人の同意で。届出のみで成立（普通養子）。"),
            ("養子縁組を相続税対策と認定されるリスクは？", "近年の最高裁判例（最判平29.1.31）では、節税目的でも<strong>真意の養子縁組なら有効</strong>と判断。ただし極端な租税回避は否認リスク。"),
            ("配偶者の連れ子は養子にすべき？", "養子縁組しないと相続権なし。確実に相続させたいなら養子縁組または遺贈で対応。"),
        ],
    },
]

ARTICLES += [
    {
        "slug": "nominee-deposit",
        "title": "名義預金とは｜税務調査で否認されないための対策",
        "h1": "名義預金と税務調査リスク",
        "desc": "子・孫名義の口座でも実質的に被相続人の財産と認定される「名義預金」の判定基準と、認定を回避するための贈与契約・口座管理のポイントを解説。",
        "keywords": "名義預金,贈与契約書,税務調査,贈与税申告,相続税申告漏れ",
        "lead": "<strong>名義預金</strong>は相続税の税務調査で最も指摘されやすい論点。子・孫名義でも実質判定で被相続人の財産とされ追徴課税の対象になります。",
        "sections": [
            ("名義預金とみなされる典型例", "<ul><li>子・孫名義の通帳・印鑑を被相続人が保管</li><li>受贈者本人が口座の存在を知らない</li><li>受贈者が引き出し・運用していない</li><li>贈与契約書がない</li><li>110万円超の贈与なのに贈与税申告がない</li></ul>"),
            ("認定回避の5原則", "<ol><li><strong>毎年贈与契約書を作成</strong>（双方署名押印）</li><li>受贈者本人が口座を開設・管理</li><li>通帳・印鑑・キャッシュカードを受贈者が保管</li><li>110万円超なら必ず贈与税申告</li><li>受贈者が自分の意思で運用・引出</li></ol>"),
            ("生前のチェックリスト", "<ul><li>□ 子・孫名義の口座を本人に通知済み</li><li>□ 通帳・印鑑を本人が保管</li><li>□ 過去の贈与記録（契約書）を整備</li><li>□ 贈与税申告書の控えを保管</li><li>□ 入金パターンが「定期贈与」と認定されないよう変化</li></ul>"),
            ("税務調査で発覚した場合", "<p>相続財産に追加され、<strong>相続税＋過少申告加算税（10〜15%）＋延滞税</strong>。仮装隠蔽認定なら<strong>重加算税35〜40%</strong>。10年以上経過した贈与でも、名義預金と認定されると相続財産扱いになります。</p>"),
        ],
        "faqs": [
            ("孫の進学資金として貯めているお金は？", "毎年110万円以内なら贈与税非課税ですが、贈与契約書を作り孫本人が管理する必要があります。教育資金一括贈与の非課税特例（1,500万円）も検討。"),
            ("妻名義の専業主婦の貯金は？", "夫の収入から積み立てた場合、実質夫の財産とされる「<strong>妻名義預金</strong>」リスクあり。夫婦間でも贈与契約の整備が安全。"),
            ("過去の名義預金を今から贈与扱いに戻せますか？", "改めて贈与契約書を作成し、本人管理に切り替えるのが基本。ただし過去分の贈与税申告漏れの責任は残るため税理士相談を。"),
        ],
    },
    {
        "slug": "shared-property",
        "title": "共有名義不動産の相続｜トラブル回避と持分整理",
        "h1": "共有名義不動産の相続",
        "desc": "夫婦・兄弟の共有名義不動産が相続でさらに細分化されるリスク、共有解消の手法、持分売買・共有物分割訴訟までを解説。",
        "keywords": "共有名義,不動産,相続,持分,共有物分割,共有解消",
        "lead": "<strong>共有名義不動産</strong>は相続で持分がさらに細分化し、深刻なトラブルの温床に。早期の整理が必須です。",
        "sections": [
            ("共有名義の問題点", "<ul><li>売却・賃貸に<strong>全員の同意</strong>が必要（民法251条）</li><li>持分の細分化で利害関係者激増</li><li>遠縁の親族と共有状態になると意思決定不能</li><li>持分割合と固定資産税負担で揉める</li></ul>"),
            ("共有解消の主な方法", "<ol><li><strong>持分売買</strong>：他の共有者間で持分を売買して単独所有化</li><li><strong>共有物分割協議</strong>：現物分割・代償分割・換価分割</li><li><strong>共有物分割訴訟</strong>：協議不成立時に裁判所で分割（民法258条）</li><li><strong>不動産競売</strong>：分割不能な場合の最終手段</li></ol>"),
            ("生前の対策", "<ul><li>共有持分を遺言で特定者に集約</li><li>持分を生前に売却・贈与</li><li>家族信託で意思決定を一本化</li><li>収益不動産化して持分按分で現金分配</li></ul>"),
            ("税務上の注意", "<p>持分の売買・贈与には<strong>譲渡所得税・贈与税</strong>が発生。共有物分割では現物割合と評価額の差で課税対象になることも。事前のシミュレーションが必須。</p>"),
        ],
        "faqs": [
            ("持分だけを売却できますか？", "可能です。ただし市場価格より大幅に低くなる（買い手限定のため）。不動産買取業者には専門業者あり。"),
            ("音信不通の共有者がいる場合は？", "不在者財産管理人選任（家裁）または失踪宣告で解決。長期的には共有物分割訴訟も視野に。"),
            ("配偶者居住権と共有はどう違いますか？", "配偶者居住権は<strong>使用権のみ</strong>で所有権ではないため、共有特有の意思決定問題が回避できます。"),
        ],
    },
    {
        "slug": "mortgage-inheritance",
        "title": "住宅ローンと相続｜団信で残債が消える仕組み",
        "h1": "住宅ローン残債の相続",
        "desc": "住宅ローン契約者が死亡した場合の団体信用生命保険（団信）による残債消滅、団信未加入時の処理、ペアローンと相続を解説。",
        "keywords": "住宅ローン,相続,団信,団体信用生命保険,残債,ペアローン",
        "lead": "<strong>住宅ローン</strong>は契約者死亡時に団信で完済される仕組み。例外パターンを知っておくことが重要です。",
        "sections": [
            ("団信の基本", "<p>大半の住宅ローンに<strong>団体信用生命保険（団信）</strong>が付帯。契約者が死亡または高度障害になると、保険金で<strong>残債が完済</strong>され、相続人はローン無しで不動産を取得できます。</p>"),
            ("団信未加入のケース", "<ul><li>フラット35（団信任意加入）で未加入</li><li>健康上の理由で団信加入できなかった</li><li>古い時代のローンで団信なし</li><li>事業用融資（住宅ローンと別物）</li></ul><p>この場合、残債は<strong>相続債務</strong>として通常の相続対象に。相続放棄も選択肢に。</p>"),
            ("ペアローン・収入合算の相続", "<ul><li><strong>ペアローン</strong>：夫婦それぞれが債務者。死亡した方の分は団信で完済、生存者の分は残る</li><li><strong>収入合算（連帯債務）</strong>：両者が債務者。死亡者分のみ団信完済</li><li><strong>連帯保証</strong>：主債務者は1人。連帯保証人の死亡では完済されない</li></ul>"),
            ("団信のチェックポイント", "<ol><li>団信加入の有無を契約書で確認</li><li>3大疾病・がん特約付き団信か確認</li><li>団信免責期間（契約から1〜2年）に注意</li><li>住宅以外の借入（カードローン等）は対象外</li></ol>"),
        ],
        "faqs": [
            ("団信で完済した家は相続税対象？", "はい、<strong>不動産は相続税の対象</strong>。ただし債務はゼロなので、評価額そのまま課税。小規模宅地等の特例で評価減可能。"),
            ("死亡後すぐに団信は適用されますか？", "金融機関への死亡連絡→団信請求→保険会社の審査→完済まで<strong>2〜3ヶ月</strong>かかります。その間の月々の返済は引き続き必要。"),
            ("団信加入のローンを借り換えると？", "新ローンで再加入が必要。年齢・健康状態で加入不可になるリスクがあるため要注意。"),
        ],
    },
    {
        "slug": "siblings-only-inheritance",
        "title": "兄弟姉妹のみが相続人の場合｜遺留分なし・代襲は甥姪まで",
        "h1": "兄弟姉妹だけが相続人のケース",
        "desc": "配偶者・子・親がいない場合の兄弟姉妹相続。遺留分なし、代襲は甥姪まで（一代限り）、相続税2割加算、半血兄弟の1/2など特殊ルールを解説。",
        "keywords": "兄弟姉妹,相続,遺留分なし,甥姪,代襲,2割加算,半血兄弟",
        "lead": "配偶者・子・親がいない方の相続では<strong>兄弟姉妹</strong>が相続人になります。子の相続とは大きく異なるルールに注意。",
        "sections": [
            ("兄弟姉妹相続の特徴", "<ul><li>第3順位の相続人（民法889条）</li><li><strong>遺留分なし</strong>（民法1042条）→ 遺言で完全に排除可能</li><li>代襲は<strong>甥姪まで</strong>の一代限り（民法889条2項）</li><li>相続税は<strong>2割加算</strong>（相続税法18条）</li><li>半血兄弟（親の片方のみ同じ）は全血の<strong>1/2</strong>（民法900条4号但書）</li></ul>"),
            ("遺言書の重要性", "<p>子のいない夫婦で、配偶者に全財産を残したい場合、<strong>遺言書がないと配偶者と兄弟姉妹で遺産分割</strong>に。配偶者3/4、兄弟姉妹1/4が法定相続分。遺言で「配偶者に全部」とすれば兄弟姉妹に遺留分がないため確実に配偶者へ。</p>"),
            ("計算例：兄弟3人で相続", "<p>遺産6,000万円、配偶者なし、子なし、親なし、兄弟3人（うち1人は異母兄弟）の場合：</p><ul><li>全血兄弟2人：各 6,000 × 2/(2+2+1) = <strong>2,400万円</strong></li><li>半血兄弟1人：6,000 × 1/(2+2+1) = <strong>1,200万円</strong></li></ul>"),
            ("甥姪の代襲", "<p>兄弟姉妹が先に死亡している場合、その子（甥姪）が代襲相続。ただし<strong>甥姪の子（再代襲）は不可</strong>（民法889条2項は887条2項の準用なし）。子の代襲が無限なのと対照的。</p>"),
            ("相続手続きの実務", "<ul><li>戸籍収集が大変（被相続人の両親まで遡る必要）</li><li>兄弟姉妹の死亡で甥姪まで追跡</li><li>音信不通の兄弟がいるケース多</li><li>遺産分割に時間がかかりがち</li></ul>"),
        ],
        "faqs": [
            ("子のいない夫婦で兄弟と仲が悪い場合は？", "<strong>必ず公正証書遺言</strong>で「配偶者に全部」と書きましょう。兄弟姉妹に遺留分がないため、遺言が完全に有効に。"),
            ("甥姪に相続させたくない場合は？", "兄弟姉妹（とその代襲）に遺留分はないので、遺言で完全に排除可能。"),
            ("兄弟姉妹の相続税は2割増しですか？", "はい、配偶者・1親等血族以外なので2割加算（相続税法18条）。子なし夫婦が配偶者死亡後に甥姪に相続させると、2割加算で税負担増。"),
        ],
    },
    {
        "slug": "freelance-inheritance",
        "title": "個人事業主・フリーランスの相続｜事業と債務の引継ぎ",
        "h1": "個人事業主・フリーランスの相続",
        "desc": "個人事業主の事業承継、事業用資産・債務の引継ぎ、青色申告承認、消費税課税事業者の届出など、相続後の事業継続に必要な手続きを解説。",
        "keywords": "個人事業主,フリーランス,相続,事業承継,青色申告,事業引継ぎ",
        "lead": "個人事業主・フリーランスの相続は、法人と違い<strong>事業と相続が直結</strong>。手続きを怠ると事業継続不能になります。",
        "sections": [
            ("4ヶ月以内：所得税準確定申告", "<p>被相続人の1月1日から死亡日までの所得を<strong>準確定申告</strong>（所得税法125条）。事業所得・不動産所得は青色決算書・収支内訳書も必要。</p>"),
            ("事業承継の選択肢", "<ol><li><strong>相続人が事業を引継ぐ</strong>：開業届・青色申告承認申請書を新たに提出</li><li><strong>廃業して資産売却</strong>：消費税課税事業者なら廃業届</li><li><strong>法人成り</strong>：相続後に法人化して事業継続</li></ol>"),
            ("青色申告承認申請の期限", "<p>相続で事業を引継ぐ場合、青色申告の承認を改めて受ける必要があります。期限：</p><ul><li>死亡日が1〜8月：その年の12月31日</li><li>死亡日が9〜10月：その年の12月31日</li><li>死亡日が11〜12月：翌年2月15日</li></ul>"),
            ("事業用資産・債務の評価", "<ul><li>事業用不動産：小規模宅地等の特例（特定事業用宅地）で<strong>400㎡まで80%減</strong></li><li>機械装置・棚卸資産：取得価額・時価で評価</li><li>売掛金・買掛金：額面評価</li><li>事業借入金：債務控除で課税価格から減額</li></ul>"),
            ("屋号付き口座の処理", "<p>個人名の口座は通常通り凍結・解約。屋号付き口座も<strong>事業主個人の財産</strong>として相続対象。継続事業の場合、相続人名義の新口座開設＋取引先への振込先変更通知が必須。</p>"),
        ],
        "faqs": [
            ("妻が引き継ぐ場合の手続きは？", "妻が新たに開業届・青色申告承認申請を提出。事業用資産は相続評価で承継。事業用借入も債務控除可能。"),
            ("法人成りすれば節税になりますか？", "規模次第。年商1,000万円以上で消費税課税事業者になるなら法人化メリット大。所得分散・社会保険加入義務もメリット/デメリット両面。"),
            ("売掛金の取り立ては誰が？", "相続人が事業継続するなら相続人。廃業なら相続人が「相続人代表」として回収。"),
        ],
    },
]

ARTICLES += [
    {
        "slug": "notarized-will",
        "title": "公正証書遺言の作り方｜費用・必要書類・証人の手配",
        "h1": "公正証書遺言の作り方と費用",
        "desc": "公証人が作成する公正証書遺言の作成手順、費用（手数料）の早見、必要書類、証人2名の手配、自筆証書との違いを解説。無効リスクが極めて低い最も確実な遺言方式です。",
        "keywords": "公正証書遺言,作り方,費用,手数料,証人,必要書類,公証人",
        "lead": "<strong>公正証書遺言</strong>は公証人が作成する遺言で、無効になるリスクが極めて低く、検認も不要な最も確実な方式です。費用と手順を解説します。",
        "sections": [
            ("公正証書遺言のメリット", "<ul><li>公証人が関与するため<strong>無効リスクがほぼない</strong></li><li>原本を公証役場が保管（紛失・偽造の心配なし）</li><li>家庭裁判所の<strong>検認が不要</strong></li><li>病気で自書できなくても作成可能</li></ul>"),
            ("作成の手順", "<ol><li>遺言内容を整理（誰に何を遺すか）</li><li>必要書類を収集</li><li>公証人と事前打ち合わせ（文案作成）</li><li>証人2名を手配</li><li>公証役場で遺言者・証人立会いのもと署名押印</li></ol>"),
            ("費用（手数料）の目安", """<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
<thead><tr style="background:#27AE60;color:white;"><th style="padding:.5rem;border:1px solid #ddd;">目的価額</th><th style="padding:.5rem;border:1px solid #ddd;">手数料</th></tr></thead>
<tbody>
<tr><td style="padding:.5rem;border:1px solid #ddd;">100万円以下</td><td style="padding:.5rem;border:1px solid #ddd;">5,000円</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">100万〜200万円</td><td style="padding:.5rem;border:1px solid #ddd;">7,000円</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">500万〜1,000万円</td><td style="padding:.5rem;border:1px solid #ddd;">17,000円</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">1,000万〜3,000万円</td><td style="padding:.5rem;border:1px solid #ddd;">23,000円</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">3,000万〜5,000万円</td><td style="padding:.5rem;border:1px solid #ddd;">29,000円</td></tr>
</tbody></table><p>相続人ごとに財産を分けて計算し合算。別途「遺言加算」1.1万円等がかかります。</p>"""),
            ("必要書類", "<ul><li>遺言者の印鑑証明書（3ヶ月以内）</li><li>遺言者と相続人の関係が分かる戸籍謄本</li><li>財産を遺す相手の住民票（相続人以外の場合）</li><li>不動産の登記事項証明書・固定資産評価証明書</li><li>証人2名の身分情報</li></ul>"),
        ],
        "faqs": [
            ("証人は誰でもなれますか？", "推定相続人・受遺者とその配偶者・直系血族はなれません（民法974条）。適任者がいなければ公証役場や専門家が証人を手配できます（有料）。"),
            ("公証役場に行けない場合は？", "公証人に<strong>出張</strong>してもらえます（入院中・施設入所中など）。その場合は手数料が1.5倍になり日当・交通費も加算されます。"),
            ("自筆証書遺言とどちらがいい？", "確実性を重視するなら公正証書、手軽さ・費用を抑えるなら自筆証書（＋法務局保管制度）。資産が多い・紛争リスクがある場合は公正証書を推奨します。"),
        ],
    },
    {
        "slug": "will-executor",
        "title": "遺言執行者とは｜役割・選び方・報酬の相場",
        "h1": "遺言執行者の役割と選び方",
        "desc": "遺言の内容を実現する遺言執行者の役割、指定方法、報酬相場、専門家に依頼するメリットを解説。相続登記や預貯金解約を円滑に進める鍵となります。",
        "keywords": "遺言執行者,役割,選び方,報酬,相場,民法1012条",
        "lead": "<strong>遺言執行者</strong>は、遺言の内容を実際に実現する人です（民法1012条）。指定しておくと相続手続きが格段にスムーズになります。",
        "sections": [
            ("遺言執行者の役割", "<ul><li>相続財産の管理</li><li>不動産の相続登記</li><li>預貯金・有価証券の名義変更・解約</li><li>遺贈の履行</li><li>認知（婚外子の認知）・推定相続人の廃除</li></ul><p>2019年改正で権限が明確化され、単独で手続きを進めやすくなりました。</p>"),
            ("誰を指定できるか", "<p>未成年者・破産者以外なら誰でも可（民法1009条）。相続人本人でも、第三者（弁護士・税理士・司法書士）でも指定できます。紛争リスクがある場合は<strong>中立な専門家</strong>が安全です。</p>"),
            ("指定方法", "<ul><li>遺言書で直接指定する</li><li>遺言書で「指定を第三者に委託する」</li><li>遺言執行者がいない場合は<strong>家庭裁判所が選任</strong>（利害関係人が申立て）</li></ul>"),
            ("報酬の相場", "<p>遺言書で報酬を定められます。専門家に依頼する場合の目安は<strong>遺産総額の1〜3%</strong>（最低30万円程度〜）。信託銀行の遺言執行は最低100万円〜と高額な傾向。</p>"),
        ],
        "faqs": [
            ("遺言執行者は必ず必要ですか？", "必須ではありませんが、不動産の相続登記や認知・廃除がある場合は実質必要です。いないと相続人全員の協力が必要になり手続きが滞りがちです。"),
            ("相続人が遺言執行者になれますか？", "なれます。ただし他の相続人と利害が対立する内容の場合、トラブルのもとになるため中立な専門家が無難です。"),
            ("遺言執行者を解任できますか？", "正当な理由（任務を怠る等）があれば、利害関係人が家庭裁判所に解任を請求できます（民法1019条）。"),
        ],
    },
    {
        "slug": "survivor-pension",
        "title": "遺族年金の手続き｜遺族基礎年金・遺族厚生年金の受給",
        "h1": "遺族年金の種類と手続き",
        "desc": "遺族基礎年金・遺族厚生年金の受給要件、金額の目安、手続きの流れと期限を解説。相続財産とは別に受け取れる、残された家族の生活を支える制度です。",
        "keywords": "遺族年金,遺族基礎年金,遺族厚生年金,受給要件,手続き,金額",
        "lead": "<strong>遺族年金</strong>は、亡くなった方に生計を維持されていた遺族が受け取れる年金です。相続財産とは別物で、相続放棄しても受給できます。",
        "sections": [
            ("2種類の遺族年金", "<ul><li><strong>遺族基礎年金</strong>：国民年金から。子のある配偶者または子が対象</li><li><strong>遺族厚生年金</strong>：厚生年金から。会社員等の遺族が対象（子のない妻も可）</li></ul><p>両方の受給要件を満たせば併給されます。</p>"),
            ("受給要件の概要", "<ul><li>遺族基礎年金：<strong>18歳到達年度末まで</strong>の子がいること</li><li>遺族厚生年金：被保険者期間中の死亡等、一定の納付要件</li><li>生計維持関係（年収850万円未満が目安）</li></ul>"),
            ("金額の目安（2026年度水準）", "<p>遺族基礎年金：年<strong>約81万円＋子の加算</strong>（第1子・第2子 各約23万円）。遺族厚生年金：<strong>報酬比例部分の約3/4</strong>。中高齢寡婦加算（約61万円）が加わる場合も。</p>"),
            ("手続きと期限", "<ul><li>年金事務所または市区町村で請求</li><li>必要書類：死亡診断書、戸籍、住民票、年金手帳、振込口座等</li><li>時効：<strong>5年</strong>（早めの請求を）</li></ul>"),
        ],
        "faqs": [
            ("相続放棄しても遺族年金はもらえますか？", "もらえます。遺族年金は受給権者固有の権利で<strong>相続財産ではない</strong>ため、相続放棄の影響を受けません。"),
            ("再婚すると遺族年金は止まりますか？", "はい、受給者が再婚すると<strong>受給権が消滅</strong>します。事実婚も含みます。"),
            ("自営業者の遺族はどうなりますか？", "国民年金のみのため遺族厚生年金はなく、子のある配偶者は遺族基礎年金が対象。子がいない場合は<strong>寡婦年金・死亡一時金</strong>の制度があります。"),
        ],
    },
    {
        "slug": "grave-succession",
        "title": "お墓・仏壇の承継｜祭祀財産は相続財産と別扱い",
        "h1": "お墓・仏壇の承継（祭祀財産）",
        "desc": "お墓・仏壇・位牌などの祭祀財産は相続財産とは別に承継されます。祭祀主宰者の決め方、相続税の扱い、墓じまいの注意点を解説。",
        "keywords": "祭祀財産,お墓,仏壇,承継,祭祀主宰者,墓じまい,民法897条",
        "lead": "お墓・仏壇・位牌などの<strong>祭祀財産</strong>は、通常の相続財産とは別ルールで承継されます（民法897条）。遺産分割の対象外です。",
        "sections": [
            ("祭祀財産とは", "<p>系譜（家系図）・祭具（仏壇・位牌）・墳墓（墓地・墓石）を指します。これらは<strong>祭祀主宰者が単独で承継</strong>し、遺産分割の対象になりません。</p>"),
            ("祭祀主宰者の決め方", "<ol><li>被相続人の指定（遺言・口頭でも可）</li><li>指定がなければ<strong>慣習</strong>による</li><li>慣習も不明なら<strong>家庭裁判所が指定</strong></li></ol><p>長男に限らず、誰でも・複数でも指定できます。</p>"),
            ("相続税の扱い", "<p>祭祀財産は原則<strong>相続税が非課税</strong>（相続税法12条）。ただし<strong>投資目的の純金の仏像</strong>など、過度に高額・換金性が高いものは課税対象となる場合があります。生前に墓地を購入しておくと節税になります。</p>"),
            ("墓じまいの注意点", "<ul><li>改葬許可（市区町村）が必要</li><li>既存墓地の管理者・親族の同意</li><li>離檀料をめぐるトラブルに注意</li><li>永代供養・散骨・樹木葬など改葬先の選択</li></ul>"),
        ],
        "faqs": [
            ("祭祀主宰者になると費用負担の義務がありますか？", "法律上、管理費や供養費の負担を強制する規定はありません。承継しても放棄も可能ですが、慣習・親族関係への配慮が現実には必要です。"),
            ("お墓は誰も継ぎたがりません。どうすれば？", "永代供養墓への改葬、合祀、墓じまいが選択肢です。生前に方針を決めて家族と共有しておくとトラブルを防げます。"),
            ("祭祀財産を分割できますか？", "原則として祭祀主宰者が一括承継します。分割になじまない財産のため、複数人での共同主宰や事実上の分担で対応します。"),
        ],
    },
    {
        "slug": "legal-heir-info",
        "title": "法定相続情報証明制度とは｜戸籍の束が1枚に",
        "h1": "法定相続情報証明制度の使い方",
        "desc": "法務局が相続関係を証明する「法定相続情報一覧図」の取得方法を解説。これ1枚で各種相続手続きの戸籍提出を省略でき、無料で何枚でも発行できます。",
        "keywords": "法定相続情報証明制度,法定相続情報一覧図,法務局,戸籍,相続手続き",
        "lead": "<strong>法定相続情報証明制度</strong>は、相続関係を法務局が公的に証明する制度（2017年開始）。一覧図1枚で戸籍の束の代わりになり、手続きが大幅に効率化します。",
        "sections": [
            ("制度のメリット", "<ul><li>銀行・法務局・税務署など各窓口に<strong>戸籍の束を何度も出さなくて済む</strong></li><li>一覧図は<strong>無料で何枚でも発行</strong></li><li>複数手続きを同時並行で進められる</li></ul>"),
            ("取得の手順", "<ol><li>被相続人の出生〜死亡の戸籍、相続人の戸籍を収集</li><li>「法定相続情報一覧図」を作成（家系図形式）</li><li>申出書とともに法務局へ提出</li><li>登記官が確認し、認証文付き一覧図を交付</li></ol>"),
            ("どこの法務局に申し出るか", "<p>①被相続人の本籍地 ②被相続人の最後の住所地 ③申出人の住所地 ④被相続人名義の不動産所在地 のいずれかを管轄する法務局。郵送申請も可能です。</p>"),
            ("使える手続き", "<ul><li>不動産の相続登記</li><li>預貯金の払い戻し・名義変更</li><li>有価証券の名義変更</li><li>相続税の申告</li><li>遺族年金等の手続き</li></ul>"),
        ],
        "faqs": [
            ("代理人に取得を頼めますか？", "はい。資格者代理人（弁護士・司法書士・税理士・行政書士等）のほか、親族も委任状で代理申請できます。"),
            ("一覧図の有効期限はありますか？", "法律上の有効期限はありませんが、金融機関によっては発行から一定期間内を求める場合があります。"),
            ("数次相続でも使えますか？", "1つの相続につき1枚の一覧図を作成します。数次相続の場合は被相続人ごとに作成する必要があります。"),
        ],
    },
    {
        "slug": "disinheritance",
        "title": "相続欠格と相続廃除｜相続人から外す2つの制度",
        "h1": "相続欠格と相続廃除の違い",
        "desc": "特定の相続人に相続させない「相続欠格」（民法891条）と「相続廃除」（民法892条）の要件・手続き・違いを解説。遺留分を奪えるかどうかも含めて整理します。",
        "keywords": "相続欠格,相続廃除,民法891条,民法892条,遺留分,相続人から外す",
        "lead": "特定の相続人に相続させたくない場合の制度が<strong>相続欠格</strong>と<strong>相続廃除</strong>です。要件や手続きが大きく異なります。",
        "sections": [
            ("相続欠格（民法891条）", "<p>一定の非行があった相続人が<strong>法律上当然に</strong>相続権を失う制度。手続き不要。該当例：</p><ul><li>被相続人や先順位者を故意に死亡させた</li><li>詐欺・強迫で遺言を妨げた・書かせた</li><li>遺言書を偽造・変造・破棄・隠匿した</li></ul>"),
            ("相続廃除（民法892条）", "<p>被相続人に対する<strong>虐待・重大な侮辱・著しい非行</strong>があった場合に、被相続人の意思で相続権を奪う制度。<strong>家庭裁判所の審判</strong>が必要。生前申立てまたは遺言で行う。</p>"),
            ("2つの違い", """<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
<thead><tr style="background:#27AE60;color:white;"><th style="padding:.5rem;border:1px solid #ddd;">項目</th><th style="padding:.5rem;border:1px solid #ddd;">相続欠格</th><th style="padding:.5rem;border:1px solid #ddd;">相続廃除</th></tr></thead>
<tbody>
<tr><td style="padding:.5rem;border:1px solid #ddd;">手続き</td><td style="padding:.5rem;border:1px solid #ddd;">不要（当然失権）</td><td style="padding:.5rem;border:1px solid #ddd;">家裁の審判が必要</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">対象</td><td style="padding:.5rem;border:1px solid #ddd;">全相続人</td><td style="padding:.5rem;border:1px solid #ddd;">遺留分を持つ相続人</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">取消</td><td style="padding:.5rem;border:1px solid #ddd;">不可</td><td style="padding:.5rem;border:1px solid #ddd;">被相続人が取消可能</td></tr>
</tbody></table>"""),
            ("代襲相続への影響", "<p>欠格・廃除いずれの場合も、その者の<strong>子は代襲相続できます</strong>（民法887条2項）。本人は外れても、孫には権利が残る点に注意。</p>"),
        ],
        "faqs": [
            ("廃除すれば遺留分も奪えますか？", "はい。廃除されると遺留分も含めて相続権を完全に失います。「遺言で財産を渡さない」だけでは遺留分は残るため、確実に外すには廃除が必要です。"),
            ("兄弟姉妹を廃除できますか？", "できません。廃除の対象は<strong>遺留分を持つ相続人</strong>（配偶者・子・直系尊属）に限られます。兄弟姉妹は遺言で財産を渡さなければ済みます（遺留分がないため）。"),
            ("廃除は認められやすいですか？", "ハードルは高めです。単なる感情的対立では足りず、虐待・重大な侮辱など客観的な事実が必要。証拠の準備が重要です。"),
        ],
    },
    {
        "slug": "bequest-gift",
        "title": "遺贈と死因贈与の違い｜相続人以外に財産を渡す方法",
        "h1": "遺贈と死因贈与の違い",
        "desc": "相続人以外（孫・内縁の配偶者・団体等）に財産を渡す「遺贈」と「死因贈与」の違い、税金、撤回の可否を解説。包括遺贈と特定遺贈の区別も整理します。",
        "keywords": "遺贈,死因贈与,包括遺贈,特定遺贈,相続人以外,民法964条",
        "lead": "相続人以外の人や団体に財産を渡したい場合の方法が<strong>遺贈</strong>と<strong>死因贈与</strong>です。似ていますが法的性質が異なります。",
        "sections": [
            ("遺贈とは（民法964条）", "<p>遺言によって財産を無償で与えること。<strong>遺贈者の単独行為</strong>で、相手の承諾は不要。2種類あります：</p><ul><li><strong>包括遺贈</strong>：「財産の1/3を与える」など割合指定。受遺者は相続人と同様の権利義務（債務も承継）</li><li><strong>特定遺贈</strong>：「この土地を与える」など特定財産。債務は原則承継しない</li></ul>"),
            ("死因贈与とは", "<p>「私が死んだらこれを与える」という<strong>贈与契約</strong>（民法554条）。贈与者と受贈者の<strong>合意</strong>で成立。生前に契約するため、受贈者は確実に受け取れる安心感がある。</p>"),
            ("主な違い", """<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
<thead><tr style="background:#27AE60;color:white;"><th style="padding:.5rem;border:1px solid #ddd;">項目</th><th style="padding:.5rem;border:1px solid #ddd;">遺贈</th><th style="padding:.5rem;border:1px solid #ddd;">死因贈与</th></tr></thead>
<tbody>
<tr><td style="padding:.5rem;border:1px solid #ddd;">成立</td><td style="padding:.5rem;border:1px solid #ddd;">単独行為（遺言）</td><td style="padding:.5rem;border:1px solid #ddd;">契約（合意）</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">撤回</td><td style="padding:.5rem;border:1px solid #ddd;">自由</td><td style="padding:.5rem;border:1px solid #ddd;">原則自由（負担付は制限）</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">様式</td><td style="padding:.5rem;border:1px solid #ddd;">遺言の方式が必要</td><td style="padding:.5rem;border:1px solid #ddd;">口頭でも可（書面推奨）</td></tr>
</tbody></table>"""),
            ("税金の扱い", "<p>どちらも<strong>相続税</strong>の対象（贈与税ではない）。相続人以外が取得する場合は<strong>2割加算</strong>の対象。不動産の場合、遺贈・死因贈与とも登録免許税・不動産取得税がかかる場合があります。</p>"),
        ],
        "faqs": [
            ("内縁の妻に財産を残せますか？", "遺贈または死因贈与で可能です。内縁の配偶者は相続人ではないため、これらの方法か生前贈与が必要。ただし相続人の遺留分には配慮が必要です。"),
            ("遺贈は放棄できますか？", "特定遺贈はいつでも放棄可能。包括遺贈は相続人と同様、<strong>3ヶ月以内に家庭裁判所で放棄</strong>の手続きが必要です。"),
            ("死因贈与のほうが確実ですか？", "契約のため受贈者の同意があり、生前に登記の仮登記もできるため確実性は高いです。ただし税負担は遺贈と同じです。"),
        ],
    },
    {
        "slug": "education-gift",
        "title": "教育資金の一括贈与｜1,500万円まで非課税の特例",
        "h1": "教育資金一括贈与の非課税特例",
        "desc": "祖父母から孫へ教育資金を一括贈与する際、1,500万円まで非課税となる特例の要件・対象範囲・注意点を解説。使い残しへの課税リスクも整理します。",
        "keywords": "教育資金,一括贈与,非課税,1500万円,祖父母,孫,特例",
        "lead": "<strong>教育資金の一括贈与</strong>は、祖父母などから30歳未満の子・孫へ教育資金を渡す際、<strong>1,500万円まで非課税</strong>になる特例です（期限付き）。",
        "sections": [
            ("制度の概要", "<p>直系尊属から30歳未満の子・孫へ、金融機関経由で教育資金を一括贈与すると、受贈者1人につき<strong>1,500万円（学校以外は500万円）まで非課税</strong>。専用口座を開設して管理します。</p>"),
            ("対象となる教育資金", "<ul><li><strong>学校等</strong>：入学金・授業料・施設費・給食費など（1,500万円枠）</li><li><strong>学校以外</strong>：塾・習い事・通学定期・留学渡航費など（500万円枠）</li></ul>"),
            ("使い残しへの課税", "<p>注意点。受贈者が<strong>30歳に達した時点</strong>で使い切れなかった残額には<strong>贈与税</strong>が課されます（在学中等の例外あり）。贈与者死亡時の残額が相続税の対象になる場合も。</p>"),
            ("暦年贈与との比較", "<p>そもそも<strong>都度払いの教育費は非課税</strong>（扶養義務者間）。一括贈与特例は「まとめて早期に移転して相続財産を減らしたい」場合に有効。使い切る見込みがあるかが判断ポイント。</p>"),
        ],
        "faqs": [
            ("そもそも教育費は贈与税がかからないのでは？", "扶養義務者が<strong>必要な都度</strong>支払う教育費は非課税です。一括贈与特例は『まとめて先に渡す』ための制度で、相続税対策として早期移転したい場合に使います。"),
            ("孫が複数いる場合は？", "受贈者1人ごとに1,500万円枠が使えます。孫3人なら最大4,500万円を非課税で移転可能。"),
            ("制度はいつまで使えますか？", "適用期限が定められた時限措置です（延長を繰り返している）。利用前に最新の適用期限を必ず確認してください。"),
        ],
    },
    {
        "slug": "digital-legacy",
        "title": "デジタル遺産の相続｜ネット口座・サブスク・SNSの整理",
        "h1": "デジタル遺産の相続と整理",
        "desc": "ネット銀行・証券、サブスク、SNS、スマホのパスワードなど「デジタル遺産」の把握・解約・相続の進め方を解説。放置による負債リスクと生前対策を紹介。",
        "keywords": "デジタル遺産,ネット口座,サブスク,SNS,パスワード,デジタル終活",
        "lead": "<strong>デジタル遺産</strong>とは、ネット銀行・証券、電子マネー、サブスク、SNSアカウントなど、デジタル上の財産・契約です。把握しづらく、放置すると思わぬ負債やトラブルに。",
        "sections": [
            ("デジタル遺産の種類", "<ul><li><strong>資産系</strong>：ネット銀行・証券、暗号資産、電子マネー、ポイント、マイル</li><li><strong>契約系</strong>：サブスク（動画・音楽・クラウド）、有料アプリ</li><li><strong>情報系</strong>：SNS、メール、写真、ブログ</li></ul>"),
            ("把握できないリスク", "<ul><li>ネット口座の存在に気づかず<strong>相続漏れ</strong>（後で税務調査で発覚）</li><li>サブスクが<strong>解約されず課金が続く</strong></li><li>SNSの乗っ取り・なりすまし</li><li>スマホのロックが解除できず一切アクセス不能</li></ul>"),
            ("相続・解約の進め方", "<ol><li>スマホ・PC・メールから契約を洗い出す</li><li>各事業者へ死亡連絡（残高は相続財産として手続き）</li><li>サブスクを解約</li><li>SNSは追悼アカウント化または削除申請</li></ol>"),
            ("生前にやるべき対策", "<ul><li>デジタル資産・契約のリストを作成</li><li>ID・パスワードを<strong>安全な形で</strong>引き継ぐ準備（エンディングノート等）</li><li>スマホのロック解除方法を信頼できる家族に共有</li><li>暗号資産は秘密鍵の引き継ぎを明確に</li></ul>"),
        ],
        "faqs": [
            ("故人のスマホのパスワードが分かりません。", "メーカー・キャリアでも原則解除できません。生前にロック解除方法を共有しておくことが唯一の確実な対策です。"),
            ("ネット銀行の口座は相続でどうなりますか？", "通常の預貯金と同じく相続財産です。各行に死亡連絡し、戸籍・遺産分割協議書等で解約・名義変更します。口座の存在把握が最大の課題。"),
            ("サブスクを解約しないとどうなりますか？", "クレジットカードや口座から課金が続きます。カード解約だけでは未払い扱いになることもあるため、各サービスでの解約手続きが必要です。"),
        ],
    },
    {
        "slug": "consecutive-inheritance",
        "title": "数次相続とは｜相次いで相続が発生した場合の対応",
        "h1": "数次相続と相次相続控除",
        "desc": "遺産分割前に相続人が死亡し相続が重なる「数次相続」の手続きと、10年以内に相次いだ場合の相次相続控除（相続税法20条）を解説します。",
        "keywords": "数次相続,相次相続控除,相続税法20条,遺産分割,代襲相続との違い",
        "lead": "<strong>数次相続</strong>とは、ある相続の遺産分割が終わらないうちに、相続人の一人が亡くなって次の相続が発生することです。手続きが複雑化します。",
        "sections": [
            ("数次相続と代襲相続の違い", "<ul><li><strong>代襲相続</strong>：相続人が被相続人より<strong>先に</strong>死亡 → 孫等が代わりに相続</li><li><strong>数次相続</strong>：相続人が被相続人より<strong>後に</strong>死亡 → その相続人の相続人が引き継ぐ</li></ul><p>死亡の前後で扱いが全く異なります。</p>"),
            ("遺産分割協議の進め方", "<p>一次相続・二次相続の<strong>両方の相続人全員</strong>で協議が必要になり、関係者が増えて複雑化。一通の遺産分割協議書で両方をまとめることも可能です。</p>"),
            ("相次相続控除（相続税法20条）", "<p>10年以内に相次いで相続が発生した場合、前回の相続で課された相続税の一部を今回の相続税から控除できます。<strong>経過年数1年につき10%ずつ逓減</strong>した額を控除。短期間に相続が重なった負担を軽減する制度。</p>"),
            ("実務上の注意", "<ul><li>戸籍収集が二重になり手続きが長期化</li><li>未分割のまま相続税申告期限が来るリスク</li><li>登記も中間省略できる場合とできない場合がある</li><li>早めに専門家へ相談を</li></ul>"),
        ],
        "faqs": [
            ("祖父→父が相次いで亡くなりました。どうなりますか？", "祖父の遺産は、父の相続人（あなた等）が父の地位を引き継いで分割協議に参加します。祖父・父それぞれの相続手続きが必要です。"),
            ("相次相続控除はいくらですか？", "前回の相続税額をもとに、経過年数に応じて逓減した額を控除します（1年につき10%減）。10年経過するとゼロになります。"),
            ("数次相続で登記はどうなりますか？", "原則は順番に登記しますが、中間の相続人が単独相続の場合などは中間省略登記が認められることがあります。司法書士に相談を。"),
        ],
    },
    {
        "slug": "tax-surcharge",
        "title": "相続税の2割加算｜孫・兄弟姉妹が対象になる仕組み",
        "h1": "相続税の2割加算とは",
        "desc": "配偶者・子・親以外が相続・遺贈で財産を取得すると相続税が2割増しになる「2割加算」（相続税法18条）の対象者と計算方法、孫養子の注意点を解説。",
        "keywords": "相続税,2割加算,相続税法18条,孫,兄弟姉妹,孫養子",
        "lead": "<strong>相続税の2割加算</strong>とは、配偶者・子・親以外の人が財産を取得した場合に、相続税額が1.2倍になる制度です（相続税法18条）。",
        "sections": [
            ("2割加算の対象者", "<p>被相続人の<strong>配偶者・1親等の血族（子・親）以外</strong>が対象。具体的には：</p><ul><li>兄弟姉妹</li><li>甥・姪</li><li>孫（代襲相続人を除く）</li><li>内縁の配偶者・第三者（遺贈）</li></ul>"),
            ("対象にならない人", "<ul><li>配偶者</li><li>子（実子・養子）</li><li>父母</li><li><strong>代襲相続人である孫</strong>（子が先に死亡して代襲した場合は加算なし）</li></ul>"),
            ("孫養子の注意点", "<p>節税目的で孫を養子にするケースがありますが、<strong>孫養子は2割加算の対象</strong>です（代襲相続人を除く）。世代飛ばしによる節税効果と2割加算を天秤にかける必要があります。</p>"),
            ("計算方法", "<p>各人の相続税額に対して<strong>×1.2</strong>。例えば加算前の税額が500万円なら、2割加算後は<strong>600万円</strong>。配偶者の税額軽減など他の控除は加算後に適用します。</p>"),
        ],
        "faqs": [
            ("代襲相続の孫も2割加算ですか？", "いいえ。子が先に亡くなって<strong>代襲相続人</strong>となった孫は2割加算の対象外です。あくまで養子縁組による孫養子が対象です。"),
            ("子のいない夫婦で配偶者が亡くなり、甥が相続。加算は？", "甥は兄弟姉妹の代襲相続人ですが、<strong>2割加算の対象</strong>です（配偶者・1親等血族以外のため）。子なし夫婦の相続は税負担が重くなりがち。"),
            ("2割加算と配偶者控除は両方適用されますか？", "対象者が異なります。配偶者は加算対象外かつ税額軽減あり。加算は孫・兄弟等が対象で、それぞれ別の相続人に適用されます。"),
        ],
    },
    {
        "slug": "leasehold-inheritance",
        "title": "借地権・借家権の相続｜地主の承諾は必要？",
        "h1": "借地権・借家権の相続",
        "desc": "借地権・借家権も相続の対象です。地主・大家の承諾の要否、相続税評価、名義変更や更新料の扱いを解説。トラブルになりやすいポイントを整理します。",
        "keywords": "借地権,借家権,相続,地主,承諾,相続税評価,更新料",
        "lead": "<strong>借地権・借家権</strong>（土地や建物を借りる権利）も相続財産です。承継には地主・大家の承諾が必要か、という点でトラブルになりがちです。",
        "sections": [
            ("相続に地主の承諾は不要", "<p>借地権・借家権の<strong>相続</strong>は、地主・大家の承諾は<strong>不要</strong>です。相続は売買等の譲渡と異なり、当然に承継されます。承諾料を請求されても応じる法的義務はありません。</p>"),
            ("名義変更の手続き", "<ul><li>地主・大家へ相続の事実を通知</li><li>賃貸借契約の名義を相続人に変更</li><li>建物が借地上にある場合、建物の相続登記</li></ul><p>通知はトラブル防止のため書面で行うのが安全です。</p>"),
            ("相続税評価", "<p>借地権：<strong>自用地評価額 × 借地権割合</strong>（30〜90%、路線価図のアルファベットで確認）。借家権：建物評価額 × 借家権割合（通常30%）。一定の財産価値があるため評価漏れに注意。</p>"),
            ("注意点・トラブル", "<ul><li>更新料・名義書換料を不当に請求されるケース</li><li>相続人が複数の場合の権利の共有</li><li>建物の老朽化・建替え時の地主との交渉</li><li>定期借地権は期間満了で終了</li></ul>"),
        ],
        "faqs": [
            ("地主から承諾料を求められました。払う必要は？", "相続による承継では<strong>承諾料・名義書換料を支払う法的義務はありません</strong>。ただし今後の関係を考え、円満解決のため協議するケースもあります。"),
            ("借地権は分割できますか？", "相続人複数の場合、共有または代表者が承継します。分割は地主との関係で現実的でないことが多く、誰が引き継ぐか協議が必要です。"),
            ("借家（賃貸アパート）の入居権も相続できますか？", "はい、借家権も相続されます。同居していた相続人がそのまま住み続けられます。内縁配偶者には借家権の承継に関する特別な保護規定があります。"),
        ],
    },
]

ARTICLES += [
    {
        "slug": "inheritance-tax-threshold",
        "title": "相続税はいくらからかかる？かからない人の条件",
        "h1": "相続税はいくらからかかるのか",
        "desc": "相続税がかかるかどうかの分かれ目「基礎控除（3,000万円＋600万円×法定相続人数）」をわかりやすく解説。かからない人の条件、申告要否の判断、よくある勘違いを整理します。",
        "keywords": "相続税,いくらから,かからない,基礎控除,申告不要,条件",
        "lead": "「相続税はいくらから？」の答えは<strong>基礎控除を超えるかどうか</strong>です。多くの方は基礎控除内で課税されません。判断の仕方を解説します。",
        "sections": [
            ("基礎控除がボーダーライン", "<p>遺産総額が<strong>基礎控除以下なら相続税はゼロ</strong>。基礎控除＝<strong>3,000万円＋600万円×法定相続人数</strong>。</p><ul><li>相続人1人：3,600万円</li><li>相続人2人：4,200万円</li><li>相続人3人：4,800万円</li></ul>"),
            ("課税割合は約9%", "<p>実際に相続税がかかるのは全相続の<strong>1割弱</strong>。多くの家庭は基礎控除内に収まります。ただし都市部に持ち家がある場合は超えやすいので要注意。</p>"),
            ("判断の手順", "<ol><li>プラス財産（不動産・預貯金・有価証券・保険）を合計</li><li>不動産は路線価・固定資産税評価で概算</li><li>生命保険・退職金の非課税枠（500万円×人数）を差引</li><li>債務・葬儀費用を差引</li><li>基礎控除と比較</li></ol>"),
            ("よくある勘違い", "<ul><li>「現金がなければ無税」→不動産評価で超えることが多い</li><li>「配偶者がいれば無税」→税額軽減はあるが申告は必要</li><li>「特例でゼロなら申告不要」→<strong>特例適用には申告が必須</strong></li></ul>"),
        ],
        "faqs": [
            ("ぎりぎり基礎控除を超えそうです。", "概算で超えそうなら一度シミュレーションを。小規模宅地等の特例や配偶者の税額軽減で大きく下がる可能性があります。家系図Naviで無料試算できます。"),
            ("相続税がかからなくても申告は必要？", "基礎控除以下なら申告不要です。ただし<strong>特例や配偶者の税額軽減でゼロになる場合は申告が必要</strong>です。"),
            ("生命保険も相続税の対象？", "受取人指定の死亡保険金はみなし相続財産として対象ですが、500万円×法定相続人数まで非課税です。"),
        ],
    },
    {
        "slug": "spouse-tax-credit",
        "title": "配偶者の税額軽減｜1.6億円まで相続税が非課税",
        "h1": "配偶者の税額軽減（1.6億円）",
        "desc": "配偶者が取得した財産は1億6,000万円または法定相続分まで相続税が非課税になる「配偶者の税額軽減」（相続税法19条の2）の仕組み・要件・注意点を解説します。",
        "keywords": "配偶者の税額軽減,配偶者控除,1.6億円,相続税法19条の2,非課税",
        "lead": "<strong>配偶者の税額軽減</strong>は、配偶者が取得した遺産のうち<strong>1億6,000万円または法定相続分</strong>のいずれか多い方まで相続税を非課税にする強力な制度です。",
        "sections": [
            ("制度の概要", "<p>配偶者は被相続人の財産形成に貢献し、その後の生活保障も必要なことから、大きな軽減が認められています。<strong>1.6億円 or 法定相続分</strong>の多い方まで非課税。</p>"),
            ("適用の要件", "<ul><li>戸籍上の配偶者であること（内縁は不可）</li><li>原則、申告期限までに遺産分割が確定していること</li><li><strong>相続税の申告を行うこと</strong>（軽減でゼロでも申告必須）</li></ul>"),
            ("二次相続の落とし穴", "<p>配偶者にめいっぱい相続させると一次相続は非課税でも、<strong>二次相続（配偶者死亡時）で税負担が急増</strong>することがあります。配偶者取得を30〜50%に抑えるのが税額最小化の目安。</p>"),
            ("未分割の場合", "<p>申告期限までに分割が決まらない場合、一旦は軽減なしで申告し、<strong>「申告期限後3年以内の分割見込書」</strong>を提出。後で分割確定時に更正の請求で軽減を受けられます。</p>"),
        ],
        "faqs": [
            ("配偶者は絶対に相続税がかからない？", "1.6億円を超え、かつ法定相続分も超える部分には課税されます。多くのケースで非課税ですが万能ではありません。"),
            ("内縁の妻も使えますか？", "使えません。配偶者の税額軽減は戸籍上の配偶者に限られます。"),
            ("配偶者に全部相続させるべき？", "二次相続まで考えると不利になることが多いです。子への分配とのバランスを必ずシミュレーションしましょう。"),
        ],
    },
    {
        "slug": "sell-inherited-property",
        "title": "相続した不動産を売るとき｜取得費加算と税金",
        "h1": "相続した不動産の売却と税金",
        "desc": "相続した不動産を売却する際の譲渡所得税、取得費加算の特例（相続税の一部を取得費に加算）、相続後3年10ヶ月以内の期限、空き家特例との関係を解説します。",
        "keywords": "相続不動産,売却,取得費加算,譲渡所得税,3年10ヶ月,空き家特例",
        "lead": "相続した不動産を売ると<strong>譲渡所得税</strong>がかかりますが、相続税を払った人には<strong>取得費加算の特例</strong>で税負担を軽減できます。",
        "sections": [
            ("譲渡所得税の基本", "<p>売却益（譲渡価額−取得費−譲渡費用）に課税。所有期間が<strong>5年超で長期譲渡（約20%）、5年以下で短期（約39%）</strong>。被相続人の所有期間を引き継げます。</p>"),
            ("取得費加算の特例", "<p>相続税の申告期限の翌日から<strong>3年以内（相続開始から3年10ヶ月以内）</strong>に売却すれば、納めた相続税の一部を取得費に加算でき、譲渡益を圧縮できます（租特法39条）。</p>"),
            ("取得費が不明な場合", "<p>古い不動産で取得費が分からない場合、<strong>譲渡価額の5%を概算取得費</strong>とできます。ただし実際の取得費の方が高ければそちらが有利。購入時の契約書を探しましょう。</p>"),
            ("空き家特例との選択", "<p>被相続人が一人暮らしだった家を売る場合、<strong>空き家の3,000万円特別控除</strong>が使える可能性があります。取得費加算とは選択適用なので、有利な方を比較します。</p>"),
        ],
        "faqs": [
            ("相続してすぐ売ると損ですか？", "取得費加算の特例は3年10ヶ月以内が条件なので、むしろ早めの売却が有利な場合が多いです。"),
            ("兄弟で共有のまま売れますか？", "共有者全員の同意が必要です。売却益・税金も持分に応じて各自が申告します。"),
            ("譲渡所得の申告はいつ？", "売却した年の翌年2月16日〜3月15日の確定申告で行います。"),
        ],
    },
    {
        "slug": "vacant-house-deduction",
        "title": "空き家の3,000万円特別控除｜相続した実家の売却",
        "h1": "空き家の3,000万円特別控除",
        "desc": "相続した被相続人居住用家屋（空き家）を売却した際、譲渡所得から3,000万円を控除できる特例の要件・耐震/取壊し要件・期限を解説します。",
        "keywords": "空き家,3000万円特別控除,相続,実家,売却,被相続人居住用家屋",
        "lead": "相続した実家が空き家になり売却する場合、<strong>譲渡所得から3,000万円を控除</strong>できる特例があります（租特法35条3項）。要件が細かいので確認が必要です。",
        "sections": [
            ("制度の概要", "<p>被相続人が一人で住んでいた家を相続した相続人が売却する際、譲渡益から最大<strong>3,000万円を控除</strong>。実家の売却で譲渡税がほぼゼロになることも。</p>"),
            ("主な要件", "<ul><li>1981年5月31日以前の<strong>旧耐震基準</strong>の家屋</li><li>被相続人が<strong>一人暮らし</strong>だった（区分所有建物を除く）</li><li>相続後、空き家のまま（事業・賃貸・居住に使っていない）</li><li>売却時に<strong>耐震改修</strong>するか<strong>家屋を取り壊して</strong>更地で売る</li></ul>"),
            ("期限と金額上限", "<p>相続開始から<strong>3年を経過する年の12月31日まで</strong>に売却。売却代金が<strong>1億円以下</strong>であること。相続人が3人以上の場合は控除額が2,000万円に縮小（2024年改正）。</p>"),
            ("取得費加算との比較", "<p>取得費加算の特例とは<strong>選択適用</strong>。一般に譲渡益が大きいなら空き家特例（3,000万円控除）が有利なことが多いですが、必ず両方試算して比較を。</p>"),
        ],
        "faqs": [
            ("被相続人が老人ホームにいた場合は？", "一定要件（要介護認定を受け施設入所、家屋を他人に使わせていない等）を満たせば対象になります。"),
            ("兄弟で相続した場合は各自3,000万円？", "各相続人がそれぞれ控除を受けられますが、2024年改正で相続人3人以上の場合は1人2,000万円に縮小されました。"),
            ("更地にしてから売る必要がありますか？", "耐震改修して売るか、取り壊して更地で売るかのいずれかが要件です。そのまま（旧耐震のまま）売ると適用されません。"),
        ],
    },
    {
        "slug": "will-probate",
        "title": "遺言書が見つかったら｜検認手続きの流れ",
        "h1": "遺言書の検認手続き",
        "desc": "自筆証書遺言を見つけたときに必要な家庭裁判所の検認手続きの流れ、勝手に開封してはいけない理由、検認が不要なケースを解説します。",
        "keywords": "遺言書,検認,家庭裁判所,開封,自筆証書遺言,民法1004条",
        "lead": "自筆証書遺言を見つけたら、勝手に開封せず<strong>家庭裁判所の検認</strong>が必要です（民法1004条）。検認の流れを解説します。",
        "sections": [
            ("検認とは", "<p>遺言書の<strong>存在と内容を相続人に知らせ、形状や状態を記録して偽造・変造を防ぐ</strong>手続き。遺言の有効・無効を判断するものではありません。</p>"),
            ("勝手に開封してはいけない", "<p>封印のある遺言書を家庭裁判所外で開封すると<strong>5万円以下の過料</strong>（民法1005条）。遺言が無効になるわけではありませんが、トラブルのもとになります。</p>"),
            ("検認の流れ", "<ol><li>被相続人の最後の住所地の家庭裁判所に申立て</li><li>必要書類（遺言書・戸籍一式）を提出</li><li>家裁が検認期日を相続人へ通知</li><li>期日に立会いのもと開封・検認</li><li>検認済証明書の交付（手続きに必要）</li></ol>"),
            ("検認が不要なケース", "<ul><li><strong>公正証書遺言</strong>（公証役場が保管）</li><li><strong>法務局保管制度</strong>を利用した自筆証書遺言</li></ul><p>これらは検認不要ですぐ手続きに使えます。</p>"),
        ],
        "faqs": [
            ("検認にどれくらい時間がかかりますか？", "申立てから検認期日まで通常1〜2ヶ月。相続手続きを急ぐ場合はこの期間を見込んでおきましょう。"),
            ("検認すれば遺言は有効になりますか？", "いいえ。検認は内容を確認・記録する手続きで、有効性の判断はしません。要件不備があれば別途無効を争うことになります。"),
            ("相続人全員が立ち会う必要は？", "全員の立会いは不要です。欠席しても検認は実施され、後日結果が通知されます。"),
        ],
    },
    {
        "slug": "penalty-tax",
        "title": "相続税の延滞税・加算税｜申告漏れ・期限後のペナルティ",
        "h1": "相続税の延滞税と加算税",
        "desc": "相続税の申告・納付が遅れた場合や申告漏れがあった場合のペナルティ（延滞税・無申告加算税・過少申告加算税・重加算税）の税率と回避策を解説します。",
        "keywords": "相続税,延滞税,加算税,無申告加算税,重加算税,ペナルティ,期限後申告",
        "lead": "相続税の申告・納付が<strong>期限（10ヶ月）を過ぎたり申告漏れがあると、本税に加えてペナルティ</strong>が課されます。種類と税率を整理します。",
        "sections": [
            ("延滞税（納付の遅れ）", "<p>法定納期限の翌日から納付までの日数に応じて課される利息的なもの。年<strong>約2.4〜8.7%</strong>（時期・経過期間で変動）。早く納めるほど少なくなります。</p>"),
            ("無申告加算税（申告しなかった）", "<p>期限内に申告しなかった場合、原則<strong>15〜20%</strong>（自主的な期限後申告は軽減）。2024年以降、高額・繰り返しは加重されます。</p>"),
            ("過少申告加算税（少なく申告した）", "<p>当初申告が少なく、後で修正した場合、原則<strong>10%</strong>（一定額超は15%）。税務調査前の自主修正は不適用または軽減。</p>"),
            ("重加算税（仮装・隠蔽）", "<p>意図的に財産を隠す・仮装した場合、<strong>35〜40%</strong>と非常に重い。名義預金の隠匿などが典型例。絶対に避けるべき。</p>"),
        ],
        "faqs": [
            ("申告期限に間に合いそうにありません。", "未分割でも一旦は法定相続分で期限内申告を。期限後より圧倒的に有利です。資金不足は延納・物納も検討できます。"),
            ("ペナルティを軽くする方法は？", "税務調査の通知前に自主的に期限後申告・修正申告すると加算税が軽減・不適用になります。気づいたら早めの自主申告を。"),
            ("延滞税はいつまでかかりますか？", "完納するまで日割りで発生します。一部でも早く納付すれば延滞税を減らせます。"),
        ],
    },
    {
        "slug": "gift-vs-inheritance",
        "title": "生前贈与と相続どっちが得？｜判断のポイント",
        "h1": "生前贈与と相続はどちらが得か",
        "desc": "生前贈与と相続のどちらが有利かを、税率構造・持戻し・不動産コスト・タイミングの観点から比較。ケース別の使い分けの考え方を解説します。",
        "keywords": "生前贈与,相続,どっちが得,比較,暦年贈与,節税,税率",
        "lead": "「生前贈与と相続、どちらが得?」は一概に言えません。<strong>資産規模・年齢・資産の種類</strong>で変わります。判断軸を解説します。",
        "sections": [
            ("税率構造の違い", "<p>贈与税は相続税より税率の上がり方が急ですが、<strong>毎年110万円の基礎控除</strong>を使って長期間かければ、相続財産を効率的に減らせます。少額・長期なら贈与有利。</p>"),
            ("2024年改正の影響", "<p>暦年贈与は<strong>7年持戻し</strong>に延長。直前の駆け込み贈与は効果が薄れました。<strong>早期に着手</strong>するほど贈与のメリットが活きます。</p>"),
            ("不動産は要注意", "<p>不動産の生前贈与は<strong>登録免許税（2%）・不動産取得税</strong>がかかり、相続（登録免許税0.4%・取得税なし）より移転コストが高い。不動産は相続で渡す方が有利なことが多い。</p>"),
            ("ケース別の目安", """<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
<thead><tr style="background:#27AE60;color:white;"><th style="padding:.5rem;border:1px solid #ddd;">状況</th><th style="padding:.5rem;border:1px solid #ddd;">おすすめ</th></tr></thead>
<tbody>
<tr><td style="padding:.5rem;border:1px solid #ddd;">若く長期で渡せる・現金</td><td style="padding:.5rem;border:1px solid #ddd;">生前贈与（暦年）</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">値上がりする資産（自社株等）</td><td style="padding:.5rem;border:1px solid #ddd;">生前贈与（相続時精算課税）</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">不動産</td><td style="padding:.5rem;border:1px solid #ddd;">相続</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">基礎控除内の資産規模</td><td style="padding:.5rem;border:1px solid #ddd;">相続（無税）</td></tr>
</tbody></table>"""),
        ],
        "faqs": [
            ("とりあえず毎年110万円贈与すれば得ですか？", "資産規模が基礎控除内なら相続でも無税のため、贈与の手間が無駄になることも。まず相続税がかかるか試算してから判断を。"),
            ("孫への贈与は得ですか？", "孫は相続人でなければ7年持戻しの対象外で、世代飛ばし効果もあり有利なケースが多いです。"),
            ("不動産を生前にあげたいのですが。", "移転コストが高くつくため、相続まで待つか、相続時精算課税の活用を検討しましょう。"),
        ],
    },
    {
        "slug": "adult-guardianship",
        "title": "成年後見制度とは｜認知症の親の財産管理",
        "h1": "成年後見制度の仕組みと注意点",
        "desc": "認知症などで判断能力が低下した人の財産を守る成年後見制度（法定後見）の仕組み、後見・保佐・補助の3類型、費用、家族信託との違いを解説します。",
        "keywords": "成年後見,法定後見,認知症,財産管理,後見人,家族信託との違い",
        "lead": "<strong>成年後見制度</strong>は、認知症などで判断能力が低下した人の財産管理・契約を後見人が支援・代行する制度です。相続対策との関係で理解が重要です。",
        "sections": [
            ("3つの類型", "<ul><li><strong>後見</strong>：判断能力が欠けているのが通常（最も重い）</li><li><strong>保佐</strong>：判断能力が著しく不十分</li><li><strong>補助</strong>：判断能力が不十分</li></ul><p>程度に応じて後見人等の権限が異なります。</p>"),
            ("手続きと費用", "<p>家庭裁判所に申立て。鑑定が必要な場合あり。後見人には<strong>月2〜6万円程度の報酬</strong>（家裁が決定）。近年は親族より<strong>弁護士・司法書士等の専門職</strong>が選任される傾向。</p>"),
            ("相続対策上の制約", "<p>後見人は<strong>本人の財産保護が最優先</strong>のため、<strong>相続税対策の生前贈与や資産の組み替えは原則できません</strong>。認知症発症後は相続対策がほぼ止まる点が最大の注意点。</p>"),
            ("家族信託との違い", """<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
<thead><tr style="background:#27AE60;color:white;"><th style="padding:.5rem;border:1px solid #ddd;">項目</th><th style="padding:.5rem;border:1px solid #ddd;">成年後見</th><th style="padding:.5rem;border:1px solid #ddd;">家族信託</th></tr></thead>
<tbody>
<tr><td style="padding:.5rem;border:1px solid #ddd;">開始時期</td><td style="padding:.5rem;border:1px solid #ddd;">判断能力低下後</td><td style="padding:.5rem;border:1px solid #ddd;">元気なうちに契約</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">柔軟性</td><td style="padding:.5rem;border:1px solid #ddd;">低い（家裁監督）</td><td style="padding:.5rem;border:1px solid #ddd;">高い</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">相続対策</td><td style="padding:.5rem;border:1px solid #ddd;">原則不可</td><td style="padding:.5rem;border:1px solid #ddd;">設計可能</td></tr>
</tbody></table>"""),
        ],
        "faqs": [
            ("一度後見人がついたら外せますか？", "原則として本人の判断能力が回復しない限り続きます。専門職後見人の報酬も継続的に発生します。"),
            ("家族が後見人になれますか？", "なれますが、近年は親族間トラブル防止のため専門職が選ばれる傾向です。家裁が総合的に判断します。"),
            ("認知症対策はどうすれば？", "判断能力があるうちに<strong>家族信託や任意後見契約</strong>を準備するのが有効です。発症後は選択肢が大きく狭まります。"),
        ],
    },
    {
        "slug": "voluntary-guardianship",
        "title": "任意後見契約とは｜元気なうちに後見人を決めておく",
        "h1": "任意後見契約の活用",
        "desc": "判断能力があるうちに自分で後見人と支援内容を決めておく任意後見契約の仕組み、法定後見との違い、見守り契約・財産管理委任との組み合わせを解説します。",
        "keywords": "任意後見,任意後見契約,見守り契約,財産管理委任,認知症対策",
        "lead": "<strong>任意後見契約</strong>は、判断能力があるうちに「将来支援してくれる人」と「支援内容」を自分で決めておく制度です。法定後見より自由度が高いのが特徴。",
        "sections": [
            ("任意後見の仕組み", "<p>本人と任意後見人になる人が<strong>公正証書</strong>で契約。判断能力が低下したら、家庭裁判所が<strong>任意後見監督人</strong>を選任して効力が発生します。</p>"),
            ("法定後見との違い", "<ul><li>後見人を<strong>自分で選べる</strong>（法定後見は家裁が選任）</li><li>支援内容を<strong>事前に決められる</strong></li><li>ただし取消権はない（本人がした契約を取り消せない）</li></ul>"),
            ("3点セットで備える", "<ul><li><strong>見守り契約</strong>：定期的に連絡・面談し判断能力低下を察知</li><li><strong>財産管理委任契約</strong>：判断能力低下前の身体的サポート</li><li><strong>任意後見契約</strong>：判断能力低下後の本格支援</li></ul><p>この3点セットで切れ目なく備えられます。</p>"),
            ("費用", "<p>公正証書作成費用（1.1万円〜）＋専門家に依頼する場合の報酬。発効後は任意後見監督人への報酬（月1〜3万円程度）も発生します。</p>"),
        ],
        "faqs": [
            ("任意後見と家族信託はどちらがいい？", "目的が異なります。財産の積極的な管理・承継は家族信託、身上監護（医療・介護契約等）は後見が得意。併用も有効です。"),
            ("任意後見契約はいつ効力が出ますか？", "判断能力が低下し、家庭裁判所が任意後見監督人を選任した時点です。契約しただけでは効力は生じません。"),
            ("途中で解除できますか？", "効力発生前なら公証人の認証で自由に解除可能。発効後は正当な理由と家裁の許可が必要です。"),
        ],
    },
    {
        "slug": "disability-minor-credit",
        "title": "相続税の障害者控除・未成年者控除｜税額から直接控除",
        "h1": "障害者控除・未成年者控除",
        "desc": "相続人が障害者・未成年の場合に相続税額から直接差し引ける障害者控除・未成年者控除の計算方法と、控除しきれない分を扶養義務者から引ける仕組みを解説します。",
        "keywords": "障害者控除,未成年者控除,相続税,税額控除,扶養義務者",
        "lead": "相続人が障害者や未成年の場合、相続税額から直接差し引ける<strong>障害者控除・未成年者控除</strong>があります。税額そのものを減らす強力な控除です。",
        "sections": [
            ("未成年者控除", "<p><strong>（18歳−相続時の年齢）×10万円</strong>を相続税額から控除。例：相続時10歳なら（18−10）×10万円＝80万円。</p>"),
            ("障害者控除", "<p><strong>（85歳−相続時の年齢）×10万円</strong>（特別障害者は20万円）を控除。例：一般障害者で相続時60歳なら（85−60）×10万円＝250万円。控除額が大きい。</p>"),
            ("扶養義務者からも引ける", "<p>本人の相続税額から控除しきれない場合、<strong>扶養義務者（配偶者・親・兄弟姉妹等）の相続税額から差し引けます</strong>。家族全体の税負担を軽減できます。</p>"),
            ("適用要件", "<ul><li>法定相続人であること</li><li>財産を取得していること</li><li>日本国内に住所があること（一定の例外あり）</li></ul>"),
        ],
        "faqs": [
            ("障害者手帳は必要ですか？", "原則として障害者手帳等で障害の程度を証明します。要介護認定とは別なので確認が必要です。"),
            ("過去の相続で控除を使うと？", "2回目以降は控除額に上限調整があります（前回使った分を差し引く）。"),
            ("未成年者控除は何歳まで？", "2022年の成年年齢引き下げに伴い、18歳未満が対象です。"),
        ],
    },
    {
        "slug": "collect-koseki",
        "title": "相続手続きの戸籍の集め方｜出生から死亡まで",
        "h1": "相続に必要な戸籍の集め方",
        "desc": "相続手続きで必須となる被相続人の「出生から死亡まで」の戸籍の集め方、本籍地の追い方、郵送請求の方法、法定相続情報証明制度の活用を解説します。",
        "keywords": "戸籍,集め方,出生から死亡まで,相続,本籍地,郵送請求",
        "lead": "相続手続きでは被相続人の<strong>出生から死亡までの連続した戸籍</strong>が必要です。集め方のコツを解説します。",
        "sections": [
            ("なぜ出生からの戸籍が必要か", "<p>相続人を確定するため。<strong>認知した子・前婚の子</strong>などが過去の戸籍から判明することがあり、漏れると遺産分割協議がやり直しになります。</p>"),
            ("集め方の手順", "<ol><li>死亡時の本籍地で「死亡の記載がある戸籍」を取得</li><li>その戸籍から<strong>一つ前の本籍地・戸籍</strong>をたどる</li><li>出生まで遡って連続させる</li><li>転籍・改製があれば<strong>改製原戸籍・除籍謄本</strong>も取得</li></ol>"),
            ("郵送請求の方法", "<ul><li>各市区町村のサイトで請求書をダウンロード</li><li>本人確認書類のコピー・定額小為替（手数料）・返信用封筒を同封</li><li>「相続のため出生から死亡までの全部」と明記すると親切に揃えてくれる</li></ul><p>2024年から本籍地以外でも広域交付が一部可能になりました。</p>"),
            ("集めた後は法定相続情報を", "<p>戸籍一式が揃ったら<strong>法定相続情報証明制度</strong>で一覧図を作ると、以後の手続きで戸籍の束を何度も出さずに済みます。</p>"),
        ],
        "faqs": [
            ("戸籍集めはどれくらいかかりますか？", "本籍が転々としていると1〜2ヶ月かかることも。相続手続き全体のボトルネックになりやすいので早めに着手を。"),
            ("自分で集めるのは難しいですか？", "古い手書きの改製原戸籍は読みにくく、たどるのに手間がかかります。難しければ司法書士・行政書士に代行を依頼できます。"),
            ("広域交付とは？", "2024年3月開始。最寄りの市区町村窓口で本籍地以外の戸籍もまとめて請求できる制度です（一部制限あり）。"),
        ],
    },
    {
        "slug": "inheritance-consultation",
        "title": "相続の相談はどこにする？｜専門家の選び方",
        "h1": "相続の相談先の選び方",
        "desc": "相続の相談先（税理士・弁護士・司法書士・行政書士・銀行）の役割の違いと、悩み別の適切な相談先、無料相談の活用法を解説します。",
        "keywords": "相続,相談,どこ,専門家,税理士,弁護士,司法書士,選び方",
        "lead": "相続の相談先は悩みの内容で変わります。<strong>誰に相談すべきか</strong>を悩み別に整理しました。",
        "sections": [
            ("悩み別の相談先", """<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">
<thead><tr style="background:#27AE60;color:white;"><th style="padding:.5rem;border:1px solid #ddd;">悩み</th><th style="padding:.5rem;border:1px solid #ddd;">相談先</th></tr></thead>
<tbody>
<tr><td style="padding:.5rem;border:1px solid #ddd;">相続税の申告・節税</td><td style="padding:.5rem;border:1px solid #ddd;">税理士</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">相続人間の争い・調停</td><td style="padding:.5rem;border:1px solid #ddd;">弁護士</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">不動産の相続登記</td><td style="padding:.5rem;border:1px solid #ddd;">司法書士</td></tr>
<tr><td style="padding:.5rem;border:1px solid #ddd;">書類作成のみ</td><td style="padding:.5rem;border:1px solid #ddd;">行政書士</td></tr>
</tbody></table>"""),
            ("税理士選びのコツ", "<p>相続税は<strong>相続専門の税理士</strong>を選ぶのが重要。相続案件の経験が少ない税理士だと小規模宅地等の特例の適用漏れなどで損をすることも。実績・料金を比較しましょう。</p>"),
            ("ワンストップ事務所", "<p>税理士・司法書士・弁護士が<strong>連携するワンストップ事務所</strong>なら、窓口一つで申告・登記・紛争対応まで完結。たらい回しを防げます。</p>"),
            ("無料相談を活用", "<ul><li>自治体・税理士会・司法書士会の無料相談会</li><li>法テラス（経済的に余裕がない場合）</li><li>各事務所の初回無料相談</li></ul><p>まず無料相談で方向性と見積もりを把握しましょう。</p>"),
        ],
        "faqs": [
            ("まず誰に相談すればいい？", "相続税がかかりそうなら税理士、争いがあれば弁護士、不動産中心なら司法書士。判断に迷えば、まず無料相談やワンストップ事務所へ。"),
            ("銀行の相続相談はどうですか？", "手続き代行は便利ですが手数料が高め（最低100万円〜のことも）。内容を理解した上で専門家と比較しましょう。"),
            ("相談前に準備することは？", "家族構成・資産の概要を整理しておくとスムーズ。家系図Naviで相続分・相続税を試算してから相談すると話が早いです。"),
        ],
    },
]

GLOSSARY = [
    ("法定相続人", "民法で定められた相続人。配偶者は常に相続人、子（第1順位）→直系尊属（第2順位）→兄弟姉妹（第3順位）の順で組み合わせが決まる。"),
    ("法定相続分", "民法900条が定める相続割合。遺言がない場合のデフォルト基準。"),
    ("遺留分", "配偶者・子・直系尊属に保証された最低限の取り分（民法1042条）。兄弟姉妹にはなし。"),
    ("遺留分侵害額請求", "遺留分を侵害された者が侵害額の金銭支払を請求する権利（民法1046条）。時効1年。"),
    ("代襲相続", "相続人が死亡・欠格・廃除された場合、その子が代わりに相続する制度（民法887条2項）。"),
    ("数次相続", "相続発生後、遺産分割未了のうちに別の相続が発生すること。"),
    ("単純承認", "被相続人の権利義務をすべて承継すること。3ヶ月以内に放棄・限定承認しないと自動的にこれになる。"),
    ("相続放棄", "相続人の地位を放棄する手続き。家庭裁判所への申述が必要、3ヶ月以内（民法915条）。"),
    ("限定承認", "プラス財産の範囲でマイナス財産を引き受ける手続き。相続人全員での申述が必要。"),
    ("遺産分割協議", "相続人全員で遺産の分け方を決める協議。協議書を作成し全員が実印を押印。"),
    ("特別受益", "相続人が被相続人から生前に受けた特別な贈与（民法903条）。相続時に持ち戻し計算。"),
    ("寄与分", "被相続人の財産維持・増加に特別な貢献をした相続人の取り分を増やす制度（民法904条の2）。"),
    ("特別寄与料", "相続人以外の親族が無償で介護等した場合に金銭請求できる制度（民法1050条、2019年新設）。"),
    ("基礎控除", "相続税の非課税枠。3,000万円 + 600万円 × 法定相続人数（相続税法15条）。"),
    ("配偶者控除（配偶者の税額軽減）", "配偶者は法定相続分または1.6億円のいずれか多い方まで非課税（相続税法19条の2）。"),
    ("生命保険金の非課税枠", "500万円 × 法定相続人数まで非課税（相続税法12条）。"),
    ("小規模宅地等の特例", "自宅・事業用土地の評価額を最大80%減額できる制度（租特法69条の4）。"),
    ("路線価", "国税庁が定める道路に面する1㎡あたりの土地評価額。公示地価の80%水準。"),
    ("倍率方式", "路線価がない地域で、固定資産税評価額に倍率を掛けて土地評価する方法。"),
    ("自筆証書遺言", "全文・日付・氏名を自書し押印した遺言書（民法968条）。財産目録はPC作成可（2019年改正）。"),
    ("公正証書遺言", "公証人が作成する遺言書。証人2名必要、費用数万円〜だが無効リスクが極めて低い。"),
    ("法務局保管制度", "自筆証書遺言を法務局で保管する制度（2020年〜）。3,900円、検認不要。"),
    ("検認", "家庭裁判所が遺言書の存在と内容を確認する手続き。自筆証書遺言の開封前に必要。"),
    ("遺言執行者", "遺言の内容を実現する者。遺言で指定可、家庭裁判所が選任することも。"),
    ("配偶者居住権", "配偶者が自宅に住み続ける権利（民法1028条、2020年施行）。所有権と分離可能。"),
    ("家族信託（民事信託）", "家族間で財産管理を委ねる信託契約。認知症対策・事業承継に活用。"),
    ("成年後見制度", "判断能力低下者の財産管理を後見人が代行する制度。法定後見と任意後見の2種類。"),
    ("暦年贈与", "年110万円まで贈与税非課税。2024年改正で7年持戻しに（相続税法21条の5）。"),
    ("相続時精算課税", "累計2,500万円まで贈与税ゼロ、相続時に精算する制度（相続税法21条の9）。"),
    ("事業承継税制", "後継者への自社株贈与・相続税を猶予・免除する制度（円滑化法）。"),
    ("普通養子", "養子縁組後も実親との親族関係が継続。両方から相続可能。"),
    ("特別養子", "実親との親族関係が終了する養子縁組（民法817条の9）。家裁審判が必要。"),
    ("半血兄弟", "親の片方のみ同じ兄弟。全血兄弟の1/2の相続分（民法900条4号但書）。"),
    ("換価分割", "遺産を売却して現金で分割する方法。不動産分割の典型解。"),
    ("代償分割", "特定の相続人が遺産を取得し、他の相続人に金銭等で代償する方法。"),
    ("相続登記", "不動産の所有権を相続人名義に変更する登記。2024年4月から3年以内に義務化。"),
    ("準確定申告", "被相続人の所得税申告。相続開始から4ヶ月以内（所得税法125条）。"),
    ("仮払い制度", "遺産分割前でも預金の一部を払い戻し可能な制度（民法909条の2）。上限150万円/金融機関。"),
    ("団体信用生命保険（団信）", "住宅ローン契約者が死亡した時に残債が消える保険。多くの住宅ローンに付帯。"),
    ("不在者財産管理人", "行方不明の相続人の財産を管理する人。家庭裁判所が選任。"),
]


def render_glossary():
    body = "\n".join(
        f'<dt id="t-{i}">{term}</dt><dd>{desc}</dd>'
        for i, (term, desc) in enumerate(GLOSSARY)
    )
    nav = " · ".join(
        f'<a href="#t-{i}">{term}</a>'
        for i, (term, _) in enumerate(GLOSSARY)
    )
    desc_text = f"相続・事業承継の専門用語{len(GLOSSARY)}語を解説。法定相続分・遺留分・基礎控除・小規模宅地・家族信託など、相続実務で必須の用語を網羅。"
    defined_items = [
        {
            "@type": "DefinedTerm",
            "name": term,
            "description": desc.replace('<strong>', '').replace('</strong>', ''),
            "inDefinedTermSet": SITE_URL + "/glossary/",
        }
        for term, desc in GLOSSARY
    ]
    jsonld = {
        "@context": "https://schema.org",
        "@type": "DefinedTermSet",
        "name": "相続・事業承継用語集",
        "description": desc_text,
        "url": SITE_URL + "/glossary/",
        "hasDefinedTerm": defined_items,
    }
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>相続・事業承継用語集（{len(GLOSSARY)}語）｜家系図Navi</title>
  <meta name="description" content="{desc_text}">
  <meta name="keywords" content="相続,用語集,事業承継,法定相続分,遺留分,基礎控除,専門用語">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{CANONICAL_BASE}/glossary/">
  <meta property="og:title" content="相続・事業承継用語集（{len(GLOSSARY)}語）｜家系図Navi">
  <meta property="og:description" content="{desc_text}">
  <meta property="og:url" content="{SITE_URL}/glossary/">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{ICON}">
  <script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
  <link rel="icon" href="../icon_192.png">
  <style>
    :root {{ --green: #27AE60; --light-bg: #f8fdf9; --text: #2c3e50; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: var(--light-bg); color: var(--text); line-height: 1.8; }}
    header {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 2.5rem 1.5rem; text-align: center; }}
    header h1 {{ font-size: 1.8rem; margin: .5rem 0; }}
    header .nav {{ font-size: .9rem; opacity: .9; }}
    header .nav a {{ color: white; text-decoration: none; }}
    main {{ max-width: 880px; margin: 0 auto; padding: 2rem 1.5rem; }}
    .toc {{ background: white; padding: 1.2rem; border-radius: 8px; font-size: .85rem; line-height: 2; margin-bottom: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,.06); }}
    .toc a {{ color: var(--green); text-decoration: none; }}
    dt {{ font-weight: 700; color: var(--green); margin-top: 1.5rem; font-size: 1.05rem; }}
    dd {{ margin-left: 0; margin-top: .3rem; padding-left: 1rem; border-left: 3px solid #d4e9d8; }}
    footer {{ text-align: center; padding: 2rem; font-size: .85rem; color: #888; border-top: 1px solid #eee; margin-top: 3rem; }}
    footer a {{ color: var(--green); text-decoration: none; }}
  </style>
</head>
<body>
<header>
  <div class="nav"><a href="../">🌳 家系図Navi</a> ＞ 用語集</div>
  <h1>相続・事業承継用語集</h1>
  <p style="opacity:.95;margin-top:.6rem;">{len(GLOSSARY)}語を専門家の視点で簡潔に解説</p>
</header>
<main>
  <div class="toc"><strong>索引：</strong>{nav}</div>
  <dl>{body}</dl>
  {ad_block()}
</main>
<footer>
  <p>© 2026 Mirai Navi — <a href="../">家系図Navi / Family Tree Guide</a></p>
  <p style="margin-top:.5rem;font-size:.82rem;">🔗 姉妹サイト：<a href="https://mirainavi.net/?utm_source=note&utm_medium=article&utm_campaign=brand-story&utm_content=cta_text_bottom" target="_blank" rel="noopener" style="color:#16A085;">ミライNavi</a> ｜ <a href="https://teso-navi.vercel.app/" target="_blank" rel="noopener" style="color:#16A085;">手相ナビ</a> ｜ <a href="https://kakeizu-souzoku-navi.blog.jp/" target="_blank" rel="noopener" style="color:#16A085;">運営ブログ</a></p>
  <p style="margin-top:.5rem;font-size:.78rem;color:#999;">当サイトはアフィリエイト広告（プロモーション）を利用しています。｜<a href="https://yadianqiteng5-spec.github.io/kakeizu-navi-lp/about/" style="color:#16A085;">運営者情報・プライバシー</a></p>
</footer>
</body>
</html>
"""


QUICK_TABLES = [
    {
        "slug": "table-inheritance-tax",
        "title": "相続税早見表｜遺産額×法定相続人数の概算税額一覧",
        "h1": "相続税早見表（配偶者と子のケース）",
        "desc": "遺産5,000万円〜10億円までの相続税概算を、配偶者+子1〜4人のパターン別に一覧表示。配偶者控除適用前後の両方を掲載。",
        "keywords": "相続税,早見表,概算,遺産額,法定相続人,配偶者控除",
        "intro": "配偶者と子で相続する場合の<strong>相続税概算</strong>を遺産額別にまとめました（配偶者の税額軽減フル適用前提）。国税庁速算表準拠の計算で、実際の試算は<a href=\"" + APP_URL + "\">家系図Navi</a>でも可能です。",
        "table_header": ["遺産額", "子1人", "子2人", "子3人", "子4人"],
        "table_rows": [
            ["5,000万円", "40万円", "10万円", "0円", "0円"],
            ["7,000万円", "160万円", "113万円", "80万円", "50万円"],
            ["1億円", "385万円", "315万円", "263万円", "225万円"],
            ["1.5億円", "920万円", "748万円", "665万円", "588万円"],
            ["2億円", "1,670万円", "1,350万円", "1,218万円", "1,125万円"],
            ["3億円", "3,460万円", "2,860万円", "2,540万円", "2,350万円"],
            ["5億円", "7,605万円", "6,555万円", "5,963万円", "5,500万円"],
            ["10億円", "1億9,750万円", "1億7,810万円", "1億6,635万円", "1億5,650万円"],
        ],
        "notes": [
            "上記は配偶者と子で相続し、配偶者の税額軽減（最大1.6億円または法定相続分まで非課税）をフル活用した場合の合計税額。",
            "実際の税額は遺産分割割合・適用特例・養子の有無等で変動します。",
            "基礎控除 = 3,000万円 + 600万円 × 法定相続人数（相続税法15条）。",
        ],
    },
    {
        "slug": "table-legal-share",
        "title": "法定相続分早見表｜配偶者・子・直系尊属・兄弟姉妹",
        "h1": "法定相続分早見表",
        "desc": "民法900条の法定相続分を、配偶者・子・直系尊属・兄弟姉妹の組み合わせ別に一覧表示。代襲相続・半血兄弟・養子のケースも。",
        "keywords": "法定相続分,早見表,民法900条,配偶者,子,直系尊属,兄弟姉妹",
        "intro": "民法900条の<strong>法定相続分</strong>を組み合わせ別に整理しました。",
        "table_header": ["相続人の組み合わせ", "配偶者", "他の相続人"],
        "table_rows": [
            ["配偶者のみ", "1/1（全部）", "—"],
            ["配偶者 + 子1人", "1/2", "1/2"],
            ["配偶者 + 子2人", "1/2", "各1/4"],
            ["配偶者 + 子3人", "1/2", "各1/6"],
            ["配偶者 + 父母（両方存命）", "2/3", "各1/6"],
            ["配偶者 + 父母（片方のみ）", "2/3", "1/3"],
            ["配偶者 + 兄弟姉妹2人", "3/4", "各1/8"],
            ["配偶者 + 兄弟姉妹3人", "3/4", "各1/12"],
            ["子のみ（複数）", "—", "人数で均等按分"],
            ["父母のみ", "—", "1/1または均等按分"],
            ["兄弟姉妹のみ", "—", "人数で均等按分"],
        ],
        "notes": [
            "半血兄弟（親の片方のみ同じ）は全血兄弟の1/2（民法900条4号但書）。",
            "代襲相続人は被代襲者の相続分を引き継ぎます。",
            "養子は実子と同じ相続分（人数の算入制限は基礎控除等の計算でのみ適用）。",
        ],
    },
    {
        "slug": "table-gift-tax",
        "title": "贈与税早見表｜特例税率・一般税率の対比",
        "h1": "贈与税早見表",
        "desc": "暦年贈与の贈与税額を、特例税率（直系尊属→18歳以上の子・孫）と一般税率で対比して一覧表示。基礎控除110万円差し引き後の課税価格別。",
        "keywords": "贈与税,早見表,特例税率,一般税率,直系尊属,暦年贈与",
        "intro": "<strong>暦年贈与</strong>の贈与税額（基礎控除110万円差引後の課税価格別）を、特例税率と一般税率で比較表示します。",
        "table_header": ["贈与額", "課税価格", "特例税率", "一般税率"],
        "table_rows": [
            ["200万円", "90万円", "9万円", "9万円"],
            ["300万円", "190万円", "19万円", "19万円"],
            ["500万円", "390万円", "48.5万円", "53万円"],
            ["1,000万円", "890万円", "177万円", "231万円"],
            ["1,500万円", "1,390万円", "366万円", "450.5万円"],
            ["2,000万円", "1,890万円", "585.5万円", "695万円"],
            ["3,000万円", "2,890万円", "1,035.5万円", "1,195万円"],
            ["5,000万円", "4,890万円", "2,049.5万円", "2,289.5万円"],
            ["1億円", "9,890万円", "4,799.5万円", "5,039.5万円"],
        ],
        "notes": [
            "特例税率は<strong>直系尊属（父母・祖父母）から18歳以上の子・孫</strong>への贈与に適用。",
            "それ以外は一般税率。基礎控除110万円/年は受贈者ごと。",
            "2024年改正で<strong>暦年贈与の持戻し期間は3年→7年</strong>に延長（経過措置あり）。",
        ],
    },
    {
        "slug": "table-basic-deduction",
        "title": "基礎控除額早見表｜法定相続人数別の非課税枠",
        "h1": "相続税基礎控除額早見表",
        "desc": "法定相続人数1〜10人別の相続税基礎控除額、生命保険非課税枠、死亡退職金非課税枠を一覧表示。",
        "keywords": "基礎控除,早見表,相続税,生命保険,非課税枠,死亡退職金",
        "intro": "相続税の<strong>基礎控除</strong>と各種非課税枠を法定相続人数別に整理しました（相続税法15条・12条）。",
        "table_header": ["相続人数", "基礎控除", "生命保険非課税", "死亡退職金非課税"],
        "table_rows": [
            ["1人", "3,600万円", "500万円", "500万円"],
            ["2人", "4,200万円", "1,000万円", "1,000万円"],
            ["3人", "4,800万円", "1,500万円", "1,500万円"],
            ["4人", "5,400万円", "2,000万円", "2,000万円"],
            ["5人", "6,000万円", "2,500万円", "2,500万円"],
            ["6人", "6,600万円", "3,000万円", "3,000万円"],
            ["7人", "7,200万円", "3,500万円", "3,500万円"],
            ["8人", "7,800万円", "4,000万円", "4,000万円"],
            ["10人", "9,000万円", "5,000万円", "5,000万円"],
        ],
        "notes": [
            "基礎控除 = 3,000万円 + 600万円 × 法定相続人数。",
            "生命保険・死亡退職金の非課税枠 = それぞれ500万円 × 法定相続人数。",
            "養子は基礎控除の人数計算で<strong>実子あり1人/実子なし2人</strong>まで（相続税法15条2項）。",
            "相続放棄者も基礎控除の人数に含めて計算します。",
        ],
    },
    {
        "slug": "table-deadlines",
        "title": "相続手続き期限カレンダー｜7日〜10ヶ月の全期限一覧",
        "h1": "相続手続きの期限早見表",
        "desc": "相続発生後の各種手続きの期限を一覧化。死亡届7日・準確定申告4ヶ月・相続税申告10ヶ月・相続登記3年など、漏れなくチェック。",
        "keywords": "相続,期限,カレンダー,死亡届,相続放棄,相続税申告,相続登記",
        "intro": "相続発生後の<strong>各種手続き期限</strong>を早見表にまとめました。期限超過は不利益・罰則の対象となるため要注意です。",
        "table_header": ["期限", "手続き", "根拠"],
        "table_rows": [
            ["7日以内", "死亡届の提出", "戸籍法86条"],
            ["10日以内", "厚生年金死亡届", "厚生年金保険法98条"],
            ["14日以内", "国民健康保険・国民年金死亡届、世帯主変更届", "各法令"],
            ["3ヶ月以内", "相続放棄・限定承認の申述", "民法915条"],
            ["4ヶ月以内", "被相続人の所得税準確定申告・納付", "所得税法125条"],
            ["10ヶ月以内", "相続税の申告・納付", "相続税法27条"],
            ["1年以内", "遺留分侵害額請求（侵害を知った時から）", "民法1048条"],
            ["3年以内", "相続登記の申請（2024年義務化）", "不動産登記法76条の2"],
            ["5年10ヶ月以内", "更正の請求（税額減額の修正）", "国税通則法23条"],
        ],
        "notes": [
            "期限を過ぎても手続き可能な場合がありますが、加算税・延滞税・過料の対象となることがあります。",
            "相続放棄の3ヶ月は<strong>「相続開始を知った日」</strong>から起算。",
            "相続税申告は<strong>被相続人の最後の住所地</strong>を管轄する税務署に提出。",
        ],
    },
]


def render_quick_table(qt):
    url = f"{SITE_URL}/{qt['slug']}/"
    header_html = "".join(f'<th>{h}</th>' for h in qt['table_header'])
    rows_html = "\n".join(
        "<tr>" + "".join(f'<td>{c}</td>' for c in row) + "</tr>"
        for row in qt['table_rows']
    )
    notes_html = "\n".join(f'<li>{n}</li>' for n in qt['notes'])

    # JSON-LD: Table relevant + Article
    article_jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": qt["h1"],
        "description": qt["desc"],
        "image": ICON,
        "datePublished": "2026-05-30",
        "dateModified": "2026-05-30",
        "author": {"@type": "Person", "name": "Mirai Navi"},
        "publisher": {"@type": "Organization", "name": "家系図Navi",
                      "logo": {"@type": "ImageObject", "url": ICON}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "inLanguage": "ja",
    }
    breadcrumb_jsonld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "家系図Navi", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "早見表", "item": SITE_URL + "/guides/"},
            {"@type": "ListItem", "position": 3, "name": qt["h1"], "item": url},
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{qt['title']}｜家系図Navi</title>
  <meta name="description" content="{qt['desc']}">
  <meta name="keywords" content="{qt['keywords']}">
  <meta name="robots" content="index, follow">
  <meta name="author" content="Mirai Navi">
  <link rel="canonical" href="{url.replace(SITE_URL, CANONICAL_BASE)}">
  <meta property="og:title" content="{qt['title']}｜家系図Navi">
  <meta property="og:description" content="{qt['desc']}">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="article">
  <meta property="og:image" content="{ICON}">
  <script type="application/ld+json">{json.dumps(article_jsonld, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb_jsonld, ensure_ascii=False)}</script>
  <link rel="icon" href="../icon_192.png">
  <style>
    :root {{ --green: #27AE60; --light-bg: #f8fdf9; --text: #2c3e50; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: var(--light-bg); color: var(--text); line-height: 1.7; }}
    header {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 2.5rem 1.5rem; text-align: center; }}
    header h1 {{ font-size: 1.8rem; margin: .5rem 0; }}
    header .nav {{ font-size: .85rem; opacity: .9; }}
    header .nav a {{ color: white; text-decoration: none; }}
    main {{ max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; }}
    table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,.06); border-radius: 8px; overflow: hidden; margin: 1.5rem 0; }}
    th {{ background: var(--green); color: white; padding: .7rem .5rem; text-align: center; font-size: .9rem; }}
    td {{ padding: .65rem .5rem; border-bottom: 1px solid #eee; text-align: center; font-size: .9rem; }}
    tr:hover td {{ background: #f8fdf9; }}
    .notes {{ background: #fff8e1; border-left: 4px solid #f39c12; padding: 1rem 1.2rem; border-radius: 4px; margin: 1.5rem 0; font-size: .9rem; }}
    .notes ul {{ padding-left: 1.4rem; }}
    .cta-box {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 1.6rem; border-radius: 12px; text-align: center; margin: 2rem 0; }}
    .cta-box a {{ display: inline-block; padding: .7rem 2rem; background: white; color: var(--green); font-weight: 700; border-radius: 50px; text-decoration: none; margin-top: .5rem; }}
    footer {{ text-align: center; padding: 2rem; font-size: .85rem; color: #888; border-top: 1px solid #eee; margin-top: 2rem; }}
    footer a {{ color: var(--green); text-decoration: none; }}
  </style>
</head>
<body>
<header>
  <div class="nav"><a href="../">🌳 家系図Navi</a> ＞ {qt['h1']}</div>
  <h1>{qt['h1']}</h1>
</header>
<main>
  <p>{qt['intro']}</p>
  <table>
    <thead><tr>{header_html}</tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
  <div class="notes">
    <strong>📌 注釈・前提条件</strong>
    <ul>{notes_html}</ul>
  </div>
  <div class="cta-box">
    <h3 style="margin-bottom:.5rem;">あなたのケースの正確な金額を試算</h3>
    <p style="font-size:.95rem;opacity:.95;">家族構成と資産額を入力するだけで、配偶者控除・各種特例を反映した正確な相続税概算を取得できます。</p>
    <a href="{APP_URL}" rel="noopener">家系図Naviを試す（無料）→</a>
  </div>
  {ad_block()}
</main>
<footer>
  <p>© 2026 Mirai Navi — <a href="../">家系図Navi</a> ｜ <a href="../guides/">記事一覧</a> ｜ <a href="../glossary/">用語集</a></p>
  <p style="margin-top:.5rem;font-size:.82rem;">🔗 姉妹サイト：<a href="https://mirainavi.net/?utm_source=note&utm_medium=article&utm_campaign=brand-story&utm_content=cta_text_bottom" target="_blank" rel="noopener" style="color:#16A085;">ミライNavi</a> ｜ <a href="https://teso-navi.vercel.app/" target="_blank" rel="noopener" style="color:#16A085;">手相ナビ</a> ｜ <a href="https://kakeizu-souzoku-navi.blog.jp/" target="_blank" rel="noopener" style="color:#16A085;">運営ブログ</a></p>
  <p style="margin-top:.5rem;font-size:.78rem;color:#999;">当サイトはアフィリエイト広告（プロモーション）を利用しています。｜<a href="https://yadianqiteng5-spec.github.io/kakeizu-navi-lp/about/" style="color:#16A085;">運営者情報・プライバシー</a></p>
</footer>
</body>
</html>
"""


CASE_STUDIES = [
    {"id": 1, "title": "配偶者と子2人・遺産8,000万円", "family": "夫（被相続人）／妻／長男／長女",
     "estate": "8,000万円（自宅4,000万・預貯金4,000万）",
     "shares": [("妻", "1/2", "4,000万円"), ("長男", "1/4", "2,000万円"), ("長女", "1/4", "2,000万円")],
     "tax": "基礎控除4,800万円。課税遺産3,200万円。相続税の総額は約175万円（配偶者控除前）。妻が法定相続分を取得すれば配偶者控除で妻分は非課税、実質負担は子2人分のみ。",
     "point": "最も標準的なケース。小規模宅地等の特例を使えば自宅評価が80%減となり、課税遺産が大きく下がる可能性。"},
    {"id": 2, "title": "配偶者のみ・遺産1億円", "family": "夫（被相続人）／妻（子なし・親なし・兄弟なし）",
     "estate": "1億円",
     "shares": [("妻", "1/1", "1億円")],
     "tax": "配偶者控除（1.6億円まで非課税）により相続税はゼロ。",
     "point": "配偶者がすべて取得。ただし妻の二次相続では相続人が変わるため、その時の相続人（兄弟姉妹や甥姪）を見据えた対策が必要。"},
    {"id": 3, "title": "子のみ3人・遺産1.5億円", "family": "母（被相続人・父は既に死亡）／長男／次男／長女",
     "estate": "1.5億円",
     "shares": [("長男", "1/3", "5,000万円"), ("次男", "1/3", "5,000万円"), ("長女", "1/3", "5,000万円")],
     "tax": "基礎控除4,800万円。課税遺産1億200万円。相続税の総額は約1,440万円。配偶者控除が使えないため負担が大きい。",
     "point": "二次相続の典型。一次相続（父）の段階で配分を工夫していれば、トータルの税負担を抑えられた可能性が高い。"},
    {"id": 4, "title": "配偶者と親・子なし夫婦・遺産6,000万円", "family": "夫（被相続人）／妻／夫の母（存命）",
     "estate": "6,000万円",
     "shares": [("妻", "2/3", "4,000万円"), ("夫の母", "1/3", "2,000万円")],
     "tax": "基礎控除4,200万円。課税遺産1,800万円。配偶者控除で妻分は非課税、母の分のみ課税。",
     "point": "子がいない場合、第2順位の直系尊属が相続人に。妻と義母の関係が良好でないと分割協議が難航しがち。遺言書推奨。"},
    {"id": 5, "title": "配偶者と兄弟・子なし夫婦・遺産5,000万円", "family": "夫（被相続人）／妻／夫の弟（親は既に死亡）",
     "estate": "5,000万円",
     "shares": [("妻", "3/4", "3,750万円"), ("夫の弟", "1/4", "1,250万円")],
     "tax": "基礎控除4,200万円。課税遺産800万円。配偶者控除で妻分非課税。",
     "point": "兄弟姉妹には遺留分がないため、遺言書で「妻に全部」とすれば弟は何も請求できない。子なし夫婦は遺言書が必須。"},
    {"id": 6, "title": "代襲相続・孫が相続・遺産9,000万円", "family": "祖父（被相続人）／長男（既に死亡）／長男の子＝孫2人／次男",
     "estate": "9,000万円",
     "shares": [("次男", "1/2", "4,500万円"), ("孫A（長男代襲）", "1/4", "2,250万円"), ("孫B（長男代襲）", "1/4", "2,250万円")],
     "tax": "基礎控除4,800万円（法定相続人3人）。課税遺産4,200万円。孫は代襲相続人のため2割加算の対象外。",
     "point": "長男が先に死亡しているため孫が代襲。代襲相続人の孫は2割加算されない（養子の孫とは異なる）。"},
    {"id": 7, "title": "相続放棄で順位変動・遺産3,000万円＋借金", "family": "父（被相続人）／長男（放棄）／父の弟",
     "estate": "プラス3,000万円・借金5,000万円",
     "shares": [("（長男が放棄）", "—", "次順位へ"), ("父の弟", "—", "放棄しなければ承継")],
     "tax": "債務超過のため長男は相続放棄。放棄により次順位（父の弟）に相続権が移るため、弟も連鎖的に放棄が必要。",
     "point": "債務超過時は相続人全員が順次放棄する必要。放棄者の子は代襲しないため、孫に迷惑がかからない点も子の死亡と異なる。"},
    {"id": 8, "title": "半血兄弟が混在・遺産6,000万円", "family": "本人（被相続人・配偶者/子/親なし）／全血兄2人／異母弟1人",
     "estate": "6,000万円",
     "shares": [("全血兄A", "2/5", "2,400万円"), ("全血兄B", "2/5", "2,400万円"), ("異母弟", "1/5", "1,200万円")],
     "tax": "基礎控除4,800万円。課税遺産1,200万円。兄弟相続のため全員2割加算。",
     "point": "半血兄弟（異母弟）は全血兄弟の1/2の相続分（民法900条4号但書）。比率は 2:2:1 で按分。"},
    {"id": 9, "title": "普通養子がいる・遺産1.2億円", "family": "父（被相続人）／妻／実子1人／養子1人（婿養子）",
     "estate": "1.2億円",
     "shares": [("妻", "1/2", "6,000万円"), ("実子", "1/4", "3,000万円"), ("養子", "1/4", "3,000万円")],
     "tax": "基礎控除は実子ありのため養子1人まで算入＝法定相続人3人で4,800万円。養子も実子と同じ相続分。",
     "point": "普通養子は実親・養親の双方から相続可能。基礎控除の人数算入は実子ありで1人まで（相続税法15条2項）。"},
    {"id": 10, "title": "特別養子がいる・遺産8,000万円", "family": "養親（被相続人）／配偶者／特別養子1人（実親との関係終了）",
     "estate": "8,000万円",
     "shares": [("配偶者", "1/2", "4,000万円"), ("特別養子", "1/2", "4,000万円")],
     "tax": "特別養子は実子と同じ扱いで人数制限なし。基礎控除4,200万円（法定相続人2人）。",
     "point": "特別養子は実親との親族関係が終了（民法817条の9）。養親からのみ相続し、実親からは相続しない。"},
    {"id": 11, "title": "事業承継・自社株が遺産の大半・遺産3億円", "family": "社長（被相続人）／妻／後継者の長男／非後継の次男",
     "estate": "3億円（自社株2億円・自宅5,000万・預貯金5,000万）",
     "shares": [("妻", "1/2", "1.5億円"), ("長男", "1/4", "7,500万円"), ("次男", "1/4", "7,500万円")],
     "tax": "基礎控除4,800万円。課税遺産2.52億円。相続税の総額は約3,460万円。自社株の納税資金確保が課題。",
     "point": "自社株を後継者の長男に集中させたいが、法定相続分通りだと次男にも分散。遺言＋事業承継税制（納税猶予）＋次男への代償金（生命保険）で設計。"},
    {"id": 12, "title": "二次相続まで考慮・遺産2億円", "family": "夫（一次被相続人）／妻（固有資産5,000万）／子2人",
     "estate": "一次2億円・妻固有5,000万円",
     "shares": [("一次：妻", "調整", "取得割合を最適化"), ("一次：子2人", "調整", "残り")],
     "tax": "配偶者100%取得：一次0＋二次約6,930万円。配偶者50%取得：合計約3,190万円。配偶者0%：合計約3,170万円。",
     "point": "配偶者控除をフル活用（100%取得）すると二次相続で大増税。配偶者取得を30〜50%に抑えるのが税額最小化の目安。"},
    {"id": 13, "title": "小規模宅地等の特例・自宅中心・遺産1億円", "family": "父（被相続人）／同居の長男（家なき子でなく同居親族）",
     "estate": "1億円（自宅土地8,000万円330㎡・預貯金2,000万円）",
     "shares": [("長男", "1/1", "1億円（特例適用後は評価減）")],
     "tax": "小規模宅地等の特例で自宅土地が80%減＝8,000万→1,600万円。課税遺産は1億→3,600万円相当に圧縮。基礎控除3,600万円とほぼ相殺し相続税ほぼゼロ。",
     "point": "同居親族が自宅を相続し申告期限まで居住継続すれば特例適用。評価減効果は数千万円規模。"},
    {"id": 14, "title": "生前贈与の活用・遺産1.5億円", "family": "父（被相続人）／子2人・孫4人（生前に暦年贈与を実施）",
     "estate": "贈与前1.5億円→10年で6,600万円贈与済み",
     "shares": [("子・孫", "—", "生前に分散済み")],
     "tax": "子2人・孫4人に毎年110万円×10年＝6,600万円を非課税移転。相続財産が8,400万円に圧縮され、相続税が大幅減。",
     "point": "暦年贈与は2024年改正で7年持戻し。孫（相続人でない）への贈与は持戻し対象外で特に有効。早期着手が鍵。"},
    {"id": 15, "title": "国際相続・海外資産あり・遺産2億円", "family": "父（被相続人・日本居住）／海外在住の長男／国内の次男",
     "estate": "国内1.5億円・海外不動産5,000万円",
     "shares": [("長男（海外）", "1/2", "1億円")," ", ("次男（国内）", "1/2", "1億円")],
     "tax": "全世界財産が課税対象（10年ルール）。海外不動産も日本の相続税対象。海外で課税されれば外国税額控除で調整。",
     "point": "海外在住の長男は印鑑証明が取れずサイン証明が必要。海外不動産は現地のプロベイト手続きも。専門家連携が必須。"},
    {"id": 16, "title": "再婚家庭・先妻の子と後妻・遺産1億円", "family": "父（被相続人）／後妻／先妻との子1人／後妻との子1人",
     "estate": "1億円",
     "shares": [("後妻", "1/2", "5,000万円"), ("先妻の子", "1/4", "2,500万円"), ("後妻の子", "1/4", "2,500万円")],
     "tax": "基礎控除4,800万円。課税遺産5,200万円。先妻の子も後妻の子も同じ相続分。",
     "point": "先妻の子と後妻は感情的に対立しやすい。遺言書で配分を明確にし、付言事項で意図を伝えることがトラブル予防に。"},
    {"id": 17, "title": "未成年の相続人がいる・遺産7,000万円", "family": "母（被相続人）／父（親権者）／未成年の子",
     "estate": "7,000万円",
     "shares": [("父", "1/2", "3,500万円"), ("未成年の子", "1/2", "3,500万円")],
     "tax": "基礎控除4,200万円。課税遺産2,800万円。配偶者控除で父の分は非課税。",
     "point": "親権者の父と未成年の子が共に相続人だと利益相反。家庭裁判所で特別代理人の選任が必要（民法826条）。"},
    {"id": 18, "title": "認知症の相続人がいる・遺産9,000万円", "family": "父（被相続人）／認知症の妻／子2人",
     "estate": "9,000万円",
     "shares": [("妻（認知症）", "1/2", "4,500万円"), ("子A", "1/4", "2,250万円"), ("子B", "1/4", "2,250万円")],
     "tax": "基礎控除4,800万円。課税遺産4,200万円。配偶者控除で妻分非課税。",
     "point": "認知症の妻は遺産分割協議ができないため、成年後見人の選任が必要。後見人は妻の法定相続分を確保する義務があり、二次相続対策の柔軟な配分が難しくなる。生前の対策が重要。"},
    {"id": 19, "title": "おひとりさま・相続人不存在・遺産5,000万円", "family": "本人（被相続人・配偶者/子/親/兄弟すべてなし）",
     "estate": "5,000万円",
     "shares": [("法定相続人なし", "—", "特別縁故者・国庫へ")],
     "tax": "相続人不存在。相続財産管理人を選任し、特別縁故者がいればその者へ、いなければ最終的に国庫帰属。",
     "point": "おひとりさまは遺言書がないと財産が国庫に。お世話になった人・団体へ遺贈したいなら遺言書が絶対必要。"},
    {"id": 20, "title": "遺留分侵害・全部を1人に・遺産1.2億円", "family": "父（被相続人）／長男（全部相続の遺言）／次男（遺留分請求）",
     "estate": "1.2億円",
     "shares": [("長男（遺言）", "全部", "1.2億円"), ("次男（遺留分）", "1/4", "3,000万円を請求可")],
     "tax": "遺言で長男に全部相続させても、次男は遺留分（法定相続分1/2の半分＝1/4）として3,000万円を金銭請求できる。",
     "point": "「長男に全部」の遺言でも次男の遺留分は侵害できない。遺留分侵害額請求（民法1046条）は金銭請求。時効1年に注意。"},
]


def render_case_index():
    cards = "\n".join(
        f'<a class="case-card" href="#case-{c["id"]}">'
        f'<span class="case-num">CASE {c["id"]}</span>'
        f'<h3>{c["title"]}</h3></a>'
        for c in CASE_STUDIES
    )
    details = "\n".join(_render_case_block(c) for c in CASE_STUDIES)

    # ItemList JSON-LD
    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "name": "相続ケーススタディ集",
        "itemListElement": [
            {"@type": "ListItem", "position": c["id"], "name": c["title"]}
            for c in CASE_STUDIES
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "家系図Navi", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "相続ケーススタディ集", "item": SITE_URL + "/cases/"},
        ],
    }
    desc_text = f"配偶者と子・子のみ・事業承継・二次相続・国際相続・再婚家庭・おひとりさまなど、相続の典型ケース{len(CASE_STUDIES)}例を家族構成・相続分・相続税・対策ポイントで具体的に解説。"
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>相続ケーススタディ集（{len(CASE_STUDIES)}例）｜家系図Navi</title>
  <meta name="description" content="{desc_text}">
  <meta name="keywords" content="相続,ケーススタディ,事例,家族構成,相続分,相続税,二次相続,事業承継">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{CANONICAL_BASE}/cases/">
  <meta property="og:title" content="相続ケーススタディ集（{len(CASE_STUDIES)}例）｜家系図Navi">
  <meta property="og:description" content="{desc_text}">
  <meta property="og:url" content="{SITE_URL}/cases/">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{ICON}">
  <script type="application/ld+json">{json.dumps(itemlist, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script>
  <link rel="icon" href="../icon_192.png">
  <style>
    :root {{ --green: #27AE60; --light-bg: #f8fdf9; --text: #2c3e50; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: var(--light-bg); color: var(--text); line-height: 1.8; }}
    header {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 2.5rem 1.5rem; text-align: center; }}
    header h1 {{ font-size: 1.8rem; margin: .5rem 0; }}
    header .nav {{ font-size: .85rem; opacity: .9; }}
    header .nav a {{ color: white; text-decoration: none; }}
    main {{ max-width: 880px; margin: 0 auto; padding: 2rem 1.5rem; }}
    .case-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: .8rem; margin-bottom: 2.5rem; }}
    .case-card {{ background: white; border-radius: 10px; padding: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,.06); text-decoration: none; color: inherit; border-left: 3px solid var(--green); }}
    .case-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,.1); }}
    .case-num {{ font-size: .75rem; font-weight: 700; color: var(--green); }}
    .case-card h3 {{ font-size: .92rem; margin-top: .3rem; }}
    .case-block {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,.06); scroll-margin-top: 1rem; }}
    .case-block h2 {{ color: var(--green); font-size: 1.2rem; margin-bottom: .8rem; }}
    .case-block .meta {{ font-size: .9rem; color: #555; margin: .3rem 0; }}
    .case-block .meta b {{ color: var(--text); }}
    table {{ width: 100%; border-collapse: collapse; margin: .8rem 0; }}
    th {{ background: var(--green); color: white; padding: .45rem; font-size: .85rem; }}
    td {{ padding: .45rem; border-bottom: 1px solid #eee; font-size: .88rem; text-align: center; }}
    .point {{ background: var(--light-bg); border-left: 4px solid var(--green); padding: .8rem 1rem; border-radius: 4px; margin-top: .8rem; font-size: .9rem; }}
    .cta-box {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 1.6rem; border-radius: 12px; text-align: center; margin: 2.5rem 0; }}
    .cta-box a {{ display: inline-block; padding: .7rem 2rem; background: white; color: var(--green); font-weight: 700; border-radius: 50px; text-decoration: none; margin-top: .5rem; }}
    .disclaimer {{ background: #fff8e1; border-left: 4px solid #f39c12; padding: 1rem 1.2rem; border-radius: 4px; font-size: .85rem; margin: 1.5rem 0; }}
    footer {{ text-align: center; padding: 2rem; font-size: .85rem; color: #888; border-top: 1px solid #eee; }}
    footer a {{ color: var(--green); text-decoration: none; }}
  </style>
</head>
<body>
<header>
  <div class="nav"><a href="../">🌳 家系図Navi</a> ＞ ケーススタディ集</div>
  <h1>相続ケーススタディ集</h1>
  <p style="opacity:.95;margin-top:.5rem;font-size:.95rem;">{len(CASE_STUDIES)}の典型例で「うちはどのケース？」がわかる</p>
</header>
<main>
  <p>配偶者と子の標準ケースから、事業承継・二次相続・国際相続・再婚家庭・おひとりさままで、相続の典型例を{len(CASE_STUDIES)}パターン集めました。気になるケースをタップしてください。</p>

  <div class="case-grid">
  {cards}
  </div>

  {details}

  <div class="cta-box">
    <h3 style="margin-bottom:.5rem;">あなたのケースを正確にシミュレーション</h3>
    <p style="font-size:.95rem;opacity:.95;">家族構成を入力するだけで、あなたの家の相続分・相続税・遺留分を自動計算。</p>
    <a href="{APP_URL}" rel="noopener">家系図Naviを試す（無料）→</a>
  </div>

  {ad_block()}

  <div class="disclaimer">
    <strong>⚠️ 免責事項：</strong>各ケースの税額は一般的な前提による概算であり、実際は適用特例・分割割合等で変動します。個別事案は専門家にご相談ください。
  </div>
</main>
<footer>
  <p>© 2026 Mirai Navi — <a href="../">家系図Navi</a> ｜ <a href="../guides/">記事一覧</a> ｜ <a href="../calculator/">計算ツール</a></p>
  <p style="margin-top:.5rem;font-size:.82rem;">🔗 姉妹サイト：<a href="https://mirainavi.net/?utm_source=note&utm_medium=article&utm_campaign=brand-story&utm_content=cta_text_bottom" target="_blank" rel="noopener" style="color:#16A085;">ミライNavi</a> ｜ <a href="https://teso-navi.vercel.app/" target="_blank" rel="noopener" style="color:#16A085;">手相ナビ</a> ｜ <a href="https://kakeizu-souzoku-navi.blog.jp/" target="_blank" rel="noopener" style="color:#16A085;">運営ブログ</a></p>
  <p style="margin-top:.5rem;font-size:.78rem;color:#999;">当サイトはアフィリエイト広告（プロモーション）を利用しています。｜<a href="https://yadianqiteng5-spec.github.io/kakeizu-navi-lp/about/" style="color:#16A085;">運営者情報・プライバシー</a></p>
</footer>
</body>
</html>
"""


def _render_case_block(c):
    rows = ""
    for item in c["shares"]:
        if isinstance(item, tuple) and len(item) == 3:
            rows += f'<tr><td>{item[0]}</td><td>{item[1]}</td><td>{item[2]}</td></tr>'
    table = ""
    if rows:
        table = f'<table><thead><tr><th>相続人</th><th>法定相続分</th><th>取得額の目安</th></tr></thead><tbody>{rows}</tbody></table>'
    return f"""<div class="case-block" id="case-{c['id']}">
    <h2>CASE {c['id']}：{c['title']}</h2>
    <p class="meta"><b>👪 家族構成：</b>{c['family']}</p>
    <p class="meta"><b>💰 遺産：</b>{c['estate']}</p>
    {table}
    <p class="meta"><b>🧮 相続税：</b>{c['tax']}</p>
    <div class="point"><b>💡 ポイント：</b>{c['point']}</div>
  </div>"""


def render_calculator():
    url = SITE_URL + "/calculator/"
    webapp_jsonld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "相続税かんたん計算ツール",
        "description": "遺産総額と家族構成を入力するだけで相続税の概算・基礎控除・法定相続分をその場で計算できる無料ツール。",
        "url": url,
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "Web",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        "inLanguage": "ja",
    }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "家系図Navi", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "相続税かんたん計算ツール", "item": url},
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>相続税かんたん計算ツール（無料）｜家系図Navi</title>
  <meta name="description" content="遺産総額と家族構成を入力するだけで相続税の概算・基礎控除・法定相続分をその場で自動計算。国税庁速算表準拠。登録不要・完全無料・データ保存なし。">
  <meta name="keywords" content="相続税,計算ツール,シミュレーター,基礎控除,法定相続分,無料,自動計算">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url.replace(SITE_URL, CANONICAL_BASE)}">
  <meta property="og:title" content="相続税かんたん計算ツール（無料）｜家系図Navi">
  <meta property="og:description" content="遺産総額と家族構成を入力するだけで相続税の概算をその場で自動計算。国税庁速算表準拠。">
  <meta property="og:url" content="{url}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{ICON}">
  <script type="application/ld+json">{json.dumps(webapp_jsonld, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script>
  <link rel="icon" href="../icon_192.png">
  <style>
    :root {{ --green: #27AE60; --light-bg: #f8fdf9; --text: #2c3e50; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: var(--light-bg); color: var(--text); line-height: 1.7; }}
    header {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 2.5rem 1.5rem; text-align: center; }}
    header h1 {{ font-size: 1.8rem; margin: .5rem 0; }}
    header .nav {{ font-size: .85rem; opacity: .9; }}
    header .nav a {{ color: white; text-decoration: none; }}
    main {{ max-width: 720px; margin: 0 auto; padding: 2rem 1.5rem; }}
    .calc {{ background: white; border-radius: 12px; padding: 1.8rem; box-shadow: 0 2px 12px rgba(0,0,0,.08); }}
    .field {{ margin-bottom: 1.3rem; }}
    .field label {{ display: block; font-weight: 600; margin-bottom: .4rem; font-size: .95rem; }}
    .field input, .field select {{ width: 100%; padding: .7rem; border: 2px solid #ddd; border-radius: 8px; font-size: 1rem; }}
    .field input:focus, .field select:focus {{ outline: none; border-color: var(--green); }}
    .row {{ display: flex; gap: 1rem; }}
    .row .field {{ flex: 1; }}
    .result {{ margin-top: 1.5rem; padding: 1.5rem; background: var(--light-bg); border-radius: 10px; border: 2px solid var(--green); display: none; }}
    .result.show {{ display: block; }}
    .result h3 {{ color: var(--green); margin-bottom: .8rem; }}
    .result-row {{ display: flex; justify-content: space-between; padding: .5rem 0; border-bottom: 1px dashed #ccc; }}
    .result-row.total {{ font-size: 1.2rem; font-weight: 800; color: var(--green); border-bottom: none; margin-top: .5rem; }}
    .calc-btn {{ width: 100%; padding: .9rem; background: var(--green); color: white; border: none; border-radius: 50px; font-size: 1.1rem; font-weight: 700; cursor: pointer; }}
    .calc-btn:hover {{ background: #16A085; }}
    .note {{ font-size: .82rem; color: #888; margin-top: 1rem; }}
    .cta-box {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 1.6rem; border-radius: 12px; text-align: center; margin: 2rem 0; }}
    .cta-box a {{ display: inline-block; padding: .7rem 2rem; background: white; color: var(--green); font-weight: 700; border-radius: 50px; text-decoration: none; margin-top: .5rem; }}
    footer {{ text-align: center; padding: 2rem; font-size: .85rem; color: #888; border-top: 1px solid #eee; margin-top: 2rem; }}
    footer a {{ color: var(--green); text-decoration: none; }}
    .disclaimer {{ background: #fff8e1; border-left: 4px solid #f39c12; padding: 1rem 1.2rem; border-radius: 4px; font-size: .85rem; margin: 1.5rem 0; }}
  </style>
</head>
<body>
<header>
  <div class="nav"><a href="../">🌳 家系図Navi</a> ＞ 相続税かんたん計算ツール</div>
  <h1>相続税かんたん計算ツール</h1>
  <p style="opacity:.95;margin-top:.5rem;font-size:.95rem;">遺産額と家族構成を入力するだけ・登録不要・完全無料</p>
</header>
<main>
  <div class="calc">
    <div class="field">
      <label for="estate">遺産総額（万円）</label>
      <input type="number" id="estate" placeholder="例: 10000" min="0" step="100">
    </div>
    <div class="row">
      <div class="field">
        <label for="spouse">配偶者</label>
        <select id="spouse"><option value="1">いる</option><option value="0">いない</option></select>
      </div>
      <div class="field">
        <label for="heir-type">他の相続人</label>
        <select id="heir-type">
          <option value="child">子</option>
          <option value="parent">直系尊属（親）</option>
          <option value="sibling">兄弟姉妹</option>
          <option value="none">なし（配偶者のみ）</option>
        </select>
      </div>
      <div class="field">
        <label for="heir-count">人数</label>
        <input type="number" id="heir-count" value="2" min="0" max="10">
      </div>
    </div>
    <button class="calc-btn" onclick="calcInheritance()">計算する</button>

    <div class="result" id="result">
      <h3>📊 計算結果（概算）</h3>
      <div class="result-row"><span>法定相続人の数</span><span id="r-heirs">-</span></div>
      <div class="result-row"><span>基礎控除額</span><span id="r-deduction">-</span></div>
      <div class="result-row"><span>課税遺産総額</span><span id="r-taxable">-</span></div>
      <div class="result-row total"><span>相続税の総額（概算）</span><span id="r-tax">-</span></div>
      <div id="r-spouse-note" style="margin-top:.8rem;font-size:.85rem;color:#27AE60;"></div>
    </div>

    <div class="disclaimer">
      ⚠️ 本ツールは<strong>概算の目安</strong>です。配偶者の税額軽減（最大1.6億円非課税）・小規模宅地等の特例・各種控除は反映していません。正確な試算は<a href="{APP_URL}">家系図Navi本体</a>または税理士にご確認ください。
    </div>
  </div>

  <div class="cta-box">
    <h3 style="margin-bottom:.5rem;">より正確なシミュレーションは家系図Naviで</h3>
    <p style="font-size:.95rem;opacity:.95;">配偶者控除・小規模宅地・二次相続まで含めた精密な試算が無料でできます。</p>
    <a href="{APP_URL}" rel="noopener">家系図Naviを開く →</a>
  </div>

  {ad_block()}

  <p style="font-size:.9rem;color:#666;">
    関連：<a href="../table-inheritance-tax/" style="color:var(--green);">相続税早見表</a> ｜
    <a href="../table-basic-deduction/" style="color:var(--green);">基礎控除早見表</a> ｜
    <a href="../inheritance-tax/" style="color:var(--green);">相続税の基礎控除と計算</a>
  </p>
</main>
<footer>
  <p>© 2026 Mirai Navi — <a href="../">家系図Navi</a> ｜ <a href="../guides/">記事一覧</a></p>
  <p style="margin-top:.5rem;font-size:.82rem;">🔗 姉妹サイト：<a href="https://mirainavi.net/?utm_source=note&utm_medium=article&utm_campaign=brand-story&utm_content=cta_text_bottom" target="_blank" rel="noopener" style="color:#16A085;">ミライNavi</a> ｜ <a href="https://teso-navi.vercel.app/" target="_blank" rel="noopener" style="color:#16A085;">手相ナビ</a> ｜ <a href="https://kakeizu-souzoku-navi.blog.jp/" target="_blank" rel="noopener" style="color:#16A085;">運営ブログ</a></p>
  <p style="margin-top:.5rem;font-size:.78rem;color:#999;">当サイトはアフィリエイト広告（プロモーション）を利用しています。｜<a href="https://yadianqiteng5-spec.github.io/kakeizu-navi-lp/about/" style="color:#16A085;">運営者情報・プライバシー</a></p>
</footer>

<script>
// 国税庁・相続税速算表（取得金額上限, 税率, 控除額） 単位:円
const BRACKETS = [
  [10000000, 0.10, 0],
  [30000000, 0.15, 500000],
  [50000000, 0.20, 2000000],
  [100000000, 0.30, 7000000],
  [200000000, 0.40, 17000000],
  [300000000, 0.45, 27000000],
  [600000000, 0.50, 42000000],
  [Infinity, 0.55, 72000000],
];

function taxPerPerson(amount) {{
  if (amount <= 0) return 0;
  for (const [cap, rate, deduction] of BRACKETS) {{
    if (amount <= cap) return amount * rate - deduction;
  }}
  return 0;
}}

function yen(n) {{
  return Math.round(n).toLocaleString('ja-JP') + '円';
}}

function calcInheritance() {{
  const estate = (parseFloat(document.getElementById('estate').value) || 0) * 10000;
  const hasSpouse = document.getElementById('spouse').value === '1';
  const heirType = document.getElementById('heir-type').value;
  let heirCount = parseInt(document.getElementById('heir-count').value) || 0;

  if (heirType === 'none') heirCount = 0;

  // 法定相続人数
  const numHeirs = (hasSpouse ? 1 : 0) + heirCount;
  if (numHeirs === 0) {{ alert('相続人がいません。配偶者または他の相続人を入力してください。'); return; }}

  // 基礎控除
  const deduction = 30000000 + 6000000 * numHeirs;
  const taxable = Math.max(0, estate - deduction);

  // 法定相続分の比率を決定
  let spouseShare = 0, otherTotalShare = 0;
  if (hasSpouse && heirCount > 0) {{
    if (heirType === 'child')   {{ spouseShare = 1/2; otherTotalShare = 1/2; }}
    if (heirType === 'parent')  {{ spouseShare = 2/3; otherTotalShare = 1/3; }}
    if (heirType === 'sibling') {{ spouseShare = 3/4; otherTotalShare = 1/4; }}
  }} else if (hasSpouse) {{
    spouseShare = 1; otherTotalShare = 0;
  }} else {{
    spouseShare = 0; otherTotalShare = 1;
  }}

  // 各人の法定相続分で課税遺産を按分 → 速算表 → 合算（相続税法16条）
  let totalTax = 0;
  if (hasSpouse) totalTax += taxPerPerson(taxable * spouseShare);
  if (heirCount > 0) {{
    const each = taxable * otherTotalShare / heirCount;
    totalTax += taxPerPerson(each) * heirCount;
  }}

  document.getElementById('r-heirs').textContent = numHeirs + '人';
  document.getElementById('r-deduction').textContent = yen(deduction);
  document.getElementById('r-taxable').textContent = yen(taxable);
  document.getElementById('r-tax').textContent = yen(totalTax);

  const note = document.getElementById('r-spouse-note');
  if (hasSpouse && totalTax > 0) {{
    note.innerHTML = '💡 配偶者の税額軽減（最大1.6億円非課税）を適用すると、実際の納税額はさらに下がる可能性があります。';
  }} else if (taxable === 0) {{
    note.innerHTML = '✅ 基礎控除内のため、相続税はかかりません。';
  }} else {{
    note.innerHTML = '';
  }}

  document.getElementById('result').classList.add('show');
}}
</script>
</body>
</html>
"""


def render_about():
    org_jsonld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "家系図Navi",
        "alternateName": "Mirai Navi",
        "url": SITE_URL + "/",
        "logo": ICON,
        "description": "民法・相続税法に準拠した相続シミュレーターと、専門家監修水準の解説記事を提供する独立系サービス。",
        "founder": {"@type": "Person", "name": "Mirai Navi"},
        "foundingDate": "2026-04",
        "areaServed": "JP",
        "knowsAbout": ["相続", "事業承継", "相続税", "遺言書", "家族信託", "事業承継税制"],
        "sameAs": [
            "https://mirainavi.net/",
            "https://teso-navi.vercel.app/",
            "https://kakeizu-souzoku-navi.blog.jp/",
            APP_URL,
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>家系図Naviについて｜運営方針と編集ポリシー</title>
  <meta name="description" content="家系図Naviの運営者情報・編集ポリシー・計算精度の検証方法・プライバシー設計を公開。民法・相続税法準拠を国税庁公表値で厳密検証。">
  <meta name="keywords" content="家系図Navi,運営者,編集ポリシー,Mirai Navi,相続,計算精度">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{CANONICAL_BASE}/about/">
  <meta property="og:title" content="家系図Naviについて｜運営方針と編集ポリシー">
  <meta property="og:description" content="運営者情報・編集ポリシー・計算精度の検証方法・プライバシー設計。">
  <meta property="og:url" content="{SITE_URL}/about/">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{ICON}">
  <script type="application/ld+json">{json.dumps(org_jsonld, ensure_ascii=False)}</script>
  <link rel="icon" href="../icon_192.png">
  <style>
    :root {{ --green: #27AE60; --light-bg: #f8fdf9; --text: #2c3e50; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', sans-serif; background: var(--light-bg); color: var(--text); line-height: 1.8; }}
    header {{ background: linear-gradient(135deg, var(--green), #16A085); color: white; padding: 2.5rem 1.5rem; text-align: center; }}
    header h1 {{ font-size: 1.8rem; margin: .5rem 0; }}
    header .nav {{ font-size: .9rem; opacity: .9; }}
    header .nav a {{ color: white; text-decoration: none; }}
    main {{ max-width: 820px; margin: 0 auto; padding: 2.5rem 1.5rem; }}
    h2 {{ font-size: 1.3rem; color: var(--green); margin: 2rem 0 1rem; border-left: 4px solid var(--green); padding-left: .8rem; }}
    .card {{ background: white; padding: 1.5rem; border-radius: 12px; margin: 1.2rem 0; box-shadow: 0 2px 8px rgba(0,0,0,.06); }}
    .card h3 {{ color: var(--green); margin-bottom: .6rem; }}
    footer {{ text-align: center; padding: 2rem; font-size: .85rem; color: #888; border-top: 1px solid #eee; margin-top: 3rem; }}
    footer a {{ color: var(--green); text-decoration: none; }}
  </style>
</head>
<body>
<header>
  <div class="nav"><a href="../">🌳 家系図Navi</a> ＞ About</div>
  <h1>家系図Naviについて</h1>
  <p style="opacity:.95;margin-top:.6rem;">運営方針・編集ポリシー・計算精度・プライバシー設計</p>
</header>
<main>

  <h2>サービスの目的</h2>
  <p>家系図Naviは、相続・事業承継の<strong>事前検討フェーズ</strong>を支援するシミュレーターです。専門家への相談前に「概算を把握する」「論点を整理する」ことを助け、専門家のお仕事を補完・促進するツールを目指しています。</p>

  <h2>計算精度の検証</h2>
  <div class="card">
    <h3>✅ 民法・相続税法準拠</h3>
    <p>法定相続分・遺留分は民法900〜1042条に、相続税概算は相続税法15〜19条に準拠。代襲・半血兄弟・特別養子・養子算入制限・配偶者控除など実務上の論点を網羅。</p>
  </div>
  <div class="card">
    <h3>✅ 国税庁公表値と厳密一致</h3>
    <p>相続税の計算は<strong>国税庁の速算表8段階</strong>を用い、複数の標準ケース（1億円→630万円、2億円→2,700万円、5億円→1億1,924万円）で国税庁シミュレーターと一致を確認済み。</p>
  </div>
  <div class="card">
    <h3>✅ 自動テスト 39ケース全通過</h3>
    <p>代襲相続・半血兄弟・同時死亡・特別養子・養子算入制限など39の法律ケースを単体テストで検証。GitHub Actions で push 毎・月次 cron で自動再検証。</p>
  </div>

  <h2>編集ポリシー</h2>
  <ul>
    <li>記事は<strong>民法・相続税法の条文</strong>と<strong>国税庁の公式情報</strong>を一次ソースとする</li>
    <li>判例引用は最高裁判例または確立した実務運用に限る</li>
    <li>「〜と考えられます」「〜の可能性があります」など推定表現を使い、断定を避ける</li>
    <li>個別事案の法的助言は行わず、必ず専門家相談を促す</li>
    <li>弁護士法72条（非弁活動の禁止）に抵触しない設計</li>
    <li>法改正があれば速やかに反映（2024年改正対応済み：相続登記義務化・7年持戻し）</li>
  </ul>

  <h2>プライバシーポリシー（個人情報の取扱い）</h2>
  <h3>診断ツールの入力情報（ゼロ・リテンション設計）</h3>
  <ul>
    <li>入力された個人情報（家族構成・資産・音声）は<strong>サーバーに一切保存されません</strong></li>
    <li>データはブラウザのセッション内のみで処理</li>
    <li>AI 解析結果はモデル学習に利用されない設定で運用</li>
    <li>アップロード画像・音声はオンメモリ処理</li>
  </ul>
  <h3>Cookie・アクセス解析・広告（アフィリエイト）</h3>
  <ul>
    <li>当サイトは利便性向上・アクセス解析・広告効果測定のため Cookie 等を利用し、アクセス解析（例：Google Analytics）やアフィリエイト・サービス・プロバイダー（ASP）／広告ネットワークと連携することがあります。</li>
    <li>これらは Cookie・広告識別子・閲覧履歴等（個人関連情報を含む）を取得することがあります。第三者へ提供し提供先で個人データとして取得されることが想定される場合、提供先が本人同意を取得していること等を確認します（個人情報保護法第31条）。</li>
    <li>ブラウザ設定で Cookie を拒否・削除できます。オプトアウト：<a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">Google 広告</a> ／ <a href="https://tools.google.com/dlpage/gaoptout?hl=ja" target="_blank" rel="noopener">Google Analytics</a></li>
  </ul>
  <h3>お問い合わせで取得する情報・利用目的</h3>
  <ul>
    <li>お問い合わせ時にいただく氏名・メールアドレス・内容は、回答・連絡およびこれに付随する対応の目的にのみ利用します（個人情報保護法第17条）。</li>
    <li>法令に基づく場合等を除き、ご本人の同意なく第三者へ提供しません（同法第27条）。海外サービスへの移転がある場合は同法第28条に従います。</li>
  </ul>
  <h3>開示請求・お問い合わせ窓口</h3>
  <ul>
    <li>保有個人データの利用目的の通知・開示・訂正・利用停止等を求めることができます（同法第32〜35条）。</li>
    <li>個人情報に関するお問い合わせ窓口：Mirai Navi　support@mirainavi.net</li>
  </ul>
  <p style="font-size:.85rem;color:#666;">※本記載は公開前の暫定版です。運営者名・連絡先は確定後に反映します。詳細な全文ポリシーは別途整備予定。</p>

  <h2>運営者</h2>
  <div class="card">
    <h3>Mirai Navi</h3>
    <p>○○Navi シリーズの運営者。専門家のお仕事を補完する独立系シミュレーターを開発。</p>
    <p style="margin-top:.4rem;">運営者名／屋号：Mirai Navi　｜　お問い合わせ：support@mirainavi.net（所在地はお求めに応じて遅滞なく開示します）</p>
    <p style="margin-top:.6rem;font-size:.9rem;color:#666;">本サービスは弁護士・税理士事務所ではなく、特定事案の法律事務・税務代理は行いません。個別事案は必ず専門家にご相談ください。当サイトはアフィリエイト広告を利用しています。</p>
  </div>

  <h2>免責事項</h2>
  <p>本サービスの計算結果・記事内容は一般的な情報提供であり、法的・税務的助言ではありません。具体的な判断・手続きは弁護士・税理士・司法書士等の専門家にご相談ください。</p>

</main>
<footer>
  <p>© 2026 Mirai Navi — <a href="../">家系図Navi / Family Tree Guide</a></p>
  <p style="margin-top:.5rem;font-size:.82rem;">🔗 姉妹サイト：<a href="https://mirainavi.net/?utm_source=note&utm_medium=article&utm_campaign=brand-story&utm_content=cta_text_bottom" target="_blank" rel="noopener" style="color:#16A085;">ミライNavi</a> ｜ <a href="https://teso-navi.vercel.app/" target="_blank" rel="noopener" style="color:#16A085;">手相ナビ</a> ｜ <a href="https://kakeizu-souzoku-navi.blog.jp/" target="_blank" rel="noopener" style="color:#16A085;">運営ブログ</a></p>
  <p style="margin-top:.5rem;font-size:.78rem;color:#999;">当サイトはアフィリエイト広告（プロモーション）を利用しています。｜<a href="https://yadianqiteng5-spec.github.io/kakeizu-navi-lp/about/" style="color:#16A085;">運営者情報・プライバシー</a></p>
</footer>
</body>
</html>
"""


def render_rss():
    """記事一覧のRSS 2.0フィードを生成（インデックス促進・購読対応）。"""
    import html as _html
    items = ""
    for a in ARTICLES:
        link = f"{SITE_URL}/{a['slug']}/"
        items += (
            "  <item>\n"
            f"    <title>{_html.escape(a['title'])}</title>\n"
            f"    <link>{link}</link>\n"
            f"    <guid>{link}</guid>\n"
            f"    <description>{_html.escape(a['desc'])}</description>\n"
            "    <pubDate>Sat, 30 May 2026 00:00:00 +0900</pubDate>\n"
            "  </item>\n"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>\n'
        "  <title>家系図Navi｜相続・事業承継ガイド</title>\n"
        f"  <link>{SITE_URL}/</link>\n"
        "  <description>相続税・法定相続分・遺留分・事業承継・遺言の解説記事</description>\n"
        "  <language>ja</language>\n"
        f"{items}"
        "</channel></rss>\n"
    )


def render_404():
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>ページが見つかりません｜家系図Navi</title>
  <meta name="robots" content="noindex">
  <style>
    body {{ font-family: sans-serif; background: #f8fdf9; color: #2c3e50; text-align: center; padding: 4rem 1rem; line-height: 1.7; }}
    h1 {{ color: #27AE60; font-size: 2rem; }}
    a {{ color: #27AE60; }}
  </style>
</head>
<body>
  <h1>404 - ページが見つかりません</h1>
  <p>お探しのページは移動または削除された可能性があります。</p>
  <p style="margin-top:2rem;"><a href="/kakeizu-navi-lp/">🌳 家系図Navi トップへ</a> ｜ <a href="/kakeizu-navi-lp/guides/">ガイド記事一覧へ</a></p>
</body>
</html>
"""


ARTICLES += [
    {
        "slug": "kakeizu-howto",
        "title": "家系図の作り方｜自分で戸籍をたどって作る全手順",
        "h1": "家系図の作り方と戸籍の集め方",
        "desc": "家系図を自分で作る手順を、戸籍の取り寄せから清書まで全工程で解説。必要な戸籍の種類、郵送請求のコツ、どこまで遡れるかの目安まで、初めての方にもわかるようにまとめました。",
        "keywords": "家系図 作り方,家系図 自分で,戸籍 集め方,先祖 調べる,除籍謄本,家系図 書き方",
        "lead": "<strong>家系図づくり</strong>の中心は「戸籍をさかのぼって集めること」です。特別な資格は不要で、必要書類と手数料をそろえれば、自分の手で進められます。本記事では戸籍集めから清書まで、全手順を初めての方向けに解説します。",
        "sections": [
            ("家系図づくりは「戸籍集め」が中心", "<p>家系図は古文書や言い伝えから始めるイメージがありますが、まず取り組むべきは戸籍です。戸籍には出生・婚姻・死亡・親子関係が法的根拠とともに記録され、客観的にさかのぼれます。自分の戸籍から親、祖父母へと順にたどることで、家系の幹を描いていけます。</p>"),
            ("自分で作る5ステップ", "<ol><li><strong>自分の戸籍を取る</strong>：本籍地の役所で戸籍謄本を取得し、親の本籍をたどる</li><li><strong>さかのぼって古い戸籍を集める</strong>：除籍謄本・改製原戸籍を順に取り寄せる</li><li><strong>情報を書き出す</strong>：人物・続柄・生没年を一覧に整理する</li><li><strong>家系図の形に並べる</strong>：世代ごとに線でつないでいく</li><li><strong>清書・保存する</strong>：紙、またはアプリ・ソフトでまとめて残す</li></ol>"),
            ("どこまでさかのぼれる？", "<p>戸籍制度は明治期に整備されたため、現存する戸籍では一般に<strong>江戸末期〜明治初期生まれの先祖</strong>まで確認できる場合が多いとされています。どこまで遡れるかは戸籍の保存状況により異なり、それより前は過去帳や古文書などの調査が必要になります。</p>"),
            ("つまずきやすいポイント", "<ul><li>古い戸籍（除籍・改製原戸籍）は手書き・旧字で読みにくいことがある</li><li>本籍地が遠方だと郵送請求になり、定額小為替や返信用封筒の準備が必要</li><li>転籍を繰り返している場合、複数の役所への請求が必要になる</li></ul><p>2024年から始まった戸籍の広域交付を使うと、一部の戸籍は本籍地以外の窓口でもまとめて取得しやすくなりました。</p>"),
        ],
        "faqs": [
            ("家系図づくりに資格や許可は必要ですか？", "不要です。自分や直系の親族の戸籍は、必要書類と手数料をそろえれば本人が取得できます。"),
            ("どのくらいの期間・費用がかかりますか？", "ケースにより異なりますが、戸籍の取り寄せは郵送だと往復で数週間かかることがあり、戸籍1通あたり数百円程度の手数料がかかります。"),
            ("自分で作るのが難しい場合は？", "古い戸籍の解読や遠方の役所への請求が負担な場合は、戸籍取得や家系図作成を代行するサービスを利用する方法もあります。"),
        ],
    },
    {
        "slug": "koseki-wide-area",
        "title": "戸籍の広域交付とは？2024年開始の制度と家系図づくりでの使い方",
        "h1": "戸籍の広域交付の仕組みと使い方",
        "desc": "2024年3月開始の戸籍広域交付で、本籍地以外の市区町村窓口でも戸籍をまとめて請求できるように。対象範囲・必要なもの・注意点（抄本や附票は対象外など）を家系図・相続の視点で解説します。",
        "keywords": "戸籍 広域交付,広域交付 必要書類,本籍地以外 戸籍,戸籍 まとめて取得,広域交付 注意点",
        "lead": "<strong>戸籍の広域交付</strong>は、2024年3月に始まった制度です。これまで本籍地でしか取れなかった戸籍を、最寄りの市区町村の窓口でまとめて請求できるようになり、家系図づくりや相続手続きの負担が軽くなりました。",
        "sections": [
            ("広域交付でできること", "<p>本籍地が遠方でも、お住まいの市区町村など最寄りの窓口で、戸籍謄本・除籍謄本・改製原戸籍をまとめて請求できます。複数の本籍地に分かれている戸籍も、一か所の窓口で取得しやすくなりました。</p>"),
            ("請求できる人・必要なもの", "<ul><li><strong>請求できる人</strong>：本人、配偶者、直系尊属（父母・祖父母）、直系卑属（子・孫）</li><li><strong>必要なもの</strong>：窓口で顔写真付きの本人確認書類（マイナンバーカード・運転免許証など）</li></ul><p>本人が窓口に出向いて請求するのが原則です。</p>"),
            ("対象外になるもの（注意点）", "<ul><li>戸籍<strong>抄本</strong>（個人事項証明）は対象外で、謄本（全部事項証明）が対象</li><li>戸籍の<strong>附票</strong>は広域交付の対象外</li><li><strong>郵送・代理人・オンライン</strong>での広域交付請求は不可（窓口で本人が請求）</li><li>コンピュータ化されていない一部の古い戸籍は対象外になることがある</li></ul>"),
            ("家系図づくりでの活かし方", "<p>家系図づくりでは、複数の役所に分かれた古い戸籍を集めるのが大きな手間でした。広域交付を使えば、直系の戸籍を最寄り窓口でまとめて取得しやすくなります。ただし抄本・附票が対象外な点や、兄弟姉妹など直系以外は範囲外な点に注意し、足りない分は従来どおり本籍地へ請求します。</p>"),
        ],
        "faqs": [
            ("広域交付はいつから始まりましたか？", "2024年3月1日に始まりました。戸籍法の改正による新しい制度です。"),
            ("郵送で広域交付を請求できますか？", "できません。広域交付は本人が窓口に出向いて請求する必要があり、郵送や代理人による請求は対象外です。"),
            ("兄弟姉妹の戸籍も広域交付で取れますか？", "取れません。広域交付で請求できるのは本人と直系（父母・祖父母・子・孫など）の戸籍に限られます。兄弟姉妹分は従来どおり本籍地などへの請求が必要です。"),
        ],
    },
]


ARTICLES += [
    {"slug":"koseki-removed","title":"除籍謄本・改製原戸籍の取り方｜郵送請求の手順と必要書類を解説","h1":"除籍謄本・改製原戸籍の取り方｜郵送請求の手順と必要書類を解説","desc":"除籍謄本や改製原戸籍を郵送で取り寄せる方法を、必要書類・手数料の払い方・記入のコツまで網羅的に解説。相続や家系図作成で過去の戸籍をたどりたい方に向けて、つまずきやすいポイントもわかりやすく整理しました。","keywords":"除籍謄本取り方,改製原戸籍郵送,戸籍郵送請求,相続戸籍収集,必要書類,定額小為替,本籍地役所","lead":"「親が亡くなって相続の手続きを始めたら、想像以上にたくさんの戸籍が必要だと言われた」「家系図を作りたくて先祖をたどりたいけれど、古い戸籍はどこでどう取ればいいのかわからない」——そんな戸惑いを感じている方は少なくないようです。特に除籍謄本や改製原戸籍は、ふだんの暮らしではほとんど触れる機会がないため、名前を聞いただけで身構えてしまうかもしれません。 しかし、手順そのものは決して複雑ではありません。本籍地のある役所に対して、必要書類をそろえて郵送で請求すれば、遠方に住んでいても自宅にいながら取り寄せることができます。この記事では、除籍謄本・改製原戸籍とは何かという基本から、郵送請求の具体的な流れ、つまずきやすいポイントまでを順を追って整理します。なお、運用の細部は自治体によって異なる場合があるため、最終的には請求先の役所の案内も必ず確認してください。","sections":[["除籍謄本・改製原戸籍とは何か","<p>まず言葉の整理からです。戸籍にはいくつかの種類があり、混同しやすいので押さえておきましょう。</p>\n<ul><li><strong>戸籍謄本（全部事項証明書）</strong>：現在使われている戸籍で、その戸籍に記載された全員の情報を写したもの。</li><li><strong>除籍謄本</strong>：結婚・死亡・転籍などにより、その戸籍に記載されていた全員が抜けて「閉じられた」戸籍。</li><li><strong>改製原戸籍（かいせいげんこせき／はらこせき）</strong>：法律の改正によって戸籍の様式が新しく作り替えられた際の、作り替え前の古い戸籍。</li></ul>\n<p>相続手続きでは、亡くなった方（被相続人）の「生まれてから亡くなるまで」の連続した戸籍が求められるのが一般的です。人は一生のうちに結婚や転籍などで戸籍が何度も変わるため、現在の戸籍だけでなく、過去にさかのぼって除籍謄本や改製原戸籍を集める必要が出てきます。家系図づくりでも、世代をさかのぼるほどこれらの古い戸籍が中心になります。</p>"],["郵送請求の前に確認しておきたいこと","<p>請求にとりかかる前に、いくつか確認しておくと手戻りが少なくなります。</p>\n<ul><li><strong>本籍地はどこか</strong>：戸籍は住所地ではなく「本籍地」の役所が管理しています。本籍地が今の住所と違うことはよくあるため、まずは本籍地を特定します。わからない場合は、本籍地記載ありの住民票を取得すると確認できるとされています。</li><li><strong>誰の、いつの戸籍が必要か</strong>：相続なら被相続人の出生までさかのぼる旨を、家系図なら「たどれるところまで」を請求書に書いておくと、役所側が判断しやすくなります。</li><li><strong>自分が請求できる立場か</strong>：戸籍は誰でも自由に取れるわけではなく、本人・配偶者・直系の親族などに請求が限られるのが一般的です。立場によっては、関係を示す書類が追加で必要になることがあります。</li></ul>\n<p>なお、近年は戸籍法の改正により、本籍地以外の市区町村の窓口でもまとめて請求できる「広域交付」と呼ばれる仕組みが設けられたとされています。ただし対象となる戸籍の種類や利用できる人には条件があるため、利用できるかどうかは事前に役所へ確認すると安心です。</p>"],["郵送請求に必要な書類","<p>郵送で請求する場合、一般的には次のものを封筒にそろえて送ります。自治体によって様式や名称が異なるため、あくまで代表的な構成として捉えてください。</p>\n<ul><li><strong>交付請求書</strong>：多くの役所がホームページで郵送用の請求書様式を公開しています。ダウンロードして記入するか、便箋に必要事項を書く方法を案内している自治体もあります。</li><li><strong>本人確認書類のコピー</strong>：運転免許証やマイナンバーカードなど、顔写真付きのものが求められることが一般的です。</li><li><strong>手数料分の定額小為替</strong>：郵送請求の手数料は、ゆうちょ銀行・郵便局で購入できる「定額小為替」で納めるのが一般的です。現金を直接送る方法は認められないことが多いため注意します。</li><li><strong>返信用封筒</strong>：自分の宛名を書き、切手を貼ったもの。戸籍は枚数が多くなることがあるため、料金不足にならないよう余裕をみておくとよいとされています。</li><li><strong>関係を示す書類</strong>：請求者が直系であることなどを示すため、戸籍の写しの提出を求められる場合があります。</li></ul>\n<p>手数料の金額は戸籍の種類ごとに法令で定められているのが一般的ですが、何通必要になるかは事前に読み切れないことが多いものです。定額小為替が不足すると手続きが止まってしまうため、少し多めに同封し、釣り銭が出る場合は返してもらう前提で準備する方法もよく案内されています。</p>"],["郵送請求の手順","<p>実際の流れを順番に見ていきましょう。</p>\n<p>1. <strong>本籍地の役所と請求先を確認する</strong>：市区町村のホームページで「戸籍 郵送請求」と探すと、担当窓口・様式・手数料・送付先が案内されていることが多いです。</p>\n<p>2. <strong>請求書に記入する</strong>：誰の戸籍を、何の目的で、どこまでさかのぼって必要かを具体的に書きます。「相続手続きのため、被相続人〇〇の出生から死亡までの戸籍すべて」のように書くと、役所が判断しやすくなります。</p>\n<p>3. <strong>必要書類をそろえる</strong>：本人確認書類のコピー、定額小為替、返信用封筒、関係書類などを封入します。</p>\n<p>4. <strong>郵送して到着を待つ</strong>：役所での処理や郵送の往復に日数がかかるため、時間に余裕をもって請求します。期限のある手続きでは特に早めの着手が安心です。</p>\n<p>5. <strong>届いた戸籍を確認し、不足があれば追加請求する</strong>：古い戸籍では「前の本籍地」が記載されています。そこからさらに前の戸籍を別の役所へ請求し、出生までさかのぼっていきます。</p>\n<p>このように、ひとつの役所で完結せず、本籍地を移動した分だけ複数の自治体にまたがって請求を重ねていくのが、過去の戸籍収集の特徴です。</p>"],["つまずきやすいポイントと対処","<p>最後に、よくある引っかかりどころを整理します。</p>\n<ul><li><strong>古い戸籍が手書き・旧字で読みにくい</strong>：明治・大正期の戸籍は手書きで、現代では使わない字体も多く見られます。読み取りに時間がかかることがあります。</li><li><strong>戦災や災害で戸籍が失われている場合がある</strong>：古い戸籍は、戦災などで一部が現存しないこともあるとされます。その場合は「廃棄・焼失」などの証明で代えることになるケースがあります。</li><li><strong>どこまでさかのぼれるか</strong>：戸籍には保存期間の定めがあり、際限なく古い記録が残っているわけではありません。たどれる範囲には限りがある点を、あらかじめ理解しておくとよいでしょう。</li><li><strong>手続きの負担が大きいと感じるとき</strong>：請求先が何か所にもなる、平日に動く時間が取りにくいといった場合、専門家に依頼するという選択肢もあります。依頼の可否や範囲は、扱う手続きの内容によって異なります。</li></ul>\n<p>戸籍をさかのぼる作業は、相続の必要に迫られて始める方が多い一方で、進めるうちに自分のルーツや家族の歩みに触れる時間にもなります。一度に完璧を目指さず、届いた戸籍を読み、次の本籍地へ——と一歩ずつ進めていくのが、結果的に確実な近道になりやすいといえるでしょう。</p>"]],"faqs":[["除籍謄本と改製原戸籍はどう違うのですか？","除籍謄本は記載者全員が抜けて閉じられた戸籍を指し、改製原戸籍は法改正で様式が作り替えられる前の古い戸籍を指すのが一般的です。どちらも過去をさかのぼる相続や家系図づくりで必要になることがあります。"],["郵送請求の手数料はどうやって支払うのですか？","ゆうちょ銀行・郵便局で購入できる「定額小為替」を同封して納める方法が一般的です。現金の直接送付は認められないことが多く、必要通数が読みにくいため、少し多めに用意して釣り銭を返してもらう案内もよく見られます。"],["戸籍はどこまでさかのぼって取れますか？","戸籍には保存期間の定めがあり、たどれる範囲には限りがあるとされます。また戦災などで一部が現存しない場合もあり、その際は廃棄・焼失の証明で代えることがあります。実際の可否は請求先の役所に確認すると確実です。"]]},
    {"slug":"how-far-back","title":"先祖はどこまで遡れる？戸籍・過去帳・古文書でたどるルーツ調査ロードマップ","h1":"先祖はどこまで遡れる？戸籍・過去帳・古文書でたどるルーツ調査ロードマップ","desc":"先祖はどこまで遡れるのか気になる方へ。戸籍から始め、過去帳・古文書へと段階的にルーツをたどる調査の流れと注意点を、初めての方にも分かるよう順を追って解説します。","keywords":"先祖どこまで遡れる,家系図作り方,戸籍取り寄せ,過去帳,古文書解読,ルーツ調査,除籍謄本","lead":"「自分の家のルーツは、いったいどこまでさかのぼれるのだろう」——親や祖父母の話を聞いているうちに、ふとそんな疑問がわいてくることがあります。法事で古い位牌を目にしたとき、あるいは相続で戸籍を集めたとき。きっかけはさまざまですが、いざ調べようとすると「何から手をつければいいのか分からない」と立ち止まってしまう方は少なくありません。 先祖調べには、おおまかに「戸籍」「過去帳」「古文書」という三つの段階があるとされます。手前の段階ほど入手しやすく確実で、奥へ進むほど専門性が増していきます。この記事では、その順序を一本のロードマップとして整理し、無理なく着実にさかのぼっていくための考え方を紹介します。","sections":[["まずは戸籍から始める理由","<p>ルーツ調査の出発点は、ほぼ例外なく戸籍です。理由はシンプルで、戸籍は公的に整備された記録であり、入手の手続きが明確で、内容の信頼性も高いとされるからです。いきなり古文書を探そうとするより、まず足元の確実な記録を固めるほうが結果的に近道になります。</p>\n<p>戸籍には現在の「戸籍謄本」のほかに、すでに人がいなくなった「除籍謄本」、古い様式の「改製原戸籍（はらこせき）」などがあります。これらをさかのぼって集めていくと、明治期に作られた古い戸籍までたどり着けることが一般にあるとされます。</p>\n<ul><li>自分の現在の戸籍から、親・祖父母へと一代ずつさかのぼる</li><li>本籍地の市区町村に請求し、取得できる最も古い戸籍まで集める</li><li>転籍があれば、その前の本籍地にも順に請求していく</li></ul>\n<p>戸籍は本人や直系の親族などが請求できるのが原則です。請求できる範囲や必要書類は制度で定められているため、各自治体の案内で最新の手続きを確認しておくと安心です。</p>"],["戸籍で「壁」に当たったら","<p>戸籍をさかのぼっていくと、多くの場合どこかで「これ以上は出てこない」という壁に当たります。日本の戸籍制度が整えられたのは明治初期とされ、それ以前の人物については戸籍という形では記録が残っていないのが一般的です。</p>\n<p>また、古い戸籍そのものが保存期間の経過や災害・戦災などで失われ、取得できないケースもあるとされます。「もっと古い戸籍があるはずなのに出てこない」と感じても、それは調べ方の問題ではなく、記録の限界であることが多いのです。</p>\n<p>この壁こそが、次の段階——過去帳や古文書——へ進むかどうかの分かれ道になります。戸籍で判明した最も古い先祖の名前・続柄・本籍地は、その先の調査の重要な手がかりになるため、丁寧に書き留めておきましょう。</p>"],["過去帳という次の手がかり","<p>戸籍より前の時代を知る手がかりとして、よく挙げられるのが「過去帳（かこちょう）」です。過去帳とは、亡くなった方の戒名や没年月日などを記した、お寺や各家庭で管理される記録のことを指します。</p>\n<p>過去帳には戸籍にはない情報が含まれていることがあり、江戸時代までさかのぼれる場合もあるとされます。ただし、その内容や残り方は寺院や家ごとに大きく異なり、必ず存在するとは限りません。</p>\n<ul><li>自宅の仏壇まわりに、家の過去帳が残っていないか確認する</li><li>菩提寺（先祖の墓や供養を任せてきたお寺）に過去帳がないか相談する</li><li>古い位牌や墓石に刻まれた戒名・没年も合わせて記録する</li></ul>\n<p>過去帳は個人情報を含む繊細な記録であり、近年は閲覧の取り扱いに配慮が求められる場面が増えているとされます。お寺に相談する際は、目的を丁寧に伝え、先方の判断や手続きを尊重する姿勢が大切です。あくまでお願いする立場であることを忘れないようにしましょう。</p>"],["古文書の世界へ進む","<p>過去帳でも足りない、さらに古い時代へさかのぼりたい——そうなると次は「古文書（こもんじょ）」の領域です。ここからは一気に専門性が高まり、調査のハードルも上がります。</p>\n<p>先祖調べに関わる古文書としては、江戸時代の「宗門人別改帳（しゅうもんにんべつあらためちょう）」や「検地帳」、村や家に伝わる古い文書などが挙げられることがあります。これらは地域の郷土資料館や図書館、文書館、あるいは旧家に保管されている場合があるとされます。</p>\n<p>ただし、古文書には大きく二つの壁があります。一つは「そもそも残っているか」、もう一つは「読めるか」です。</p>\n<ul><li>くずし字で書かれており、現代人には判読が難しいことが多い</li><li>保管場所が分散しており、どこにあるか特定しづらい</li><li>同姓同名や地名の変遷により、自分の先祖と断定するのが難しい</li></ul>\n<p>このため、古文書の段階では、郷土史の専門家や文書館の職員、あるいは家系調査の専門事業者などの力を借りることも一つの選択肢になります。自力にこだわりすぎず、適切に助けを求める判断も調査を前に進める鍵です。</p>"],["どこまで遡れるかは「家による」","<p>ここまで読んで、「結局どこまでさかのぼれるのか」を知りたい方が多いと思います。正直なところ、その答えは「家によって大きく異なる」というのが実情です。</p>\n<p>戸籍だけでも明治期までたどれることが一般にあるとされ、過去帳や古文書まで進めば、さらに古い時代の手がかりが得られる場合もあります。一方で、記録が早い段階で途切れ、それ以上はどうしても分からない家も珍しくありません。どちらが優れているという話ではなく、たまたま残った記録の量と運によるところが大きいのです。</p>\n<p>大切なのは、「○代前まで必ずさかのぼれる」と期待しすぎないことです。たどれるところまで丁寧にたどり、判明した事実を家系図や記録として残していく——その積み重ね自体に価値があると考えると、調査はぐっと続けやすくなります。</p>"],["無理なく進めるための心構え","<p>最後に、ルーツ調査を長く続けるためのポイントを整理します。先祖調べは一気に終わるものではなく、少しずつ手がかりをつなげていく作業です。</p>\n<ul><li>まずは戸籍という確実な土台から、順序を守って進める</li><li>集めた情報は、名前・続柄・年月日・出典をセットで記録する</li><li>高齢の親族から聞き取れる話は、早めにメモや録音で残しておく</li><li>分からない部分は「不明」として、無理に推測で埋めない</li><li>過去帳や古文書では、所有者・管理者への敬意を忘れない</li></ul>\n<p>事実と推測をきちんと分けて記録しておくことは、後から見返したときにも、家族に引き継ぐときにも大きな助けになります。あせらず、確かなところから一歩ずつ。それが、自分の家のルーツへ近づいていく最も確実な道のりだといえるでしょう。</p>"]],"faqs":[["戸籍だけで先祖はどこまで遡れますか？","家や記録の残り方によりますが、一般には明治期に作られた古い戸籍までさかのぼれる場合があるとされます。ただし保存期間の経過や災害などで取得できないこともあり、どこまで遡れるかは家ごとに異なります。"],["過去帳は誰でも見せてもらえますか？","過去帳はお寺や各家庭が管理する個人情報を含む記録で、必ず閲覧できるとは限りません。菩提寺に相談する場合は目的を丁寧に伝え、先方の判断や手続きを尊重する姿勢が大切とされています。"],["古文書は自分で読めなくても調査できますか？","くずし字などで判読が難しいことが多いため、郷土資料館や文書館の職員、家系調査の専門事業者などの力を借りる方法があります。自力にこだわらず助けを求めるのも有効な選択肢とされています。"]]},
]




# === 追加記事（自動生成） ===
ARTICLES += [
    {
        "slug": "inheritance-registration",
        "title": "相続登記の義務化（2024年4月施行）｜過料・期限・申請方法をわかりやすく解説",
        "h1": "相続登記の義務化とは？過料・期限・申請方法をやさしく解説",
        "desc": "2024年4月施行の相続登記義務化を、期限（3年以内）・10万円以下の過料・申請手順・相続人申告登記まで実務目線で解説。過去の相続も対象になる点や費用の目安、注意点も整理します。",
        "keywords": "相続登記 義務化,相続登記 期限,相続登記 過料,相続人申告登記,相続登記 申請方法,不動産登記法",
        "lead": "<strong>相続登記の義務化</strong>が2024年（令和6年）4月1日に施行され、不動産を相続した人は原則として相続を知った日から3年以内に登記の申請をする義務を負うことになりました。正当な理由なく怠ると過料の対象となる場合があり、過去に相続した不動産も対象です。本記事では期限・過料・申請方法をわかりやすく整理します。",
        "sections": [
            ("相続登記の義務化とは（2024年4月1日施行）", "<p>相続登記とは、不動産（土地・建物）の所有者が亡くなったときに、その不動産の名義を相続人へ変更する登記のことです。従来は申請するかどうかが相続人の任意に委ねられていましたが、<strong>所有者不明土地</strong>の増加が社会問題となったことを背景に、不動産登記法が改正され、<strong>2024年（令和6年）4月1日から相続登記が義務化</strong>されました（改正不動産登記法第76条の2）。</p>\n<p>ポイントは大きく次の3つです。</p>\n<ul>\n<li><strong>申請が義務になった</strong>：相続によって不動産を取得した相続人は、登記の申請をしなければなりません。</li>\n<li><strong>期限が定められた</strong>：相続の開始および所有権を取得したことを知った日から<strong>3年以内</strong>が原則です。</li>\n<li><strong>過去の相続もさかのぼって対象</strong>：施行日より前に発生した相続も義務の対象となります（後述の経過措置あり）。</li>\n</ul>\n<p>「親名義のまま何十年も放置している」「祖父名義の土地が残っている」といったケースも、今回の義務化の対象になり得る点に注意が必要です。</p>"),
            ("申請期限と「過料10万円」のルール", "<p>相続登記の申請期限は、原則として<strong>「相続の開始があったことを知り、かつ、その所有権を取得したことを知った日から3年以内」</strong>です。遺産分割協議によって不動産を取得した場合は、その<strong>分割が成立した日から3年以内</strong>に、内容に応じた登記を申請する必要があります。</p>\n<p>正当な理由がないのに期限内に申請を怠ったときは、<strong>10万円以下の過料</strong>に処せられる場合があるとされています（不動産登記法第164条）。「過料」は刑事罰である「罰金」とは異なる行政上の制裁ですが、金銭的な負担が生じ得る点では変わりません。</p>\n<p>過去に発生した相続については経過措置が設けられており、<strong>施行日（2024年4月1日）より前に相続が開始していた不動産は、施行日から3年以内（おおむね2027年3月末まで）</strong>が申請期限の目安とされています。心当たりのある方は早めの確認をおすすめします。</p>\n<p>なお、「正当な理由」があると認められる場合（相続人が極めて多数で資料収集に時間がかかる、相続人間で争いがある等）には、直ちに過料の対象とはならないと整理されています。具体的な該当性は個別判断となるため、心配な場合は法務局や司法書士へ相談すると安心です。</p>"),
            ("期限に間に合わないときの「相続人申告登記」", "<p>遺産分割の話し合いがまとまらず、3年以内に通常の相続登記まで終えられないこともあります。こうした場合に備えて、義務化と同時に<strong>相続人申告登記</strong>という新しい簡易な手続きが設けられました（不動産登記法第76条の3）。</p>\n<p>相続人申告登記は、<strong>「自分が登記名義人の相続人である」ことを法務局に申し出る</strong>制度です。これを期限内に行えば、ひとまず相続登記の申請義務を果たしたものとみなされます。特徴は次のとおりです。</p>\n<ul>\n<li>相続人が1人で申し出ることができ、<strong>遺産分割の成立を待たずに利用</strong>できます。</li>\n<li>必要書類が通常の相続登記より少なく済む場合が多く、手続きの負担が比較的軽いとされています。</li>\n<li>あくまで「申告」であり、正式な権利関係（誰が最終的に取得するか）を確定させるものではありません。</li>\n</ul>\n<p>そのため、遺産分割がまとまった後は、改めて<strong>分割成立日から3年以内</strong>に正式な相続登記を申請する必要があります。相続人申告登記は「いったん義務を果たすための応急的な手続き」と理解しておくとよいでしょう。</p>"),
            ("相続登記の申請方法と必要書類・費用の目安", "<p>相続登記は、対象の不動産を管轄する<strong>法務局（登記所）</strong>に申請します。窓口・郵送のほか、オンライン申請も利用できます。一般的な流れは次のとおりです。</p>\n<ol>\n<li>遺言書の有無を確認し、なければ法定相続人を確定する。</li>\n<li>戸籍などで相続関係を証明し、遺産分割協議書を作成する（協議による場合）。</li>\n<li>登記申請書を作成し、必要書類を添えて法務局へ申請する。</li>\n</ol>\n<p>主な必要書類の例は以下のとおりです（ケースにより異なります）。</p>\n<ul>\n<li>被相続人の出生から死亡までの戸籍（除籍・改製原戸籍を含む）</li>\n<li>相続人全員の戸籍謄本・住民票</li>\n<li>遺産分割協議書および相続人全員の印鑑証明書（協議による場合）</li>\n<li>対象不動産の固定資産評価証明書</li>\n</ul>\n<p>費用面では、<strong>登録免許税</strong>として原則「固定資産税評価額×0.4％（1000分の4）」がかかります（登録免許税法）。たとえば評価額1,000万円の不動産なら4万円が目安です。司法書士に依頼する場合は別途報酬がかかります。一定の要件を満たす場合に登録免許税が免除される特例もあるため、<strong>最新の税率・免税要件や手続きの詳細は、法務局・国税庁や司法書士などの専門家で必ずご確認ください</strong>。</p>"),
            ("放置するとどうなる？早めに動くメリット", "<p>相続登記をせずに放置すると、過料のリスクだけでなく実生活上の不利益も生じやすくなります。</p>\n<ul>\n<li><strong>売却・担保設定ができない</strong>：名義が被相続人のままだと、不動産を売ったり、住宅ローンの担保に入れたりできません。</li>\n<li><strong>相続人が増えて手続きが複雑化する</strong>：放置している間に相続人が亡くなると、次の世代へ相続が重なり、関係者が大幅に増えて協議が難航しがちです。</li>\n<li><strong>書類収集が困難になる</strong>：時間が経つほど戸籍の取得や連絡先の把握が難しくなる場合があります。</li>\n</ul>\n<p>逆に早めに手続きを済ませておけば、権利関係が明確になり、将来の世代に負担を残さずに済みます。「まだ大丈夫」と先延ばしにせず、相続が発生したら、あるいは過去の未登記に心当たりがあれば、できるだけ早く確認・着手することをおすすめします。判断に迷う場合は、最寄りの法務局や司法書士などの専門家へ相談すると安心です。</p>"),
        ],
        "faqs": [
            ("相続登記の義務化は、施行前に相続した不動産にも適用されますか？", "はい、適用されるとされています。2024年4月1日の施行より前に相続が開始した不動産も義務の対象で、経過措置として施行日から3年以内（おおむね2027年3月末まで）が申請期限の目安とされています。長年放置している名義変更がある場合は、早めに確認することをおすすめします。"),
            ("期限内に遺産分割がまとまらない場合はどうすればよいですか？", "「相続人申告登記」を利用する方法があります。自分が相続人であることを法務局に申し出ることで、いったん申請義務を果たしたものとみなされます。ただし正式な権利確定ではないため、遺産分割が成立した後は、その成立日から3年以内に改めて相続登記を申請する必要があります。"),
            ("相続登記は自分でできますか？それとも専門家に頼むべきですか？", "必要書類をそろえて法務局に申請すれば、ご自身で手続きすることも可能です。一方、相続人が多い・関係が複雑・不動産が複数あるといったケースでは、司法書士などの専門家に依頼すると手続きがスムーズです。費用や手続きの詳細は法務局や専門家でご確認ください。"),
        ],
    },
    {
        "slug": "relationship-chart",
        "title": "相続関係説明図の作り方｜法定相続情報一覧図との違いと書き方手順",
        "h1": "相続関係説明図の作り方と法定相続情報一覧図との違い",
        "desc": "相続関係説明図の作り方を、必要書類・書き方の手順・記載例までやさしく解説します。混同しやすい法定相続情報一覧図との違いや使い分け、作成時の注意点もまとめました。相続手続きを自分で進めたい方の最初の一歩に。",
        "keywords": "相続関係説明図,作り方,法定相続情報一覧図,違い,法定相続情報証明制度,相続手続き",
        "lead": "<strong>相続関係説明図</strong>は、亡くなった方（被相続人）と相続人の関係を一枚にまとめた家系図のような書類で、不動産の相続登記などで戸籍の原本を返してもらう（原本還付を受ける）ために役立ちます。よく似た「法定相続情報一覧図」との違いがわかりにくいため、本記事で作り方と使い分けを整理します。",
        "sections": [
            ("相続関係説明図とは？何のために作るのか", "<p>相続関係説明図とは、<strong>被相続人と相続人の関係を一覧にした図</strong>です。法律で様式が厳密に定められた書類ではありませんが、相続手続きの実務で広く使われています。最も典型的な用途が、不動産の名義変更である<strong>相続登記</strong>の際に、提出した戸籍謄本等の<strong>原本還付</strong>を受けるためのものです。</p>\n<p>相続登記では、被相続人の出生から死亡までの戸籍・除籍謄本や相続人全員の戸籍など、多数の書類を法務局に提出します。これらの原本は他の手続き（預貯金の解約、相続税申告など）でも必要になることが多く、相続関係説明図を添付すると、戸籍のコピーを別途用意しなくても原本を返してもらえる取扱いがされています。</p>\n<p>なお、相続登記は<strong>2024年（令和6年）4月1日</strong>から義務化され、原則として相続による不動産取得を知った日から<strong>3年以内</strong>の登記申請が求められるようになりました（不動産登記法第76条の2）。正当な理由なく怠ると過料の対象となる場合があるため、早めの準備が大切です。</p>"),
            ("法定相続情報一覧図との違い・使い分け", "<p>相続関係説明図とよく混同されるのが、<strong>法定相続情報一覧図</strong>です。これは<strong>法定相続情報証明制度</strong>（2017年〈平成29年〉5月29日開始）に基づくもので、法務局（登記所）に申し出て<strong>法務局が内容を確認・認証</strong>し、写しを交付してくれる公的な書類です。両者の主な違いは次のとおりです。</p>\n<table>\n<tr><th>項目</th><th>相続関係説明図</th><th>法定相続情報一覧図</th></tr>\n<tr><td>作成者</td><td>相続人など（自分で作成）</td><td>申出人が作成し法務局が認証</td></tr>\n<tr><td>法務局の認証</td><td>なし</td><td>あり（公的証明）</td></tr>\n<tr><td>主な用途</td><td>相続登記での戸籍原本還付</td><td>各種手続きで戸籍の束の代わり</td></tr>\n<tr><td>交付・費用</td><td>—（自作）</td><td>法務局で無料交付（複数枚可）</td></tr>\n</table>\n<p>大きな違いは、<strong>法務局の認証があるかどうか</strong>です。法定相続情報一覧図の写しは、銀行・証券会社・年金事務所・税務署など複数の窓口で<strong>戸籍一式の束の代わり</strong>として使え、無料で必要枚数を取得できる点が便利です。一方、相続登記だけを自分で行う簡単なケースでは、相続関係説明図で十分な場合もあります。手続きする窓口が多い場合は、法定相続情報一覧図の取得を検討するとよいでしょう。</p>"),
            ("相続関係説明図に必要な書類と準備", "<p>相続関係説明図を正確に作るには、まず家族関係を確定させるための戸籍を集めます。一般的に必要となる主な書類は次のとおりです。</p>\n<ul>\n<li><strong>被相続人の出生から死亡までの戸籍謄本・除籍謄本・改製原戸籍</strong>（連続したもの）</li>\n<li>被相続人の<strong>住民票の除票</strong>（または戸籍の附票）</li>\n<li>相続人全員の<strong>現在の戸籍謄本（抄本）</strong></li>\n<li>必要に応じて相続人の住民票</li>\n</ul>\n<p>戸籍は本籍地の市区町村で取得します。2024年3月以降は、<strong>戸籍の広域交付制度</strong>により、最寄りの市区町村の窓口でまとめて請求できるようになり、収集の負担が軽くなりました（一部、請求できる人や戸籍の範囲に制限があります）。集めた戸籍から、誰が相続人になるか（配偶者・子・直系尊属・兄弟姉妹といった<strong>法定相続人</strong>の範囲、民法第887条〜第890条）を確認します。</p>"),
            ("相続関係説明図の作り方（書き方の手順）", "<p>必要書類がそろったら、次の手順で作成します。手書きでもパソコン（WordやExcel）でも構いません。</p>\n<ul>\n<li><strong>1. タイトルを記載</strong>：「被相続人 ○○○○ 相続関係説明図」と上部に書きます。</li>\n<li><strong>2. 被相続人の情報</strong>：氏名・生年月日・死亡年月日・最後の本籍・最後の住所を記載します。</li>\n<li><strong>3. 相続人の情報</strong>：配偶者や子など各相続人の氏名・生年月日・続柄・住所を記載します。</li>\n<li><strong>4. 関係を線で結ぶ</strong>：配偶者とは二重線（＝）、親子は縦線でつなぎ、家系図のように関係を示します。</li>\n<li><strong>5. 相続の有無を明記</strong>：不動産を取得する人に「相続」、取得しない人に「分割」や「相続放棄」など、立場がわかる表記を添えます。</li>\n</ul>\n<p>記載のイメージは次のとおりです。</p>\n<table>\n<tr><td>被相続人 山田太郎（昭和○年○月○日生・令和○年○月○日死亡）</td></tr>\n<tr><td>　└ 妻 山田花子（＝で接続／「相続」）</td></tr>\n<tr><td>　└ 長男 山田一郎（縦線で接続／「分割」）</td></tr>\n</table>\n<p>すでに亡くなっている相続人がいて孫などが相続する場合（<strong>代襲相続</strong>、民法第887条第2項）は、その関係も忘れず図に反映します。離婚した元配偶者は相続人ではありませんが、その間の子は相続人になる点にも注意が必要です。</p>"),
            ("作成時の注意点とよくある間違い", "<p>相続関係説明図は様式が自由なぶん、記載漏れや関係の誤りが起こりやすい書類です。次の点に注意しましょう。</p>\n<ul>\n<li><strong>戸籍の連続性</strong>：被相続人の出生まで戸籍がつながっていないと相続人を確定できません。転籍や婚姻で抜けがないか確認します。</li>\n<li><strong>相続人の取りこぼし</strong>：前婚の子、認知した子、養子なども相続人になり得ます。戸籍を必ず突き合わせて確認します。</li>\n<li><strong>続柄・氏名・日付の正確さ</strong>：戸籍の記載どおりに転記し、誤字や日付の写し間違いを避けます。</li>\n<li><strong>用途による要件の違い</strong>：法定相続情報一覧図には記載事項の決まり（住所の任意記載など）があり、相続関係説明図とは要件が異なります。</li>\n</ul>\n<p>制度の要件や必要書類は改正されることがあり、提出先によって取扱いが異なる場合もあります。<strong>最新の要件は、国税庁・法務局（登記所）や、司法書士・税理士などの専門家に必ずご確認ください</strong>。判断に迷うケースや相続人が多く複雑な場合は、早めに専門家へ相談すると安心です。</p>"),
        ],
        "faqs": [
            ("相続関係説明図は手書きでもよいですか？", "はい、相続関係説明図に決まった様式はなく、手書きでもパソコン作成でも問題ないとされています。重要なのは、被相続人と相続人の関係が戸籍の内容と一致し、誰が相続人かを正確に表していることです。読みやすさの点では、WordやExcelで作成し氏名・生年月日・続柄などを整理して記載する方法が一般的です。"),
            ("相続関係説明図と法定相続情報一覧図は両方必要ですか？", "必ずしも両方は必要ありません。手続きする窓口が相続登記のみなど少ない場合は、相続関係説明図だけで戸籍の原本還付を受けられることがあります。一方、銀行・証券・年金など複数の窓口で手続きする場合は、法務局が認証し無料で複数枚交付される法定相続情報一覧図の方が、戸籍一式を何度も提出せずに済み便利です。用途に応じて使い分けるとよいでしょう。"),
            ("相続関係説明図の作成に費用はかかりますか？", "自分で作成する場合、図そのものの作成費用はかかりません。ただし、作成の前提として戸籍謄本・除籍謄本などの取得手数料が必要です（1通あたり数百円程度が一般的ですが、種類により異なります）。司法書士などの専門家に依頼する場合は別途報酬がかかります。最新の手数料は各市区町村や専門家にご確認ください。"),
        ],
    },
    {
        "slug": "old-koseki-reading",
        "title": "古い戸籍の読み方｜旧字体・くずし字と家系調査のコツ",
        "h1": "古い戸籍の読み方と家系調査の進め方",
        "desc": "相続手続きで集めた古い戸籍が読めない方へ。旧字体・くずし字の解読、改製原戸籍や除籍の見方、明治期までさかのぼる家系調査のコツを、実務目線でわかりやすく解説します。",
        "keywords": "古い戸籍 読み方,旧字体,くずし字,改製原戸籍,除籍謄本,家系調査",
        "lead": "<strong>古い戸籍の読み方</strong>に戸惑う方は少なくありません。相続手続きでは亡くなった方の出生から死亡までの戸籍をすべて集める必要があり、明治・大正期の手書き戸籍にぶつかります。本記事では旧字体やくずし字の読み解き方、戸籍の種類と構造、家系調査のコツを実務目線で整理します。",
        "sections": [
            ("なぜ相続で「古い戸籍」を読む必要があるのか", "<p>相続では、法定相続人を確定するために<strong>被相続人（亡くなった方）の出生から死亡までの連続した戸籍</strong>を集めるのが基本です。婚姻・転籍・法改正などで戸籍は何度も作り替えられているため、最新の戸籍だけでは出生までさかのぼれず、過去の戸籍を取り寄せることになります。</p>\n<p>集めた戸籍は、預貯金の解約、不動産の相続登記、相続税の申告など多くの場面で使われます。とくに<strong>不動産の相続登記は令和6年（2024年）4月1日から義務化</strong>され、原則として相続を知った日から3年以内の申請が求められるようになりました。手続きの入口で戸籍が読めずに止まってしまうケースは珍しくありません。</p>\n<ul>\n<li><strong>戸籍謄本（全部事項証明書）</strong>：現在の戸籍。多くは横書き・印字。</li>\n<li><strong>改製原戸籍（かいせいげんこせき）</strong>：法改正で作り替えられる前の古い戸籍。手書きが多い。</li>\n<li><strong>除籍謄本</strong>：全員が抜けて閉じられた戸籍。古いものは縦書き・手書き。</li>\n</ul>\n<p>なお令和6年（2024年）3月から<strong>戸籍の広域交付</strong>が始まり、本籍地以外の市区町村の窓口でも、本人や直系の親族分をまとめて請求しやすくなりました（一部対象外あり）。最新の運用は本籍地の市区町村や法務局でご確認ください。</p>"),
            ("旧字体・異体字を見分けるコツ", "<p>古い戸籍でまず戸惑うのが<strong>旧字体（旧漢字）や異体字</strong>です。同じ人物・地名でも、戸籍ごとに字体が違って見えることがあります。代表的な対応を知っておくと一気に読みやすくなります。</p>\n<table>\n<tr><th>旧字体・異体字</th><th>現在の字</th></tr>\n<tr><td>澤</td><td>沢</td></tr>\n<tr><td>邊・邉</td><td>辺</td></tr>\n<tr><td>齊・齋</td><td>斉・斎</td></tr>\n<tr><td>髙（はしごだか）</td><td>高</td></tr>\n<tr><td>廣</td><td>広</td></tr>\n<tr><td>櫻</td><td>桜</td></tr>\n</table>\n<p>注意したいのは、戸籍上の氏名は<strong>登記や金融機関の名義と完全一致が求められる場合がある</strong>点です。「高橋」と「髙橋」のように、戸籍では旧字・異体字のまま記載されていることがあります。手続き先によって取り扱いが異なるため、写しを取る際は<strong>字体をそのまま正確に記録</strong>しておくと後の照合がスムーズです。判断に迷う字は、勝手に新字に置き換えず原本どおり控えるのが安全です。</p>"),
            ("くずし字・変体仮名の読み解き方", "<p>明治から昭和初期の戸籍は<strong>毛筆や手書き</strong>で、続け字（くずし字）や<strong>変体仮名</strong>が使われていることがあります。変体仮名とは、現在は使われない平仮名の字形のことです（例：「す」を「春」をくずした形で書くなど）。読みにくいときは次の手順が有効です。</p>\n<ul>\n<li><strong>前後の文脈から推測する</strong>：戸籍の様式は決まっているため、「父」「母」「長男」「妻」「出生」「婚姻」などの定型語を手がかりにする。</li>\n<li><strong>同じ字を探す</strong>：同一戸籍内で同じ文字が別の箇所に出ていれば、読みやすい方から判断できる。</li>\n<li><strong>年号と元号で日付を絞る</strong>：明治・大正・昭和の元号と数字の形に慣れると、生年月日や届出日が読みやすくなる。</li>\n<li><strong>地名・屋号は地図や旧地名で照合</strong>：本籍の番地は現在と表記が異なることがある。</li>\n</ul>\n<p>独力で読めない場合は、自治体の<strong>くずし字・古文書の解読サービス</strong>や、図書館・郷土資料館の相談窓口、専門家（司法書士・行政書士など）に相談する方法もあります。近年は変体仮名の学習サイトやアプリも整備されつつあり、補助として活用できる場合があります。</p>"),
            ("戸籍の構造を理解すると読みやすくなる", "<p>古い戸籍は、字そのものより<strong>「どこに何が書いてあるか」</strong>がわかると格段に読みやすくなります。明治・大正・昭和（改正前）の戸籍は、原則として<strong>「戸主」を筆頭とした家単位</strong>で編成されており、戸主・その配偶者・子・場合によっては親や兄弟までが一つの戸籍に入っていました。</p>\n<p>各人の欄には、おおむね次のような事項が記載されます。読む順番の目安として押さえておくと便利です。</p>\n<ul>\n<li><strong>本籍・戸主の氏名</strong>（戸籍の冒頭）</li>\n<li><strong>各人の続柄</strong>（長男・二女・妻・母 など）</li>\n<li><strong>出生・婚姻・養子縁組・死亡などの事由</strong>と、その年月日・届出日</li>\n<li><strong>従前戸籍・新本籍</strong>（どこから入り、どこへ出たか）</li>\n</ul>\n<p>とくに重要なのが<strong>「いつ、どこから入り、どこへ出たか」</strong>の記載です。「○年○月○日 ○○より入籍」「○年○月○日 ○○へ婚姻により除籍」といった文言をたどることで、次に取り寄せるべき戸籍（前の本籍地の戸籍）がわかり、出生まで連続してさかのぼれます。現行の戸籍法（昭和23年施行の改正により「家」制度を前提とした戸主制度は廃止）以前のものほど家単位の色が濃いため、構造を意識して読むことが解読の近道です。</p>"),
            ("家系調査として戸籍をさかのぼるコツ", "<p>相続手続きにとどまらず、ルーツを知る<strong>家系調査</strong>として戸籍を活用する方も増えています。戸籍は法律上、現存するものは<strong>明治期（明治19年式・明治31年式の戸籍など）までさかのぼれる場合がある</strong>とされますが、戦災・災害・保存期間満了などで取得できないこともあります。</p>\n<ul>\n<li><strong>取得は「新しい順」にたどる</strong>：現在の戸籍 → 改製原戸籍 → 除籍 と、記載されている従前本籍を手がかりに一つずつ古い方へ請求する。</li>\n<li><strong>除籍・改製原戸籍の保存期間</strong>：現在は法令上150年とされています（過去の取扱いで既に廃棄され取得できないものもあります）。古いものは早めの請求が安心です。</li>\n<li><strong>請求できる人の範囲</strong>：戸籍は誰でも取れるわけではなく、本人・配偶者・直系の親族などに限られます。家系調査でも続柄の証明が必要になる場合があります。</li>\n<li><strong>専門家への依頼</strong>：司法書士・行政書士は職務上、戸籍収集を代行できる場合があります。判読や取り寄せが難しいときの選択肢になります。</li>\n</ul>\n<p>保存期間や請求できる範囲、広域交付の対象などの制度は改正されることがあります。<strong>最新の要件や具体的な手続きは、本籍地の市区町村役場・法務局・国税庁(相続税関連)や、司法書士などの専門家でご確認ください。</strong>本記事は一般的な解説であり、個別の事案の判断を保証するものではありません。</p>"),
        ],
        "faqs": [
            ("古い戸籍が手書きで全く読めません。どうすればよいですか。", "まずは戸籍の様式が定型である点を利用し、「父」「母」「長男」「出生」「婚姻」などの決まった語と元号・日付から読み解くのが基本です。それでも難しい場合は、図書館や郷土資料館のくずし字相談、自治体の解読サービス、司法書士・行政書士などの専門家に相談する方法があります。氏名や日付の読み違いは手続きに影響するため、自己判断で断定せず確認することをおすすめします。"),
            ("戸籍の氏名が旧字体です。新しい字に直して手続きしてよいですか。", "手続き先によって取り扱いが異なります。相続登記や金融機関の名義照合では、戸籍どおりの字体での記載を求められる場合があるため、勝手に新字へ置き換えるのは避け、原本どおり正確に控えておくのが安全です。具体的な記載方法は、提出先の法務局や金融機関、専門家にご確認ください。"),
            ("戸籍はどこまで古くさかのぼれますか。", "現存するものでは明治期の戸籍（明治19年式・明治31年式など）までさかのぼれる場合があるとされますが、戦災・災害・保存期間満了により取得できないこともあります。除籍・改製原戸籍の保存期間は現在150年とされていますが、過去の取扱いで既に廃棄されているものもあるため、古い戸籍は早めの請求が安心です。"),
        ],
    },
    {
        "slug": "property-division-methods",
        "title": "換価分割と代償分割の違い｜不動産が分けにくい相続の選択肢",
        "h1": "換価分割と代償分割の違いと選び方",
        "desc": "換価分割と代償分割の違いを、不動産が分けにくい相続の場面で解説します。仕組み・メリット・デメリット・税金（譲渡所得税・小規模宅地等の特例）・手続きの注意点を実務目線で整理し、選び方の判断材料を提供します。",
        "keywords": "換価分割,代償分割,遺産分割,不動産相続,譲渡所得税,小規模宅地等の特例",
        "lead": "<strong>換価分割と代償分割</strong>は、現金で分けにくい不動産などをめぐる遺産分割でよく使われる2つの方法です。どちらを選ぶかで、手取り額・税金・手続きの負担が大きく変わることがあります。",
        "sections": [
            ("遺産分割の4つの方法と「分けにくい財産」の問題", "<p>相続財産の分け方には、主に4つの方法があるとされています。まずは全体像を押さえると、換価分割・代償分割の位置づけが理解しやすくなります。</p>\n<ul>\n<li><strong>現物分割</strong>：不動産はAさん、預貯金はBさん、というように財産そのものを各相続人へ割り当てる方法。</li>\n<li><strong>代償分割</strong>：特定の相続人が不動産などを取得し、他の相続人へその差額を現金等で支払う方法。</li>\n<li><strong>換価分割</strong>：不動産などを売却し、その売却代金を相続人で分ける方法。</li>\n<li><strong>共有分割</strong>：複数の相続人で共有名義のまま持ち合う方法。</li>\n</ul>\n<p>問題になりやすいのが、遺産の大半が自宅などの不動産で、現金が少ないケースです。不動産は1円単位できれいに分けられないため、現物分割だけでは公平に分けにくくなります。安易に共有名義にすると、将来の売却や建て替えに共有者全員の同意が必要になり、トラブルの火種になりやすいとされます。こうした「分けにくい財産」を公平に分ける手段として、換価分割と代償分割が選択肢になります。</p>"),
            ("換価分割とは｜売って現金で分ける方法", "<p><strong>換価分割</strong>は、相続した不動産などを売却し、得られた現金を相続人で分け合う方法です。たとえば、自宅(評価額3,000万円)を相続人3人で分けるとき、誰も住む予定がなければ売却して、諸費用を差し引いた手取りを法定相続分などに応じて分配します。</p>\n<p>主なメリットは次のとおりです。</p>\n<ul>\n<li>現金で分けるため、1円単位で公平に分けやすい。</li>\n<li>誰も使わない不動産を手放せ、固定資産税や管理の負担から解放される。</li>\n<li>代償金を用意できる相続人がいなくても成立する。</li>\n</ul>\n<p>一方で注意点もあります。</p>\n<ul>\n<li>売却益が出ると<strong>譲渡所得税・住民税</strong>の対象になる場合があります。売却代金から取得費・譲渡費用を差し引いた譲渡所得に課税され、被相続人が取得した時期を引き継ぐため、長期譲渡所得(所有期間5年超)として扱われることが多いとされます。</li>\n<li>売却まで時間がかかり、希望価格で売れるとは限りません。</li>\n<li>思い出のある実家を手放すことになり、心理的な抵抗が生じることもあります。</li>\n</ul>\n<p>なお、相続した空き家を売る場合の特例(被相続人の居住用財産＝空き家に係る譲渡所得の特別控除)など、要件を満たせば税負担を軽減できる制度もあります。適用には細かな要件と期限があるため、利用を検討する際は事前に確認が必要です。</p>"),
            ("代償分割とは｜1人が取得して差額を払う方法", "<p><strong>代償分割</strong>は、特定の相続人が不動産などを単独で取得する代わりに、他の相続人へ取得分との差額を金銭(代償金)で支払う方法です。たとえば、長男が3,000万円の実家を取得し、他の2人の相続人へそれぞれ1,000万円ずつ支払う、といった形です。</p>\n<p>主なメリットは次のとおりです。</p>\n<ul>\n<li>実家に住み続けたい人がいる場合など、不動産を手放さずに済む。</li>\n<li>事業用地や同族会社の株式など、分散させたくない財産を1人に集約できる。</li>\n<li>売却の手間や売却益への課税が、原則として生じない。</li>\n</ul>\n<p>一方で注意点もあります。</p>\n<ul>\n<li>取得する相続人に、代償金を支払うだけの<strong>資力</strong>が必要です。</li>\n<li>不動産の評価額をいくらと見るか(時価・路線価・固定資産税評価額など)で代償金の額が変わり、相続人間で対立しやすいとされます。</li>\n<li>遺産分割協議書に「代償分割として支払う」旨を明記しておかないと、税務上、相続人間の贈与とみなされるおそれがあるとされます。</li>\n</ul>\n<p>代償金を不動産など金銭以外で支払うと、支払う側に譲渡所得税が課される場合があるため、現金での支払いが基本とされます。</p>"),
            ("税金の違いと「小規模宅地等の特例」への影響", "<p>2つの方法は、かかる税金の種類が異なります。整理すると次のとおりです。</p>\n<table>\n<tr><th>項目</th><th>換価分割</th><th>代償分割</th></tr>\n<tr><td>相続税</td><td>かかる(取得した現金額に応じて)</td><td>かかる(取得した財産・代償金を調整して計算)</td></tr>\n<tr><td>譲渡所得税・住民税</td><td>売却益が出れば各相続人にかかる場合がある</td><td>原則かからない(金銭以外で代償した場合を除く)</td></tr>\n<tr><td>不動産取得・名義</td><td>売却して現金化</td><td>取得者へ名義変更(登録免許税等)</td></tr>\n</table>\n<p>見落とされがちなのが<strong>小規模宅地等の特例</strong>(相続税の課税価格を計算する際、一定の宅地の評価額を最大80%減額できる制度)です。被相続人の自宅敷地について、配偶者や同居していた親族などが取得し、申告期限まで保有・居住を続けるなどの要件を満たすと適用できる場合があります。</p>\n<p>換価分割で申告期限前に売却してしまうと、要件によっては特例が使えなくなるおそれがあるとされます。一方、代償分割で要件を満たす相続人が取得すれば、特例の適用を受けつつ他の相続人へ代償金を渡せる場合があります。誰が取得すると相続税全体が有利になるかは個別事情で変わるため、申告前のシミュレーションが重要です。</p>\n<p>なお、税率・控除額・各特例の適用要件や期限は改正されることがあります。<strong>最新の要件は、国税庁・法務局や、税理士・司法書士などの専門家で必ずご確認ください。</strong></p>"),
            ("どちらを選ぶ？判断のポイントと手続きの流れ", "<p>どちらが適しているかは、家族の希望と財産の中身によって変わります。判断の目安は次のとおりです。</p>\n<ul>\n<li><strong>換価分割が向くケース</strong>：誰もその不動産を使う予定がない／公平に現金で分けたい／代償金を用意できる人がいない。</li>\n<li><strong>代償分割が向くケース</strong>：住み続けたい人や事業で使う人がいる／不動産を手放したくない／取得者に十分な資力がある。</li>\n</ul>\n<p>両者を組み合わせ、一部の不動産は売却して分け、残りは1人が取得して代償金を払う、といった併用も可能とされます。</p>\n<p>大まかな手続きの流れは次のとおりです。</p>\n<ul>\n<li>相続人の確定と財産・評価額の把握(不動産は時価や路線価などを確認)。</li>\n<li>分割方法の話し合い(遺産分割協議)。</li>\n<li>合意内容を<strong>遺産分割協議書</strong>に明記(換価分割・代償分割である旨、代償金の額・支払時期などを具体的に記載)。</li>\n<li>相続登記(2024年4月1日から相続登記は義務化されており、原則として取得を知った日から3年以内の申請が求められるとされます)。換価分割では、いったん代表者等へ登記してから売却する方法もあります。</li>\n<li>相続税の申告・納付(原則として相続の開始を知った日の翌日から10か月以内)。</li>\n</ul>\n<p>分け方の選択は、税金・登記・家族関係が複雑に絡みます。早めに専門家へ相談し、シミュレーションのうえで進めることをおすすめします。</p>"),
        ],
        "faqs": [
            ("換価分割と代償分割は併用できますか？", "併用は可能とされます。たとえば、複数の不動産のうち一部を売却して現金で分け(換価分割)、残りの一棟は同居していた相続人が取得して他の相続人へ代償金を支払う(代償分割)、といった組み合わせができます。財産の種類や家族の希望に応じて柔軟に設計できますが、遺産分割協議書にそれぞれの方法と内容を明確に記載しておくことが大切です。"),
            ("代償分割で支払う代償金に贈与税はかかりますか？", "遺産分割協議書に「代償分割として支払う」旨を明記し、遺産の取得に伴う適正な代償として支払う限り、原則として贈与税の対象にはならないとされます。ただし、協議書への記載がない場合や、取得した財産の価額に比べて代償金が過大な場合などは、相続人間の贈与とみなされるおそれがあるとされます。判断に迷う場合は税理士へご確認ください。"),
            ("換価分割で不動産を売ったとき、税金は誰にかかりますか？", "売却によって譲渡益(売却代金から取得費・譲渡費用を差し引いた額)が出た場合、その不動産を相続して売却した各相続人に、持分に応じて譲渡所得税・住民税がかかる場合があります。被相続人の取得時期や取得費を引き継いで計算するため、長期譲渡所得として扱われることが多いとされます。空き家の譲渡所得の特別控除など、要件を満たせば負担を軽減できる制度もあるため、最新の要件を国税庁等でご確認ください。"),
        ],
    },
    {
        "slug": "land-to-state",
        "title": "相続土地国庫帰属制度とは｜いらない土地を国に返す方法と費用・要件【2023年開始】",
        "h1": "相続土地国庫帰属制度｜いらない土地を手放す方法",
        "desc": "2023年4月に始まった相続土地国庫帰属制度を解説。相続した使わない土地を国に引き取ってもらう仕組み、対象外となる土地の要件、負担金10年分の費用、申請手続きの流れと注意点を、相続実務の観点からわかりやすくまとめます。",
        "keywords": "相続土地国庫帰属制度,いらない土地,土地放棄,負担金,法務局申請,相続放棄",
        "lead": "<strong>相続土地国庫帰属制度</strong>は、相続した「使い道のない土地」を一定の要件と負担金のもとで国に引き取ってもらえる制度として、2023年4月27日に施行されました。空き地・遠方の山林など、手放したくても買い手がつかない土地への新たな選択肢として注目されています。",
        "sections": [
            ("相続土地国庫帰属制度とはどんな制度か", "<p>相続土地国庫帰属制度は、<strong>相続土地国庫帰属法（相続等により取得した土地所有権の国庫への帰属に関する法律）</strong>にもとづき、2023年（令和5年）4月27日に施行された制度です。相続または遺贈（相続人に対する遺贈に限る）によって土地を取得した人が、一定の要件を満たす場合に、その土地の所有権を国に引き渡す（国庫に帰属させる）ことを申請できます。</p>\n<p>背景には、<strong>所有者不明土地</strong>や管理されない空き地の増加があります。使わない土地でも所有している限り固定資産税や管理の負担が続くため、「いらない土地だけを手放したい」というニーズに応えるために設けられました。土地の売却や寄付がうまくいかない場合の選択肢の一つとされています。</p>\n<p>申請の窓口は、その土地を管轄する<strong>法務局・地方法務局</strong>です。審査を経て承認されると、定められた負担金を納付することで土地の所有権が国に移ります。</p>"),
            ("相続放棄との違い", "<p>「いらない土地を手放す」方法として相続放棄と混同されがちですが、両者はまったく別の制度です。違いを整理します。</p>\n<table>\n<tr><th>項目</th><th>相続土地国庫帰属制度</th><th>相続放棄</th></tr>\n<tr><td>対象</td><td>欲しくない土地だけを選んで手放せる</td><td>プラスの財産も含めすべて放棄</td></tr>\n<tr><td>期限</td><td>明確な申請期限はない（相続後いつでも可）</td><td>原則、自己のために相続の開始を知った時から3か月以内</td></tr>\n<tr><td>根拠</td><td>相続土地国庫帰属法</td><td>民法第915条ほか</td></tr>\n</table>\n<p>相続放棄は、預貯金や自宅などの<strong>プラスの財産も一切受け取れなくなる</strong>うえ、原則3か月という熟慮期間の制限があります。一方、相続土地国庫帰属制度は、他の財産は相続したうえで<strong>不要な土地だけを切り離せる</strong>点が大きな特徴です。すでに相続した土地にも利用できるため、過去の相続分にも対応できる場合があります。</p>"),
            ("引き取ってもらえない土地（却下・不承認の要件）", "<p>どんな土地でも引き取ってもらえるわけではありません。法律上、申請の段階で受け付けられない「<strong>却下事由</strong>」と、審査で承認されない「<strong>不承認事由</strong>」が定められています。代表的なものは次のとおりです。</p>\n<ul>\n<li><strong>建物がある土地</strong>（更地にする必要があります）</li>\n<li>担保権（抵当権など）や使用収益権が設定されている土地</li>\n<li>他人の利用が予定されている土地、通路など</li>\n<li>土壌汚染がある土地</li>\n<li>境界が明らかでない土地、所有権の存否や範囲に争いがある土地</li>\n<li>崖（勾配・高さ等が一定以上で管理に過分な費用・労力がかかるもの）がある土地</li>\n<li>管理・処分を阻害する工作物、車両、樹木などが地上にある土地</li>\n<li>除去しなければならない有体物が地下にある土地</li>\n</ul>\n<p>つまり、<strong>そのまま国が管理できる状態</strong>であることが前提です。農地や山林も対象になり得ますが、管理に過分な費用や労力を要するものは不承認となる場合があります。自分の土地が該当するか不安な場合は、申請前に法務局へ相談することができます。</p>"),
            ("費用と手続きの流れ", "<p>制度を利用するには、<strong>審査手数料</strong>と<strong>負担金</strong>の2種類の費用がかかります。</p>\n<ul>\n<li><strong>審査手数料</strong>：土地一筆あたり1万4,000円（収入印紙で納付）。承認されなくても返還されません。</li>\n<li><strong>負担金</strong>：原則として、土地の<strong>10年分の管理費相当額</strong>として算定されます。多くの宅地・農地などは1筆あたり20万円が基準とされますが、面積や種目（市街化区域の宅地・農地など）によっては面積に応じて増額される場合があります。</li>\n</ul>\n<p>大まかな手続きの流れは次のとおりです。</p>\n<ul>\n<li>① 法務局へ事前相談（任意・予約制）</li>\n<li>② 承認申請書と添付書類を法務局へ提出、審査手数料を納付</li>\n<li>③ 法務局による書面審査・実地調査</li>\n<li>④ 承認・不承認の通知</li>\n<li>⑤ 承認後、通知された負担金を期限内（通知から30日以内）に納付</li>\n<li>⑥ 納付した時点で土地の所有権が国庫に帰属</li>\n</ul>\n<p>負担金を期限内に納付しないと承認の効力が失われる点に注意が必要です。<strong>審査手数料・負担金の具体的な金額や算定方法、最新の要件は、法務省・法務局の公式情報や専門家（司法書士・弁護士など）で必ずご確認ください。</strong></p>"),
            ("利用前に検討したい注意点と代替策", "<p>この制度は便利ですが、すべての土地で使えるわけではなく、費用もかかります。申請前に次の点を整理しておくと判断しやすくなります。</p>\n<ul>\n<li><strong>建物がある場合は解体費用がかかる</strong>：更地にする費用と負担金の合計が、土地の価値に見合うか検討します。</li>\n<li><strong>売却・贈与が先か</strong>：買い手や引き取り手がいるなら、売却や自治体・隣地所有者への譲渡のほうが負担が軽い場合があります。</li>\n<li><strong>共有地は全員の合意が必要</strong>：共有名義の土地は、共有者全員で共同して申請する必要があるとされます。</li>\n<li><strong>境界の確定や書類準備</strong>：境界が不明確だと却下されるため、事前の測量や資料整理が必要になることがあります。</li>\n</ul>\n<p>これらの判断は税務（譲渡所得・固定資産税など）や登記とも関わるため、<strong>司法書士・弁護士・税理士などの専門家に早めに相談する</strong>ことをおすすめします。制度の対象になるかどうかの感触は、管轄法務局の事前相談で確認できます。</p>"),
        ],
        "faqs": [
            ("相続土地国庫帰属制度に申請の期限はありますか？", "<p>相続放棄のような明確な期限は定められていません。相続や遺贈で土地を取得した人であれば、制度開始前（2023年4月27日より前）に相続した土地についても申請できるとされています。ただし要件を満たす必要があるため、早めに法務局へ相談すると安心です。</p>"),
            ("負担金はいくらかかりますか？", "<p>負担金は土地の10年分の管理費相当額として算定され、多くの宅地・農地などでは1筆あたり20万円が基準とされています。ただし、市街化区域内の宅地や農地などは面積に応じて増額される場合があります。これとは別に、申請時に土地一筆あたり1万4,000円の審査手数料が必要です。最新の金額は法務局でご確認ください。</p>"),
            ("建物が建っている土地でも申請できますか？", "<p>建物がある土地はそのままでは申請できず、却下の対象とされています。利用するには建物を解体して更地にする必要があります。解体費用と負担金の合計が見合うかどうかを含め、売却など他の方法と比較して検討することをおすすめします。</p>"),
        ],
    },
    {
        "slug": "quasi-final-tax-return",
        "title": "準確定申告とは｜亡くなった人の所得税を4ヶ月以内に申告する方法",
        "h1": "準確定申告とは｜亡くなった人の所得税を相続人が申告する手続き",
        "desc": "準確定申告とは、亡くなった方の所得税を相続人が代わりに申告・納付する手続きです。期限は相続開始を知った日の翌日から4ヶ月以内。対象者・必要書類・医療費控除など実務のポイントをわかりやすく解説します。",
        "keywords": "準確定申告,準確定申告 期限,準確定申告 必要書類,4ヶ月以内,所得税 死亡,確定申告 相続人",
        "lead": "<strong>準確定申告</strong>とは、亡くなった方のその年の所得税を、相続人が代わりに申告・納付する手続きです。通常の確定申告と異なり期限が短く、相続開始を知った日の翌日から4ヶ月以内とされているため、早めの準備が大切です。",
        "sections": [
            ("準確定申告とは｜通常の確定申告との違い", "<p>準確定申告とは、年の途中で亡くなった方について、その年の1月1日から死亡日までの所得を集計し、相続人などが代わりに所得税の申告・納付を行う手続きです。所得税法第124条・第125条に根拠があり、確定申告をすべき人が亡くなった場合に必要となります。</p>\n<p>通常の確定申告との主な違いは次のとおりです。</p>\n<ul>\n<li><strong>申告する人</strong>：本人ではなく<strong>相続人(または包括受遺者)</strong>が行います。</li>\n<li><strong>対象期間</strong>：その年の1月1日から<strong>死亡日まで</strong>の所得が対象です。</li>\n<li><strong>期限</strong>：相続の開始があったことを知った日の翌日から<strong>4ヶ月以内</strong>です。</li>\n<li><strong>添付書類</strong>：相続人が複数いる場合は「死亡した者の所得税及び復興特別所得税の確定申告書付表」を添付します。</li>\n</ul>\n<p>なお、亡くなった年の前年分の確定申告がまだ済んでいない時期(例：1月1日から3月15日までの間)に亡くなった場合は、前年分と本年分の<strong>2年分</strong>の準確定申告が必要になる場合があります。</p>"),
            ("申告が必要な人・不要な人", "<p>準確定申告が必要かどうかは、亡くなった方が「もし生きていれば確定申告をする必要があったか」で判断します。一般に、次のようなケースでは申告が必要とされます。</p>\n<ul>\n<li>個人事業主・フリーランスだった</li>\n<li>給与収入が一定額(目安として2,000万円)を超えていた</li>\n<li>2か所以上から給与を受けていた</li>\n<li>公的年金等の収入が一定額を超えていた(年金収入のみであれば、目安として400万円以下かつ他の所得が20万円以下なら申告不要とされる場合があります)</li>\n<li>不動産所得・事業所得・譲渡所得などがあった</li>\n<li>多額の医療費を支払っており、医療費控除で還付を受けられる</li>\n</ul>\n<p>一方で、給与や年金のみで源泉徴収だけで課税が完結している場合などは、申告が不要なこともあります。ただし、源泉徴収された税金が納め過ぎになっているケースでは、申告(<strong>還付申告</strong>)をすることで税金が戻る場合があります。判断に迷うときは、税理士や所轄の税務署に確認すると安心です。</p>"),
            ("期限と納付・還付の流れ", "<p>準確定申告の期限は、<strong>相続の開始があったことを知った日の翌日から4ヶ月以内</strong>です。通常の確定申告のように「翌年3月15日まで」ではない点に注意が必要です。たとえば6月15日に亡くなったことを知った場合、原則として同年10月15日が期限の目安となります。</p>\n<p>主な流れは次のとおりです。</p>\n<ul>\n<li><strong>1. 所得の集計</strong>：1月1日から死亡日までの収入・経費・控除を整理します。</li>\n<li><strong>2. 申告書の作成</strong>：通常の確定申告書を使い、相続人が連署して作成します(付表を添付)。</li>\n<li><strong>3. 提出先</strong>：亡くなった方の死亡当時の納税地(住所地)を所轄する税務署へ提出します。</li>\n<li><strong>4. 納付・還付</strong>：納税額がある場合は各相続人が相続分に応じて納め、還付の場合は相続分に応じて受け取ります。</li>\n</ul>\n<p>期限を過ぎると、無申告加算税や延滞税が課される場合があります。相続放棄や遺産分割など他の手続きと並行することも多いため、早めの着手をおすすめします。</p>"),
            ("控除の取り扱いで間違えやすいポイント", "<p>準確定申告では、各種控除の対象期間や金額の考え方が通常の確定申告と異なる点があり、間違えやすいので注意が必要です。</p>\n<ul>\n<li><strong>医療費控除</strong>：死亡日までに本人が支払った医療費が対象です。死亡後に相続人が支払った入院費などは、原則として準確定申告の医療費控除には含められません(相続税の債務控除の対象になる場合があります)。</li>\n<li><strong>社会保険料・生命保険料控除</strong>：死亡日までに本人が支払った分が対象となります。</li>\n<li><strong>配偶者控除・扶養控除</strong>：控除対象となるかどうかは、原則として<strong>死亡日の現況</strong>で判定します。</li>\n<li><strong>基礎控除</strong>：月割りではなく、要件を満たせば通常どおり適用されます。</li>\n</ul>\n<p>これらの取り扱いは法改正によって変わることがあります。税率・控除額・期限などの<strong>最新の要件は、必ず国税庁や所轄の税務署、税理士などの専門家でご確認ください</strong>。</p>"),
            ("申告に必要な書類と進め方", "<p>準確定申告をスムーズに進めるために、早い段階で必要書類を集めておくとよいでしょう。一般的に必要とされる書類の例は次のとおりです。</p>\n<ul>\n<li>確定申告書(死亡した方のもの)</li>\n<li>死亡した者の所得税及び復興特別所得税の確定申告書付表(相続人が複数の場合)</li>\n<li>亡くなった方の源泉徴収票・年金の源泉徴収票</li>\n<li>事業所得・不動産所得がある場合は収支内訳書や帳簿類</li>\n<li>医療費の領収書、各種保険料の控除証明書</li>\n<li>相続人のマイナンバーがわかるものや本人確認書類</li>\n</ul>\n<p>申告書は書面のほか、一定の要件を満たせば<strong>e-Tax(電子申告)</strong>で提出できる場合もあります。事業を引き継ぐ場合は、青色申告の承認申請など別の手続きが必要になることもあります。相続税の申告(相続開始を知った日の翌日から10ヶ月以内)とも関係するため、全体のスケジュールを見ながら、必要に応じて税理士に相談しながら進めると安心です。</p>"),
        ],
        "faqs": [
            ("準確定申告をしないとどうなりますか？", "申告・納税が必要なのに行わなかった場合、無申告加算税や延滞税が課される場合があります。一方、本来は税金が還付されるケースで申告をしないと、戻るはずの税金を受け取れないことになります。必要かどうか判断に迷う場合は、所轄の税務署や税理士に確認することをおすすめします。"),
            ("相続人が複数いる場合は誰が申告しますか？", "原則として相続人全員が連署して1通の準確定申告書を提出します。その際、「死亡した者の所得税及び復興特別所得税の確定申告書付表」に各相続人の情報や相続分を記載します。なお、他の相続人の氏名を付記すれば各人が個別に提出することも可能とされていますが、その場合は申告内容を他の相続人へ通知する必要があります。"),
            ("準確定申告と相続税の申告は何が違いますか？", "準確定申告は、亡くなった方の生前の「所得税」を精算する手続きで、期限は相続開始を知った日の翌日から4ヶ月以内です。一方、相続税の申告は、相続した財産にかかる「相続税」の手続きで、期限は同10ヶ月以内とされています。対象となる税金も期限も異なるため、それぞれ別に対応が必要です。"),
        ],
    },
    {
        "slug": "car-inheritance",
        "title": "相続した車の名義変更｜必要書類と手続きの流れを徹底解説",
        "h1": "相続した車の名義変更｜必要書類と手続きの流れ",
        "desc": "相続した車の名義変更（移転登録）の手順を解説。普通車・軽自動車別の必要書類、遺産分割協議書のひな型ポイント、期限や費用、売却・廃車時の注意点まで、実務に沿ってわかりやすくまとめました。",
        "keywords": "相続 車 名義変更,自動車 相続 手続き,移転登録 相続,遺産分割協議書 車,軽自動車 相続 名義変更,相続 車 必要書類",
        "lead": "<strong>相続した車の名義変更</strong>は、放置すると売却も廃車もできず、思わぬトラブルにつながることがあります。ここでは普通車・軽自動車それぞれの必要書類と手続きの流れを、実務に沿って整理します。",
        "sections": [
            ("車の名義変更は「相続」による移転登録になる", "<p>故人（被相続人）名義の自動車は、そのまま乗り続けたり売却したりすることはできず、まず相続人へ名義を移す<strong>移転登録</strong>（軽自動車の場合は「自動車検査証記入申請」）が必要です。これは売買による名義変更と異なり、相続を原因とする手続きとなります。</p>\n<p>自動車は<strong>動産</strong>ですが、登録自動車（普通車）は道路運送車両法に基づく登録が権利関係の公示手段とされており、相続が発生した時点で法律上は相続人の共有財産になります（民法第898条・第899条）。実際に誰が引き継ぐかは、遺言書がなければ<strong>遺産分割協議</strong>で決めるのが一般的です。</p>\n<p>なお、相続登記（不動産）のような明確な義務化・罰則は自動車にはありませんが、名義をそのままにしておくと、売却・廃車・任意保険の引き継ぎなどで支障が出るため、早めの手続きが望ましいとされます。</p>"),
            ("まず確認すること（車検証・相続人・分け方）", "<p>手続きの前に、以下を確認しておくとスムーズです。</p>\n<ul>\n<li><strong>車検証で「登録車（普通車）か軽自動車か」を確認</strong>：手続き窓口（運輸支局か軽自動車検査協会）が変わります。</li>\n<li><strong>所有者欄の名義</strong>：ローン中などで所有者が信販会社・ディーラーになっている場合、相続手続きではなく所有者側の手続きが必要になることがあります。</li>\n<li><strong>相続人の範囲</strong>：戸籍をたどり、法定相続人を確定します。</li>\n<li><strong>誰が引き継ぐか</strong>：1人が単独で相続するのか、いったん共有にするのかを決めます。</li>\n</ul>\n<p>車を相続する人が決まったら、その人を<strong>新所有者</strong>として手続きを進めます。価値の低い車については簡易な扱いが認められる場合もありますが、原則は次に挙げる書類をそろえます。</p>"),
            ("必要書類（普通車・軽自動車の違い）", "<p>普通車（登録車）と軽自動車では、必要書類が大きく異なります。代表的なものを整理します。</p>\n<table>\n<tr><th>書類</th><th>普通車（運輸支局）</th><th>軽自動車（軽自動車検査協会）</th></tr>\n<tr><td>車検証（自動車検査証）</td><td>必要</td><td>必要</td></tr>\n<tr><td>故人の死亡が分かる戸籍（除籍）謄本</td><td>必要</td><td>必要</td></tr>\n<tr><td>相続人全員が分かる戸籍謄本</td><td>必要</td><td>原則不要(注)</td></tr>\n<tr><td>遺産分割協議書（または遺言書）</td><td>必要</td><td>原則不要(注)</td></tr>\n<tr><td>新所有者の印鑑証明書・実印</td><td>必要</td><td>不要(認印で可)</td></tr>\n<tr><td>申請書・手数料納付書・税申告書</td><td>必要</td><td>必要</td></tr>\n<tr><td>車庫証明（保管場所の変更がある場合）</td><td>必要なことが多い</td><td>地域により必要</td></tr>\n</table>\n<p>(注)軽自動車は手続きが簡素で、原則として遺産分割協議書や印鑑証明書は不要とされ、申請書に新所有者・旧所有者の情報を記載する方式が一般的です。ただし取扱いは窓口で異なる場合があるため、事前確認をおすすめします。</p>\n<p>普通車では、相続人が複数いる場合に<strong>遺産分割協議書</strong>へ相続人全員の署名・実印が原則必要です。車の価額が一定額以下のときは、代表者が作成する「遺産分割協議成立申立書」など簡略な書面で足りる取扱いもあります。</p>"),
            ("手続きの流れと費用・期限", "<p>普通車を例にした一般的な流れは次のとおりです。</p>\n<ul>\n<li><strong>1. 書類の収集</strong>：戸籍・印鑑証明書・車検証などをそろえる。</li>\n<li><strong>2. 遺産分割協議</strong>：誰が車を相続するか決め、協議書を作成。</li>\n<li><strong>3. 申請書類の作成</strong>：移転登録申請書などを記入。</li>\n<li><strong>4. 運輸支局で申請</strong>：管轄の運輸支局（軽は軽自動車検査協会）で手続き。ナンバー変更を伴う場合は車の持ち込みが必要。</li>\n<li><strong>5. 新しい車検証の交付</strong>：あわせて任意保険の名義も変更します。</li>\n</ul>\n<p>費用は、移転登録の登録手数料（数百円程度）に加え、ナンバープレート代、車庫証明の取得費、行政書士へ依頼する場合の報酬などがかかります。明確な期限の定めはありませんが、相続税の申告が必要な場合は、相続開始を知った日の翌日から<strong>10か月以内</strong>が申告期限とされ（相続税法第27条）、車も相続財産として評価額に含めて計算します。</p>\n<p>具体的な必要書類・手数料・取扱いは変更されることがあるため、<strong>最新の要件は国土交通省（運輸支局）・軽自動車検査協会・国税庁、または行政書士・税理士などの専門家でご確認ください。</strong></p>"),
            ("売却・廃車したいときと注意点", "<p>相続した車をすぐ売却・廃車したい場合でも、原則として<strong>いったん相続人名義に変更してから</strong>でないと処分できません。実務では、買取業者が相続人名義への変更と売買を同時に代行してくれるケースもあります。</p>\n<p>注意したいのは次の点です。</p>\n<ul>\n<li><strong>共有のまま放置しない</strong>：相続人全員の共有状態だと、後で1人でも協力が得られないと売却できなくなる恐れがあります。</li>\n<li><strong>自動車税の扱い</strong>：4月1日時点の所有者に課税されるため、年度をまたぐ前に手続きを進めると無用な負担を避けやすいです。</li>\n<li><strong>任意保険・自賠責</strong>：名義変更とあわせて見直し、無保険運転を避けます。</li>\n<li><strong>ローン残債</strong>：所有権留保が付いている車は、完済・名義移転の手続きが別途必要です。</li>\n</ul>\n<p>手続きが煩雑に感じる場合は、行政書士に代行を依頼することもできます。相続人の人数が多い、戸籍が複雑などのケースでは、早めに専門家へ相談すると安心です。</p>"),
        ],
        "faqs": [
            ("相続した車の名義変更に期限はありますか？", "自動車の名義変更（移転登録）そのものに、相続登記のような明確な法定期限や罰則は設けられていないとされています。ただし、名義を放置すると売却・廃車・保険の引き継ぎができず、自動車税の扱いでも不利になりがちです。なお相続税の申告が必要な場合は、相続開始を知った日の翌日から10か月以内（相続税法第27条）が期限となるため、車もその財産評価に含めて早めに手続きするのが安心です。"),
            ("軽自動車の相続手続きは普通車より簡単ですか？", "一般に軽自動車のほうが簡素とされ、原則として遺産分割協議書や印鑑証明書は不要で、申請書に新旧所有者の情報を記載する方式が用いられることが多いです。窓口は軽自動車検査協会になります。ただし取扱いは地域や事案で異なる場合があるため、必要書類は事前に管轄の窓口へご確認ください。"),
            ("遺産分割協議書がなくても名義変更できますか？", "普通車で相続人が複数いる場合は、原則として相続人全員が署名・実印を押した遺産分割協議書（または遺言書）が必要です。ただし車の査定価額が一定額以下のときは、代表相続人が作成する「遺産分割協議成立申立書」など簡略な書面で手続きできる取扱いもあります。利用できるかは価額や窓口の運用によるため、運輸支局や専門家にご確認ください。"),
        ],
    },
    {
        "slug": "single-person-endlife",
        "title": "おひとりさまの終活・相続｜身寄りがない場合の備えと手続き完全ガイド",
        "h1": "おひとりさまの終活と相続｜身寄りがない場合の備え",
        "desc": "おひとりさまの終活・相続を専門的に解説。身寄りがない場合に必要な遺言・死後事務委任・財産管理の備え、相続人がいないときの財産の行方や相続税の注意点まで、実務的にわかりやすくまとめました。",
        "keywords": "おひとりさま 終活,身寄りがない 相続,死後事務委任契約,遺言書,任意後見,相続人不存在",
        "lead": "<strong>おひとりさまの終活・相続</strong>では、判断能力の低下や死後の手続きを託せる家族がいないことを前提に、生前のうちから契約や書面で備えておくことが何より重要です。本記事では身寄りがない方が安心して暮らし、最期を迎えるための実務的なポイントを整理します。",
        "sections": [
            ("おひとりさまが備えるべき3つの局面", "<p>おひとりさまの備えは、大きく分けて<strong>「判断能力があるうちの生前」「判断能力が低下したとき」「亡くなった後」</strong>の3つの局面に分かれます。家族がいれば自然に担ってもらえる役割を、自分で誰かに託す仕組みをつくっておく必要があります。</p>\n<ul>\n<li><strong>生前(元気なうち)</strong>：財産の把握、医療・介護の意思表示、見守りの体制づくり</li>\n<li><strong>判断能力の低下時</strong>：財産管理や契約行為を代わりに行う後見の仕組み</li>\n<li><strong>死後</strong>：葬儀・納骨、各種解約、相続財産の承継</li>\n</ul>\n<p>これらは一つの契約や書面だけではカバーできず、目的ごとに複数の制度を組み合わせるのが一般的です。それぞれが対応する「タイミング」が異なる点を意識すると、漏れなく準備しやすくなります。</p>"),
            ("判断能力が低下したときの備え（任意後見・財産管理）", "<p>認知症などで判断能力が低下すると、預貯金の引き出しや施設の契約が自分でできなくなる場合があります。元気なうちに、信頼できる人や専門家(弁護士・司法書士など)と契約しておくことで備えられます。</p>\n<ul>\n<li><strong>任意後見契約</strong>：判断能力が低下した後の支援内容と後見人をあらかじめ決めておく契約です。「任意後見契約に関する法律」に基づき、<strong>公正証書で作成</strong>することが必須とされています。実際に支援が始まるのは、家庭裁判所が任意後見監督人を選任した時点からです。</li>\n<li><strong>財産管理等委任契約(任意代理)</strong>：判断能力はあるが体が不自由などの場合に、財産管理や手続きを委任する契約です。任意後見契約とセットで結び、移行型として備えるケースもあります。</li>\n<li><strong>見守り契約</strong>：定期的な連絡や訪問で状況を確認してもらう契約で、支援開始のタイミングを見逃さない役割を果たします。</li>\n</ul>\n<p>なお、契約を結ばないまま判断能力が低下した場合は、家庭裁判所が後見人等を選ぶ<strong>法定後見</strong>(民法に基づく成年後見制度)を利用することになります。自分で後見人を選びたい場合は、元気なうちの任意後見契約が有効とされます。</p>"),
            ("亡くなった後の手続きを託す「死後事務委任契約」", "<p>遺言は財産の承継を定めるものですが、<strong>葬儀・納骨・各種解約・遺品整理といった「事務手続き」は遺言では十分にカバーできない</strong>とされています。そこで活用されるのが<strong>死後事務委任契約</strong>です。これは民法の委任(民法643条以下)を根拠とし、自分の死後に行ってほしい事務を生前に第三者へ委任しておく契約です。</p>\n<p>死後事務委任契約で定めておくことの多い項目は次のとおりです。</p>\n<ul>\n<li>葬儀・火葬・納骨・埋葬に関する手続き</li>\n<li>病院・施設の精算、退去・明渡し</li>\n<li>公共料金・携帯電話・サブスクリプションなどの解約</li>\n<li>行政への届出(年金・健康保険など)</li>\n<li>SNSやデジタルデータの整理(いわゆるデジタル遺品)</li>\n</ul>\n<p>契約相手は親族のほか、弁護士・司法書士・行政書士などの専門家やNPO法人が担うこともあります。預託金の管理方法や、契約相手が先に亡くなった場合の取り扱いなど、トラブルを避けるための条件をあらかじめ確認しておくことが大切です。</p>"),
            ("遺言書で財産の行き先を決めておく", "<p>身寄りがない方こそ、<strong>遺言書</strong>で財産の承継先を明確にしておく意義が大きいといえます。法定相続人がいない、あるいは疎遠な親族しかいない場合でも、遺言があれば、お世話になった人や団体(寄付など)に財産を遺すことができます。</p>\n<p>主な遺言の方式は次の2つです。</p>\n<table>\n<tr><th>方式</th><th>特徴</th></tr>\n<tr><td>自筆証書遺言</td><td>自分で書く方式。費用を抑えられるが、形式不備で無効になるリスクがある。法務局の<strong>自筆証書遺言書保管制度</strong>(2020年7月開始)を使うと、紛失・改ざんを防ぎ、家庭裁判所の検認も不要になるとされる。</td></tr>\n<tr><td>公正証書遺言</td><td>公証人が関与して作成する方式。証人2人が必要だが、形式不備のリスクが低く、原本が公証役場に保管されるため安全性が高いとされる。</td></tr>\n</table>\n<p>遺言で財産を渡す相手を決める場合、確実に手続きを進めてもらうために<strong>遺言執行者</strong>を指定しておくと安心です。おひとりさまの場合、遺言・死後事務委任・任意後見の担い手を専門家に一本化し、連携させておく方法もよく用いられます。</p>"),
            ("相続人がいない場合、財産はどうなるか", "<p>法定相続人(配偶者・子・親・兄弟姉妹など)が誰もいない、あるいは全員が相続放棄した場合、その財産は<strong>「相続人不存在」</strong>として扱われ、民法951条以降の手続きにより清算されます。流れの概要は次のとおりです。</p>\n<ul>\n<li>家庭裁判所が利害関係人などの申立てにより<strong>相続財産清算人</strong>(民法改正により従来の「相続財産管理人」から名称変更)を選任する</li>\n<li>債権者や受遺者へ支払いを行い、財産を清算する</li>\n<li><strong>特別縁故者</strong>(療養看護に努めた人など)から申立てがあれば、家庭裁判所が認めた範囲で財産が分与される場合がある(民法958条の2)</li>\n<li>それでも残った財産は、最終的に<strong>国庫に帰属</strong>する(民法959条)</li>\n</ul>\n<p>このように、何も準備しなければ財産は国庫に入る可能性があります。特定の人や団体に確実に遺したい場合は、前述の遺言書の作成が不可欠です。なお、相続税の基礎控除は「3,000万円+600万円×法定相続人の数」とされ、法定相続人がいない場合は基礎控除が3,000万円となるため、財産規模によっては課税の有無に注意が必要です。<strong>税率・控除額・各種期限などの最新の要件は、国税庁・法務局や、税理士・弁護士などの専門家に必ずご確認ください。</strong></p>"),
            ("元気なうちに進めたい具体的な準備の手順", "<p>おひとりさまの終活は、思い立ったときから少しずつ進めるのが現実的です。次のステップで整理してみましょう。</p>\n<ul>\n<li><strong>1. 財産・契約の棚卸し</strong>：預貯金・不動産・保険・証券・サブスク・借入などを一覧化する(エンディングノートの活用が便利)</li>\n<li><strong>2. 緊急連絡先・意思表示の明確化</strong>：入院時の連絡先、延命治療の希望(リビングウィル)などを書き残す</li>\n<li><strong>3. 専門家への相談</strong>：任意後見・死後事務委任・遺言の組み合わせを設計する</li>\n<li><strong>4. 書面・契約の作成</strong>：公正証書での作成や法務局保管制度の利用を検討する</li>\n<li><strong>5. 定期的な見直し</strong>：財産状況や人間関係の変化に応じて内容を更新する</li>\n</ul>\n<p>エンディングノートには法的な効力はないとされますが、自分の希望や情報をまとめておくことで、支援する人の負担を大きく減らせます。法的効力を持たせたい事項は、遺言書や各種契約として別途整えておくとよいでしょう。</p>"),
        ],
        "faqs": [
            ("おひとりさまの終活は何から始めればよいですか？", "まずは財産や契約内容の棚卸しから始めるのがおすすめです。預貯金・不動産・保険・サブスクなどを一覧化し、緊急連絡先や医療の希望を書き残します。そのうえで、任意後見・死後事務委任・遺言をどう組み合わせるか、弁護士や司法書士などの専門家に相談しながら設計していくと進めやすいとされます。"),
            ("遺言書だけ用意しておけば十分ですか？", "遺言書は財産の承継先を定めるものですが、葬儀・納骨・各種解約といった死後の事務手続きや、判断能力が低下したときの財産管理まではカバーできないとされています。そのため、遺言書に加えて「死後事務委任契約」「任意後見契約」などを組み合わせて備えるのが一般的です。"),
            ("身寄りがなく相続人もいない場合、財産は最終的にどうなりますか？", "相続人不存在として家庭裁判所が相続財産清算人を選任し、債権の清算や特別縁故者への分与(認められた場合)を経て、残った財産は最終的に国庫に帰属するとされています(民法959条)。特定の人や団体に遺したい場合は、遺言書を作成しておくことが不可欠です。"),
        ],
    },
    {
        "slug": "amended-tax-return",
        "title": "相続税の修正申告と更正の請求｜申告漏れ・払いすぎの正しい直し方",
        "h1": "相続税の修正申告と更正の請求｜申告後の是正手続き",
        "desc": "相続税の申告後に財産の漏れが見つかったときの修正申告、払いすぎを取り戻す更正の請求について、期限・必要書類・加算税や延滞税の扱いまで、相続実務の観点からわかりやすく解説します。",
        "keywords": "相続税 修正申告,更正の請求,申告漏れ,過大申告,加算税,延滞税",
        "lead": "<strong>相続税の修正申告と更正の請求</strong>は、いったん提出した相続税の申告内容に誤りが見つかったときに、税額を正しく直すための手続きです。財産の計上漏れで税額が少なかった場合は「修正申告」、逆に払いすぎていた場合は「更正の請求」と、方向によって手続きが分かれます。",
        "sections": [
            ("修正申告と更正の請求の違い", "<p>相続税の当初申告(期限内申告)の後で内容に誤りが判明した場合、是正の手続きは大きく2つに分かれます。どちらに当たるかは「<strong>税額が増えるか、減るか</strong>」で決まります。</p>\n<ul>\n<li><strong>修正申告</strong>:申告した税額が本来より<strong>少なかった</strong>とき(納め足りない場合)に、自主的に不足分を申告し直す手続きです(国税通則法第19条)。</li>\n<li><strong>更正の請求</strong>:申告した税額が本来より<strong>多すぎた</strong>とき(払いすぎ)に、税務署に「税額を減らしてください」と請求する手続きです(国税通則法第23条)。請求が認められると還付されます。</li>\n</ul>\n<p>なお、納税者側からの手続きとは別に、税務署が職権で税額を直すことを「<strong>更正</strong>」「<strong>決定</strong>」といいます。税務調査の結果として更正処分を受けるケースもあり、その場合は加算税の負担が重くなる傾向があります。</p>\n<table>\n<tr><th>状況</th><th>手続き</th><th>結果</th></tr>\n<tr><td>税額が不足(申告漏れ)</td><td>修正申告</td><td>追加で納税</td></tr>\n<tr><td>税額が過大(払いすぎ)</td><td>更正の請求</td><td>還付される</td></tr>\n</table>"),
            ("修正申告が必要になる典型例と進め方", "<p>修正申告は、当初の申告後に<strong>財産の計上漏れや評価の誤り</strong>が見つかったときに行います。実務でよくあるのは次のようなケースです。</p>\n<ul>\n<li>申告後に被相続人名義の<strong>別口座や保険、貸金庫の財産</strong>が見つかった</li>\n<li>名義預金(家族名義だが実質は被相続人の財産)が後から判明した</li>\n<li>土地の評価や非上場株式の評価に誤りがあり、本来より低く計上していた</li>\n<li>遺産分割が確定し、特例適用後の税額が当初より増えた</li>\n</ul>\n<p>進め方としては、相続税の修正申告書を作成し、増えた分の税額を<strong>納付と同時または速やかに</strong>納めます。税務署の調査による指摘を受ける前に<strong>自主的に</strong>修正申告をすれば、過少申告加算税がかからない、または軽減される場合があります。一方、調査の通知後や指摘後の修正は加算税の対象となるのが原則です。</p>\n<p>誤りに気づいたら、放置せず早めに対応することがペナルティを抑えるポイントです。</p>"),
            ("更正の請求ができる場合と期限", "<p>更正の請求は「払いすぎ」を取り戻す手続きで、<strong>期限管理が特に重要</strong>です。大きく次の2系統があります。</p>\n<ul>\n<li><strong>通常の更正の請求</strong>:計算誤りなどで税額が過大だった場合。原則として<strong>法定申告期限から5年以内</strong>に請求します(国税通則法第23条第1項)。</li>\n<li><strong>後発的事由による更正の請求</strong>:申告時には予測できなかった事情が後から生じた場合。相続税には固有の特則があり、たとえば<strong>未分割だった遺産が分割され</strong>、配偶者の税額軽減や小規模宅地等の特例が適用できるようになった、新たな相続人の存在が判明した、遺留分侵害額が確定した、といった事由が生じてから<strong>原則4か月以内</strong>に請求します(相続税法第32条)。</li>\n</ul>\n<p>具体例として、申告期限までに遺産分割が間に合わず、いったん特例を使わずに高い税額で申告したケースがあります。その後に分割が成立して配偶者の税額軽減を適用できるようになれば、更正の請求で払いすぎた税額の還付を受けられる可能性があります(申告時に「申告期限後3年以内の分割見込書」の提出が前提となります)。</p>"),
            ("加算税・延滞税など追加の負担", "<p>修正申告で税額が増える場合、本税のほかに以下のような<strong>附帯税</strong>がかかることがあります。負担の重さは「<strong>いつ・どのきっかけで</strong>是正したか」で変わります。</p>\n<ul>\n<li><strong>過少申告加算税</strong>:税務調査の指摘などで修正した場合に課されます。自主的な修正申告では原則かかりませんが、調査通知後はかかる場合があります。</li>\n<li><strong>無申告加算税</strong>:そもそも期限内に申告していなかった場合に課されます。</li>\n<li><strong>重加算税</strong>:財産を意図的に隠したり、仮装・隠蔽があった場合に課される最も重いペナルティです。</li>\n<li><strong>延滞税</strong>:法定納期限の翌日から実際の納付日までの期間に応じてかかる利息的な負担です。</li>\n</ul>\n<p>これらの<strong>税率や割合は年度や状況によって異なり、近年も見直しが行われています</strong>。実際の負担額は事案により大きく変わるため、具体的な金額は試算が必要です。最新の要件・税率・控除額・期限などは、必ず<strong>国税庁の公表資料や税務署、税理士などの専門家でご確認ください</strong>。</p>"),
            ("手続きで迷わないための実務ポイント", "<p>修正申告・更正の請求は書類の準備と期限管理がカギになります。実務で押さえておきたい点を整理します。</p>\n<ul>\n<li><strong>根拠資料をそろえる</strong>:更正の請求では、なぜ税額が過大なのかを示す<strong>遺産分割協議書、評価資料、戸籍などの添付書類</strong>が必要です。資料が不十分だと認められないことがあります。</li>\n<li><strong>期限を最優先で確認</strong>:更正の請求は「5年」または後発的事由から「4か月」など期限が厳格です。1日でも過ぎると原則として請求できません。</li>\n<li><strong>誤りに気づいたら早めに動く</strong>:修正申告は調査前の自主申告であるほどペナルティが軽くなる傾向があります。</li>\n<li><strong>専門家への相談を検討</strong>:評価や特例の適用は判断が難しく、土地評価や名義預金が絡む場合は税理士に相談すると安全です。</li>\n</ul>\n<p>「直すと損をする」と感じて放置すると、かえって加算税や延滞税で負担が増えることがあります。逆に、払いすぎに気づかないまま期限を過ぎると、戻るはずのお金が戻らなくなります。どちらの方向でも、<strong>早めの確認と行動</strong>が結果的に最も負担を小さくします。</p>"),
        ],
        "faqs": [
            ("修正申告をすると必ず加算税がかかりますか?", "必ずかかるわけではありません。税務署の調査による指摘を受ける前に、自主的に修正申告をした場合は、過少申告加算税がかからない、または軽減されるのが原則です。一方で、調査の通知後や指摘後に修正した場合は加算税の対象となります。延滞税は納付が遅れた期間に応じて別途かかる点に注意してください。具体的な取り扱いは状況により異なるため、税務署や税理士にご確認ください。"),
            ("遺産分割が後からまとまった場合、払いすぎた相続税は戻りますか?", "戻る可能性があります。申告期限までに分割が間に合わず、配偶者の税額軽減や小規模宅地等の特例を使わずに申告していた場合、その後に分割が成立すれば、相続税法第32条に基づく更正の請求(原則として事由が生じてから4か月以内)により還付を受けられる場合があります。ただし当初申告時に「申告期限後3年以内の分割見込書」を提出していることが前提となるため、詳細は専門家にご確認ください。"),
            ("更正の請求の期限が過ぎてしまったら、もう払いすぎは取り戻せませんか?", "原則として、期限(通常は法定申告期限から5年、後発的事由は事由発生から原則4か月など)を過ぎると更正の請求はできなくなります。期限管理が非常に重要です。ただし事案によって起算日や適用される特則の判断が分かれることもあるため、期限が近い、または過ぎたかもしれないと感じた場合は、あきらめる前に早めに税務署や税理士へ相談することをおすすめします。"),
        ],
    },
    {
        "slug": "division-mediation",
        "title": "遺産分割調停の流れと費用｜協議がまとまらない時の家庭裁判所手続き",
        "h1": "遺産分割調停の流れ｜協議がまとまらない時の家庭裁判所手続き",
        "desc": "遺産分割協議がまとまらないときの遺産分割調停について、申立先や必要書類、当日の進め方から不成立後の審判までの流れを、相続実務の視点でわかりやすく解説します。",
        "keywords": "遺産分割調停,遺産分割協議,家庭裁判所,遺産分割審判,相続,寄与分",
        "lead": "<strong>遺産分割調停</strong>は、相続人どうしの話し合い（遺産分割協議）がまとまらないときに、家庭裁判所の調停委員を間に入れて解決を図る手続きです。「誰が何を相続するか決まらない」「連絡が取れない相続人がいる」といった場合の現実的な解決策として知られています。本記事では申立てから成立・不成立後までの全体像を、実務に沿って解説します。",
        "sections": [
            ("遺産分割調停とは｜協議・調停・審判の関係", "<p>相続が起きると、遺言がない場合は相続人全員で<strong>遺産分割協議</strong>を行い、誰がどの財産を取得するかを決めます。協議は全員の合意が必要で、一人でも反対すると成立しません。話し合いがまとまらない、あるいは相手が協議に応じない場合に利用するのが家庭裁判所の手続きです。</p>\n<p>遺産分割をめぐる家庭裁判所の手続きには、大きく次の段階があります。</p>\n<ul>\n<li><strong>遺産分割協議</strong>：相続人同士の任意の話し合い（裁判所は関与しない）</li>\n<li><strong>遺産分割調停</strong>：調停委員を介して話し合いで合意を目指す手続き</li>\n<li><strong>遺産分割審判</strong>：調停が不成立の場合に、裁判官が法定相続分等を基準に判断する手続き</li>\n</ul>\n<p>遺産分割は、いきなり審判ではなく、まず調停から行うのが原則です（家事事件手続法の調停前置の運用）。調停はあくまで話し合いの場であり、合意できなければ自動的に審判へ移行する点が特徴です。</p>"),
            ("申立ての方法｜申立先・費用・必要書類", "<p>遺産分割調停は、<strong>相手方（他の相続人）の住所地を管轄する家庭裁判所</strong>、または当事者が合意で定めた家庭裁判所に申し立てます。相手方が複数いる場合は、そのうちの誰か一人の住所地の家庭裁判所でも申立て可能とされています。</p>\n<p>申立てにかかる費用や主な必要書類は次のとおりです。具体的な金額や様式は事案により変わるため、最新の要件は管轄の家庭裁判所や専門家でご確認ください。</p>\n<ul>\n<li><strong>収入印紙</strong>：被相続人1人につき1,200円分</li>\n<li><strong>連絡用の郵便切手</strong>（金額は裁判所により異なります）</li>\n<li>被相続人の出生から死亡までの<strong>戸籍（除籍・改製原戸籍）</strong>一式</li>\n<li>相続人全員の戸籍謄本・住民票</li>\n<li>遺産に関する資料（不動産登記事項証明書、固定資産評価証明書、預貯金の残高証明書など）</li>\n<li>遺産目録・申立書</li>\n</ul>\n<p>戸籍の収集には時間がかかることが多く、法務局の<strong>法定相続情報証明制度</strong>を利用すると手続きが簡便になる場合があります。</p>"),
            ("調停当日の流れ｜話し合いはどう進むか", "<p>調停は、通常2名の<strong>調停委員</strong>（裁判官または調停官を含む調停委員会が構成されます）が当事者双方から事情を聴く形で進みます。多くの場合、申立人と相手方は別々の待合室に分かれ、交互に調停室へ呼ばれて意見を述べます。直接顔を合わせずに話を進められるため、感情的な対立を避けやすいとされます。</p>\n<p>調停では、主に次のような点が話し合われます。</p>\n<ul>\n<li>相続人の範囲（誰が相続人か）の確認</li>\n<li>遺産の範囲と評価額（不動産・預貯金・株式など）</li>\n<li><strong>特別受益</strong>（生前贈与など）や<strong>寄与分</strong>（介護・事業への貢献など）の有無</li>\n<li>各相続人の取得分・分割方法（現物分割・代償分割・換価分割など）</li>\n</ul>\n<p>1回の調停では終わらないことが一般的で、おおむね1〜2か月に1回のペースで複数回（半年〜1年以上に及ぶこともあります）行われます。話し合いがまとまると<strong>調停調書</strong>が作成され、これは確定判決と同一の効力を持ち、相手が応じない場合は強制執行の根拠にもなります。</p>"),
            ("調停が不成立になったら｜審判への移行", "<p>当事者が合意に至らない場合、調停は<strong>不成立（調停不成立）</strong>となります。遺産分割の場合、調停が不成立になると、特別な手続きを要せず<strong>自動的に審判手続へ移行</strong>するのが大きな特徴です（家事事件手続法272条4項の趣旨）。</p>\n<p>審判では、裁判官がこれまでの主張・資料をもとに、法定相続分などを基準として遺産の分割方法を決定します。話し合いではなく裁判官の判断で結論が出るため、必ずしも自分の希望どおりになるとは限りません。審判の結果に不服がある場合は、原則として告知から2週間以内に<strong>即時抗告</strong>を申し立てることができるとされています。</p>\n<p>なお、寄与分や使途不明金など争点が複雑なケースでは、別途<strong>訴訟（民事訴訟）</strong>での解決が必要になる場合もあります。どの手続きが適切かは事案によって異なるため、早めに弁護士などの専門家へ相談することが望ましいでしょう。</p>"),
            ("知っておきたい注意点｜期限・税金との関係", "<p>遺産分割には法律上の確定的な期限はありませんが、関連する手続きには期限があるため注意が必要です。とくに次の点は早めの対応が求められます。</p>\n<ul>\n<li><strong>相続税の申告・納付</strong>：相続の開始を知った日の翌日から原則10か月以内。期限内に分割が決まらない場合でも、いったん法定相続分で申告・納税する必要があります。</li>\n<li><strong>配偶者の税額軽減・小規模宅地等の特例</strong>：未分割のままだと適用できないのが原則ですが、「申告期限後3年以内の分割見込書」を提出しておくことで、後日適用できる場合があります。</li>\n<li><strong>相続登記の義務化</strong>：2024年（令和6年）4月1日から相続登記が義務化され、原則として取得を知った日から3年以内の登記が必要とされています。</li>\n</ul>\n<p>また、2023年（令和5年）4月施行の改正により、相続開始から<strong>10年</strong>を経過すると、原則として特別受益・寄与分を考慮せず法定相続分で分割される取扱いとなりました。長期間放置するほど不利になる可能性があるため、早めの着手が大切です。税率・控除額・各期限の最新の要件は、必ず国税庁・法務局・税理士・弁護士などの専門家にご確認ください。</p>"),
        ],
        "faqs": [
            ("遺産分割調停には必ず弁護士が必要ですか？", "弁護士なしでも本人だけで申立て・出席は可能です。手続き自体は当事者が自分で進められるよう設計されています。ただし、寄与分や特別受益、不動産評価などの争点が複雑な場合や、相手方に弁護士がついている場合は、専門家に依頼することで適切な主張・立証がしやすくなります。費用と見込まれる成果を踏まえて検討するとよいでしょう。"),
            ("相続人の一人が遠方に住んでいたり、行方不明の場合はどうなりますか？", "遠方の相続人は、電話会議やウェブ会議の方法で調停に参加できる場合があります。連絡が取れない・行方不明の相続人がいる場合は、家庭裁判所に不在者財産管理人の選任を申し立てる、または失踪宣告の手続きを利用するなど、別途対応が必要になることがあります。状況に応じて家庭裁判所や専門家に相談してください。"),
            ("調停を申し立ててから解決まで、どれくらいの期間がかかりますか？", "事案により大きく異なりますが、調停はおおむね1〜2か月に1回のペースで複数回開かれ、半年から1年以上かかることも珍しくありません。争点が少なく相続人間の対立が小さいほど早く、財産が多い・評価でもめる・相続人が多いといった場合は長期化する傾向があります。不成立となれば、その後さらに審判の期間が加わります。"),
        ],
    },
    {
        "slug": "pet-legacy",
        "title": "ペットを遺す方法｜負担付遺贈とペット信託の仕組みと注意点",
        "h1": "ペットを遺す方法｜負担付遺贈とペット信託",
        "desc": "自分の死後にペットの世話を託す方法を解説。負担付遺贈と負担付死因贈与、ペット信託の仕組み・費用・税金・注意点を相続の専門家がわかりやすく整理し、後悔しない準備の進め方を紹介します。",
        "keywords": "ペット 遺す,負担付遺贈,ペット信託,負担付死因贈与,ペット 終活,相続 ペット",
        "lead": "<strong>ペットを遺す方法</strong>として注目されるのが「負担付遺贈」と「ペット信託」です。ペットは法律上「物」として扱われ、財産を直接相続させることはできないため、信頼できる人へ世話を託す仕組みをあらかじめ整える必要があります。",
        "sections": [
            ("なぜペットには「特別な備え」が必要なのか", "<p>日本の民法では、ペットは権利の主体ではなく<strong>「物」（動産）</strong>として扱われます。人間のように財産を相続したり、遺言で受遺者になったりすることはできません。そのため「全財産を愛犬に遺す」といった遺言は法的に効力を持たない、とされています。</p>\n<p>飼い主が亡くなった後、ペットの引き取り手が決まっていないと、親族間でたらい回しになったり、最悪の場合は行き場を失ったりすることがあります。だからこそ、<strong>「誰に・何を条件に・どの資金で」世話を託すか</strong>を生前に決めておくことが重要です。主な選択肢として、次のような方法があります。</p>\n<ul>\n<li><strong>負担付遺贈</strong>：遺言で財産を渡す代わりに、ペットの世話という義務を負わせる方法</li>\n<li><strong>負担付死因贈与</strong>：生前に契約を交わし、死亡を条件に財産を贈与しつつ世話を義務づける方法</li>\n<li><strong>ペット信託</strong>：信頼できる人や法人に飼育資金を信託し、第三者が管理・監督する仕組み</li>\n</ul>"),
            ("負担付遺贈・負担付死因贈与のしくみと注意点", "<p><strong>負担付遺贈</strong>は、民法第1002条に基づく方法です。「Aさんに200万円を遺贈する。その代わり私の猫を最期まで世話すること」というように、財産の受け取りと世話の義務をセットにします。遺言書（特に公正証書遺言）に明記する形が一般的です。</p>\n<p>一方、<strong>負担付死因贈与</strong>は、生前に贈与者と受贈者が契約を結ぶ点が特徴で、民法第553条により遺贈に関する規定が準用されるとされています。双方の合意で成立するため、相手が引き受ける意思を生前に確認できる安心感があります。</p>\n<p>ただし、どちらにも次のような<strong>弱点</strong>があります。</p>\n<ul>\n<li>遺贈は<strong>放棄が可能</strong>（民法第986条）で、受遺者が「いらない」と拒否すると効力が失われる場合があります</li>\n<li>財産を受け取った後、本当に世話をしているかを<strong>継続的に監督する仕組みがない</strong></li>\n<li>義務を果たさない場合、相続人は相当の期間を定めて履行を催告し、応じなければ遺言の取消しを家庭裁判所に請求できる（民法第1027条）とされますが、手間と時間がかかります</li>\n</ul>\n<p>そのため、世話をきちんと監督したい場合は、後述の信託や遺言執行者の指定と組み合わせる工夫が有効です。</p>"),
            ("ペット信託のしくみとメリット", "<p><strong>ペット信託</strong>は、信託法（平成18年法律第108号、平成19年9月施行）を活用した比較的新しい方法です。飼い主（委託者）が、信頼できる人や法人（受託者）に飼育用の資金を信託財産として託し、実際に世話をする人（受益者・飼育者）へ資金が適切に使われるよう設計します。</p>\n<p>最大の特長は、<strong>「お金の管理」と「世話の実行」を分けられる</strong>点です。さらに、第三者である<strong>信託監督人</strong>を置くことで、飼育者がきちんと世話をしているか、資金が目的どおり使われているかをチェックできます。これは遺贈にはない大きな利点とされます。</p>\n<ul>\n<li>飼い主の<strong>判断能力低下時や入院時</strong>から効力を持たせる設計も可能（生前から備えられる）</li>\n<li>飼育資金を<strong>使い込みから守りやすい</strong>（信託財産は受託者固有の財産と分別管理される）</li>\n<li>ペットの<strong>死亡後に残った資金の行き先</strong>（残余財産の帰属先）も決めておける</li>\n</ul>\n<p>契約は家族間で結ぶ「家族信託（民事信託）」型のほか、信託会社や一般社団法人などを活用する形もあります。設計の自由度が高い反面、<strong>専門的な知識が必要</strong>になるため、司法書士・弁護士など信託に詳しい専門家への相談が前提になることが多い方法です。</p>"),
            ("税金はどうなる？費用の目安", "<p>ペットを遺す仕組みでは、財産を受け取る人に<strong>税金</strong>がかかる可能性があります。仕組みごとにおおまかに整理します。</p>\n<table>\n<tr><th>方法</th><th>かかりうる税金（概要）</th></tr>\n<tr><td>負担付遺贈・負担付死因贈与</td><td>受け取った財産から負担額を差し引いた額に相続税がかかる扱いとされます（相続税法基本通達などで負担分の調整あり）</td></tr>\n<tr><td>ペット信託</td><td>受益者が利益を受けるとみなされ、設計内容に応じて贈与税・相続税の対象となる場合があります</td></tr>\n</table>\n<p>相続税には<strong>基礎控除（3,000万円＋600万円×法定相続人の数）</strong>があり、財産総額がこの範囲内なら相続税はかからないのが原則です。なお、法定相続人でない第三者が遺贈・贈与を受ける場合、相続税額の<strong>2割加算</strong>の対象になることがあります。</p>\n<p>費用の目安としては、公正証書遺言の作成手数料、信託契約書の作成・専門家報酬、信託監督人への報酬などがかかります。金額は財産規模や契約内容で大きく変わるため一概には言えません。<strong>税率・控除額・要件は改正されることがあるため、最新の内容は国税庁・法務局や、税理士・司法書士・弁護士などの専門家に必ずご確認ください。</strong></p>"),
            ("自分に合った方法の選び方と準備の進め方", "<p>どの方法が適しているかは、財産の規模・託せる相手の有無・どこまで厳格に管理したいかによって変わります。おおまかな目安は次のとおりです。</p>\n<ul>\n<li><strong>信頼できる引き取り手がいて、内容もシンプル</strong>→ 負担付遺贈や負担付死因贈与で対応しやすい</li>\n<li><strong>世話の実行や資金管理を厳格にチェックしたい</strong>→ ペット信託が向く場合が多い</li>\n<li><strong>認知症など生前の判断能力低下にも備えたい</strong>→ 信託や任意後見との組み合わせを検討</li>\n</ul>\n<p>準備の進め方の一例です。</p>\n<ol>\n<li>ペットの<strong>情報を整理</strong>（年齢・持病・かかりつけ医・食事・性格・必要な月額費用の見積り）</li>\n<li><strong>引き取り手・飼育者の候補</strong>を探し、引き受けの意思を確認する</li>\n<li>必要な<strong>飼育資金</strong>を試算する（残りの寿命×年間費用＋医療予備費を目安に）</li>\n<li>方法を選び、<strong>公正証書遺言や信託契約書</strong>として書面化する</li>\n<li>定期的に内容を<strong>見直す</strong>（ペットや候補者の状況は変わるため）</li>\n</ol>\n<p>口約束だけでは、いざというときに実行されないおそれがあります。書面で残し、できれば専門家のチェックを受けておくことが、ペットの将来を守る確実な一歩になります。</p>"),
        ],
        "faqs": [
            ("ペットに直接お金や財産を相続させることはできますか？", "できません。日本の民法上ペットは「物」として扱われ、権利の主体になれないため、遺言で財産を相続させたり受遺者に指定したりすることはできない、とされています。代わりに、世話をする人へ資金とともに義務を託す「負担付遺贈」や「ペット信託」といった方法を使います。"),
            ("負担付遺贈とペット信託は、どちらが安心ですか？", "一概には言えませんが、世話の実行や資金の使い道を継続的にチェックしたい場合は、信託監督人を置けるペット信託のほうが管理面では手厚いとされます。一方で内容がシンプルで信頼できる相手がいるなら、負担付遺贈でも十分なことがあります。財産規模や希望に応じて専門家と検討するのが安心です。"),
            ("ペットのためにいくら遺せばよいですか？", "明確な決まりはありませんが、ペットの想定される残りの寿命に年間の飼育費（餌・トリミング・ワクチン等）を掛け、これに高齢期の医療費の予備を加えて見積もる方法が一般的です。多すぎると税負担や使い道の問題、少なすぎると飼育者の負担増につながるため、現実的な金額を専門家と相談して決めるとよいでしょう。"),
        ],
    },
    {
        "slug": "renounce-still-receive",
        "title": "相続放棄しても受け取れる財産｜生命保険・遺族年金の扱いを解説",
        "h1": "相続放棄しても受け取れる財産とは",
        "desc": "相続放棄をしても生命保険金や遺族年金、未支給年金などは受け取れる場合があります。受取人指定の死亡保険金が「固有の財産」となる理由や税務・注意点、放棄を取り消せないリスクまで実務的に解説します。",
        "keywords": "相続放棄,生命保険金,遺族年金,固有の財産,みなし相続財産,未支給年金",
        "lead": "<strong>相続放棄しても受け取れる財産</strong>があることをご存じでしょうか。借金などのマイナスの財産を引き継がないために相続放棄をしても、生命保険金や遺族年金など、相続財産とは別の「受取人固有の財産」として受け取れるものがあります。本記事では何が受け取れて何が受け取れないのかを、根拠とあわせて整理します。",
        "sections": [
            ("相続放棄の基本と「受け取れる財産」がある理由", "<p>相続放棄とは、被相続人（亡くなった方）の財産に関する一切の権利義務を引き継がない手続きです。家庭裁判所への申述によって行い、受理されると<strong>その相続に関して初めから相続人とならなかったもの</strong>とみなされます（民法第939条）。プラスの財産だけでなく借金などのマイナスの財産も引き継がないため、債務超過のケースでよく利用されます。</p>\n<p>ここで重要なのは、相続放棄で受け取れなくなるのは<strong>「相続財産」に含まれるもの</strong>に限られるという点です。被相続人が所有していた預貯金・不動産・株式などは相続財産ですが、世の中には「被相続人の死亡をきっかけに発生するが、法律上は相続財産ではない」というお金が存在します。これらは受取人自身の固有の権利として支払われるため、相続放棄をしても受け取れる場合があります。</p>\n<ul>\n<li><strong>受取人が指定された生命保険金</strong>（死亡保険金）</li>\n<li><strong>遺族年金（遺族基礎年金・遺族厚生年金など）</strong></li>\n<li><strong>未支給年金</strong></li>\n<li>勤務先から遺族へ支払われる<strong>死亡退職金</strong>（規程により固有財産とされる場合）</li>\n</ul>\n<p>なお、相続放棄は原則として<strong>自己のために相続の開始があったことを知った時から3か月以内</strong>に行う必要があります（民法第915条第1項、いわゆる熟慮期間）。期限や手続きの詳細は事案によって異なるため、判断に迷う場合は早めに専門家へ相談してください。</p>"),
            ("生命保険金（死亡保険金）は受け取れる", "<p>生命保険の死亡保険金は、契約で<strong>受取人が指定されている場合、その受取人の固有の財産</strong>となります。これは保険契約に基づき保険会社から受取人へ直接支払われるお金であり、被相続人から相続する財産ではないためです。判例上も、特定の相続人が受取人に指定されている場合の保険金請求権は受取人固有の権利と解されており、相続放棄をしても受け取れるとされています。</p>\n<p>ただし、注意すべき点があります。</p>\n<ul>\n<li><strong>受取人が「被相続人本人」になっている場合</strong>：保険金請求権が相続財産に含まれると扱われることがあり、相続放棄をすると受け取れない可能性があります。</li>\n<li><strong>受取人が「相続人」とだけ指定されている場合</strong>：誰が受取人かは契約内容や約款によるため、保険会社への確認が必要です。</li>\n</ul>\n<p><strong>税金の扱い</strong>も押さえておきましょう。受取人固有の財産であっても、死亡保険金は相続税法上の「みなし相続財産」として<strong>相続税の課税対象</strong>になります（相続税法第3条第1項第1号）。生命保険金には「500万円×法定相続人の数」の非課税枠がありますが、<strong>相続放棄をした人はこの非課税枠を使えません</strong>。一方で、非課税枠を計算する際の「法定相続人の数」には、放棄した人も含めて数えます。税額は事案ごとに大きく変わるため、最新の要件や計算は国税庁の情報や税理士にご確認ください。</p>"),
            ("遺族年金・未支給年金は相続財産ではない", "<p><strong>遺族年金</strong>（遺族基礎年金・遺族厚生年金など）は、一定の要件を満たす遺族が<strong>自分自身の権利として</strong>受け取る給付です。被相続人から相続する財産ではないため、相続放棄をしても受給に影響しないとされています。受給できる遺族の範囲や要件は法律で定められており、配偶者や子などが対象となる場合があります。</p>\n<p>また、年金を受けていた方が亡くなった月分などで、まだ支払われていない年金（<strong>未支給年金</strong>）は、生計を同じくしていた一定範囲の遺族が<strong>自己の固有の権利</strong>として請求できます。判例でも未支給年金請求権は相続の対象ではなく遺族固有の権利と解されており、相続放棄をしても請求できると考えられています。</p>\n<p>税務上の取り扱いも整理しておきます。</p>\n<ul>\n<li><strong>遺族基礎年金・遺族厚生年金</strong>：原則として<strong>非課税</strong>とされています。</li>\n<li><strong>未支給年金</strong>：受け取った遺族の<strong>一時所得</strong>として扱われ、相続税の対象ではないとされています。</li>\n</ul>\n<p>年金は手続きをしないと受け取れません。遺族年金や未支給年金には請求期限（時効）があるため、該当しそうな場合は早めに年金事務所へ確認しましょう。</p>"),
            ("受け取れないもの・判断に注意が必要なもの", "<p>逆に、次のようなものは相続財産に含まれ、原則として相続放棄をすると受け取れません。受け取ってしまうと、相続を承認したとみなされて<strong>放棄が認められなくなる（または取り消せなくなる）</strong>リスクがあるため特に注意が必要です。</p>\n<ul>\n<li>被相続人名義の<strong>預貯金・現金・不動産・株式</strong>などのプラスの財産</li>\n<li>被相続人が受取人になっている保険金（前述）</li>\n<li>被相続人が支払うべきだった還付金等のうち、相続財産と評価されるもの</li>\n</ul>\n<p>判断が難しいのが、葬儀費用や形見分け、被相続人の財産の取り扱いです。相続財産を処分したり消費したりすると、<strong>単純承認をしたとみなされる（法定単純承認、民法第921条）</strong>ことがあります。社会通念上相当な範囲の葬儀費用の支出などは問題にならないとされる場合もありますが、線引きは個別事情によります。</p>\n<table>\n<tr><th>区分</th><th>例</th><th>相続放棄しても受け取れるか</th></tr>\n<tr><td>受取人指定の死亡保険金</td><td>配偶者・子が受取人</td><td>受け取れる（みなし相続財産・課税対象）</td></tr>\n<tr><td>遺族年金</td><td>遺族基礎・遺族厚生年金</td><td>受け取れる（原則非課税）</td></tr>\n<tr><td>未支給年金</td><td>死亡月分の年金など</td><td>受け取れる（一時所得）</td></tr>\n<tr><td>相続財産</td><td>預貯金・不動産・株式</td><td>受け取れない</td></tr>\n</table>\n<p>「受け取ってよいか分からない」という場合は、手をつける前に専門家へ相談するのが安全です。</p>"),
            ("手続きの流れと専門家への相談", "<p>実務では、次のような順序で進めると整理しやすくなります。</p>\n<ul>\n<li><strong>1. 財産・債務の調査</strong>：プラスの財産とマイナスの財産（借金・保証債務など）を洗い出します。</li>\n<li><strong>2. 相続放棄の判断</strong>：債務超過などで放棄が適切かを検討します。期限（原則3か月）に注意します。</li>\n<li><strong>3. 受け取れる財産の確認</strong>：生命保険の受取人指定、遺族年金・未支給年金の受給資格を確認します。</li>\n<li><strong>4. 家庭裁判所への申述</strong>：被相続人の最後の住所地を管轄する家庭裁判所に相続放棄の申述を行います。</li>\n<li><strong>5. 各給付の請求</strong>：放棄が受理された後でも、固有の財産である保険金・年金は別途請求します。</li>\n</ul>\n<p>注意したいのは、<strong>相続放棄と保険金・年金の請求は別の手続き</strong>だという点です。相続放棄をしたからといって自動的に保険金が支払われるわけではなく、受取人としての請求が必要です。逆に、保険金を受け取ったこと自体は、それが固有の財産であれば相続放棄の妨げにはならないと考えられています。</p>\n<p>相続放棄は一度受理されると原則として撤回できません（民法第919条第1項）。判断を誤ると借金を背負ったり、受け取れたはずの財産を失ったりするおそれがあります。<strong>個別の事情によって結論が変わる</strong>ため、生命保険や年金が絡む相続放棄を検討する際は、弁護士・司法書士・税理士などの専門家や、年金事務所・国税庁・家庭裁判所といった窓口で最新の要件を確認することをおすすめします。</p>"),
        ],
        "faqs": [
            ("相続放棄をすると生命保険金も受け取れなくなりますか？", "受取人があなた自身など特定の相続人に指定されている死亡保険金は、受取人固有の財産とされ、相続放棄をしても受け取れる場合があります。ただし受取人が被相続人本人になっている場合は相続財産に含まれ、受け取れない可能性があります。また保険金は相続税法上の「みなし相続財産」として課税対象となり、相続放棄をした人は生命保険金の非課税枠を使えない点にも注意してください。"),
            ("相続放棄しても遺族年金や未支給年金はもらえますか？", "遺族年金は要件を満たす遺族が自分自身の権利として受け取る給付であり、相続財産ではないため、相続放棄をしても受給に影響しないとされています。未支給年金も生計を同じくしていた一定範囲の遺族が固有の権利として請求できると解されています。いずれも自動では支払われず請求手続きと期限があるため、年金事務所で早めにご確認ください。"),
            ("保険金を受け取ると相続放棄ができなくなりますか？", "受取人固有の財産である死亡保険金を受け取っても、それ自体は相続財産の処分にはあたらないため、相続放棄の妨げにはならないと考えられています。一方で、被相続人名義の預貯金を引き出して使うなど相続財産を処分すると、単純承認をしたとみなされ放棄が認められなくなるおそれがあります（民法第921条）。判断に迷う場合は手をつける前に専門家へ相談してください。"),
        ],
    },
    {
        "slug": "diy-inheritance",
        "title": "相続手続きを自分でやる｜専門家に頼まず進める手順と注意点",
        "h1": "相続手続きを自分でやる｜全体の流れと注意点",
        "desc": "相続手続きを自分でやる方法を、期限のある手続きから戸籍収集・遺産分割・名義変更まで実務的に解説。専門家に頼むべきケースの見極めや、2024年義務化の相続登記など最新の注意点も整理します。",
        "keywords": "相続手続き 自分で,相続手続き 流れ,相続登記 自分で,遺産分割協議書 書き方,法定相続情報一覧図,相続放棄 期限",
        "lead": "<strong>相続手続きを自分でやる</strong>ことは、財産構成がシンプルで相続人の協力が得られる場合、十分に可能とされます。ただし期限のある手続きを見落とすと不利益が生じることもあるため、全体像を押さえてから着手することが大切です。",
        "sections": [
            ("まずは全体像と「期限のある手続き」を押さえる", "<p>相続手続きは数が多く、なかには厳しい期限が設けられているものがあります。自分で進める場合は、まず<strong>期限のあるもの</strong>から優先的に確認しましょう。</p>\n<ul>\n<li><strong>相続放棄・限定承認：原則として自己のために相続の開始があったことを知った時から3か月以内</strong>（民法915条）。借金などマイナスの財産が多い場合に検討します。</li>\n<li><strong>所得税の準確定申告：相続の開始を知った日の翌日から4か月以内</strong>（被相続人に申告が必要な所得があった場合）。</li>\n<li><strong>相続税の申告・納付：相続の開始を知った日の翌日から10か月以内</strong>（相続税法27条）。基礎控除を超える場合に必要です。</li>\n</ul>\n<p>これらは過ぎると放棄ができなくなったり、加算税・延滞税が生じたりする場合があります。<strong>「いつ起算するか」</strong>を正確に把握することが、自分で進めるうえでの第一歩です。</p>"),
            ("戸籍・必要書類を集める（法定相続情報一覧図の活用）", "<p>誰が相続人かを確定するため、被相続人の<strong>出生から死亡までの連続した戸籍（除籍・改製原戸籍を含む）</strong>と、相続人全員の現在の戸籍を集めます。本籍地のある市区町村役場で取得しますが、本籍が複数回移っている場合は、さかのぼって複数の自治体に請求する必要があります。</p>\n<p>なお2024年3月から、最寄りの市区町村窓口でまとめて戸籍を請求できる<strong>戸籍の広域交付制度</strong>が始まり、収集の負担は軽くなってきています（請求できる人や対象に条件があります）。</p>\n<p>集めた戸籍をもとに、法務局で<strong>法定相続情報一覧図</strong>を無料で作成・交付してもらえます。これがあると、金融機関や法務局での手続きのたびに大量の戸籍束を提出せずに済み、一覧図の写し1枚で代用できるため、複数の窓口を回る自分での手続きでは特に役立ちます。</p>"),
            ("遺産分割協議書を作成する", "<p>遺言書がない場合、相続人全員で誰が何を取得するかを話し合い（遺産分割協議）、その結果を<strong>遺産分割協議書</strong>にまとめます。協議は相続人全員の合意が必要で、一人でも欠けると無効とされます。</p>\n<p>作成時のポイントは次のとおりです。</p>\n<ul>\n<li>不動産は登記事項証明書のとおりに正確に特定し、預貯金は金融機関名・支店・口座番号まで記載する。</li>\n<li>相続人全員が署名し、<strong>実印で押印</strong>したうえで、全員の<strong>印鑑証明書</strong>を添付する。</li>\n<li>後から見つかった財産の取り扱い（誰が取得するか)を一文入れておくと、再協議の手間を避けやすい。</li>\n</ul>\n<p>遺言書が自筆証書遺言で見つかった場合は、開封前に家庭裁判所の<strong>検認</strong>が必要なことがある点にも注意してください（法務局の自筆証書遺言書保管制度を利用していた場合は検認は不要です）。</p>"),
            ("名義変更・相続登記を行う（2024年から義務化）", "<p>分割内容が決まったら、財産ごとに名義変更を進めます。</p>\n<ul>\n<li><strong>不動産</strong>：管轄の法務局へ相続登記を申請。<strong>2024年4月1日から相続登記が義務化</strong>され、原則として取得を知った日から3年以内の申請が求められ、正当な理由なく怠ると過料の対象となる場合があります（過去の相続も対象で経過措置があります）。</li>\n<li><strong>預貯金</strong>：各金融機関で相続手続きを行い、解約・名義変更する。所定の相続届に相続人の署名押印が必要です。</li>\n<li><strong>自動車・有価証券など</strong>：それぞれ運輸支局や証券会社で手続きします。</li>\n</ul>\n<p>相続登記は申請書の作成や添付書類の準備が必要ですが、法務局には<strong>登記手続案内</strong>（事前予約制の相談）があり、自分で申請する人向けの情報も公開されています。登録免許税は原則として固定資産税評価額の0.4％が目安とされます。</p>"),
            ("自分でできる範囲と、専門家に頼むべきケースの見極め", "<p>自分で進めやすいのは、おおむね次のような場合とされます。</p>\n<ul>\n<li>相続人が少なく、全員が協力的で連絡が取りやすい。</li>\n<li>財産が預貯金や自宅程度で、構成が比較的シンプル。</li>\n<li>借金などマイナスの財産がなく、相続税の申告も不要（基礎控除内）。</li>\n</ul>\n<p>一方、次のようなケースは専門家への相談を検討した方がよいとされます。</p>\n<ul>\n<li>相続人同士で意見が対立している、または連絡の取れない相続人がいる（弁護士など）。</li>\n<li>相続税の申告が必要、または特例の適用で判断が難しい（税理士など）。</li>\n<li>不動産が複数ある、未登記・共有・遠方など登記が複雑（司法書士など）。</li>\n</ul>\n<p>専門家に依頼する場合でも、戸籍収集など一部だけを依頼する方法もあります。費用と手間のバランスを見て、無理のない範囲で進めるとよいでしょう。<strong>税率・控除額・期限などの具体的な要件や最新の取り扱いは、必ず国税庁・法務局や専門家でご確認ください。</strong></p>"),
        ],
        "faqs": [
            ("相続手続きを全部自分でやることはできますか？", "財産構成がシンプルで相続人の協力が得られる場合は、戸籍収集から遺産分割協議書の作成、相続登記や預貯金の名義変更まで、自分で進めることは十分に可能とされます。ただし相続税の申告が必要なケースや、相続人間で争いがある場合などは、専門家に相談した方が安全な場合があります。"),
            ("相続手続きで最初に確認すべき期限は何ですか？", "まず確認したいのは、相続放棄・限定承認の原則3か月（民法915条）、準確定申告の4か月、相続税の申告・納付の10か月（相続税法27条）です。いずれも起算日は「相続の開始を知った時（日）」が基準とされ、過ぎると不利益が生じる場合があります。詳しい起算日や要件は専門家や国税庁・裁判所でご確認ください。"),
            ("相続登記はいつまでにしないといけませんか？", "2024年4月1日から相続登記が義務化され、原則として不動産を取得したことを知った日から3年以内の申請が求められます。正当な理由なく怠ると過料の対象となる場合があります。施行前に発生した相続も対象で経過措置が設けられているため、具体的な期限は法務局でご確認ください。"),
        ],
    },
    {
        "slug": "will-trust-bank",
        "title": "遺言信託（銀行）とは｜サービス内容・費用・向き不向きを解説",
        "h1": "遺言信託（銀行）とは｜サービス内容・費用・向き不向き",
        "desc": "銀行の「遺言信託」とは何かをわかりやすく解説。遺言書の作成サポートから保管、執行までのサービス内容、費用相場、メリット・デメリット、向いている人・向かない人の見分け方まで実務目線で紹介します。",
        "keywords": "遺言信託,銀行 遺言信託,遺言執行,遺言信託 費用,遺言書 保管,遺言執行者",
        "lead": "<strong>遺言信託（銀行）</strong>とは、信託銀行などが遺言書の作成相談から保管、相続発生後の執行までを一括でサポートするサービスの通称です。名前に「信託」と付きますが、信託法上の「信託」とは異なる点に注意が必要です。",
        "sections": [
            ("遺言信託（銀行）とは何か｜「信託」という言葉の誤解に注意", "<p>銀行や信託銀行が提供する<strong>「遺言信託」</strong>は、一般的に次の3つを一括で引き受けるサービスを指します。</p>\n<ul>\n<li>遺言書（主に公正証書遺言）の作成についての相談・助言</li>\n<li>作成した遺言書（正本・謄本）の<strong>保管</strong></li>\n<li>相続発生後の<strong>遺言執行</strong>（遺言の内容を実現する手続き）</li>\n</ul>\n<p>ここで注意したいのは、この「遺言信託」は信託法上の「信託」とは別物だという点です。信託法上の信託は、財産を受託者に移転して管理・運用してもらう仕組み（民法・信託法に基づく「信託契約」や「遺言による信託」）を指します。一方、銀行の商品名としての「遺言信託」は、<strong>遺言の作成支援・保管・執行を支援するサービス</strong>であり、銀行が財産を預かって運用するものではありません。同じ言葉でも内容が異なるため、契約前に「どちらの意味か」を確認することが大切です。</p>"),
            ("サービスの流れ｜相談から遺言執行までの3ステップ", "<p>銀行の遺言信託は、おおむね次の流れで進みます。</p>\n<ul>\n<li><strong>1. 相談・遺言書の作成</strong>：財産や相続人の状況をヒアリングし、遺言の内容を整理します。実際の遺言書は、本人が公証役場で作成する<strong>公正証書遺言</strong>（民法969条）が用いられるのが一般的です。銀行は作成のサポート役で、遺言を書くのはあくまで本人です。</li>\n<li><strong>2. 遺言書の保管・定期的な照会</strong>：作成した遺言書を銀行が保管し、定期的に内容の確認や見直しの連絡を行います。財産や家族構成が変わったときに書き換えやすいのが特長です。</li>\n<li><strong>3. 遺言執行</strong>：相続が発生すると、銀行が<strong>遺言執行者</strong>（民法1006条以降）として、相続財産の調査、預貯金の解約・名義変更、不動産の登記手続きの手配、相続人への分配などを行います。</li>\n</ul>\n<p>遺言執行者は、相続人の代理人として遺言の内容を実現する立場で、就任後は遅滞なく財産目録を作成して相続人に交付する義務があります（民法1011条）。専門の担当者が手続きを進めるため、相続人の事務負担が軽くなる場合があります。</p>"),
            ("費用の目安｜何にいくらかかるのか", "<p>費用は金融機関ごとに異なりますが、一般的に次のような構成になっています。具体的な金額は各行の最新の料金表でご確認ください。</p>\n<table>\n<tr><th>費目</th><th>内容</th><th>目安</th></tr>\n<tr><td>申込時手数料</td><td>契約締結時に支払う初期費用</td><td>数十万円程度のことが多い</td></tr>\n<tr><td>保管料</td><td>遺言書を預けている間の年間費用</td><td>年間数千円〜数万円程度</td></tr>\n<tr><td>遺言執行報酬</td><td>相続発生後の執行手続きの報酬</td><td>財産額に応じた料率＋最低報酬額</td></tr>\n</ul>\n</table>\n<p>特に大きいのが<strong>遺言執行報酬</strong>です。多くの場合、承継する財産の価額に対して一定の料率をかけて算定され、<strong>最低報酬額</strong>（例：100万円以上などと設定されることが多い）が定められています。財産規模が大きいほど報酬も高くなる傾向があるため、見積もりを事前に取ることが重要です。なお、これらの費用とは別に、公正証書作成のための公証人手数料や、不動産登記の登録免許税・司法書士報酬などの実費が別途かかります。</p>"),
            ("メリットとデメリット｜専門家・士業との比較", "<p><strong>メリット</strong>として、次の点が挙げられます。</p>\n<ul>\n<li>金融機関としての信頼性・継続性があり、長期の保管・執行を任せやすい</li>\n<li>遺言書の紛失・改ざんのリスクを避けられ、定期的な見直しの案内が受けられる</li>\n<li>相続人同士で執行を担う負担や争いを避けられる場合がある</li>\n</ul>\n<p>一方、<strong>デメリット・注意点</strong>もあります。</p>\n<ul>\n<li><strong>費用が比較的高め</strong>になりやすく、特に遺言執行報酬の負担が大きい</li>\n<li>銀行は弁護士法の制約上、相続人間に争いがある（争続）案件には対応できず、紛争化すると<strong>辞退・別途専門家への依頼</strong>が必要になることがある</li>\n<li>遺言の内容によっては、銀行が執行を引き受けられないケースがある</li>\n</ul>\n<p>同じ役割は、<strong>弁護士・司法書士・行政書士・税理士</strong>などの専門家に依頼することもできます。紛争性がある場合や節税を重視する場合は士業、財産が多く中立的な機関に長期間任せたい場合は銀行、というように適性が分かれます。</p>"),
            ("向いている人・向いていない人", "<p>銀行の遺言信託が<strong>向いている</strong>と考えられるのは、次のような方です。</p>\n<ul>\n<li>相続財産が多く、預貯金・不動産・有価証券など内容が複雑な方</li>\n<li>相続人が遠方・多人数で、手続きを任せられる中立的な機関を求める方</li>\n<li>費用よりも安心感・確実性を優先したい方</li>\n</ul>\n<p>逆に<strong>向いていない</strong>可能性が高いのは、次のような方です。</p>\n<ul>\n<li>相続人間に対立があり、紛争化が見込まれる方（弁護士への相談が適切な場合があります）</li>\n<li>財産が比較的少なく、費用負担を抑えたい方</li>\n<li>自宅の保管や法務局の<strong>自筆証書遺言書保管制度</strong>（2020年7月施行）など、より低コストな方法で十分な方</li>\n</ul>\n<p>なお、税率・控除額・各種制度の要件は改正されることがあります。相続税の計算や遺言の有効性に関わる最新の要件は、<strong>国税庁・法務局・弁護士や税理士などの専門家</strong>に必ずご確認ください。本記事は一般的な解説であり、個別の判断を保証するものではありません。</p>"),
        ],
        "faqs": [
            ("銀行の「遺言信託」は、財産を預けて運用してもらうサービスですか？", "いいえ。商品名としての「遺言信託」は、遺言書の作成支援・保管・遺言執行を行うサービスで、銀行が財産を預かって運用するものではありません。財産を移転して管理・運用してもらう信託法上の「信託」とは別物です。混同しやすいため、契約前にサービス内容を確認することをおすすめします。"),
            ("遺言信託を利用すれば、相続人同士のもめごとも解決してもらえますか？", "いいえ。銀行は弁護士法の制約により、相続人間に争いがある案件の代理交渉などは行えません。すでに対立がある、または紛争化が見込まれる場合は、遺言執行を辞退されることがあります。争いの解決や予防を重視するなら、弁護士への相談が適切な場合があります。"),
            ("費用はどれくらいかかりますか？", "金融機関により異なりますが、一般に申込時手数料（数十万円程度のことが多い）、年間の保管料、相続発生後の遺言執行報酬で構成されます。特に遺言執行報酬は財産額に応じた料率と最低報酬額（100万円以上などとされることが多い）があり、負担が大きくなりがちです。正確な金額は各金融機関の最新の料金表でご確認ください。"),
        ],
    },
]

def main():
    # 全記事タイトル一覧（関連記事リンク用）
    all_pairs = [(a["slug"], a["h1"]) for a in ARTICLES]

    for art in ARTICLES:
        related = [(s, t) for s, t in all_pairs if s != art["slug"]][:5]
        out_dir = ROOT / art["slug"]
        out_dir.mkdir(exist_ok=True)
        html = render(art, related)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  OK /{art['slug']}/")

    # /guides/ 一覧ページ
    guides_dir = ROOT / "guides"
    guides_dir.mkdir(exist_ok=True)
    (guides_dir / "index.html").write_text(render_guides_index(), encoding="utf-8")
    print(f"  OK /guides/")

    # /glossary/ 用語集ページ
    glossary_dir = ROOT / "glossary"
    glossary_dir.mkdir(exist_ok=True)
    (glossary_dir / "index.html").write_text(render_glossary(), encoding="utf-8")
    print(f"  OK /glossary/ ({len(GLOSSARY)} terms)")

    # /about/ 運営者情報
    about_dir = ROOT / "about"
    about_dir.mkdir(exist_ok=True)
    (about_dir / "index.html").write_text(render_about(), encoding="utf-8")
    print(f"  OK /about/")

    # 早見表ページ
    for qt in QUICK_TABLES:
        qt_dir = ROOT / qt["slug"]
        qt_dir.mkdir(exist_ok=True)
        (qt_dir / "index.html").write_text(render_quick_table(qt), encoding="utf-8")
        print(f"  OK /{qt['slug']}/")

    # 柱ページ（トピッククラスター）
    meta = _meta_map()
    for pillar in PILLARS:
        pdir = ROOT / pillar["slug"]
        pdir.mkdir(exist_ok=True)
        (pdir / "index.html").write_text(render_pillar(pillar, meta), encoding="utf-8")
        print(f"  OK /{pillar['slug']}/ (柱ページ)")

    # /calculator/ インタラクティブ計算ツール
    calc_dir = ROOT / "calculator"
    calc_dir.mkdir(exist_ok=True)
    (calc_dir / "index.html").write_text(render_calculator(), encoding="utf-8")
    print(f"  OK /calculator/")

    # /cases/ ケーススタディ集
    cases_dir = ROOT / "cases"
    cases_dir.mkdir(exist_ok=True)
    (cases_dir / "index.html").write_text(render_case_index(), encoding="utf-8")
    print(f"  OK /cases/ ({len(CASE_STUDIES)} cases)")

    # 404.html
    (ROOT / "404.html").write_text(render_404(), encoding="utf-8")
    print(f"  OK 404.html")

    # RSS フィード
    (ROOT / "feed.xml").write_text(render_rss(), encoding="utf-8")
    print(f"  OK feed.xml ({len(ARTICLES)} items)")

    # sitemap.xml を再生成
    today = "2026-05-30"
    urls = (
        [SITE_URL + "/", SITE_URL + "/guides/", SITE_URL + "/glossary/", SITE_URL + "/about/",
         SITE_URL + "/calculator/", SITE_URL + "/cases/"]
        + [f"{SITE_URL}/{p['slug']}/" for p in PILLARS]
        + [f"{SITE_URL}/{a['slug']}/" for a in ARTICLES]
        + [f"{SITE_URL}/{qt['slug']}/" for qt in QUICK_TABLES]
    )
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    pillar_urls = {f"{SITE_URL}/{p['slug']}/" for p in PILLARS}
    hub_urls = set(urls[1:6]) | pillar_urls
    for u in urls:
        if u == urls[0]:
            priority = '1.0'
        elif u in hub_urls:
            priority = '0.9'
        else:
            priority = '0.8'
        sm.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>{priority}</priority></url>")
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")
    print(f"  OK sitemap.xml ({len(urls)} URLs)")



# --- 2026-06 SEOギャップ8記事(相続時精算課税/生前贈与加算7年/おしどり贈与/住宅資金贈与/代襲相続/特別寄与料/相続財産清算人/遺言無効) ---
ARTICLES += [{'slug': 'settlement-taxation-gift', 'title': '相続時精算課税制度とは｜2024年改正の110万円基礎控除と選び方', 'h1': '相続時精算課税制度と2024年改正のポイント', 'desc': '相続時精算課税制度の仕組みを、2024年に新設された年110万円の基礎控除を中心に解説。2,500万円の特別控除、暦年課税との違いと選び方、一度選ぶと戻れない注意点まで分かりやすくまとめます。', 'keywords': '相続時精算課税,110万円,2024年改正,基礎控除,2500万円,暦年贈与,選び方', 'lead': '<strong>相続時精算課税制度</strong>は、生前贈与を「いったん非課税に近い形で渡し、相続のときにまとめて精算する」贈与税の制度です。2024年1月の改正で<strong>年110万円の基礎控除</strong>が新設され、使い勝手が大きく変わりました。本記事では制度の仕組みと、暦年課税との選び方を整理します。', 'sections': [('制度の基本：2,500万円まで贈与税ゼロ', '<p>相続時精算課税は、<strong>60歳以上の父母・祖父母</strong>から<strong>18歳以上の子・孫</strong>への贈与で選べる制度です（相続税法21条の9）。累計<strong>2,500万円</strong>の特別控除までは贈与税がかからず、超えた部分は一律20%で課税されます。</p><p>ただし「非課税」ではなく「<strong>精算</strong>」が名前のとおりで、贈与した財産は最終的に<strong>相続財産に持ち戻して</strong>相続税で計算し直します。すでに払った贈与税は相続税から差し引かれます。</p>'), ('2024年改正：年110万円の基礎控除が新設', '<p>2024年1月1日以後の贈与から、相続時精算課税にも<strong>年110万円の基礎控除</strong>が設けられました。これは暦年課税の110万円とは<strong>別枠</strong>で、この制度を選んだ人に毎年適用されます。</p><ul><li>年110万円以下の贈与なら<strong>贈与税の申告は不要</strong></li><li>110万円以下の部分は<strong>相続時の持ち戻しも不要</strong>（相続財産に加算されない）</li><li>2,500万円の特別控除とは別に、毎年使える</li></ul><p>改正前は「少額でも全額を持ち戻す」点が大きなデメリットでしたが、年110万円までは持ち戻し不要となり、コツコツ贈与にも使いやすくなりました。</p>'), ('暦年課税との比較', '\n<table style="width:100%;border-collapse:collapse;margin:1rem 0;background:white;">\n  <thead><tr style="background:#27AE60;color:white;"><th style="padding:.6rem;border:1px solid #ddd;">比較項目</th><th style="padding:.6rem;border:1px solid #ddd;">暦年課税</th><th style="padding:.6rem;border:1px solid #ddd;">相続時精算課税</th></tr></thead>\n  <tbody>\n    <tr><td style="padding:.6rem;border:1px solid #ddd;">毎年の非課税枠</td><td style="padding:.6rem;border:1px solid #ddd;">110万円</td><td style="padding:.6rem;border:1px solid #ddd;">110万円（2024年〜）＋特別控除2,500万円</td></tr>\n    <tr><td style="padding:.6rem;border:1px solid #ddd;">相続時の持ち戻し</td><td style="padding:.6rem;border:1px solid #ddd;">死亡前一定期間の贈与を加算（最長7年へ延長中）</td><td style="padding:.6rem;border:1px solid #ddd;">110万円超の贈与を全額加算</td></tr>\n    <tr><td style="padding:.6rem;border:1px solid #ddd;">制度の変更</td><td style="padding:.6rem;border:1px solid #ddd;">いつでも可</td><td style="padding:.6rem;border:1px solid #ddd;">一度選ぶと暦年に戻れない</td></tr>\n  </tbody>\n</table>\n<p>大きな財産を早めにまとまった額で渡したい場合や、値上がりが見込まれる資産（自社株など）の贈与には精算課税が向くことがあります。一方、長期間かけて少しずつ渡すなら暦年課税が有利なケースもあります。</p>\n'), ('選ぶ前に押さえたい注意点', '<p><strong>一度選ぶと暦年課税には戻れません</strong>（同じ贈与者からの贈与について）。最初の贈与をした年の翌年3月15日までに「相続時精算課税選択届出書」を提出します。</p><ul><li>持ち戻しは<strong>贈与時の価額</strong>で行うため、値下がりする財産では不利になることがある</li><li>小規模宅地等の特例は、精算課税で贈与した宅地には使えない</li><li>どちらが有利かは家族構成・財産の種類・金額で変わります</li></ul><p>判断に迷う場合は、税理士に試算を依頼すると安心です。税制は改正されることがあるため、最新の取扱いは<strong>国税庁の公表資料</strong>で確認してください。</p>')], 'faqs': [('110万円の基礎控除は暦年課税と両方使えますか？', '同じ贈与者からの贈与については、どちらか一方の制度しか選べません。相続時精算課税を選ぶと、その贈与者からの贈与には精算課税の110万円が適用され、暦年課税の110万円は使えません。別の贈与者からの贈与であれば、それぞれ別に制度を選べます。'), ('一度選んだら本当に取り消せませんか？', 'はい、相続時精算課税はいったん選択すると、その贈与者からの贈与について暦年課税へ戻すことはできません（相続税法21条の9第6項）。選択は慎重に判断してください。'), ('精算課税で贈与した財産は相続税が必ずかかりますか？', '相続財産に持ち戻して計算しますが、遺産総額が基礎控除（3,000万円＋600万円×法定相続人数）以下なら相続税はかかりません。納めた贈与税が相続税を上回る場合は差額が還付されることもあります。')]}, {'slug': 'gift-addback-7year', 'title': '生前贈与加算の7年ルール｜2024年改正で3年から7年へ延長', 'h1': '生前贈与加算（持ち戻し）の7年ルール', 'desc': '暦年贈与の生前贈与加算が、2024年改正で相続開始前3年から7年へ段階的に延長。延長された4年分の100万円控除や経過措置のスケジュール、相続時精算課税との違いと対策を解説します。', 'keywords': '生前贈与加算,7年ルール,2024年改正,持ち戻し,3年,相続税,暦年贈与', 'lead': '暦年贈与で渡した財産でも、相続が近い時期のものは相続財産に<strong>持ち戻して</strong>相続税が計算されます。これを<strong>生前贈与加算</strong>といい、2024年の改正で対象期間が<strong>3年から7年へ</strong>延長されました。本記事で改正の中身と対策を整理します。', 'sections': [('生前贈与加算とは', '<p>暦年課税（年110万円まで非課税）で贈与しても、贈与者が亡くなる直前の一定期間に行った贈与は、<strong>相続財産に加算</strong>して相続税を計算します（相続税法19条）。「駆け込み贈与で相続税を逃れる」ことを防ぐための仕組みです。</p><p>加算の対象になるのは、原則として<strong>相続や遺贈で財産を取得した人</strong>（相続人など）への贈与です。孫など相続で財産を受け取らない人への贈与は、原則として加算対象外です。</p>'), ('2024年改正：3年→7年へ段階的に延長', '<p>2024年1月1日以後の贈与から、加算期間が<strong>相続開始前3年→7年</strong>へ延長されました。延長された<strong>4年間（死亡前3年超〜7年）</strong>の贈与については、その合計額から<strong>総額100万円を控除</strong>して加算します。</p><ul><li>死亡前3年以内の贈与：全額を加算（従来どおり）</li><li>死亡前3年超〜7年の贈与：合計から100万円を引いて加算</li></ul><p>改正は2024年贈与分から段階的に効いてくるため、<strong>7年フルで加算されるのは2031年1月1日以後の相続から</strong>です。それまでは経過措置で加算期間が徐々に延びます。</p>'), ('対策の考え方', '<p>加算期間が延びたことで、「亡くなる間際の暦年贈与」の節税効果は薄まりました。対策としては次のような視点があります。</p><ul><li><strong>早めに始める</strong>：7年より前の贈与は加算されないため、若いうちからの計画的な贈与が有効</li><li><strong>相続で財産を取得しない人へ贈与</strong>：孫などへの贈与は原則加算対象外（ただし遺贈や保険金受取などがあると対象になることも）</li><li><strong>相続時精算課税の110万円</strong>：2024年新設の精算課税の年110万円基礎控除は、生前贈与加算の対象外</li></ul>'), ('相続時精算課税との違い', '<p>同じ「持ち戻し」でも、暦年課税の生前贈与加算と相続時精算課税は別の仕組みです。精算課税では2024年から年110万円までの贈与は持ち戻し不要になったため、コツコツ贈与の選択肢として見直されています。</p><p>どちらが有利かは財産額・年齢・家族構成で変わります。税制は改正が続く分野のため、最新の取扱いは<strong>国税庁の公表資料</strong>で確認し、判断に迷う場合は税理士へ相談すると確実です。</p>')], 'faqs': [('孫への贈与も7年加算の対象ですか？', '原則として、相続や遺贈で財産を取得しない孫への贈与は加算対象外です。ただし、孫が遺言で財産を受け取ったり、生命保険金の受取人になっている場合などは対象になることがあります。'), ('延長された4年分の100万円控除は毎年100万円ですか？', 'いいえ。死亡前3年超〜7年の4年間の贈与の合計額から、総額で100万円を控除します。毎年100万円ではなく、4年分まとめて100万円である点に注意してください。'), ('今から始めても効果はありますか？', 'あります。加算されるのは相続開始前7年以内の贈与なので、それより前に贈与した分は持ち戻されません。早く始めるほど、加算対象から外れる贈与を積み上げられます。')]}, {'slug': 'spouse-gift-deduction', 'title': 'おしどり贈与（贈与税の配偶者控除）｜2,000万円まで非課税の要件', 'h1': 'おしどり贈与（贈与税の配偶者控除）', 'desc': '婚姻20年以上の夫婦間で居住用不動産などを贈与すると最大2,000万円まで非課税になる「おしどり贈与」。要件・申告の必要性・生前贈与加算の対象外になる点や、登録免許税など見落としやすい注意点を解説します。', 'keywords': 'おしどり贈与,贈与税の配偶者控除,2000万円,婚姻20年,居住用不動産,非課税', 'lead': '<strong>おしどり贈与</strong>は、長年連れ添った夫婦間で自宅などを贈与したときに使える特例で、正式には<strong>贈与税の配偶者控除</strong>といいます（相続税法21条の6）。基礎控除110万円に加えて<strong>最大2,000万円</strong>まで非課税になりますが、得とは限らない場面もあります。要件と注意点を整理します。', 'sections': [('制度の概要：110万円＋2,000万円', '<p>婚姻期間が<strong>20年以上</strong>の夫婦間で、<strong>居住用不動産</strong>またはその<strong>取得資金</strong>を贈与した場合、基礎控除110万円に加えて最高<strong>2,000万円</strong>まで贈与税の課税価格から控除できます。合わせて最大2,110万円までが非課税です。</p><p>適用は<strong>同じ夫婦間で一生に一度</strong>のみです。</p>'), ('主な要件', '<ul><li>贈与の時点で<strong>婚姻期間が20年以上</strong>であること（20年以上かどうかは年単位で判定）</li><li>贈与財産が<strong>居住用不動産</strong>、またはそれを取得するための<strong>金銭</strong>であること</li><li>贈与を受けた配偶者が、その不動産に<strong>翌年3月15日まで</strong>に居住し、その後も住み続ける見込みであること</li><li><strong>贈与税の申告が必須</strong>（控除の結果、税額が0になる場合でも申告が必要）</li></ul>'), ('相続対策としてのメリット', '<p>大きな利点は、おしどり贈与で渡した2,000万円分が<strong>生前贈与加算の対象外</strong>になることです。暦年贈与は相続前の一定期間（最長7年へ延長中）の分が相続財産に持ち戻されますが、配偶者控除を使った2,000万円分は持ち戻されません。</p><p>配偶者には相続時に「配偶者の税額軽減（最大1.6億円）」もあるため、両制度をどう組み合わせるかが相続対策のポイントになります。</p>'), ('見落としやすい注意点', '<p>非課税でも「タダ」ではありません。不動産の名義変更には次のコストがかかります。</p><ul><li><strong>登録免許税</strong>：贈与は固定資産税評価額の2%（相続による移転は0.4%）</li><li><strong>不動産取得税</strong>：贈与では課税される（相続では非課税）</li></ul><p>このため、自宅をそのまま相続で渡したほうが税コストが小さくなるケースもあります。「使えば必ず得」ではない点に注意し、税理士に試算してもらうのがおすすめです。最新の税率・要件は<strong>国税庁の公表資料</strong>で確認してください。</p>')], 'faqs': [('内縁関係でも使えますか？', '使えません。贈与税の配偶者控除は、法律上の婚姻関係にある配偶者が対象です。内縁関係には適用されません。'), ('税額が0なら申告しなくてもいいですか？', 'いいえ。この特例は申告が適用の条件です。控除の結果として贈与税が0円になる場合でも、必ず贈与税の申告をしてください。'), ('自宅の持分の一部だけ贈与してもいいですか？', '可能です。評価額が2,000万円を超える自宅でも、持分の一部を2,000万円分まで贈与する形で活用できます。具体的な持分の決め方は専門家に相談すると確実です。')]}, {'slug': 'housing-fund-gift', 'title': '住宅取得等資金の贈与の非課税｜最大1,000万円・要件と期限', 'h1': '住宅取得等資金の贈与の非課税特例', 'desc': '父母・祖父母から住宅取得資金の贈与を受けると一定額まで非課税になる特例を解説。良質な住宅で最大1,000万円・一般500万円の枠、所得や床面積などの要件、暦年・精算課税との併用、申告の必要性をまとめます。', 'keywords': '住宅取得等資金の贈与,非課税,1000万円,要件,省エネ住宅,直系尊属', 'lead': 'マイホームの購入資金を親や祖父母から援助してもらうとき、<strong>住宅取得等資金の贈与の非課税特例</strong>（租税特別措置法70条の2）を使うと、一定額まで贈与税がかかりません。枠・要件・期限を正しく押さえることが大切です。', 'sections': [('非課税になる金額', '<p>父母・祖父母（直系尊属）から、住宅の新築・取得・増改築のための資金贈与を受けた場合、住宅の性能に応じて次の額まで非課税になります。</p><ul><li><strong>省エネ等の良質な住宅</strong>：最大1,000万円</li><li><strong>それ以外の一般住宅</strong>：500万円</li></ul><p>この枠は暦年課税の110万円や相続時精算課税の特別控除と<strong>併用できます</strong>。たとえば一般住宅なら、500万円＋暦年110万円＝610万円までを非課税にできる計算です。</p>'), ('主な要件', '<ul><li>贈与を受けた年の1月1日時点で<strong>18歳以上</strong>であること</li><li>受贈者の合計所得金額が<strong>2,000万円以下</strong>（床面積40㎡以上50㎡未満の場合は1,000万円以下）</li><li>住宅の<strong>床面積が40㎡以上240㎡以下</strong>で、その2分の1以上が居住用であること</li><li>贈与を受けた年の<strong>翌年3月15日まで</strong>に住宅を取得し、居住するか居住が確実と見込まれること</li></ul>'), ('使うときの流れと注意点', '<p>非課税の適用を受けるには、税額が0になる場合でも<strong>贈与税の申告が必須</strong>です。贈与を受けた年の翌年2月1日〜3月15日に、必要書類（登記事項証明書、契約書の写しなど）を添えて申告します。</p><p>「資金の贈与」が対象であり、<strong>すでに建っている家そのものの贈与は対象外</strong>です。また、贈与を受けてから家を買うという順番（資金を先に受け取る）が原則です。</p>'), ('期限と最新情報の確認', '<p>この特例は適用期限や非課税枠が法改正で見直される制度です。現行では<strong>2026年12月31日まで</strong>の贈与が対象とされていますが、金額・要件・期限は変更されることがあります。</p><p>マイホーム計画に組み込む際は、必ず<strong>国税庁の公表資料</strong>で最新の枠と期限を確認し、住宅ローン控除との兼ね合いも含めて税理士に相談すると安心です。</p>')], 'faqs': [('親からの借入とどちらが得ですか？', '贈与は非課税枠を使えますが、枠を超える部分には贈与税がかかります。親子間の借入は、無利子・あいまいな返済だと「贈与とみなされる」リスクがあるため、契約書・返済実績をきちんと残すことが重要です。状況により有利不利が変わるので専門家に相談してください。'), ('土地だけの購入資金でも使えますか？', '原則として、住宅とともに取得する土地の資金は対象になりますが、土地だけを先行取得するケースなど扱いが細かく分かれます。具体的な可否は国税庁の資料や税理士に確認してください。'), ('贈与を受けたのに家の完成が遅れたら？', '翌年3月15日までに新築工事が完了していなくても、棟上げ（屋根を有する状態）まで進んでいれば適用できる場合があります。期限に間に合わないと特例が使えず課税されることがあるため、工程には余裕を持たせてください。')]}, {'slug': 'substitution-inheritance', 'title': '代襲相続とは｜範囲・相続分・再代襲をわかりやすく解説', 'h1': '代襲相続の範囲と相続分', 'desc': '相続人になるはずの子や兄弟姉妹が先に亡くなっている場合に、その子（孫・甥姪）が代わりに相続する代襲相続を解説。再代襲の有無、相続放棄との違い、相続分の計算を具体例で整理します。', 'keywords': '代襲相続,範囲,相続分,孫,甥姪,再代襲,相続放棄', 'lead': '<strong>代襲相続（だいしゅうそうぞく）</strong>とは、本来相続人になるはずだった子や兄弟姉妹が被相続人より先に亡くなっているとき、その人の子が代わりに相続することをいいます（民法887条2項など）。誰がどこまで代襲できるか、相続分はどうなるかを整理します。', 'sections': [('代襲相続が起きるケース', '<p>次の場合に、本来の相続人の<strong>子</strong>が代わって相続人になります。</p><ul><li>相続人になるはずの人が<strong>被相続人より先に死亡</strong>している</li><li>その人が<strong>相続欠格</strong>に当たる、または<strong>廃除</strong>されている</li></ul><p>重要なのは、<strong>相続放棄は代襲の原因にならない</strong>点です（民法939条）。放棄した人は「初めから相続人でなかった」とみなされ、その子も代襲しません。一方、欠格・廃除の場合はその子が代襲します。</p>'), ('どこまで代襲できるか（範囲）', '<p>代襲できる範囲は、相続人の立場によって異なります。</p><ul><li><strong>子の系統</strong>：子が先に死亡 → 孫が代襲。孫も死亡なら曽孫へと続く（<strong>再代襲あり・無限</strong>、民法887条3項）</li><li><strong>兄弟姉妹の系統</strong>：兄弟姉妹が先に死亡 → 甥・姪が代襲。ただし<strong>一代限り</strong>で、甥姪の子は代襲しない（再代襲なし）</li></ul><p>直系尊属（親・祖父母）には代襲という考え方はなく、近い世代の人が順に相続人になります。</p>'), ('代襲相続人の相続分', '<p>代襲相続人は、<strong>本来の相続人（被代襲者）が受けるはずだった相続分</strong>を引き継ぎます。代襲者が複数いる場合は、その相続分を頭数で按分します。</p><p>例：被相続人の遺産6,000万円、相続人が長男と次男だが長男はすでに死亡し、長男に子（孫）が2人いるケース。</p><ul><li>次男：6,000万円 × 1/2 ＝ <strong>3,000万円</strong></li><li>孫A・孫B：長男の取り分3,000万円を2人で按分 ＝ 各<strong>1,500万円</strong></li></ul>'), ('間違えやすいポイント', '<p>養子の子が代襲するかどうかは、生まれた時期で変わります。<strong>養子縁組の後に生まれた子</strong>は代襲しますが、<strong>縁組前から養子にいた連れ子</strong>は被相続人と血縁がないため代襲しません。</p><p>相続税では、孫が代襲相続人として相続する場合は2割加算の対象外ですが、代襲でない孫養子などは2割加算の対象になります。判断が難しいケースは、司法書士・税理士などの専門家に相続関係を確認してもらうと確実です。</p>')], 'faqs': [('親が相続放棄したら、その子（孫）は相続できますか？', 'できません。相続放棄は代襲の原因にならないため、放棄した人の子は代襲しません。放棄により次順位（親や兄弟姉妹）へ相続権が移ります。'), ('甥や姪の子は代襲できますか？', 'できません。兄弟姉妹の代襲は甥・姪までの一代限りで、再代襲はありません。子の系統（孫・曽孫）の無限代襲とは扱いが異なります。'), ('代襲相続人にも遺留分はありますか？', '子の系統の代襲相続人（孫など）には遺留分があります。一方、兄弟姉妹にはもともと遺留分がないため、その代襲相続人である甥姪にも遺留分はありません。')]}, {'slug': 'special-contribution-fee', 'title': '特別寄与料とは｜相続人以外の親族（嫁など）の貢献を金銭請求', 'h1': '特別寄与料（相続人以外の貢献）', 'desc': '長男の嫁など相続人でない親族が被相続人を無償で介護した場合に、相続人へ金銭を請求できる特別寄与料（2019年新設）を解説。寄与分との違い、請求できる人、6か月・1年の期限、相続税の扱いまでまとめます。', 'keywords': '特別寄与料,相続人以外,嫁,2019年,請求,寄与分,療養看護', 'lead': '義理の親を長年介護したのに、相続人でないため一切財産をもらえない——そんな不公平を和らげるため、2019年に<strong>特別寄与料</strong>の制度が新設されました（民法1050条）。相続人でない親族が、貢献に応じた金銭を相続人へ請求できる仕組みです。', 'sections': [('特別寄与料とは', '<p><strong>特別寄与料</strong>は、相続人でない親族が、被相続人を<strong>無償で療養看護</strong>するなどして財産の維持・増加に特別の貢献をした場合に、相続人に対して金銭の支払いを請求できる制度です（民法1050条、2019年7月1日施行）。</p><p>典型例は「<strong>長男の嫁</strong>が義父母を長年介護したケース」です。嫁は相続人ではないため従来は何ももらえませんでしたが、この制度で貢献を金銭として評価できるようになりました。</p>'), ('寄与分との違い', '<p>似た制度に「寄与分」がありますが、対象者が異なります。</p><ul><li><strong>寄与分</strong>（民法904条の2）：<strong>相続人</strong>の貢献を、その人の相続分に上乗せして評価する</li><li><strong>特別寄与料</strong>（民法1050条）：<strong>相続人でない親族</strong>の貢献を、相続人への金銭請求として評価する</li></ul><p>請求できるのは「<strong>被相続人の親族</strong>」（6親等内の血族・3親等内の姻族）で、内縁の配偶者や友人・知人は含まれません。</p>'), ('請求の流れと期限', '<p>まずは相続人と<strong>協議</strong>し、まとまらなければ<strong>家庭裁判所</strong>に協議に代わる処分を申し立てます。金額は、貢献の内容・期間・程度などを踏まえて決められます。</p><p>注意したいのが<strong>期限</strong>です。特別寄与料の請求は、<strong>相続開始と相続人を知った時から6か月</strong>、または<strong>相続開始から1年</strong>を過ぎると、家庭裁判所への申立てができなくなります（民法1050条2項但書）。短い期間なので早めの行動が必要です。</p>'), ('相続税の扱い', '<p>特別寄与料を受け取った人は、被相続人から<strong>遺贈を受けたものとみなされて</strong>相続税の対象になります。配偶者や一親等の血族以外なので、相続税額の<strong>2割加算</strong>の対象になる点にも注意が必要です。</p><p>金額の決め方や証拠（介護記録・領収書など）の整え方は判断が難しいため、弁護士・税理士などの専門家に早めに相談することをおすすめします。</p>')], 'faqs': [('介護の記録がないと請求できませんか？', '請求自体は可能ですが、貢献の程度を裏づける記録（介護日誌、医療・介護費の領収書、メモなど）があるほど金額交渉や調停で有利になります。日頃から記録を残しておくことが大切です。'), ('少しだけ手伝った程度でも請求できますか？', '通常の親族間の助け合いを超える「特別の寄与」が必要とされます。短期間・軽微な手伝いでは認められにくく、無償で継続的に療養看護を担ったといえる程度が目安になります。'), ('内縁の妻でも特別寄与料を請求できますか？', 'できません。請求できるのは法律上の親族（6親等内の血族・3親等内の姻族）に限られ、内縁の配偶者は含まれません。内縁の場合は遺言や特別縁故者の制度などで備える必要があります。')]}, {'slug': 'estate-administrator', 'title': '相続財産清算人と特別縁故者｜相続人がいない遺産のゆくえ', 'h1': '相続人がいない場合（相続財産清算人・特別縁故者）', 'desc': '相続人が誰もいない、または全員が放棄した場合の遺産の扱いを解説。2023年改正で名称が変わった相続財産清算人の選任、内縁の配偶者など特別縁故者への分与、最終的な国庫帰属までの流れと、おひとりさまの備えをまとめます。', 'keywords': '相続財産清算人,特別縁故者,相続人不存在,国庫帰属,おひとりさま,相続財産管理人', 'lead': '相続人が一人もいない、あるいは全員が相続放棄した場合、遺産は誰のものになるのでしょうか。こうしたケースでは<strong>相続財産清算人</strong>が選ばれ、債務の清算や<strong>特別縁故者</strong>への分与を経て、残れば国のものになります。流れを整理します。', 'sections': [('相続人不存在とは', '<p>「相続人がいない」とは、配偶者も子も親も兄弟姉妹もいない場合のほか、相続人全員が<strong>相続放棄</strong>して誰も相続しなくなった場合も含みます。こうした状態を<strong>相続人不存在</strong>といいます。</p><p>このとき遺産は宙に浮くため、家庭裁判所が管理・清算する人を選任して手続きを進めます。</p>'), ('相続財産清算人の選任（2023年改正）', '<p>2023年4月の民法改正で、従来の「相続財産管理人」は<strong>相続財産清算人</strong>に名称が変わり、手続きも合理化されました。</p><p>債権者や受遺者、特別縁故者になり得る人などの<strong>利害関係人</strong>、または検察官が家庭裁判所に申し立てると、清算人が選ばれます。清算人は、官報での公告を経て相続人を捜索し、被相続人の<strong>債務を弁済</strong>し、財産を整理します。</p>'), ('特別縁故者への財産分与', '<p>相続人がいないと確定した後、被相続人と特別の縁故があった人は、家庭裁判所に<strong>財産分与の申立て</strong>ができます（民法958条の2）。これを<strong>特別縁故者</strong>といいます。</p><ul><li>被相続人と<strong>生計を同じくしていた人</strong>（内縁の配偶者など）</li><li>被相続人の<strong>療養看護に努めた人</strong></li><li>その他、被相続人と特別に親しかった人</li></ul><p>申立てには期限があり、相続人捜索の公告期間満了後<strong>3か月以内</strong>に行う必要があります。</p>'), ('最終的に残れば国庫へ／おひとりさまの備え', '<p>債務の弁済も特別縁故者への分与も済んだうえで財産が残った場合、その遺産は<strong>国庫に帰属</strong>します（民法959条）。つまり、何も備えをしないと、内縁の相手や世話になった人に渡らず国のものになることがあります。</p><p>身寄りのない「おひとりさま」は、<strong>遺言書</strong>で渡したい相手を指定したり、死後事務委任契約を結んでおくことで、自分の意思を反映できます。具体的な備えは弁護士・司法書士に相談すると安心です。</p>')], 'faqs': [('内縁の配偶者は何ももらえないのですか？', '法定相続人ではないため自動的には相続できませんが、特別縁故者として家庭裁判所に財産分与を申し立てることができます。ただし認められるかは事情によるため、遺言で備えておくほうが確実です。'), ('相続財産清算人は誰でも申し立てられますか？', '利害関係人（債権者・受遺者・特別縁故者になり得る人など）または検察官が申し立てられます。申立てには予納金が必要になることが一般的です。'), ('相続人全員が放棄したら借金はどうなりますか？', '相続放棄すれば相続人は借金を負いません。残った財産は相続財産清算人が管理し、その範囲で債権者へ弁済されます。プラス財産を超える債務は、原則として誰も負担しません。')]}, {'slug': 'invalid-will', 'title': '遺言書が無効になるケース｜要件不備・遺言能力・無効の争い方', 'h1': '遺言書が無効になるケースと対策', 'desc': 'せっかくの遺言書が無効になってしまう典型例を解説。自筆証書遺言の方式不備、遺言能力の欠如、共同遺言の禁止などの無効原因と、無効を争う手続き、そして無効を防ぐ作成上の注意点をまとめます。', 'keywords': '遺言無効,遺言能力,要件不備,自筆証書遺言,無効確認の訴え,公正証書遺言', 'lead': '遺言書は、書き方や状態によっては<strong>無効</strong>になってしまいます。無効になると故人の意思が反映されず、かえって争いの種になることも。本記事では遺言が無効になる典型例と、無効を防ぐための注意点を整理します。', 'sections': [('方式の不備による無効', '<p>とくに<strong>自筆証書遺言</strong>は、形式が法律で厳格に決められており（民法968条）、満たさないと無効になります。</p><ul><li><strong>全文を自書</strong>していない（本文をパソコンで作成した等。※財産目録はワープロ可だが各ページに署名押印が必要）</li><li><strong>日付がない</strong>、または「令和7年5月吉日」のように日が特定できない</li><li><strong>氏名の自書や押印がない</strong></li><li>加除訂正の方法が法定のルールに従っていない</li></ul><p>こうした不備は意外に多く、<strong>法務局の自筆証書遺言書保管制度</strong>や<strong>公正証書遺言</strong>を使うと方式不備のリスクを減らせます。</p>'), ('遺言能力の欠如による無効', '<p>遺言は<strong>満15歳以上</strong>でなければできず（民法961条）、さらに遺言をするときに<strong>意思能力</strong>（遺言の内容を理解し判断する力）が必要です。</p><p>重度の認知症などで判断能力を欠いた状態で書かれた遺言は、<strong>遺言能力がなかった</strong>として無効を主張されることがあります。実務では、作成時の診断書や医療記録が争点になります。</p>'), ('その他の無効原因', '<ul><li><strong>共同遺言の禁止</strong>：2人以上が同一の証書で一緒に作った遺言は無効（民法975条。夫婦連名でも不可）</li><li><strong>錯誤・詐欺・強迫</strong>：だまされたり脅されて書いた遺言は取り消し得る</li><li><strong>内容が不明確</strong>：誰に何を渡すのか特定できない</li><li><strong>公序良俗違反</strong>：法律上認められない内容</li></ul><p>なお、遺留分を侵害する遺言は「無効」ではなく、侵害された相続人が<strong>遺留分侵害額請求</strong>をできるという扱いになります。</p>'), ('無効を争う方法と予防', '<p>遺言が無効ではないかと争う場合、まず家庭裁判所の<strong>調停</strong>を経て、まとまらなければ<strong>遺言無効確認の訴え</strong>（地方裁判所）で決着をつけます。立証の負担は重く、時間も費用もかかります。</p><p>無用な争いを避けるには、<strong>公正証書遺言</strong>を使う、作成時に<strong>医師の診断書</strong>を残す、専門家に関与してもらうといった備えが有効です。遺言の作成・見直しは、弁護士・司法書士・公証人などに相談しながら進めると安心です。</p>')], 'faqs': [('日付を「吉日」と書いたら無効ですか？', 'はい。「令和7年5月吉日」のように日が特定できない書き方は、自筆証書遺言として無効と判断されます。年月日を具体的に記載してください。'), ('夫婦で1枚の紙に一緒に遺言を書けますか？', '書けません。2人以上が同一の証書で行う共同遺言は禁止されており無効です（民法975条）。夫婦でもそれぞれ別の遺言書を作成してください。'), ('認知症だと必ず遺言は無効ですか？', '必ず無効になるわけではありません。認知症でも、遺言時に内容を理解し判断できる状態（意思能力）があれば有効です。後の争いに備え、診断書や作成時の状況を記録しておくと安心です。')]}]


# --- 2026-06 SEOギャップ第2弾5記事(財産調査/遺産分割やり直し/特別代理人/相続放棄後の保存義務/死亡保険金請求) ---
ARTICLES += [{'slug': 'asset-investigation', 'title': '相続財産の調査と財産目録の作り方｜預貯金・不動産・借金の探し方', 'h1': '相続財産の調査・財産目録の作り方', 'desc': '亡くなった方の財産がどこに何があるか分からない——相続でまず必要になる財産調査の進め方を解説。預貯金・不動産・有価証券・借金の探し方と、財産目録の作り方、相続放棄の判断との関係まで整理します。', 'keywords': '相続財産調査,財産目録,借金の調べ方,名寄帳,信用情報,相続放棄', 'lead': '相続が始まってまず行き詰まりやすいのが「<strong>そもそも何が遺産なのか分からない</strong>」という壁です。財産の全体像が分からないと、遺産分割も相続税も、相続放棄の判断もできません。財産調査の進め方を整理します。', 'sections': [('なぜ最初に財産調査が必要か', '<p>遺産には、預貯金や不動産といったプラスの財産だけでなく、借金や保証債務といったマイナスの財産もあります。これらを把握しないまま手続きを進めると、後から財産が見つかって分割をやり直す手間や、<strong>想定外の借金</strong>を背負うリスクが生じます。</p><p>とくに<strong>相続放棄は原則3か月以内</strong>という期限があるため、借金の有無を早めに調べることが大切です。</p>'), ('財産の種類別・探し方', '<ul><li><strong>預貯金</strong>：通帳・キャッシュカード・郵便物から取引銀行を特定し、残高証明書を取得</li><li><strong>不動産</strong>：固定資産税の納税通知書や、市区町村の<strong>名寄帳（固定資産課税台帳）</strong>で所有不動産を確認</li><li><strong>有価証券</strong>：証券会社からの郵便物、証券保管振替機構（ほふり）への照会</li><li><strong>借金・ローン</strong>：契約書や請求書のほか、信用情報機関（JICC・CIC・KSC）に開示請求して把握する方法がある</li></ul>'), ('財産目録を作る', '<p>調べた財産は、<strong>財産目録</strong>として一覧にまとめます。プラスの財産（種類・金額・所在）とマイナスの財産（借入先・残高）を並べると、相続税がかかりそうか、相続放棄を検討すべきかの判断材料になります。</p><p>遺産分割協議書を作る際の基礎資料にもなるため、できるだけ早い段階で着手すると、その後の手続きが楽になります。</p>'), ('見つからない・分からないとき', '<p>すべてを自力で調べきれない場合もあります。金融機関や役所での手続きには戸籍などの書類が必要で、時間もかかります。手に負えないと感じたら、<strong>司法書士・税理士・弁護士</strong>に調査を依頼するのも一つの方法です。最新の照会方法や必要書類は、各機関の公式案内で確認してください。</p>')], 'faqs': [('借金があるかどうか、どう調べればいいですか？', '契約書や督促状などの郵便物を確認するほか、信用情報機関（JICC・CIC・KSC）に開示請求すると、貸金やクレジットの借入状況を把握できます。連帯保証は信用情報に出ないこともあるため、書類の確認も併せて行いましょう。'), ('不動産をすべて把握する方法はありますか？', '市区町村ごとに名寄帳（固定資産課税台帳）を取得すると、その自治体内の所有不動産を一覧で確認できます。複数の地域に不動産がある場合は、それぞれの自治体で取得が必要です。'), ('財産目録は必ず作らないといけませんか？', '法律上の義務ではありませんが、相続税の要否判断や遺産分割、相続放棄の検討に役立つため、作成をおすすめします。限定承認を選ぶ場合は財産目録の提出が必要です。')]}, {'slug': 'division-redo', 'title': '遺産分割のやり直しはできる？｜無効になるケースと税務の注意点', 'h1': '遺産分割のやり直しと注意点', 'desc': '一度まとまった遺産分割協議をやり直せるのか、という疑問に答えます。原則やり直せない理由と、例外的に認められるケース、やり直しに伴う贈与税・譲渡所得税のリスクまで、トラブルを避けるために知っておきたい点を解説します。', 'keywords': '遺産分割,やり直し,無効,取消,贈与税,協議のやり直し', 'lead': '「分け方に納得がいかない」「後から財産が出てきた」——成立した遺産分割をやり直したい場面はあります。ただし、やり直しは<strong>原則として簡単には認められず</strong>、認められても税金の問題が絡みます。考え方を整理します。', 'sections': [('原則：成立した協議はやり直せない', '<p>遺産分割協議は、相続人全員が合意して成立すると、法的に確定した取り決めになります。後から「やっぱり不公平だ」と感じても、<strong>原則としてやり直し（再分割）はできません</strong>。これは、いったん決まった権利関係を安定させるためです。</p>'), ('例外的にやり直せる・無効になるケース', '<ul><li><strong>相続人全員が再分割に合意した</strong>場合（ただし税務上の注意あり・後述）</li><li>協議に<strong>詐欺・強迫・錯誤</strong>があり、取消しや無効を主張できる場合（民法）</li><li>協議後に<strong>新たな相続人や遺言が見つかった</strong>場合（前提が崩れる）</li><li>一部の財産が<strong>協議から漏れていた</strong>場合（その財産についてのみ協議が必要）</li></ul>'), ('やり直しに潜む税金のリスク', '<p>注意したいのが税務です。相続人全員の合意で再分割した場合、税務上は<strong>いったん取得した財産を、別の相続人へ贈与または譲渡した</strong>とみなされることがあります。すると、相続税とは別に<strong>贈与税や譲渡所得税</strong>が課される可能性があります。</p><p>「全員が納得しているから問題ない」と安易に進めると、思わぬ課税につながりかねません。再分割を検討する際は、税理士に相談するのが安全です。'), ('トラブルを防ぐために', '<p>やり直しの多くは、最初の協議が不十分だったことに端を発します。<strong>財産の調査を尽くす</strong>、<strong>協議書を丁寧に作る</strong>、不明点は専門家に確認する——この積み重ねが、後のやり直しを防ぎます。最新の税務の取扱いは国税庁の情報や税理士で確認してください。</p>')], 'faqs': [('相続人全員が合意すればやり直せますか？', '全員の合意があれば再分割自体は可能ですが、税務上は贈与や譲渡とみなされ、贈与税や譲渡所得税がかかる場合があります。安易に行わず、税理士に相談することをおすすめします。'), ('協議の後に遺言書が見つかったらどうなりますか？', '遺言の内容によっては、協議の前提が崩れ、やり直しが必要になることがあります。遺言が優先されるのが原則ですが、相続人全員が遺言と異なる分割に合意する余地もあります。状況により判断が分かれるため専門家に相談しましょう。'), ('錯誤や勘違いで合意した場合は取り消せますか？', '重要な点に関する錯誤や、詐欺・強迫があった場合は、取消しや無効を主張できる余地があります。ただし立証が必要で争いになりやすいため、早めに弁護士へ相談するのが現実的です。')]}, {'slug': 'special-agent-minor', 'title': '未成年の相続人と特別代理人｜親が代理できない「利益相反」とは', 'h1': '未成年の相続人と特別代理人', 'desc': '未成年の子と親がともに相続人になる場合、親が子を代理して遺産分割すると利益相反になり認められません。特別代理人の選任が必要になる理由と、家庭裁判所への申立ての流れ、認知症の相続人との違いを解説します。', 'keywords': '特別代理人,未成年,利益相反,遺産分割,民法826条,家庭裁判所', 'lead': '親が亡くなり、配偶者と未成年の子が相続人になる——よくあるケースですが、ここには落とし穴があります。<strong>親が子の代理人として遺産分割を進めることが、原則できない</strong>のです。理由と手続きを整理します。', 'sections': [('なぜ親が代理できないのか（利益相反）', '<p>遺産分割では、相続人どうしが取り分を分け合います。親（配偶者）と未成年の子がともに相続人の場合、親が子を代理すると、<strong>親が自分と子の取り分を一人で決める</strong>ことになり、子の利益が害されるおそれがあります。これを<strong>利益相反</strong>といい、民法826条により親はその行為について子を代理できません。</p>'), ('特別代理人の選任が必要', '<p>そこで、子のために<strong>特別代理人</strong>を立てます。家庭裁判所に選任を申し立て、選ばれた特別代理人が、その子に代わって遺産分割協議に加わります。未成年の子が複数いる場合は、原則として<strong>子ごとに別々の特別代理人</strong>が必要です。</p>'), ('手続きの流れ', '<ul><li>親など（親権者）が、子の住所地を管轄する家庭裁判所に<strong>特別代理人選任の申立て</strong>を行う</li><li>遺産分割協議書の案を添えて提出するのが一般的（分割内容の妥当性も見られる）</li><li>家庭裁判所が特別代理人を選任（祖父母や叔父叔母など親族、または専門家がなることが多い）</li><li>特別代理人を加えて遺産分割協議を行う</li></ul>'), ('認知症の相続人との違い', '<p>判断能力が不十分な相続人（認知症など）がいる場合は、特別代理人ではなく<strong>成年後見人</strong>の選任が必要になります。さらに後見人と本人がともに相続人で利益相反になるときは、別途特別代理人が必要になることもあります。判断が難しいため、司法書士・弁護士などに相談すると確実です。</p>')], 'faqs': [('子の取り分を法定相続分どおりにしても特別代理人は必要ですか？', 'はい。分割内容にかかわらず、親と未成年の子がともに相続人で利益相反となる場合は、特別代理人の選任が必要です。家庭裁判所は分割内容が子に不利でないかも確認します。'), ('特別代理人には誰がなれますか？', '利益相反のない親族（祖父母や叔父叔母など）が選ばれることが多いですが、適任者がいない場合は司法書士や弁護士などの専門家が選ばれることもあります。最終的には家庭裁判所が判断します。'), ('申立てに費用や時間はかかりますか？', '収入印紙や郵券などの実費がかかり、選任までに数週間程度かかるのが一般的です。相続税の申告期限なども踏まえ、早めに申し立てると安心です。')]}, {'slug': 'renounce-duty', 'title': '相続放棄後の管理（保存）義務｜2023年改正で変わった実家・空き家の扱い', 'h1': '相続放棄したあとの保存義務（2023年改正）', 'desc': '相続放棄をすれば財産も負担もすべて手放せる、と考えがちですが、放棄時に占有していた財産には保存義務が残ることがあります。2023年4月の民法改正で整理された相続放棄後の管理責任と、実家・空き家の扱いを解説します。', 'keywords': '相続放棄,管理義務,保存義務,2023年改正,民法940条,空き家', 'lead': '「相続放棄をすれば、実家も借金もすべて関係なくなる」——多くはそうですが、<strong>放棄したあとも一定の責任が残る</strong>場合があります。2023年4月の民法改正で扱いが整理されたこのテーマを解説します。', 'sections': [('相続放棄をしても残ることがある「保存義務」', '<p>相続放棄をすると、その人は初めから相続人でなかったものとみなされ、原則として財産も債務も引き継ぎません。ただし、<strong>放棄の時点でその財産を現に占有していた</strong>場合には、次に管理すべき人に引き継ぐまで、その財産を<strong>保存する義務</strong>が残ります（民法940条）。</p>'), ('2023年改正で何が変わったか', '<p>2023年4月施行の改正で、この義務が整理されました。改正前は「管理を継続する義務」とされ範囲が曖昧でしたが、改正後は<strong>「放棄時に現に占有している財産」を対象に、自己の財産と同一の注意をもって保存する</strong>義務へと明確化されました。実際に住んでいた実家などが典型例です。</p>'), ('実家・空き家はどう扱うか', '<p>放棄したからといって、占有していた実家をすぐに放置してよいわけではありません。次の相続人や、相続人がいなければ<strong>相続財産清算人</strong>に引き継ぐまで、最低限の保存が求められることがあります。誰も相続せず管理者も決まらない場合は、家庭裁判所に相続財産清算人の選任を申し立てる方法があります。</p>'), ('判断に迷ったら', '<p>「自分に保存義務があるのか」「いつまで管理が必要か」は、占有の有無や他の相続人の状況によって変わり、判断が難しい部分です。空き家の管理リスク（倒壊・近隣トラブル）もあるため、迷う場合は弁護士・司法書士に相談してください。最新の条文・運用は法務省などの公式情報で確認しましょう。</p>')], 'faqs': [('相続放棄すれば実家を放置してもいいですか？', '放棄時にその実家を現に占有していた場合は、次に管理すべき人へ引き継ぐまで保存義務が残ることがあります。放置すると倒壊や近隣トラブルの責任を問われかねないため、引継ぎ先を確保するまでは最低限の管理が必要です。'), ('いつまで管理しないといけませんか？', '次の相続人や相続財産清算人など、管理すべき人に引き継ぐまでが目安です。相続人が誰もいない場合は、家庭裁判所に相続財産清算人の選任を申し立てて引き継ぐ方法があります。'), ('相続人全員が放棄したら家はどうなりますか？', '管理する相続人がいなくなるため、利害関係人が家庭裁判所へ相続財産清算人の選任を申し立て、清算人が管理・処分します。最終的に残った財産は国庫に帰属します。')]}, {'slug': 'life-insurance-claim', 'title': '死亡保険金の受け取り方｜請求の手続き・必要書類と税金の扱い', 'h1': '死亡保険金の請求手続きと税金', 'desc': '亡くなった方の死亡保険金を受け取る手続きを解説。保険会社への連絡から必要書類、3年の請求期限までの流れと、受取人と契約者の関係で相続税・所得税・贈与税のどれになるか、非課税枠の考え方も整理します。', 'keywords': '死亡保険金,請求手続き,必要書類,受取人,相続税,非課税枠', 'lead': '<strong>死亡保険金</strong>は、遺された家族の生活を支える大切なお金です。受け取りには請求の手続きが必要で、税金の扱いも契約の形によって変わります。手続きの流れと税金の基本を整理します。', 'sections': [('保険金は「受取人固有の財産」', '<p>受取人が指定された死亡保険金は、原則として<strong>受取人固有の財産</strong>であり、遺産分割の対象には含まれません。そのため、相続放棄をした人でも、受取人になっていれば保険金は受け取れます（ただし税務上の扱いは別途確認が必要です）。</p>'), ('請求の流れと期限', '<ul><li>保険会社に<strong>被保険者が亡くなった旨を連絡</strong>する</li><li>案内に従って請求書類を準備・提出する</li><li>審査を経て、指定口座に保険金が支払われる</li></ul><p>保険金の請求には<strong>時効（一般に3年）</strong>があるとされています。忘れずに、早めに手続きしましょう。'), ('主な必要書類', '<p>保険会社や契約により異なりますが、一般的には次のような書類が求められます。</p><ul><li>保険証券、請求書（保険会社所定）</li><li>被保険者の死亡を証明する書類（死亡診断書の写しなど）</li><li>受取人の本人確認書類・戸籍関係の書類</li></ul>'), ('税金はどうなるか', '<p>死亡保険金にかかる税金は、<strong>契約者（保険料負担者）・被保険者・受取人の関係</strong>で変わります。</p><ul><li>契約者と被保険者が同じで、受取人が相続人 → <strong>相続税</strong>（<strong>500万円×法定相続人数</strong>の非課税枠あり）</li><li>契約者と受取人が同じ → 受取人の<strong>所得税</strong></li><li>契約者・被保険者・受取人がすべて異なる → <strong>贈与税</strong></li></ul><p>非課税枠や税区分は誤解しやすいため、最新の取扱いは国税庁の資料や税理士で確認してください。</p>')], 'faqs': [('死亡保険金は遺産分割の対象になりますか？', '受取人が指定されている場合、原則として受取人固有の財産となり、遺産分割の対象には含まれません。ただし、保険金が遺産に対して著しく高額な場合などは、例外的に持ち戻しが問題になることもあります。'), ('相続放棄しても保険金は受け取れますか？', '受取人として指定されていれば、相続放棄をしても死亡保険金は受け取れるのが原則です。ただし、相続税の非課税枠は放棄した人には適用されないなど税務上の違いがあるため、確認が必要です。'), ('いつまでに請求すればいいですか？', '保険金の請求権には一般に3年の時効があるとされています。期限を過ぎると受け取れなくなるおそれがあるため、できるだけ早く保険会社に連絡しましょう。')]}]

if __name__ == "__main__":
    main()
