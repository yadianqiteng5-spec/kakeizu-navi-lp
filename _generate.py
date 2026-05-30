"""記事ページ一括生成スクリプト。data 配列を編集して python _generate.py で再生成。"""
import os
import json
from pathlib import Path

ROOT = Path(__file__).parent
APP_URL = "https://kakeizu-navi-3joa5l78sjkams2axwbxix.streamlit.app/"
SITE_URL = "https://yadianqiteng5-spec.github.io/kakeizu-navi-lp"
ICON = f"{SITE_URL}/icon_512.png"

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


def render(article, related_links):
    title = article["title"]
    desc = article["desc"]
    h1 = article["h1"]
    slug = article["slug"]
    url = f"{SITE_URL}/{slug}/"

    sections_html = "\n".join(
        f'<h2>{i+1}. {h2}</h2>\n{body}'
        for i, (h2, body) in enumerate(article["sections"])
    )
    faq_html = "\n".join(
        f'<details><summary>{q}</summary><p>{a}</p></details>'
        for q, a in article["faqs"]
    )
    related_html = "\n".join(
        f'<li><a href="../{s}/">{t}</a></li>'
        for s, t in related_links
    )

    article_jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1,
        "description": desc,
        "image": ICON,
        "datePublished": "2026-05-30",
        "dateModified": "2026-05-30",
        "author": {"@type": "Person", "name": "DrumNavi"},
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
    breadcrumb_jsonld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "家系図Navi", "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": h1, "item": url},
        ],
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
  <meta name="author" content="DrumNavi">
  <link rel="canonical" href="{url}">
  <link rel="alternate" hreflang="ja" href="{url}">

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
    .disclaimer {{ background: #fff8e1; border-left: 4px solid #f39c12; padding: 1rem 1.2rem; border-radius: 4px; font-size: .9rem; margin: 2rem 0; }}
    footer {{ text-align: center; padding: 2rem; font-size: .85rem; color: #888; border-top: 1px solid #eee; }}
    footer a {{ color: var(--green); text-decoration: none; }}
  </style>
</head>
<body>

<header>
  <div class="nav"><a href="../">🌳 家系図Navi</a> ＞ {h1}</div>
  <h1>{h1}</h1>
  <p class="lead">{desc}</p>
  <a class="cta" href="{APP_URL}" rel="noopener">無料シミュレーターを試す →</a>
</header>

<main>

  <p>{article["lead"]}</p>

  {sections_html}

  <h2>よくある質問</h2>
  {faq_html}

  <div class="cta-box">
    <h3>家族構成を入力するだけで自動診断</h3>
    <p>法定相続分・相続税・遺留分を国税庁公表値準拠で計算。データ保存なしの完全無料アプリ。</p>
    <a href="{APP_URL}" rel="noopener">家系図Naviを開く →</a>
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
  <p>© 2026 DrumNavi — <a href="../">家系図Navi / Family Tree Guide</a></p>
</footer>

</body>
</html>
"""


def main():
    # 全記事タイトル一覧（関連記事リンク用）
    all_pairs = [(a["slug"], a["h1"]) for a in ARTICLES]

    for art in ARTICLES:
        related = [(s, t) for s, t in all_pairs if s != art["slug"]][:5]
        out_dir = ROOT / art["slug"]
        out_dir.mkdir(exist_ok=True)
        html = render(art, related)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  ✓ /{art['slug']}/")

    # sitemap.xml を再生成
    today = "2026-05-30"
    urls = [SITE_URL + "/"] + [f"{SITE_URL}/{a['slug']}/" for a in ARTICLES]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>{'1.0' if u == urls[0] else '0.8'}</priority></url>")
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")
    print(f"  ✓ sitemap.xml ({len(urls)} URLs)")


if __name__ == "__main__":
    main()
