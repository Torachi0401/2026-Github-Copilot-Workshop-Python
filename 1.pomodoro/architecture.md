# Webアプリケーションアーキテクチャ案

## 概要
このドキュメントは、Flask と HTML/CSS/JavaScript を用いて実装するポモドーロタイマーWebアプリのアーキテクチャ案をまとめたものです。目的はモック（UI画像）に沿った見た目と動作を実現しつつ、ユニットテストが書きやすく保守しやすい構成にすることです。

## 高レベル設計
- バックエンド: Flask アプリ（API + テンプレート配信）、永続化は SQLite（Flask-SQLAlchemy）
- フロントエンド: 静的HTML/CSS + JavaScript（タイマー制御・描画・同期）
- テスト: pytest を用いたユニット/統合テスト、フロントは Jest 等

## 目的別責務
- Flask: ルーティング、認証（将来）、API（開始・完了・統計）、DB永続化
- サービス層: ビジネスロジック（タイマー処理、集計）を提供
- リポジトリ層: DBアクセスを抽象化し、テストで差し替え可能にする
- フロント: UI 表示、タイマー実行、サーバとの同期

## 推奨フォルダ構成

```
project-root/
├─ app/                      # Flask アプリ本体
│  ├─ __init__.py            # create_app()（ファクトリ）
│  ├─ config.py
│  ├─ models.py
│  ├─ routes/
│  │  ├─ api.py              # API BluePrint
│  │  └─ views.py            # ページルート
│  ├─ services/
│  │  └─ timer_service.py
│  └─ repositories/
│     └─ pomodoro_repo.py
├─ templates/
│  └─ index.html
├─ static/
│  ├─ css/styles.css
│  └─ js/timer.js            # UI とタイマー制御（ロジック分離）
├─ tests/
│  ├─ conftest.py
│  └─ test_timer_service.py
├─ requirements.txt
└─ architecture.md
```

## データモデル（概略）
- `Pomodoro` テーブル
  - `id` : int
  - `start_time` : datetime
  - `end_time` : datetime (nullable)
  - `duration_sec` : int
  - `status` : string (running/completed/cancelled)
  - `type` : string (work/break)

日次の集計は DB クエリで算出（例: 今日の completed 件数、合計集中時間）。

## API（代表例）
- `GET /` : メイン UI（`index.html`）
- `POST /api/start` : 開始。payload { type: "work" } → 新規レコード(status=running)
- `POST /api/complete` : 完了。payload { id, end_time, duration_sec } → status=completed に更新
- `POST /api/reset` : リセット（必要ならサーバ通知）
- `GET /api/stats?date=YYYY-MM-DD` : 日次集計を返す

※ 将来的に複数端末/タブ間同期が必要なら `Flask-SocketIO` を追加する。

## サービス層とリポジトリ層
- `services/timer_service.py` : タイマーの状態遷移、時間計算、バリデーション等の純ロジックを実装（副作用なしの関数/クラス中心）
- `repositories/pomodoro_repo.py` : ORM セッションを引数に取り DB 操作を行う。テスト時はモック置換可能にする。
- ルート（`routes/api.py`）は入力検証とサービス呼び出しのみを行い、ビジネスロジックや DB ロジックは持たない。

## クライアント設計（タイマー）
- タイマーはクライアント側で実行する（UIレスポンスと精度のため）。
- 時間経過・表示の責務を分離：
  - `timer_logic.js` : 残り時間の計算、状態遷移（純ロジック、単体テスト可能）
  - `timer_ui.js` : DOM操作と描画（SVG や Canvas を用いた円形プログレス）
- 開始時に `/api/start` を呼び、完了時に `/api/complete` を呼ぶ。ネットワーク障害時は `localStorage` にイベントを保存し、復帰時に同期する。

## 同期と整合性戦略
- シンプル案（推奨初期実装）: サーバは「記録」のみ担当。クライアントは自主的に動作し、完了したらサーバへ送信。未送信は後で再送。
- 進化案: WebSocket でリアルタイム同期（複数タブ/端末）やサーバ検証を追加。

## テスト設計（ユニット重視）
- アプリファクトリ (`create_app`) を実装し、テスト用設定（`TestingConfig`、`sqlite:///:memory:`）でアプリを生成する。
- `tests/conftest.py` に `app`, `client`, `db_session` の pytest フィクスチャを用意。
- サービス層（`timer_service`）は副作用を持たない純粋関数にしてユニットテストを充実させる。
- DB 関連はリポジトリをモックしてサービスの単体テストを行う。API の統合テストは in-memory DB と `test_client` で実行。
- 時刻依存は `Clock` インターフェース（`now()`）を注入して固定化、または `freezegun` を併用。

## 依存ライブラリ（候補）
- Backend: `Flask`, `Flask-SQLAlchemy`, `Flask-Migrate`（任意）, `Flask-SocketIO`（必要時）
- Testing: `pytest`, `pytest-mock`, `freezegun`, `factory_boy`
- Frontend: （任意）`dayjs`、テスト用に `jest`, `@testing-library/dom`、E2Eに `playwright`

## 開発フロー（短期）
1. `create_app()` の導入とベース雛形の作成（テスト設定含む）。
2. `timer_service`（純ロジック）の実装とユニットテスト作成。
3. 最小限の API（`/api/start`, `/api/complete`, `/api/stats`）を実装し統合テストを追加。
4. フロントのタイマー基本機能（開始/完了/リセット）を実装し、サーバ同期を確認。
5. UI デザイン調整、E2E テスト、必要に応じて WebSocket を追加。

## 次のアクション候補
- 上記に従い、`create_app` と `timer_service`、`pomodoro_repo` の雛形とサンプルテストを作成します。進めてよければ実装を開始します。

---
作成日: 2026-02-24
