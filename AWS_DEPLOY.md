# AWSへのデプロイガイド (AWS Deployment Guide)

このドキュメントでは、本アプリケーション（Dockerコンテナ化済みNode.jsアプリ）をAWS上で公開するための代表的なデプロイ手順を解説します。

---

## 🚀 おすすめのAWSサービス: **AWS App Runner**
初心者〜中級者に最もおすすめなのが **AWS App Runner** です。インフラ管理不要で、コンテナイメージまたはGitHubリポジトリを指定するだけでSSL（HTTPS）対応のURLを自動発行して公開してくれます。

---

## 手順 1: AWS ECR (Elastic Container Registry) へのコンテナイメージ登録

まず、ローカルで作成したDockerイメージをAWSのプライベート/パブリックレジストリ（ECR）に送信します。

### 1-1. ECR リポジトリの作成
```bash
aws ecr create-repository --repository-name cute-cat-app --region ap-northeast-1
```

### 1-2. Docker の AWS ECR ログイン認証
```bash
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com
```

### 1-3. コンテナイメージのビルドとタグ付け
```bash
docker build -t cute-cat-app .

docker tag cute-cat-app:latest <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com/cute-cat-app:latest
```

### 1-4. ECR へイメージをプッシュ
```bash
docker push <YOUR_AWS_ACCOUNT_ID>.dkr.ecr.ap-northeast-1.amazonaws.com/cute-cat-app:latest
```

---

## 手順 2: AWS App Runner で公開する（最短・簡単）

1. [AWS コンソール](https://console.aws.amazon.com/apprunner/) にログインし、「**サービスを作成**」をクリックします。
2. **ソース**: 「コンテナレジストリ」を選び、プロバイダーで「Amazon ECR」を選択します。
3. **イメージの指定**: 手順1でプッシュした `cute-cat-app:latest` を選択。
4. **デプロイトリガー**: 「自動」（新しいイメージがプッシュされたら自動再デプロイ）または「手動」を選択。
5. **設定**:
   - サービス名: `cute-cat-service`
   - ポート: `3000`
   - ヘルスチェックパス: `/health`
6. 「**作成とデプロイ**」をクリック。
7. 数分後、発行された `https://xxx.awsapprunner.com` 形式のURLにアクセスすれば世界中に公開完了です！🎉

---

## 補足: その他のデプロイ方法

### A. AWS ECS Fargate
スケーラビリティやVPC連携が必要な場合は ECS Fargate をご利用ください。
- タスク定義を作成し、コンテナイメージURLとポート `3000` を設定
- アプリケーションロードバランサー (ALB) とターゲットグループ（ヘルスチェック `/health`）を設定

### B. Amazon EC2
1. EC2インスタンス（Amazon Linux 2023等）を起動
2. Dockerをインストール: `sudo dnf install docker -y && sudo systemctl start docker`
3. 本リポジトリを `git clone` または Dockerイメージを取得
4. `docker run -d -p 80:3000 cute-cat-app` で80番ポートで公開
