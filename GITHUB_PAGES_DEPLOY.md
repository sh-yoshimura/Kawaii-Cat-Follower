# GitHub Pages での無料公開ガイド (GitHub Pages Deployment Guide)

本Webアプリケーションは、サーバー不要でブラウザのみで動作する完全レスポンシブな構成となっているため、**GitHub Pages を使うことで完全無料・サーバー管理不要で世界中に公開可能**です！

---

## 🚀 最短手順: GitHub Pages で公開する（完全無料）

### 手順 1. GitHub にリポジトリを作成
1. [GitHub](https://github.com/) にログインし、「**New repository**」をクリックします。
2. **Repository name**: `cute-cat-app`（任意）と入力。
3. **Public / Private**: `Public` を選択（※無料版GitHub PagesはPublicリポジトリで利用可能）。
4. 「**Create repository**」をクリック。

---

### 手順 2. コードを GitHub に Push
ターミナルまたは Git Bash で、本アプリのフォルダに移動して実行します：

```bash
# Git リポジトリの初期化
git init
git add .
git commit -m "Initial commit of Cute Cat App"

# GitHubリポジトリへの紐付けとPush
git branch -M main
git remote add origin https://github.com/<あなたのGitHubユーザー名>/cute-cat-app.git
git push -u origin main
```

---

### 手順 3. GitHub Pages の有効化
1. GitHub上の対象リポジトリ画面で **「Settings (設定)」** タブをクリック。
2. 左メニューの **「Pages」** を選択。
3. **Build and deployment** セクションで以下を設定：
   - **Source**: `Deploy from a branch`
   - **Branch**: `main` / `/ (root)` または `/public` を選択
4. **「Save」** ボタンをクリック！

---

### 手順 4. 公開確認
約 1〜2 分後、GitHub Pages 設定画面の上部に：

> 🎉 **Your site is live at `https://<あなたのユーザー名>.github.io/cute-cat-app/`**

と表示され、発行されたURLにアクセスすれば公開完了です！

---

## 💡 補足: GitHub 連携で Docker コンテナのまま無料公開したい場合

Dockerコンテナのまま（Node.jsサーバーとして）GitHub連携で無料公開したい場合は、以下のサービスも利用できます：
- **Render.com** (GitHubリポジトリを連携して Docker Web Service を無料公開)
- **Vercel** (GitHubと連携してワンクリック公開)
- **Cloudflare Pages** (完全無料・超高速配信)
