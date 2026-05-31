# はてなブログ 自動投稿スキーム

LP の44記事を「要約＋送客」記事に変換し、はてなブログ公式 AtomPub API で自動投稿します。

## 仕組み

- `post_to_hatena.py` … 未投稿記事を1本、はてなへ投稿し `posted.json` に記録
- `.github/workflows/hatena-post.yml` … 2日に1本、自動実行（約3ヶ月で全44本配信）
- 重複コンテンツ回避のため**全文転載はせず**、要点＋「詳しくはLPへ」＋「無料試算はアプリへ」の送客型

## セットアップ（初回のみ）

### 1. はてなブログを作成
https://blog.hatena.ne.jp/ でアカウント＋ブログを作成。

### 2. AtomPub APIキーを取得
ブログ管理画面 → **設定 → 詳細設定** → ページ下部 **「AtomPub」** 欄：
- **ルートエンドポイント** が `https://blog.hatena.ne.jp/{はてなID}/{ブログID}/atom` の形で表示される
- **APIキー** は同設定ページ内に表示（または はてな → アカウント設定）

### 3. GitHub Secrets に登録
リポジトリ → Settings → Secrets and variables → Actions → New repository secret：

| Name | Value 例 |
|---|---|
| `HATENA_ID` | `taro123`（はてなID） |
| `HATENA_BLOG_ID` | `taro123.hatenablog.com`（ブログID） |
| `HATENA_API_KEY` | 取得したAPIキー |

### 4. 動作テスト
Actions → 「Auto Post to Hatena Blog」 → Run workflow：
- まず **dry_run = true** でプレビュー確認
- 次に **draft = true** で下書き投稿テスト（はてな管理画面で確認）
- 問題なければ通常実行（2日ごとに自動投稿開始）

## ローカルでのテスト

```bash
# プレビュー（投稿しない）
python hatena/post_to_hatena.py --dry-run

# 実投稿（要環境変数）
HATENA_ID=... HATENA_BLOG_ID=... HATENA_API_KEY=... python hatena/post_to_hatena.py
```

## 調整

- **投稿間隔**：`hatena-post.yml` の `cron` を変更（例 `0 1 * * *` で毎日）
- **1回の本数**：`POST_LIMIT` 環境変数（既定1）
- **やり直し**：`posted.json` を `{"posted": []}` に戻すと最初から
