# GitHub Workflows

## Pomodoro Documentation Sync ワークフロー（無効化済み）

### 現状

`pomodoro-docs-sync` ワークフローは現在無効化されています（`.disabled` 拡張子が付与されています）。

### 無効化理由

このワークフローは GitHub Copilot CLI を使用するため、`COPILOT_GITHUB_TOKEN` シークレットが必要ですが、現在このシークレットがリポジトリに設定されていません。

シークレットが設定されていない状態でワークフローが実行されると、以下のエラーで失敗します：

```
⚠️ Secret Verification Failed: The workflow's secret validation step failed.
```

### ワークフローを有効化する方法

このワークフローを有効化したい場合は、以下の手順を実行してください：

1. **COPILOT_GITHUB_TOKEN シークレットを設定**
   - リポジトリの Settings → Secrets and variables → Actions に移動
   - "New repository secret" をクリック
   - Name: `COPILOT_GITHUB_TOKEN`
   - Value: GitHub Copilot CLI 用の有効なトークン
   - 詳細: https://github.github.com/gh-aw/reference/engines/#github-copilot-default

2. **ワークフローファイルの名前を変更**
   ```bash
   mv .github/workflows/pomodoro-docs-sync.lock.yml.disabled .github/workflows/pomodoro-docs-sync.lock.yml
   mv .github/workflows/pomodoro-docs-sync.md.disabled .github/workflows/pomodoro-docs-sync.md
   ```

3. **変更をコミット・プッシュ**

### ワークフローの機能

このワークフローが有効化されると、以下の機能を提供します：

- `1.pomodoro/` 配下のコード変更を検出
- ソースコードを分析して、ドキュメント（`1.pomodoro/docs/`）の更新が必要かを判断
- ドキュメントの更新が必要な場合、自動的にプルリクエストを作成
- APIリファレンス、アーキテクチャ、データモデルなどのドキュメントを最新の状態に保つ

### 代替手段

シークレットを設定せずにドキュメントを更新したい場合は、手動で以下を実行してください：

```bash
# ドキュメントを確認・更新
cd 1.pomodoro/docs/
# 必要に応じてファイルを編集
# git add, commit, push
```

---

**注意**: このワークフローは Agentic Workflows (gh-aw) を使用して生成された `.lock.yml` ファイルです。直接編集せず、`.md` ソースファイルを編集してから `gh aw compile` を実行してください。
